# Working on this booklet

A tutorial for editing the Module 3 booklet, written for someone who has not
used git in anger. It assumes you can open a terminal and that you have Quarto
installed; everything else is explained.

Two people edit this booklet — whoever is at the keyboard, and an assistant
working through the GitHub API, whose commits are authored **sciency** so you can
tell them apart in the history. This document is how the two stay out of each
other's way.

---

## 1. The three places

The booklet exists in three places at once, and most confusion about git comes
from not knowing which one you are looking at.

**Your folder.** Where you type. Nothing here is visible to anyone else until you
deliberately send it onward, so you can break things freely.

**GitHub.** The official copy, at
<https://github.com/InFlamUOB/HDS_M3>. It is the only thing both of us can see,
which makes it the referee: what is there is the truth, and what is not there
did not happen.

**The live site**, at <https://inflamuob.github.io/HDS_M3/>. Built automatically
from GitHub. You never edit it and never upload to it. When something arrives on
GitHub, a robot renders the booklet and the site follows about a minute later.
If the site looks wrong, the problem is in GitHub, never in the site.

So the life of a change is: *type it in your folder → send it to GitHub → the
site follows*. Git is the tool for the middle arrow.

How to tell where you are:

| Question | Command |
|---|---|
| What have I changed and not yet sent? | `git status` |
| What exactly did I change? | `git diff` |
| What has been sent, by whom? | `git log --oneline` |
| Is the robot finished? | the **Actions** tab on GitHub |

---

## 2. Your first change, step by step

Do this once, with a harmless edit, so that the mechanics are familiar before
they matter.

**Step 1 — get the booklet.** Once only:

```bash
cd ~/Documents
git clone https://github.com/InFlamUOB/HDS_M3.git
cd HDS_M3
```

`clone` means "make me a folder containing this repository and remember where it
came from". You now have the whole history, not just the current files.

**Step 2 — open it.** Open the `HDS_M3` folder in Positron, or double-click
`HDS_M3.Rproj`. This matters: it sets the working directory to the project root,
which is what every file path in the booklet assumes.

**Step 3 — catch up before you type.** Always:

```bash
git pull
```

"Bring me anything that arrived on GitHub since last time." If it says *Already
up to date*, good. This is the habit that prevents nearly every problem in this
document.

**Step 4 — make an edit.** Open `roadmap.qmd` and change one word in the Day 2
row. Save.

**Step 5 — ask git what it thinks happened.**

```bash
git status
```

It will list `roadmap.qmd` as modified. Then:

```bash
git diff
```

Lines starting `-` are what you removed, `+` what you added. Reading this before
sending anything is the single most useful habit in git; it has caught more
mistakes than any amount of care.

**Step 6 — send it.** Three commands, which mean *include it*, *label it*,
*send it*:

```bash
git add -A
git commit -m "Reword the Day 2 roadmap entry"
git push
```

`add -A` stages every change you made. `commit` records them as one labelled step
in the history — the message is for the next reader, who is usually you in three
months, so say *what changed and why* rather than "update". `push` sends the
commit to GitHub.

**Step 7 — watch it go live.** Open the repository's **Actions** tab. A run
appears, takes under a minute, and turns green. Then reload the live site with
**Cmd-Shift-R**.

> Use the hard reload. A normal reload often serves the cached page, which makes
> a perfectly successful deploy look as though nothing happened.

If your word is on the live site, you have done the entire loop.

---

## 3. The loop, once you no longer need the explanation

```bash
git pull                                 # 1. catch up
# edit; Preview button or `make preview` to see it
make check                               # 2. catch what renders fine but breaks for students
git add -A && git commit -m "why"        # 3. record
git pull --rebase                        # 4. catch up again, in case I pushed meanwhile
git push                                 # 5. send; the site follows
```

Steps 1 and 4 are the whole protocol. Skipping 1 means editing a stale file;
skipping 4 means a rejected push.

What `make check` catches: a chapter missing its `engine: markdown`, two
exercises sharing a key on one page, a hint or solution whose key has no
exercise, a task with no `______` to fill in, a solution that cannot run on its
own, a data file used but not mounted into the browser, a package used but not
in the runtime list, and a link to a chapter that does not exist. All of these
render perfectly and fail only in front of a student.

---

## 4. When something goes wrong

