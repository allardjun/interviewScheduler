# TODO — low-hanging improvements

A prioritized list of small, self-contained improvements for this repo. Each item is
scoped so it can be handed to Claude (Opus 4.8) and completed in one focused pass.

---

## 1. Update all dependencies (do this first)

`requirements.txt` pins a stack from early 2024. It is now well behind, and — more
practically — **it will not install cleanly on the Python interpreter on this machine
(3.13.2)**. `pillow==10.2.0`, `numpy==1.26.3`, `pandas==2.2.0`, and `contourpy==1.2.0`
all predate Python 3.13 wheels, so `pip install -r requirements.txt` tries to build them
from source and is likely to fail.

### The pillow situation (checked)

- **How it's used here:** pillow is *not* imported anywhere in the code. It is pulled in
  only as a transitive dependency of `matplotlib`, which itself is used only for the
  optional annealing visualization (`visualize = 0` by default in `makeSchedule.py`).
  This tool never opens untrusted image files, so the pillow CVEs below are not reachable
  in normal use — the real problem with `pillow==10.2.0` is that **it has no wheel for
  Python 3.13** and is generally stale.
- **Security, for the record:** `10.2.0` (Jan 2024) is affected by CVE-2024-28219 (a
  buffer overflow in `_imagingcms.c`, fixed in 10.3.0) plus several later CVEs. The
  current release is **12.3.0** (July 2026), which is the latest non-vulnerable version.
- **Action:** bump pillow to `>=12.3.0` (or just unpin it and let matplotlib pull a
  current version). Since pillow isn't a direct dependency, it does not need to be pinned
  in `requirements.txt` at all — dropping the line is a reasonable option.

### ⚠️ Blocker: a numpy 2.x upgrade requires a code fix first

`makeSchedule.py:241-242` uses `np.Inf`, which **was removed in NumPy 2.0**. Bumping numpy
past 2.0 without changing this will crash the solver on startup. Fix: replace `np.Inf`
with `np.inf` (two occurrences) as part of the dependency bump. (A repo-wide grep for
`np.NaN`, `np.float`, `np.int`, `np.bool` came back clean, so `np.Inf` is the only such
case.)

### Suggested approach

1. Fix `np.Inf` → `np.inf` in `makeSchedule.py`.
2. Regenerate `requirements.txt` against current releases that support Python 3.13
   (pillow ≥12.3.0, a numpy 2.x, pandas ≥2.2.3, matplotlib current, etc.).
3. Migrate `fuzzywuzzy` → `rapidfuzz` (see item 6) so the deprecated package can be dropped.
4. Smoke-test the full pipeline on `SampleData_RealAnon/` (see item 9) to confirm the
   upgraded stack still produces output.

**Do this together with item 2 (uv migration):** rather than hand-editing
`requirements.txt`, capture the corrected/bumped versions directly in `pyproject.toml` and
let `uv lock` produce the pinned lockfile.

---

## 2. Migrate dependency management from `requirements.txt` + venv to `uv`

