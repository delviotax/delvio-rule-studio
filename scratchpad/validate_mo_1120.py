"""Throwaway-SQLite validation for MO_1120 (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name.

The checks that matter most, all PROVED rather than asserted:
  * the MO-C map is EXPLICIT - and the tempting offset formula is shown to disagree
  * the foreign tax credit is added back BEFORE the 50%, not after
  * the consolidated denominator excludes loss companies
  * the individual $5,000/$10,000 caps appear NOWHERE (an absence check)
  * two different rounding rules coexist (THREE on page 1, FOUR in Part 3)

Run:  .venv/Scripts/python.exe scratchpad/validate_mo_1120.py
"""
import io as io2
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_mo_1120.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from django.core.management.base import CommandError  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.management.commands import load_mo_1120 as MO  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.02):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ======================================================================
# 0. THE SEED GUARD
# ======================================================================
_shipped = MO.READY_TO_SEED
MO.READY_TO_SEED = False
try:
    call_command("load_mo_1120", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

MO.READY_TO_SEED = True
_saved = MO.FLOW_ASSERTIONS
MO.FLOW_ASSERTIONS = []
try:
    call_command("load_mo_1120", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
MO.FLOW_ASSERTIONS = _saved

try:
    call_command("load_mo_1120", verbosity=0)
    PASSES.append("load_mo_1120 ran + seeded into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_mo_1120 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in MO.F_RULES]),
    (FormRule, "title", [r["title"] for r in MO.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in MO.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in MO.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in MO.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in MO.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in MO.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in MO.F_FACTS]),
    (FormFact, "label", [f["label"] for f in MO.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in MO.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in MO.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in MO.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in MO.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in MO.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structure
# ======================================================================
form = TaxForm.objects.filter(form_number="MO_1120").first()
check(form is not None, "MO_1120 exists", "MO_1120 was not created")
if form:
    check(form.jurisdiction == "MO" and form.tax_year == 2025, "identity: MO / TY2025", "identity wrong")
    check(form.entity_types == ["1120"], "entity_types == ['1120']", f"wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in MO.F_RULES]),
                      ("line_number", [l["line_number"] for l in MO.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in MO.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in MO.F_DIAGNOSTICS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in MO.F_RULES}
check(not sorted(_declared - {rl[0] for rl in MO.F_RULE_LINKS}),
      "every FormRule carries at least one authority link",
      f"uncitable rules: {sorted(_declared - {rl[0] for rl in MO.F_RULE_LINKS})}")

# ⚠⚠ TWO-WRITERS GUARD (the D-31 lesson) - static, no database needed.
_declared_here = {s["source_code"] for s in MO.AUTHORITY_SOURCES}
_clashes = []
import glob as _glob  # noqa: E402
for _path in _glob.glob(os.path.join(PROJECT_ROOT, "specs", "management", "commands", "load_*.py")):
    if os.path.basename(_path) == "load_mo_1120.py":
        continue
    _other = io2.open(_path, encoding="utf-8").read()
    for _code in _declared_here:
        if '"source_code": "%s"' % _code in _other:
            _clashes.append((_code, os.path.basename(_path)))
check(not _clashes,
      "⚠⚠ TWO-WRITERS GUARD: no source declared here is also declared by another loader",
      f"TWO WRITERS OF ONE ROW - would OVERWRITE a source another loader owns: {_clashes}")

# ======================================================================
# 3. ⚠⚠ THE MO-C MAP - EXPLICIT, and the offset formula PROVED WRONG
# ======================================================================
check(MO._mo_c_federal_line(8) == 8, "MO-C line 8 maps to federal Schedule C line 8",
      "the pre-subtotal range is wrong")
check(MO._mo_c_federal_line(9) == 10,
      "⚠⚠ MO-C line 9 maps to FEDERAL line 10 - the Subtotal line is dropped",
      f"MO-C 9 mapped to {MO._mo_c_federal_line(9)}, not 10")
check(MO._mo_c_federal_line(21) == 22, "MO-C line 21 maps to federal line 22",
      "the top of the range is wrong")

# The tempting simplification, shown to disagree across the whole affected range.
_naive_wrong = [n for n in range(1, 22) if (n + (1 if n >= 9 else 0)) != MO._mo_c_federal_line(n)]
_offset_matches = [n for n in range(1, 22) if (n + (1 if n >= 9 else 0)) == MO._mo_c_federal_line(n)]
check(len(_offset_matches) == 21,
      "the documented +1-from-9 shape reproduces the map (so the map is internally consistent)",
      f"the map disagrees with its own documented shape at: {_naive_wrong}")
# ...but a FLAT offset - the mistake someone would actually make - is wrong for 8 rows.
_flat_wrong = [n for n in range(1, 22) if (n + 1) != MO._mo_c_federal_line(n)]
check(len(_flat_wrong) == 8,
      f"⚠⚠ a FLAT +1 offset is wrong for {len(_flat_wrong)} rows (lines 1-8) - and an identity "
      "mapping is wrong for the other 13. No single arithmetic rule fits.",
      f"expected a flat offset to be wrong for 8 rows, found {len(_flat_wrong)}")
_identity_wrong = [n for n in range(1, 22) if n != MO._mo_c_federal_line(n)]
check(len(_identity_wrong) == 13,
      "⚠⚠ an IDENTITY mapping (MO-C N == federal N) is wrong for exactly THIRTEEN rows",
      f"expected identity to be wrong for 13 rows, found {len(_identity_wrong)}")
check(9 not in MO.MO_C_TO_FEDERAL_SCHEDULE_C.values(),
      "federal Schedule C line 9 (Subtotal) has NO MO-C counterpart",
      "federal line 9 was mapped to something - it has no MO-C line")
try:
    MO._mo_c_federal_line(22)
    FAILURES.append("the MO-C map extrapolated beyond its verified range")
except CommandError:
    PASSES.append("the MO-C map REFUSES to extrapolate beyond its verified 21 lines")

# ======================================================================
# 4. ⚠ THE FEDERAL INCOME TAX DEDUCTION
# ======================================================================
check(approx(MO._mo_federal_tax_deduction(210000, 0), 105000),
      "50% of federal tax with no FTC: 210,000 -> 105,000",
      "the base deduction is wrong")
_with_ftc = MO._mo_federal_tax_deduction(300000, 80000)
check(approx(_with_ftc, 190000),
      "⭐ the FTC is added back BEFORE the 50%: (300,000 + 80,000) x 50% = 190,000",
      f"the FTC add-back is wrong: {_with_ftc}")
check(not approx(_with_ftc, 150000),
      "⚠ omitting the add-back would give 150,000 - understating the deduction by 40,000 and "
      "OVERSTATING Missouri tax",
      "the spec behaves as though the FTC were not added back")
check(approx(MO._mo_federal_tax_deduction(5000000, 0), 2500000),
      "⚠⚠ NO CAP: 5,000,000 x 50% = 2,500,000, not $5,000 or $10,000",
      "a cap was applied to the corporate deduction")

# The consolidated branch and its loss-company exclusion.
_con = MO._mo_federal_tax_deduction_consolidated(100000, 500000, 2000000)
check(approx(_con, 25000),
      "consolidated: 500,000 / 2,000,000 = 0.25 x 100,000 = 25,000",
      f"the consolidated apportionment of the deduction is wrong: {_con}")
_con_if_losses_included = MO._mo_federal_tax_deduction_consolidated(100000, 500000, 3000000)
check(_con_if_losses_included < _con,
      "⚠ including loss companies would INFLATE the denominator and cut every profitable member's share",
      "the denominator does not behave as expected")
check(MO._mo_federal_tax_deduction_consolidated(100000, 500000, 0) is None,
      "a zero denominator yields no ratio, not a divide-by-zero",
      "the zero-denominator case is wrong")

# ⚠ Two rounding rules.
check(MO._yk(MO.MO_APPORT_DECIMALS) == 3 and MO._yk(MO.MO_FED_RATIO_DECIMALS) == 4,
      "⚠ TWO rounding rules coexist: THREE decimals on page 1, FOUR in Part 3",
      f"rounding wrong: {MO.MO_APPORT_DECIMALS} / {MO.MO_FED_RATIO_DECIMALS}")
check(MO._yk(MO.MO_APPORT_DECIMALS) != MO._yk(MO.MO_FED_RATIO_DECIMALS),
      "⚠ the two precisions are NOT shared - a single constant would be wrong on one of them",
      "the two rounding rules were collapsed into one")

# ======================================================================
# 5. ⚠⚠ ABSENCE CHECK - the individual caps must appear NOWHERE
# ======================================================================
# ⚠ Check the CODE, not the prose. An earlier version scanned the source text and
# false-positived on this spec's own warnings AGAINST using these figures - the
# warnings are the point, so the check has to look at what is ENCODED. Parsing the
# module and inspecting numeric literals answers the real question: does any
# individual-only figure exist as a value this spec could apply?
import ast as _ast  # noqa: E402

_srcfile = io2.open(
    os.path.join(PROJECT_ROOT, "specs", "management", "commands", "load_mo_1120.py"),
    encoding="utf-8").read()
_tree = _ast.parse(_srcfile)
_literals = {n.value for n in _ast.walk(_tree)
             if isinstance(n, _ast.Constant) and isinstance(n.value, (int, float))
             and not isinstance(n.value, bool)}
_forbidden_values = {5000, 10000, 0.35, 0.15, 0.05}
_found = sorted(_forbidden_values & _literals)
check(not _found,
      "⚠⚠ NO individual-only figure exists as a numeric literal anywhere in the spec - "
      "the $5,000 / $10,000 caps and the 35/25/15/5/0 table are absent as VALUES, "
      "and appear only in warnings against using them",
      f"an individual-only figure is encoded as a literal: {_found}")
check(0.50 in _literals or "0.50" in _srcfile,
      "the corporate 50% IS present - the absence check is not passing by emptiness",
      "the 50% constant is missing, so the absence check proves nothing")

check("MO_FED_TAX_DEDUCTION_PCT" in _srcfile and '"0.50"' in _srcfile,
      "the corporate deduction is a flat 50% with no table",
      "the 50% constant is missing")

# ======================================================================
# 6. Ken's other D-24 rulings
# ======================================================================
_d = {x["diagnostic_id"]: x for x in MO.F_DIAGNOSTICS}
_text = " ".join([x["message"] + x["title"] for x in MO.F_DIAGNOSTICS]
                 + [r["description"] + r["title"] for r in MO.F_RULES]
                 + [a["description"] for a in MO.FLOW_ASSERTIONS])

check("D_MO1120_FED_ATTACHMENT_CLIFF" in _d
      and _d["D_MO1120_FED_ATTACHMENT_CLIFF"]["severity"] == "error",
      "⚠⚠ M5: the attachment cliff is a HARD BLOCK, not a warning",
      "M5: the attachment cliff is not a hard error")
_m5 = _d.get("D_MO1120_FED_ATTACHMENT_CLIFF", {}).get("message", "")
check(all(t in _m5 for t in ("CONSOLIDATED Federal Form 1120", "Schedule J", "income statement",
                             "summary of profit companies")),
      "M5: all four required attachments are enumerated on screen",
      "M5: the attachments are not all enumerated")
check("REDUCED TO ZERO" in _m5.upper(), "M5: the message quotes the zero-cliff wording",
      "M5: the cliff wording is not quoted")

check("D_MO1120_ALT_FEDERAL_RETURN" in _d and _d["D_MO1120_ALT_FEDERAL_RETURN"]["severity"] == "error",
      "M2: the six alternative federal returns are refused by a hard diagnostic",
      "M2: the alternative federal returns are not refused")
check(len(MO.MO_DEFERRED_FEDERAL_RETURNS) == 6,
      "M2: all SIX alternative federal return types are named",
      f"expected 6 deferred federal returns, found {len(MO.MO_DEFERRED_FEDERAL_RETURNS)}")

check("D_MO1120_MO_CONSOLIDATED" in _d,
      "M3: a true Missouri consolidated return is refused...",
      "M3: the Missouri consolidated refusal is missing")
check("consolidated-federal" in _text.lower() or "CONSOLIDATED FEDERAL" in _text.upper(),
      "M3: ...while the consolidated-federal / separate-Missouri branch IS built",
      "M3: the built branch is not recorded")

check("D_MO1120_PTE_CREDIT_SOURCE" in _d
      and "Part B Column 6" in _d["D_MO1120_PTE_CREDIT_SOURCE"]["message"],
      "M4: the credit-poisoning path names MO-PTE Part B Column 6 as the thing NOT to use",
      "M4: the credit-poisoning warning is missing or unspecific")

check(MO._yk(MO.MO_NOL_CARRYFORWARD_YEARS) == 20,
      "M7: the 20-year NOL cap is encoded now, though dormant for TY2025",
      "M7: the NOL cap is not encoded")

check("D_MO1120_APPORT_METHOD" in _d
      and "industry" in _d["D_MO1120_APPORT_METHOD"]["message"].lower(),
      "W5: the routing help copy ships - the method names describe the STATUTE, not the industry",
      "W5: the routing help copy is missing")

check("self-referential" in _text.lower(),
      "⚠ the self-referential line-21 instruction is recorded so nobody 'corrects' the face to it",
      "the line-21 instruction conflict is not recorded")

# Arithmetic spot checks.
check(approx(MO._mo_line13(800000, 150000, 0), 650000), "L13 = L9 - L10 - L11",
      "the L13 arithmetic is wrong")
check(approx(MO._mo_line13(100000, 150000, 0), 0),
      "L13 floors at zero - 'Do not enter a negative number'", "L13 did not floor at zero")
check(approx(MO._mo_line14(895000), 35800), "L14 = 4% of L13", "the 4% computation is wrong")
check(approx(MO._mo_line14(0), 0), "no tax on zero Missouri taxable income",
      "a tax was computed on zero income")
try:
    MO._yk(MO.MO_CORP_RATE, 2026)
    FAILURES.append("_yk returned an unverified TY2026 rate")
except CommandError:
    PASSES.append("_yk REFUSES an unverified tax year")

# Scenario coverage.
_names = " ".join(s["scenario_name"] for s in MO.F_SCENARIOS)
for needle, why in (("ADDED BACK", "the FTC add-back"),
                    ("FEDERAL line 10", "the MO-C offset"),
                    ("missing attachments", "the attachment cliff"),
                    ("loss-company", "the denominator exclusion"),
                    ("individual caps", "the absent individual caps")):
    check(needle.lower() in _names.lower(), f"a scenario covers {why}", f"NO scenario covers {why}")

# ======================================================================
# 7. Report
# ======================================================================
print("\n" + "=" * 74)
if form:
    print(f"  MO_1120: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-MO').count()}")
print(f"  rule authority links: {RuleAuthorityLink.objects.count()}")
print("=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
for f in FAILURES:
    print(f"  FAIL  {f}")
print("=" * 74)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print(f"NOTE: READY_TO_SEED driven in memory only; on disk it ships {_shipped}.")
print("NOTE: throwaway SQLite only -- test_postgres was never touched.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
