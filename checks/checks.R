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


# ---------------------------------------------------------------------------
# Added for Days 2-6.
# ---------------------------------------------------------------------------

# Day 3: did the number you computed yourself land on the number a standard
# routine gives? Used for gradient descent against lm(), and for a closed-form
# estimator against the fitted model. `tol` is relative to the target, with a
# floor of 1 so that a target of zero still has a sensible tolerance.
check_matches <- function(value, target, tol = 0.01, label = "value") {
  limit <- tol * max(1, abs(target))
  ok <- is.numeric(value) && length(value) == 1 && is.finite(value) &&
        abs(value - target) <= limit
  hds_check(paste0(label, " matches the reference answer"), ok,
            hint = "a gap much larger than the tolerance usually means too few iterations, a learning rate that is too small, or a sign error in the gradient",
            detail = if (is.numeric(value) && length(value) == 1)
              sprintf("%.4f vs %.4f (gap %.4g, allowed %.4g)",
                      value[1], target, abs(value[1] - target), limit)
            else class(value))
  invisible(ok)
}

check_probabilities <- function(p, prevalence, tol = 0.02) {
  ok_range <- is.numeric(p) && length(p) > 0 && all(p >= 0 & p <= 1)
  hds_check("every value is a probability between 0 and 1", ok_range,
            hint = "you may have kept the log-odds, or a class label, instead of a probability",
            detail = if (is.numeric(p)) sprintf("range %.3f to %.3f", min(p), max(p)) else class(p))
  if (!ok_range) return(invisible(FALSE))
  hds_check("the mean predicted probability matches the observed prevalence",
            abs(mean(p) - prevalence) < tol,
            hint = "a logistic regression with an intercept averages to the prevalence on its training rows; if yours averages to one minus that, you have taken the other probability column",
            detail = sprintf("mean %.3f vs prevalence %.3f", mean(p), prevalence))
  invisible(NULL)
}

# Day 5: a classifier's accuracy is only meaningful next to the accuracy of
# predicting the commonest class for everybody. `truth` is the vector of true
# labels for the rows the accuracy was computed on.
check_beats_prevalence <- function(accuracy, truth) {
  truth    <- as.factor(truth)
  majority <- max(table(truth)) / length(truth)
  hds_check("the model beats the majority-class rule",
            is.numeric(accuracy) && length(accuracy) == 1 && accuracy > majority,
            hint = paste("predicting the commonest class for everyone needs no data and no model;",
                         "an accuracy below that bar means the model has learnt nothing usable"),
            detail = sprintf("model %.3f vs majority-class %.3f (%+.1f percentage points)",
                             accuracy, majority, 100 * (accuracy - majority)))
  invisible(majority)
}

# Day 5: the gap between a score on the rows a model was fitted to and the same
# score on held-out rows. Pass scores where higher is better (accuracy, AUC).
check_overfit_gap <- function(train_score, test_score, max_gap = 0.05,
                              label = "score") {
  gap <- train_score - test_score
  hds_check(paste0("train-minus-test gap in ", label, " is under ", max_gap),
            is.numeric(gap) && length(gap) == 1 && is.finite(gap) && gap < max_gap,
            hint = paste("a wide gap means the model has fitted rows it will never see again;",
                         "the cure is less capacity, not more training"),
            detail = sprintf("train %.3f, test %.3f, gap %+.3f",
                             train_score, test_score, gap))
  invisible(gap)
}

# Day 6: a control column of random numbers is added to the predictors, and
# every importance measure is asked where it put it. `importance` is either a
# named numeric vector or a data frame with columns Variable and Importance
# (what vip::vi() returns). The check passes when the control is worth less
# than `tol` of the strongest predictor. A [fix] here is not necessarily a
# mistake in your code - read the detail line and @sec-importance.
check_noise_control <- function(importance, noise = "noise", tol = 0.1) {
  if (is.data.frame(importance)) {
    v <- stats::setNames(importance$Importance, importance$Variable)
  } else {
    v <- importance
  }
  if (!is.numeric(v) || is.null(names(v))) {
    return(invisible(hds_check("importance is a named numeric vector", FALSE,
      hint = "pass vi(fit), or a vector whose names are the predictors")))
  }
  if (!noise %in% names(v)) {
    return(invisible(hds_check(paste0("the control column '", noise, "' is present"), FALSE,
      hint = "add it to the predictors before fitting, or set noise= to its name",
      detail = paste(names(v), collapse = ", "))))
  }
  v <- sort(v, decreasing = TRUE)
  rank <- which(names(v) == noise)
  share <- unname(v[[noise]] / v[[1]])
  hds_check(paste0("the pure-noise control is worth less than ",
                   round(100 * tol), "% of the top predictor"),
            share < tol,
            hint = paste0("this measure gives a column of random numbers a real share of ",
                          "the credit, so it is describing the model rather than the data"),
            detail = sprintf("'%s' ranks %d of %d, %.0f%% of '%s' (%.4g vs %.4g)",
                             noise, rank, length(v), 100 * share, names(v)[1],
                             v[[noise]], v[[1]]))
  invisible(share)
}

