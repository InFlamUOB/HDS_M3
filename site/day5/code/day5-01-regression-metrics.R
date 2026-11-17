# Exercise 5.1 — Evaluating a regression model on training and test data
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-01-regression-metrics.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-01-regression-metrics.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels"))

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 4)     # show four significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(glucose, mass, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

dim(diabetes)
dim(train)
dim(test)

# --------------------------------------------------------------------
# Part 1 — A cubic model as a pre-processing step
# --------------------------------------------------------------------

cubic_spec <- linear_reg() |>
  set_engine("lm")

cubic_rec <- recipe(glucose ~ age, data = train) |>
  step_poly(age, degree = 3)

cubic_rec |>
  prep() |>
  bake(new_data = NULL)

cubic_wf <- workflow() |>
  add_model(cubic_spec) |>
  add_recipe(cubic_rec)

model_cubic <- cubic_wf |>
  fit(data = train)

tidy(model_cubic)

age_grid <- tibble(age = 21:81)
curve <- augment(model_cubic, age_grid)

ggplot(train, aes(x = age, y = glucose)) +
  geom_point(alpha = 0.3) +
  geom_line(data = curve, aes(y = .pred), colour = "red", linewidth = 1) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)",
       title = "Cubic fit of glucose on age, training rows")

# --------------------------------------------------------------------
# Part 2 — Predictions on the training and the test rows
# --------------------------------------------------------------------

predict(model_cubic, new_data = train) |>
  head()

train_preds <- augment(model_cubic, new_data = train)
test_preds  <- augment(model_cubic, new_data = test)

head(test_preds)

both_sets <- bind_rows(train_preds |> mutate(set = "train (600)"),
                       test_preds  |> mutate(set = "test (150)")) |>
  mutate(set = factor(set, levels = c("train (600)", "test (150)")))   # train first

ggplot(both_sets, aes(x = age, y = glucose)) +
  geom_point(alpha = 0.3) +
  geom_line(aes(y = .pred), colour = "red", linewidth = 1) +
  facet_wrap(~ set) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)",
       title = "The same fitted cubic, on the training and the test rows")

# --------------------------------------------------------------------
# Part 3 — Measuring the error, by hand and with a package
# --------------------------------------------------------------------

train_preds |>
  mutate(error = glucose - .pred) |>
  summarise(MSE  = mean(error^2),
            RMSE = sqrt(MSE),
            MAE  = mean(abs(error)))

# Replace every ______ below, then run this cell.
test_preds |>
  mutate(error = ______) |>
  summarise(MSE  = mean(error^2),
            RMSE = ______,
            MAE  = mean(abs(error)))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

rmse(train_preds, truth = glucose, estimate = .pred)

reg_metrics <- metric_set(rmse, mae)
reg_metrics(train_preds, truth = glucose, estimate = .pred)

# Replace every ______ below, then run this cell.
reg_metrics(______, truth = glucose, estimate = ______)

# --------------------------------------------------------------------
# Part 4 — More flexible is not more accurate
# --------------------------------------------------------------------

degree_results <- tibble()

for (d in 1:8) {
  poly_wf <- workflow() |>
    add_model(linear_reg()) |>
    add_recipe(recipe(glucose ~ age, data = train) |>
                 step_poly(age, degree = d))
  poly_fit <- poly_wf |>
    fit(data = train)

  train_rmse <- augment(poly_fit, new_data = train) |>
    rmse(truth = glucose, estimate = .pred)
  test_rmse <- augment(poly_fit, new_data = test) |>
    rmse(truth = glucose, estimate = .pred)

  degree_results <- bind_rows(degree_results,
                              tibble(degree     = d,
                                     train_rmse = train_rmse$.estimate,
                                     test_rmse  = test_rmse$.estimate))
}

degree_results

degree_results |>
  pivot_longer(c(train_rmse, test_rmse), names_to = "set", values_to = "RMSE") |>
  ggplot(aes(x = degree, y = RMSE, colour = set)) +
  geom_line() +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 1:8) +
  labs(x = "Degree of the polynomial", y = "RMSE (mg/dL)", colour = NULL,
       title = "Training error keeps falling; test error does not")
