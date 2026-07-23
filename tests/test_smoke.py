"""End-to-end smoke test for the scheduler.

Runs ``makeSchedule`` against the committed fixture in ``tests/fixtures/sample_v2/``
(a self-consistent, synthetically-augmented version of the anonymized sample data
built by ``make_fixture.py``) with a small ``ntmax`` so it finishes in seconds, and
asserts the four output workbooks are produced.

This guards against dependency upgrades or refactors breaking the pipeline. It does
not check schedule quality — only that the solver runs end-to-end and writes output.
"""

import os
import shutil
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "sample_v2")
sys.path.insert(0, REPO_ROOT)

EXPECTED_OUTPUTS = [
    "fromBot_FacultySchedules.xlsx",
    "fromBot_FacultySchedules_1SheetEach.xlsx",
    "fromBot_StudentSchedules.xlsx",
    "fromBot_StudentSchedules_1SheetEach.xlsx",
]


@pytest.fixture
def workdir(tmp_path):
    """A private copy of the fixture so the test never dirties tracked files."""
    dest = tmp_path / "data"
    shutil.copytree(FIXTURE, dest)
    return str(dest)


def test_makeschedule_runs_and_writes_outputs(workdir, monkeypatch):
    # makeSchedule inspects sys.argv[1] for an optional RNG seed; keep it to one
    # element so the no-seed branch is taken under pytest.
    monkeypatch.setattr(sys, "argv", ["test"])
    from makeSchedule import makeSchedule

    makeSchedule(workdir, ntmax=2000)

    for name in EXPECTED_OUTPUTS:
        path = os.path.join(workdir, name)
        assert os.path.exists(path), f"expected output missing: {name}"
        assert os.path.getsize(path) > 0, f"output is empty: {name}"
