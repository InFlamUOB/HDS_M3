# Exercise 9.1 — Variable importance, and a column of pure noise
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day9/day6-01-importance.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day6-01-importance.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "ranger", "vip"))

library(tidyverse)
library(tidymodels)
library(vip)                   # variable importance for many kinds of model

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 3)     # show three significant figures in tables

# --------------------------------------------------------------------
# Part 1 — The data and the forest
# --------------------------------------------------------------------

diabetes <- read_csv("data/diabetes.csv") |>
  select(pregnant, glucose, mass, pedigree, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

count(train, diabetes)

set.seed(1)
rf_fit <- rand_forest(trees = 500) |>
  set_engine("ranger", importance = "impurity") |>
  set_mode("classification") |>
  fit(diabetes ~ ., data = train)

test_preds <- predict(rf_fit, new_data = test, type = "prob") |>
  bind_cols(test)

roc_auc(test_preds, truth = diabetes, .pred_pos, event_level = "second")

# --------------------------------------------------------------------
# Part 2 — Impurity-based importance
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
impurity_importance <- vi(rf_fit) |>
  mutate(share = Importance / ______)

impurity_importance

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

vip(rf_fit, num_features = 5, aesthetics = list(fill = "steelblue")) +
  labs(title = "Random forest: impurity-based importance")

# --------------------------------------------------------------------
# Part 3 — Permutation importance
# --------------------------------------------------------------------

auc_before <- roc_auc(test_preds, truth = diabetes, .pred_pos,
                      event_level = "second") |>
  pull(.estimate)

set.seed(1)
test_shuffled <- test |>
  mutate(glucose = sample(glucose))               # glucose now belongs to someone else

auc_after <- predict(rf_fit, new_data = test_shuffled, type = "prob") |>
  bind_cols(test_shuffled) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second") |>
  pull(.estimate)

c(before = auc_before, after = auc_after, drop = auc_before - auc_after)

# Replace every ______ below, then run this cell.
set.seed(1)
test_shuffled <- test |>
  mutate(mass = sample(______))

auc_after <- predict(rf_fit, new_data = ______, type = "prob") |>
  bind_cols(test_shuffled) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second") |>
  pull(.estimate)

c(before = auc_before, after = auc_after, drop = auc_before - auc_after)

set.seed(1)
perm_results <- tibble()                          # one row per shuffle

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

perm_importance <- perm_results |>
  group_by(variable) |>
  summarise(importance = mean(auc_drop), sd = sd(auc_drop)) |>
  arrange(desc(importance))

perm_importance

perm_importance |>
  ggplot(aes(x = importance, y = reorder(variable, importance))) +
  geom_col(fill = "coral") +
  geom_errorbar(aes(xmin = importance - sd, xmax = importance + sd),
                width = 0.3, orientation = "y") +
  geom_vline(xintercept = 0) +
  labs(x = "Mean drop in test AUC when the variable is shuffled (± 1 SD)",
       y = NULL, title = "Random forest: permutation importance")

# --------------------------------------------------------------------
# Part 4 — A control: a column of pure noise
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
set.seed(1)
train_noise <- train |> mutate(noise = rnorm(______))   # one random number per row
test_noise  <- test  |> mutate(noise = rnorm(______))

set.seed(1)
rf_noise <- rand_forest(trees = 500) |>
  set_engine("ranger", importance = "impurity") |>
  set_mode("classification") |>
  fit(diabetes ~ ., data = train_noise)

vi(rf_noise) |>
  mutate(share = Importance / sum(Importance))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

auc_noise_before <- predict(rf_noise, new_data = test_noise, type = "prob") |>
  bind_cols(test_noise) |>
  roc_auc(truth = diabetes, .pred_pos, event_level = "second") |>
  pull(.estimate)

set.seed(1)
perm_results_noise <- tibble()

for (variable in c("pregnant", "glucose", "mass", "pedigree", "age", "noise")) {
  for (repeat_number in 1:20) {
    test_shuffled <- test_noise
    test_shuffled[[variable]] <- sample(test_shuffled[[variable]])

    auc_after <- predict(rf_noise, new_data = test_shuffled, type = "prob") |>
      bind_cols(test_shuffled) |>
      roc_auc(truth = diabetes, .pred_pos, event_level = "second") |>
      pull(.estimate)

    perm_results_noise <- bind_rows(perm_results_noise,
                                    tibble(variable = variable,
                                           auc_drop = auc_noise_before - auc_after))
  }
}

perm_results_noise |>
  group_by(variable) |>
  summarise(importance = mean(auc_drop), sd = sd(auc_drop)) |>
  arrange(desc(importance))
