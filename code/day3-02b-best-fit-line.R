# Exercise 3.3 — The best fit line
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-02b-best-fit-line.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-02b-best-fit-line.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Where we left off
# --------------------------------------------------------------------

library(tidyverse)

glu <- read_csv("data/glucose_study.csv")

fit_ols <- lm(glucose ~ age, data = glu)

glu_bad <- glu |>
  mutate(glucose = if_else(row_number() %in% c(1, 3, 5),
                           glucose * 3, glucose))

coef(fit_ols)

# --------------------------------------------------------------------
# Step 1 — The loss as a function of the parameters
# --------------------------------------------------------------------

glu |>
  slice(1:3) |>
  mutate(pred = 3 + 5 * age,
         r    = glucose - pred) |>
  summarise(MSE = mean(r^2))

# --------------------------------------------------------------------
# Task 1 — Score two candidate lines on all 80 patients
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
glu |>
  mutate(r_3_5 = glucose - (3 + 5 * age),
         r_4_7 = glucose - (______)) |>
  summarise(at_3_5 = mean(r_3_5^2),
            at_4_7 = mean(r_4_7^2)) |>
  round(1)

# --------------------------------------------------------------------
# Step 2 — Every candidate line at once
# --------------------------------------------------------------------

candidates <- expand_grid(b0 = seq(60, 160, by = 1),
                          b1 = seq(-1, 2, by = 0.02))

scores <- candidates |>
  cross_join(glu |> select(age, glucose)) |>
  mutate(r = glucose - (b0 + b1 * age)) |>
  summarise(MSE = mean(r^2),
            MAE = mean(abs(r)), .by = c(b0, b1))

scores

ggplot(scores, aes(x = b0, y = b1)) +
  geom_raster(aes(fill = log10(MSE))) +
  geom_contour(aes(z = log10(MSE)), colour = "white",
               alpha = 0.4, bins = 12) +
  annotate("point", x = coef(fit_ols)[[1]], y = coef(fit_ols)[[2]],
           colour = "red", size = 3) +
  scale_fill_viridis_c(option = "magma") +
  labs(x = expression(hat(beta)[0]), y = expression(hat(beta)[1]),
       fill = "log10(MSE)")

# --------------------------------------------------------------------
# Task 2 — Find the best candidate under each loss
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
scores |> slice_min(______, n = 1)
scores |> slice_min(MAE, n = 1)

coef(fit_ols)   # the fitted line, to compare

scores_bad <- candidates |>
  cross_join(glu_bad |> select(age, glucose)) |>
  mutate(r = glucose - (b0 + b1 * age)) |>
  summarise(MSE = mean(r^2),
            MAE = mean(abs(r)), .by = c(b0, b1))

bind_rows(
  clean_MSE        = scores     |> slice_min(MSE, n = 1) |> select(b0, b1),
  contaminated_MSE = scores_bad |> slice_min(MSE, n = 1) |> select(b0, b1),
  clean_MAE        = scores     |> slice_min(MAE, n = 1) |> select(b0, b1),
  contaminated_MAE = scores_bad |> slice_min(MAE, n = 1) |> select(b0, b1),
  .id = "best_under")
