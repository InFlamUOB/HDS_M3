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
  "  Simulated here, seed 20262. 180 rows, one per patient, as a deliberately",
  "  messy GP extract. There is no bmi column on purpose: height and weight are",
  "  given and BMI is derived by students in Exercise 2.3, which is what makes",
  "  the three heights typed in metres matter - they propagate into a BMI in the",
  "  hundreds of thousands against a plausible range of about 16 to 44.",
  "",
  "  Deliberate defects: patient_id is unique per row, so one-hot encoding it",
  "  gives one column per patient; GP_practice has four common practices, three",
  "  rare ones and an Other that already exists, so grouping rare levels merges",
  "  into an existing category and cuts the encoded columns from 16 to 13; sex",
  "  appears as Male/male/M/Female/female/F and smoking_status in four",
  "  spellings; age contains one impossible 250 and weight_kg one impossible",
  "  800.",
  "",
  "  Missing values use five conventions across four columns - the strings",
  "  unknown, ?, not recorded and N/A, the number -999, and genuinely empty",
  "  cells. A naive is.na() count finds 9 of the 44. -999 is the dangerous one:",
  "  it parses as a number, so systolic_BP loads as numeric and its mean reads",
  "  73.6 mmHg instead of 131.7 with no error and no warning, whereas the text",
  "  codes at least force height_cm and weight_kg to character.",
  "",
  "  diabetes was drawn from the complete values before anything was spoiled,",
  "  and systolic_BP is a straight line in age and BMI, so Exercise 2.6 has a",
  "  genuinely predictable regression target."
), "data/PROVENANCE.txt")

# ---------------------------------------------------------------------------
# Day 2, Exercises 2.3-2.6: one messy GP patient extract.
#
# Everything from cleaning to the finished pipeline runs on this single file,
# so each exercise inherits the previous one's output. 180 rows - small enough
# that a student can print it and find problems by eye, large enough that a
# histogram and an 80/20 split still mean something.
#
# Its own seed, so the draws above are untouched.
#
# NOTE: there is deliberately no bmi column. Height and weight are here and BMI
# is derived by students in Exercise 2.3, which is what makes the height
# recorded in metres matter: it propagates into a BMI in the thousands.
#
# Deliberate defects, one per teaching point:
#   patient_id      a unique value per row, so one-hot encoding it produces one
#                   column per patient - the "should we encode everything?" case
#   GP_practice     four common practices, THREE rare ones, and an "Other" that
#                   already exists, so grouping rare levels has to merge into an
#                   existing category and genuinely reduces the column count
#   sex             Male / male / M / Female / female / F
#   smoking_status  inconsistent labels, plus two missing-value codes
#   age             one impossible 250
#   height_cm       mostly centimetres, three entered in metres
#   weight_kg       one impossible 800
#   systolic_BP     missing recorded as -999 and as an empty cell
#   missing codes   five conventions across four columns: "unknown", "?",
#                   "not recorded", "N/A", -999, and genuinely empty cells.
#                   -999 is the dangerous one: it PARSES AS A NUMBER, so the
#                   column stays numeric and the mean is silently wrong, where
#                   the text codes at least force the column to character and
#                   make the failure loud.
#
# diabetes is generated from the COMPLETE values, before anything is spoiled,
# and systolic_BP is a straight line in age and BMI so that Exercise 2.6 has a
# genuinely predictable regression target.
# ---------------------------------------------------------------------------

set.seed(20262)
n_clinic <- 180

height_true <- round(rnorm(n_clinic, 168, 9.5))
weight_true <- round(exp(rnorm(n_clinic, log(76), 0.19)), 1)
bmi_true    <- weight_true / (height_true / 100)^2
age_true    <- round(pmin(pmax(rnorm(n_clinic, 58, 14), 19), 92))
sbp_true    <- round(88 + 0.46 * age_true + 0.62 * bmi_true +
                       rnorm(n_clinic, 0, 9))

lp <- -7.6 + 0.045 * age_true + 0.075 * bmi_true + 0.012 * sbp_true
diabetes <- rbinom(n_clinic, 1, plogis(lp))

# Four common practices, three rare, and an Other that is already in the data.
practice <- sample(
  c("Alderley Road", "Bournbrook", "Cherry Tree", "Dovecote Lane",
    "Edgbaston Row", "Fiveways", "Granton Street", "Other"),
  n_clinic, replace = TRUE,
  prob = c(0.24, 0.21, 0.18, 0.15, 0.035, 0.03, 0.025, 0.08))

sex <- sample(c("Male", "male", "M", "Female", "female", "F"),
              n_clinic, replace = TRUE,
              prob = c(0.26, 0.11, 0.08, 0.29, 0.14, 0.12))

smoking <- sample(c("Never", "never", "Ex-smoker", "ex smoker", "Current",
                    "current smoker"),
                  n_clinic, replace = TRUE,
                  prob = c(0.3, 0.12, 0.2, 0.08, 0.2, 0.1))

clinic <- data.frame(
  patient_id     = sprintf("P%03d", seq_len(n_clinic)),
  GP_practice    = practice,
  sex            = sex,
  age            = as.character(age_true),
  height_cm      = as.character(height_true),
  weight_kg      = as.character(weight_true),
  systolic_BP    = as.character(sbp_true),
  smoking_status = smoking,
  diabetes       = diabetes,
  stringsAsFactors = FALSE
)

# --- now spoil the recording, after diabetes exists ------------------------

# Data-entry errors, each one correctable by a reader who thinks about it.
clinic$age[13]       <- "250"                       # impossible
clinic$weight_kg[47] <- "800"                       # impossible
metres <- c(22, 96, 141)                            # height typed in metres
clinic$height_cm[metres] <- sprintf(
  "%.2f", as.numeric(clinic$height_cm[metres]) / 100)

# Missing values, five conventions across four columns.
pool <- setdiff(seq_len(n_clinic), c(13, 47, metres))
pick <- function(k) { out <- sample(pool, k); pool <<- setdiff(pool, out); out }

clinic$height_cm[pick(8)]      <- "unknown"
clinic$height_cm[pick(4)]      <- NA            # written out as an empty cell
clinic$weight_kg[pick(7)]      <- "?"
clinic$systolic_BP[pick(9)]    <- "-999"        # parses as a number
clinic$systolic_BP[pick(5)]    <- NA
clinic$smoking_status[pick(6)] <- "not recorded"
clinic$smoking_status[pick(5)] <- "N/A"

readr::write_csv(clinic, "data/clinic_extract.csv", na = "")
message("wrote clinic_extract.csv: ", nrow(clinic), " rows")
