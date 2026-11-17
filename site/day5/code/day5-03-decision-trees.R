# Exercise 5.3 — Decision trees, overfitting and tuning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-03-decision-trees.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-03-decision-trees.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

library(tidyverse)
library(tidymodels)
library(rpart.plot)            # to draw a fitted rpart tree

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
# Part 1 — A basic decision tree
# --------------------------------------------------------------------

tree_spec_basic <- decision_tree() |>
  set_engine("rpart") |>
  set_mode("classification")

tree_rec <- recipe(diabetes ~ ., data = train)

tree_wf_basic <- workflow() |>
  add_model(tree_spec_basic) |>
  add_recipe(tree_rec)

tree_fit_basic <- tree_wf_basic |>
  fit(data = train)

tree_fit_basic

tree_fit_basic |>
  extract_fit_engine() |>
  rpart.plot(extra = 101, roundint = FALSE)

tree_spec_full <- decision_tree(cost_complexity = 0, min_n = 2) |>
  set_engine("rpart") |>
  set_mode("classification")

tree_fit_full <- workflow() |>
  add_model(tree_spec_full) |>
  add_recipe(tree_rec) |>
  fit(data = train)

tree_full_frame <- extract_fit_engine(tree_fit_full)$frame   # one row per node
sum(tree_full_frame$var == "<leaf>")                          # number of leaves

# --------------------------------------------------------------------
# Part 2 — Does a tree that nothing stops overfit?
# --------------------------------------------------------------------

train_preds_full <- predict(tree_fit_full, new_data = train, type = "prob") |>
  bind_cols(predict(tree_fit_full, new_data = train, type = "class")) |>
  bind_cols(train)

test_preds_full <- predict(tree_fit_full, new_data = test, type = "prob") |>
  bind_cols(predict(tree_fit_full, new_data = test, type = "class")) |>
  bind_cols(test)

conf_mat(train_preds_full, truth = diabetes, estimate = .pred_class)

class_metrics <- metric_set(accuracy, precision, recall, sens, spec)

class_metrics(train_preds_full, truth = diabetes, estimate = .pred_class,
              event_level = "second")

# Replace every ______ below, then run this cell.
conf_mat(______, truth = diabetes, estimate = .pred_class)

class_metrics(______, truth = diabetes, estimate = .pred_class,
              event_level = "second")

predict(tree_fit_basic, new_data = train, type = "class") |>
  bind_cols(train) |>
  accuracy(truth = diabetes, estimate = .pred_class)
predict(tree_fit_basic, new_data = test, type = "class") |>
  bind_cols(test) |>
  accuracy(truth = diabetes, estimate = .pred_class)

# --------------------------------------------------------------------
# Part 3 — Restraining the tree by hand
# --------------------------------------------------------------------

tree_spec_shallow <- decision_tree(cost_complexity = 0,   # no 1% rule, as in Part 1
                                   tree_depth = 3, min_n = 20) |>
  set_engine("rpart") |>
  set_mode("classification")

tree_fit_shallow <- workflow() |>
  add_model(tree_spec_shallow) |>
  add_recipe(tree_rec) |>
  fit(data = train)

tree_fit_shallow |>
  extract_fit_engine() |>
  rpart.plot(extra = 101, roundint = FALSE)

train_preds_shallow <- predict(tree_fit_shallow, new_data = train, type = "class") |>
  bind_cols(train)
test_preds_shallow <- predict(tree_fit_shallow, new_data = test, type = "class") |>
  bind_cols(test)

class_metrics(train_preds_shallow, truth = diabetes, estimate = .pred_class,
              event_level = "second")
class_metrics(test_preds_shallow, truth = diabetes, estimate = .pred_class,
              event_level = "second")

# Replace every ______ below, then run this cell.
tree_fit_try <- workflow() |>
  add_model(decision_tree(cost_complexity = 0, tree_depth = ______, min_n = ______) |>
              set_engine("rpart") |>
              set_mode("classification")) |>
  add_recipe(tree_rec) |>
  fit(data = train)

predict(tree_fit_try, new_data = train, type = "class") |>
  bind_cols(train) |>
  accuracy(truth = diabetes, estimate = .pred_class)
predict(tree_fit_try, new_data = test, type = "class") |>
  bind_cols(test) |>
  accuracy(truth = diabetes, estimate = .pred_class)

# --------------------------------------------------------------------
# Part 4 — Tuning the hyperparameters with a grid search
# --------------------------------------------------------------------

tree_spec_tune <- decision_tree(cost_complexity = 0, tree_depth = tune(), min_n = tune()) |>
  set_engine("rpart") |>
  set_mode("classification")

tree_wf_cv <- workflow() |>
  add_model(tree_spec_tune) |>
  add_recipe(tree_rec)

tree_grid <- grid_regular(tree_depth(range = c(1L, 10L)),
                          min_n(range = c(2L, 30L)),
                          levels = 5)
tree_grid

set.seed(123)
folds <- vfold_cv(train, v = 5, strata = diabetes)

tree_res <- tune_grid(
  tree_wf_cv,
  resamples = folds,
  grid      = tree_grid,
  metrics   = metric_set(roc_auc, accuracy),
  control   = control_grid(event_level = "second")
)

show_best(tree_res, metric = "roc_auc", n = 5)

autoplot(tree_res)

best_tree <- select_best(tree_res, metric = "roc_auc")
best_tree

final_tree_fit <- finalize_workflow(tree_wf_cv, best_tree) |>
  fit(data = train)

final_tree_fit |>
  extract_fit_engine() |>
  rpart.plot(extra = 101, roundint = FALSE)

# Replace every ______ below, then run this cell.
train_preds_final <- predict(final_tree_fit, new_data = train, type = "prob") |>
  bind_cols(predict(final_tree_fit, new_data = train, type = "class")) |>
  bind_cols(train)
test_preds_final <- predict(final_tree_fit, new_data = ______, type = "prob") |>
  bind_cols(predict(final_tree_fit, new_data = ______, type = "class")) |>
  bind_cols(test)

class_metrics(test_preds_final, truth = diabetes, estimate = .pred_class,
              event_level = "second")
roc_auc(train_preds_final, truth = diabetes, .pred_pos, event_level = "second")
roc_auc(test_preds_final,  truth = diabetes, ______, event_level = "second")
