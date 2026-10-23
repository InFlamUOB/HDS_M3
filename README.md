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

Commit, push, and the site rebuilds with every worked answer and its output
visible. Set it back to `false` to hide them again. Until then the answers are
not merely collapsed — they are not in the page at all.

## Running it

Install [Quarto](https://quarto.org/docs/get-started/) 1.4 or newer, plus R and
a Python environment, since the chapters execute when rendered:

```r
install.packages(c("tidymodels", "tidyverse", "data.table", "rpart", "reticulate"))
```

```bash
conda create -n hds-python python=3.11 numpy pandas matplotlib seaborn scikit-learn joblib
```

Set `HDS_PYTHON_ENV` in `.Renviron` if your environment has another name;
`_common.qmd` points `reticulate` at it.

```bash
make preview        # http://localhost:4200, reloads as you edit
make site           # build into _book/
make check          # before you push
make                # every command
```

## Publishing

`.github/workflows/publish.yml` renders and deploys to GitHub Pages on every
push to `main`. It does **not** execute the chapters: the executed results live
in `_freeze/`, which is committed, so the job needs Quarto alone.

That is the one obligation this design carries: **after changing a chapter's
code, render locally (`make site`) and commit `_freeze/`**, or the published
output will be stale. CI fails if `_freeze/` is missing altogether.

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
_freeze/                 executed chapter output, committed so CI need not run code
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
make site            # executes them; commit _freeze/ with your changes
git push
```
