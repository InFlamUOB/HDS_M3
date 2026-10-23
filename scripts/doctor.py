#!/usr/bin/env python3
"""Check that this machine can do everything the booklet asks of it.

    python3 scripts/doctor.py          # or: make doctor

Reports three tiers, because they are needed for different things:

  REQUIRED   build and preview the site            (Quarto, git, the extension,
                                                    the data files)
  OPTIONAL   regenerate the datasets               (R + four packages)
  OPTIONAL   work the exercises on this machine    (Python + five packages)
             rather than in the browser

Every line starts [ok] or [fix], and a [fix] names the command that resolves it.
Nothing is installed or changed by running this.
"""

import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
R_PKGS = ["tidymodels", "tidyverse", "data.table", "rpart"]
PY_MODS = ["pandas", "numpy", "matplotlib", "seaborn", "sklearn", "joblib"]
PY_INSTALL = "pandas numpy matplotlib seaborn scikit-learn joblib"

fixes: list[tuple[str, str]] = []


def check(label, ok, hint="", detail=""):
    print(("[ok]  " if ok else "[fix] ") + label + (f"  ({detail})" if detail else ""))
    if not ok and hint:
        print("       " + hint)
        fixes.append((label, hint))
    return ok


def run(cmd, timeout=180):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def section(title):
    print(f"\n{title}\n" + "-" * len(title))


def main() -> int:
    print("Checking what this machine can do with the booklet.\n"
          f"Project: {ROOT}")

    # ---- required: build and preview -----------------------------------
    section("Required — to build and preview the site")

    quarto = shutil.which("quarto")
    if check("Quarto is installed", bool(quarto),
             "install it from https://quarto.org/docs/get-started/",
             detail=quarto or "not on PATH"):
        _, out = run(["quarto", "--version"])
        ver = re.match(r"(\d+)\.(\d+)", out.strip())
        major, minor = (int(ver.group(1)), int(ver.group(2))) if ver else (0, 0)
        check("Quarto is 1.4 or newer", (major, minor) >= (1, 4),
              "upgrade from https://quarto.org/docs/get-started/ — the live code "
              "cells need 1.4+",
              detail=out.strip().splitlines()[0] if out else "unreadable")

    check("git is installed", bool(shutil.which("git")),
          "install git, or use GitHub Desktop",
          detail=shutil.which("git") or "not on PATH")

    check("the Quarto Live extension is present",
          (ROOT / "_extensions" / "live" / "live.lua").exists(),
          "quarto add r-wasm/quarto-live   (it is normally committed, so a "
          "missing copy means an incomplete clone)")

    csvs = sorted((ROOT / "data").glob("*.csv")) if (ROOT / "data").is_dir() else []
    check("the datasets are present", len(csvs) >= 5,
          "Rscript scripts/make_data.R   (needs R; the files are normally committed)",
          detail=f"{len(csvs)} csv files in data/")

    # ---- optional: R ----------------------------------------------------
    section("Optional — R, to regenerate the datasets")

    rscript = shutil.which("Rscript")
    if check("R is installed", bool(rscript),
             "install R from https://cran.r-project.org — only needed if you "
             "change the datasets or work the exercises locally",
             detail=rscript or "not on PATH"):
        code, out = run(["Rscript", "--vanilla", "-e", (
            "cat(paste(vapply(c(%s), function(p) "
            "paste0(p, '=', requireNamespace(p, quietly=TRUE)), character(1)), "
            "collapse=' '))" % ", ".join(f"'{p}'" for p in R_PKGS))])
        found = dict(re.findall(r"(\w[\w.]*)=(TRUE|FALSE)", out)) if code == 0 else {}
        missing = [p for p in R_PKGS if found.get(p) != "TRUE"]
        check("the R packages are installed", not missing,
              'Rscript -e \'install.packages(c("%s"))\'' % '", "'.join(missing),
              detail="missing: " + ", ".join(missing) if missing else "all four")

    # ---- optional: Python ------------------------------------------------
    section("Optional — Python, to work the exercises off-browser")

    py = shutil.which("python3") or shutil.which("python")
    if check("Python is installed", bool(py),
             "install Miniforge from https://conda-forge.org/download/",
             detail=py or "not on PATH"):
        # `import importlib` alone does not bring in importlib.util
        code, out = run([py, "-c",
                         "import importlib.util as u;print(' '.join(m+'='+"
                         "str(u.find_spec(m) is not None) for m in %r))" % PY_MODS])
        found = dict(re.findall(r"(\w+)=(True|False)", out)) if code == 0 else {}
        missing = [m for m in PY_MODS if found.get(m) != "True"]
        check("the Python packages are installed", not missing,
              f"conda create -n hds-python python=3.11 {PY_INSTALL}   "
              "(then activate it before running python)",
              detail="missing: " + ", ".join(missing) if missing else "all six")

    # ---- verdict ----------------------------------------------------------
    section("Verdict")
    if not fixes:
        print("Everything checked out. `make preview` will serve the booklet at\n"
              "http://localhost:4200, and you can run the exercises locally too.")
        return 0
    print(f"{len(fixes)} thing(s) to fix, in order:\n")
    for i, (label, hint) in enumerate(fixes, 1):
        print(f"  {i}. {label}\n     {hint}")
    print("\nOnly failures under 'Required' stop you editing and previewing the\n"
          "booklet; the optional ones matter when you change data or work the\n"
          "exercises outside the browser.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
