# Exercise 9.3 — One toolbox for explanations: DALEX
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-03-dalex.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-03-dalex.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn "dalex>=1.8"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dalex as dx             # explanations for any model

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, cohen_kappa_score

# --------------------------------------------------------------------
# Part 1 — The model and the explainer
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

rf = RandomForestClassifier(n_estimators=500, random_state=1)
rf = rf.fit(train[predictors], train["diabetes"])

test_class = rf.predict(test[predictors])          # predicted class, threshold 0.5

print("accuracy:", round(accuracy_score(test["diabetes"], test_class), 3))
print("kappa:   ", round(cohen_kappa_score(test["diabetes"], test_class), 3))

# Replace every ______ below, then run this cell.
explainer = dx.Explainer(
    rf,
    data=test[______],
    y=test["diabetes"],                           # already 1 = diabetes, 0 = none
    label="Random forest",
    verbose=False,                                # no progress report
)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

performance = explainer.model_performance()
performance.result.round(3)

# --------------------------------------------------------------------
# Part 2 — Global: which variables matter?
# --------------------------------------------------------------------

importance_dalex = explainer.model_parts(random_state=1)

importance_dalex.result[["variable", "dropout_loss"]].round(3)

result = importance_dalex.result
full_loss = result.loc[result["variable"] == "_full_model_", "dropout_loss"].iloc[0]
bars = result[~result["variable"].isin(["_full_model_", "_baseline_"])]
bars = bars.sort_values("dropout_loss")

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.barh(bars["variable"], bars["dropout_loss"] - full_loss, left=full_loss, color="coral")
ax.axvline(full_loss, color="black", linestyle="--")
ax.set_xlim(left=full_loss - 0.01)                # leave room to see the dashed line
ax.set_xlabel("1 - AUC after shuffling the variable (dashed: no variable shuffled)")
ax.set_title("Random forest: permutation importance (DALEX)")
fig.tight_layout()
plt.show()

# dalex's own plot gives the same picture, as an interactive plotly figure:
# importance_dalex.plot()

# --------------------------------------------------------------------
# Part 3 — How does the prediction change with one variable?
# --------------------------------------------------------------------

pdp_glucose = explainer.model_profile(variables=["glucose"], type="partial",
                                      verbose=False)

pdp_glucose.result.iloc[::20].round(3)   # every 20th of the 101 grid points

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(pdp_glucose.result["_x_"], pdp_glucose.result["_yhat_"], color="steelblue", linewidth=2)
ax.set_xlabel("Glucose (mg/dL)")
ax.set_ylabel("Average predicted probability of diabetes")
ax.set_title("Partial dependence profile: glucose")
fig.tight_layout()
plt.show()

ice = pdp_glucose.raw_profiles.result

fig, ax = plt.subplots(figsize=(6, 3.5))
for patient_id in ice["_ids_"].unique():
    one = ice[ice["_ids_"] == patient_id]
    ax.plot(one["glucose"], one["_yhat_"], color="grey", alpha=0.3, linewidth=0.7)
ax.plot(pdp_glucose.result["_x_"], pdp_glucose.result["_yhat_"], color="steelblue", linewidth=2.5)
ax.set_xlabel("Glucose (mg/dL)")
ax.set_ylabel("Predicted probability of diabetes")
ax.set_title("ICE profiles (grey) and their average (blue)")
fig.tight_layout()
plt.show()

# Replace every ______ below, then run this cell.
pdp_more = explainer.model_profile(variables=[______, ______], type="partial",
                                   verbose=False)

fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), sharey=True)
for ax, name in zip(axes, ["pedigree", "age"]):
    one = pdp_more.result[pdp_more.result["_vname_"] == name]
    ax.plot(one["_x_"], one["_yhat_"], color="steelblue", linewidth=2)
    ax.set_xlabel(name)
axes[0].set_ylabel("Average predicted probability of diabetes")
fig.tight_layout()
plt.show()

# --------------------------------------------------------------------
# Part 4 — One patient: break-down and SHAP
# --------------------------------------------------------------------

new_observation = test[predictors].iloc[[0]]

print(new_observation)
print(explainer.predict(new_observation))     # her predicted probability

shap_patient = explainer.predict_parts(new_observation, type="shap", B=25,
                                       random_state=1)

shap_average = shap_patient.result[shap_patient.result["B"] == 0]   # B = 0 holds the average over the 25 orders
shap_average = shap_average[["variable", "contribution"]]
shap_average.sort_values("contribution", key=abs, ascending=False).round(3)

ordered = shap_average.sort_values("contribution", key=abs)
colours = np.where(ordered["contribution"] > 0, "firebrick", "steelblue")

fig, ax = plt.subplots(figsize=(6, 3))
ax.barh(ordered["variable"], ordered["contribution"], color=colours)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("SHAP contribution to the predicted probability")
ax.set_title("SHAP values for the first test patient (dalex)")
fig.tight_layout()
plt.show()

# Replace every ______ below, then run this cell.
breakdown_patient = explainer.predict_parts(new_observation, type=______)

breakdown_patient.result[["variable", "contribution", "cumulative"]].round(3)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

# Optional, not run here: an interactive dashboard of everything above
# arena = dx.Arena()
# arena.push_model(explainer)
# arena.push_observations(test[predictors])
# arena.run_server()
