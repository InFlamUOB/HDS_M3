#!/usr/bin/env python3
"""Write one R script and one Python script per chapter, for students to download.

    python3 scripts/make_code_files.py              # every chapter offering a download
    python3 scripts/make_code_files.py day3-02-loss-functions.qmd

Writes code/<chapter>.R and code/<chapter>.py. Each file holds the code a
student sees on the page, in page order, with the section headings kept as
comments so the script reads like the chapter.

What it does NOT include: anything inside a
::: {.content-visible when-meta="show-solutions"} block. The worked answers are
not published, so they are not downloadable either. The blanks (______) are
left exactly as they appear on the page: these are worksheets, not solutions,
and they are not meant to run end to end until the student fills them in.

The chapters are the single source of truth. Do not edit the generated files;
edit the chapter and re-run. scripts/check_cells.py checks that they are current.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "code"
SITE = "https://inflamuob.github.io/HDS_M3/"

COMMENT = {"r": "#", "python": "#"}
EXT = {"r": ".R", "python": ".py"}
LABEL = {"r": "R", "python": "Python"}


def offers_download(path):
    """Does this chapter link to its own downloadable code file?"""
    return "](code/%s" % path.stem in path.read_text()


def live_chapters():
    """Chapters that offer a download link, which is what decides the scope.

    Add the link to a chapter and it gets files; remove it and they go.
    """
    return [p.name for p in sorted(ROOT.glob("day*.qmd")) if offers_download(p)]


def extract(path, with_answers=False):
    """Return (title, {lang: [(heading, code), ...]}) for one chapter.

    with_answers=True keeps the code of the worked-answer blocks; instructor
    blocks are never included.
    """
    text = path.read_text()
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)       # YAML header
    lines = text.splitlines()

    blocks = {"r": [], "python": []}
    title = None
    stack = []            # open fenced divs, innermost last
    heading = None        # most recent heading not yet attached to a chunk
    tab = None            # which language tab we are inside
    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced divs
        if re.match(r"^:{3,}\s*$", line):
            if stack:
                stack.pop()
            i += 1
            continue
        # any fence line with something after the colons opens a div, braces
        # or not: `::: {.callout-note}`, `::: instructor`, `::: panel-tabset`
        m = re.match(r"^:{3,}\s*(\S.*?)\s*$", line)
        if m:
            stack.append(m.group(1))
            i += 1
            continue

        hidden = any(("show-solutions" in d and not with_answers)
                     or "when-profile" in d or "instructor" in d for d in stack)

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level, text_ = len(m.group(1)), m.group(2)
            text_ = re.sub(r"\s*\{#[^}]*\}\s*$", "", text_).strip()
            if level == 1 and title is None:
                title = text_
            elif level == 2 and text_ in ("R", "Python"):
                tab = "r" if text_ == "R" else "python"
                heading = None
            elif not hidden:
                heading = text_
            i += 1
            continue

        # code chunks
        m = re.match(r"^```\{(r|python)\}\s*$", line)
        if m:
            lang = m.group(1)
            j = i + 1
            body = []
            while j < len(lines) and not re.match(r"^```\s*$", lines[j]):
                body.append(lines[j])
                j += 1
            # A chunk with `#| echo: false` draws a figure the page shows without
            # its code (the 3D loss surface); it is not part of the student code.
            shown = not any(re.match(r"#\|\s*echo:\s*false", b) for b in body)
            if not hidden and shown:
                body = [b for b in body if not b.startswith("#| ")]
                while body and not body[0].strip():
                    body.pop(0)
                while body and not body[-1].strip():
                    body.pop()
                blocks[lang].append((heading, "\n".join(body)))
                heading = None
            i = j + 1
            continue

        i += 1

    return title, blocks


def render(stem, title, lang, chunks):
    c = COMMENT[lang]
    rule = c + " " + "-" * 68
    # Each day is published at its own address: .../HDS_M3/day3/<chapter>.html
    # The day is the "Day N" part that lists the chapter in _quarto.yml, so the
    # explainability chapters (files day6-*) point at day9/, where they are published.
    day = ""
    part = None
    for line in (ROOT / "_quarto.yml").read_text().splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.match(r'- part:\s*"Day (\d+)\b', s)
        if m:
            part = m.group(1)
        elif part and s == f"- {stem}.qmd":
            day = f"day{part}/"
    if not day:
        m = re.match(r"day(\d+)-", stem)
        day = f"day{m.group(1)}/" if m else ""
    # Say "fill in the blanks" only when the chapter has blanks.
    blanks = [
        f"{c} Lines with ______ are blanks to fill in, so this file is a worksheet:",
        f"{c} it will not run end to end until you have filled them.",
    ] if any("______" in code for _, code in chunks) else []
    head = [
        f"{c} {title}",
        f"{c} HDS MSc · Module 3 · exercise booklet",
        f"{c} {SITE}{day}{stem}.html",
        c,
        f"{c} The {LABEL[lang]} code from the chapter, in page order, for you to copy and run.",
        *blanks,
        f"{c} Run it from the folder that holds your `data` folder.",
        c,
        f"{c} Generated from {stem}.qmd. Edit the chapter, not this file.",
        "",
    ]
    body = []
    for heading, code in chunks:
        if heading:
            body += ["", rule, f"{c} {heading}", rule, ""]
        elif body:
            body += [""]
        body += [code]
    return "\n".join(head + body).rstrip() + "\n"


def main(argv):
    targets = argv[1:] or live_chapters()
    OUT.mkdir(exist_ok=True)
    written = []
    for name in targets:
        path = ROOT / name
        stem = path.stem
        title, blocks = extract(path)
        for lang, chunks in blocks.items():
            dest = OUT / (stem + EXT[lang])
            if not chunks:
                if dest.exists():
                    dest.unlink()
                continue
            dest.write_text(render(stem, title, lang, chunks))
            written.append(f"{dest.relative_to(ROOT)}  {len(chunks)} chunks")
    print("\n".join(written) or "nothing to write")


if __name__ == "__main__":
    main(sys.argv)
