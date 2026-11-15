# Exercise 3.3 — The best fit line
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-02b-best-fit-line.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02b-best-fit-line.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Where we left off
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

glu = pd.read_csv("data/glucose_study.csv")

fit_ols = LinearRegression().fit(glu[["age"]], glu["glucose"])

glu_bad = glu.copy()
glu_bad.loc[[0, 2, 4], "glucose"] *= 3

fit_ols.intercept_, fit_ols.coef_[0]

# --------------------------------------------------------------------
# Step 1 — The loss as a function of the parameters
# --------------------------------------------------------------------

first3 = glu.head(3).copy()
first3["pred"] = 3 + 5 * first3["age"]
first3["r"]    = first3["glucose"] - first3["pred"]

(first3["r"] ** 2).mean()

# --------------------------------------------------------------------
# Task 1 — Score two candidate lines on all 80 patients
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
r_3_5 = glu["glucose"] - (3 + 5 * glu["age"])
r_4_7 = glu["glucose"] - (______)

pd.Series({"at_3_5": (r_3_5 ** 2).mean(),
           "at_4_7": (r_4_7 ** 2).mean()}).round(1)

# --------------------------------------------------------------------
# Step 2 — Every candidate line at once
# --------------------------------------------------------------------

b0s = np.arange(60, 161, 1)
b1s = np.round(np.arange(-1, 2.001, 0.02), 2)

candidates = pd.MultiIndex.from_product(
    [b0s, b1s], names=["b0", "b1"]).to_frame(index=False)

scores = candidates.merge(glu[["age", "glucose"]], how="cross")
scores["r"] = scores["glucose"] - (scores["b0"] + scores["b1"] * scores["age"])
scores = (scores.assign(sq=lambda d: d["r"] ** 2,
                        ab=lambda d: d["r"].abs())
                .groupby(["b0", "b1"], as_index=False)
                .agg(MSE=("sq", "mean"), MAE=("ab", "mean")))

scores.head()

surface = scores.pivot(index="b1", columns="b0", values="MSE")

fig, ax = plt.subplots()
cs = ax.contourf(surface.columns, surface.index,
                 np.log10(surface.values), levels=20, cmap="magma")
ax.scatter([fit_ols.intercept_], [fit_ols.coef_[0]], color="red", zorder=3)
cbar = fig.colorbar(cs, ax=ax, label="log10(MSE)")
ax.set_xlabel(r"$\hat\beta_0$")
ax.set_ylabel(r"$\hat\beta_1$")
plt.show()

# --------------------------------------------------------------------
# Task 2 — Find the best candidate under each loss
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
print(scores.nsmallest(1, ______))
print(scores.nsmallest(1, "MAE"))

print(fit_ols.intercept_, fit_ols.coef_[0])   # the fitted line, to compare

scores_bad = candidates.merge(glu_bad[["age", "glucose"]], how="cross")
scores_bad["r"] = (scores_bad["glucose"]
                   - (scores_bad["b0"] + scores_bad["b1"] * scores_bad["age"]))
scores_bad = (scores_bad.assign(sq=lambda d: d["r"] ** 2,
                                ab=lambda d: d["r"].abs())
                        .groupby(["b0", "b1"], as_index=False)
                        .agg(MSE=("sq", "mean"), MAE=("ab", "mean")))

pd.DataFrame(
    [scores.nsmallest(1, "MSE")[["b0", "b1"]].iloc[0],
     scores_bad.nsmallest(1, "MSE")[["b0", "b1"]].iloc[0],
     scores.nsmallest(1, "MAE")[["b0", "b1"]].iloc[0],
     scores_bad.nsmallest(1, "MAE")[["b0", "b1"]].iloc[0]],
    index=["clean_MSE", "contaminated_MSE", "clean_MAE", "contaminated_MAE"])
