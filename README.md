
# Interview scheduler bot for MCSB PhD recruitment

MIT License. This software is provided "as is".

## Quickstart

### Installation

Requires python and the following python packages:
`` numpy, xlsxwriter, sys, matplotlib, pandas, fuzzywuzzy ``

### Input data

Requires two xlsx spreadsheets located in a folder (anywhere on machine)

1. __FOLDERNAME/forBot_StudentRequestList.xlsx__ contains:
 - student names,
- student Timezone. Just set to "PST" for local interviews.
 - student properties "asterisk": 0 or 1 to prioritize preferences
 - student property "W" for optional additional property
 - names of requested faculty, separated by commas. These will be fuzzy-compared, so minor typos and missing first names are usually ok. "Faculty requested" means requested by student. "Faculty suggested" means requested by MCSB. In the algorithm they will be combined and treated equally.

2. __FOLDERNAME/forBot_FacultyAvailabilitySurvey.xls__ contains:
 - Faculty names
 - Time slots they're available. The format is clunky, but it's what came out of the survey web tool.
 - Optional faculty property slot "W"

3. __FOLDERNAME/forBot_timeslotNames.xlsx__ contains 
 - names of timeslots as output by the survey tool, 
 - names to be displayed by the robot's schedule
 - what timezone these slots are appropriate for. You can just put "PST" everywhere if all in-person.

### To run

To run,
1. Edit the FOLDERNAME near bottom of translateStudentRequests.py.
2. Run ```python translateStudentRequests.py```.  This should create `forBot_StudentRequestMatrix.xlsx`. It will also write to the terminal a list of faculty names who were requested but are not in the availability schedule.
3. Run ```python translateFacultyAvailability.py```. This will create `forBot_FacultyAvailabilityMatrix.xlsx`
3. Run ``python makeSchedule.py``

4. This will create 4 xlsx spreadsheets:
 - `fromBot_FacultySchedules.xlsx`
 - `fromBot_FacultySchedules_1SheetEach.xlsx`
 - `fromBot_StudentSchedules.xlsx`
 - `fromBot_StudentSChedules_1SheetEach.xlsx`


## Options

* The variable ``ntmax`` determines how long the optimization search will last. On our real data with ~25 students, ~40 faculty and ~8 slots,``ntmax = 2e5`` takes about 3 minutes on a laptop and gives fairly robust optima.
* The ``alpha`` numbers following ``# relative importances of the targets`` allows you to request different prioritization of optima. For example, making the ``alpha`` associated with asterisk students makes their requests much more important than other students.


## Wishlist/todo

* Create campus zones so the student schedules minimize walking.

