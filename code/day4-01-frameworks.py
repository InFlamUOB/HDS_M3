# Exercise 4.1 — Unified modelling frameworks in R and Python
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-01-frameworks.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-01-frameworks.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------
# Part 1 — What model, and which engine
# --------------------------------------------------------------------

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

log_spec  = LogisticRegression()
tree_spec = DecisionTreeClassifier()
rf_spec   = RandomForestClassifier()
knn_spec  = KNeighborsClassifier()

print(log_spec)

print(tree_spec)

log_spec_lbfgs     = LogisticRegression(solver="lbfgs")       # the default
log_spec_liblinear = LogisticRegression(solver="liblinear")   # another algorithm

print(log_spec_liblinear)

# --------------------------------------------------------------------
# Part 2 — Fit and predict a logistic regression
# --------------------------------------------------------------------

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["glucose", "mass", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

train["diabetes"].value_counts()

X_train = train[["glucose"]]     # two-dimensional: a data frame with one column
y_train = train["diabetes"]      # one-dimensional: a single column

logistic_fit = LogisticRegression(C=np.inf)
logistic_fit = logistic_fit.fit(X_train, y_train)

print(logistic_fit.intercept_, logistic_fit.coef_)

print(logistic_fit.classes_)    # column 0 is class 0 (neg), column 1 is class 1 (pos)

probs = logistic_fit.predict_proba(test[["glucose"]])

test_preds = test.copy()
test_preds["prob_neg"] = probs[:, 0]
test_preds["prob_pos"] = probs[:, 1]

test_preds.head()

fig, ax = plt.subplots()
ax.scatter(test_preds["glucose"], test_preds["prob_pos"], alpha=0.5)
ax.set_xlabel("Glucose (mg/dL)")
ax.set_ylabel("Predicted probability of diabetes")
plt.show()

# --------------------------------------------------------------------
# Part 3 — Pipelines
# --------------------------------------------------------------------

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

features = ["glucose", "mass", "age"]

log_pipe = Pipeline([
    ("scale", StandardScaler()),                 # preprocessing step
    ("model", LogisticRegression(C=np.inf)),     # the model
])

log_pipe = log_pipe.fit(train[features], train["diabetes"])

print(log_pipe)

print("accuracy:       ", round(log_pipe.score(test[features], test["diabetes"]), 3))
print("always says neg:", round((test["diabetes"] == 0).mean(), 3))

# Replace every ______ below, then run this cell.
from sklearn.tree import DecisionTreeClassifier

tree_pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", ______(random_state=1)),
])

tree_pipe = tree_pipe.fit(train[features], train["diabetes"])

print("accuracy:", round(tree_pipe.score(______, test["diabetes"]), 3))
