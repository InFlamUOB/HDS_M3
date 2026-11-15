# Exercise 3.1 — Supervised learning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-01-supervised-learning.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-01-supervised-learning.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# The data we fit to
# --------------------------------------------------------------------

library(tidyverse)
library(tidymodels)

glu <- read_csv("data/glucose_study.csv")

glu

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point(alpha = 0.7) +
  labs(x = "Age in years (the feature)",
       y = "Glucose, mg/dL (the label)")

# --------------------------------------------------------------------
# Fitting the model
# --------------------------------------------------------------------

lm_model <- linear_reg() |> set_engine("lm") |> set_mode("regression")
ls_fit   <- lm_model |> fit(glucose ~ age, data = glu)

coef(extract_fit_engine(ls_fit))

# --------------------------------------------------------------------
# Predicting, inside and outside the data
# --------------------------------------------------------------------

new_patients <- data.frame(age = c(45, 10))
predict(ls_fit, new_data = new_patients)

# --------------------------------------------------------------------
# Task 1 — Predict from the parameters, not from the function
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
b <- coef(extract_fit_engine(ls_fit))
pred_60 <- ______ + ______ * 60
unname(pred_60)

# --------------------------------------------------------------------
# Task 2 — Change the algorithm, keep everything else
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
library(rpart); library(rpart.plot)

dt_model <- decision_tree(mode = "regression") |> set_engine("______")
dt_fit   <- dt_model |> fit(glucose ~ age, data = glu)

rpart.plot(extract_fit_engine(dt_fit), roundint = FALSE)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

dt_fit_shown <- decision_tree(mode = "regression") |> set_engine("rpart") |>
  fit(glucose ~ age, data = glu)

glu_pred <- glu |>
  mutate(pred_tree = predict(dt_fit_shown, new_data = glu)$.pred,
         pred_line = predict(ls_fit,       new_data = glu)$.pred)

ggplot(glu_pred, aes(x = age)) +
  geom_point(aes(y = glucose), alpha = 0.5) +
  geom_step(aes(y = pred_tree), colour = "darkred", linewidth = 1) +
  geom_line(aes(y = pred_line), colour = "steelblue", linewidth = 1) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

# --------------------------------------------------------------------
# Task 3 — The role of the dataset
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
glu30 <- glu |> slice(______)

ls_fit30 <- lm_model |> fit(glucose ~ age, data = ______)
dt_fit30 <- decision_tree(mode = "regression") |> set_engine("rpart") |>
  fit(glucose ~ age, data = ______)

at25 <- data.frame(age = 25)
c(line80 = predict(ls_fit,   at25)$.pred, line30 = predict(ls_fit30, at25)$.pred,
  tree80 = predict(dt_fit_shown, at25)$.pred, tree30 = predict(dt_fit30, at25)$.pred)
