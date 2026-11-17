# Exercise 3.2 — Loss functions
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-02-loss-functions.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02-loss-functions.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# The data
# --------------------------------------------------------------------

library(tidyverse)

glu <- read_csv("data/glucose_study.csv")

glu

# --------------------------------------------------------------------
# Step 1 — One patient, one residual
# --------------------------------------------------------------------

glu <- glu |>
  mutate(pred_guess  = 120 + 0.5 * age,
         resid_guess = glucose - pred_guess)

glu

glu |> slice_max(abs(resid_guess), n = 1)

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point(alpha = 0.6) +
  geom_abline(intercept = 120, slope = 0.5,
              colour = "darkorange", linewidth = 1) +
  geom_segment(aes(xend = age, yend = pred_guess),
               colour = "red", alpha = 0.3) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

# --------------------------------------------------------------------
# Step 2 — From 80 residuals to one number
# --------------------------------------------------------------------

glu <- glu |>
  mutate(squared  = resid_guess^2,
         absolute = abs(resid_guess))

glu |> select(age, glucose, resid_guess, squared, absolute)

glu |>
  summarise(SSR  = sum(squared),
            MSE  = mean(squared),
            RMSE = sqrt(mean(squared)),
            MAE  = mean(absolute)) |>
  round(2)

# --------------------------------------------------------------------
# Task 1 — Score the fitted line against the hand-drawn one
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
fit_ols <- lm(glucose ~ age, data = glu)

glu <- glu |>
  mutate(pred_ols  = predict(fit_ols),
         resid_ols = ______)

glu |>
  summarise(MSE = mean(resid_ols^2),
            MAE = mean(abs(resid_ols))) |>
  round(2)

# --------------------------------------------------------------------
# Task 2 — Contaminate three readings
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
glu_bad <- glu |>
  mutate(glucose = if_else(row_number() %in% c(1, 3, 5),
                           glucose * ______, glucose))

fit_bad <- lm(glucose ~ age, data = ______)

rbind(clean        = coef(fit_ols),
      contaminated = coef(fit_bad))

# --------------------------------------------------------------------
# Step 3 — Which line is better depends on the loss
# --------------------------------------------------------------------

b_clean <- coef(fit_ols)
b_bad   <- coef(fit_bad)

glu_bad |>
  mutate(r_clean = glucose - (b_clean[1] + b_clean[2] * age),
         r_bad   = glucose - (b_bad[1]   + b_bad[2]   * age)) |>
  summarise(MSE_clean = mean(r_clean^2),   MSE_bad = mean(r_bad^2),
            MAE_clean = mean(abs(r_clean)), MAE_bad = mean(abs(r_bad))) |>
  round(1)
