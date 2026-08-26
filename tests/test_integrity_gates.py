"""The pre-seed integrity gates must actually run.

WHY THIS FILE EXISTS (2026-08-26, delvio-states S-9, Ken: "whichever you think").
`check_ga500_integrity.py` had been FAILING FOUR SCENARIOS since campaign D-36
(2026-08-23) without anyone noticing. It computed the Schedule 3 proration ratio at
full precision while the scenarios encode the ratified printed-percentage convention
— the loader's own note says that scenario exists precisely to fail the superseded
reading.

It could rot undetected for one reason: NONE of the check_*_integrity.py gates is in
pytest, so the suite's green never covered any of them. That is the campaign's
recurring shape — a mechanism present, documented, believed in, and not connected to
anything. "Does this exist?" and "does this run?" are different questions.

⚠ SCOPE, DELIBERATELY NARROW. A sweep on 2026-08-26 found 12 of 47 gates failing:
1040x, 1065_se, 4562_recon, 6252, k1_basis_704d, schedule_a, schedule_e_8582,
schedule_f, simplified_method, spine, topic8, topic9. Wiring all 47 in would turn the
suite red on eleven pre-existing failures nobody has diagnosed, which is a decision for
Ken and not a side effect of fixing one gate. Only the gate that was actually repaired
is pinned here. The rest are staged (delvio-states STAGED_FOR_KEN.md).

⭐ When one of those eleven is diagnosed and fixed, ADD IT TO GATES BELOW in the same
commit. That is the whole point: a gate outside the suite is a gate that can lie.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Gates proven green and therefore pinned. Growing this list is the goal.
GATES = [
    "check_ga500_integrity.py",
]


@pytest.mark.parametrize("gate", GATES)
def test_integrity_gate_passes(gate):
    """A pinned pre-seed gate exits 0.

    Bug it catches: a ratified convention change (D-36 and its successors) landing in
    the loaders but not in the gate that re-derives them, so the gate silently
    disagrees with the specs it is supposed to police.
    """
    script = REPO_ROOT / gate
    assert script.exists(), f"{gate} is pinned in this test but missing from the repo"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"{gate} FAILED (exit {result.returncode}).\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


def test_pinned_gates_are_a_subset_of_the_real_ones():
    """Every pinned gate name matches a real check_*_integrity.py in the repo root.

    Bug it catches: a gate renamed or deleted while this list still names it — which
    would leave the parametrised test silently covering nothing.
    """
    on_disk = {p.name for p in REPO_ROOT.glob("check_*_integrity.py")}
    missing = sorted(set(GATES) - on_disk)
    assert not missing, f"pinned gates no longer on disk: {missing}"
