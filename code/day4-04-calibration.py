# Exercise 4.4 — Is a predicted 0.7 worth 0.7?
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-04-calibration.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-04-calibration.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["glucose", "mass", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes_dummy"] = (diabetes["diabetes"] == "pos").astype(int) # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

log_fit = LogisticRegression(C=np.inf)
log_fit = log_fit.fit(train[["glucose"]], train["diabetes_dummy"])

train_preds = train.copy()
train_preds["prob"] = log_fit.predict_proba(train[["glucose"]])[:, 1]
test_preds = test.copy()
test_preds["prob"] = log_fit.predict_proba(test[["glucose"]])[:, 1]

# --------------------------------------------------------------------
# Part 1 — Calibration in the large
# --------------------------------------------------------------------

print("training rows: mean predicted", round(train_preds["prob"].mean(), 4),
      "| prevalence", round(train_preds["diabetes_dummy"].mean(), 4))
print("test patients: mean predicted", round(test_preds["prob"].mean(), 4),
      "| prevalence", round(test_preds["diabetes_dummy"].mean(), 4))

# --------------------------------------------------------------------
# Part 2 — The calibration table, step by step
# --------------------------------------------------------------------

test_binned = test_preds.copy()
test_binned["bin"] = pd.cut(test_binned["prob"], bins=[0, 0.2, 0.4, 0.6, 0.8, 1],
                            include_lowest=True)

test_binned[["glucose", "diabetes_dummy", "prob", "bin"]].head()

# Replace every ______ below, then run this cell.
calibration_table = (test_binned
    .groupby("bin", observed=False)
    .agg(n=("prob", "size"),
         mean_predicted=("prob", "mean"),
         observed_rate=("______", "mean"))
    .reset_index())

calibration_table.round(3)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(5, 5))
ax.plot([0, 1], [0, 1], linestyle="--", color="grey")
ax.plot(calibration_table["mean_predicted"], calibration_table["observed_rate"],
        color="steelblue")
ax.scatter(calibration_table["mean_predicted"], calibration_table["observed_rate"],
           s=calibration_table["n"] * 5, color="steelblue")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel("Mean predicted probability in the bin")
ax.set_ylabel("Observed rate in the bin")
plt.show()

# --------------------------------------------------------------------
# Part 3 — Same order, different numbers
# --------------------------------------------------------------------

test_preds["squashed"] = 0.5 + (test_preds["prob"] - 0.5) / 3

print("before:", round(test_preds["prob"].min(), 3), "to", round(test_preds["prob"].max(), 3))
print("after: ", round(test_preds["squashed"].min(), 3), "to", round(test_preds["squashed"].max(), 3))
print("same order:", (test_preds["prob"].rank() == test_preds["squashed"].rank()).all())

# Replace every ______ below, then run this cell.
brier_before = ((test_preds["prob"] - test_preds["diabetes_dummy"]) ** 2).mean()
brier_after  = ((______ - test_preds["diabetes_dummy"]) ** 2).mean()

print("Brier before:", round(brier_before, 3))
print("Brier after: ", round(brier_after, 3))

truth = test_preds["diabetes_dummy"]
for threshold in [0.2, 0.5]:
    for name in ["prob", "squashed"]:
        p = test_preds[name]
        tested = (p >= threshold).sum()
        cost = 5 * ((truth == 1) & (p < threshold)).sum() + ((truth == 0) & (p >= threshold)).sum()
        label = "before" if name == "prob" else "after "
        print(f"threshold {threshold}, {label}: {tested} tested, cost {cost}")
