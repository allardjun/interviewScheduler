# Implementation Plan

Detailed, sequenced plan for executing the improvements in [`TODO.md`](TODO.md).
Each work item maps to one topic branch and one pull request against `master`.

- **Repo:** `github.com/allardjun/interviewScheduler` (remote `origin`, default branch `master`)
- **Toolchain:** `uv` 0.5.9 is already installed; target Python is 3.13.
- **Nature of the project:** a script-based tool run manually a couple of times a year.
  There is no CI and no test suite today, so "verification" below means *actually running
  the pipeline against `SampleData_RealAnon/` and confirming the four `fromBot_*.xlsx`
  outputs are produced*, until item PR-2 makes that repeatable.

---

## Guiding principles

1. **Foundation first.** Nothing can be verified until the environment installs and the
   pipeline runs on Python 3.13. PR-1 (uv + dependency bump) and PR-2 (smoke test) come
   first and unblock everything else.
2. **One concern per PR.** Keep functional changes, refactors, and pure cleanups in
   separate PRs so each diff is small and reviewable.
3. **Serialize edits to `makeSchedule.py`.** Five items touch this one file (PR-1, PR-3,
   PR-4, PR-6, PR-9). Do them in sequence, rebasing each branch on the freshly-merged
   `master`, to avoid painful conflicts.
4. **Never break the runnable state.** After each PR merges, the sample pipeline must still
   produce output. The smoke test (PR-2) enforces this for every PR that follows it.

---

## Branch & PR conventions

- Branch off the latest `master`: `git switch master && git pull && git switch -c <branch>`.
- One logical change per commit; imperative commit subjects.
- Every commit message ends with the trailers this environment requires:

  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01E9S3kTMDWjzZWHV2Y4ToeK
  ```

- Open a PR to `master` with `gh pr create`; PR bodies end with:

  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  ```

- Merge strategy: **never squash.** Preserve every commit — merge each PR with a merge
  commit (`gh pr merge --merge`, not `--squash`) so the individual commits stay in history.
  Then delete the branch and rebase the next branch on updated `master` before continuing.

---

## Execution order (dependency graph)

```
PR-7 (gitignore/.DS_Store)      ── independent, can land any time (do it first, it's trivial)
        │
PR-1 (uv + deps + np.inf fix)   ── FOUNDATION, unblocks all runnable work
        │
PR-2 (smoke test)               ── regression guard for everything below
        ├── PR-3 (Targets reporting bug)
        ├── PR-4 (CLI folder argument)
        ├── PR-5 (rapidfuzz migration)     ── also drops fuzzywuzzy from pyproject + re-lock
        ├── PR-6 (os.makedirs)
        └── PR-8 (README fixes)            ── after PR-1 & PR-4 so it documents the final CLI/uv flow
                    │
PR-9 (remove dead code)         ── LAST: purely mechanical, over the now-stable code
```

Commits are never squashed at any stage — each PR keeps its full commit history via a
merge commit.

Recommended linear sequence: **PR-7 → PR-1 → PR-2 → PR-3 → PR-4 → PR-5 → PR-6 → PR-8 → PR-9.**
PR-7 and PR-1 are independent and could be reordered or parallelized; everything from PR-3
on assumes PR-2's smoke test exists.

---

## PR-7 — Stop tracking `.DS_Store`, fix `.gitignore` (TODO item 7)

*Sequenced first because it is trivial, independent, and touches no code.*

- **Branch:** `chore/gitignore-dsstore`
- **Files:** `.gitignore`, plus removal of 3 tracked files.
- **Steps:**
  1. Change the `.gitignore` line `**/.DS_Stores` → `**/.DS_Store` (the trailing "s" means
     it currently matches nothing).
  2. `git rm --cached SampleData_RealAnon/.DS_Store old/RemoteYearBot/.DS_Store old/RemoteYearBot/SampleData_RealAnon2020/.DS_Store`
  3. Confirm `git status` shows the three files staged for deletion and no `.DS_Store`
     remains tracked (`git ls-files | grep -i ds_store` → empty).
- **Verification:** `git ls-files` no longer lists any `.DS_Store`.
- **Risk:** none (removes OS cruft only).

---

## PR-1 — Migrate to uv + bump dependencies + fix `np.Inf` (TODO items 1 & 2)

*The foundation. Combines the dependency bump and the uv migration because the bump decides
version floors and the migration decides how they are declared/locked — doing them together
avoids editing versions twice. Includes the `np.Inf` fix because a numpy 2.x bump is
otherwise a hard crash.*

- **Branch:** `chore/migrate-to-uv`
- **Files:** new `pyproject.toml`, new `uv.lock`, delete `requirements.txt`,
  `makeSchedule.py` (np.Inf), `README.md` (Installation section).
