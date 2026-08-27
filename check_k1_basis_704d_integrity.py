"""Pre-seed math gate for load_1040_k1_basis_704d (partner §704(d) basis limitation).

Run:  poetry run python check_k1_basis_704d_integrity.py

Independently recomputes every scenario from its OWN transcription of the
§704(d) worksheet arithmetic — available basis (distributions before the loss
test, floored at zero), the two consistency identities (allowed + suspended =
loss; allowed ≤ available), and the routing cap max(raw, −allowed) — and
cross-checks the loader's helper function. The loader and this gate share NO
math. This spec derives nothing under §704(d) (preparer-asserted), so the gate
verifies the CHECKING arithmetic, the scenario expectations, and the invariants
the spec promises (full box amounts preserved; QBI untouched).
"""
import os
import sys
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_1040_k1_basis_704d as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def check(name, got, want):
    if D(got) != D(want):
        err(f"{name}: recomputed {got} != authored {want}")


# ── Independent re-typing of the worksheet arithmetic (Reg §1.704-1(d)(2):
#    distributions reduce basis BEFORE the loss test; §704(d)(1): allowed ≤
#    end-of-year basis; the cap convention mirrors k1_sche_net / Form 7203) ──

def ind_available(beg, adds, dists):
    avail = D(beg) + D(adds) - D(dists)
    return avail if avail > 0 else D(0)


def ind_consistent(loss, allowed, suspended, avail):
    return D(allowed) + D(suspended) == D(loss) and D(allowed) <= D(avail)


def ind_limited(raw_net, allowed):
    cap = -D(allowed)
    return D(raw_net) if D(raw_net) > cap else cap


# ── Cross-check the loader's helper on every scenario ──
for sc in m.N_SCENARIOS:
    name = sc["scenario_name"].split(" — ")[0]
    i = sc["inputs"]
    exp = sc["expected_outputs"]

    avail = ind_available(i.get("beginning_basis"), i.get("current_additions"),
                          i.get("distributions"))
    cons = ind_consistent(i.get("current_loss"), i.get("allowed_loss"),
                          i.get("suspended_carryforward"), avail)
    lim = ind_limited(i.get("raw_net"), i.get("allowed_loss"))

    got = m.compute_k1_basis_704d(
        beginning_basis=i.get("beginning_basis", 0),
        current_additions=i.get("current_additions", 0),
        distributions=i.get("distributions", 0),
        current_loss=i.get("current_loss", 0),
        allowed_loss=i.get("allowed_loss", 0),
        suspended_carryforward=i.get("suspended_carryforward", 0),
        raw_net=i.get("raw_net", 0),
    )

    # The gate's independent math vs the loader's helper
    check(f"{name} available (gate vs loader)", got["available_basis"], avail)
    check(f"{name} limited (gate vs loader)", got["sche_net_limited"], lim)
    if got["consistent"] != cons:
        err(f"{name} consistent: loader {got['consistent']} != gate {cons}")

    # The gate's independent math vs the authored expectations
    if "fk1b_available_basis" in exp:
        check(f"{name} expected available", avail, exp["fk1b_available_basis"])
    if "fk1b_sche_net_limited" in exp:
        check(f"{name} expected limited", lim, exp["fk1b_sche_net_limited"])
    if "consistent" in exp and cons != exp["consistent"]:
        err(f"{name} expected consistent={exp['consistent']}, gate says {cons}")

    # Diagnostic expectations re-derived from the inputs
    if exp.get("D_K1B_ARITH") and cons:
        err(f"{name}: expects D_K1B_ARITH but the worksheet is consistent")
    if exp.get("D_K1B_FULLY_ALLOWED") and not (
        D(i.get("allowed_loss")) == D(i.get("current_loss"))
        and D(i.get("suspended_carryforward")) == 0
    ):
        err(f"{name}: expects D_K1B_FULLY_ALLOWED but allowed != loss or suspended != 0")
    if exp.get("D_K1B_EXCESS_DISTRIB") and not (
        D(i.get("distributions")) > D(i.get("beginning_basis")) + D(i.get("current_additions"))
    ):
        err(f"{name}: expects D_K1B_EXCESS_DISTRIB but distributions <= basis available")

    # QBI invariant (T7): the §199A figure passes through untouched
    if "form_8995_line2_component" in exp:
        if D(exp["form_8995_line2_component"]) != D(i.get("section_199a_qbi")):
            err(f"{name}: QBI expectation {exp['form_8995_line2_component']} != "
                f"input {i.get('section_199a_qbi')} — the worksheet must never touch QBI")

