# Exercise 5.2 — Evaluating a classification model on training and test data
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-02-classification-metrics.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-02-classification-metrics.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import roc_curve, roc_auc_score

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["pregnant", "glucose", "mass", "pedigree", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

print(train["diabetes"].value_counts())
print(test["diabetes"].value_counts())

# --------------------------------------------------------------------
# Part 1 — An age-only model, and its predictions
# --------------------------------------------------------------------

age_model = LogisticRegression(C=np.inf)
age_model = age_model.fit(train[["age"]], train["diabetes"])

print("intercept:", round(age_model.intercept_[0], 4))
print("age:      ", round(age_model.coef_[0, 0], 4))

train_preds = train.copy()
train_preds["prob"] = age_model.predict_proba(train[["age"]])[:, 1]   # probability of 1
train_preds["pred_class"] = (train_preds["prob"] >= 0.5).astype(int)

train_preds.head().round(3)

test_preds = test.copy()
test_preds["prob"] = age_model.predict_proba(test[["age"]])[:, 1]
test_preds["pred_class"] = (test_preds["prob"] >= 0.5).astype(int)

test_preds["pred_class"].value_counts()

# --------------------------------------------------------------------
# Part 2 — Metrics on the training and the test rows
# --------------------------------------------------------------------

truth     = train_preds["diabetes"]
predicted = train_preds["pred_class"]

print("accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("precision:  ", round(precision_score(truth, predicted), 3))
print("recall:     ", round(recall_score(truth, predicted), 3))
print("sensitivity:", round(recall_score(truth, predicted), 3))
print("specificity:", round(recall_score(truth, predicted, pos_label=0), 3))

# Replace every ______ below, then run this cell.
truth     = ______
predicted = test_preds["pred_class"]

print("accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("precision:  ", round(precision_score(truth, predicted), 3))
print("recall:     ", round(recall_score(truth, predicted), 3))
print("sensitivity:", round(recall_score(truth, predicted), 3))
print("specificity:", round(recall_score(truth, predicted, ______), 3))

# --------------------------------------------------------------------
# Part 3 — Score distributions and the ROC curve
# --------------------------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
for ax, data, name in [(axes[0], train_preds, "Training rows"), (axes[1], test_preds, "Test rows")]:
    ax.boxplot([data.loc[data["diabetes"] == 0, "prob"], data.loc[data["diabetes"] == 1, "prob"]],
               tick_labels=["no diabetes (0)", "diabetes (1)"])
    ax.set_title(name)
    ax.set_xlabel("True class")
axes[0].set_ylabel("Predicted probability of diabetes")
plt.show()

fpr_age, tpr_age, thresholds_age = roc_curve(test_preds["diabetes"], test_preds["prob"])
auc_age = roc_auc_score(test_preds["diabetes"], test_preds["prob"])

print("test AUC, age only:", round(auc_age, 3))

fig, ax = plt.subplots(figsize=(5, 5))
ax.plot(fpr_age, tpr_age, color="black")
ax.plot([0, 1], [0, 1], color="grey", linestyle="--")
ax.set_xlabel("1 - specificity")
ax.set_ylabel("Sensitivity")
ax.set_title("ROC curve, age-only model (test rows)")
plt.show()

# Replace every ______ below, then run this cell.
auc_age_train = roc_auc_score(______, ______)

print("training AUC, age only:", round(auc_age_train, 3))

# --------------------------------------------------------------------
# Part 4 — Include more features
# --------------------------------------------------------------------

predictors = ["pregnant", "glucose", "mass", "pedigree", "age"]

rich_pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(C=np.inf)),
])
rich_pipe = rich_pipe.fit(train[predictors], train["diabetes"])

pd.Series(rich_pipe["model"].coef_[0], index=predictors).round(3)

train_preds2 = train.copy()
train_preds2["prob"] = rich_pipe.predict_proba(train[predictors])[:, 1]
train_preds2["pred_class"] = (train_preds2["prob"] >= 0.5).astype(int)

test_preds2 = test.copy()
test_preds2["prob"] = rich_pipe.predict_proba(test[predictors])[:, 1]
test_preds2["pred_class"] = (test_preds2["prob"] >= 0.5).astype(int)

for name, data in [("train", train_preds2), ("test", test_preds2)]:
    truth, predicted = data["diabetes"], data["pred_class"]
    print(name,
          "accuracy", round(accuracy_score(truth, predicted), 3),
          "precision", round(precision_score(truth, predicted), 3),
          "sensitivity", round(recall_score(truth, predicted), 3),
          "specificity", round(recall_score(truth, predicted, pos_label=0), 3))

# Replace every ______ below, then run this cell.
fpr_rich, tpr_rich, thresholds_rich = roc_curve(test_preds2["diabetes"], ______)
auc_rich = roc_auc_score(test_preds2["diabetes"], ______)

print("test AUC, five predictors:", round(auc_rich, 3))

fpr2, tpr2, thr2 = roc_curve(test_preds2["diabetes"], test_preds2["prob"])

fig, ax = plt.subplots(figsize=(5.5, 5))
ax.plot(fpr_age, tpr_age, linewidth=2, label="age only")
ax.plot(fpr2, tpr2, linewidth=2, label="five predictors")
ax.plot([0, 1], [0, 1], color="grey", linestyle="--")
ax.set_xlabel("1 - specificity")
ax.set_ylabel("Sensitivity")
ax.set_title("ROC curves on the test rows")
ax.legend()
plt.show()
