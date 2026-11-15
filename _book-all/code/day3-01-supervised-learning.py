# Exercise 3.1 — Supervised learning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-01-supervised-learning.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-01-supervised-learning.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# The data we fit to
# --------------------------------------------------------------------

import pandas as pd
import numpy as np

glu = pd.read_csv("data/glucose_study.csv")

glu.head()

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"], alpha=0.7)
ax.set_xlabel("Age in years (the feature)")
ax.set_ylabel("Glucose, mg/dL (the label)")
plt.show()

# --------------------------------------------------------------------
# Fitting the model
# --------------------------------------------------------------------

from sklearn.linear_model import LinearRegression

X = glu[["age"]]      # 2-D: a frame, not a series
y = glu["glucose"]    # 1-D
lin_reg = LinearRegression().fit(X, y)

lin_reg.intercept_, lin_reg.coef_[0]

# --------------------------------------------------------------------
# Predicting, inside and outside the data
# --------------------------------------------------------------------

lin_reg.predict(pd.DataFrame({"age": [45, 10]}))

# --------------------------------------------------------------------
# Task 1 — Predict from the parameters, not from the function
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
pred_60 = ______ + ______ * 60
print(round(pred_60, 2))

# --------------------------------------------------------------------
# Task 2 — Change the algorithm, keep everything else
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
from sklearn.tree import DecisionTreeRegressor, export_text

tree_reg = DecisionTreeRegressor(max_depth=3, min_samples_leaf=5).fit(______, ______)
print(export_text(tree_reg, feature_names=["age"]))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

from sklearn.tree import DecisionTreeRegressor
tree_shown = DecisionTreeRegressor(max_depth=3, min_samples_leaf=5).fit(X, y)

grid = pd.DataFrame({"age": np.linspace(glu["age"].min(), glu["age"].max(), 400)})
fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"], alpha=0.5)
ax.plot(grid["age"], tree_shown.predict(grid), color="darkred")
ax.plot(grid["age"], lin_reg.predict(grid), color="steelblue")
ax.set_xlabel("Age (years)"); ax.set_ylabel("Glucose (mg/dL)")
plt.show()

# --------------------------------------------------------------------
# Task 3 — The role of the dataset
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
glu30 = glu.head(______)
X30, y30 = glu30[["age"]], glu30["glucose"]

lin30  = LinearRegression().fit(______, ______)
tree30 = DecisionTreeRegressor(max_depth=3, min_samples_leaf=5).fit(______, ______)

at25 = pd.DataFrame({"age": [25]})
{"line80": lin_reg.predict(at25)[0],   "line30": lin30.predict(at25)[0],
 "tree80": tree_shown.predict(at25)[0], "tree30": tree30.predict(at25)[0]}
