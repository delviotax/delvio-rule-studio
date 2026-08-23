"""Throwaway-SQLite validation for AZ_120 + AZ_120A (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name.

The two checks that matter most, both PROVED rather than asserted:
  * a BLANK apportionment ratio and a 0.000000 produce OPPOSITE outcomes
  * the $50 minimum is ONE PER TAXPAYER - a ten-member group pays $50, not $500

Run:  .venv/Scripts/python.exe scratchpad/validate_az_120.py
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

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_az_120.sqlite3")
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
from specs.management.commands import load_az_120 as AZ  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ======================================================================
# 0. THE SEED GUARD
# ======================================================================
_shipped = AZ.READY_TO_SEED
AZ.READY_TO_SEED = False
try:
    call_command("load_az_120", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

AZ.READY_TO_SEED = True
_saved = AZ.FLOW_ASSERTIONS
AZ.FLOW_ASSERTIONS = []
try:
    call_command("load_az_120", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
AZ.FLOW_ASSERTIONS = _saved

try:
    call_command("load_az_120", verbosity=0)
    PASSES.append("load_az_120 ran + seeded BOTH forms into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_az_120 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields
# ======================================================================
_rules = [r for s in AZ.FORMS for r in s["rules"]]
_lines = [l for s in AZ.FORMS for l in s["lines"]]
_diag = [d for s in AZ.FORMS for d in s["diagnostics"]]
_facts = [f for s in AZ.FORMS for f in s["facts"]]
_scen = [x for s in AZ.FORMS for x in s["scenarios"]]

for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in _rules]),
    (FormRule, "title", [r["title"] for r in _rules]),
    (FormLine, "line_number", [l["line_number"] for l in _lines]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in AZ.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in AZ.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in _diag]),
    (FormDiagnostic, "title", [d["title"] for d in _diag]),
    (FormFact, "fact_key", [f["fact_key"] for f in _facts]),
    (FormFact, "label", [f["label"] for f in _facts]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in _scen]),
    (AuthorityTopic, "topic_name", [n for _c, n in AZ.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in AZ.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in AZ.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in AZ.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structure - TWO forms, shared rules, NOT shared line maps
# ======================================================================
for fn in ("AZ_120", "AZ_120A"):
    f = TaxForm.objects.filter(form_number=fn).first()
    check(f is not None, f"{fn} exists", f"{fn} was not created")
    if f:
        check(f.jurisdiction == "AZ" and f.tax_year == 2025, f"{fn}: AZ / TY2025", f"{fn} identity wrong")

_ids = [r["rule_id"] for r in _rules]
check(len(_ids) == len(set(_ids)), "no duplicate rule_id across BOTH forms",
      f"duplicate rule_id: {sorted({i for i in _ids if _ids.count(i) > 1})}")

# ⚠ A3 - the Schedule A/B RULES are shared (same suffixes, different prefixes)...
_120_suffixes = {r["rule_id"].split("-", 2)[-1] for r in AZ.FORMS[0]["rules"]}
_120a_suffixes = {r["rule_id"].split("-", 2)[-1] for r in AZ.FORMS[1]["rules"]}
_shared = _120_suffixes & _120a_suffixes
check({"SCHA", "SCHB", "965C", "TAX"} <= _shared,
      "A3: Schedule A, Schedule B, the 965(c) add-back and the tax rule are SHARED across both forms",
      f"A3: the shared rule library is incomplete - shared suffixes: {sorted(_shared)}")

# ...but the LINE MAPS are not.
_120_lines = {l["line_number"] for l in AZ.FORMS[0]["lines"]}
_120a_lines = {l["line_number"] for l in AZ.FORMS[1]["lines"]}
check(not (_120_lines & _120a_lines),
      "⚠ A3/G4: the two forms share NO line numbers - the field maps are separate",
      f"G4 violation - shared line numbers: {sorted(_120_lines & _120a_lines)}")
check(all(l.startswith("AZ120-") for l in _120_lines)
      and all(l.startswith("AZ120A-") for l in _120a_lines),
      "G4: each form's lines are namespaced to that form",
      "G4: a line number is not namespaced to its own form")

for spec in AZ.FORMS:
    declared = {r["rule_id"] for r in spec["rules"]}
    bad = [rl[0] for rl in spec["rule_links"] if rl[0] not in declared]
    check(not bad, f"{spec['identity']['form_number']}: rule_links resolve", f"unresolved rule_links: {bad}")

# ======================================================================
# 3. ⚠⚠ THE $50 MINIMUM - ONE PER TAXPAYER, PROVED
# ======================================================================
check(approx(AZ._az_tax(1000000), 49000), "TY2025: 1,000,000 x 4.9% = 49,000",
      f"the ordinary tax is wrong: {AZ._az_tax(1000000)}")
check(approx(AZ._az_tax(0), 50), "a zero-income corporation still owes the $50 minimum",
      "the $50 minimum did not apply at zero income")
check(approx(AZ._az_tax(-250000), 50), "⚠ a LOSS year still owes $50 - the minimum is part of the levy",
      "the $50 minimum did not apply in a loss year")
check(approx(AZ._az_tax(500), 50), "at 500 income the computed 24.50 is displaced by the $50 minimum",
      "the greater-of rule is wrong just below the crossover")
check(approx(AZ._az_tax(0, group_members=10), 50),
      "⚠⚠ a TEN-MEMBER GROUP owes $50, NOT $500 - a unitary/affiliated group is a SINGLE taxpayer",
      f"the minimum was applied per member: {AZ._az_tax(0, group_members=10)}")
check(not approx(AZ._az_tax(0, group_members=10), 500),
      "⚠ the per-member reading (which would overstate a ten-member group by $450) is provably not used",
      "the spec behaves as though the minimum were per member")

# The five TY-keyed rate tiers.
for yr, want in ((2010, "0.06968"), (2014, "0.065"), (2015, "0.060"), (2016, "0.055"),
                 (2017, "0.049"), (2025, "0.049")):
    check(AZ._az_rate(yr) == want, f"A.R.S. 43-1111: TY{yr} rate is {want}",
          f"TY{yr} rate wrong: {AZ._az_rate(yr)}")
check(len(AZ.AZ_RATE_TIERS) == 5, "all FIVE statutory tiers are encoded, not a bare 4.9%",
      f"expected 5 tiers, found {len(AZ.AZ_RATE_TIERS)}")

# ======================================================================
# 4. ⚠⚠ BLANK vs ZERO - OPPOSITE OUTCOMES, PROVED
# ======================================================================
check(AZ._az_apportionment_semantics(None) == "wholly_arizona",
      "⚠⚠ a BLANK ratio means WHOLLY ARIZONA - everything is taxed here",
      f"blank gave {AZ._az_apportionment_semantics(None)!r}")
check(AZ._az_apportionment_semantics(0.0) == "no_nexus",
      "⚠⚠ a 0.000000 ratio means NO ARIZONA NEXUS - nothing is taxed here",
      f"zero gave {AZ._az_apportionment_semantics(0.0)!r}")
check(AZ._az_apportionment_semantics(None) != AZ._az_apportionment_semantics(0.0),
      "⚠⚠ blank and zero are OPPOSITE outcomes and are never normalised to each other",
      "blank and zero resolve to the same thing - the return would be inverted")
check(AZ._az_apportionment_semantics(1.0) == "wholly_arizona",
      "a 1.000000 ratio also means wholly Arizona", "the 1.000000 case is wrong")
check(AZ._az_apportionment_semantics(0.25) == "apportioned",
      "an ordinary fraction apportions normally", "the apportioned case is wrong")

# ======================================================================
# 5. The other D-23 rulings
# ======================================================================
_dmap = {d["diagnostic_id"]: d for d in _diag}
_text = " ".join([d["message"] + d["title"] for d in _diag]
                 + [r["description"] + r["title"] for r in _rules]
                 + [a["description"] for a in AZ.FLOW_ASSERTIONS])

# W5 - the estimates band.
_hi = AZ._az_estimates_posture(1500)
_band_elect = AZ._az_estimates_posture(750, elects_to_pay=True)
_band_no = AZ._az_estimates_posture(750, elects_to_pay=False)
_low = AZ._az_estimates_posture(300)
check(_hi == {"payments_required": True, "eft_required": True},
      "W5: at or above $1,000 payments are REQUIRED and must be by EFT", f"high band wrong: {_hi}")
check(_band_elect == {"payments_required": False, "eft_required": True},
      "⚠ W5: in the $501-$999 band payment is OPTIONAL but EFT is MANDATORY if elected",
      f"the band-with-election case is wrong: {_band_elect}")
check(_band_no == {"payments_required": False, "eft_required": False},
      "W5: in the band with no election, neither applies", f"band-no-election wrong: {_band_no}")
check(_low == {"payments_required": False, "eft_required": False},
      "W5: at or below $500 neither applies", f"low band wrong: {_low}")

# A2 - the 120A book is reference only; D14 recorded.
check("D_AZ120A_BOOK_IS_REFERENCE" in _dmap,
      "A2: the Form 120A instruction book is recorded as a transcription reference only",
      "A2: the standing rule is not recorded")
check("OMITS" in _dmap.get("D_AZ120A_BOOK_IS_REFERENCE", {}).get("message", "").upper(),
      "A2: defect D14 - the omitted 965(c) sentence - is named",
      "A2: D14 is not named")
check("43-1121(12)" in _dmap.get("D_AZ120A_BOOK_IS_REFERENCE", {}).get("message", ""),
      "A2: defect D17 - the irrelevant child-care-facility cite - is named",
      "A2: D17 is not named")

# A1 - the 965(c) add-back on BOTH forms.
_965_rules = [r["rule_id"] for r in _rules if r["rule_id"].endswith("-965C")]
check(len(_965_rules) == 2,
      "⚠ A1: the § 965(c) add-back rule exists on BOTH AZ_120 and AZ_120A",
      f"the add-back is not on both forms: {_965_rules}")
check("43-961(5)" in _text, "A1: the § 43-961(5) general hook is cited", "A1: the hook is not cited")
check("does NOT name" in _text or "is merely SILENT" in _text or "silent" in _text.lower(),
      "A1: the record states that the pinpointed statute does not name § 965(c)",
      "A1: the pinpoint gap is not recorded")

# W8 - zero bonus, no tier table, no ported constant.
check("AZ_165_B1_TIERS" in _text and "not be ported" in _text.lower(),
      "⚠ W8: the record forbids porting AZ_165_B1_TIERS from the pass-through side",
      "W8: the do-not-port warning is missing")
check(AZ._yk(AZ.AZ_BONUS_PCT_ALL_VINTAGES) == "0.00",
      "W8: Arizona bonus depreciation is 0% for every vintage",
      f"the bonus constant is wrong: {AZ.AZ_BONUS_PCT_ALL_VINTAGES}")
check(AZ.AZ_168N_FIRST_YEAR == 2026, "§ 168(n) applies from TY2026 only",
      f"the 168(n) first year is wrong: {AZ.AZ_168N_FIRST_YEAR}")

# W6, W9.
check("D_AZ120_COGS_DEPRECIATION" in _dmap
      and "auto" in _dmap["D_AZ120_COGS_DEPRECIATION"]["message"].lower(),
      "W6: line A1 must capture COGS depreciation by direct entry, never an auto-pull",
      "W6: the COGS-depreciation trap is not recorded")
check("D_AZ120_CREDITS_DEFERRED" in _dmap,
      "W9: Form 300 is a direct-entry aggregator with the credit forms deferred",
      "W9: the credit deferral is not recorded")

# ⚠⚠ The AZ_120A routing trap.
check(AZ._az_120a_eligible(True, True) is True,
      "AZ_120A: a separate-company wholly-Arizona filer is eligible",
      "the ordinary eligible case is wrong")
check(AZ._az_120a_eligible(True, True, partner_in_multistate_or_non_az_partnership=True) is False,
      "⚠⚠ AZ_120A: a partner in a MULTISTATE partnership is FORCED to Form 120, "
      "even though the corporation itself is separate-company and wholly Arizona",
      "the partnership routing trap is not enforced")
check(AZ._az_120a_eligible(False, True) is False and AZ._az_120a_eligible(True, False) is False,
      "AZ_120A: a non-separate or non-wholly-Arizona filer is refused",
      "the basic eligibility conditions are not enforced")
check("D_AZ120A_NOT_ELIGIBLE" in _dmap
      and _dmap["D_AZ120A_NOT_ELIGIBLE"]["severity"] == "error",
      "AZ_120A: ineligibility is a HARD diagnostic", "AZ_120A: ineligibility is not a hard error")

# Apportionment: three methods, sales factor may reach 2.0 - no clamp.
check("2.0" in _text and "clamp" in _text.lower(),
      "the sales factor may reach 2.0 and must NOT be clamped",
      "the no-clamp rule is not recorded")

# TY-keying refuses an unverified year.
try:
    AZ._yk(AZ.AZ_MINIMUM_TAX, 2026)
    FAILURES.append("_yk returned an unverified TY2026 minimum")
except CommandError:
    PASSES.append("_yk REFUSES an unverified tax year")

# Scenario coverage.
_names = " ".join(s["scenario_name"] for s in _scen)
for needle, why in (("ten-member", "the one-minimum-per-group rule"),
                    ("NO NEXUS", "the zero-ratio semantics"),
                    ("blank ratio", "the blank-ratio semantics"),
                    ("estimates band", "the $501-$999 band"),
                    ("FORCES Form 120", "the partnership routing trap"),
                    ("rate tiers", "the TY-keyed rate tiers")):
    check(needle.lower() in _names.lower(), f"a scenario covers {why}", f"NO scenario covers {why}")


# ======================================================================
# ⚠⚠ TWO-WRITERS GUARD - no source this loader DECLARES may also be
#    declared by another loader file.
# ----------------------------------------------------------------------
# Found the hard way 2026-08-23: load_va_500 declared VA_CODE_58_1_408, which
# load_va_pte.py (SEEDED AND LIVE) owns and two live rules cite. update_or_create
# would have silently rewritten its title, citation, trust_score and source_rank
# - `controlling` down to `primary_official`. That is not D-29's duplication; it
# is TWO WRITERS OF ONE ROW, the hazard the 2026-07-05 delta audit flagged.
# A static check over the command files catches it with no database at all.
# ======================================================================
import glob as _glob  # noqa: E402
import os as _os  # noqa: E402

_this = _os.path.basename(r"load_az_120.py")
_declared_here = {s["source_code"] for s in AZ.AUTHORITY_SOURCES}
_clashes = []
for _path in _glob.glob(_os.path.join(PROJECT_ROOT, "specs", "management", "commands", "load_*.py")):
    if _os.path.basename(_path) == _this:
        continue
    _other = io2.open(_path, encoding="utf-8").read()
    for _code in _declared_here:
        if '"source_code": "%s"' % _code in _other:
            _clashes.append((_code, _os.path.basename(_path)))
check(not _clashes,
      "⚠⚠ TWO-WRITERS GUARD: no source declared here is also declared by another loader",
      f"TWO WRITERS OF ONE ROW - this loader would OVERWRITE a source another loader owns: {_clashes}")

# ======================================================================
# 6. Report
# ======================================================================
print("\n" + "=" * 74)
for fn in ("AZ_120", "AZ_120A"):
    f = TaxForm.objects.filter(form_number=fn).first()
    if f:
        print(f"  {fn}: facts {FormFact.objects.filter(tax_form=f).count()} / "
              f"rules {FormRule.objects.filter(tax_form=f).count()} / "
              f"lines {FormLine.objects.filter(tax_form=f).count()} / "
              f"diag {FormDiagnostic.objects.filter(tax_form=f).count()} / "
              f"tests {TestScenario.objects.filter(tax_form=f).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-AZ').count()}")
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
