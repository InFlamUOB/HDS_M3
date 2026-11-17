# Exercise 4.1 — Unified modelling frameworks in R and Python
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-01-frameworks.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-01-frameworks.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "glmnet", "rpart"))

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot

# --------------------------------------------------------------------
# Part 1 — What model, and which engine
# --------------------------------------------------------------------

log_spec  <- logistic_reg(mode = "classification")
tree_spec <- decision_tree(mode = "classification")
rf_spec   <- rand_forest(mode = "classification")
knn_spec  <- nearest_neighbor(mode = "classification")

log_spec

tree_spec

log_spec_glm <- logistic_reg(mode = "classification") |>
  set_engine("glm")       # base R glm() with family = binomial

log_spec_glmnet <- logistic_reg(mode = "classification") |>
  set_engine("glmnet")    # penalised (regularised) regression

tree_spec_rpart <- decision_tree(mode = "classification") |>
  set_engine("rpart")     # rpart, the classic tree algorithm

log_spec_glmnet

# --------------------------------------------------------------------
# Part 2 — Fit and predict a logistic regression
# --------------------------------------------------------------------

diabetes <- read_csv("data/diabetes.csv") |>
  select(glucose, mass, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

count(train, diabetes)

logistic_spec <- logistic_reg(mode = "classification") |>
  set_engine("glm")

logistic_fit <- logistic_spec |>
  fit(diabetes ~ glucose, data = train)

logistic_fit

tidy(logistic_fit)

test_preds <- predict(logistic_fit, new_data = test, type = "prob") |>
  bind_cols(test)

head(test_preds)

ggplot(test_preds, aes(x = glucose, y = .pred_pos)) +
  geom_point(alpha = 0.5) +
  labs(x = "Glucose (mg/dL)", y = "Predicted probability of diabetes")

# --------------------------------------------------------------------
# Part 3 — Pipelines: recipes and workflows
# --------------------------------------------------------------------

log_recipe <- recipe(diabetes ~ glucose + mass + age, data = train) |>
  step_normalize(all_numeric_predictors())

log_workflow <- workflow() |>
  add_recipe(log_recipe) |>
  add_model(logistic_spec)

log_workflow_fit <- fit(log_workflow, data = train)

log_workflow_fit

predict(log_workflow_fit, new_data = test) |>
  bind_cols(test) |>
  summarise(accuracy        = mean(.pred_class == diabetes),
            always_says_neg = mean(diabetes == "neg"))

# Replace every ______ below, then run this cell.
tree_spec <- decision_tree(mode = "classification") |>
  set_engine("______")

tree_workflow_fit <- workflow() |>
  add_recipe(log_recipe) |>
  add_model(______) |>
  fit(data = train)

predict(tree_workflow_fit, new_data = test) |>
  bind_cols(test) |>
  summarise(accuracy = mean(.pred_class == diabetes))
