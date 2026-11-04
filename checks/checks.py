"""Self-check helpers for the Module 3 booklet (Python side).

    import sys; sys.path.append("checks")
    from checks import *

These are not a grading system. They are a way of finding out, in the five
seconds after you write a line of code, whether the object you just made is the
object the next step expects. Every check prints what it looked at, so a
failure tells you where to look rather than only that something is wrong.
"""

import codecs
import re

import numpy as np
import pandas as pd

__all__ = [
    "hds_check",
    "check_setup",
    "check_data",
    "check_split",
    "check_metric_range",
    "check_beats_baseline",
    "check_shift_answers",
    "check_matches",
    "check_probabilities",
    "check_beats_prevalence",
    "check_overfit_gap",
    "check_noise_control",
    "check_gap_vs_noise",
    "check_selection",
]


def hds_check(label, ok, hint="", detail=""):
    ok = bool(ok)
    mark = "[ok]  " if ok else "[fix] "
    print(f"{mark}{label}" + (f"  ({detail})" if detail else ""))
    if not ok and hint:
        print(f"       hint: {hint}")
    return ok


def check_setup():
    import importlib
    for p in ["pandas", "numpy", "sklearn", "matplotlib", "joblib"]:
        try:
            m = importlib.import_module(p)
            hds_check(f"package '{p}' available", True,
                      detail=getattr(m, "__version__", ""))
        except ImportError:
            hds_check(f"package '{p}' available", False,
                      hint=f"pip install {p}  (see the Setup chapter)")


def check_data(df, n_expected=1000):
    hds_check("data is a DataFrame", isinstance(df, pd.DataFrame),
              hint="did pd.read_csv() succeed? check the file path")
    if not isinstance(df, pd.DataFrame):
        return
    hds_check("columns are Age, Severity, LOS",
              sorted(df.columns) == ["Age", "LOS", "Severity"],
              hint="check you loaded los_data.csv and not something else",
              detail=", ".join(df.columns))
    hds_check(f"has {n_expected} rows", len(df) == n_expected,
              hint="a short file usually means the download was interrupted",
              detail=f"{len(df)} rows")
    hds_check("no missing values", not df.isna().any().any(),
              hint="decide what to do about them before modelling, not after")


def check_split(X_train, X_test, X_full, prop=0.8, tol=0.02):
    n = len(X_train) + len(X_test)
    hds_check("train and test together use every row exactly once",
              n == len(X_full),
              hint="you have either dropped rows or sampled with replacement",
              detail=f"{len(X_train)} + {len(X_test)} = {n} vs {len(X_full)}")
    hds_check(f"training share is about {prop}",
              abs(len(X_train) / n - prop) < tol,
              hint="check the test_size= argument of train_test_split()",
              detail=f"{len(X_train) / n:.3f}")
    try:
        shared = set(X_train.index) & set(X_test.index)
    except AttributeError:
        shared = set()
    hds_check("no row appears in both sets", len(shared) == 0,
              hint="this is the single most common way to fool yourself in ML",
              detail=f"{len(shared)} shared index labels")


def check_metric_range(value, lo, hi, label="metric"):
    ok = np.isscalar(value) and lo <= float(value) <= hi
    hds_check(f"{label} is in the expected range [{lo}, {hi}]", ok,
              hint="if it is far too good, suspect leakage; if far too bad, "
                   "suspect the formula or the column names",
              detail=f"{float(value):.3f}" if np.isscalar(value) else type(value).__name__)


def check_beats_baseline(mae_model, mae_baseline):
    hds_check("the model beats the predict-the-mean baseline",
              mae_model < mae_baseline,
              hint="a model that does not beat the baseline has learnt nothing worth having",
              detail=f"model {mae_model:.2f} vs baseline {mae_baseline:.2f} "
                     f"({100 * mae_model / mae_baseline:.0f}% of the baseline error)")


