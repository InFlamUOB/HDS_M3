# Exercise 3.2 — Loss functions
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-02-loss-functions.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02-loss-functions.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# The data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np

glu = pd.read_csv("data/glucose_study.csv")

glu.head()

# --------------------------------------------------------------------
# Step 1 — One patient, one residual
# --------------------------------------------------------------------

glu["pred_guess"]  = 120 + 0.5 * glu["age"]
glu["resid_guess"] = glu["glucose"] - glu["pred_guess"]

glu.head()

glu.loc[[glu["resid_guess"].abs().idxmax()]]

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"], alpha=0.6)
ax.plot(glu["age"], glu["pred_guess"], color="darkorange")
ax.vlines(glu["age"], glu["pred_guess"], glu["glucose"],
          color="red", alpha=0.3)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
plt.show()

# --------------------------------------------------------------------
# Step 2 — From 80 residuals to one number
# --------------------------------------------------------------------

glu["squared"]  = glu["resid_guess"] ** 2
glu["absolute"] = glu["resid_guess"].abs()

glu[["age", "glucose", "resid_guess", "squared", "absolute"]].head()

pd.Series({"SSR":  glu["squared"].sum(),
           "MSE":  glu["squared"].mean(),
           "RMSE": np.sqrt(glu["squared"].mean()),
           "MAE":  glu["absolute"].mean()}).round(2)

# --------------------------------------------------------------------
# Task 1 — Score the fitted line against the hand-drawn one
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
from sklearn.linear_model import LinearRegression

X, y = glu[["age"]], glu["glucose"]
fit_ols = LinearRegression().fit(X, y)

glu["pred_ols"]  = fit_ols.predict(X)
glu["resid_ols"] = ______

pd.Series({"MSE": (glu["resid_ols"] ** 2).mean(),
           "MAE": glu["resid_ols"].abs().mean()}).round(2)

# --------------------------------------------------------------------
# Task 2 — Contaminate three readings
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
glu_bad = glu.copy()
glu_bad.loc[[0, 2, 4], "glucose"] *= ______

fit_bad = LinearRegression().fit(______[["age"]], ______["glucose"])

pd.DataFrame({"intercept": [fit_ols.intercept_, fit_bad.intercept_],
              "slope":     [fit_ols.coef_[0],   fit_bad.coef_[0]]},
             index=["clean", "contaminated"])

# --------------------------------------------------------------------
# Step 3 — Which line is better depends on the loss
# --------------------------------------------------------------------

r_clean = glu_bad["glucose"] - fit_ols.predict(glu_bad[["age"]])
r_bad   = glu_bad["glucose"] - fit_bad.predict(glu_bad[["age"]])

pd.Series({"MSE_clean": (r_clean ** 2).mean(),
           "MSE_bad":   (r_bad ** 2).mean(),
           "MAE_clean": r_clean.abs().mean(),
           "MAE_bad":   r_bad.abs().mean()}).round(1)
