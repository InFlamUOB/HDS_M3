# Exercise 3.5 — Ordinary least squares, in closed form
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-04-ols.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-04-ols.qmd. Edit the chapter, not this file.

# Replace every ______ below, then run this cell.
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

glu = pd.read_csv("data/glucose_study.csv")
x, y = glu["age"], glu["glucose"]

b1hat = ______ / ______          # pandas: x.cov(y) and x.var(), both ddof=1
b0hat = y.mean() - b1hat * ______

fit = LinearRegression().fit(glu[["age"]], y)
print({"closed_form": (b0hat, b1hat), "sklearn": (fit.intercept_, fit.coef_[0])})

# Replace every ______ below, then run this cell.
r_fitted = ______                      # residuals of the fitted line
r_guess  = y - (120 + 0.5 * x)

print({"fitted": (r_fitted.sum(), (x * r_fitted).sum()),
       "guess":  (r_guess.sum(),  (x * r_guess).sum())})

rows = []
for lo, hi in [(21, 25), (21, 30), (21, 40), (21, 81)]:
    s = glu[(glu["age"] >= lo) & (glu["age"] <= hi)]
    rows.append({"band": f"{lo} to {hi}", "n": len(s),
                 "var_age": s["age"].var(),
                 "slope": s["age"].cov(s["glucose"]) / s["age"].var()})
pd.DataFrame(rows)

# Replace every ______ below, then run this cell.
bwt = pd.read_csv("data/birthweight.csv")

slope_bw     = ______
intercept_bw = ______

fit_bw = LinearRegression().fit(bwt[["bpd"]], bwt["bw"])
print({"closed_form": (intercept_bw, slope_bw),
       "sklearn": (fit_bw.intercept_, fit_bw.coef_[0])})
