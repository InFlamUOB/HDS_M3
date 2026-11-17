# Exercise 4.3 — The decision threshold
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-03-thresholds.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-03-thresholds.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 4)     # show four significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(glucose, mass, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes       = factor(diabetes, levels = c("neg", "pos")),
         diabetes_dummy = if_else(diabetes == "pos", 1, 0))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

# --------------------------------------------------------------------
# Part 1 — From a probability to a predicted class
# --------------------------------------------------------------------

log_fit <- logistic_reg(mode = "classification") |>
  set_engine("glm") |>
  fit(diabetes ~ glucose, data = train)

tidy(log_fit)

patients15 <- test |>
  slice(26:40)

prediction_15 <- predict(log_fit, new_data = patients15, type = "prob") |>
  rename(prob = .pred_pos) |>
  select(prob) |>
  bind_cols(patients15)

prediction_15 |>
  select(glucose, diabetes_dummy, prob)

prediction_15 <- prediction_15 |>
  mutate(class_0.3 = if_else(prob >= 0.3, 1, 0),
         class_0.5 = if_else(prob >= 0.5, 1, 0),
         class_0.7 = if_else(prob >= 0.7, 1, 0))

prediction_15 |>
  select(glucose, diabetes_dummy, prob, class_0.3, class_0.5, class_0.7)

prediction_15 |>
  mutate(truth = if_else(diabetes_dummy == 1, "diabetes (1)", "no diabetes (0)")) |>
  ggplot(aes(x = glucose, y = prob, colour = truth)) +
  geom_point(size = 3, alpha = 0.8) +
  geom_hline(yintercept = 0.3, colour = "blue",   linetype = "dashed") +
  geom_hline(yintercept = 0.5, colour = "red",    linetype = "dashed") +
  geom_hline(yintercept = 0.7, colour = "purple", linetype = "dashed") +
  scale_colour_manual(values = c("darkorange", "grey40")) +
  labs(x = "Glucose (mg/dL)", y = "Predicted probability of diabetes",
       colour = "What is true",
       title = "Predicted probabilities with the thresholds 0.3, 0.5 and 0.7")

# --------------------------------------------------------------------
# Part 2 — Confusion tables, sensitivity and specificity
# --------------------------------------------------------------------

table(True = prediction_15$diabetes_dummy, Predicted = prediction_15$class_0.5)

# Replace every ______ below, then run this cell.
threshold_compare <- prediction_15 |>
  pivot_longer(c(class_0.3, class_0.5, class_0.7),
               names_to = "threshold", values_to = "predicted") |>
  group_by(threshold) |>
  summarise(TP = sum(diabetes_dummy == 1 & predicted == 1),
            FP = sum(diabetes_dummy == 0 & predicted == 1),
            FN = sum(______),
            TN = sum(diabetes_dummy == 0 & predicted == 0)) |>
  mutate(sensitivity = TP / (TP + FN),
         specificity = ______)

threshold_compare

# --------------------------------------------------------------------
# Part 3 — The packaged version, on all 150 test patients
# --------------------------------------------------------------------

test_preds <- predict(log_fit, new_data = test, type = "prob") |>
  bind_cols(test) |>
  mutate(predicted_0.5 = factor(if_else(.pred_pos >= 0.5, "pos", "neg"),
                                levels = c("neg", "pos")))

cm <- test_preds |>
  conf_mat(truth = diabetes, estimate = predicted_0.5)

cm

autoplot(cm, type = "heatmap")

# --------------------------------------------------------------------
# Rows and columns are the other way round in Python
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
thresholds <- tibble(threshold = seq(0.1, 0.9, by = 0.1))

threshold_costs <- thresholds |>
  cross_join(test_preds) |>                      # every threshold with every patient
  group_by(threshold) |>
  summarise(FN = sum(diabetes == "pos" & .pred_pos <  threshold),
            FP = sum(diabetes == "neg" & .pred_pos >= threshold)) |>
  mutate(cost = ______)

threshold_costs