Two things will actually happen to you. Everything else is rare.

### "Updates were rejected"

```
! [rejected]        main -> main (fetch first)
error: failed to push some refs
```

This means I pushed while you were working. Nothing is broken and nothing is
lost:

```bash
git pull --rebase
git push
```

`--rebase` replays your commits on top of mine, so the history stays a straight
line.

### A conflict

If we changed *the same lines of the same file*, git stops and asks you to
decide. It writes both versions into the file:

```
<<<<<<< HEAD
your version of the line
=======
my version of the line
>>>>>>> main
```

Open the file, delete the three marker lines, keep whatever is right — often
both, in some order — then:

```bash
git add path/to/that-file.qmd
git rebase --continue
```

If you would rather not deal with it now, `git rebase --abort` puts you back
exactly where you started and loses nothing.

Conflicts only happen in files we both touched. Tell me which chapter you are
working in and I will stay out of it; git handles separate files by itself.

---

## 5. How my changes reach you

For anything beyond a one-line fix I open a **pull request**: the change sits
next to the official copy rather than inside it. You get the diff, the automated
checks run on it, and nothing reaches students until you press Merge.

1. You get an email, or see it on the **Pull requests** tab.
2. Open it and read **Files changed** — this is the same `git diff` view as on
   your own machine.
3. The checks run automatically and must pass; a pull request cannot publish, so
   a red check costs nothing but my time.
4. Press **Merge pull request**, then **Confirm merge**.
5. On your machine, `git pull`.

Step 5 is easy to forget, and forgetting it is how you end up editing a stale
file an hour later.

---

## 6. Undoing things

| Situation | Command |
|---|---|
| Throw away edits to one file, not yet committed | `git checkout -- path/to/file.qmd` |
| Unstage something you `add`ed | `git restore --staged path/to/file.qmd` |
| Reword the last commit message, before pushing | `git commit --amend -m "better message"` |
| Undo the last commit but keep the edits | `git reset --soft HEAD~1` |
| See what a file looked like last week | `git log -p path/to/file.qmd` |

**Never run `git push --force` on `main`.** It rewrites shared history and can
delete commits — mine or yours. Nothing in this project needs it.

---

## 7. Working from the terminal

Quarto, R and the booklet's own tools, without leaving the command line.

### Seeing the booklet

```bash
make preview                 # whole book at http://localhost:4200, reloads as you save
quarto preview day1-02-first-pipeline.qmd    # one chapter, faster
make site                    # build into _book/ without serving it
```

### Running R

```bash
R                            # interactive console; q() to leave
Rscript -e 'sessionInfo()'   # one expression
Rscript scripts/make_data.R  # regenerate every dataset from seed 2025
make setup-r                 # install the four R packages the booklet uses
```

### Testing the live cells — the one that matters

The `{webr}` and `{pyodide}` cells are executed by the *reader's browser*, never
at render time. A clean `quarto render` therefore proves nothing at all about
whether that code works. This runs it for real:

```bash
make test-cells DAY=1        # both languages
python3 scripts/run_cells.py --day 1 --lang r
```

It rebuilds each chapter as a session — the worked examples in order, and for
every task cell the published solution in place of the blanks — runs it in your
local R and Python, and reports what the self-checks said:

```
day1-02-first-pipeline.qmd   R   5 cells  5 ok, 0 fix  ok
```

It fails in two ways, both of which a student would have hit. A cell that does
not run at all:

```
day1-02-first-pipeline.qmd   R   5 cells  0 ok, 0 fix  FAILED
      Error in linear_regg() : could not find function "linear_regg"
```

and a cell that runs but builds the wrong object:

```
day1-02-first-pipeline.qmd   R   5 cells  4 ok, 1 fix  checks failed
      [fix] the model beats the predict-the-mean baseline  (model 3.42 vs baseline 0.50)
```

Run it after touching any code in a chapter. It needs R and Python locally —
`make doctor` will tell you whether you have them.

### Checking the machine

```bash
make doctor                  # what is installed, what is missing, and the fix
make                         # every available command
```

---

## 8. The short version

- `git pull` before you start and before you push.
- `git diff` before you commit.
- `make check` before you push; `make test-cells DAY=n` if you touched code.
- Say which chapter you are editing, and I will stay out of that file.
- Never force-push.
