# Installs everything the booklet needs on your own machine: the R packages, and
# a small Python environment that R can see.
#
#   Rscript scripts/setup_local.R      # or: make setup-r
#
# Run it once, then restart R. It is safe to run again; it only adds what is
# missing.
#
# Why a Python environment at all: the {python} cells in the chapters are
# executed through reticulate, which needs to be told which Python to use. Left
# to itself it finds whichever Python the operating system ships — on a Mac,
# usually one with no pandas — and the first `import pandas` fails. This script
# builds a dedicated environment and records it, so that question is settled
# once rather than every time you open the project.

r_pkgs  <- c("tidymodels", "tidyverse", "data.table", "rpart", "reticulate")
py_pkgs <- c("pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "joblib")
venv    <- "hds-python"

# ---- R side ----------------------------------------------------------------
missing <- r_pkgs[!vapply(r_pkgs, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) == 0) {
  message("R packages: all present (", paste(r_pkgs, collapse = ", "), ")")
} else {
  message("R packages, installing: ", paste(missing, collapse = ", "))
  install.packages(missing, repos = "https://cloud.r-project.org")
  still <- missing[!vapply(missing, requireNamespace, logical(1), quietly = TRUE)]
  if (length(still)) {
    stop("Failed to install: ", paste(still, collapse = ", "),
         "\nInstall them from the Packages pane and run this again.")
  }
}

# ---- Python side -----------------------------------------------------------
# virtualenv_starter() asks reticulate for a Python it considers usable as a
# base; Sys.which() is the fallback when it finds none.
base <- tryCatch(reticulate::virtualenv_starter(), error = function(e) NULL)
if (length(base) == 0 || is.na(base[1]) || !nzchar(base[1])) {
  base <- Sys.which("python3")
}
if (!nzchar(base[1])) {
  stop("No Python found to build the environment from.\n",
       "Install Python 3 (python.org, or `brew install python` on a Mac), ",
       "then run this script again.")
}
base <- as.character(base[1])

if (reticulate::virtualenv_exists(venv)) {
  message("Python environment '", venv, "': exists, checking packages")
} else {
  message("Python environment '", venv, "': creating from ", base)
  reticulate::virtualenv_create(venv, python = base)
}
ok <- tryCatch({
  reticulate::virtualenv_install(venv, packages = py_pkgs)
  TRUE
}, error = function(e) {
  message("\nInstalling the Python packages failed:\n  ", conditionMessage(e))
  message("\nThe two usual causes:")
  message("  * no network, or a proxy that intercepts HTTPS — on a university")
  message("    network pip may report an SSL certificate error. Try again off VPN,")
  message("    or ask IT for the pip proxy settings.")
  message("  * the base Python is too old. Check with: ", base, " --version")
  message("\nYou can also install them by hand and re-run this script:")
  message("  ", reticulate::virtualenv_python(venv),
          " -m pip install ", paste(py_pkgs, collapse = " "))
  FALSE
})
if (!ok) stop("Python packages not installed; see above.")

# ---- Tell every R session in this project which Python to use --------------
# .Renviron is read by R at startup. It holds a path specific to this machine,
# so it is not committed.
py_path <- reticulate::virtualenv_python(venv)
line    <- sprintf('RETICULATE_PYTHON="%s"', py_path)
existing <- if (file.exists(".Renviron")) readLines(".Renviron", warn = FALSE) else character()
keep <- existing[!grepl("^\\s*RETICULATE_PYTHON\\s*=", existing)]
writeLines(c(keep, line), ".Renviron")

message("\nPython: ", py_path)
message("Recorded in .Renviron (this machine only; not committed).")
message("\nNow restart R — Session > Restart R, or the circular arrow in the\n",
        "console pane — so it picks that up. Then run the checks in setup.qmd.")
