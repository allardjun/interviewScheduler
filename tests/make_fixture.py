"""Build a self-consistent test fixture for the scheduler from the anonymized
sample data.

The committed ``SampleData_RealAnon/`` files are snapshots from different years
and no longer satisfy the invariants ``makeSchedule.py`` requires:

  * the faculty availability matrix (41 faculty) and the student request matrix
    (46 faculty) do not share a faculty axis;
  * the faculty survey names carry trailing whitespace/newlines that don't match
    the (clean) availability-matrix column names;
  * the survey lacks the ``Office Location`` / ``Office Phone Number`` /
    ``Campus Zone`` columns the current solver reads; and
  * the student list lacks the ``wngbngd`` / ``Mon`` / ``Tue`` columns the
    current solver reads.

This script reconciles those files onto a single faculty axis (the availability
matrix) and adds **synthetic** values for the missing fields, writing a working,
canonically-named dataset to ``tests/fixtures/sample_v2/``. The output is what
``tests/test_smoke.py`` exercises. Re-run with ``uv run python tests/make_fixture.py``
if the source anon data changes.

All added field *values* are synthetic (deterministic, seeded); only the real
anonymized names/availability/requests are carried over.
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, os.pardir, "SampleData_RealAnon")
OUT = os.path.join(HERE, "fixtures", "sample_v2")

rng = np.random.default_rng(0)


def main():
    os.makedirs(OUT, exist_ok=True)

    availability = pd.read_excel(
        os.path.join(SRC, "forBot_FacultyAvailabilityMatrix.xlsx"), index_col=0
    ).fillna(0)
    survey = pd.read_excel(os.path.join(SRC, "forBot_FacultyAvailabilitySurvey.xlsx"))
    requests = pd.read_excel(
        os.path.join(SRC, "forBot_StudentRequestsMatrix.xlsx"), index_col=0
    ).fillna(0)
    student_list = pd.read_excel(
        os.path.join(SRC, "forBot_StudentRequestList.xlsx"), index_col=0
    )

    # Authoritative faculty axis = the availability matrix columns (clean names).
    faculty = list(availability.columns)
    n_fac = len(faculty)
    n_slots = availability.shape[0]

    # --- Faculty availability matrix: carry over unchanged. -------------------
    availability.to_excel(os.path.join(OUT, "forBot_FacultyAvailabilityMatrix.xlsx"))

    # --- Faculty survey: align names to the availability axis, add synthetic
    #     Office Location / Office Phone Number / Campus Zone. --------------------
    survey = survey.copy()
    survey["Name"] = survey["Name"].astype(str).str.strip()
    survey = survey.drop_duplicates(subset="Name").set_index("Name")
    survey_v2 = pd.DataFrame({"Name": faculty})
    survey_v2["W"] = [
        int(survey.loc[f, "W"]) if f in survey.index and not pd.isna(survey.loc[f, "W"]) else 0
        for f in faculty
    ]
    def _max_students(f):
        if f in survey.index:
            v = survey.loc[f, "Max number of students"]
            if not pd.isna(v) and int(v) > 0:
                return int(v)
        return 5

    survey_v2["Max number of students"] = [_max_students(f) for f in faculty]
    # Synthetic office/zone fields.
    survey_v2["Office Location"] = [f"Bldg {i % 6 + 1} Rm {100 + i}" for i in range(n_fac)]
    survey_v2["Office Phone Number"] = [f"949-555-{1000 + i:04d}" for i in range(n_fac)]
    survey_v2["Campus Zone"] = [int(rng.integers(1, 4)) for _ in range(n_fac)]
    survey_v2.to_excel(os.path.join(OUT, "forBot_FacultyAvailabilitySurvey.xlsx"), index=False)

    # --- Student request matrix: reindex columns onto the faculty axis. --------
    requests_v2 = requests.reindex(columns=faculty, fill_value=0).fillna(0).astype(int)
    requests_v2.to_excel(os.path.join(OUT, "forBot_StudentRequestsMatrix.xlsx"))
    students = list(requests_v2.index)
    n_stud = len(students)

    # --- Student list: same students/order, add synthetic wngbngd/Mon/Tue. -----
    asterisk = (
        [int(x) for x in student_list["Asterisk"].fillna(0)]
        if "Asterisk" in student_list.columns
        else [0] * n_stud
    )
    student_v2 = pd.DataFrame(
        {
            "Student name": students,
            "Asterisk": asterisk[:n_stud],
            "Timezone": "PST",
            "W": 0,
            "wngbngd": [i % 3 == 0 for i in range(n_stud)],  # synthetic
            "Mon": 1,  # synthetic: everyone present both days
            "Tue": 1,
        }
    ).set_index("Student name")
    student_v2["wngbngd"] = student_v2["wngbngd"].astype(int)
    student_v2.to_excel(os.path.join(OUT, "forBot_StudentRequestList.xlsx"))

    # --- Timeslot names: one per availability row. -----------------------------
    days = ["Mon"] * 5 + ["Tue"] * 4
    names = []
    for i in range(n_slots):
        day = days[i] if i < len(days) else f"Extra{i}"
        names.append(f"{day} slot {i}")
    pd.DataFrame({"Timeslot name": names}).to_excel(
        os.path.join(OUT, "forBot_timeslotNames.xlsx"), index=False
    )

    print(
        f"Wrote fixture to {OUT}: {n_fac} faculty, {n_stud} students, {n_slots} timeslots"
    )


if __name__ == "__main__":
    main()
