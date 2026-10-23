# Read by R whenever it starts in this project folder — Positron, RStudio or the
# terminal. Its one job is to declare which Python libraries the {python} cells
# need. reticulate (1.41 and later) then assembles a matching Python environment
# the first time Python is used, downloading Python itself if the machine has
# none, and caches it. There is nothing to install by hand and nothing to
# activate.
#
# If you have set RETICULATE_PYTHON to a Python of your own, that wins and this
# does nothing.

local({
  pkgs <- c("pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "joblib")
  if (nzchar(Sys.getenv("RETICULATE_PYTHON"))) return(invisible(NULL))
  if (!requireNamespace("reticulate", quietly = TRUE)) return(invisible(NULL))
  if (!exists("py_require", envir = asNamespace("reticulate"))) {
    message("reticulate is older than 1.41: run source(\"scripts/setup_local.R\") ",
            "to build the Python environment explicitly.")
    return(invisible(NULL))
  }
  try(reticulate::py_require(pkgs), silent = TRUE)
})
