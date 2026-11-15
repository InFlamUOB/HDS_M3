# Everything you need for a teaching day. Run `make` for the list.
#
#   make setup-r            install the R packages and settle the Python side
#   make preview            the whole booklet, reloading as you edit — not published
#   make book               build the whole booklet into _book/ to read — not published
#   make day-site DAY=1     build one day as its own site, to look at before releasing
#   make release DAY=1      build that day and put it in site/ — commit and push to publish
#   make release DAY=1 ANSWERS=1   the same, with that day's worked answers shown
#   make release DAY=2 UNLISTED=1  online at its own address, but not on the homepage
#   make unrelease DAY=3    take a day off the site
#   make instructor         build the staff copy into _book-instructor/
#   make day DAY=2 TITLE="..."  scaffold the next day and register it
#   make data               regenerate every dataset from scripts/make_data.R
#   make data-zip           rebuild hds-m3-data.zip
#   make check              source checks (blanks, hidden answers, links)
#   make links              check site/ for dead links
#   make clean              remove build output (never site/)

DAY ?= 1
TITLE ?= Title of the day
ANSWERS ?=
UNLISTED ?=
QUARTO ?= quarto
PYTHON ?= python3
RSCRIPT ?= Rscript

.DEFAULT_GOAL := help
.PHONY: help setup-r preview book day-site release unrelease instructor day data data-zip check links clean

help:
	@grep -E '^#   make' $(MAKEFILE_LIST) | sed 's/^#   //'

setup-r:
	$(RSCRIPT) scripts/setup_local.R

# The whole booklet is your working copy. Students never see _book/.
preview:
	$(QUARTO) preview

book: data-zip
	$(QUARTO) render --to html

# One day, as a site of its own. Each released day lives at its own address,
# site/day<N>/, and changes only when you release that day again.
day-site:
	$(PYTHON) scripts/make_day_site.py --day $(DAY) $(if $(ANSWERS),--answers,)

release:
	$(PYTHON) scripts/make_day_site.py --day $(DAY) --publish $(if $(ANSWERS),--answers,) $(if $(UNLISTED),--unlisted,)
	@$(PYTHON) scripts/check_links.py site

unrelease:
	$(PYTHON) scripts/make_day_site.py --unpublish $(DAY)

instructor:
	$(QUARTO) render --to html --profile instructor

day:
	$(PYTHON) scripts/new_day.py --day $(DAY) --title "$(TITLE)"

data:
	$(RSCRIPT) scripts/make_data.R

# The same gate the publish workflow applies.
check:
	@$(PYTHON) scripts/check_cells.py

# Checks the published folder for links whose target is missing and
# for cross-references Quarto could not resolve.
links:
	@$(PYTHON) scripts/check_links.py site

clean:
	rm -rf _book dist _book-instructor _freeze .quarto
