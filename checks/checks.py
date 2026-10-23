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
    "hds_check", "check_setup", "check_data", "check_split",
    "check_metric_range", "check_beats_baseline", "check_shift_answers",
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
