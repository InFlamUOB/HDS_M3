#!/usr/bin/env python3
"""Build one teaching day as a site of its own, with an address of its own.

    python3 scripts/make_day_site.py --day 1              # build, to look at
    python3 scripts/make_day_site.py --day 1 --publish    # build and release
    python3 scripts/make_day_site.py --day 1 --publish --answers
    python3 scripts/make_day_site.py --unpublish 3        # take a day down
    python3 scripts/make_day_site.py --home               # rebuild the homepage only

What students see is the folder site/, and nothing else:

    site/index.html     the module homepage, linking the released days
    site/day1/          Day 1: its own sidebar, its own search, its own address
    site/day2/          present only once Day 2 has been released

GitHub publishes site/ as it is committed. So a day's pages change only when
you run this script for that day and commit the result. Editing Day 4, or
rebuilding Day 2, leaves site/day1/ byte for byte as it was.

The booklet (_quarto.yml, `make preview`) stays the place you write: every
chapter in one book, built into _book/, which is not published.

How a day is built: its chapters are copied, unchanged, into dist/day<N>/ with
the booklet's own theme, shared setup and settings, and rendered as a small
book. Worked answers are hidden exactly as they are in the booklet, by
`show-solutions`; --answers turns them on for that day only. Nothing in dist/
is committed.

Needs quarto on PATH. Run from the repository root.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QUARTO = shutil.which("quarto") or "quarto"


# ------------------------------------------------------------ what a day holds

def day_part(day):
    """(part title, [chapter filenames]) for one day, from _quarto.yml."""
    title, chapters, inside = None, [], False
    for line in (ROOT / "_quarto.yml").read_text().splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.match(r'- part:\s*"([^"]+)"', s)
        if m:
            if inside:
                break
            if re.match(r"Day %d\b" % day, m.group(1)):
                title, inside = m.group(1), True
            continue
        if inside:
            m = re.match(r"-\s+(\S+\.qmd)$", s)
            if m:
                chapters.append(m.group(1))
    if not chapters:
        sys.exit("No chapters for day %d in _quarto.yml" % day)
    return title, chapters


def chapter_title(name):
    m = re.search(r"^# (.+?)(?:\s*\{[^}]*\})?\s*$", (ROOT / name).read_text(), re.M)
    return m.group(1) if m else name


def data_files(texts):
    """Every data/… file the chapters read or link to."""
    found = set()
    for t in texts:
        found |= set(re.findall(r'["(](data/[\w./-]+)["\)]', t))
    return sorted(f for f in found if (ROOT / f).is_file())


# ----------------------------------------------------------------- one day

def day_config(part_title, chapters, answers):
    master = (ROOT / "_quarto.yml").read_text()
    tail = master[master.index("bibliography:"):]
    tail = re.sub(r"^show-solutions:.*$",
                  "show-solutions: %s" % ("true" if answers else "false"),
                  tail, flags=re.M)
    chapter_lines = "\n".join("    - %s" % c for c in chapters)
    return f"""# Written by scripts/make_day_site.py. Do not edit: edit the booklet and rebuild.

project:
  type: book
  output-dir: _book
  resources:
    - data/
    - code/

book:
  title: "{part_title}"
  subtitle: "Statistical Machine Learning & Data Analytics · HDS MSc · Module 3"
  author: "Laura Bravo"
  date: today
  date-format: "MMMM YYYY"
  search: true
  sidebar:
    style: docked
    collapse-level: 2
  page-footer:
    left: "HDS MSc · Module 3"
    right: "Code to read, copy and run yourself"
  chapters:
    - index.qmd
{chapter_lines}

{tail}"""


def day_landing(day, part_title, chapters, data, answers):
    rows = "\n".join("- [%s](%s)" % (chapter_title(c), c) for c in chapters)
    files = "\n".join("| [`%s`](%s){download=\"%s\"} |"
                      % (pathlib.Path(f).name, f, pathlib.Path(f).name) for f in data)
    zip_name = "day%d-data.zip" % day
    return f"""---
engine: markdown
---

# {part_title} {{.unnumbered}}

These are the exercises for one teaching day of **Module 3** of the Health Data
Science MSc. Each chapter is one exercise you can finish in a single sitting,
with an R path and a Python path doing the same work. Pick one; in class we go
through R most of the time.

Some tasks appear as code containing `______` for you to fill in. They are shown
but not run, which is why no output appears beneath them.
{"The worked answers are shown after each task." if answers
 else "The worked answers are published after the session."}

## The exercises

{rows}

## The data

Save these in a folder called `data`, beside your script, before you start:
[**{zip_name}**](data/{zip_name}){{download="{zip_name}"}} has all of them.

| File |
|------|
{files}

---

