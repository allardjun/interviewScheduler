
# Interview scheduler bot for MCSB PhD recruitment

MIT License. This software is provided "as is".

## Quickstart

### Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.
With uv installed, run:

```
uv sync
```

This creates a virtual environment (`.venv/`) with all dependencies pinned in
`uv.lock`. Run any of the scripts below with `uv run python <script>.py`.

### Input data

Requires three xlsx spreadsheets located in a folder (anywhere on machine)

1. __FOLDERNAME/forBot_StudentRequestList.xlsx__ contains:
 - student names,
- student Timezone. Just set to "PST" for local interviews.
 - student properties "asterisk": 0 or 1 to prioritize preferences
 - student property "W" for optional additional property
 - names of requested faculty, separated by commas. These will be fuzzy-compared, so minor typos and missing first names are usually ok. "Faculty requested" means requested by student. "Faculty suggested" means requested by MCSB. In the algorithm they will be combined and treated equally.

2. __FOLDERNAME/forBot_FacultyAvailabilitySurvey.xlsx__ contains:
 - Faculty names
 - Time slots they're available. The format is clunky, but it's what came out of the survey web tool.
 - Optional faculty property slot "W"

3. __FOLDERNAME/forBot_timeslotNames.xlsx__ contains 
 - names of timeslots as output by the survey tool, 
 - names to be displayed by the robot's schedule
 - what timezone these slots are appropriate for. You can just put "PST" everywhere if all in-person.

### To run

Each script takes the data folder as a command-line argument (call it
`FOLDER`); all input and output files live in that folder. Run the three
stages in order:

1. Build the faculty availability matrix:
   ```
   uv run python translateFacultyAvailability.py FOLDER
   ```
   This creates `forBot_FacultyAvailabilityMatrix.xlsx`.
2. Build the student request matrix (needs the availability matrix from step 1):
   ```
   uv run python translateStudentRequests.py FOLDER
   ```
   This creates `forBot_StudentRequestsMatrix.xlsx`, and prints a list of
   faculty who were requested but are not in the availability schedule.
3. Generate the schedules:
   ```
   uv run python makeSchedule.py FOLDER
   ```
   Add `--seed N` for a repeatable run; its output is written to `FOLDER/N/`.

Step 3 creates 4 xlsx spreadsheets in `FOLDER`:
 - `fromBot_FacultySchedules.xlsx`
 - `fromBot_FacultySchedules_1SheetEach.xlsx`
 - `fromBot_StudentSchedules.xlsx`
 - `fromBot_StudentSchedules_1SheetEach.xlsx`

> **Note:** the committed `SampleData_RealAnon/` is a snapshot that predates the
> current input schema and no longer runs. A small, self-consistent sample that
> works with the current code lives in `tests/fixtures/sample_v2/` (see
> `tests/make_fixture.py`), and is exercised by `uv run pytest`.


## Options

* The ``ntmax`` parameter of ``makeSchedule`` (default ``5e5``) determines how long the optimization search will last. On our real data with ~25 students, ~40 faculty and ~8 slots, ``ntmax = 2e5`` takes about 3 minutes on a laptop and gives fairly robust optima.
* The ``alpha`` numbers following ``# relative importances of the targets`` allows you to request different prioritization of optima. For example, making the ``alpha`` associated with asterisk students makes their requests much more important than other students.


## Wishlist/todo

* [x] Create campus zones so the student schedules minimize walking.
* Campus zones use a number code. Switch to meaningful names
* Issue with multi-space names like Rodriguez Verdugo

