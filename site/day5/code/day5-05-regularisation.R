# Exercise 5.5 — Regularisation: lasso and ridge logistic regression
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-05-regularisation.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-05-regularisation.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "glmnet"))

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 3)     # show three significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(pregnant, glucose, mass, pedigree, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

norm_rec <- recipe(diabetes ~ ., data = train) |>
  step_normalize(all_numeric_predictors())

# --------------------------------------------------------------------
# Part 1 — Coefficient paths
# --------------------------------------------------------------------

lambdas <- 10^seq(-3, 0, length.out = 31)

lasso_fit <- workflow() |>
  add_model(logistic_reg(penalty = 0.01, mixture = 1) |>
              set_engine("glmnet", path_values = lambdas)) |>
  add_recipe(norm_rec) |>
  fit(data = train)

lasso_path <- lasso_fit |>
  extract_fit_engine() |>        # the glmnet fit, with the whole path
  tidy(return_zeros = TRUE) |>  # keep the coefficients that are exactly zero
  filter(term != "(Intercept)")

lasso_path |>
  filter(step == 11)             # the coefficients at one penalty

ggplot(lasso_path, aes(x = lambda, y = estimate, colour = term)) +
  geom_line(linewidth = 1) +
  geom_hline(yintercept = 0, colour = "grey50") +
  scale_x_log10() +
  labs(x = "Penalty (log scale)", y = "Coefficient (per standard deviation)",
       colour = NULL, title = "Lasso: coefficients drop out one by one")

# Replace every ______ below, then run this cell.
ridge_fit <- workflow() |>
  add_model(logistic_reg(penalty = 0.01, mixture = ______) |>
              set_engine("glmnet", path_values = lambdas)) |>
  add_recipe(norm_rec) |>
  fit(data = train)

ridge_path <- ridge_fit |>
  extract_fit_engine() |>
  tidy(return_zeros = TRUE) |>  # keep the coefficients that are exactly zero
  filter(term != "(Intercept)")

ggplot(ridge_path, aes(x = lambda, y = estimate, colour = term)) +
  geom_line(linewidth = 1) +
  geom_hline(yintercept = 0, colour = "grey50") +
  scale_x_log10() +
  labs(x = "Penalty (log scale)", y = "Coefficient (per standard deviation)",
       colour = NULL, title = "Ridge: every coefficient shrinks, none drops out")

# --------------------------------------------------------------------
# Part 2 — Choosing the penalty by cross-validation
# --------------------------------------------------------------------

lasso_wf <- workflow() |>
  add_model(logistic_reg(penalty = tune(), mixture = 1) |>
              set_engine("glmnet", path_values = lambdas)) |>
  add_recipe(norm_rec)

set.seed(123)
folds <- vfold_cv(train, v = 5, strata = diabetes)

lasso_res <- tune_grid(
  lasso_wf,
  resamples = folds,
  grid      = tibble(penalty = lambdas),
  metrics   = metric_set(roc_auc),
  control   = control_grid(event_level = "second")
)

show_best(lasso_res, metric = "roc_auc", n = 5)

autoplot(lasso_res) +
  labs(title = "Cross-validated AUC along the lasso path")

# --------------------------------------------------------------------
# Part 3 — Does the penalty help on the test rows?
# --------------------------------------------------------------------

best_penalty <- select_best(lasso_res, metric = "roc_auc")
best_penalty

final_lasso_fit <- finalize_workflow(lasso_wf, best_penalty) |>
  fit(data = train)
tidy(final_lasso_fit)

plain_fit <- workflow() |>
  add_model(logistic_reg() |> set_engine("glm")) |>
  add_recipe(norm_rec) |>
  fit(data = train)

# Replace every ______ below, then run this cell.
predict(final_lasso_fit, new_data = test, type = "prob") |>
  bind_cols(test) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second")

predict(______, new_data = test, type = "prob") |>
  bind_cols(test) |>
  roc_auc(truth = diabetes, ______, event_level = "second")
