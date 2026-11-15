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

def check_release_lists() -> None:
    """A released chapter must also be in the all-days working profile.

    _quarto.yml is the student site; _quarto-all.yml is what you render while
    writing. A chapter in the first but not the second means `make preview`
    silently stops showing a page students can already read.
    """
    def listed(path):
        return [re.match(r"-\s+(\S+\.qmd)$", l.strip()).group(1)
                for l in (ROOT / path).read_text().splitlines()
                if not l.strip().startswith("#") and re.match(r"-\s+\S+\.qmd$", l.strip())]

    released, working = listed("_quarto.yml"), listed("_quarto-all.yml")
    for name in released:
        if name not in working:
            problems.append(f"{name} is published in _quarto.yml but missing "
                            "from _quarto-all.yml")
    days = sorted({n[:4] for n in released if n.startswith("day")})
    print(f"\n  published to students: {', '.join(days) or 'none'} "
          f"({len(released)} chapters); {len(working)} written in total")


def check_code_files() -> None:
    """The downloadable scripts must still match the chapters they came from.

    Only chapters that link to their code file are checked: a chapter without
    that link simply does not offer a download yet.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_code_files as mcf

    n = 0
    for chapter in sorted(ROOT.glob("day*.qmd")):
        dests = {lang: ROOT / "code" / (chapter.stem + ext)
                 for lang, ext in mcf.EXT.items()}
        if not mcf.offers_download(chapter):
            for dest in dests.values():
                if dest.exists():
                    problems.append(f"code/{dest.name} exists but {chapter.name} "
                                    "does not link to it; delete one or the other")
            continue
        title, blocks = mcf.extract(chapter)
        for lang, dest in dests.items():
            chunks = blocks[lang]
            if not chunks:
                if dest.exists():
                    problems.append(f"code/{dest.name}: the chapter has no {lang} "
                                    "cells left; delete the file")
            elif not dest.exists():
                problems.append(f"code/{dest.name} is missing; run "
                                "python3 scripts/make_code_files.py")
            elif dest.read_text() != mcf.render(chapter.stem, title, lang, chunks):
                problems.append(f"code/{dest.name} is out of date; run "
                                "python3 scripts/make_code_files.py")
            else:
                n += 1
    print(f"\n  {n} downloadable code files match their chapters")


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

    check_code_files()
    check_release_lists()

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
