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

# ---------------------------------------------------------------------------
# Days 2-6: the diabetes case study.
#
# The exercises were written against PimaIndiansDiabetes, which mlbench removed
# in version 2.1-10 after UCI withdrew it: the data had apparently been included
# in those repositories without informed consent. mlbench now ships
# SynthDiabetes in its place - 768 rows, the same nine columns, created by
# Matthias Templ to mimic Smith et al. (1988), with every value synthetic and no
# row corresponding to a real person. That is what the booklet uses.
#
# The zeros in glucose, pressure, triceps, insulin and mass are kept: they are
# physiologically impossible and stand for missing values. Finding them is the
# first thing Day 2 asks students to do.
# ---------------------------------------------------------------------------
if (requireNamespace("mlbench", quietly = TRUE)) {
  data("SynthDiabetes", package = "mlbench", envir = environment())
  diabetes <- get("SynthDiabetes", envir = environment())
  readr::write_csv(diabetes, "data/diabetes.csv")
  message("wrote diabetes.csv: ", nrow(diabetes), " rows")
} else {
  message("mlbench not installed; data/diabetes.csv left as committed")
}

# Two files are not generated here and are committed as supplied:
#   data/longisland_heart.csv  - teaching extract used in the Day 2 missing-data
#                                exercise; 13 predictors with 20 missing each.
#   data/bupa.csv              - liver function tests, used in the Day 2
#                                transformation exercise.
# Both come from the module's existing material. See data/PROVENANCE.txt.
writeLines(c(
  paste("generated:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  paste("R version:", getRversion()),
  "seed: 2025",
  "script: scripts/make_data.R",
  "",
  "simulated here: los_data.csv, los_data_skewed.csv, extract_A/B/C.csv, birthweight.csv",
  paste("exported from mlbench SynthDiabetes:", "diabetes.csv",
        if (requireNamespace("mlbench", quietly = TRUE))
          paste0("(mlbench ", utils::packageVersion("mlbench"), ")") else ""),
  "committed as supplied: longisland_heart.csv, bupa.csv",
  "",
  "gapminder.csv",
  "  The gapminder dataset, written out from the R package of the same name",
  "  (Jennifer Bryan, CRAN). 1704 rows: country, continent, year, lifeExp, pop,",
  "  gdpPercap. Shipped as a CSV so the Python side of Exercise 2.1 does not need",
  "  an extra package; the R side loads the package, as written.",
  "",
  "clinic_extract.csv",
  "  Simulated here, seed 20262. 150 rows, one row per patient. Carries the",
  "  defects Exercises 2.3-2.6 are built on: three spellings of one referral",
  "  source (GP / gp / General Practitioner), six hospital sites of which one is",
  "  rare, a near-constant consent flag, a right-skewed bmi containing one",
  "  implausible 61.2, a bp_systolic on a different numeric scale, and missing",
  "  values recorded three different ways - the string \'unknown\' in age, the",
  "  string \'?\' in bmi, and empty cells in bp_systolic. The outcome was drawn",
  "  from the complete values before anything was blanked out, so the",
  "  missingness is a recording failure and nothing more."
), "data/PROVENANCE.txt")

# ---------------------------------------------------------------------------
# Day 2, Exercises 2.3-2.6: one small, deliberately messy clinic extract.
#
# Everything from cleaning to the finished pipeline runs on this single file,
# so each exercise inherits the previous one's output. It is small on purpose -
# 150 rows, so a student can print the whole table and find the problems by
# eye before writing any code to find them - but large enough that a histogram
# and an 80/20 split still mean something.
#
# Its own seed, so the draws above are untouched and regenerating this block
# cannot change any earlier file.
#
# Deliberate defects, one per teaching point:
#   referral_source   GP / gp / General Practitioner - the same source, three
#                     spellings, so a naive count reports three categories
#   hospital_site     six sites, one of them rare - the "group into Other"
#                     case, and the one most likely to be absent from a
#                     training split
#   consented         near-constant: one value for all but two rows, so its
#                     variance is almost zero and it carries almost nothing
#   bmi               right-skewed, plus one implausible 61.2 that survives
#                     every scaler differently
#   bp_systolic       on a quite different numeric scale from bmi, which is
#                     what makes scaling visible at all
#   missing values    written three different ways in three columns - the
#                     string "unknown", the string "?", and an empty cell -
#                     so read_csv types all three columns as text and a
#                     student who does not look gets a mean of NA
#
# The outcome is generated from the COMPLETE values, before any value is
# blanked out. Missingness here is a recording failure, not a cause of the
# outcome, which is the honest setup for imputation: the information really is
# recoverable in principle.
# ---------------------------------------------------------------------------

set.seed(20262)
n_clinic <- 150

clinic <- data.frame(
  patient_id  = sprintf("P%03d", seq_len(n_clinic)),
  age         = round(pmin(pmax(rnorm(n_clinic, 58, 14), 19), 92)),
  bmi         = round(exp(rnorm(n_clinic, log(27), 0.22)), 1)
)
clinic$bmi[7] <- 61.2   # a transcription slip: 61.2 instead of 26.1

# Systolic pressure rises with age and with BMI, both as straight lines. It is
# the regression target of Exercise 2.6, so it has to be genuinely predictable:
# a leak can only be measured against a model that was learning something in
# the first place. The relationship is linear by construction, which is why the
# squared-term task in Exercise 2.5 correctly finds nothing.
clinic$bp_systolic <- round(
  88 + 0.46 * clinic$age + 0.62 * clinic$bmi + rnorm(n_clinic, 0, 9))

clinic$referral_source <- sample(
  c("GP", "gp", "General Practitioner", "A&E", "Self-referral"),
  n_clinic, replace = TRUE, prob = c(0.34, 0.12, 0.10, 0.30, 0.14))

clinic$hospital_site <- sample(
  c("Queen Elizabeth", "Heartlands", "Good Hope", "Solihull", "City", "Sutton"),
  n_clinic, replace = TRUE, prob = c(0.26, 0.22, 0.20, 0.15, 0.15, 0.02))

clinic$consented <- ifelse(seq_len(n_clinic) %in% c(44, 119), "N", "Y")

lp <- -6.2 + 0.045 * clinic$age + 0.070 * clinic$bmi + 0.012 * clinic$bp_systolic
clinic$outcome <- rbinom(n_clinic, 1, plogis(lp))

# Now spoil the recording, after the outcome exists.
clinic$age         <- as.character(clinic$age)
clinic$bmi         <- as.character(clinic$bmi)
clinic$bp_systolic <- as.character(clinic$bp_systolic)
clinic$age[sample(n_clinic, 11)]         <- "unknown"
clinic$bmi[sample(n_clinic, 9)]          <- "?"
clinic$bp_systolic[sample(n_clinic, 13)] <- NA    # written out as an empty cell

clinic <- clinic[, c("patient_id", "age", "bmi", "bp_systolic",
                     "referral_source", "hospital_site", "consented", "outcome")]
readr::write_csv(clinic, "data/clinic_extract.csv", na = "")
message("wrote clinic_extract.csv: ", nrow(clinic), " rows")