# ── The pilot's headline figures (item 7's reproduction) ──
PILOT_LOSS, PILOT_ALLOWED, PILOT_SUSPENDED = 26850, 10621, 16229
if PILOT_ALLOWED + PILOT_SUSPENDED != PILOT_LOSS:
    err("pilot identity: 10,621 + 16,229 != 26,850")
# Line 41 / AGI movement: both deltas equal the suspended amount
if 106270 - 90041 != PILOT_SUSPENDED or 211235 - 195006 != PILOT_SUSPENDED:
    err("pilot movement: the line-41 and AGI corrections must both equal the suspended 16,229")

# ── Structural checks ──
# READY_TO_SEED provenance check (rewritten 2026-08-26, delvio-states S-10).
# WAS a PRE-FLIP guard: "if READY_TO_SEED: error". Correct while the spec was unapproved,
# and permanently red the moment Ken approved it -- which is why this gate had been failing
# with nothing actually wrong. A gate that cannot go green after the event it guards is not
# a gate; it is a countdown that already finished.
# NOW: the flip is allowed, but it must CARRY ITS AUTHORISATION -- naming Ken and the date of
# the Gate-1 walk, either inline on the flip line or in the comment block directly above it.
# ⚠ THE WINDOW IS NOT DECORATION. The first version of this check read the flip LINE only,
#   and immediately produced a FALSE ACCUSATION against load_1040_schedule_d.py, whose
#   approval is a nine-line comment block above the line ("FLIPPED 2026-06-13 -- Ken APPROVED
#   the review walk in-session (\"Looks good. Go.\")") enumerating all ten walk items. Two
#   loaders annotate inline, one annotates above; encoding the first format as if it were the
#   rule accused the best-documented of the three.
if m.READY_TO_SEED:
    import io as _io
    import re as _re
    _lines = _io.open(m.__file__, encoding="utf-8").read().splitlines()
    _annotated = False
    for _i, _ln in enumerate(_lines):
        if not _re.match(r"\s*READY_TO_SEED\s*=\s*True", _ln):
            continue
        _window = [_ln]
        _j = _i - 1
        while _j >= 0 and (_lines[_j].lstrip().startswith("#") or not _lines[_j].strip()):
            _window.append(_lines[_j])
            _j -= 1
        _blob = "\n".join(_window)
        if "Ken" in _blob and _re.search(r"20\d\d-\d\d-\d\d", _blob):
            _annotated = True
    if not _annotated:
        err("READY_TO_SEED is True but the flip carries no approval annotation "
            "(expected Ken's name and the Gate-1 walk date on the READY_TO_SEED line "
            "or in the comment block directly above it)")
for sc in m.N_SCENARIOS:
    if sc["scenario_type"] not in ("normal", "edge", "failure"):
        err(f"{sc['scenario_name']}: invalid scenario_type {sc['scenario_type']}")
rule_ids = {r["rule_id"] for r in m.N_RULES}
linked = {rid for rid, *_ in m.N_RULE_LINKS}
if rule_ids - linked:
    err(f"uncited rules: {rule_ids - linked}")

if errors:
    print("K1_BASIS_704D INTEGRITY: FAIL")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"K1_BASIS_704D INTEGRITY: OK — {len(m.N_SCENARIOS)} scenarios re-derived, "
      f"{len(rule_ids)} rules all cited, seed guard closed")
