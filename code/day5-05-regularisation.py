# Exercise 5.5 — Regularisation: lasso and ridge logistic regression
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-05-regularisation.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-05-regularisation.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
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

# --------------------------------------------------------------------
# Part 1 — Coefficient paths
# --------------------------------------------------------------------

lambdas = 10 ** np.linspace(-3, 0, 31)
n = len(train)

rows = []
for lam in lambdas:
    lasso = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(l1_ratio=1, C=1 / (n * lam), solver="saga",
                                     max_iter=10000, random_state=123)),
    ])
    lasso = lasso.fit(train[predictors], train["diabetes"])
    for name, coef in zip(predictors, lasso["model"].coef_[0]):
        rows.append({"lambda": lam, "term": name, "estimate": coef})

lasso_path = pd.DataFrame(rows)
lasso_path[lasso_path["lambda"] == lambdas[20]].round(3)   # the coefficients at one penalty

fig, ax = plt.subplots()
for name in predictors:
    rows = lasso_path[lasso_path["term"] == name]
    ax.plot(rows["lambda"], rows["estimate"], linewidth=2, label=name)
ax.axhline(0, color="grey")
ax.set_xscale("log")
ax.set_xlabel("Penalty (log scale)")
ax.set_ylabel("Coefficient (per standard deviation)")
ax.set_title("Lasso: coefficients drop out one by one")
ax.legend()
plt.show()

# Replace every ______ below, then run this cell.
rows = []
for lam in lambdas:
    ridge = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(l1_ratio=______, C=1 / (n * lam), solver="saga",
                                     max_iter=10000, random_state=123)),
    ])
    ridge = ridge.fit(train[predictors], train["diabetes"])
    for name, coef in zip(predictors, ridge["model"].coef_[0]):
        rows.append({"lambda": lam, "term": name, "estimate": coef})
ridge_path = pd.DataFrame(rows)

fig, ax = plt.subplots()
for name in predictors:
    path_rows = ridge_path[ridge_path["term"] == name]
    ax.plot(path_rows["lambda"], path_rows["estimate"], linewidth=2, label=name)
ax.axhline(0, color="grey")
ax.set_xscale("log")
ax.set_xlabel("Penalty (log scale)")
ax.set_ylabel("Coefficient (per standard deviation)")
ax.set_title("Ridge: every coefficient shrinks, none drops out")
ax.legend()
plt.show()

# --------------------------------------------------------------------
# Part 2 — Choosing the penalty by cross-validation
# --------------------------------------------------------------------

lasso_pipe = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(l1_ratio=1, solver="saga", max_iter=10000, random_state=123)),
])

lasso_search = GridSearchCV(lasso_pipe, param_grid={"model__C": 1 / (n * lambdas)},
                            cv=5, scoring="roc_auc")
lasso_search = lasso_search.fit(train[predictors], train["diabetes"])

lasso_results = pd.DataFrame(lasso_search.cv_results_)
lasso_results["lambda"] = 1 / (n * lasso_results["param_model__C"].astype(float))
lasso_results = lasso_results[["lambda", "param_model__C", "mean_test_score", "std_test_score"]]
lasso_results.sort_values("mean_test_score", ascending=False).head(5).round(4)

fig, ax = plt.subplots()
ax.errorbar(lasso_results["lambda"], lasso_results["mean_test_score"],
            yerr=lasso_results["std_test_score"] / np.sqrt(5), marker="o", capsize=2)
ax.set_xscale("log")
ax.set_xlabel("Penalty (log scale)")
ax.set_ylabel("Mean cross-validated AUC")
ax.set_title("Cross-validated AUC along the lasso path")
plt.show()

# --------------------------------------------------------------------
# Part 3 — Does the penalty help on the test rows?
# --------------------------------------------------------------------

print(lasso_search.best_params_)
final_lasso = lasso_search.best_estimator_
print(pd.Series(final_lasso["model"].coef_[0], index=predictors).round(3))

plain = Pipeline([
    ("scale", StandardScaler()),
    ("model", LogisticRegression(C=np.inf)),
])
plain = plain.fit(train[predictors], train["diabetes"])

# Replace every ______ below, then run this cell.
lasso_prob = final_lasso.predict_proba(test[predictors])[:, 1]
plain_prob = ______.predict_proba(test[predictors])[:, 1]

print("lasso, test AUC:      ", round(roc_auc_score(test["diabetes"], lasso_prob), 3))
print("unpenalised, test AUC:", round(roc_auc_score(test["diabetes"], ______), 3))
