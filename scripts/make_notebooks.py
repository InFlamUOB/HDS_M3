#!/usr/bin/env python3
"""Write one R Markdown notebook and one Jupyter notebook per chapter.

    python3 scripts/make_notebooks.py              # every chapter offering a download
    python3 scripts/make_notebooks.py day3-02-loss-functions.qmd

Writes code/<chapter>.Rmd (the R version of the exercise) and
code/<chapter>.ipynb (the Python version). Each holds the whole exercise as a
student sees it in that language: the text, the questions, the tasks with their
______ blanks, and every code cell in page order, including the code for the
plots. Students who only have the notebook therefore have the whole exercise.

Left out: the other language, worked answers (show-solutions blocks) and
instructor notes. Quarto-only markup is turned into plain Markdown: callouts
become quoted blocks with a bold title, language tabs and side-by-side columns
keep only the matching language.

The notebooks are saved without outputs. The chapters are the single source of
truth: do not edit the generated files; edit the chapter and re-run.
scripts/check_cells.py checks that they are current.

--test DIR writes the same notebooks with the worked answers in place of the
fill-in cells (exactly what a render executes) into DIR, for checking that
every notebook runs from top to bottom.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "code"
SITE = "https://inflamuob.github.io/HDS_M3/"
EXT = {"r": ".Rmd", "python": ".ipynb"}
LABEL = {"r": "R", "python": "Python"}
CALLOUT_NAME = {"note": "Note", "tip": "Tip", "important": "Important",
                "warning": "Warning", "caution": "Caution"}


def offers_download(path):
    """Does this chapter link to its own notebooks?"""
    return "](code/%s." % path.stem in path.read_text()


def live_chapters():
    """Chapters that offer a download link, which is what decides the scope."""
    return [p.name for p in sorted(ROOT.glob("day*.qmd")) if offers_download(p)]


def day_of(stem):
    """The 'Day N' part of _quarto.yml that lists this chapter (day6-* is Day 9)."""
    part = None
    for line in (ROOT / "_quarto.yml").read_text().splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.match(r'- part:\s*"Day (\d+)\b', s)
        if m:
            part = m.group(1)
        elif part and s == f"- {stem}.qmd":
            return part
    m = re.match(r"day(\d+)-", stem)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- parsing
def parse(lines, i=0, until_close=False):
    """Lines -> list of nodes: ('text', line) | ('chunk', lang, body_lines) |
    ('div', attrs, children). Returns (nodes, next_index)."""
    nodes = []
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^```\{(\w+)[^}]*\}\s*$", line)
        if m:
            j = i + 1
            body = []
            while j < len(lines) and not re.match(r"^```\s*$", lines[j]):
                body.append(lines[j])
                j += 1
            nodes.append(("chunk", m.group(1), body))
            i = j + 1
            continue
        if re.match(r"^```", line):              # plain (non-executed) code block
            j = i + 1
            block = [line]
            while j < len(lines) and not re.match(r"^```\s*$", lines[j]):
                block.append(lines[j])
                j += 1
            if j < len(lines):
                block.append(lines[j])
            nodes += [("text", b) for b in block]
            i = j + 1
            continue
        # a closing fence is checked first: `^:{3,}\s*\S` would match `::::`
        if re.match(r"^:{3,}\s*$", line):
            if until_close:
                return nodes, i + 1
            i += 1
            continue
        m = re.match(r"^:{3,}\s*(\S.*?)\s*$", line)
        if m:
            children, i = parse(lines, i + 1, until_close=True)
            nodes.append(("div", m.group(1), children))
            continue
        nodes.append(("text", line))
        i += 1
    return nodes, i


def chunk_langs(nodes):
    found = set()
    for n in nodes:
        if n[0] == "chunk":
            found.add(n[1])
        elif n[0] == "div":
            found |= chunk_langs(n[2])
    return found


def first_text(nodes):
    for n in nodes:
        if n[0] == "text" and n[1].strip():
            return n[1].strip()
        if n[0] != "text":
            return None
    return None


# ---------------------------------------------------------------- one language
def clean_md(line):
    """Quarto-only markup -> plain Markdown."""
    if re.match(r"^\{\{<.*>\}\}\s*$", line):                 # shortcodes
        return None
    if re.match(r"^:\s*\{tbl-[^}]*\}\s*$", line):             # table attributes
        return None
    line = re.sub(r"\s*\{#[\w-]+[^}]*\}\s*$", "", line)       # heading anchors
    line = re.sub(r"\)\{[^}]*\}", ")", line)                  # link attributes
    line = re.sub(r"\[([^\]]+)\]\{\.[^}]*\}", r"\1", line)    # [text]{.class}
    return line


def reference(nodes, lang, quote):
    """The other language's code, shown but not run, for chapters that compare
    the two languages side by side."""
    other = "python" if lang == "r" else "r"
    out = []
    for n in nodes:
        if n[0] == "chunk" and n[1] == other:
            body = [b for b in n[2] if not b.startswith("#|") and not re.match(
                r"#\s*(Packages for this exercise|install\.packages|pip install|\(in a Jupyter)", b)]
            while body and not body[0].strip():
                body.pop(0)
            if not any("______" in b for b in body) and any(b.strip() for b in body):
                out += [("md", "", quote),
                        ("md", f"*For comparison, the same step in {LABEL[other]} "
                               "(not run here):*", quote), ("md", "", quote),
                        ("md", "```" + other, quote)]
                out += [("md", b, quote) for b in body]
                out += [("md", "```", quote), ("md", "", quote)]
        elif n[0] == "div" and not ("show-solutions" in n[1] or "when-profile" in n[1]
                                    or "instructor" in n[1]):
            out += reference(n[2], lang, quote)
    return out


COMPARE = False      # set per chapter: does it put the two languages side by side?
SOLUTIONS = False    # set by build(): the "-solutions" notebooks, answers filled in


def view(nodes, lang, test=False, quote=0):
    """Flatten the tree for one language into ('md', line, quote_depth) and
    ('code', body_lines) items."""
    out = []
    for n in nodes:
        kind = n[0]
        if kind == "text":
            t = clean_md(n[1])
            if t is not None:
                out.append(("md", t, quote))
        elif kind == "chunk":
            if n[1] != lang:
                continue
            body = n[2]
            opts = " ".join(b for b in body if b.startswith("#|"))
            if re.search(r"#\|\s*(echo|include):\s*false", opts):
                continue
            is_task = any("______" in b for b in body)
            if (test or SOLUTIONS) and is_task:
                continue                     # the worked answer comes instead
            if test and re.search(r"#\|\s*eval:\s*false", opts):
                continue                     # not run on the page either
            out.append(("code", body, is_task))
        else:
            attrs, children = n[1], n[2]
            if "show-solutions" in attrs and "content-visible" in attrs:
                if test:
                    out += [x for x in view(children, lang, test, quote) if x[0] == "code"]
                elif SOLUTIONS:
                    out += view(children, lang, test, quote)
                continue
            if "show-solutions" in attrs and "content-hidden" in attrs and SOLUTIONS:
                continue                     # e.g. "Released after the session"
            if "when-profile" in attrs or "instructor" in attrs:
                continue
            if "panel-tabset" in attrs:
                out += view(tab_for(children, lang), lang, test, quote)
                if COMPARE and not test:
                    other = "python" if lang == "r" else "r"
                    out += reference(tab_for(children, other), lang, quote)
            elif attrs.strip() == "columns" or ".columns" in attrs:
                for col in children:
                    if col[0] != "div":
                        continue
                    got = col_lang(col[2])
                    if got == lang:
                        kids = col[2]
                        label = first_text(kids)
                        if label in ("**R**", "**Python**"):
                            kids = drop_first_text(kids)
                        out += view(kids, lang, test, quote)
                if COMPARE and not test:
                    out += reference([c for c in children if c[0] == "div"
                                      and col_lang(c[2]) not in (lang, None)], lang, quote)
            elif "callout" in attrs:
                out += callout(attrs, children, lang, test, quote)
            else:
                out += view(children, lang, test, quote)
    return out


def tab_for(children, lang):
    """The children of a tabset that belong to the tab for `lang`."""
    want = LABEL[lang]
    tabs, cur = {}, None
    for n in children:
        if n[0] == "text":
            m = re.match(r"^#{2,3}\s+(R|Python)\s*$", n[1])
            if m:
                cur = m.group(1)
                tabs[cur] = []
                continue
        if cur:
            tabs[cur].append(n)
    return tabs.get(want, children if not tabs else [])


def col_lang(kids):
    langs = chunk_langs(kids)
    if langs == {"r"}:
        return "r"
    if langs == {"python"}:
        return "python"
    label = first_text(kids)
    if label == "**R**":
        return "r"
    if label == "**Python**":
        return "python"
    return None


def drop_first_text(kids):
    out, dropped = [], False
    for n in kids:
        if not dropped and n[0] == "text" and n[1].strip():
            dropped = True
            continue
        out.append(n)
    return out


def callout(attrs, children, lang, test, quote):
    kind = re.search(r"callout-(\w+)", attrs)
    title = CALLOUT_NAME.get(kind.group(1), "Note") if kind else "Note"
    kids = list(children)
    for k, n in enumerate(kids):
        if n[0] == "text" and n[1].strip():
            m = re.match(r"^#{2,4}\s+(.*)$", n[1])
            if m:
                title = clean_md(m.group(1))
                kids = kids[:k] + kids[k + 1:]
            break
    folded = any(n[0] == "text" and "folded away" in n[1] for n in kids)
    if title == "The plots are for looking at" or folded:
        body = [("md", "The code for every plot is included, so that you can run "
                       "it and see the figure. You are not expected to write it "
                       "yourself.", quote + 1)]
        return [("md", "", quote), ("md", f"**{title}**", quote + 1), ("md", "", quote + 1)] + body
    return ([("md", "", quote), ("md", f"**{title}**", quote + 1), ("md", "", quote + 1)]
            + view(kids, lang, test, quote + 1))


# ---------------------------------------------------------------- assembling
def extract(path, lang, test=False):
    """(title, items) for one chapter in one language."""
    text = path.read_text()
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    nodes, _ = parse(text.splitlines())
    # Chapters that set the languages side by side (several small tabs, or
    # columns) also show the other language's code, not run, for comparison.
    global COMPARE
    tabsets = len(re.findall(r"^:{3,}\s*\{?\.?panel-tabset", text, re.M))
    COMPARE = tabsets > 1 or bool(re.search(r"^:{3,}\s*columns", text, re.M))
    items = view(nodes, lang, test)
    title, rest = None, []
    for it in items:
        if it[0] == "md" and title is None:
            m = re.match(r"^#\s+(.*)$", it[1])
            if m:
                title = m.group(1).strip()
                continue
        if it[0] == "md" and "](code/" in it[1]:
            continue                    # the page's own download links
        rest.append(it)
    return title or path.stem, rest


def cells(items):
    """Group items into ('markdown', lines) and ('code', lines, is_task) cells."""
    out, md = [], []
    for it in items:
        if it[0] == "md":
            _, line, q = it
            md.append(("> " * q + line).rstrip() if q else line)
        else:
            if md:
                out.append(("markdown", md))
                md = []
            out.append(("code", it[1], it[2]))
    if md:
        out.append(("markdown", md))
    tidy = []
    for c in out:
        if c[0] == "markdown":
            lines = c[1]
            # collapse runs of blank (or blank quoted) lines, trim the ends
            keep = []
            for line in lines:
                blank = not line.strip(" >")
                if blank and (not keep or not keep[-1].strip(" >")):
                    continue
                keep.append(line)
            while keep and not keep[-1].strip(" >"):
                keep.pop()
            if keep:
                tidy.append(("markdown", keep))
        else:
            tidy.append(c)
    return tidy


def intro(stem, lang):
    day = day_of(stem)
    url = f"{SITE}day{day}/{stem}.html" if day else SITE
    where = ("Open it in Positron or RStudio and run it a chunk at a time"
             if lang == "r" else
             "Open it in Jupyter, VS Code or Positron and run it a cell at a time")
    return [f"*HDS MSc · Module 3 · the {LABEL[lang]} version of this exercise; "
            f"the web page is at <{url}>.*", "",
            f"*{where}. Keep it in the folder that holds your `data` folder. "
            + ("This version has the worked answers filled in.*" if SOLUTIONS else
               "Cells with `______` are blanks for you to fill in.*")]


def option_lines(body, keep):
    """Chunk options: Rmd keeps knitr's `#|` lines (minus page-only ones);
    notebooks drop them all."""
    out = []
    for b in body:
        if b.startswith("#|"):
            if not keep or re.match(r"#\|\s*code-(fold|summary)", b):
                continue
            if re.match(r"#\|\s*eval:\s*false", b) and any("______" in x for x in body):
                continue              # a filled-in task should run when knitted
        out.append(b)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def to_rmd(stem, title, items):
    head = ["---", f'title: "{title}"', "output: html_document", "---", ""]
    body = intro(stem, "r") + [""]
    for c in cells(items):
        if c[0] == "markdown":
            body += c[1] + [""]
        else:
            body += ["```{r}"] + option_lines(c[1], keep=True) + ["```", ""]
    return "\n".join(head + body).rstrip() + "\n"


def to_ipynb(stem, title, items):
    def src(lines):
        return [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else []
    nb_cells = [{"cell_type": "markdown", "metadata": {},
                 "source": src([f"# {title}", ""] + intro(stem, "python"))}]
    for c in cells(items):
        if c[0] == "markdown":
            nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": src(c[1])})
        else:
            nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                             "outputs": [], "source": src(option_lines(c[1], keep=False))})
    nb = {"cells": nb_cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    for k, c in enumerate(nb["cells"]):
        c["id"] = f"cell-{k:03d}"
    return json.dumps(nb, indent=1, ensure_ascii=False) + "\n"


def build(path, test=False, solutions=False):
    """{dest filename: text} for one chapter (languages without code are skipped).
    solutions=True gives the "-solutions" notebooks: worked answers in place of
    the fill-in cells, with their explanation. They are published only when a
    day is released with its answers (make release DAY=n ANSWERS=1)."""
    global SOLUTIONS
    SOLUTIONS = solutions
    stem = path.stem
    files = {}
    try:
        for lang, ext in EXT.items():
            title, items = extract(path, lang, test)
            if not any(it[0] == "code" for it in items):
                continue
            if solutions:
                title += " (with solutions)"
            name = stem + ("-solutions" if solutions else "") + ext
            files[name] = (to_rmd if lang == "r" else to_ipynb)(stem, title, items)
    finally:
        SOLUTIONS = False
    return files


def all_files(path):
    """Student and solution notebooks for one chapter."""
    files = build(path)
    files.update(build(path, solutions=True))
    return files


def main(argv):
    test_dir = None
    if "--test" in argv:
        k = argv.index("--test")
        test_dir = pathlib.Path(argv[k + 1])
        argv = argv[:k] + argv[k + 2:]
    targets = argv[1:] or live_chapters()
    out = test_dir or OUT
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name in targets:
        path = ROOT / name
        files = build(path, test=True) if test_dir else all_files(path)
        if not test_dir:
            for ext in EXT.values():                 # drop a language that has gone
                for stale in (OUT / (path.stem + ext), OUT / (path.stem + "-solutions" + ext)):
                    if stale.name not in files and stale.exists():
                        stale.unlink()
        for fname, text in files.items():
            (out / fname).write_text(text)
            written.append(str((out / fname).relative_to(ROOT) if not test_dir else out / fname))
    print("\n".join(written) or "nothing to write")


if __name__ == "__main__":
    main(sys.argv)
