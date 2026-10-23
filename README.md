# HDS MSc · Module 3 — exercise booklet

**Live: <https://inflamuob.github.io/HDS_M3/>**

A Quarto book of machine learning exercises for the Health Data Science MSc,
organised by teaching day. Each exercise is given in both R and Python. Students
read the exercise on the site and copy the code into their own script.

**Day 1 is complete.** Later days are placeholders: see `roadmap.qmd` and the
*Adding a day* appendix.

## How it works

The chapters are ordinary Quarto documents with `{r}` and `{python}` chunks, so
**you can run any cell in Positron as you write it** — the same file is what
builds the website.

- **Worked examples** execute when you render, so the site shows each one with
  its output: the printed table, the MAE, the plot.
- **Tasks** are chunks marked `eval: false` containing `______` for the student
  to fill in. They display as code and are never run.
- **Worked answers** sit in `::: {.content-visible when-meta="show-solutions"}`
  blocks. They are *absent from the published HTML* until you release them.

### Releasing the answers after a session

One line in `_quarto.yml`:

```yaml
show-solutions: true
```

Then `make site` and push. The site rebuilds with every worked answer and its
output visible. Set it back to `false`, render and push to hide them again. Until then the answers are
not merely collapsed — they are not in the page at all.

## Running it

Install [Quarto](https://quarto.org/docs/get-started/) 1.4 or newer, plus R and
a Python environment, since the chapters execute when rendered:

```r
install.packages(c("tidymodels", "tidyverse", "data.table", "rpart", "reticulate"))
```

Or do both in one step, including the Python side, with:

```r
source("scripts/setup_local.R")   # or: make setup-r
```

It builds a Python environment called `hds-python` from whatever Python you
have, installs the six libraries, and writes `RETICULATE_PYTHON` into
`.Renviron` so every R session in the project uses it. Restart R afterwards.
`.Renviron` is machine-specific and is not committed.

```bash
make preview        # http://localhost:4200, reloads as you edit
make site           # build into _book/
make check          # before you push
make                # every command
```

## Publishing

`.github/workflows/publish.yml` publishes to GitHub Pages on every push to
`main`. It does **not** build the site: you render on your own machine, where R
and Python live, and commit `_book/`; the job publishes that folder. Students
therefore see byte for byte what you saw locally, with no dependence on which
Quarto version a runner installs.

That is the one obligation this design carries: **after changing a chapter, run
`make site` and commit `_book/` with it.** CI refuses to publish if `_book/` is
missing, or if any `.qmd` is newer than the rendered site.

Pull requests get the same checks and the same render with deployment skipped,
so a change can be proved before it publishes.

## Layout

```
_quarto.yml              book structure, one part per day; the show-solutions switch
_quarto-instructor.yml   instructor profile (adds the teaching notes)
_common.qmd              knitr options and the reticulate pointer, included per chapter
_templates/exercise.qmd  skeleton for a new exercise
index.qmd                how to use the booklet
day1-*.qmd               Day 1: overview, three exercises, consolidation
roadmap.qmd              the intended arc of the remaining days
setup.qmd                installing R and Python (written for students)
appendix/                data provenance, troubleshooting, glossary,
                         adding a day, instructor guide
checks/                  self-check helpers used inside the exercises, R and Python
scripts/make_data.R      generates every dataset from one seed
scripts/check_cells.py   the pre-push check
scripts/check_links.py   dead links and unresolved cross-references, after a render
data/                    generated CSVs, published so students can download them
_book/                   the rendered site, committed; this is what gets published
```

## Design decisions worth knowing before you edit

- **Chapters live at the project root**, named `dayN-nn-slug.qmd`.
- **Paths are relative to the project root** (`execute-dir: project`), which is
  why opening `HDS_M3.Rproj` matters.
- **All data is simulated by one seeded script**, which is what makes the
  expected values in the instructor guide quotable and gives Exercise 1.3 a
  checkable right answer. `scripts/make_data.R` contains that answer — exclude
  `scripts/` from the published site if that matters to you.
- **Expected values are quoted as ranges**, because changing an `n` in
  `make_data.R` shifts the random stream downstream.
- **A hint names the function, never the line.** Hints are always visible, so a
  hint containing the answer publishes the answer.

## Adding a day

```bash
make day DAY=2 TITLE="Validation you can defend"
# write the chapters
make check
make site            # executes them; commit _book/ with your changes
git push
```
