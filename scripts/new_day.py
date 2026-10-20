#!/usr/bin/env python3
"""Scaffold a new teaching day and register it in the book.

    python3 scripts/new_day.py --day 2 --title "Validation you can defend" \
        --exercises resampling,metrics

Creates day<N>-00-overview.qmd, one chapter per named exercise from
_templates/exercise.qmd, and day<N>-99-consolidation.qmd, then inserts the
part: block into _quarto.yml ahead of roadmap.qmd. Safe to re-run: existing
files are left alone and the part block is only added once.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

OVERVIEW = """---
engine: knitr
---

# Day {day} — Overview {{#sec-day{day}}}

One paragraph: what today does, and why it is today rather than any other day.
Name the loose end from an earlier day that this one picks up.

## Objectives

By the end of the day you should be able to, without looking anything up:

::: {{.objective-list}}
- ...
- ...
:::

## Shape of the day

| | Exercise | Time | Mode |
|---|---------|------|------|
{rows}
| — | Consolidation | 20 min | plenary |

: {{tbl-colwidths="[6,52,18,24]"}}

## What you need before you start

- A browser. The code cells run in the page.
- ...

::: {{.content-visible when-profile="instructor"}}
::: {{.instructor}}
**Running the day.** ...

**Where the time actually goes.** ...

**Plenary.** ...
:::
:::
"""

CONSOLIDATION = """---
engine: knitr
---

# Day {day} — Consolidation {{#sec-day{day}-consolidation}}

**20 minutes · plenary**

## Say it in one sentence

...

## Self-assessment

- [ ] ...
- [ ] ...

## Questions

1. ...
2. ...

::: {{.content-visible when-profile="instructor"}}
::: {{.instructor}}
**Answers.** ...

**Rubric.** ...
:::
:::

## What carries into Day {next_day}

The loose ends left deliberately, each of which opens the next session.

1. ...
"""


def write(path: pathlib.Path, text: str) -> bool:
    if path.exists():
        print(f"  exists, left alone: {path.name}")
        return False
    path.write_text(text)
    print(f"  created: {path.name}")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--day", type=int, required=True)
    p.add_argument("--title", default="Title of the day")
    p.add_argument("--exercises", default="first-exercise",
                   help="comma-separated slugs, one chapter each")
    args = p.parse_args()

    day = args.day
    slugs = [s.strip() for s in args.exercises.split(",") if s.strip()]

    template = (ROOT / "_templates" / "exercise.qmd").read_text()

    rows, chapters = [], [f"day{day}-00-overview.qmd"]
    for i, slug in enumerate(slugs, start=1):
        name = f"day{day}-{i:02d}-{slug}.qmd"
        title = slug.replace("-", " ").capitalize()
        body = (template
                .replace("# Exercise N.M — Title {#sec-shortname}",
                         f"# Exercise {day}.{i} — {title} {{#sec-{slug}}}")
                .replace("unique_key_r", f"{slug.replace('-', '_')}_{i}_r"))
        write(ROOT / name, body)
        chapters.append(name)
        rows.append(f"| {day}.{i} | [{title}]({name}) | 45 min | individual |")

    write(ROOT / f"day{day}-00-overview.qmd",
          OVERVIEW.format(day=day, rows="\n".join(rows)))
    write(ROOT / f"day{day}-99-consolidation.qmd",
          CONSOLIDATION.format(day=day, next_day=day + 1))
    chapters.append(f"day{day}-99-consolidation.qmd")

    # register the part in _quarto.yml, immediately before roadmap.qmd
    cfg_path = ROOT / "_quarto.yml"
    cfg = cfg_path.read_text()
    if f'day{day}-00-overview.qmd' in cfg:
        print("  _quarto.yml already lists this day")
    else:
        block = (f'    - part: "Day {day} — {args.title}"\n'
                 + "      chapters:\n"
                 + "".join(f"        - {c}\n" for c in chapters))
        new_cfg, n = re.subn(r"^(    - roadmap\.qmd\n)", block + r"\1",
                             cfg, count=1, flags=re.M)
        if n == 0:
            print("  could not find '- roadmap.qmd' in _quarto.yml; add the part "
                  "block by hand:", file=sys.stderr)
            print(block, file=sys.stderr)
            return 1
        cfg_path.write_text(new_cfg)
        print(f"  registered Day {day} in _quarto.yml")

    print(f"""
Next:
  1. write the chapters, using {{webr}} and {{pyodide}} cells
  2. append any new data to scripts/make_data.R, and register the file under
     BOTH `resources:` keys in _quarto.yml
  3. make check
  4. make worksheets DAY={day}
  5. commit and push — the site rebuilds itself""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
