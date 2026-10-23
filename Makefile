# Everything you need for a teaching day. Run `make` for the list.
#
#   make setup-r            install the R packages used off-browser
#   make preview            live-reloading local site (the one you work in)
#   make site               build the student booklet into _book/
#   make instructor         build the staff copy into _book-instructor/
#   make worksheets DAY=1   printable PDFs for one day
#   make day DAY=2 TITLE="..."  scaffold the next day and register it
#   make data               regenerate every dataset from scripts/make_data.R
#   make check              source checks (live cells, links), before you push
#   make code DAY=1         write the day's code out as plain R and Python scripts
#   make links              check the built site for dead links
#   make all DAY=1          data + site + instructor + worksheets
#   make clean              remove build output

DAY ?= 1
TITLE ?= Title of the day
QUARTO ?= quarto
PYTHON ?= python3
RSCRIPT ?= Rscript

.DEFAULT_GOAL := help
.PHONY: help setup-r preview site instructor worksheets day data check code links all clean

help:
	@grep -E '^#   make' $(MAKEFILE_LIST) | sed 's/^#   //'

setup-r:
	$(RSCRIPT) scripts/setup_local.R

preview:
	$(QUARTO) preview

site:
	$(QUARTO) render --to html

instructor:
	$(QUARTO) render --to html --profile instructor

worksheets:
	$(PYTHON) scripts/make_worksheet.py --day $(DAY) --profile student
	$(PYTHON) scripts/make_worksheet.py --day $(DAY) --profile instructor
	$(QUARTO) render print/day$(DAY)-student.qmd    --to typst
	$(QUARTO) render print/day$(DAY)-instructor.qmd --to typst
	@$(PYTHON) -c "import re,sys; \
	  d=open('print/day$(DAY)-student.pdf','rb').read(); \
	  n=max(int(m.group(1)) for m in re.finditer(rb'/Count (\d+)', d)); \
	  print(f'day $(DAY) student worksheet: {n} pages'); \
	  sys.exit(0 if n <= 20 else 1)" \
	  || (echo 'The worksheet is over twenty pages. Move narrative into a ::: {.web-only} block rather than cutting tasks.'; exit 1)

day:
	$(PYTHON) scripts/new_day.py --day $(DAY) --title "$(TITLE)"

data:
	$(RSCRIPT) scripts/make_data.R

# The same gate the publish workflow applies.
check:
	@$(PYTHON) scripts/check_cells.py

# Needs a build: checks the rendered HTML for links whose target is missing and
# for cross-references Quarto could not resolve.
code:
	@$(PYTHON) scripts/make_code.py --day $(DAY)

links:
	@$(PYTHON) scripts/check_links.py _book

all: data site links instructor worksheets

clean:
	rm -rf _book _book-instructor _freeze .quarto print/.quarto print/*.typ
