# Exercise 9.4 — For whom is the model worst?
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-04-subgroups.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-04-subgroups.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["pregnant", "glucose", "mass", "pedigree", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

predictors = ["pregnant", "glucose", "mass", "pedigree", "age"]

rf = RandomForestClassifier(n_estimators=500, random_state=1)
rf = rf.fit(train[predictors], train["diabetes"])

test_preds = test.copy()
test_preds["prob"] = rf.predict_proba(test[predictors])[:, 1]   # probability of diabetes
test_preds["pred"] = rf.predict(test[predictors])               # predicted class, threshold 0.5

# --------------------------------------------------------------------
# Part 1 — Performance by age group
# --------------------------------------------------------------------

test_preds["age_group"] = pd.cut(test_preds["age"], bins=[20, 29, 39, np.inf],
                                 labels=["21-29", "30-39", "40 and over"])

test_preds.groupby("age_group", observed=False).agg(
    patients=("diabetes", "size"),
    with_diabetes=("diabetes", "sum"))

rows = []
for group, patients in test_preds.groupby("age_group", observed=False):
    has_diabetes = patients["diabetes"] == 1
    flagged      = patients["pred"] == 1
    rows.append({"age_group": group,
                 "roc_auc": roc_auc_score(patients["diabetes"], patients["prob"]),
                 "sens": (has_diabetes & flagged).sum() / has_diabetes.sum(),
                 "spec": (~has_diabetes & ~flagged).sum() / (~has_diabetes).sum()})

by_age = pd.DataFrame(rows)
by_age.round(3)

groups = ["21-29", "30-39", "40 and over"]
fig, ax = plt.subplots(figsize=(7, 3.5))
for shift, outcome, colour in [(-0.2, 0, "tab:blue"), (0.2, 1, "tab:red")]:
    for i, group in enumerate(groups):
        values = test_preds.loc[(test_preds["age_group"] == group) &
                                (test_preds["diabetes"] == outcome), "prob"]
        ax.boxplot(values, positions=[i + shift], widths=0.3, showfliers=False)
        ax.scatter(np.full(len(values), i + shift), values, color=colour, alpha=0.5,
                   label=("diabetes" if outcome == 1 else "no diabetes") if i == 0 else None)
ax.axhline(0.5, color="black", linestyle="--")
ax.set_xticks(range(len(groups)))
ax.set_xticklabels(groups)
ax.set_xlabel("Age group")
ax.set_ylabel("Predicted probability of diabetes")
ax.legend(title="Diabetes", loc="center left", bbox_to_anchor=(1, 0.5))
fig.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 2 — By BMI, and how far to trust a small group
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
test_preds["bmi_group"] = np.where(test_preds["mass"] < ______, "under 30", "30 and over")

rows = []
for group, patients in test_preds.groupby(______):
    has_diabetes = patients["diabetes"] == 1
    flagged      = patients["pred"] == 1
    rows.append({"bmi_group": group,
                 "patients": len(patients),
                 "with_diabetes": has_diabetes.sum(),
                 "roc_auc": roc_auc_score(patients["diabetes"], patients["prob"]),
                 "sens": (has_diabetes & flagged).sum() / has_diabetes.sum(),
                 "spec": (~has_diabetes & ~flagged).sum() / (~has_diabetes).sum()})

pd.DataFrame(rows).round(3)
