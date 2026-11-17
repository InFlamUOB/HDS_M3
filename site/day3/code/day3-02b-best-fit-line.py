# Exercise 3.3 — The best fit line
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-02b-best-fit-line.html
#
# The Python code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02b-best-fit-line.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression

glu = pd.read_csv("data/glucose_study.csv")

glu3 = glu.iloc[:3]
glu3

age     = glu3["age"]       # x, the feature
glucose = glu3["glucose"]   # y, the outcome label
m       = len(age)          # the number of samples

# --------------------------------------------------------------------
# Pause for understanding!
# --------------------------------------------------------------------

def mse_practical(beta0, beta1, x, y, m):
    return (1 / m) * np.sum((y - (beta0 + beta1 * x)) ** 2)

mse_practical(3, 5, age, glucose, m)

mse_practical(beta0=3, beta1=5, x=age, y=glucose, m=m)

((194 - 143)**2 + (129 - 223)**2 + (132 - 133)**2) / 3

# Replace every ______ below, then run this cell.
mse_practical(beta0=______, beta1=______, x=age, y=glucose, m=m)

ages = np.array([0, 60])   # the two ends of each line

fig, ax = plt.subplots()
ax.scatter(glu3["age"], glu3["glucose"], color="black", s=60, zorder=3)
ax.plot(ages, 3 + 5 * ages, color="blue", label="B0 = 3, B1 = 5")
ax.plot(ages, 4 + 7 * ages, color="red", label="B0 = 4, B1 = 7")
ax.set_xlim(0, 60)
ax.set_ylim(0, 350)
ax.set_title("Different betas")
ax.set_xlabel("Age")
ax.set_ylabel("Glucose")
ax.legend()
plt.show()

# --------------------------------------------------------------------
# Trying many lines
# --------------------------------------------------------------------

age     = glu["age"]
glucose = glu["glucose"]
m       = len(age)

ages = np.array([glu["age"].min(), glu["age"].max()])

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(glu["age"], glu["glucose"], color="black", s=25, zorder=3)
colours = {100: "tab:red", 110: "tab:green", 120: "tab:blue"}    # one colour per intercept
styles = {0: "-", 0.25: "--", 0.5: "-.", 0.75: ":"}              # one line type per slope
for b0 in colours:
    for b1 in styles:
        ax.plot(ages, b0 + b1 * ages, color=colours[b0], linestyle=styles[b1],
                label=f"B0 = {b0}, B1 = {b1}")
ax.set_title("Effect of different B0 and B1 values on the regression line")
ax.set_xlabel("Age (feature)")
ax.set_ylabel("Glucose (label)")
ax.legend(title="Parameter combination", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------
# The loss function in 3D
# --------------------------------------------------------------------

B0_values = np.arange(60, 161, 1)                   # 60, 61, ..., 160
B1_values = np.round(np.linspace(-1, 2, 151), 2)    # -1, -0.98, ..., 2

df = pd.DataFrame(
    [{"B0": b0, "B1": b1, "MSE": mse_practical(b0, b1, age, glucose, m)}
     for b0 in B0_values for b1 in B1_values]
)

df.head()

from matplotlib.colors import LogNorm

# plot_surface() wants the MSE as a matrix: one row per B1, one column per B0
MSE_matrix = df.pivot(index="B1", columns="B0", values="MSE")
B0_grid, B1_grid = np.meshgrid(MSE_matrix.columns, MSE_matrix.index)
best = df[df["MSE"] == df["MSE"].min()]    # the lowest point, to mark it in red

fig = plt.figure(figsize=(7, 5.5))
ax = fig.add_subplot(projection="3d", computed_zorder=False)
ax.plot_surface(B0_grid, B1_grid, MSE_matrix.values, cmap="magma", norm=LogNorm())
ax.scatter(best["B0"], best["B1"], best["MSE"], color="red", s=70, zorder=5)
ax.view_init(elev=22, azim=-55)    # the angle we look from: try other numbers
ax.set_xlabel("B0 (intercept)")
ax.set_ylabel("B1 (slope)")
ax.set_zlabel("MSE", labelpad=12)
plt.show()

# This plot needs the plotly package: pip install plotly
import plotly.graph_objects as go

fig_3d = go.Figure(go.Surface(x=MSE_matrix.columns, y=MSE_matrix.index,
                              z=MSE_matrix.values, colorbar={"title": "MSE"}))
fig_3d.add_trace(go.Scatter3d(x=best["B0"], y=best["B1"], z=best["MSE"],
                              mode="markers", marker={"size": 7, "color": "red"},
                              name="Minimum MSE"))
fig_3d.update_layout(scene={"xaxis_title": "B0 (intercept)",
                            "yaxis_title": "B1 (slope)",
                            "zaxis_title": "MSE",
                            "camera": {"eye": {"x": 1.5, "y": -1.7, "z": 0.9}}})
fig_3d.show()

df["MSE"].min()

# Find the minimum point
df[df["MSE"] == df["MSE"].min()]

fig, ax = plt.subplots()
cs = ax.contourf(MSE_matrix.columns, MSE_matrix.index, np.log10(MSE_matrix.values),
                 levels=20, cmap="magma")
ax.scatter(best["B0"], best["B1"], color="red", zorder=3)
fig.colorbar(cs, ax=ax, label="log10(MSE)")
ax.set_xlabel("B0 (intercept)")
ax.set_ylabel("B1 (slope)")
plt.show()

fit1 = LinearRegression()
fit1 = fit1.fit(glu[["age"]], glu["glucose"])

print(fit1.intercept_, fit1.coef_[0])