- **Steps:**
  1. **Code prerequisite:** in `makeSchedule.py`, replace `np.Inf` → `np.inf` at lines
     ~241–242 (both occurrences). `np.Inf` was removed in NumPy 2.0.
  2. Create `pyproject.toml` with `requires-python = ">=3.13"` and only the **direct**
     runtime dependencies with 3.13-compatible lower bounds:
     - `numpy` (a 2.x), `pandas>=2.2.3`, `matplotlib`, `openpyxl`, `xlsxwriter`
     - `fuzzywuzzy` + `python-Levenshtein` **for now** (the rapidfuzz swap is PR-5; do not
       change imports here)
     - Do **not** list transitive packages (`pillow`, `contourpy`, `kiwisolver`,
       `fonttools`, `pytz`, `six`, …); `uv` resolves and locks them. This also resolves the
       pillow concern from TODO item 1 — a current pillow (≥12.3.0) comes in automatically
       via matplotlib, and it never needed a direct pin.
  3. `uv lock` to generate `uv.lock`; `uv sync` to build the environment.
  4. Delete `requirements.txt`.
  5. Update `README.md` "Installation" to `uv sync`; note that scripts run via
     `uv run python <script>.py`. (Leave deeper README polish to PR-8.)
  6. Confirm `.venv/` is git-ignored — the existing `venv/` line does **not** match uv's
     default `.venv/`; add a `.venv/` line if missing.
- **Verification:**
  `uv run python translateFacultyAvailability.py SampleData_RealAnon` (once PR-4 exists) —
  for now, temporarily point the script's `FOLDERNAME` at `SampleData_RealAnon`, run all
  three stages, and confirm the four `fromBot_*.xlsx` files regenerate. Revert the temporary
  `FOLDERNAME` edit before committing (the permanent fix is PR-4).
- **Risk:** medium — the numpy 2.x / pandas upgrade could surface other deprecations beyond
  `np.Inf`. Run the full pipeline and watch for warnings/errors. If numpy 2.x proves
  troublesome, a `numpy>=1.26,<2` floor that still has 3.13 wheels is an acceptable interim
  target, but then the `np.inf` fix is still correct to keep.
- **Commit both `pyproject.toml` and `uv.lock`** (the lockfile is meant to be tracked).

---

## PR-2 — Add a runnable smoke test (TODO item 9)

*Lands right after the foundation so every subsequent PR can be regression-checked.*

- **Branch:** `test/smoke-pipeline`
- **Files:** new `tests/test_smoke.py` (or `scripts/smoke.sh` / a `Makefile` target — pick
  one; a pytest file is preferred for a clean `uv run pytest`).
