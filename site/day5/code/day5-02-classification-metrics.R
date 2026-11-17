# Exercise 5.2 — Evaluating a classification model on training and test data
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day5/day5-02-classification-metrics.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day5-02-classification-metrics.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

library(tidyverse)
library(tidymodels)
library(patchwork)             # to put two plots side by side

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 3)     # show three significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(pregnant, glucose, mass, pedigree, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

count(train, diabetes)
count(test, diabetes)

# --------------------------------------------------------------------
# Part 1 — An age-only model, and its predictions
# --------------------------------------------------------------------

log_spec <- logistic_reg() |>
  set_engine("glm") |>
  set_mode("classification")

log_rec <- recipe(diabetes ~ age, data = train)

log_wf <- workflow() |>
  add_model(log_spec) |>
  add_recipe(log_rec)

log_fit <- log_wf |>
  fit(data = train)

tidy(log_fit)

train_preds <- predict(log_fit, new_data = train, type = "prob") |>
  bind_cols(train) |>
  mutate(pred_class = factor(if_else(.pred_pos >= 0.5, "pos", "neg"),
                             levels = c("neg", "pos")))

head(train_preds)

test_preds <- predict(log_fit, new_data = test, type = "prob") |>
  bind_cols(test) |>
  mutate(pred_class = factor(if_else(.pred_pos >= 0.5, "pos", "neg"),
                             levels = c("neg", "pos")))

count(test_preds, pred_class)

# --------------------------------------------------------------------
# Part 2 — Metrics on the training and the test rows
# --------------------------------------------------------------------

class_metrics <- metric_set(accuracy, precision, recall, sens, spec)

class_metrics(train_preds, truth = diabetes, estimate = pred_class,
              event_level = "second")

# Replace every ______ below, then run this cell.
class_metrics(______, truth = diabetes, estimate = pred_class,
              event_level = ______)

# --------------------------------------------------------------------
# Part 3 — Score distributions and the ROC curve
# --------------------------------------------------------------------

train_plot <- ggplot(train_preds, aes(x = diabetes, y = .pred_pos, fill = diabetes)) +
  geom_boxplot(alpha = 0.7) +
  labs(x = "True class", y = "Predicted probability of diabetes",
       title = "Training rows") +
  theme(legend.position = "none")

test_plot <- ggplot(test_preds, aes(x = diabetes, y = .pred_pos, fill = diabetes)) +
  geom_boxplot(alpha = 0.7) +
  labs(x = "True class", y = "Predicted probability of diabetes",
       title = "Test rows") +
  theme(legend.position = "none")

train_plot + test_plot

roc_age <- roc_curve(test_preds, truth = diabetes, .pred_pos, event_level = "second")
auc_age <- roc_auc(test_preds, truth = diabetes, .pred_pos, event_level = "second")

auc_age

autoplot(roc_age) +
  ggtitle("ROC curve, age-only model (test rows)")

# Replace every ______ below, then run this cell.
roc_auc(______, truth = diabetes, ______, event_level = "second")

# --------------------------------------------------------------------
# Part 4 — Include more features
# --------------------------------------------------------------------

log_rec2 <- recipe(diabetes ~ pregnant + glucose + mass + pedigree + age,
                   data = train) |>
  step_normalize(all_numeric_predictors())

log_wf2 <- workflow() |>
  add_model(log_spec) |>
  add_recipe(log_rec2)

log_fit2 <- log_wf2 |>
  fit(data = train)

tidy(log_fit2)

train_preds2 <- predict(log_fit2, new_data = train, type = "prob") |>
  bind_cols(train) |>
  mutate(pred_class = factor(if_else(.pred_pos >= 0.5, "pos", "neg"),
                             levels = c("neg", "pos")))

test_preds2 <- predict(log_fit2, new_data = test, type = "prob") |>
  bind_cols(test) |>
  mutate(pred_class = factor(if_else(.pred_pos >= 0.5, "pos", "neg"),
                             levels = c("neg", "pos")))

class_metrics(train_preds2, truth = diabetes, estimate = pred_class,
              event_level = "second")
class_metrics(test_preds2, truth = diabetes, estimate = pred_class,
              event_level = "second")

# Replace every ______ below, then run this cell.
roc_rich <- roc_curve(______, truth = diabetes, .pred_pos, event_level = "second")
auc_rich <- roc_auc(______, truth = diabetes, .pred_pos, event_level = "second")

auc_rich

roc_both <- bind_rows(
  roc_curve(test_preds,  truth = diabetes, .pred_pos, event_level = "second") |>
    mutate(model = "age only"),
  roc_curve(test_preds2, truth = diabetes, .pred_pos, event_level = "second") |>
    mutate(model = "five predictors"))

ggplot(roc_both, aes(x = 1 - specificity, y = sensitivity, colour = model)) +
  geom_path(linewidth = 1) +
  geom_abline(linetype = "dashed", colour = "grey50") +
  coord_equal() +
  labs(colour = NULL, title = "ROC curves on the test rows")
