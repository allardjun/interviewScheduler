
# Interview scheduler bot for MCSB PhD recruitment

## Quickstart

### Installation

Requires python and the following python packages:
`` numpy, xlsxwriter, sys, matplotlib, pandas, fuzzywuzzy ``

### Input data

Requires two xlsx spreadsheets located in a folder (anywhere on machine)

1. __FOLDERNAME/forBot_StudentRequestList.xlsx__ contains:
 - student names,
 - student properties "asterisk": 0 or 1 to prioritize preferences
 - student property "W": 1 for woman, non-gender-binary or non-gender-declared
 - names of requested faculty, separated by commas. These will be fuzzy-compared, so minor typos and missing first names are usually ok.

2. __FOLDERNAME/forBot_FacultyAvailabilityMatrix.xls__ contains:
 - Faculty names
 - Office location and any other info to be displayed on the student schedules
 - Time slots
 - Whether the faculty is available or not in each slot: 1 for available, 0 or empty for unavailable.
 - Faculty gender: 1 for woman.

### To run

To run,
1. Edit the FOLDERNAME near bottom of translateStudentRequests.py.
2. Run ```python translateStudentRequests.py```.  This should create forBot_StudentRequestMatrix.xlsx. It will also write to the terminal a list of faculty names who were requested but are not in the availability schedule.
3. Run ``python schedulerBot.py``

4. This will create 4 xlsx spreadsheets:
 - fromBot_FacultySchedules.xlsx
 - fromBot_FacultySchedules_1SheetEach.xlsx
 - fromBot_StudentSchedules.xlsx
 - fromBot_StudentSChedules_1SheetEach.xlsx


## Options

* The variable ``ntmax`` determines how long the optimization search will last. On our real data with ~25 students, ~40 faculty and ~8 slots,``ntmax = 2e5`` takes about 3 minutes on a laptop and gives fairly robust optima.
* The ``alpha`` numbers following ``# relative importances of the targets`` allows you to request different prioritization of optima. For example, making the ``alpha`` associated with asterisk students makes their requests much more important than other students.


## Wishlist/todo

* Create campus zones so the student schedules minimize walking.
* Make the studentRequestList have another column for pairings that are identified as important by Admissions Committee.
