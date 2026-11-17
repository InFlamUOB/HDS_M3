# Exercise 5.1 — Evaluating a regression model on training and test data
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-01-regression-metrics.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-01-regression-metrics.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["glucose", "mass", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

print(diabetes.shape)
print(train.shape)
print(test.shape)

# --------------------------------------------------------------------
# Part 1 — A cubic model as a pre-processing step
# --------------------------------------------------------------------

poly_step = PolynomialFeatures(degree=3, include_bias=False)   # age, age^2, age^3

cubic_features = poly_step.fit_transform(train[["age"]])

pd.DataFrame(cubic_features, columns=poly_step.get_feature_names_out()).head(10)

cubic_pipe = Pipeline([
    ("poly", PolynomialFeatures(degree=3, include_bias=False)),
    ("model", LinearRegression()),
])
cubic_pipe = cubic_pipe.fit(train[["age"]], train["glucose"])

print("intercept:   ", round(cubic_pipe["model"].intercept_, 3))
print("coefficients:", cubic_pipe["model"].coef_)

age_grid = pd.DataFrame({"age": np.arange(21, 82)})
curve = cubic_pipe.predict(age_grid)

fig, ax = plt.subplots()
ax.scatter(train["age"], train["glucose"], alpha=0.3, color="black")
ax.plot(age_grid["age"], curve, color="red", linewidth=2)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Glucose (mg/dL)")
ax.set_title("Cubic fit of glucose on age, training rows")
plt.show()

# --------------------------------------------------------------------
# Part 2 — Predictions on the training and the test rows
# --------------------------------------------------------------------

cubic_pipe.predict(train[["age"]])[:6].round(2)

train_preds = train.copy()
train_preds["pred"] = cubic_pipe.predict(train[["age"]])

test_preds = test.copy()
test_preds["pred"] = cubic_pipe.predict(test[["age"]])

test_preds.head().round(2)

fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
for ax, data, name in [(axes[0], train_preds, "train (600)"), (axes[1], test_preds, "test (150)")]:
    data = data.sort_values("age")
    ax.scatter(data["age"], data["glucose"], alpha=0.3, color="black")
    ax.plot(data["age"], data["pred"], color="red", linewidth=2)
    ax.set_title(name)
    ax.set_xlabel("Age (years)")
axes[0].set_ylabel("Glucose (mg/dL)")
fig.suptitle("The same fitted cubic, on the training and the test rows")
plt.show()

# --------------------------------------------------------------------
# Part 3 — Measuring the error, by hand and with a package
# --------------------------------------------------------------------

train_error = train_preds["glucose"] - train_preds["pred"]

train_mse  = np.mean(train_error ** 2)
train_rmse = np.sqrt(train_mse)
train_mae  = np.mean(np.abs(train_error))

print("MSE: ", round(train_mse, 2))
print("RMSE:", round(train_rmse, 2))
print("MAE: ", round(train_mae, 2))

# Replace every ______ below, then run this cell.
test_error = ______

test_mse  = np.mean(test_error ** 2)
test_rmse = ______
test_mae  = np.mean(np.abs(test_error))

print("MSE: ", round(test_mse, 2))
print("RMSE:", round(test_rmse, 2))
print("MAE: ", round(test_mae, 2))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

from sklearn.metrics import mean_squared_error, root_mean_squared_error, mean_absolute_error

print("train MSE: ", round(mean_squared_error(train_preds["glucose"], train_preds["pred"]), 2))
print("train RMSE:", round(root_mean_squared_error(train_preds["glucose"], train_preds["pred"]), 2))
print("train MAE: ", round(mean_absolute_error(train_preds["glucose"], train_preds["pred"]), 2))

# Replace every ______ below, then run this cell.
print("test MSE: ", round(mean_squared_error(______, ______), 2))
print("test RMSE:", round(root_mean_squared_error(test_preds["glucose"], test_preds["pred"]), 2))
print("test MAE: ", round(mean_absolute_error(test_preds["glucose"], test_preds["pred"]), 2))

# --------------------------------------------------------------------
# Part 4 — More flexible is not more accurate
# --------------------------------------------------------------------

from sklearn.preprocessing import StandardScaler

rows = []
for d in range(1, 9):
    poly_pipe = Pipeline([
        ("scale", StandardScaler()),
        ("poly", PolynomialFeatures(degree=d, include_bias=False)),
        ("model", LinearRegression()),
    ])
    poly_pipe = poly_pipe.fit(train[["age"]], train["glucose"])

    train_rmse = root_mean_squared_error(train["glucose"], poly_pipe.predict(train[["age"]]))
    test_rmse  = root_mean_squared_error(test["glucose"], poly_pipe.predict(test[["age"]]))
    rows.append({"degree": d, "train_rmse": train_rmse, "test_rmse": test_rmse})

degree_results = pd.DataFrame(rows)
degree_results.round(3)

fig, ax = plt.subplots()
ax.plot(degree_results["degree"], degree_results["train_rmse"], marker="o", label="train_rmse")
ax.plot(degree_results["degree"], degree_results["test_rmse"], marker="o", label="test_rmse")
ax.set_xlabel("Degree of the polynomial")
ax.set_ylabel("RMSE (mg/dL)")
ax.set_title("Training error keeps falling; test error does not")
ax.legend()
plt.show()
