# Exercise 4.2 — Fitting a logistic regression model
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day4/day4-02-logistic-regression.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day4-02-logistic-regression.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels"))

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())          # white background for every plot
options(pillar.sigfig = 4)     # show four significant figures in tables

diabetes <- read_csv("data/diabetes.csv") |>
  select(glucose, mass, age, diabetes) |>
  filter(glucose > 0, mass > 0) |>              # remove the impossible zeros
  mutate(diabetes = factor(diabetes, levels = c("neg", "pos")))

test_rows <- seq(1, nrow(diabetes), by = 5)     # every fifth person is held back
train <- diabetes[-test_rows, ]
test  <- diabetes[test_rows, ]

# --------------------------------------------------------------------
# Part 1 — Probability, odds and log-odds
# --------------------------------------------------------------------

prob     <- 0.8
odds     <- prob / (1 - prob)
log_odds <- log(odds)

c(probability = prob, odds = odds, log_odds = log_odds)

# Replace every ______ below, then run this cell.
tibble(prob = c(0.8, 0.5, 0.2, 0.9)) |>
  mutate(odds     = ______,
         log_odds = log(odds))

tibble(log_odds = seq(-6, 6, by = 0.1)) |>
  mutate(probability = 1 / (1 + exp(-log_odds))) |>
  ggplot(aes(x = log_odds, y = probability)) +
  geom_line(colour = "red", linewidth = 1) +
  geom_hline(yintercept = c(0, 1), linetype = "dashed", colour = "grey50") +
  labs(x = "Log-odds z", y = "Probability p = 1 / (1 + exp(-z))")

# --------------------------------------------------------------------
# Part 2 — Fit the model
# --------------------------------------------------------------------

count(train, diabetes)

logistic_spec <- logistic_reg(mode = "classification") |>
  set_engine("glm")

logistic_fit_glucose <- logistic_spec |>
  fit(diabetes ~ glucose, data = train)

tidy(logistic_fit_glucose)

# --------------------------------------------------------------------
# Part 3 — From the model to odds and probability
# --------------------------------------------------------------------

b <- logistic_fit_glucose$fit$coefficients    # intercept first, then the slope

glucose_value <- 120

log_odds_120 <- b[1] + b[2] * glucose_value   # the straight line
odds_120     <- exp(log_odds_120)             # odds
prob_120     <- 1 / (1 + exp(-log_odds_120))  # probability

round(c(log_odds = unname(log_odds_120), odds = unname(odds_120),
        probability = unname(prob_120)), 3)

predict(logistic_fit_glucose, new_data = tibble(glucose = 120), type = "prob")

# Replace every ______ below, then run this cell.
glucose_value <- ______

log_odds_160 <- b[1] + b[2] * glucose_value
odds_160     <- exp(log_odds_160)
prob_160     <- 1 / (1 + exp(-______))

round(c(log_odds = unname(log_odds_160), odds = unname(odds_160),
        probability = unname(prob_160)), 3)

test_preds <- predict(logistic_fit_glucose, new_data = test, type = "prob") |>
  rename(prob_pos = .pred_pos, prob_neg = .pred_neg) |>
  bind_cols(test)

test_preds |>
  select(glucose, diabetes, prob_pos, prob_neg) |>
  head()

test_preds |>
  mutate(diabetes_numeric = if_else(diabetes == "pos", 1, 0)) |>
  ggplot(aes(x = glucose)) +
  geom_point(aes(y = diabetes_numeric), alpha = 0.4) +
  geom_line(aes(y = prob_pos), colour = "red", linewidth = 1) +
  scale_y_continuous(breaks = c(0, 0.5, 1), limits = c(-0.05, 1.05)) +
  labs(x = "Glucose (mg/dL)",
       y = "Observed outcome (0/1) and predicted probability")