def check_shift_answers(answers):
    """answers: dict like {"A": "none", "B": "covariate", "C": "concept"}

    The key is lightly obscured so that reading this file does not hand over
    the answer to Exercise 1.3.
    """
    key = {k: codecs.encode(v, "rot13")
           for k, v in {"A": "abar", "B": "pbinevngr", "C": "pbaprcg"}.items()}

    def norm(x):
        x = str(x).strip().lower()
        x = re.sub(r"[ _-]*shift$", "", x).strip()
        if x.startswith("no"):
            return "none"
        if x.startswith("cov"):
            return "covariate"
        if x.startswith("con"):
            return "concept"
        return x

    n_right = sum(norm(answers.get(k, "")) == v for k, v in key.items())
    print(f"you got {n_right} of 3 right.")
    if n_right < 3:
        print("Before you guess again: the two questions are separate.\n"
              " 1. Did the PATIENTS change?   compare the Age and Severity distributions.\n"
              " 2. Did the RULES change?      refit the model on the extract and compare\n"
              "                               its coefficients with the original ones.")
    else:
        print("All three. Note which evidence settled each one - that is the "
              "transferable part.")
    return n_right


# ---------------------------------------------------------------------------
# Added for Days 2-6.
# ---------------------------------------------------------------------------


def check_matches(value, target, tol=0.01, label="value"):
    """Day 3: did the number you computed yourself land on the number a standard
    routine gives? Used for gradient descent against lm()/LinearRegression, and
    for a closed-form estimator against the fitted model. `tol` is relative to
    the target, with a floor of 1 so that a target of zero still has a sensible
    tolerance.
    """
    limit = tol * max(1, abs(target))
    ok = np.isscalar(value) and np.isfinite(value) and abs(value - target) <= limit
    hds_check(f"{label} matches the reference answer", ok,
              hint="a gap much larger than the tolerance usually means too few "
                   "iterations, a learning rate that is too small, or a sign "
                   "error in the gradient",
              detail=(f"{float(value):.4f} vs {float(target):.4f} "
                      f"(gap {abs(float(value) - float(target)):.4g}, allowed {limit:.4g})")
                     if np.isscalar(value) else type(value).__name__)
    return ok


def check_probabilities(p, prevalence, tol=0.02):
    """p: predicted probabilities of the POSITIVE class. prevalence: observed rate."""
    p = np.asarray(p, dtype=float).ravel()
    ok_range = p.size > 0 and bool(((p >= 0) & (p <= 1)).all())
    hds_check("every value is a probability between 0 and 1", ok_range,
              hint="you may have kept the log-odds, or a class label, instead of a "
                   "probability",
              detail=f"range {p.min():.3f} to {p.max():.3f}" if p.size else "empty")
    if not ok_range:
        return
    hds_check("the mean predicted probability matches the observed prevalence",
              abs(p.mean() - prevalence) < tol,
              hint="a logistic regression with an intercept averages to the prevalence "
                   "on its training rows; if yours averages to one minus that, you have "
                   "taken the other probability column",
              detail=f"mean {p.mean():.3f} vs prevalence {prevalence:.3f}")


def check_beats_prevalence(accuracy, truth):
    """Day 5: compare an accuracy against the majority-class rule.

    `truth` is the vector of true labels for the rows the accuracy was
    computed on; the bar is the share of the commonest class in it.
    """
    truth = pd.Series(np.asarray(truth))
    majority = truth.value_counts(normalize=True).max()
    hds_check("the model beats the majority-class rule",
              np.isscalar(accuracy) and float(accuracy) > majority,
              hint="predicting the commonest class for everyone needs no data and "
                   "no model; an accuracy below that bar means the model has "
                   "learnt nothing usable",
              detail=f"model {float(accuracy):.3f} vs majority-class {majority:.3f} "
                     f"({100 * (float(accuracy) - majority):+.1f} percentage points)")
    return majority


def check_overfit_gap(train_score, test_score, max_gap=0.05, label="score"):
    """Day 5: the gap between a fitted-rows score and a held-out score.

    Pass scores where higher is better (accuracy, AUC).
    """
    gap = float(train_score) - float(test_score)
    hds_check(f"train-minus-test gap in {label} is under {max_gap}",
              np.isfinite(gap) and gap < max_gap,
              hint="a wide gap means the model has fitted rows it will never see "
                   "again; the cure is less capacity, not more training",
              detail=f"train {float(train_score):.3f}, test {float(test_score):.3f}, "
                     f"gap {gap:+.3f}")
    return gap


