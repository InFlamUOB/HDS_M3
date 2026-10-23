# Installs everything the booklet needs on your own machine, and proves it works.
#
#   Rscript scripts/setup_local.R      # or: make setup-r
#
# Safe to run again; it only adds what is missing.
#
# The R packages are installed from CRAN. The Python side needs no action from
# you: .Rprofile declares the libraries the {python} cells use, and reticulate
# assembles a Python environment to match — downloading Python itself if your
# machine has none. This script simply triggers that once, so the first cell you
# run in a session is not the one that waits for the download.

r_pkgs  <- c("tidymodels", "tidyverse", "data.table", "rpart", "reticulate")
py_pkgs <- c("pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "joblib")

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
if (nzchar(Sys.getenv("RETICULATE_PYTHON"))) {
  message("\nRETICULATE_PYTHON is set, so that Python is used as is:\n  ",
          Sys.getenv("RETICULATE_PYTHON"),
          "\nUnset it (or clear it from .Renviron) to let reticulate manage one.")
} else if (exists("py_require", envir = asNamespace("reticulate"))) {
  message("\nPython: asking reticulate for an environment with ",
          paste(py_pkgs, collapse = ", "))
  message("The first time, this downloads Python and the libraries — a few minutes.")
  reticulate::py_require(py_pkgs)
  ok <- tryCatch({
    reticulate::py_run_string("import pandas, numpy, matplotlib, seaborn, sklearn, joblib")
    TRUE
  }, error = function(e) {
    message("\nCould not build the Python environment:\n  ", conditionMessage(e))
    message("\nThe usual cause is the network: a proxy that intercepts HTTPS will ",
            "break\nthe download. Try again off VPN, or ask IT for the proxy settings.")
    FALSE
  })
  if (!ok) stop("Python environment not ready; see above.")
  cfg <- reticulate::py_config()
  message("Python ready: ", cfg$python)
  message("pandas ", reticulate::py_eval("__import__('pandas').__version__"),
          ", scikit-learn ", reticulate::py_eval("__import__('sklearn').__version__"))
} else {
  # reticulate older than 1.41 cannot assemble an environment on its own.
  message("\nreticulate ", as.character(utils::packageVersion("reticulate")),
          " is older than 1.41.")
  message("Update it with install.packages(\"reticulate\"), restart R, and run ",
          "this again\n— that is much easier than building an environment by hand.")
}

message("\nDone. Restart R, then open a chapter and run its first cell.")
