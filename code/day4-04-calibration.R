# Exercise 4.4 — Is a predicted 0.7 worth 0.7?
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-04-calibration.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-04-calibration.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 3)     # show three significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(glucose, mass, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes       = factor(diabetes, levels = c("neg", "pos")),
         diabetes_dummy = if_else(diabetes == "pos", 1, 0))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

log_fit <- logistic_reg(mode = "classification") |>
  set_engine("glm") |>
  fit(diabetes ~ glucose, data = train)

train_preds <- predict(log_fit, new_data = train, type = "prob") |> bind_cols(train)
test_preds  <- predict(log_fit, new_data = test,  type = "prob") |> bind_cols(test)

# --------------------------------------------------------------------
# Part 1 — Calibration in the large
# --------------------------------------------------------------------

train_preds |>
  summarise(mean_predicted = mean(.pred_pos), prevalence = mean(diabetes_dummy))

test_preds |>
  summarise(mean_predicted = mean(.pred_pos), prevalence = mean(diabetes_dummy))

# --------------------------------------------------------------------
# Part 2 — The calibration table, step by step
# --------------------------------------------------------------------

test_binned <- test_preds |>
  mutate(bin = cut(.pred_pos, breaks = seq(0, 1, by = 0.2), include.lowest = TRUE))

test_binned |>
  select(glucose, diabetes_dummy, .pred_pos, bin) |>
  head()

# Replace every ______ below, then run this cell.
calibration_table <- test_binned |>
  group_by(bin) |>
  summarise(n              = n(),
            mean_predicted = mean(.pred_pos),
            observed_rate  = mean(______))

calibration_table

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

ggplot(calibration_table, aes(x = mean_predicted, y = observed_rate)) +
  geom_abline(linetype = "dashed", colour = "grey50") +
  geom_line(colour = "steelblue") +
  geom_point(aes(size = n), colour = "steelblue") +
  coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
  labs(x = "Mean predicted probability in the bin",
       y = "Observed rate in the bin", size = "Patients")

# --------------------------------------------------------------------
# Part 3 — Same order, different numbers
# --------------------------------------------------------------------

test_preds <- test_preds |>
  mutate(squashed = 0.5 + (.pred_pos - 0.5) / 3)

test_preds |>
  summarise(lowest_before  = min(.pred_pos), highest_before = max(.pred_pos),
            lowest_after   = min(squashed),  highest_after  = max(squashed),
            same_order     = all(rank(.pred_pos) == rank(squashed)))

# Replace every ______ below, then run this cell.
test_preds |>
  summarise(brier_before = mean((.pred_pos - diabetes_dummy)^2),
            brier_after  = mean((______ - diabetes_dummy)^2))

tibble(threshold = c(0.2, 0.5)) |>
  cross_join(test_preds) |>
  group_by(threshold) |>
  summarise(tested_before = sum(.pred_pos >= threshold),
            cost_before   = 5 * sum(diabetes == "pos" & .pred_pos < threshold) +
                                sum(diabetes == "neg" & .pred_pos >= threshold),
            tested_after  = sum(squashed >= threshold),
            cost_after    = 5 * sum(diabetes == "pos" & squashed < threshold) +
                                sum(diabetes == "neg" & squashed >= threshold))
