# Exercise 3.5 — Ordinary least squares, in closed form
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3-04-ols.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-04-ols.qmd. Edit the chapter, not this file.

# Replace every ______ below, then run this cell.
library(tidyverse)

glu <- read_csv("data/glucose_study.csv")
x    <- glu$age
y    <- glu$glucose

b1hat <- ______ / ______
b0hat <- mean(y) - b1hat * ______

fit <- lm(glucose ~ age, data = glu)
rbind(closed_form = c(b0hat, b1hat), lm = coef(fit))

# Replace every ______ below, then run this cell.
r_fitted <- ______                     # residuals of the fitted line
r_guess  <- y - (120 + 0.5 * x)        # residuals of the hand-drawn line

rbind(fitted = c(sum_r = sum(r_fitted), sum_xr = sum(x * r_fitted)),
      guess  = c(sum_r = sum(r_guess),  sum_xr = sum(x * r_guess)))

bands <- list(c(21, 25), c(21, 30), c(21, 40), c(21, 81))

do.call(rbind, lapply(bands, function(b) {
  s <- glu |> filter(age >= b[1], age <= b[2])
  data.frame(band = paste(b[1], "to", b[2]), n = nrow(s),
             var_age = var(s$age),
             slope = cov(s$age, s$glucose) / var(s$age))
}))

# Replace every ______ below, then run this cell.
bwt <- read_csv("data/birthweight.csv")

slope_bw     <- ______
intercept_bw <- ______

fit_bw <- lm(bw ~ bpd, data = bwt)
rbind(closed_form = c(intercept_bw, slope_bw), lm = coef(fit_bw))
