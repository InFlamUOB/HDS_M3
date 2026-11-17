# HDS MSc · Module 3 — exercise booklet

**Live, one address per teaching day:**
<https://inflamuob.github.io/HDS_M3/day1/> ·
<https://inflamuob.github.io/HDS_M3/day2/> ·
<https://inflamuob.github.io/HDS_M3/day3/>

A Quarto book of machine learning exercises for the Health Data Science MSc,
organised by teaching day. Each exercise is given in both R and Python. Students
read the exercise on the site and copy the code into their own script.

**Days 1 to 6 are written**: twenty-five exercises, each in both languages,
with hidden worked answers released after the session they belong to.

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

Per day, with one command:

```bash
make release DAY=1 ANSWERS=1
```

Then commit `site/` and push. Day 1's pages now show every worked answer with
its output; the other days are untouched. Run `make release DAY=1` to hide them
again. Until released, the answers are not merely collapsed — they are not in
the page at all. Leave `show-solutions: false` in `_quarto.yml`.

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

The Python side needs no decisions: `.Rprofile` declares the six libraries the
`{python}` cells use, and `reticulate` (1.41 or later) assembles a Python
environment to match on first use, fetching Python itself if the machine has
none. `scripts/setup_local.R` triggers that once so the download does not land
mid-exercise. Nothing to activate, and nothing machine-specific to commit.

These are the commands. The first two are Quarto itself, and the Preview and
Render buttons in Positron run exactly the same thing:

```bash
quarto preview                     # local site at :4200, reloads as you edit
quarto render                      # build the whole booklet into _book/ — your own preview, not published
python3 scripts/check_cells.py     # before you push: blanks, hidden answers, links
python3 scripts/check_links.py site    # dead links in what is published
```

The rest are the occasional ones:

```bash
Rscript scripts/setup_local.R                       # install R packages, settle Python
Rscript scripts/make_data.R                         # regenerate every dataset
quarto render --profile instructor                  # staff copy, into _book-instructor/
python3 scripts/new_day.py --day 2 --title "..." --exercises a,b   # next day
```

There is a `Makefile` with shortcuts for all of these — `make preview`, `make
release DAY=1`, `make check`, `make day DAY=2`, `make` for the list — but it is only a
convenience. `make` is a general build tool that ships with macOS, nothing to do
with Quarto, and the commands above are what it runs. Ignore it if you prefer.

## Publishing

Students see the folder `site/`, and nothing else. It holds one sub-folder per
released day, each a small site of its own with its own address:

```
site/day1/    https://inflamuob.github.io/HDS_M3/day1/
site/day2/    https://inflamuob.github.io/HDS_M3/day2/
```

`.github/workflows/publish.yml` publishes `site/` to GitHub Pages on every push
to `main`, exactly as committed. It does **not** build anything: you build on
your own machine, where R and Python live.

```bash
make release DAY=2             # build Day 2 into site/day2/
make release DAY=2 ANSWERS=1   # the same, showing that day's worked answers and adding the -solutions notebooks
make day-site DAY=2            # build it to look at, without releasing
make unrelease DAY=2           # take the day down
git add site && git commit -m "Release Day 2" && git push
```

**Editing a chapter and pushing it does not change what students see.** A day's
pages change only when you release that day again. That is the point: you can
keep writing Day 4 while Day 1 stays exactly as it was handed out.

There is no common index. The days do not link to each other, and the front
page lists none of them. To bring a list back, add a line containing `{{DAYS}}`
to `_home/index.qmd` and release the days again.

CI refuses to publish if a released page shows a worked answer that was not
released with `ANSWERS=1`, or shows instructor notes. Pull requests get the same
checks with deployment skipped.

## Layout

```
_quarto.yml              the whole working booklet, one part per day
_quarto-instructor.yml   instructor profile (adds the teaching notes)
_common.qmd              knitr options and the reticulate pointer, included per chapter
_templates/exercise.qmd  skeleton for a new exercise
index.qmd                how to use the booklet
day1-*.qmd  ... day6-*.qmd   the exercises, numbered N.M within each day
appendix/glossary.qmd        the glossary
checks/                  self-check helpers used inside the exercises, R and Python
scripts/make_data.R      generates every dataset from one seed
scripts/check_cells.py   the pre-push check
scripts/check_links.py   dead links and unresolved cross-references, after a render
data/                    generated CSVs, published so students can download them
site/                    what is published: one folder per released day
_home/index.qmd          the text of the front page
code/                    each chapter as an R Markdown (.Rmd) and a Jupyter (.ipynb) notebook, for download
scripts/make_day_site.py builds and releases one day
_book/                   your local render of the whole booklet; not committed, not published
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
python3 scripts/new_day.py --day 2 --title "Validation you can defend" \
    --exercises first-exercise,second-exercise
# write the chapters
python3 scripts/check_cells.py
make release DAY=2   # builds the day into site/day2/
git add -A && git commit -m "Day 2" && git push
```

