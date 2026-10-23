#!/usr/bin/env python3
"""Run a day's live code cells in real R and Python, from the terminal.

    python3 scripts/run_cells.py --day 1              # both languages
    python3 scripts/run_cells.py --day 1 --lang r     # or: make test-cells DAY=1

Why this exists: `{webr}` and `{pyodide}` cells are executed by the reader's
browser, never at render time, so a clean `quarto render` is no evidence that any
of that code works. This reconstructs each chapter as a session and runs it
locally — the worked-example cells in order, and for every task cell containing
`______` the published solution in its place, which is the state a student
reaches by the end of the page.

It reports the self-checks each chapter printed, and fails on any error. Needs R
with the booklet's packages (`make setup-r`) and a Python with pandas, numpy,
matplotlib and scikit-learn; `make doctor` reports both.
"""

import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CELL = re.compile(r"^```\{(webr|pyodide)\}\n((?:#\|[^\n]*\n)*)(.*?)\n```\s*$", re.S | re.M)


def r_preamble() -> str:
    """Attach the same packages the browser runtime attaches for the reader."""
    cfg = (ROOT / "_quarto.yml").read_text()
    m = re.search(r"^webr:\n(?:  .*\n)*?  packages:\s*\[(.*?)\]", cfg, re.M)
    pkgs = [p.strip() for p in m.group(1).split(",")] if m else []
    return ("suppressPackageStartupMessages({\n"
            + "".join(f'  library({p})\n' for p in pkgs) + "})\n")


def session(chapter: pathlib.Path, engine: str) -> list[str]:
    text = chapter.read_text()
    cells = []
    for m in CELL.finditer(text):
        eng, opts, body = m.group(1), m.group(2), m.group(3)
        kind = ("solution" if "solution: true" in opts
                else "hint" if "hint: true" in opts else "main")
        key = re.search(r"exercise:\s*(\S+)", opts)
        cells.append((eng, kind, key.group(1) if key else None, body))
    solutions = {k: b for e, kind, k, b in cells if e == engine and kind == "solution"}
    out = []
    for e, kind, k, body in cells:
        if e != engine or kind != "main":
            continue
        out.append(solutions.get(k, body) if "______" in body else body)
    return out


def run(chapter: pathlib.Path, engine: str, keep: bool) -> tuple[int, int, bool]:
    cells = session(chapter, engine)
    if not cells:
        return 0, 0, True
    suffix, marker = (".R", 'cat("--- cell %d ---\\n")') if engine == "webr" else (".py", 'print("--- cell %d ---")')
    body = "".join(f"{marker % i}\n{c}\n" for i, c in enumerate(cells))
    script = (r_preamble() + body) if engine == "webr" else body

    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=not keep,
                                     dir=ROOT, prefix=".cells_") as fh:
        fh.write(script)
        fh.flush()
        cmd = (["Rscript", "--vanilla", fh.name] if engine == "webr"
               else [sys.executable, fh.name])
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=900)

    out = p.stdout + p.stderr
    ok = len(re.findall(r"^\[ok\]", out, re.M))
    fix = len(re.findall(r"^\[fix\]", out, re.M))
    broke = p.returncode != 0 or bool(
        re.search(r"^Error|Error in |Traceback \(most recent", out, re.M))
    lang = "R" if engine == "webr" else "Python"
    status = "FAILED" if broke else ("checks failed" if fix else "ok")
    print(f"  {chapter.name:<34} {lang:<7} {len(cells):>2} cells  "
          f"{ok} ok, {fix} fix  {status}")
    if broke or fix:
        for line in out.splitlines():
            if re.match(r"^(\[fix\]|Error|Traceback|\s+File \"|\w*Error:)", line):
                print("        " + line)
    return ok, fix, not broke


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, default=1)
    ap.add_argument("--lang", choices=["r", "python", "both"], default="both")
    ap.add_argument("--keep", action="store_true", help="leave the generated scripts in place")
    args = ap.parse_args()

    chapters = sorted(ROOT.glob(f"day{args.day}-*.qmd"))
    if not chapters:
        print(f"no chapters for day {args.day}", file=sys.stderr)
        return 1
    engines = {"r": ["webr"], "python": ["pyodide"], "both": ["webr", "pyodide"]}[args.lang]

    print(f"Running the live cells of day {args.day} against local R / Python.\n")
    total_ok = total_fix = 0
    all_good = True
    for chapter in chapters:
        for engine in engines:
            ok, fix, good = run(chapter, engine, args.keep)
            total_ok += ok
            total_fix += fix
            all_good &= good

    print(f"\n{total_ok} checks passed, {total_fix} failed, "
          f"{'no errors' if all_good else 'ERRORS — see above'}")
    if total_fix or not all_good:
        print("\nA [fix] means a self-check rejected the object the cell built; an error\n"
              "means the cell did not run at all. Both are things a student would hit.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
