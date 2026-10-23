#!/usr/bin/env python3
"""Check the chapters before you push.  `make check`

Three faults that render without complaint:

  * a task chunk (one containing `______`) that is NOT marked `eval: false`,
    which makes the render fail or, worse, publish a broken result;
  * a worked answer that is not inside a `when-meta="show-solutions"` block, so
    it would be published before the session;
  * a link to a chapter file that does not exist.

It also prints whether solutions are currently released, since that is a
deliberate switch and worth seeing before a push.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHUNK = re.compile(r"^```\{(r|python)\}\n((?:#\|[^\n]*\n)*)(.*?)\n```[ \t]*$", re.S | re.M)
problems: list[str] = []

def main() -> int:
    cfg = (ROOT / "_quarto.yml").read_text()
    released = re.search(r"^show-solutions:\s*true", cfg, re.M) is not None

    for chapter in sorted(ROOT.glob("day*.qmd")):
        text, name = chapter.read_text(), chapter.name

        # worked answers must sit inside the released-only block
        spans = [(m.start(), m.end()) for m in
                 re.finditer(r':::+ \{\.content-visible when-meta="show-solutions"\}.*?\n:::\n:::',
                             text, re.S)]
        for m in re.finditer(r"## Worked answer", text):
            if not any(a <= m.start() <= b for a, b in spans):
                problems.append(f"{name}: a 'Worked answer' sits outside the "
                                "when-meta=\"show-solutions\" block, so it would publish early")

        n_task = n_worked = 0
        for m in CHUNK.finditer(text):
            opts, body = m.group(2), m.group(3)
            if "______" in body:
                n_task += 1
                if not re.search(r"^#\|\s*eval:\s*false", opts, re.M):
                    problems.append(f"{name}: a chunk containing ______ is missing "
                                    "`#| eval: false` and will fail when rendered")
            else:
                n_worked += 1

        for link in re.findall(r"\]\(([\w./-]+\.qmd)(?:#[\w-]+)?\)", text):
            if not (ROOT / link).exists():
                problems.append(f"{name}: link to `{link}`, which does not exist")

        print(f"  {name:<34} {n_worked:>2} worked, {n_task:>2} tasks, "
              f"{len(spans):>2} worked answers")

    print(f"\nsolutions are {'RELEASED (published to students)' if released else 'hidden'}")
    if problems:
        print("\nproblems:", file=sys.stderr)
        for p in problems:
            print("  ✗ " + p, file=sys.stderr)
        return 1
    print("chapters pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
