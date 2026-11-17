# Exercise 9.4 — For whom is the model worst?
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-04-subgroups.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-04-subgroups.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "ranger"))

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

set.seed(1)
rf_fit <- rand_forest(trees = 500) |>
  set_engine("ranger") |>
  set_mode("classification") |>
  fit(diabetes ~ ., data = train)

test_preds <- predict(rf_fit, new_data = test, type = "prob") |>
  bind_cols(predict(rf_fit, new_data = test)) |>     # adds .pred_class
  bind_cols(test)

# --------------------------------------------------------------------
# Part 1 — Performance by age group
# --------------------------------------------------------------------

test_preds <- test_preds |>
  mutate(age_group = cut(age, breaks = c(20, 29, 39, Inf),
                         labels = c("21-29", "30-39", "40 and over")))

test_preds |>
  group_by(age_group) |>
  summarise(patients = n(), with_diabetes = sum(diabetes == "pos"))

auc_by_age <- test_preds |>
  group_by(age_group) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second")

sens_by_age <- test_preds |>
  group_by(age_group) |>
  sens(truth = diabetes, estimate = .pred_class, event_level = "second")

spec_by_age <- test_preds |>
  group_by(age_group) |>
  spec(truth = diabetes, estimate = .pred_class, event_level = "second")

bind_rows(auc_by_age, sens_by_age, spec_by_age) |>
  select(age_group, .metric, .estimate) |>
  pivot_wider(names_from = .metric, values_from = .estimate)

test_preds |>
  ggplot(aes(x = age_group, y = .pred_pos, colour = diabetes)) +
  geom_boxplot(outlier.shape = NA) +
  geom_point(position = position_jitterdodge(jitter.width = 0.15, seed = 1), alpha = 0.5) +
  geom_hline(yintercept = 0.5, linetype = "dashed") +
  labs(x = "Age group", y = "Predicted probability of diabetes", colour = "Diabetes")

# --------------------------------------------------------------------
# Part 2 — By BMI, and how far to trust a small group
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
test_preds <- test_preds |>
  mutate(bmi_group = if_else(mass < ______, "under 30", "30 and over"))

test_preds |>
  group_by(bmi_group) |>
  summarise(patients = n(), with_diabetes = sum(diabetes == "pos"))

bind_rows(
  test_preds |> group_by(bmi_group) |> roc_auc(truth = diabetes, .pred_pos, event_level = "second"),
  test_preds |> group_by(bmi_group) |> sens(truth = diabetes, estimate = .pred_class, event_level = "second"),
  test_preds |> group_by(______) |> spec(truth = diabetes, estimate = .pred_class, event_level = "second")
) |>
  select(bmi_group, .metric, .estimate) |>
  pivot_wider(names_from = .metric, values_from = .estimate)
