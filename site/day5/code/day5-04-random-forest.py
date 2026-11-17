# Exercise 5.4 — Random forests and tuning with a workflow
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-04-random-forest.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-04-random-forest.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import roc_auc_score, classification_report

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["pregnant", "glucose", "mass", "pedigree", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

predictors = ["pregnant", "glucose", "mass", "pedigree", "age"]

# --------------------------------------------------------------------
# Part 1 — A random forest with tunable hyperparameters
# --------------------------------------------------------------------

rf = RandomForestClassifier(n_estimators=500, random_state=123, n_jobs=-1)
print(rf)

# --------------------------------------------------------------------
# Part 2 — The grid, the folds and the search
# --------------------------------------------------------------------

rf_grid = {"max_features":      [1, 2, 3, 4, 5],
           "min_samples_split": [2, 4, 6, 8, 10]}

rf_search = GridSearchCV(rf, param_grid=rf_grid, cv=5, scoring="roc_auc")
rf_search = rf_search.fit(train[predictors], train["diabetes"])

rf_results = pd.DataFrame(rf_search.cv_results_)
rf_results = rf_results[["param_max_features", "param_min_samples_split",
                         "mean_test_score", "std_test_score"]]
print(rf_results.round(3).to_string())

# --------------------------------------------------------------------
# Part 3 — Inspect the tuning results
# --------------------------------------------------------------------

fig, ax = plt.subplots()
for split in rf_grid["min_samples_split"]:
    rows = rf_results[rf_results["param_min_samples_split"] == split]
    ax.plot(rows["param_max_features"], rows["mean_test_score"], marker="o", label=str(split))
ax.set_xlabel("max_features (mtry)")
ax.set_ylabel("Mean cross-validated AUC")
ax.legend(title="min_samples_split")
plt.show()

# Replace every ______ below, then run this cell.
rf_results.sort_values(______, ascending=False).head(5).round(3)

# --------------------------------------------------------------------
# Part 4 — The final forest, evaluated once
# --------------------------------------------------------------------

print(rf_search.best_params_)
print("cross-validated AUC:", round(rf_search.best_score_, 3))

final_rf = rf_search.best_estimator_

train_preds = train.copy()
train_preds["prob"] = final_rf.predict_proba(train[predictors])[:, 1]
train_preds["pred_class"] = final_rf.predict(train[predictors])

test_preds = test.copy()
test_preds["prob"] = final_rf.predict_proba(test[predictors])[:, 1]
test_preds["pred_class"] = final_rf.predict(test[predictors])

truth, predicted = train_preds["diabetes"], train_preds["pred_class"]
print("train accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("train precision:  ", round(precision_score(truth, predicted), 3))
print("train sensitivity:", round(recall_score(truth, predicted), 3))
print("train specificity:", round(recall_score(truth, predicted, pos_label=0), 3))
print("train AUC:        ", round(roc_auc_score(truth, train_preds["prob"]), 3))

# Replace every ______ below, then run this cell.
truth, predicted = ______, test_preds["pred_class"]
print("test accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("test precision:  ", round(precision_score(truth, predicted), 3))
print("test sensitivity:", round(recall_score(truth, predicted), 3))
print("test specificity:", round(recall_score(truth, predicted, pos_label=0), 3))
print("test AUC:        ", round(roc_auc_score(truth, ______), 3))

# --------------------------------------------------------------------
# Part 5 — Extra: was the tuning worth it?
# --------------------------------------------------------------------

rf_basic = RandomForestClassifier(random_state=123)
rf_basic = rf_basic.fit(train[predictors], train["diabetes"])

basic_class = rf_basic.predict(test[predictors])
basic_prob  = rf_basic.predict_proba(test[predictors])[:, 1]

print("basic forest, test accuracy:", round(accuracy_score(test["diabetes"], basic_class), 3))
print("basic forest, test AUC:     ", round(roc_auc_score(test["diabetes"], basic_prob), 3))
print(classification_report(test["diabetes"], basic_class, digits=3))
