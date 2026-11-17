# Exercise 9.1 — Variable importance, and a column of pure noise
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-01-importance.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-01-importance.qmd. Edit the chapter, not this file.


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
from sklearn.inspection import permutation_importance

# --------------------------------------------------------------------
# Part 1 — The data and the forest
# --------------------------------------------------------------------

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["pregnant", "glucose", "mass", "pedigree", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

predictors = ["pregnant", "glucose", "mass", "pedigree", "age"]

train["diabetes"].value_counts()

rf = RandomForestClassifier(n_estimators=500, random_state=1)
rf = rf.fit(train[predictors], train["diabetes"])

test_prob = rf.predict_proba(test[predictors])[:, 1]    # probability of diabetes

auc_before = roc_auc_score(test["diabetes"], test_prob)
round(auc_before, 3)

# --------------------------------------------------------------------
# Part 2 — Impurity-based importance
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
impurity_importance = pd.Series(rf.______, index=predictors)

impurity_importance = impurity_importance.sort_values(ascending=False)
print(impurity_importance.round(3))
print("sum:", impurity_importance.sum().round(3))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(6, 3.5))
impurity_importance.sort_values().plot(kind="barh", ax=ax, color="steelblue")
ax.set_xlabel("Mean decrease in impurity (share of the total)")
ax.set_title("Random forest: impurity-based importance")
fig.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 3 — Permutation importance
# --------------------------------------------------------------------

rng = np.random.default_rng(1)

test_shuffled = test.copy()
test_shuffled["glucose"] = rng.permutation(test_shuffled["glucose"].values)   # glucose now belongs to someone else

auc_after = roc_auc_score(test_shuffled["diabetes"],
                          rf.predict_proba(test_shuffled[predictors])[:, 1])

print("before:", round(auc_before, 3))
print("after: ", round(auc_after, 3))
print("drop:  ", round(auc_before - auc_after, 3))

# Replace every ______ below, then run this cell.
rng = np.random.default_rng(1)

test_shuffled = test.copy()
test_shuffled["mass"] = rng.permutation(test_shuffled[______].values)

auc_after = roc_auc_score(test_shuffled["diabetes"],
                          rf.predict_proba(______[predictors])[:, 1])

print("drop:", round(auc_before - auc_after, 3))

perm = permutation_importance(rf, test[predictors], test["diabetes"],
                              scoring="roc_auc", n_repeats=20, random_state=1)

perm_importance = pd.DataFrame({"variable": predictors,
                                "importance": perm.importances_mean,
                                "sd": perm.importances_std})
perm_importance = perm_importance.sort_values("importance", ascending=False)
perm_importance.round(3)

ordered = perm_importance.sort_values("importance")

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.barh(ordered["variable"], ordered["importance"], xerr=ordered["sd"],
        color="coral", capsize=3)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Mean drop in test AUC when the variable is shuffled (± 1 SD)")
ax.set_title("Random forest: permutation importance")
fig.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 4 — A control: a column of pure noise
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
rng = np.random.default_rng(1)
train_noise = train.copy()
test_noise  = test.copy()
train_noise["noise"] = rng.normal(size=______)            # one random number per row
test_noise["noise"]  = rng.normal(size=______)

predictors_noise = predictors + ["noise"]

rf_noise = RandomForestClassifier(n_estimators=500, random_state=1)
rf_noise = rf_noise.fit(train_noise[predictors_noise], train_noise["diabetes"])

pd.Series(rf_noise.feature_importances_, index=predictors_noise).round(3)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

perm_noise = permutation_importance(rf_noise, test_noise[predictors_noise],
                                    test_noise["diabetes"], scoring="roc_auc",
                                    n_repeats=20, random_state=1)

perm_importance_noise = pd.DataFrame({"variable": predictors_noise,
                                      "importance": perm_noise.importances_mean,
                                      "sd": perm_noise.importances_std})
perm_importance_noise.sort_values("importance", ascending=False).round(3)
