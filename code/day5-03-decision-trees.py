# Exercise 5.3 — Decision trees, overfitting and tuning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-03-decision-trees.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-03-decision-trees.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix, roc_auc_score

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
# Part 1 — A basic decision tree
# --------------------------------------------------------------------

tree_basic = DecisionTreeClassifier(random_state=123)
tree_basic = tree_basic.fit(train[predictors], train["diabetes"])

print("depth: ", tree_basic.get_depth())
print("leaves:", tree_basic.get_n_leaves())

fig, ax = plt.subplots(figsize=(22, 8))
drawn = plot_tree(tree_basic, max_depth=3, feature_names=predictors,
                  class_names=["neg", "pos"], filled=True, fontsize=8, ax=ax)
plt.show()

# --------------------------------------------------------------------
# Part 2 — Does a tree that nothing stops overfit?
# --------------------------------------------------------------------

train_preds_basic = train.copy()
train_preds_basic["prob"] = tree_basic.predict_proba(train[predictors])[:, 1]
train_preds_basic["pred_class"] = tree_basic.predict(train[predictors])

test_preds_basic = test.copy()
test_preds_basic["prob"] = tree_basic.predict_proba(test[predictors])[:, 1]
test_preds_basic["pred_class"] = tree_basic.predict(test[predictors])

confusion_matrix(train_preds_basic["diabetes"], train_preds_basic["pred_class"])

truth, predicted = train_preds_basic["diabetes"], train_preds_basic["pred_class"]

print("accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("precision:  ", round(precision_score(truth, predicted), 3))
print("sensitivity:", round(recall_score(truth, predicted), 3))
print("specificity:", round(recall_score(truth, predicted, pos_label=0), 3))

# Replace every ______ below, then run this cell.
truth, predicted = ______, test_preds_basic["pred_class"]

print(confusion_matrix(truth, predicted))
print("accuracy:   ", round(accuracy_score(truth, predicted), 3))
print("precision:  ", round(precision_score(truth, predicted), 3))
print("sensitivity:", round(recall_score(truth, predicted), 3))
print("specificity:", round(______, 3))

# --------------------------------------------------------------------
# Part 3 — Restraining the tree by hand
# --------------------------------------------------------------------

tree_shallow = DecisionTreeClassifier(max_depth=3, min_samples_split=20, random_state=123)
tree_shallow = tree_shallow.fit(train[predictors], train["diabetes"])

fig, ax = plt.subplots(figsize=(14, 7))
drawn = plot_tree(tree_shallow, feature_names=predictors,
                  class_names=["neg", "pos"], filled=True, fontsize=9, ax=ax)
plt.show()

for name, data in [("train", train), ("test", test)]:
    truth = data["diabetes"]
    predicted = tree_shallow.predict(data[predictors])
    print(name,
          "accuracy", round(accuracy_score(truth, predicted), 3),
          "precision", round(precision_score(truth, predicted), 3),
          "sensitivity", round(recall_score(truth, predicted), 3),
          "specificity", round(recall_score(truth, predicted, pos_label=0), 3))

# Replace every ______ below, then run this cell.
tree_try = DecisionTreeClassifier(max_depth=______, min_samples_split=______, random_state=123)
tree_try = tree_try.fit(train[predictors], train["diabetes"])

print("train accuracy:", round(accuracy_score(train["diabetes"], tree_try.predict(train[predictors])), 3))
print("test accuracy: ", round(accuracy_score(test["diabetes"], tree_try.predict(test[predictors])), 3))

# --------------------------------------------------------------------
# Part 4 — Tuning the hyperparameters with a grid search
# --------------------------------------------------------------------

tree_grid = {"max_depth":         [1, 3, 5, 7, 10],
             "min_samples_split": [2, 9, 16, 23, 30]}

tree_search = GridSearchCV(DecisionTreeClassifier(random_state=123),
                           param_grid=tree_grid, cv=5, scoring="roc_auc")
tree_search = tree_search.fit(train[predictors], train["diabetes"])

tree_results = pd.DataFrame(tree_search.cv_results_)
tree_results = tree_results[["param_max_depth", "param_min_samples_split",
                             "mean_test_score", "std_test_score"]]
tree_results.sort_values("mean_test_score", ascending=False).head(5).round(3)

fig, ax = plt.subplots()
for split in tree_grid["min_samples_split"]:
    rows = tree_results[tree_results["param_min_samples_split"] == split]
    ax.plot(rows["param_max_depth"], rows["mean_test_score"], marker="o", label=str(split))
ax.set_xlabel("max_depth")
ax.set_ylabel("Mean cross-validated AUC")
ax.legend(title="min_samples_split")
plt.show()

print(tree_search.best_params_)
print("cross-validated AUC:", round(tree_search.best_score_, 3))

final_tree = tree_search.best_estimator_
print("leaves:", final_tree.get_n_leaves())

# Replace every ______ below, then run this cell.
test_prob  = final_tree.predict_proba(test[predictors])[:, 1]
test_class = final_tree.predict(______)
train_prob = final_tree.predict_proba(train[predictors])[:, 1]

print("test accuracy:   ", round(accuracy_score(test["diabetes"], test_class), 3))
print("test sensitivity:", round(recall_score(test["diabetes"], test_class), 3))
print("test specificity:", round(recall_score(test["diabetes"], test_class, pos_label=0), 3))
print("train AUC:", round(roc_auc_score(train["diabetes"], train_prob), 3))
print("test AUC: ", round(roc_auc_score(test["diabetes"], ______), 3))
