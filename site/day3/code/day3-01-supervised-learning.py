# Exercise 3.1 — Supervised learning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-01-supervised-learning.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-01-supervised-learning.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib seaborn scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, plot_tree, export_text  # a new learning algorithm

glu = pd.read_csv("data/glucose_study.csv")

glu.head()

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"])
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
plt.show()

# --------------------------------------------------------------------
# A supervised learning algorithm: linear regression
# --------------------------------------------------------------------

fig, ax = plt.subplots()
sns.regplot(data=glu, x="age", y="glucose", ci=None, ax=ax)
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
plt.show()

# 1. Separate X (the feature) and y (the label)
X = glu[["age"]]      # two-dimensional: a data frame with one column
y = glu["glucose"]    # one-dimensional: a single column

# 2. Define the model
lin_reg = LinearRegression()

# 3. Fit the model
lin_reg = lin_reg.fit(X, y)

intercept = lin_reg.intercept_
slope = lin_reg.coef_[0]

print(intercept, slope)

ages = np.array([glu["age"].min(), glu["age"].max()])   # the two ends of the line

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"])
ax.plot(ages, intercept + slope * ages, color="red", linestyle="--", linewidth=2)
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
plt.show()

age_newsample = 45
predicted_glucose = 110.30 + 0.289 * age_newsample
print(round(predicted_glucose, 3))

# predict() wants a data frame, because it normally receives more than one
# sample and more than one feature. Here it has one row and one column.
lin_reg.predict(pd.DataFrame({"age": [45]}))

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"])
ax.plot(ages, intercept + slope * ages, color="red", linestyle="--", linewidth=2)
ax.scatter(age_newsample, predicted_glucose, color="grey", s=150, zorder=3)
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
plt.show()

age_newsample = 10
predicted_glucose = 110.30 + 0.289 * age_newsample
print(round(predicted_glucose, 3))

ages = np.array([0, 100])   # draw the line well beyond the data

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"])
ax.plot(ages, intercept + slope * ages, color="red", linestyle="--", linewidth=2)
ax.scatter(age_newsample, predicted_glucose, color="grey", s=150, zorder=3)
ax.set_xlim(0, 100)
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
plt.show()

# --------------------------------------------------------------------
# Exercise: understand the role of the dataset in predictive modelling
# --------------------------------------------------------------------

# at most 3 questions deep, and at least 5 people in every final group
tree_reg = DecisionTreeRegressor(max_depth=3, min_samples_leaf=5)

tree_reg = tree_reg.fit(X, y)

print(export_text(tree_reg, feature_names=["age"]))

fig, ax = plt.subplots(figsize=(10, 6))
plot_tree(tree_reg, feature_names=["age"], filled=True, rounded=True,
          fontsize=8, ax=ax)
plt.tight_layout()
plt.show()

glu["predicted_glucose"] = tree_reg.predict(X)

glu.head()

# --------------------------------------------------------------------
# Stop here
# --------------------------------------------------------------------

ordered = glu.sort_values("age")   # a step line has to be drawn from left to right

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"], s=60, color="blue", alpha=0.7)
ax.step(ordered["age"], ordered["predicted_glucose"], where="post",
        color="darkred", linewidth=2)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
plt.show()

fig, ax = plt.subplots()
ax.scatter(glu["age"], glu["glucose"], s=60, color="blue", alpha=0.7)
ax.step(ordered["age"], ordered["predicted_glucose"], where="post",
        color="darkred", linewidth=2)
ax.scatter(glu["age"], glu["predicted_glucose"], s=30, color="grey", alpha=0.8, zorder=3)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
plt.show()

# --------------------------------------------------------------------
# Discuss
# --------------------------------------------------------------------

glu30 = glu.iloc[:30]
glu30.shape