# Day 6: an observed gap between subgroups, against the gap that appears when
# the groups are made up. `null_values` is the vector of gaps produced by
# shuffling the group labels (or by any other procedure under which there is
# nothing to find). A [fix] here means the observed gap sits inside the noise
# floor, which at these sample sizes is the usual result and not a mistake in
# your code - read the detail line and @sec-subgroups.
check_gap_vs_noise <- function(observed, null_values, label = "gap") {
  null_values <- null_values[is.finite(null_values)]
  usable <- is.numeric(observed) && length(observed) == 1 &&
            is.finite(observed) && length(null_values) > 1
  if (!usable) {
    return(invisible(hds_check(
      paste0(label, " can be compared with a noise floor"), FALSE,
      hint = paste("pass one observed gap and a vector of gaps from permuted",
                   "labels; an NA usually means a subgroup had only one class"),
      detail = sprintf("observed %s, %d usable null values",
                       paste(format(observed), collapse = ", "), length(null_values)))))
  }
  q95 <- unname(stats::quantile(null_values, 0.95))
  p   <- (sum(null_values >= observed) + 1) / (length(null_values) + 1)
  hds_check(paste0(label, " is larger than the gap chance alone produces"),
            observed > q95,
            hint = paste("a gap inside the noise floor is not a finding;",
                         "report the intervals and the group sizes, not the ordering"),
            detail = sprintf("observed %.3f, median null %.3f, 95th centile %.3f, p = %.3f (%d permutations)",
                             observed, stats::median(null_values), q95, p,
                             length(null_values)))
  invisible(p)
}

# Day 5: which predictors did a penalised fit actually keep? `coefficients` is
# either a named numeric vector or a data frame with columns term and estimate
# (what tidy() returns for a glmnet fit). `controls` names the columns known to
# carry no signal. The check passes when none of them survived, and reports how
# many real predictors were dropped alongside them, because that is the price.
# A [fix] here is not necessarily a mistake in your code - read the detail line
# and @sec-regularisation.
check_selection <- function(coefficients, controls = "noise",
                            label = "the penalised fit") {
  v <- if (is.data.frame(coefficients)) {
    stats::setNames(coefficients$estimate, coefficients$term)
  } else {
    coefficients
  }
  if (!is.numeric(v) || is.null(names(v))) {
    return(invisible(hds_check("coefficients is a named numeric vector", FALSE,
      hint = "pass tidy(fit), or a vector whose names are the predictors")))
  }
  v <- v[names(v) != "(Intercept)"]
  absent <- setdiff(controls, names(v))
  if (length(absent)) {
    return(invisible(hds_check("every control column is present", FALSE,
      hint = "add the controls to the predictors before fitting, or set controls= to their names",
      detail = paste0("missing: ", paste(absent, collapse = ", ")))))
  }
  kept    <- controls[v[controls] != 0]
  real    <- setdiff(names(v), controls)
  dropped <- real[v[real] == 0]
  hds_check(paste0(label, " kept none of the ", length(controls), " controls"),
            length(kept) == 0,
            hint = paste("a penalty chosen to predict well is not chosen to select variables;",
                         "look at what the whole path does before you report a variable list"),
            detail = sprintf("controls kept: %s; real predictors dropped: %s",
                             if (length(kept)) paste(kept, collapse = ", ") else "none",
                             if (length(dropped)) paste(dropped, collapse = ", ") else "none"))
  invisible(list(controls_kept = kept, dropped = dropped))
}
