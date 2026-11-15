# Exercise 3.4 — Gradient descent
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-03-gradient-descent.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Lines with ______ are blanks to fill in, so this file is a worksheet:
# it will not run end to end until you have filled them.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-03-gradient-descent.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Minimising $f(x) = x^2$
# --------------------------------------------------------------------

library(tidyverse)
library(patchwork)

f       <- function(x) x^2
f_prime <- function(x) 2 * x

curve_df <- data.frame(x = seq(-10, 10, length.out = 200)) |>
  mutate(f_x = f(x), f_prime_x = f_prime(x))

p1 <- ggplot(curve_df, aes(x, f_x)) + geom_line(colour = "steelblue") +
  geom_hline(yintercept = 0) + geom_vline(xintercept = 0) +
  labs(title = expression(f(x) == x^2), y = "f(x)")
p2 <- ggplot(curve_df, aes(x, f_prime_x)) + geom_line(colour = "firebrick") +
  geom_hline(yintercept = 0) + geom_vline(xintercept = 0) +
  labs(title = expression(paste(f, "'", (x) == 2 * x)), y = "f'(x)")
p1 + p2

alpha <- 0.8
x     <- -10
path  <- numeric(10)

for (i in 1:10) {
  x       <- x - alpha * f_prime(x)
  path[i] <- x
  cat("step", i, ": x =", signif(x, 4), " f(x) =", signif(f(x), 4), "\n")
}

steps_df <- data.frame(step = 1:10, x = path) |> mutate(f_x = f(x))

ggplot(curve_df, aes(x, f_x)) +
  geom_line(colour = "grey60") +
  geom_point(data = steps_df, aes(x = x, y = f_x, fill = step),
             shape = 21, size = 3, colour = "black") +
  scale_fill_gradient(low = "yellow", high = "red") +
  labs(x = "x", y = "f(x)", fill = "step")

# --------------------------------------------------------------------
# Task 1 — Your turn, on a function whose minimum you can check
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
g       <- function(x) x^2 + 3 * x + 5
g_prime <- function(x) ______

alpha <- 0.1
x     <- 2
for (i in 1:40) {
  x <- x - ______ * g_prime(x)
}
x   # your algebra said -1.5

# --------------------------------------------------------------------
# The learning rate is the whole game
# --------------------------------------------------------------------

descend_1d <- function(alpha, x0 = -10, n = 20) {
  x <- x0
  for (i in seq_len(n)) x <- x - alpha * f_prime(x)
  x
}

rates <- c(0.01, 0.1, 0.8, 1.0, 1.05)
data.frame(alpha = rates,
           final_x = sapply(rates, descend_1d),
           final_f = sapply(rates, function(a) f(descend_1d(a))))

# --------------------------------------------------------------------
# Task 2 — Find the edge yourself
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
rates <- seq(0.8, 1.2, by = 0.05)
finals <- sapply(rates, function(a) descend_1d(a, x0 = -10, n = ______))
data.frame(alpha = rates, final_x = signif(finals, 3))

# --------------------------------------------------------------------
# Local and global minima
# --------------------------------------------------------------------

h       <- function(x) x^4 + x^3 - 2 * x^2
h_prime <- function(x) 4 * x^3 + 3 * x^2 - 4 * x

descend_h <- function(x0, alpha = 0.03, n = 200) {
  x <- x0
  for (i in seq_len(n)) x <- x - alpha * h_prime(x)
  c(start = x0, end = x, f_end = h(x))
}

t(sapply(c(1, 0.2, 0, -0.1, -0.5, 2), descend_h))

curve_h <- data.frame(x = seq(-2, 1.5, length.out = 300)) |> mutate(f_x = h(x))
ends    <- data.frame(start = c(1, 0.2, 0, -0.1, -0.5, 2)) |>
  mutate(end = sapply(start, function(s) descend_h(s)[["end"]]), f_end = h(end))

ggplot(curve_h, aes(x, f_x)) +
  geom_line(colour = "grey40") +
  geom_point(data = ends, aes(x = end, y = f_end), colour = "red", size = 3) +
  labs(x = "x", y = "f(x)")

# --------------------------------------------------------------------
# Task 3 — Where is the watershed
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
starts <- seq(-0.1, 0.2, by = 0.01)
data.frame(start = starts,
           end = round(sapply(starts, function(s) ______), 3))

# --------------------------------------------------------------------
# Two parameters at once
# --------------------------------------------------------------------

fxy <- function(x, y) x * sin(y) + x^2
grad_x <- function(x, y) sin(y) + 2 * x
grad_y <- function(x, y) x * cos(y)

x <- 1; y <- 2; alpha <- 0.01
trace_xy <- data.frame(iter = 0, x = x, y = y, f = fxy(x, y))

for (i in 1:1000) {
  gx <- grad_x(x, y); gy <- grad_y(x, y)
  x <- x - alpha * gx
  y <- y - alpha * gy
  if (i %% 100 == 0)
    trace_xy <- rbind(trace_xy, data.frame(iter = i, x = x, y = y, f = fxy(x, y)))
}
trace_xy

# --------------------------------------------------------------------
# The result that should bother you
# --------------------------------------------------------------------

glu <- read_csv("data/glucose_study.csv")

descend_mse <- function(x, y, alpha, n) {
  b0 <- 0; b1 <- 0
  mse <- numeric(n)
  for (i in seq_len(n)) {
    r  <- y - (b0 + b1 * x)
    b0 <- b0 - alpha * (-2 * mean(r))
    b1 <- b1 - alpha * (-2 * mean(x * r))
    mse[i] <- mean((y - (b0 + b1 * x))^2)
  }
  list(b0 = b0, b1 = b1, mse = mse)
}

raw <- descend_mse(glu$age, glu$glucose, alpha = 1e-4, n = 1000)
c(intercept = raw$b0, slope = raw$b1, MSE = tail(raw$mse, 1))
coef(lm(glucose ~ age, data = glu))

# --------------------------------------------------------------------
# Task 4 — Make it converge
# --------------------------------------------------------------------

# Replace every ______ below, then run this cell.
zx <- (glu$age - mean(glu$age)) / sd(glu$age)
zy <- (glu$glucose - ______) / sd(glu$glucose)

std <- descend_mse(zx, zy, alpha = 0.1, n = 50)

slope     <- std$b1 * sd(glu$glucose) / sd(glu$age)
intercept <- mean(glu$glucose) + sd(glu$glucose) * std$b0 - slope * mean(glu$age)

c(intercept = intercept, slope = slope)
coef(lm(glucose ~ age, data = glu))   # the answer to compare with

# --------------------------------------------------------------------
# One more thing the standardised fit tells you
# --------------------------------------------------------------------

std_shown <- descend_mse((glu$age - mean(glu$age)) / sd(glu$age),
                         (glu$glucose - mean(glu$glucose)) / sd(glu$glucose),
                         alpha = 0.1, n = 50)

data.frame(iteration = 1:50, MSE = std_shown$mse) |>
  ggplot(aes(iteration, MSE)) +
  geom_line(colour = "firebrick") +
  labs(x = "Iteration", y = "MSE (standardised units)")
