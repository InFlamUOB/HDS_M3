# Exercise 3.1 — Supervised learning
# HDS MSc · Module 3 · exercise booklet
# https://inflamuob.github.io/HDS_M3/day3/day3-01-supervised-learning.html
#
# The R code from the chapter, in page order, for you to copy and run.
# Run it from the folder that holds your `data` folder.
#
# Generated from day3-01-supervised-learning.qmd. Edit the chapter, not this file.


# --------------------------------------------------------------------
# Packages and data
# --------------------------------------------------------------------

# Packages for this exercise. If one is missing, remove the # and run this line once:
# install.packages(c("tidyverse", "tidymodels", "rpart.plot"))

library(tidyverse)     # data wrangling and plotting (ggplot2 is part of it)
library(tidymodels)    # modelling

theme_set(theme_bw())  # white background for every plot

glu <- read_csv("data/glucose_study.csv")

head(glu)

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point() +
  labs(x = "Age (feature)", y = "Glucose (label)")

# --------------------------------------------------------------------
# A supervised learning algorithm: linear regression
# --------------------------------------------------------------------

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point() +
  labs(x = "Age (feature)", y = "Glucose (label)") +
  geom_smooth(method = "lm", se = FALSE)

lm_model <- linear_reg() |>
  set_engine("lm") |>        # the lm implementation of linear regression
  set_mode("regression")

ls_fit <- lm_model |>
  fit(glucose ~ age, data = glu)

b <- ls_fit$fit$coefficients   # intercept first, then the slope
b

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point() +
  labs(x = "Age (feature)", y = "Glucose (label)") +
  geom_abline(intercept = b[1], slope = b[2],
              colour = "red", linetype = "dashed", linewidth = 1.5)

age_newsample <- 45
predicted_glucose <- 110.30 + 0.289 * age_newsample
print(predicted_glucose)

# predict() wants a data frame, because it normally receives more than one
# sample and more than one feature. Here it has one row and one column.
predict(ls_fit, new_data = data.frame(age = 45))

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point() +
  annotate("point", x = age_newsample, y = predicted_glucose,
           colour = "grey50", size = 5) +
  labs(x = "Age (feature)", y = "Glucose (label)") +
  geom_abline(intercept = b[1], slope = b[2],
              colour = "red", linetype = "dashed", linewidth = 1.5)

age_newsample <- 10
predicted_glucose <- 110.30 + 0.289 * age_newsample
print(predicted_glucose)

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point() +
  annotate("point", x = age_newsample, y = predicted_glucose,
           colour = "grey50", size = 5) +
  labs(x = "Age (feature)", y = "Glucose (label)") +
  geom_abline(intercept = b[1], slope = b[2],
              colour = "red", linetype = "dashed", linewidth = 1.5) +
  xlim(0, 100)

# --------------------------------------------------------------------
# Exercise: understand the role of the dataset in predictive modelling
# --------------------------------------------------------------------

dt_model <- decision_tree() |>
  set_engine("rpart") |>     # check out what the rpart package is about
  set_mode("regression")

dt_fit <- dt_model |>
  fit(glucose ~ age, data = glu)

# View(dt_fit)
dt_fit$fit

library(rpart.plot)

rpart.plot(dt_fit$fit, type = 3, fallen.leaves = TRUE,
           box.palette = "Blues", shadow.col = "gray", roundint = FALSE)

glu$predicted_glucose <- predict(dt_fit, new_data = glu)$.pred

head(glu)

# --------------------------------------------------------------------
# Stop here
# --------------------------------------------------------------------

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point(size = 3, colour = "blue", alpha = 0.7) +
  geom_step(aes(y = predicted_glucose), colour = "darkred", linewidth = 1.5) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

ggplot(glu, aes(x = age, y = glucose)) +
  geom_point(size = 3, colour = "blue", alpha = 0.7) +
  geom_step(aes(y = predicted_glucose), colour = "darkred", linewidth = 1.5) +
  geom_point(aes(y = predicted_glucose), size = 2, colour = "grey", alpha = 0.8) +
  labs(x = "Age (years)", y = "Glucose (mg/dL)")

# --------------------------------------------------------------------
# Discuss
# --------------------------------------------------------------------

glu30 <- glu[1:30, ]
dim(glu30)
