# HDS MSc · Module 3 — interactive exercise booklet

**Live: <https://inflamuob.github.io/HDS_M3/>**

A Quarto book of machine learning exercises for the Health Data Science MSc,
organised by teaching day. **Every code cell runs in the reader's browser** —
R via webR, Python via Pyodide — so students install nothing before the first
session. Each exercise has an R path and a Python path.

**Day 1 is complete.** Later days are placeholders: see `roadmap.qmd` and the
*Adding a day* appendix.

## Running it

Install [Quarto](https://quarto.org/docs/get-started/) — that is the only
requirement, because nothing in the booklet executes at render time. **Quarto
1.4 or newer**, which is what the Quarto Live extension needs; CI builds with
1.7.32. Check yours with `quarto --version`.

`make doctor` reports all of this for your machine and prints the exact install
command for anything missing. It changes nothing.

R and Python are *not* needed to build or preview the site. They are needed only
to run `scripts/make_data.R`, or to work through the exercises on your own
machine rather than in the browser. Nothing here uses `reticulate` or a conda
environment: the browser runtimes replaced both.

```bash
make preview        # local site at http://localhost:4200, reloads as you edit
make site           # build the student booklet into _book/
make instructor     # build the staff copy into _book-instructor/
make worksheets     # printable PDFs for Day 1 (override with DAY=2)
make check          # the gates CI applies, before you push
make                # the full list
```

`make preview` is the one you work in: edit a chapter, save, and the page
reloads with your live cells working exactly as a student will see them.

## Editing in Positron or RStudio

Open `HDS_M3.Rproj`. Both editors then treat this as a project with the working
directory at the project root, which is what every path in the booklet assumes —
getting that wrong is the usual cause of "file not found" when editing Quarto by
hand.

The **Render** and **Preview** buttons act on the whole book, via `_quarto.yml`,
and are equivalent to `make preview`.

One thing that surprises people: the editor will *not* offer to run the
` ```{webr} ` and ` ```{pyodide} ` cells in your local R or Python session, and
there is no "Run cell" button on them. That is correct — those cells exist to be
executed by the reader's browser, and the chapters pin `engine: markdown` so
nothing is executed at render time either. To try a cell's code against real R or
Python, paste it into the console. That is also how changes should be checked
before they are pushed: the code in a live cell is never exercised by rendering,
so rendering cleanly is no evidence that it works.

## Working on this together

This repository is the single source of truth. Two people edit it — whoever is
at the keyboard, and an assistant working through the GitHub API — and anything
that reaches `main` is published automatically. That works as long as both
sides follow the same small discipline.

**Editing on your machine**

```bash
git pull                       # ALWAYS first: the assistant may have pushed
# ... edit the .qmd files, `make preview` to see them ...
make check                     # catches the faults that only show up in a browser
make test-cells DAY=1          # if you touched code: runs the live cells for real
git add -A && git commit -m "what changed and why"
git pull --rebase              # again, in case something landed while you worked
git push
```

The two `git pull`s are the whole protocol. Skipping the first means editing a
stale file; skipping the second means a rejected push and a merge to untangle.

**When the assistant edits**

It reads the current state from GitHub rather than any copy it holds, so it
cannot overwrite work it has not seen, and it never force-pushes. Anything
beyond a small fix arrives as a **pull request** rather than a push to `main`,
so you see the diff and decide what lands. Merge it on GitHub, then `git pull`
locally.

**If you are both editing at once**

Different files are fine; git merges them without help. The same file at the
same time is the one case that needs care — say which chapter you are working
in, and the other side stays out of it. There is no locking.

**What is never committed**

`_book/`, `_book-instructor/`, `_freeze/`, `.quarto/` and `print/` are build
output, all listed in `.gitignore`. Only sources belong in the repository; the
site is rebuilt from them on every push.

## Publishing

The repository ships a GitHub Actions workflow, `.github/workflows/publish.yml`,
that renders the student booklet and deploys it to GitHub Pages on every push to
`main`. It needs no secrets and no R or Python, and it runs in under a minute.

This is already configured for this repository (Settings → Pages → Build and
deployment → Source: GitHub Actions); a fresh fork needs that setting once. After that, adding a day is `git push` and the site
rebuilds itself. The instructor build is deliberately *not* produced in CI — it
is local-only, so solutions cannot reach the public site.

If you would rather publish by hand, `quarto publish gh-pages` also works; it
pushes the rendered output to a `gh-pages` branch. Do not mix the two
approaches in one repository — pick whichever matches how `HDS_Intro` is already
set up.

> Two things the workflow guards, because they are invisible until a student
> clicks something: that no chapter has slipped back to a server-executed
> `{r}` chunk, and that the live cells pass `scripts/check_cells.py`.

## Build targets in detail

```bash
quarto render                                     # student site -> _book/
quarto render --profile instructor                # staff copy   -> _book-instructor/

python3 scripts/make_worksheet.py --day 1 --profile student
quarto render print/day1-student.qmd --to typst   # 14-page worksheet
```

Publish `_book/` only. The Quarto Live extension is committed in
`_extensions/live/`, so no `quarto add` step is needed on a fresh clone or in
CI. The printable worksheets use Typst, which Quarto bundles, so they need no
LaTeX.

## Layout

```
_quarto.yml              book structure (one part per day), runtime package lists,
                         and the resource list mounted into the browser
_quarto-instructor.yml   the instructor profile
_extensions/live/        Quarto Live (webR + Pyodide)
_templates/exercise.qmd  skeleton for a new exercise
index.qmd                how to use the booklet
day1-*.qmd               Day 1: overview, three exercises, consolidation
roadmap.qmd              the intended arc of the remaining days
setup.qmd                installing R and Python locally (optional for students)
appendix/                data provenance, troubleshooting, glossary,
                         adding a day, instructor guide
checks/                  self-check helpers, R and Python, kept in step
scripts/make_data.R      generates every dataset from one seed
scripts/make_worksheet.py builds the printable worksheet from the chapters
data/                    generated CSVs (committed, so everyone's are identical)
print/                   generated worksheet sources — do not edit by hand
```

## Design decisions worth knowing before you edit

- **Chapters live at the project root**, named `dayN-nn-slug.qmd`. Not in folders:
  live cells fetch data relative to the page and write it to the same path in the
  browser filesystem, so a flat layout keeps one path string working in the
  browser, in RStudio and in the worksheet.
- **Each page is a separate browser session.** Exercise 1.3 therefore rebuilds its
  model in the first cell instead of loading one saved in 1.2.
- **A solution cell must run standalone.** Clicking *Solution* replaces the
  editor's contents and runs them.
- **The browser loads `parsnip`, `rsample` and `yardstick` rather than the
  `tidymodels` metapackage** — 50 WebAssembly packages (48 MB) against 81 (82 MB).
  Locally, use `library(tidymodels)`; nothing else changes.
- **All data is simulated by one seeded script.** That is what makes the expected
  values in the instructor guide quotable and lets Exercise 1.3 have a checkable
  right answer. `scripts/make_data.R` contains that answer — exclude `scripts/`
  from the published site if that matters to you.
- **Expected values are quoted as ranges**, because changing an `n` in
  `make_data.R` shifts the random stream downstream.
- **The worksheet is generated, not maintained.** Edit the chapter, re-run
  `make_worksheet.py`.

## Adding a day

```bash
make day DAY=2                 # scaffolds the chapters and registers them
# ... write the chapters ...
make check                     # catches the mistakes that only show up in a browser
make worksheets DAY=2          # fails if the worksheet exceeds twenty pages
git push                       # the site rebuilds itself
```

`make day` creates `day2-00-overview.qmd`, one chapter per exercise you name, and
`day2-99-consolidation.qmd`, then inserts the `part:` block into `_quarto.yml`.
It is safe to re-run: existing files are left alone.

`make check` is the part worth knowing about. It catches six faults that render
cleanly and then fail in front of a student: a chapter missing its `engine:
markdown` front matter, two exercises sharing a key on one page, a hint or solution
whose key has no exercise, an exercise with no `______` to fill in, a solution
that cannot run standalone because the cell it replaces did the imports, a data
file used but not mounted into the browser, and a package used but absent from
the runtime list.

Still manual: append any new data to `scripts/make_data.R`, register that file
under both `resources:` keys, and add any new check to **both**
`checks/checks.R` and `checks/checks.py`. The *Adding a day* appendix is the full procedure, including
the live-cell options and the three rules that are easy to get wrong.