def check_noise_control(importance, noise="noise", tol=0.1):
    """Day 6: where did the pure-noise control land?

    A control column of random numbers is added to the predictors, and every
    importance measure is asked where it put it. `importance` is a pandas
    Series (or a dict) whose index is the predictor names. The check passes
    when the control is worth less than `tol` of the strongest predictor. A
    [fix] here is not necessarily a mistake in your code - read the detail
    line, and the chapter.
    """
    s = pd.Series(importance)
    if noise not in s.index:
        return hds_check(f"the control column '{noise}' is present", False,
                         hint="add it to the predictors before fitting, or set "
                              "noise= to its name",
                         detail=", ".join(map(str, s.index)))
    s = s.sort_values(ascending=False)
    rank = list(s.index).index(noise) + 1
    share = s[noise] / s.iloc[0]
    hds_check(f"the pure-noise control is worth less than {round(100 * tol)}% "
              "of the top predictor",
              share < tol,
              hint="this measure gives a column of random numbers a real share "
                   "of the credit, so it is describing the model rather than "
                   "the data",
              detail=f"'{noise}' ranks {rank} of {len(s)}, {100 * share:.0f}% of "
                     f"'{s.index[0]}' ({s[noise]:.4g} vs {s.iloc[0]:.4g})")
    return share


def check_gap_vs_noise(observed, null_values, label="gap"):
    """Day 6: an observed gap between subgroups, against the gap that appears
    when the groups are made up.

    `null_values` is the vector of gaps produced by shuffling the group labels
    (or by any other procedure under which there is nothing to find). A [fix]
    here means the observed gap sits inside the noise floor, which at these
    sample sizes is the usual result and not a mistake in your code - read the
    detail line, and the chapter.
    """
    null_values = np.asarray(null_values, dtype=float).ravel()
    null_values = null_values[np.isfinite(null_values)]
    usable = (np.isscalar(observed) and np.isfinite(observed)
              and null_values.size > 1)
    if not usable:
        return hds_check(f"{label} can be compared with a noise floor", False,
                         hint="pass one observed gap and a vector of gaps from "
                              "permuted labels; a nan usually means a subgroup "
                              "had only one class",
                         detail=f"observed {observed}, {null_values.size} usable "
                                "null values")
    q95 = float(np.quantile(null_values, 0.95))
    p = (float((null_values >= observed).sum()) + 1) / (null_values.size + 1)
    hds_check(f"{label} is larger than the gap chance alone produces",
              float(observed) > q95,
              hint="a gap inside the noise floor is not a finding; report the "
                   "intervals and the group sizes, not the ordering",
              detail=f"observed {float(observed):.3f}, median null "
                     f"{float(np.median(null_values)):.3f}, 95th centile {q95:.3f}, "
                     f"p = {p:.3f} ({null_values.size} permutations)")
    return p


def check_selection(coefficients, controls=("noise",), label="the penalised fit"):
    """Day 5: which predictors did a penalised fit actually keep?

    `coefficients` is a pandas Series (or a dict) whose index is the predictor
    names. `controls` names the columns known to carry no signal. The check
    passes when none of them survived, and reports how many real predictors
    were dropped alongside them, because that is the price. A [fix] here is not
    necessarily a mistake in your code - read the detail line, and the chapter.
    """
    s = pd.Series(coefficients).drop(labels=["(Intercept)", "intercept"],
                                     errors="ignore")
    controls = list(controls)
    absent = [c for c in controls if c not in s.index]
    if absent:
        return hds_check("every control column is present", False,
                         hint="add the controls to the predictors before fitting, "
                              "or set controls= to their names",
                         detail="missing: " + ", ".join(map(str, absent)))
    kept = [c for c in controls if s[c] != 0]
    real = [c for c in s.index if c not in controls]
    dropped = [c for c in real if s[c] == 0]
    hds_check(f"{label} kept none of the {len(controls)} controls",
              len(kept) == 0,
              hint="a penalty chosen to predict well is not chosen to select "
                   "variables; look at what the whole path does before you "
                   "report a variable list",
              detail=f"controls kept: {', '.join(kept) if kept else 'none'}; "
                     f"real predictors dropped: "
                     f"{', '.join(dropped) if dropped else 'none'}")
    return {"controls_kept": kept, "dropped": dropped}
