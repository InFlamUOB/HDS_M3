# Exercise 4.2 — Fitting a logistic regression model
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-02-logistic-regression.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-02-logistic-regression.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["glucose", "mass", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes"] = (diabetes["diabetes"] == "pos").astype(int)       # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

# --------------------------------------------------------------------
# Part 1 — Probability, odds and log-odds
# --------------------------------------------------------------------

prob     = 0.8
odds     = prob / (1 - prob)
log_odds = np.log(odds)

print("probability:", prob)
print("odds:       ", round(odds, 3))
print("log-odds:   ", round(log_odds, 3))

# Replace every ______ below, then run this cell.
table = pd.DataFrame({"prob": [0.8, 0.5, 0.2, 0.9]})
table["odds"]     = ______
table["log_odds"] = np.log(table["odds"])

table.round(3)

log_odds = np.linspace(-6, 6, 121)
probability = 1 / (1 + np.exp(-log_odds))

fig, ax = plt.subplots()
ax.plot(log_odds, probability, color="red", linewidth=2)
ax.axhline(0, color="grey", linestyle="--")
ax.axhline(1, color="grey", linestyle="--")
ax.set_xlabel("Log-odds z")
ax.set_ylabel("Probability p = 1 / (1 + exp(-z))")
plt.show()

# --------------------------------------------------------------------
# Part 2 — Fit the model
# --------------------------------------------------------------------

train["diabetes"].value_counts()

logistic_fit_glucose = LogisticRegression(C=np.inf)
logistic_fit_glucose = logistic_fit_glucose.fit(train[["glucose"]], train["diabetes"])

intercept = logistic_fit_glucose.intercept_[0]
slope     = logistic_fit_glucose.coef_[0, 0]

print("intercept:", round(intercept, 4))
print("slope:    ", round(slope, 4))

# --------------------------------------------------------------------
# Part 3 — From the model to odds and probability
# --------------------------------------------------------------------

glucose_value = 120

log_odds_120 = intercept + slope * glucose_value   # the straight line
odds_120     = np.exp(log_odds_120)                # odds
prob_120     = 1 / (1 + np.exp(-log_odds_120))     # probability

print("log-odds:   ", round(log_odds_120, 3))
print("odds:       ", round(odds_120, 3))
print("probability:", round(prob_120, 3))

logistic_fit_glucose.predict_proba(pd.DataFrame({"glucose": [120]}))

# Replace every ______ below, then run this cell.
glucose_value = ______

log_odds_160 = intercept + slope * glucose_value
odds_160     = np.exp(log_odds_160)
prob_160     = 1 / (1 + np.exp(-______))

print("log-odds:   ", round(log_odds_160, 3))
print("odds:       ", round(odds_160, 3))
print("probability:", round(prob_160, 3))

probs = logistic_fit_glucose.predict_proba(test[["glucose"]])

test_preds = test.copy()
test_preds["prob_neg"] = probs[:, 0]
test_preds["prob_pos"] = probs[:, 1]

test_preds[["glucose", "diabetes", "prob_pos", "prob_neg"]].head()

ordered = test_preds.sort_values("glucose")   # a line has to be drawn from left to right

fig, ax = plt.subplots()
ax.scatter(test_preds["glucose"], test_preds["diabetes"], alpha=0.4, color="black")
ax.plot(ordered["glucose"], ordered["prob_pos"], color="red", linewidth=2)
ax.set_yticks([0, 0.5, 1])
ax.set_xlabel("Glucose (mg/dL)")
ax.set_ylabel("Observed outcome (0/1) and predicted probability")
plt.show()
