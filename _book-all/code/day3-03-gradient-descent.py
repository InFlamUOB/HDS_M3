# Exercise 3.4 — Gradient descent
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-03-gradient-descent.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-03-gradient-descent.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Minimising $f(x) = x^2$
# --------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

f       = lambda x: x**2
f_prime = lambda x: 2 * x

xs = np.linspace(-10, 10, 200)
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
axes[0].plot(xs, f(xs), color="steelblue");  axes[0].set_title("f(x) = x^2")
axes[1].plot(xs, f_prime(xs), color="firebrick"); axes[1].set_title("f'(x) = 2x")
for ax in axes:
    ax.axhline(0, color="black", lw=0.8); ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("x")
plt.tight_layout(); plt.show()

alpha = 0.8
x     = -10.0
path  = []

for i in range(1, 11):
    x = x - alpha * f_prime(x)
    path.append(x)
    print(f"step {i}: x = {x:.4g}  f(x) = {f(x):.4g}")

fig, ax = plt.subplots()
ax.plot(xs, f(xs), color="grey")
sc = ax.scatter(path, [f(v) for v in path], c=range(1, len(path) + 1),
                cmap="autumn_r", edgecolor="black", zorder=3)
cbar = fig.colorbar(sc, ax=ax, label="step")
ax.set_xlabel("x"); ax.set_ylabel("f(x)")
plt.show()

# --------------------------------------------------------------------
# Task 1 — Your turn, on a function whose minimum you can check
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
g       = lambda x: x**2 + 3 * x + 5
g_prime = lambda x: ______

alpha = 0.1
x = 2.0
for i in range(40):
    x = x - ______ * g_prime(x)

print(round(x, 4))   # your algebra said -1.5

# --------------------------------------------------------------------
# The learning rate is the whole game
# --------------------------------------------------------------------

import pandas as pd

def descend_1d(alpha, x0=-10.0, n=20):
    x = x0
    for _ in range(n):
        x = x - alpha * f_prime(x)
    return x

rates = [0.01, 0.1, 0.8, 1.0, 1.05]
pd.DataFrame({"alpha": rates,
              "final_x": [descend_1d(a) for a in rates],
              "final_f": [f(descend_1d(a)) for a in rates]})

# --------------------------------------------------------------------
# Task 2 — Find the edge yourself
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
rates = np.arange(0.8, 1.21, 0.05)
finals = [descend_1d(a, x0=-10.0, n=______) for a in rates]
pd.DataFrame({"alpha": rates.round(2), "final_x": np.round(finals, 3)})

# --------------------------------------------------------------------
# Local and global minima
# --------------------------------------------------------------------

h       = lambda x: x**4 + x**3 - 2 * x**2
h_prime = lambda x: 4 * x**3 + 3 * x**2 - 4 * x

def descend_h(x0, alpha=0.03, n=200):
    x = float(x0)
    for _ in range(n):
        x = x - alpha * h_prime(x)
    return {"start": x0, "end": x, "f_end": h(x)}

pd.DataFrame([descend_h(s) for s in (1, 0.2, 0, -0.1, -0.5, 2)])

grid_h = np.linspace(-2, 1.5, 300)
ends = [descend_h(s)["end"] for s in (1, 0.2, 0, -0.1, -0.5, 2)]

fig, ax = plt.subplots()
ax.plot(grid_h, h(grid_h), color="grey")
ax.scatter(ends, [h(e) for e in ends], color="red", zorder=3)
ax.set_xlabel("x"); ax.set_ylabel("f(x)")
plt.show()

# --------------------------------------------------------------------
# Task 3 — Where is the watershed
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
starts = np.arange(-0.1, 0.201, 0.01)
pd.DataFrame({"start": starts.round(2),
              "end": [round(______, 3) for s in starts]})

# --------------------------------------------------------------------
# Two parameters at once
# --------------------------------------------------------------------

fxy    = lambda x, y: x * np.sin(y) + x**2
grad_x = lambda x, y: np.sin(y) + 2 * x
grad_y = lambda x, y: x * np.cos(y)

x, y, alpha = 1.0, 2.0, 0.01
rows = [{"iter": 0, "x": x, "y": y, "f": fxy(x, y)}]

for i in range(1, 1001):
    gx, gy = grad_x(x, y), grad_y(x, y)
    x, y = x - alpha * gx, y - alpha * gy
    if i % 100 == 0:
        rows.append({"iter": i, "x": x, "y": y, "f": fxy(x, y)})

pd.DataFrame(rows)

# --------------------------------------------------------------------
# The result that should bother you
# --------------------------------------------------------------------

import pandas as pd
glu = pd.read_csv("data/glucose_study.csv")

def descend_mse(x, y, alpha, n):
    x, y = np.asarray(x, float), np.asarray(y, float)
    b0 = b1 = 0.0
    mse = np.empty(n)
    for i in range(n):
        r = y - (b0 + b1 * x)
        b0 = b0 - alpha * (-2 * r.mean())
        b1 = b1 - alpha * (-2 * (x * r).mean())
        mse[i] = np.mean((y - (b0 + b1 * x))**2)
    return {"b0": b0, "b1": b1, "mse": mse}

raw = descend_mse(glu["age"], glu["glucose"], alpha=1e-4, n=1000)
raw["b0"], raw["b1"], raw["mse"][-1]

# --------------------------------------------------------------------
# Task 4 — Make it converge
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
from sklearn.linear_model import LinearRegression

mx, sx = glu["age"].mean(), glu["age"].std()
my, sy = glu["glucose"].mean(), glu["glucose"].std()
zx = (glu["age"] - mx) / sx
zy = (glu["glucose"] - ______) / sy

std = descend_mse(zx, zy, alpha=0.1, n=50)

slope     = std["b1"] * sy / sx
intercept = my + sy * std["b0"] - slope * mx

ref = LinearRegression().fit(glu[["age"]], glu["glucose"])
print(intercept, slope)
print(round(ref.intercept_, 3), round(ref.coef_[0], 4))   # the answer to compare with

# --------------------------------------------------------------------
# One more thing the standardised fit tells you
# --------------------------------------------------------------------

std_shown = descend_mse((glu["age"] - glu["age"].mean()) / glu["age"].std(),
                        (glu["glucose"] - glu["glucose"].mean()) / glu["glucose"].std(),
                        alpha=0.1, n=50)

fig, ax = plt.subplots()
ax.plot(range(1, 51), std_shown["mse"], color="firebrick")
ax.set_xlabel("Iteration"); ax.set_ylabel("MSE (standardised units)")
plt.show()