Replace the manual `pip install -r requirements.txt` / venv workflow with
[uv](https://docs.astral.sh/uv/), which gives fast, reproducible installs, a proper
lockfile, and automatic Python-version management (relevant here, since the pinned stack
doesn't build on the machine's Python 3.13 — see item 1).

### Steps

1. Create a `pyproject.toml` declaring the project and its **direct** runtime dependencies
   only — `numpy`, `pandas`, `matplotlib`, `openpyxl`, `xlsxwriter`, and the fuzzy-matching
   library (`rapidfuzz` after item 5; `fuzzywuzzy` before). The many transitive pins
   currently in `requirements.txt` (`contourpy`, `kiwisolver`, `fonttools`, `pillow`,
   `pytz`, `six`, …) should **not** be listed — `uv` resolves and locks them automatically.
   Use lower-bound constraints that work on Python 3.13, and set `requires-python = ">=3.13"`
   (or whatever floor is intended).
2. Run `uv lock` to generate `uv.lock`, then `uv sync` to create the environment.
3. Verify the pipeline runs under uv: `uv run python makeSchedule.py SampleData_RealAnon`
   (pairs with the smoke test in item 9).
4. Remove `requirements.txt` once `pyproject.toml` + `uv.lock` are in place, and update
   `README.md` "Installation" / "To run" sections to use `uv sync` and `uv run`. `venv/`
   is already in `.gitignore`; uv's default `.venv/` is likewise ignored by that entry only
   if the pattern matches — confirm `.venv/` is ignored and add it if not.

### Notes

- Commit both `pyproject.toml` and `uv.lock` (the lockfile is meant to be tracked).
- This is a natural companion to item 1: the dependency *bump* decides the version floors;
  the uv *migration* decides how they're declared and locked. Doing them in one pass avoids
  editing dependency versions twice.

---

## 3. Fix the `Targets` "worst-case" reporting bug

In `makeSchedule.py`, the per-target dictionaries are written with the key `["min"]`
(e.g. lines 309, 317, 323, 351), but the class defines and reads the key `["worst"]`:

- `Targets.__init__` seeds `{'worst': 0, 'mean': 0}` (lines 562-567)
- `Targets.copy()` only copies `'worst'` and `'mean'` (line 573), silently dropping the
  `'min'` values the solver actually computed
- `Targets.print()` reports `['worst']` (line 597), and the `visualize` plot reads
  `['worst']` (line 545)

Net effect: the end-of-run summary always prints **"at worst 0%"** for every fraction
target, regardless of the real minimum. Standardize on one key name (`'min'` reads most
naturally given the code) across the call sites, `__init__`, `copy()`, `print()`, and the
visualize block.

---

## 4. Replace hardcoded `FOLDERNAME` with a command-line argument

All three entry points (`translateStudentRequests.py`, `translateFacultyAvailability.py`,
`makeSchedule.py`) require hand-editing a hardcoded absolute path near the bottom of the
file before every run:

```python
FOLDERNAME = '/Volumes/Carrot/Dropbox/.../2024RealData'  # EDIT FOLDERNAME HERE
```

Add `argparse` so the data folder is passed on the command line
(`python makeSchedule.py <folder> [seed]`), defaulting to `SampleData_RealAnon` when
omitted. This removes the source-editing step and makes the sample data runnable out of
the box. Note `makeSchedule.py` already uses `sys.argv[1]` for the RNG seed, so preserve
that behavior when introducing argparse.

---

## 5. Use `os.makedirs(..., exist_ok=True)` instead of `os.system("mkdir ...")`

`makeSchedule.py:53` shells out to `mkdir` via `os.system`, which is not cross-platform
(fails on Windows), errors if the directory exists, and breaks on paths with spaces.
Replace with `os.makedirs(directoryName + subdirectoryName, exist_ok=True)`.

---

## 6. Migrate off the deprecated `fuzzywuzzy` package

`fuzzywuzzy` is unmaintained and its successor guidance points to `rapidfuzz` — which is
**already in `requirements.txt`** (pulled in transitively). Both translator scripts import
`from fuzzywuzzy import fuzz, process`. `rapidfuzz` exposes the same `fuzz` /
`process.extractOne` API, so this is close to a drop-in swap. Doing so lets `fuzzywuzzy`,
`python-Levenshtein`, and `Levenshtein` be removed from `requirements.txt`.

---

## 7. Stop tracking `.DS_Store` files and fix the `.gitignore` pattern

Three `.DS_Store` files are committed to the repo:

```
SampleData_RealAnon/.DS_Store
old/RemoteYearBot/.DS_Store
old/RemoteYearBot/SampleData_RealAnon2020/.DS_Store
```

The `.gitignore` entry is `**/.DS_Stores` (trailing "s"), which never matches the real
filename `.DS_Store`. Fix the pattern to `**/.DS_Store` (or just `.DS_Store`) and
`git rm --cached` the three tracked files.

---

## 8. Fix README inaccuracies

Small documentation corrections in `README.md`:

- The dependency list includes `sys`, which is part of the Python standard library and
  should not be listed as an install requirement.
- Step numbering under "To run" has two consecutive `3.` items.
- Output filename typos: the text says `forBot_StudentRequestMatrix.xlsx` (the code writes
  `forBot_StudentRequestsMatrix.xlsx`, with an "s") and `fromBot_StudentSChedules.xlsx`
  (stray capital "C").
- Once item 4 lands, update the "To run" section to describe the command-line argument
  instead of editing `FOLDERNAME` in the source.

---

## 9. Add a runnable smoke test / verification path

There is currently no automated way to confirm the pipeline still works after a change
(no tests, no CI). Add a minimal script or Makefile target that runs the three stages
end-to-end against `SampleData_RealAnon/` and asserts the four `fromBot_*.xlsx` output
files are produced. This makes items 1 and 6 verifiable and guards future edits. Keep
`ntmax` small for the test run so it finishes in seconds rather than minutes.

---

## 10. Remove dead / commented-out code

`makeSchedule.py` and both translator scripts carry large blocks of commented-out
debugging `print`s and abandoned earlier approaches (e.g. the `# debugging` blocks around
lines 264-268, 302-304, 370-373, 409-413, and the commented `facultyList`/`Last Name`
reconstruction around lines 118-143). Removing these improves readability without changing
behavior. Low-risk, purely mechanical — but do it as its own commit, separate from the
functional changes above, so the diff stays reviewable.

---

## Larger items (noted, but NOT low-hanging — from the README wishlist)

These need data-format decisions or domain knowledge and are better left to the maintainer
or a dedicated design pass rather than a one-shot cleanup:

- Multi-word last names (e.g. "Rodriguez Verdugo") break the `split(' ')` / reverse
  name-sorting logic in the translators. A correct fix needs a convention for
  distinguishing given vs. family names.
- Campus zones use numeric codes; the README asks for human-readable names, which requires
  changing the input data format.