- **Steps:**
  1. Add `pytest` as a dev dependency (`uv add --dev pytest`), re-lock.
  2. Write a test that runs all three stages against a **copy** of `SampleData_RealAnon/`
     in a temp dir (so it doesn't dirty the tracked sample outputs), with a small `ntmax`
     (e.g. override to ~2000) so it finishes in seconds, and asserts the four
     `fromBot_*.xlsx` files exist and are non-empty.
  3. To make `ntmax` overridable for the test, expose it as a parameter/env var in
     `makeSchedule()` (small, backward-compatible signature addition with a default).
- **Verification:** `uv run pytest` passes locally.
- **Optional:** add a minimal GitHub Actions workflow (`.github/workflows/ci.yml`) running
  `uv sync` + `uv run pytest` on push/PR. Nice-to-have; can be a follow-up.
- **Risk:** low. The only production-code change is the optional `ntmax` parameter.

---

## PR-3 — Fix the `Targets` "worst-case" reporting bug (TODO item 3)

- **Branch:** `fix/targets-reporting`
- **Files:** `makeSchedule.py`
- **Problem:** call sites write dict key `["min"]` (lines ~309–351) but `__init__`,
  `copy()`, `print()`, and the visualize block read `["worst"]` — so the run summary always
  prints "at worst 0%".
- **Steps:** standardize on a single key. Recommended: use `'min'` everywhere (it reads
  naturally against the code). Update `Targets.__init__` (lines ~562–567), `copy()` (line
  ~573), `print()` (line ~597), and the `visualize` plot (line ~545) to use `'min'`.
  Verify no remaining `'worst'` references (`grep -n "worst" makeSchedule.py`).
- **Verification:** run the pipeline; confirm the summary now prints non-zero, plausible
  "at worst" percentages. `uv run pytest` still passes.
- **Risk:** low, and reporting-only — does not change the optimization/output schedules.

---

## PR-4 — Replace hardcoded `FOLDERNAME` with a CLI argument (TODO item 4)

- **Branch:** `feat/cli-folder-arg`
- **Files:** `translateStudentRequests.py`, `translateFacultyAvailability.py`,
  `makeSchedule.py`.
- **Steps:**
  1. Add `argparse` to each script's `__main__` block: a positional `folder` argument
     defaulting to `SampleData_RealAnon`, so `python makeSchedule.py <folder>` works and the
     sample data runs out of the box.
  2. `makeSchedule.py` currently reads `sys.argv[1]` as the RNG seed — preserve this by
     making seed an optional second positional / `--seed` flag. Keep the existing
     subdirectory-per-seed behavior.
  3. Remove the hand-edited `FOLDERNAME = '/Volumes/Carrot/...'` absolute paths.
- **Verification:** `uv run python makeSchedule.py SampleData_RealAnon 7` reproduces a run;
  `uv run pytest` passes.
- **Risk:** low–medium — be careful not to regress the seed-handling / subdirectory logic in
  `makeSchedule.py`.

---

## PR-5 — Migrate `fuzzywuzzy` → `rapidfuzz` (TODO item 6)

- **Branch:** `refactor/rapidfuzz`
- **Files:** `translateStudentRequests.py`, `translateFacultyAvailability.py`,
  `pyproject.toml`, `uv.lock`.
- **Steps:**
  1. Replace `from fuzzywuzzy import fuzz, process` with the `rapidfuzz` equivalents
     (`from rapidfuzz import fuzz, process`). The `fuzz.WRatio` / `process.extractOne` API is
     compatible; verify the return-tuple shape (`(match, score, index)` in rapidfuzz vs
     `(match, score)` in fuzzywuzzy) and adjust the unpacking / `[1]` score indexing at the
     call sites accordingly.
  2. Remove `fuzzywuzzy` and `python-Levenshtein` from `pyproject.toml`; `uv lock` to re-lock.
- **Verification:** re-run both translators against `SampleData_RealAnon/`; confirm the
  generated matrices and the "MIA faculty" report match the prior fuzzywuzzy output
  (spot-check a few names). `uv run pytest` passes.
- **Risk:** medium — scoring differences between libraries could change fuzzy matches at the
  margin. Compare before/after on the sample data. This is why it is its own PR.

---

## PR-6 — Cross-platform `os.makedirs` (TODO item 5)

- **Branch:** `chore/cross-platform-mkdir`
- **Files:** `makeSchedule.py`
- **Steps:** replace `os.system("mkdir " + directoryName + subdirectoryName)` (line ~53)
  with `os.makedirs(directoryName + subdirectoryName, exist_ok=True)`.
- **Verification:** run with a seed argument twice (same seed) and confirm the subdirectory
  is created without error on the second run. `uv run pytest` passes.
- **Risk:** low.

---

## PR-8 — README fixes (TODO item 8)

*After PR-1 and PR-4 so it can document the final uv + CLI-argument workflow.*

- **Branch:** `docs/readme-fixes`
- **Files:** `README.md`
- **Steps:**
  - Drop `sys` from the dependency list (stdlib).
  - Fix the duplicated `3.` step numbering under "To run".
  - Fix output-filename typos: `forBot_StudentRequestMatrix.xlsx` → `...RequestsMatrix...`;
    `fromBot_StudentSChedules.xlsx` → `...Schedules...`.
  - Rewrite "To run" to use `uv run python <script>.py <folder>` instead of editing
    `FOLDERNAME` in the source.
- **Verification:** manual read-through; every documented command actually runs.
- **Risk:** none (docs only).

---

## PR-9 — Remove dead / commented-out code (TODO item 10)

*Last, so it operates over now-stable code and each earlier PR stayed easy to review.*

- **Branch:** `chore/remove-dead-code`
- **Files:** `makeSchedule.py`, `translateStudentRequests.py`,
  `translateFacultyAvailability.py`.
- **Steps:** delete commented-out `# debugging` blocks (e.g. `makeSchedule.py` ~264–268,
  302–304, 370–373, 409–413) and abandoned reconstruction blocks (~118–143), plus stray
  commented `print`s in the translators. **Behavior-preserving only** — do not touch live
  code paths.
- **Verification:** `git diff` shows only comment/blank-line removals; `uv run pytest`
  passes; pipeline output on sample data is byte-identical for a fixed seed.
- **Risk:** low, but review carefully to ensure no line inside a live block is removed.

---

## Out of scope (tracked separately)

From the TODO's "Larger items" — **not** part of this plan; they need data-format decisions
and belong to a dedicated design pass:

- Multi-word last name handling ("Rodriguez Verdugo") in the name-sort logic.
- Human-readable campus-zone names (requires input-format change).

---

## Summary table

| PR   | Branch                      | TODO item | Touches `makeSchedule.py` | Risk    |
|------|-----------------------------|-----------|:-------------------------:|---------|
| PR-7 | `chore/gitignore-dsstore`   | 7         | no                        | none    |
| PR-1 | `chore/migrate-to-uv`       | 1, 2      | yes (np.inf)              | medium  |
| PR-2 | `test/smoke-pipeline`       | 9         | yes (ntmax param)         | low     |
| PR-3 | `fix/targets-reporting`     | 3         | yes                       | low     |
| PR-4 | `feat/cli-folder-arg`       | 4         | yes                       | low–med |
| PR-5 | `refactor/rapidfuzz`        | 6         | no                        | medium  |
| PR-6 | `chore/cross-platform-mkdir`| 5         | yes                       | low     |
| PR-8 | `docs/readme-fixes`         | 8         | no                        | none    |
| PR-9 | `chore/remove-dead-code`    | 10        | yes                       | low     |
