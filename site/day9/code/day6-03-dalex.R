# Exercise 9.3 — One toolbox for explanations: DALEX
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-03-dalex.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-03-dalex.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "DALEX", "DALEXtra", "ranger"))

library(tidyverse)
library(tidymodels)
library(DALEX)                 # explanations for any model
library(DALEXtra)              # connects DALEX to tidymodels

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 3)     # show three significant figures in tables

# --------------------------------------------------------------------
# Part 1 — The model and the explainer
# --------------------------------------------------------------------

diabetes <- read_csv("data/diabetes.csv") |>
  select(pregnant, glucose, mass, pedigree, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

set.seed(1)
rf_fit <- rand_forest(trees = 500) |>
  set_engine("ranger", importance = "impurity") |>
  set_mode("classification") |>
  fit(diabetes ~ ., data = train)

test_preds <- predict(rf_fit, new_data = test, type = "prob") |>
  bind_cols(predict(rf_fit, new_data = test)) |>     # adds .pred_class
  bind_cols(test)

test_preds |>
  metrics(truth = diabetes, estimate = .pred_class)

# Replace every ______ below, then run this cell.
explainer <- explain_tidymodels(
  rf_fit,
  data  = test |> select(-diabetes),
  y     = as.numeric(test$diabetes == ______),   # 1 = diabetes, 0 = none
  label = "Random forest",
  verbose = FALSE                                # no progress report
)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

performance <- model_performance(explainer)
performance$measures |> as_tibble()

# --------------------------------------------------------------------
# Part 2 — Global: which variables matter?
# --------------------------------------------------------------------

set.seed(1)
importance_dalex <- model_parts(explainer)

importance_dalex |>
  as_tibble() |>
  filter(permutation == 0) |>        # permutation 0 is the average over the 10 shuffles
  select(variable, dropout_loss)

full_loss <- importance_dalex |>
  as_tibble() |>
  filter(variable == "_full_model_", permutation == 0) |>
  pull(dropout_loss)

importance_dalex |>
  as_tibble() |>
  filter(permutation > 0, !variable %in% c("_full_model_", "_baseline_")) |>
  ggplot(aes(x = dropout_loss, y = reorder(variable, dropout_loss))) +
  geom_boxplot(fill = "coral", alpha = 0.6) +
  geom_vline(xintercept = full_loss, linetype = "dashed") +
  labs(x = "1 - AUC after shuffling the variable (dashed: no variable shuffled)",
       y = NULL, title = "Random forest: permutation importance (DALEX)")

# DALEX's own plot gives the same picture: plot(importance_dalex)

# --------------------------------------------------------------------
# Part 3 — How does the prediction change with one variable?
# --------------------------------------------------------------------

pdp_glucose <- model_profile(explainer, variables = "glucose", type = "partial",
                             N = NULL,                         # use all 150 patients
                             variable_splits_type = "uniform") # an evenly spaced grid

pdp_glucose$agr_profiles |>
  as_tibble() |>
  slice(seq(1, 101, by = 20))          # every 20th of the 101 grid points

pdp_glucose$agr_profiles |>
  ggplot(aes(x = `_x_`, y = `_yhat_`)) +
  geom_line(colour = "steelblue", linewidth = 1) +
  labs(x = "Glucose (mg/dL)", y = "Average predicted probability of diabetes",
       title = "Partial dependence profile: glucose")

# DALEX's own plot: plot(pdp_glucose)

pdp_glucose$cp_profiles |>
  as_tibble() |>
  ggplot(aes(x = glucose, y = `_yhat_`, group = `_ids_`)) +
  geom_line(colour = "grey60", alpha = 0.4) +
  geom_line(data = pdp_glucose$agr_profiles,
            aes(x = `_x_`, y = `_yhat_`, group = NULL),
            colour = "steelblue", linewidth = 1.2) +
  labs(x = "Glucose (mg/dL)", y = "Predicted probability of diabetes",
       title = "ICE profiles (grey) and their average (blue)")

# DALEX's own plot: plot(pdp_glucose, geom = "profiles")

# Replace every ______ below, then run this cell.
pdp_more <- model_profile(explainer, variables = c(______, ______), type = "partial",
                          N = NULL, variable_splits_type = "uniform")

pdp_more$agr_profiles |>
  ggplot(aes(x = `_x_`, y = `_yhat_`)) +
  geom_line(colour = "steelblue", linewidth = 1) +
  facet_wrap(~ `_vname_`, scales = "free_x") +
  labs(x = NULL, y = "Average predicted probability of diabetes")

# --------------------------------------------------------------------
# Part 4 — One patient: break-down and SHAP
# --------------------------------------------------------------------

new_observation <- test |>
  slice(1) |>
  select(-diabetes)

new_observation
predict(explainer, new_observation)          # her predicted probability

set.seed(1)
shap_patient <- predict_parts(explainer, new_observation = new_observation,
                              type = "shap", B = 25)

shap_patient |>
  as_tibble() |>
  filter(B == 0) |>                    # B = 0 holds the average over the 25 orders
  select(variable, contribution) |>
  arrange(desc(abs(contribution)))

shap_patient |>
  as_tibble() |>
  filter(B == 0) |>
  ggplot(aes(x = contribution, y = reorder(variable, abs(contribution)),
             fill = contribution > 0)) +
  geom_col(show.legend = FALSE) +
  scale_fill_manual(values = c("steelblue", "firebrick")) +
  labs(x = "SHAP contribution to the predicted probability", y = NULL,
       title = "SHAP values for the first test patient (DALEX)")

# DALEX's own plot, with boxplots over the 25 orders: plot(shap_patient)

# Replace every ______ below, then run this cell.
breakdown_patient <- predict_parts(explainer, new_observation = new_observation,
                                   type = ______)

breakdown_patient |>
  as_tibble() |>
  select(variable, contribution, cumulative)

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

# Optional, not run here: an interactive dashboard of everything above
# library(modelStudio)
# modelStudio(explainer)
