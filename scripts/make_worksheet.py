#!/usr/bin/env python3
"""Build the printable worksheet for one teaching day from the chapter sources.

    python3 scripts/make_worksheet.py --day 1 --profile student
    python3 scripts/make_worksheet.py --day 1 --profile instructor

Writes print/day<N>-<profile>.qmd, which is rendered with

    quarto render print/day1-student.qmd --to typst

The chapters are the single source of truth: this script only transforms them.

What it does
  * rewrites executable cells (```{r} / ```{python}) into plain ```r / ```python
    blocks and strips their `#|` options, since nothing executes on paper;
  * drops the worked-answer blocks for the student profile, keeps and labels
    them for the instructor profile;
  * drops ::: {.content-visible when-profile="instructor"} blocks for the
    student profile;
  * drops ::: {.web-only} blocks, which say things that are only true on screen;
  * drops {{< include >}} directives, which are render plumbing;
  * flattens ::: {.panel-tabset} into bold language labels, which is both
    shorter and clearer in print.

Do not edit the generated file; edit the chapter and re-run.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

HEADER = """---
title: "Machine Learning for Health Data"
subtitle: "HDS MSc · Module 3 · Day {day} worksheet{suffix}"
date: today
date-format: "MMMM YYYY"
format:
  typst:
    papersize: a4
    margin: {{x: 2.2cm, y: 2.2cm}}
    toc: true
    toc-depth: 1
    number-sections: true
    number-depth: 1
    fontsize: 10pt
engine: markdown
bibliography: references.bib
---

::: {{.callout-note appearance="simple"}}
This is the printable companion to the booklet. The code is here so that you can
read and annotate it away from a screen; you run it in the `.qmd` chapters
themselves, in your editor, which is where you should actually work. Blanks
written `______` are yours to fill in.
:::

"""

LANG = {"r": "r", "python": "python"}


def transform(text: str, instructor: bool) -> str:
    # drop the chapter's own YAML front matter
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    out, lines = [], text.splitlines()
    i, div_stack, drop_depth, tabset_depth = 0, [], None, None

    while i < len(lines):
        line = lines[i]

        # {{< include _common.qmd >}} is render plumbing (it only configures
        # knitr and reticulate) and its path would not resolve from print/.
        if re.match(r"^\{\{<\s*include\s+.*>\}\}\s*$", line):
            i += 1
            continue

        # --- fenced code cells -------------------------------------------
        m = re.match(r"^```\{(r|python)\}\s*$", line)
        if m:
            lang, body, opts = LANG[m.group(1)], [], {}
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                opt = re.match(r"^#\|\s*([a-z-]+)\s*:\s*(.*)$", lines[i])
                if opt:
                    opts[opt.group(1)] = opt.group(2).strip()
                else:
                    body.append(lines[i])
                i += 1
            i += 1                                     # closing fence
            if drop_depth is not None:
                continue
            out.append(f"```{lang}")
            out.extend(body)
            out.append("```")
            out.append("")
            continue

        # --- div fences ---------------------------------------------------
        if line.startswith(":::"):
            attrs = re.match(r"^:::+\s*\{(.*)\}\s*$", line)
            if attrs:                                   # opening
                a = attrs.group(1)
                div_stack.append(a)
                if drop_depth is None and (
                    ".web-only" in a
                    or (not instructor and 'when-profile="instructor"' in a)
                    or (not instructor and 'when-meta="show-solutions"' in a)
                ):
                    drop_depth = len(div_stack)
                    i += 1
                    continue
                # the callout inside already carries a "Worked answer" heading
                if instructor and 'when-meta="show-solutions"' in a and drop_depth is None:
                    i += 1
                    continue
                if ".panel-tabset" in a and drop_depth is None:
                    tabset_depth = len(div_stack)
                    i += 1
                    continue
            else:                                       # closing
                depth = len(div_stack)
                if div_stack:
                    div_stack.pop()
                if drop_depth is not None and depth == drop_depth:
                    drop_depth = None
                    i += 1
                    continue
                if tabset_depth is not None and depth == tabset_depth:
                    tabset_depth = None
                    i += 1
                    continue
            if drop_depth is not None:
                i += 1
                continue
            out.append(line)
            i += 1
            continue

        if drop_depth is not None:
            i += 1
            continue

        # tab labels become bold language labels
        if tabset_depth is not None and re.match(r"^##\s+(R|Python)\s*$", line):
            out.append(f"**{line.split(maxsplit=1)[1].strip()}**")
            out.append("")
            i += 1
            continue

        out.append(line)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--day", type=int, default=1)
    p.add_argument("--profile", choices=["student", "instructor"], default="student")
    args = p.parse_args()

    chapters = sorted(ROOT.glob(f"day{args.day}-*.qmd"))
    if not chapters:
        print(f"no chapters found for day {args.day}", file=sys.stderr)
        return 1

    instructor = args.profile == "instructor"
    parts = [HEADER.format(day=args.day,
                           suffix=" — INSTRUCTOR COPY" if instructor else "")]
    for ch in chapters:
        parts.append(transform(ch.read_text(), instructor))
        parts.append("")

    # Typst refuses to read outside the render root, so keep a copy alongside.
    (ROOT / "print").mkdir(exist_ok=True)
    (ROOT / "print" / "references.bib").write_text((ROOT / "references.bib").read_text())

    dest = ROOT / "print" / f"day{args.day}-{args.profile}.qmd"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text("\n".join(parts))
    print(f"wrote {dest.relative_to(ROOT)} from {len(chapters)} chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
