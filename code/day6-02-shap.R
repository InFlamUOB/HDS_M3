# Exercise 9.2 — SHAP values: global and local explanations
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-02-shap.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-02-shap.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "kernelshap", "ranger", "shapviz", "vip"))

library(tidyverse)
library(tidymodels)
library(vip)                   # impurity importance, as in Exercise 9.1
library(kernelshap)            # computes SHAP values for any model
library(shapviz)               # plots SHAP values

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
  set_engine("ranger", importance = "impurity") |>
  set_mode("classification") |>
  fit(diabetes ~ ., data = train)

test_preds <- predict(rf_fit, new_data = test, type = "prob") |>
  bind_cols(test)

# --------------------------------------------------------------------
# Part 1 — SHAP values for the test patients
# --------------------------------------------------------------------

set.seed(1)
background <- train |>
  slice_sample(n = 100) |>
  select(-diabetes)

shap_rf <- kernelshap(rf_fit, X = test |> select(-diabetes), bg_X = background,
                      type = "prob", verbose = FALSE)

sv_pos <- shapviz(shap_rf)$.pred_pos       # SHAP values for the probability of pos

dim(get_shap_values(sv_pos))               # one row per patient, one column per predictor
get_baseline(sv_pos)                       # the average prediction

# Replace every ______ below, then run this cell.
patient_shap <- get_shap_values(sv_pos)[1, ]
patient_shap

get_baseline(sv_pos) + ______(patient_shap)
test_preds$.pred_pos[1]

# --------------------------------------------------------------------
# Part 2 — Global summaries: bar plot and beeswarm
# --------------------------------------------------------------------

shap_importance <- get_shap_values(sv_pos) |>
  abs() |>
  colMeans()

sort(shap_importance, decreasing = TRUE)

sv_importance(sv_pos, fill = "steelblue")

sv_importance(sv_pos, kind = "beeswarm")

# --------------------------------------------------------------------
# Part 3 — One patient: the waterfall plot
# --------------------------------------------------------------------

test_preds |>
  slice(1) |>
  select(pregnant, glucose, mass, pedigree, age, diabetes, .pred_pos)

sv_waterfall(sv_pos, row_id = 1)

# Replace every ______ below, then run this cell.
highest <- which.max(test_preds$______)     # the row number of the highest probability
test_preds |> slice(highest)

sv_waterfall(sv_pos, row_id = ______)

# --------------------------------------------------------------------
# Part 4 — Logistic regression, and all the measures side by side
# --------------------------------------------------------------------

log_fit <- logistic_reg() |>
  set_engine("glm") |>
  fit(diabetes ~ ., data = train)

tidy(log_fit)

predict(log_fit, new_data = test, type = "prob") |>
  bind_cols(test) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second")

# Replace every ______ below, then run this cell.
predictor_sd <- train |>
  select(-diabetes) |>
  summarise(across(everything(), sd)) |>
  pivot_longer(everything(), names_to = "term", values_to = "sd")

coefs <- tidy(log_fit) |>
  filter(term != "(Intercept)") |>
  left_join(predictor_sd, by = "term") |>
  mutate(per_sd = estimate * ______)

coefs |> select(term, estimate, sd, per_sd)

auc_before <- roc_auc(test_preds, truth = diabetes, .pred_pos,
                      event_level = "second") |>
  pull(.estimate)

set.seed(1)
perm_results <- tibble()

for (variable in c("pregnant", "glucose", "mass", "pedigree", "age")) {
  for (repeat_number in 1:20) {
    test_shuffled <- test
    test_shuffled[[variable]] <- sample(test_shuffled[[variable]])

    auc_after <- predict(rf_fit, new_data = test_shuffled, type = "prob") |>
      bind_cols(test_shuffled) |>
      roc_auc(truth = diabetes, .pred_pos, event_level = "second") |>
      pull(.estimate)

    perm_results <- bind_rows(perm_results,
                              tibble(variable = variable,
                                     auc_drop = auc_before - auc_after))
  }
}

comparison <- vi(rf_fit) |>
  select(variable = Variable, impurity = Importance) |>
  left_join(perm_results |>
              group_by(variable) |>
              summarise(permutation = mean(auc_drop)),
            by = "variable") |>
  left_join(tibble(variable = names(shap_importance), shap = shap_importance),
            by = "variable") |>
  left_join(coefs |> select(variable = term, logistic = per_sd),
            by = "variable") |>
  mutate(impurity    = impurity / max(impurity),
         permutation = permutation / max(permutation),
         shap        = shap / max(shap),
         logistic    = abs(logistic) / max(abs(logistic)))

comparison

comparison |>
  pivot_longer(-variable, names_to = "measure", values_to = "relative") |>
  mutate(measure = factor(measure, levels = c("impurity", "permutation",
                                              "shap", "logistic"))) |>
  ggplot(aes(x = relative, y = reorder(variable, relative), fill = measure)) +
  geom_col(position = "dodge") +
  labs(x = "Importance relative to the top variable of each measure",
       y = NULL, fill = "Measure")
