# Exercise 9.2 — SHAP values: global and local explanations
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-02-shap.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-02-shap.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn shap

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.inspection import permutation_importance

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

test_prob = rf.predict_proba(test[predictors])[:, 1]    # probability of diabetes

# --------------------------------------------------------------------
# Part 1 — SHAP values for the test patients
# --------------------------------------------------------------------

explainer = shap.TreeExplainer(rf)
explanation = explainer(test[predictors])

shap_pos = explanation[:, :, 1]            # SHAP values for class 1 (diabetes)

print("shape:   ", shap_pos.values.shape)  # one row per patient, one column per predictor
print("baseline:", round(shap_pos.base_values[0], 3))   # the average prediction

# Replace every ______ below, then run this cell.
patient_shap = shap_pos.values[0]
print(np.round(patient_shap, 3))

print(shap_pos.base_values[0] + patient_shap.______())
print(test_prob[0])

# --------------------------------------------------------------------
# Part 2 — Global summaries: bar plot and beeswarm
# --------------------------------------------------------------------

shap_importance = pd.Series(np.abs(shap_pos.values).mean(axis=0), index=predictors)

shap_importance.sort_values(ascending=False).round(3)

shap.plots.bar(shap_pos, show=False)
plt.tight_layout()
plt.show()

shap.plots.beeswarm(shap_pos, show=False)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 3 — One patient: the waterfall plot
# --------------------------------------------------------------------

patient = test.iloc[[0]]                   # double brackets keep it a one-row table
print(patient)
print("predicted probability:", round(test_prob[0], 3))

shap.plots.waterfall(shap_pos[0], show=False)
plt.tight_layout()
plt.show()

# Replace every ______ below, then run this cell.
highest = test_prob.______()                # the position of the highest probability
print(test.iloc[[highest]])

shap.plots.waterfall(shap_pos[______], show=False)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 4 — Logistic regression, and all the measures side by side
# --------------------------------------------------------------------

log_fit = LogisticRegression(C=np.inf, max_iter=5000)
log_fit = log_fit.fit(train[predictors], train["diabetes"])

coefs = pd.DataFrame({"term": predictors, "estimate": log_fit.coef_[0]})
print("intercept:", round(log_fit.intercept_[0], 3))
print(coefs.round(4))

auc_log = roc_auc_score(test["diabetes"], log_fit.predict_proba(test[predictors])[:, 1])
print("test AUC:", round(auc_log, 3))

# Replace every ______ below, then run this cell.
coefs["sd"] = train[predictors].std().values
coefs["per_sd"] = coefs["estimate"] * ______

coefs.round(3)

perm = permutation_importance(rf, test[predictors], test["diabetes"],
                              scoring="roc_auc", n_repeats=20, random_state=1)

comparison = pd.DataFrame({
    "impurity":    rf.feature_importances_,
    "permutation": perm.importances_mean,
    "shap":        shap_importance.values,
    "logistic":    np.abs(coefs["per_sd"].values)}, index=predictors)

comparison = comparison / comparison.max()        # each column divided by its largest value
comparison.round(2)

ordered = comparison.sort_values("shap")

fig, ax = plt.subplots(figsize=(7, 4))
ordered.plot(kind="barh", ax=ax, width=0.8)
ax.set_xlabel("Importance relative to the top variable of each measure")
ax.legend(title="Measure")
fig.tight_layout()
plt.show()
