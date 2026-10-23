# ---------------------------------------------------------------------------
# checks.R - self-check helpers for the Module 3 booklet (R side)
#
#   source("checks/checks.R")
#
# These are not a grading system. They are a way of finding out, in the five
# seconds after you write a line of code, whether the object you just made is
# the object the next step expects. Every check prints what it looked at, so a
# failure tells you where to look rather than only that something is wrong.
# ---------------------------------------------------------------------------

hds_check <- function(label, ok, hint = "", detail = "") {
  ok <- isTRUE(ok)
  mark <- if (ok) "[ok]  " else "[fix] "
  cat(mark, label, if (nzchar(detail)) paste0("  (", detail, ")") else "", "\n", sep = "")
  if (!ok && nzchar(hint)) cat("       hint: ", hint, "\n", sep = "")
  invisible(ok)
}

check_setup <- function() {
  pkgs <- c("tidymodels", "ggplot2", "readr", "dplyr")
  for (p in pkgs) {
    hds_check(paste0("package '", p, "' available"),
              requireNamespace(p, quietly = TRUE),
              hint = paste0('install.packages("', p, '")'))
  }
  have_retic <- requireNamespace("reticulate", quietly = TRUE)
  hds_check("package 'reticulate' available", have_retic,
            hint = 'install.packages("reticulate")')
  if (have_retic) {
    ok <- tryCatch({ reticulate::py_run_string("import sklearn, pandas"); TRUE },
                   error = function(e) FALSE)
    hds_check("Python can be reached from R, with pandas and scikit-learn", ok,
              hint = "run source(\"scripts/setup_local.R\") and restart R; check with reticulate::py_config()")
  }
  invisible(NULL)
}

check_data <- function(df, n_expected = 1000) {
  hds_check("data is a data frame", is.data.frame(df),
            hint = "did read_csv() succeed? check the file path")
  if (!is.data.frame(df)) return(invisible(FALSE))
  hds_check("columns are Age, Severity, LOS",
            identical(sort(names(df)), c("Age", "LOS", "Severity")),
            hint = "check you loaded los_data.csv and not something else",
            detail = paste(names(df), collapse = ", "))
  hds_check(paste0("has ", n_expected, " rows"), nrow(df) == n_expected,
            hint = "a short file usually means the download was interrupted",
            detail = paste(nrow(df), "rows"))
  hds_check("no missing values", !anyNA(df),
            hint = "decide what to do about them before modelling, not after")
  invisible(NULL)
}

check_split <- function(train, test, full, prop = 0.8, tol = 0.02) {
  n <- nrow(train) + nrow(test)
  hds_check("train and test together use every row exactly once",
            n == nrow(full),
            hint = "you have either dropped rows or sampled with replacement",
            detail = paste0(nrow(train), " + ", nrow(test), " = ", n,
                            " vs ", nrow(full)))
  hds_check(paste0("training share is about ", prop),
            abs(nrow(train) / n - prop) < tol,
            hint = "check the prop= argument of initial_split()",
            detail = sprintf("%.3f", nrow(train) / n))
  # Row names are no help here: rsample's training()/testing() both return
  # tibbles numbered from 1. Compare the rows themselves instead - an inner join
  # on every column returns the rows the two sets have in common.
  shared <- nrow(merge(as.data.frame(train), as.data.frame(test)))
  hds_check("no row appears in both sets", shared == 0,
            hint = "this is the single most common way to fool yourself in ML",
            detail = paste(shared, "rows found in both sets"))
  invisible(NULL)
}

check_metric_range <- function(value, lo, hi, label = "metric") {
  hds_check(paste0(label, " is in the expected range [", lo, ", ", hi, "]"),
            is.numeric(value) && length(value) == 1 && value >= lo && value <= hi,
            hint = "if it is far too good, suspect leakage; if far too bad, suspect the formula or the column names",
            detail = if (is.numeric(value)) sprintf("%.3f", value[1]) else class(value))
  invisible(NULL)
}

check_beats_baseline <- function(mae_model, mae_baseline) {
  hds_check("the model beats the predict-the-mean baseline",
            mae_model < mae_baseline,
            hint = "a model that does not beat the baseline has learnt nothing worth having",
            detail = sprintf("model %.2f vs baseline %.2f (%.0f%% of the baseline error)",
                             mae_model, mae_baseline, 100 * mae_model / mae_baseline))
  invisible(NULL)
}

# Exercise 1.3: answers are checked against a lightly obscured key so that
# reading this file does not hand over the answer. Give one of
# "none", "covariate", "concept" for each extract, e.g.
#   check_shift_answers(c(A = "none", B = "covariate", C = "concept"))
check_shift_answers <- function(answers) {
  key <- vapply(c(A = "abar", B = "pbinevngr", C = "pbaprcg"),
                function(x) chartr("a-zA-Z", "n-za-mN-ZA-M", x), character(1))
  norm <- function(x) {
    x <- tolower(trimws(as.character(x)))
    x <- sub("[ _-]*shift$", "", x)
    x <- sub("^no.*", "none", x)
    x <- sub("^cov.*", "covariate", x)
    x <- sub("^con?cept.*", "concept", x)
    trimws(x)
  }
  given <- norm(answers[names(key)])
  n_right <- sum(given == key, na.rm = TRUE)
  cat("you got ", n_right, " of 3 right.\n", sep = "")
  if (n_right < 3) {
    cat("Before you guess again: the two questions are separate.\n",
        " 1. Did the PATIENTS change?   compare the Age and Severity distributions.\n",
        " 2. Did the RULES change?      refit the model on the extract and compare\n",
        "                               its coefficients with the original ones.\n", sep = "")
  } else {
    cat("All three. Note which evidence settled each one - that is the transferable part.\n")
  }
  invisible(n_right)
}
