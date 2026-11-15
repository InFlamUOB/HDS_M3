# Exercise 3.2 — Residuals and loss functions
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-02-loss-functions.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02-loss-functions.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from sklearn.linear_model import LinearRegression

glu = pd.read_csv("data/glucose_study.csv")

glu.head()

# --------------------------------------------------------------------
# Part 1 — Follow one prediction into a loss
# --------------------------------------------------------------------

three = pd.DataFrame({"person":  ["A", "B", "C"],
                      "age":     [28, 30, 55],
                      "glucose": [194, 115, 111]})

three

ages = np.array([20, 60])   # the two ends of the line

fig, ax = plt.subplots()
ax.plot(ages, 110 + 0.3 * ages, color="darkorange")
ax.vlines(three["age"], 110 + 0.3 * three["age"], three["glucose"],
          color="red", linestyle="--")
ax.scatter(three["age"], 110 + 0.3 * three["age"], color="darkorange", s=60, zorder=3)
ax.scatter(three["age"], three["glucose"], color="black", s=60, zorder=3)
for person, age, glucose in zip(three["person"], three["age"], three["glucose"]):
    ax.annotate(person, (age + 1, glucose), fontweight="bold")
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
plt.show()

# Replace every ______ below, then run this cell.
three["predicted"] = 110 + 0.3 * three["age"]
three["residual"]  = ______ - ______
three["absolute"]  = three["residual"].abs()
three["squared"]   = three["residual"] ** 2

print(three)

print("MAE: ", round(three["absolute"].mean(), 2))
print("MSE: ", round(three["squared"].mean(), 2))
print("RMSE:", round(np.sqrt(three["squared"].mean()), 2))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

# put the three squares side by side, with a gap of 10 between them
left = [0, 85.6, 99.6]

fig, ax = plt.subplots(figsize=(7, 5))
for person, start, size in zip(three["person"], left, three["absolute"]):
    ax.add_patch(Rectangle((start, 0), size, size, color="firebrick", alpha=0.3))
    ax.plot([start, start + size], [0, 0], color="firebrick", linewidth=4)
    ax.annotate(person, (start + size / 2, size + 3), ha="center", fontweight="bold")
ax.set_xlim(-5, 120)
ax.set_ylim(-3, 85)
ax.set_aspect("equal")                  # one unit is the same length both ways
ax.set_xticks([])
ax.set_xlabel("Thick line: the absolute residual. Shaded square: the squared residual.")
ax.set_ylabel("Size of the residual (mg/dL)")
plt.show()

# --------------------------------------------------------------------
# Part 2 — From three people to all 80
# --------------------------------------------------------------------

glu["predicted"] = 110 + 0.3 * glu["age"]
glu["residual"]  = glu["glucose"] - glu["predicted"]

glu.head()

ages = np.array([glu["age"].min(), glu["age"].max()])

fig, ax = plt.subplots()
ax.vlines(glu["age"], glu["predicted"], glu["glucose"],
          color="red", linestyle="--", alpha=0.5)
ax.plot(ages, 110 + 0.3 * ages, color="darkorange")
ax.scatter(glu["age"], glu["glucose"], color="black", alpha=0.7, zorder=3)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
plt.show()

round(glu["residual"].sum(), 1)

glu["absolute"] = glu["residual"].abs()
glu["squared"]  = glu["residual"] ** 2

glu.head()

print("SSR: ", round(glu["squared"].sum(), 2))
print("MSE: ", round(glu["squared"].mean(), 2))
print("RMSE:", round(np.sqrt(glu["squared"].mean()), 2))
print("MAE: ", round(glu["absolute"].mean(), 2))

# Replace every ______ below, then run this cell.
predicted_hand = ______
residual_hand  = glu["glucose"] - predicted_hand

print("SSR: ", round((residual_hand ** 2).sum(), 2))
print("MSE: ", round((residual_hand ** 2).mean(), 2))
print("RMSE:", round(np.sqrt((residual_hand ** 2).mean()), 2))
print("MAE: ", round(residual_hand.abs().mean(), 2))

# --------------------------------------------------------------------
# Part 3 — What outliers do to each loss
# --------------------------------------------------------------------

fit_clean = LinearRegression()
fit_clean = fit_clean.fit(glu[["age"]], glu["glucose"])

print(fit_clean.intercept_, fit_clean.coef_[0])

# Replace every ______ below, then run this cell.
glu_outliers = glu.copy()
glu_outliers.loc[[0, 2, 4], "glucose"] = glu_outliers.loc[[0, 2, 4], "glucose"] * ______

fit_outliers = LinearRegression()
fit_outliers = fit_outliers.fit(______[["age"]], ______["glucose"])

print(fit_outliers.intercept_, fit_outliers.coef_[0])

ages = np.array([glu["age"].min(), glu["age"].max()])

fig, axes = plt.subplots(1, 2, figsize=(8, 4), sharey=True)
for ax, data, fit, title in [(axes[0], glu, fit_clean, "Without outliers"),
                             (axes[1], glu_outliers, fit_outliers, "With three outliers")]:
    colours = np.where(data["glucose"] > 250, "red", "blue")   # the outliers in red
    ax.scatter(data["age"], data["glucose"], color=colours, alpha=0.7)
    ax.plot(ages, fit.intercept_ + fit.coef_[0] * ages,
            color="black", linestyle="--", linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Age (years)")
axes[0].set_ylabel("Glucose (mg/dL)")
plt.tight_layout()
plt.show()

r_clean    = glu_outliers["glucose"] - fit_clean.predict(glu_outliers[["age"]])
r_outliers = glu_outliers["glucose"] - fit_outliers.predict(glu_outliers[["age"]])

print("MSE, line fitted without outliers:", round((r_clean ** 2).mean(), 1))
print("MSE, line fitted with outliers:   ", round((r_outliers ** 2).mean(), 1))
print("MAE, line fitted without outliers:", round(r_clean.abs().mean(), 1))
print("MAE, line fitted with outliers:   ", round(r_outliers.abs().mean(), 1))
