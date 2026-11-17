# Exercise 5.4 — Random forests and tuning with a workflow
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-04-random-forest.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-04-random-forest.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

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

# --------------------------------------------------------------------
# Part 1 — A random forest with tunable hyperparameters
# --------------------------------------------------------------------

rf_spec <- rand_forest(mtry = tune(), min_n = tune(), trees = 500) |>
  set_engine("ranger") |>
  set_mode("classification")

rf_rec <- recipe(diabetes ~ ., data = train)

rf_wf <- workflow() |>
  add_model(rf_spec) |>
  add_recipe(rf_rec)

rf_wf

# --------------------------------------------------------------------
# Part 2 — The grid, the folds and the search
# --------------------------------------------------------------------

rf_grid <- grid_regular(mtry(range = c(1L, 5L)),
                        min_n(range = c(2L, 10L)),
                        levels = 5)
rf_grid

set.seed(123)
folds <- vfold_cv(train, v = 5, strata = diabetes)

rf_res <- tune_grid(
  rf_wf,
  resamples = folds,
  grid      = rf_grid,
  metrics   = metric_set(accuracy, roc_auc),
  control   = control_grid(event_level = "second")
)

rf_metrics <- collect_metrics(rf_res)
rf_metrics

# --------------------------------------------------------------------
# Part 3 — Inspect the tuning results
# --------------------------------------------------------------------

autoplot(rf_res, metric = "roc_auc")

# Replace every ______ below, then run this cell.
rf_metrics |>
  filter(.metric == ______) |>
  arrange(desc(______)) |>
  head(5)

# --------------------------------------------------------------------
# Part 4 — The final forest, evaluated once
# --------------------------------------------------------------------

best_rf <- select_best(rf_res, metric = "roc_auc")
best_rf

final_rf_wf <- finalize_workflow(rf_wf, best_rf)

set.seed(123)
final_rf_fit <- final_rf_wf |>
  fit(data = train)

train_preds <- predict(final_rf_fit, new_data = train, type = "prob") |>
  bind_cols(predict(final_rf_fit, new_data = train, type = "class")) |>
  bind_cols(train)
test_preds <- predict(final_rf_fit, new_data = test, type = "prob") |>
  bind_cols(predict(final_rf_fit, new_data = test, type = "class")) |>
  bind_cols(test)

class_metrics <- metric_set(accuracy, precision, recall, sens, spec)

class_metrics(train_preds, truth = diabetes, estimate = .pred_class,
              event_level = "second")
roc_auc(train_preds, truth = diabetes, .pred_pos, event_level = "second")

# Replace every ______ below, then run this cell.
class_metrics(______, truth = diabetes, estimate = .pred_class,
              event_level = "second")
roc_auc(______, truth = diabetes, .pred_pos, event_level = "second")

# --------------------------------------------------------------------
# Part 5 — Extra: was the tuning worth it?
# --------------------------------------------------------------------

set.seed(123)
rf_basic_fit <- workflow() |>
  add_model(rand_forest(mode = "classification") |> set_engine("ranger")) |>
  add_recipe(rf_rec) |>
  fit(data = train)

test_preds_basic <- predict(rf_basic_fit, new_data = test, type = "prob") |>
  bind_cols(predict(rf_basic_fit, new_data = test, type = "class")) |>
  bind_cols(test)

class_metrics(test_preds_basic, truth = diabetes, estimate = .pred_class,
              event_level = "second")
roc_auc(test_preds_basic, truth = diabetes, .pred_pos, event_level = "second")
