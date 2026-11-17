# Exercise 4.3 — The decision threshold
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-03-thresholds.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-03-thresholds.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, install it once from a terminal
# (in a Jupyter notebook, type %pip instead of pip):
# pip install pandas numpy matplotlib scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression

diabetes = pd.read_csv("data/diabetes.csv")
diabetes = diabetes[["glucose", "mass", "age", "diabetes"]]
diabetes = diabetes[(diabetes["glucose"] > 0) & (diabetes["mass"] > 0)]   # remove the impossible zeros
diabetes = diabetes.reset_index(drop=True)
diabetes["diabetes_dummy"] = (diabetes["diabetes"] == "pos").astype(int) # 1 = pos, 0 = neg

is_test = diabetes.index % 5 == 0               # every fifth person is held back
train = diabetes[~is_test]
test  = diabetes[is_test]

# --------------------------------------------------------------------
# Part 1 — From a probability to a predicted class
# --------------------------------------------------------------------

log_fit = LogisticRegression(C=np.inf)
log_fit = log_fit.fit(train[["glucose"]], train["diabetes_dummy"])

print("intercept:", round(log_fit.intercept_[0], 4))
print("slope:    ", round(log_fit.coef_[0, 0], 4))

patients15 = test.iloc[25:40].copy()

prediction_15 = patients15.copy()
prediction_15["prob"] = log_fit.predict_proba(patients15[["glucose"]])[:, 1]

prediction_15[["glucose", "diabetes_dummy", "prob"]].round(3)

prediction_15["class_0.3"] = (prediction_15["prob"] >= 0.3).astype(int)
prediction_15["class_0.5"] = (prediction_15["prob"] >= 0.5).astype(int)
prediction_15["class_0.7"] = (prediction_15["prob"] >= 0.7).astype(int)

prediction_15[["glucose", "diabetes_dummy", "prob",
               "class_0.3", "class_0.5", "class_0.7"]].round(3)

has_diabetes = prediction_15["diabetes_dummy"] == 1

fig, ax = plt.subplots()
ax.scatter(prediction_15.loc[has_diabetes, "glucose"], prediction_15.loc[has_diabetes, "prob"],
           color="darkorange", s=60, label="diabetes (1)")
ax.scatter(prediction_15.loc[~has_diabetes, "glucose"], prediction_15.loc[~has_diabetes, "prob"],
           color="grey", s=60, label="no diabetes (0)")
ax.axhline(0.3, color="blue",   linestyle="--")
ax.axhline(0.5, color="red",    linestyle="--")
ax.axhline(0.7, color="purple", linestyle="--")
ax.set_xlabel("Glucose (mg/dL)")
ax.set_ylabel("Predicted probability of diabetes")
ax.set_title("Predicted probabilities with the thresholds 0.3, 0.5 and 0.7")
ax.legend(title="What is true")
plt.show()

# --------------------------------------------------------------------
# Part 2 — Confusion tables, sensitivity and specificity
# --------------------------------------------------------------------

pd.crosstab(prediction_15["diabetes_dummy"], prediction_15["class_0.5"],
            rownames=["True"], colnames=["Predicted"])

# Replace every ______ below, then run this cell.
rows = []
for threshold in ["0.3", "0.5", "0.7"]:
    truth     = prediction_15["diabetes_dummy"]
    predicted = prediction_15["class_" + threshold]
    rows.append({"threshold": threshold,
                 "TP": ((truth == 1) & (predicted == 1)).sum(),
                 "FP": ((truth == 0) & (predicted == 1)).sum(),
                 "FN": (______).sum(),
                 "TN": ((truth == 0) & (predicted == 0)).sum()})

threshold_compare = pd.DataFrame(rows)
threshold_compare["sensitivity"] = threshold_compare["TP"] / (threshold_compare["TP"] + threshold_compare["FN"])
threshold_compare["specificity"] = ______

threshold_compare.round(3)

# --------------------------------------------------------------------
# Part 3 — The packaged version, on all 150 test patients
# --------------------------------------------------------------------

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

test_preds = test.copy()
test_preds["prob"] = log_fit.predict_proba(test[["glucose"]])[:, 1]
test_preds["predicted_0.5"] = (test_preds["prob"] >= 0.5).astype(int)

cm = confusion_matrix(test_preds["diabetes_dummy"], test_preds["predicted_0.5"])
cm

display = ConfusionMatrixDisplay(cm, display_labels=["neg (0)", "pos (1)"])
display = display.plot(cmap="Blues")
plt.show()

# --------------------------------------------------------------------
# Rows and columns are the other way round in R
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
rows = []
for threshold in np.round(np.arange(0.1, 1.0, 0.1), 1):
    truth = test_preds["diabetes_dummy"]
    prob  = test_preds["prob"]
    FN = ((truth == 1) & (prob <  threshold)).sum()
    FP = ((truth == 0) & (prob >= threshold)).sum()
    rows.append({"threshold": threshold, "FN": FN, "FP": FP, "cost": ______})

threshold_costs = pd.DataFrame(rows)
threshold_costs
