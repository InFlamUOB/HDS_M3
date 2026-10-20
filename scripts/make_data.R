# ---------------------------------------------------------------------------
# make_data.R  —  generates every dataset used in this booklet
#
# Run from the project root:   Rscript scripts/make_data.R
#
# Everything the students analyse is SIMULATED. That is a feature, not a
# shortcut: because we wrote the data-generating process ourselves, we know
# the true answer to every question in the booklet, so a student can find out
# whether their diagnosis was right rather than whether it was plausible.
#
# The parameters of the "original" world below were chosen to match the
# los_data.csv distributed in earlier years of this module (OLS of LOS on Age
# and Severity recovers intercept -8.5, Age 0.94, Severity 3.37, residual SD
# 4.3, R-squared 0.95). Regenerating gives different row values but the same
# structure, and every answer in the booklet is stated as a range, so the
# older file can be substituted without invalidating anything.
#
# NOTE FOR INSTRUCTORS: this file contains the answer to Exercise 1.3 (which
# of extracts A, B and C shifted, and how). If you publish the student site
# from this same repository, either keep this script out of the published
# directory or accept that a curious student can read the answer here.
# ---------------------------------------------------------------------------

set.seed(2025)
dir.create("data", showWarnings = FALSE)

# --- helpers ---------------------------------------------------------------

draw_patients <- function(n, age_mean, age_sd, age_min, sev_mean, sev_sd) {
  # Age is truncated below (no paediatric admissions in this service) but NOT
  # above: the original dataset contains implausibly old patients, and that is
  # deliberately preserved - it is the first data-quality finding of Day 1.
  age <- pmax(rnorm(n, age_mean, age_sd), age_min)
  sev <- pmin(pmax(rnorm(n, sev_mean, sev_sd), 1), 10)   # score is 1-10 by definition
  data.frame(Age = age, Severity = sev)
}

add_los <- function(d, b0, b_age, b_sev, noise_sd) {
  d$LOS <- b0 + b_age * d$Age + b_sev * d$Severity + rnorm(nrow(d), 0, noise_sd)
  d
}

# --- the original world (training data) ------------------------------------
# Older, moderately ill medical inpatients. LOS rises steeply with age.

ORIGINAL <- list(b0 = -8.5, b_age = 0.94, b_sev = 3.37, noise_sd = 4.3)

los <- draw_patients(1000, age_mean = 60, age_sd = 15, age_min = 18,
                     sev_mean = 5.4, sev_sd = 2.07)
los <- add_los(los, ORIGINAL$b0, ORIGINAL$b_age, ORIGINAL$b_sev, ORIGINAL$noise_sd)
write.csv(los, "data/los_data.csv", row.names = FALSE)

# --- three later extracts, for Exercise 1.3 ---------------------------------
# The students are told only that these are three monthly extracts taken after
# the model went live. They must work out what happened to each.
#
#   extract_A : NO SHIFT. Same patients, same rules. The control.
#   extract_B : COVARIATE SHIFT ONLY. Younger and sicker patients, but LOS
#               still depends on Age and Severity exactly as before, so a
#               correct model stays correct (it is merely extrapolating).
#   extract_C : COVARIATE *AND* CONCEPT SHIFT. Same new case-mix as B, but the
#               relationship itself changed: age now matters far less and the
#               intercept is much lower (think a reorganised service with
#               early supported discharge).

extract_A <- draw_patients(400, 60, 15, 18, 5.4, 2.07)
extract_A <- add_los(extract_A, ORIGINAL$b0, ORIGINAL$b_age, ORIGINAL$b_sev, ORIGINAL$noise_sd)

NEW_CASEMIX <- list(age_mean = 27, age_sd = 6, age_min = 18, sev_mean = 7.4, sev_sd = 1.5)

extract_B <- draw_patients(400, NEW_CASEMIX$age_mean, NEW_CASEMIX$age_sd,
                           NEW_CASEMIX$age_min, NEW_CASEMIX$sev_mean, NEW_CASEMIX$sev_sd)
extract_B <- add_los(extract_B, ORIGINAL$b0, ORIGINAL$b_age, ORIGINAL$b_sev, ORIGINAL$noise_sd)

extract_C <- draw_patients(400, NEW_CASEMIX$age_mean, NEW_CASEMIX$age_sd,
                           NEW_CASEMIX$age_min, NEW_CASEMIX$sev_mean, NEW_CASEMIX$sev_sd)
extract_C <- add_los(extract_C, b0 = 4.0, b_age = 0.15, b_sev = 1.60, noise_sd = 4.3)

write.csv(extract_A, "data/extract_A.csv", row.names = FALSE)
write.csv(extract_B, "data/extract_B.csv", row.names = FALSE)
write.csv(extract_C, "data/extract_C.csv", row.names = FALSE)

# --- a clinically plausible variant, for later days -------------------------
# LOS in a real hospital is right-skewed with a median of a few days, not a
# symmetric cloud around two months. Day 2 (metrics) and the GLM session use
# this file to show why the choice of error metric and outcome distribution
# matters. Not used on Day 1.

plaus <- draw_patients(1000, 60, 15, 18, 5.4, 2.07)
mu <- exp(0.15 + 0.012 * plaus$Age + 0.17 * plaus$Severity)   # multiplicative
plaus$LOS <- rgamma(nrow(plaus), shape = 2, scale = mu / 2)
write.csv(plaus, "data/los_data_skewed.csv", row.names = FALSE)

cat("written:\n"); print(list.files("data", pattern = "csv$"))

# --- provenance record ------------------------------------------------------
writeLines(c(
  paste("generated:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  paste("R version:", getRversion()),
  "seed: 2025",
  "script: scripts/make_data.R"
), "data/PROVENANCE.txt")

# --- a second dataset, for the transfer task in Exercise 1.2 ----------------
# Same pipeline, different clinical question: predict birth weight from two
# ultrasound measurements. Variable names and units are plausible, the numbers
# are simulated. It exists so that students rerun the pipeline on data whose
# column names are nothing like the ones they just used, which is the only way
# to find out whether they learnt the pipeline or memorised the script.
# (Instructors: the Module 2 birth-weight dataset can be substituted directly.)

n <- 600
bw <- data.frame(
  bpd = rnorm(n, 90, 5),    # biparietal diameter, mm
  ad  = rnorm(n, 100, 8)    # abdominal diameter, mm
)
bw$bw <- -1700 + 30 * bw$bpd + 25 * bw$ad + rnorm(n, 0, 250)   # grams
write.csv(bw, "data/birthweight.csv", row.names = FALSE)
cat("also written: data/birthweight.csv\n")
