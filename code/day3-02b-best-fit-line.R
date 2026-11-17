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
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "plotly"))

library(tidyverse)
library(tidymodels)

theme_set(theme_bw())  # white background for every plot

glu <- read_csv("data/glucose_study.csv")

glu3 <- glu[1:3, ]
glu3

age     <- glu3$age        # x, the feature
glucose <- glu3$glucose    # y, the outcome label
m       <- length(age)     # the number of samples

# --------------------------------------------------------------------
# Pause for understanding!
# --------------------------------------------------------------------

mse_practical <- function(beta0, beta1, x, y, m) {
  (1 / m) * sum((y - (beta0 + beta1 * x))^2)
}

mse_practical(3, 5, age, glucose, m)

mse_practical(beta0 = 3, beta1 = 5, x = age, y = glucose, m = m)

((194 - 143)^2 + (129 - 223)^2 + (132 - 133)^2) / 3

# Replace every ______ below, then run this cell.
mse_practical(beta0 = ______, beta1 = ______, x = age, y = glucose, m = m)

ggplot(glu3, aes(x = age, y = glucose)) +
  geom_point(size = 3) +
  geom_abline(aes(intercept = 3, slope = 5, colour = "B0 = 3, B1 = 5"), linewidth = 1) +
  geom_abline(aes(intercept = 4, slope = 7, colour = "B0 = 4, B1 = 7"), linewidth = 1) +
  scale_colour_manual(values = c("blue", "red")) +
  xlim(0, 60) +
  ylim(0, 350) +
  labs(title = "Different betas", x = "Age", y = "Glucose", colour = NULL)

# --------------------------------------------------------------------
# Trying many lines
# --------------------------------------------------------------------

age     <- glu$age
glucose <- glu$glucose
m       <- length(age)

line_data <- expand_grid(B0 = c(100, 110, 120), B1 = c(0, 0.25, 0.5, 0.75))

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point(size = 2) +
  geom_abline(data = line_data,
              aes(intercept = B0, slope = B1,
                  colour = factor(B0), linetype = factor(B1)), linewidth = 0.8) +
  labs(title = "Effect of different B0 and B1 values on the regression line",
       x = "Age (feature)", y = "Glucose (label)",
       colour = "B0 (intercept)", linetype = "B1 (slope)")

# --------------------------------------------------------------------
# The loss function in 3D
# --------------------------------------------------------------------

B0_values <- seq(60, 160, by = 1)
B1_values <- seq(-1, 2, by = 0.02)

df <- expand_grid(B0 = B0_values, B1 = B1_values) |>
  rowwise() |>
  mutate(MSE = mse_practical(beta0 = B0, beta1 = B1, x = age, y = glucose, m = m)) |>
  ungroup()

head(df)

# persp() wants the MSE as a matrix: one row per B0, one column per B1
MSE_matrix <- matrix(df$MSE, nrow = length(B0_values), ncol = length(B1_values),
                     byrow = TRUE)
best <- df[which.min(df$MSE), ]    # the lowest point, to mark it in red

# colour each small tile of the surface by its height (dark = low MSE)
n0 <- nrow(MSE_matrix)
n1 <- ncol(MSE_matrix)
tile_height <- (MSE_matrix[-1, -1] + MSE_matrix[-1, -n1] +
                MSE_matrix[-n0, -1] + MSE_matrix[-n0, -n1]) / 4
tile_colour <- viridisLite::magma(100)[cut(log10(tile_height), 100, labels = FALSE)]

par(mar = c(3, 3, 1, 2))                # narrow margins around the plot
view <- persp(B0_values, B1_values, MSE_matrix,
              theta = 35, phi = 22,     # the angle we look from: try other numbers
              col = tile_colour, border = NA, shade = 0.25,
              ticktype = "detailed", expand = 0.75, cex.axis = 0.6,
              xlab = "\nB0 (intercept)", ylab = "\nB1 (slope)", zlab = "\nMSE")
points(trans3d(best$B0, best$B1, best$MSE, view), col = "red", pch = 19, cex = 1.6)

# This plot needs the plotly package: install.packages("plotly")
fig_3d <- plotly::plot_ly() |>
  plotly::add_surface(x = B0_values, y = B1_values, z = t(MSE_matrix),
                      colorbar = list(title = "MSE")) |>
  plotly::add_markers(x = best$B0, y = best$B1, z = best$MSE,
                      marker = list(size = 7, color = "red"),
                      name = "Minimum MSE") |>
  plotly::layout(scene = list(xaxis = list(title = "B0 (intercept)"),
                              yaxis = list(title = "B1 (slope)"),
                              zaxis = list(title = "MSE"),
                              camera = list(eye = list(x = 1.5, y = -1.7, z = 0.9))))

fig_3d

min(df$MSE)

# Find the minimum point
filter(df, MSE == min(MSE))

ggplot(df, aes(x = B0, y = B1)) +
  geom_raster(aes(fill = log10(MSE))) +
  geom_contour(aes(z = log10(MSE)), colour = "white", alpha = 0.4, bins = 12) +
  geom_point(data = best, colour = "red", size = 3) +
  scale_fill_viridis_c(option = "magma") +
  labs(x = "B0 (intercept)", y = "B1 (slope)", fill = "log10(MSE)")

lm_model <- linear_reg() |>
  set_engine("lm") |>        # the lm implementation of linear regression
  set_mode("regression")

fit1 <- lm_model |>
  fit(glucose ~ age, data = glu)

fit1