[All days of this module](../index.html)
"""


def build_day(day, answers=False):
    part_title, chapters = day_part(day)
    work = ROOT / "dist" / ("day%d" % day)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    texts = []
    for name in chapters:
        text = (ROOT / name).read_text()
        texts.append(text)
        # A chapter may set show-solutions in its own header, which overrides
        # the project setting. In the copy that is rendered, this build's flag
        # decides, whatever the chapter says.
        head = re.match(r"\A---\n.*?\n---\n", text, flags=re.S)
        if head:
            fixed = re.sub(r"^show-solutions:.*$",
                           "show-solutions: %s" % ("true" if answers else "false"),
                           head.group(0), flags=re.M)
            text = fixed + text[head.end():]
        (work / name).write_text(text)
    for shared in ("_common.qmd", "theme.scss", "references.bib"):
        shutil.copy2(ROOT / shared, work / shared)

    data = data_files(texts)
    (work / "data").mkdir()
    for f in data:
        shutil.copy2(ROOT / f, work / f)
    with zipfile.ZipFile(work / "data" / ("day%d-data.zip" % day), "w",
                         zipfile.ZIP_DEFLATED) as z:
        for f in data:
            z.write(ROOT / f, f)

    (work / "code").mkdir()
    for name in chapters:
        for ext in (".R", ".py"):
            src = ROOT / "code" / (name[:-4] + ext)
            if src.exists():
                shutil.copy2(src, work / "code" / src.name)

    (work / "_quarto.yml").write_text(day_config(part_title, chapters, answers))
    (work / "index.qmd").write_text(day_landing(day, part_title, chapters, data, answers))

    print("rendering day %d (%d chapters) …" % (day, len(chapters)), flush=True)
    r = subprocess.run([QUARTO, "render", "--to", "html"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit((r.stdout + r.stderr)[-3000:])

    book = work / "_book"
    pages = sorted(book.glob("*.html"))
    # The gate: nothing a student should not see may be on a built page.
    leaks = []
    for page in pages:
        html = page.read_text(errors="replace")
        if not answers and "Worked answer" in html:
            leaks.append("%s shows a worked answer" % page.name)
        if re.search(r"Expected values|Common failures|Plenary\.", html):
            leaks.append("%s shows instructor notes" % page.name)
    if leaks:
        sys.exit("NOT PUBLISHABLE:\n  " + "\n  ".join(leaks))
    print("  %s: %d pages, %d data files%s"
          % (book.relative_to(ROOT), len(pages), len(data),
             ", WITH worked answers" if answers else ", answers hidden"))
    return book


# -------------------------------------------------------------- the homepage

def released_days():
    return sorted(int(p.name[3:]) for p in SITE.glob("day[0-9]*")
                  if (p / "index.html").exists())


def build_home():
    """site/index.html: the module homepage, listing the days that are in site/."""
    work = ROOT / "dist" / "home"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    blocks = []
    for day in released_days():
        try:
            part_title, chapters = day_part(day)
        except SystemExit:
            continue
        lines = ["### [%s](day%d/index.html)" % (part_title, day), ""]
        for c in chapters:
            page = c.replace(".qmd", ".html")
            if (SITE / ("day%d" % day) / page).exists():
                lines.append("- [%s](day%d/%s)" % (chapter_title(c), day, page))
        blocks.append("\n".join(lines))
    days = "\n\n".join(blocks) or "*No days have been released yet.*"

    text = (ROOT / "_home" / "index.qmd").read_text()
    if "{{DAYS}}" not in text:
        sys.exit("_home/index.qmd must contain the line {{DAYS}}")
    (work / "index.qmd").write_text(text.replace("{{DAYS}}", days))
    shutil.copy2(ROOT / "theme.scss", work / "theme.scss")
    (work / "_quarto.yml").write_text("project:\n  type: default\n")

    r = subprocess.run([QUARTO, "render", "index.qmd", "--to", "html"], cwd=work,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit((r.stdout + r.stderr)[-3000:])
    SITE.mkdir(exist_ok=True)
    shutil.copy2(work / "index.html", SITE / "index.html")
    (SITE / ".nojekyll").write_text("")
    print("  site/index.html lists: %s"
          % (", ".join("Day %d" % d for d in released_days()) or "no days"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int)
    ap.add_argument("--publish", action="store_true",
                    help="copy the built day into site/ and relist the homepage")
    ap.add_argument("--answers", action="store_true",
                    help="show the worked answers in this build")
    ap.add_argument("--unpublish", type=int, metavar="DAY")
    ap.add_argument("--home", action="store_true")
    args = ap.parse_args()

    if args.unpublish:
        target = SITE / ("day%d" % args.unpublish)
        if target.exists():
            shutil.rmtree(target)
            print("removed %s" % target.relative_to(ROOT))
        build_home()
        return
    if args.home:
        build_home()
        return
    if not args.day:
        ap.error("give --day N, --unpublish N or --home")

    book = build_day(args.day, args.answers)
    if args.publish:
        target = SITE / ("day%d" % args.day)
        if target.exists():
            shutil.rmtree(target)
        SITE.mkdir(exist_ok=True)
        shutil.copytree(book, target)
        if args.answers:
            # tells the publish workflow that answers on these pages are meant
            (target / "answers-released").write_text(
                "This day was released with its worked answers shown.\n")
        print("  published to %s" % target.relative_to(ROOT))
        build_home()
        print("\nCommit site/ and push: that is what puts it online.")
    else:
        print("\nBuilt only. Open %s/index.html to look at it;\n"
              "add --publish to release it." % book.relative_to(ROOT))


if __name__ == "__main__":
    main()
