# Exercise 3.2 — Residuals and loss functions
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
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse"))

library(tidyverse)

theme_set(theme_bw())         # white background for every plot
options(pillar.sigfig = 6)    # print tables with more decimal places

glu <- read_csv("data/glucose_study.csv")

head(glu)

# --------------------------------------------------------------------
# Part 1 — Follow one prediction into a loss
# --------------------------------------------------------------------

three <- tibble(person  = c("A", "B", "C"),
                age     = c(28, 30, 55),
                glucose = c(194, 115, 111))

three

ggplot(three, aes(x = age, y = glucose)) +
  geom_abline(intercept = 110, slope = 0.3, colour = "darkorange", linewidth = 1) +
  geom_segment(aes(xend = age, yend = 110 + 0.3 * age),
               colour = "red", linetype = "dashed") +
  geom_point(aes(y = 110 + 0.3 * age), colour = "darkorange", size = 3) +
  geom_point(size = 3) +
  geom_text(aes(label = person), nudge_x = 1.5, fontface = "bold") +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

# Replace every ______ below, then run this cell.
three <- three |>
  mutate(predicted = 110 + 0.3 * age,
         residual  = ______ - ______,
         absolute  = abs(residual),
         squared   = residual^2)

three

three |>
  summarise(MAE  = mean(absolute),
            MSE  = mean(squared),
            RMSE = sqrt(mean(squared)))

# --------------------------------------------------------------------
# Stuck?
# --------------------------------------------------------------------

# put the three squares side by side, with a gap of 10 between them
squares <- three |>
  mutate(left  = c(0, 85.6, 99.6),
         right = left + absolute)

ggplot(squares) +
  geom_rect(aes(xmin = left, xmax = right, ymin = 0, ymax = absolute),
            fill = "firebrick", alpha = 0.3) +
  geom_segment(aes(x = left, xend = right, y = 0, yend = 0),
               colour = "firebrick", linewidth = 2) +
  geom_text(aes(x = (left + right) / 2, y = absolute + 4, label = person),
            fontface = "bold") +
  coord_fixed() +                       # one unit is the same length both ways
  labs(x = "Thick line: the absolute residual. Shaded square: the squared residual.",
       y = "Size of the residual (mg/dL)") +
  theme(axis.text.x = element_blank(), axis.ticks.x = element_blank())

# --------------------------------------------------------------------
# Part 2 — From three people to all 80
# --------------------------------------------------------------------

glu <- glu |>
  mutate(predicted = 110 + 0.3 * age,
         residual  = glucose - predicted)

head(glu)

ggplot(glu, aes(x = age, y = glucose)) +
  geom_segment(aes(xend = age, yend = predicted),
               colour = "red", linetype = "dashed", alpha = 0.5) +
  geom_abline(intercept = 110, slope = 0.3, colour = "darkorange", linewidth = 1) +
  geom_point(alpha = 0.7) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

sum(glu$residual)

glu <- glu |>
  mutate(absolute = abs(residual),
         squared  = residual^2)

head(glu)

glu |>
  summarise(SSR  = sum(squared),
            MSE  = mean(squared),
            RMSE = sqrt(mean(squared)),
            MAE  = mean(absolute))

# Replace every ______ below, then run this cell.
glu |>
  mutate(predicted_hand = ______,
         residual_hand  = glucose - predicted_hand) |>
  summarise(SSR  = sum(residual_hand^2),
            MSE  = mean(residual_hand^2),
            RMSE = sqrt(mean(residual_hand^2)),
            MAE  = mean(abs(residual_hand)))

# --------------------------------------------------------------------
# Part 3 — What outliers do to each loss
# --------------------------------------------------------------------

fit_clean <- lm(glucose ~ age, data = glu)

coef(fit_clean)

# Replace every ______ below, then run this cell.
glu_outliers <- glu |>
  mutate(glucose = if_else(row_number() %in% c(1, 3, 5),
                           glucose * ______, glucose))

fit_outliers <- lm(glucose ~ age, data = ______)

coef(fit_outliers)

both <- bind_rows("Without outliers" = glu,
                  "With three outliers" = glu_outliers, .id = "data") |>
  mutate(data = fct_inorder(data))

lines <- tibble(data      = fct_inorder(c("Without outliers", "With three outliers")),
                intercept = c(coef(fit_clean)[1], coef(fit_outliers)[1]),
                slope     = c(coef(fit_clean)[2], coef(fit_outliers)[2]))

ggplot(both, aes(x = age, y = glucose)) +
  geom_point(aes(colour = glucose > 250), alpha = 0.7) +   # the outliers in red
  geom_abline(data = lines, aes(intercept = intercept, slope = slope),
              colour = "black", linetype = "dashed", linewidth = 1) +
  scale_colour_manual(values = c("blue", "red"), guide = "none") +
  facet_wrap(~ data) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

b_clean    <- coef(fit_clean)
b_outliers <- coef(fit_outliers)

glu_outliers |>
  mutate(r_clean    = glucose - (b_clean[1]    + b_clean[2]    * age),
         r_outliers = glucose - (b_outliers[1] + b_outliers[2] * age)) |>
  summarise(MSE_clean = mean(r_clean^2),
            MSE_outliers = mean(r_outliers^2),
            MAE_clean = mean(abs(r_clean)),
            MAE_outliers = mean(abs(r_outliers)))
