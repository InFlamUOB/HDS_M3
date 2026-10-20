#!/usr/bin/env python3
"""Lint the live code cells. Run with `make check`, before you push.

Catches the mistakes that are invisible at render time and only show up when a
student clicks something:

  * a chapter missing its `engine: knitr` front matter (Quarto then reaches for
    Jupyter and the render fails);
  * two exercises sharing a key on one page (the Quarto Live filter errors);
  * a hint or solution cell whose key has no exercise;
  * an exercise cell with no `______` for the student to fill in;
  * a solution cell that cannot run on its own, because the exercise cell it
    replaces did the imports;
  * a data file used in a cell but not mounted into the browser filesystem;
  * a library or module used in a cell but absent from the runtime package list.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CELL = re.compile(r"^```\{(webr|pyodide)\}\n((?:#\|[^\n]*\n)*)(.*?)\n```\s*$",
                  re.S | re.M)

problems: list[str] = []
notes: list[str] = []


def fail(chapter: str, msg: str) -> None:
    problems.append(f"{chapter}: {msg}")


def runtime_packages() -> tuple[set[str], set[str]]:
    cfg = (ROOT / "_quarto.yml").read_text()
    def listed(key: str) -> set[str]:
        m = re.search(rf"^{key}:\n(?:  .*\n)*?  packages:\s*\[(.*?)\]", cfg, re.M)
        return {p.strip() for p in m.group(1).split(",")} if m else set()
    return listed("webr"), listed("pyodide")


def mounted_files() -> set[str]:
    cfg = (ROOT / "_quarto.yml").read_text()
    tail = cfg.split("\nresources:", 1)[-1]
    return set(re.findall(r"^\s*-\s*(\S+)\s*$", tail, re.M))


def main() -> int:
    webr_pkgs, pyodide_pkgs = runtime_packages()
    mounted = mounted_files()
    stdlib = set(sys.stdlib_module_names) | {"checks"}
    # names the runtime attaches for us, plus pandas' conventional aliases
    py_ok = pyodide_pkgs | {"sklearn", "matplotlib", "numpy", "pandas"}

    for chapter in sorted(ROOT.glob("day*.qmd")):
        text = chapter.read_text()
        name = chapter.name

        if not text.startswith("---"):
            fail(name, "missing front matter; add `engine: knitr`")
        elif "engine: knitr" not in text.split("---", 2)[1]:
            fail(name, "front matter does not pin `engine: knitr`")

        keys: dict[str, list[str]] = {}
        for eng, opts, body in ((m.group(1), m.group(2), m.group(3))
                               for m in CELL.finditer(text)):
            key = re.search(r"exercise:\s*(\S+)", opts)
            key = key.group(1) if key else None
            kind = ("solution" if "solution: true" in opts
                    else "hint" if "hint: true" in opts else "main")
            if key:
                keys.setdefault(key, []).append(kind)

            if kind == "main" and key and "______" not in body:
                fail(name, f"exercise `{key}` has no ______ for the student")

            for f in re.findall(r'["\'](data/[\w./-]+)["\']', body):
                if f not in mounted and not re.search(r"\{.*\}", f):
                    fail(name, f"`{f}` is used but not under `resources:` in _quarto.yml")

            if eng == "webr":
                for lib in re.findall(r"library\((\w+)\)", body):
                    if lib not in webr_pkgs:
                        fail(name, f"`library({lib})` but {lib} is not in the webr package list")
            else:
                for mod in re.findall(r"^\s*(?:import|from)\s+([\w.]+)", body, re.M):
                    top = mod.split(".")[0]
                    if top not in py_ok and top not in stdlib:
                        fail(name, f"`import {top}` but {top} is not in the pyodide package list")

        for key, kinds in keys.items():
            if kinds.count("main") == 0:
                fail(name, f"key `{key}` has a {kinds[0]} cell but no exercise cell")
            if kinds.count("main") > 1:
                fail(name, f"key `{key}` is used by {kinds.count('main')} exercise cells")

        # a solution must stand alone: if the cell it replaces imports or sources
        # something, the solution has to do it too
        for key in keys:
            cells = {kind: body for _, opts, body in
                     ((m.group(1), m.group(2), m.group(3)) for m in CELL.finditer(text))
                     if (kind := ("solution" if "solution: true" in opts
                                  else "hint" if "hint: true" in opts else "main"))
                     and re.search(r"exercise:\s*" + re.escape(key) + r"\b", opts)}
            main_cell, sol = cells.get("main", ""), cells.get("solution")
            if sol is None:
                continue
            setup = re.findall(r"^\s*(?:import\s+\w+|from\s+[\w.]+\s+import|source\(.*\))",
                               main_cell, re.M)
            if setup and not re.findall(
                    r"^\s*(?:import\s+\w+|from\s+[\w.]+\s+import|source\(.*\))", sol, re.M):
                fail(name, f"solution for `{key}` omits the imports its exercise cell makes; "
                           "clicking Solution replaces that cell, so it must run standalone")

        n = len(CELL.findall(text))
        if n:
            notes.append(f"{name}: {n} live cells, {len(keys)} exercises")

    for line in notes:
        print("  " + line)
    if problems:
        print("\nproblems found:", file=sys.stderr)
        for p in problems:
            print("  ✗ " + p, file=sys.stderr)
        return 1
    print("\nall live cells pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
