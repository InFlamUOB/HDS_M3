# Installs the R packages the booklet uses outside the browser.
#
#   Rscript scripts/setup_local.R      # or: make setup-r
#
# Only needed to regenerate the datasets (scripts/make_data.R) or to work the
# exercises in RStudio rather than in the page. Building and previewing the
# site needs no R at all.

pkgs <- c("tidymodels", "tidyverse", "data.table", "rpart")
missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]

if (length(missing) == 0) {
  message("All four already installed: ", paste(pkgs, collapse = ", "))
} else {
  message("Installing: ", paste(missing, collapse = ", "))
  install.packages(missing, repos = "https://cloud.r-project.org")
  still <- missing[!vapply(missing, requireNamespace, logical(1), quietly = TRUE)]
  if (length(still)) {
    stop("Failed to install: ", paste(still, collapse = ", "),
         "\nInstall them from RStudio's Packages pane and run again.")
  }
  message("Done.")
}
