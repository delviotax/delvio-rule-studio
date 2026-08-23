"""Throwaway-SQLite validation for Oregon's shared schedules OR_AP + OR_ASC_CORP.

⚠ NEVER touches `test_postgres` — RS and delvio-tax share that database name.

Checks:
  0. The seed guard, pinned to the GATE MECHANISM (campaign D-17), never to the
     sentinel's disk value.
  1. CharField caps read from the REAL model fields (Postgres enforces, SQLite
     does not).
  2. Structural integrity + the D-25/O4 point: both forms EXIST, so the seeded
     OR_20_S references resolve.
  3. Arithmetic oracles through the loader's own helpers -- especially the
     ALTERNATIVE worksheet's LIVE divisor, which is the trap this spec exists
     to prevent.
  4. The form-gating and G4 namespacing rules are encoded, not assumed.

Run:  .venv/Scripts/python.exe scratchpad/validate_or_shared.py
"""
import os
import sys

# The Windows console defaults to cp1252 and cannot encode the marks used in
# these messages. Force UTF-8 rather than stripping the text.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_or_shared.sqlite3")
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
from sources.models import (  # noqa: E402
    AuthorityExcerpt, AuthoritySource, AuthorityTopic, RuleAuthorityLink,
)
from specs.management.commands import load_or_shared_schedules as OR  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.00005):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ======================================================================
# 0. THE SEED GUARD -- pin the MECHANISM, not the sentinel's value
# ======================================================================
_shipped = OR.READY_TO_SEED

OR.READY_TO_SEED = False
try:
    call_command("load_or_shared_schedules", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"guard fired with an unexpected message: {msg[:160]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule (a relayed approval never opens it)",
          "the guard message omits the gate rule")
    # ⚠ CORRECTED 2026-08-23: an earlier version asserted the guard said this seed
    # "RE-POINTS the already-seeded OR_20_S". A pre-flight against PROD showed that
    # is NOT what the loader does - it creates two new forms and adds
    # AuthorityFormLink rows keyed on a form_code STRING, touching no OR_20_S row.
    # The guard now states the scope accurately and this pins the accurate wording.
    # Overstating a blast radius is its own defect: it trains the reader to
    # discount the warning.
    check("this seed is ADDITIVE" in msg and "does NOT modify any OR_20_S row" in msg,
          "the guard states the seed scope ACCURATELY (additive; no OR_20_S row modified)",
          f"the guard misstates the seed scope: {msg[:200]!r}")
    check("SEPARATE change" in msg,
          "the guard records that wiring OR_20_S own lines is a separate, still-open change",
          "the guard does not distinguish the deeper re-point as separate")

# ⚠ PROVE THE REFERENCE CHECK BITES BEFORE STANDING THE PREREQUISITES UP.
# After the 2026-08-23 consolidation this loader REFERENCES the OR-AP and
# OR-ASC-CORP sources rather than creating them (they belong to load_or_pte).
# With the throwaway DB empty, the loader must REFUSE - that refusal is the
# dangling-reference guard doing its job, and it is worth asserting before we
# satisfy it.
OR.READY_TO_SEED = True
try:
    call_command("load_or_shared_schedules", verbosity=0)
    FAILURES.append("the loader did NOT refuse with its referenced sources absent")
except CommandError as exc:
    check("DANGLING REFERENCE" in str(exc),
          "the loader REFUSES while its referenced sources are absent, naming the D-25/O4 defect",
          f"refused, but without naming the defect: {str(exc)[:140]!r}")

# Stand up the prerequisites the way PROD has them: load_or_pte.py owns these two
# source_codes. Minimal stand-ins are enough for this harness's purposes.
for _code, _title in (
    ("OR_2025_SCH_OR_AP", "2025 Schedule OR-AP, Apportionment of Income for Corporations and Partnerships"),
    ("OR_2025_SCH_ASC_CORP", "2025 Schedule OR-ASC-CORP, Oregon Adjustments for Corporation Returns"),
):
    AuthoritySource.objects.update_or_create(
        source_code=_code,
        defaults={"source_type": "state_form", "source_rank": "primary_official",
                  "jurisdiction_code": "OR", "title": _title,
                  "issuer": "Oregon Department of Revenue", "current_status": "active",
                  "is_substantive_authority": True, "trust_score": 9.5},
    )
PASSES.append("prerequisite sources stood up (in prod these come from load_or_pte)")

_saved = OR.FORMS[0]["assertions"]
OR.FORMS[0]["assertions"] = []
try:
    call_command("load_or_shared_schedules", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a spec with NO flow assertions")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
OR.FORMS[0]["assertions"] = _saved

try:
    call_command("load_or_shared_schedules", verbosity=0)
    PASSES.append("loader ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"loader raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields
# ======================================================================
_all_rules = [r for s in OR.FORMS for r in s["rules"]]
_all_lines = [l for s in OR.FORMS for l in s["lines"]]
_all_diag = [d for s in OR.FORMS for d in s["diagnostics"]]
_all_facts = [f for s in OR.FORMS for f in s["facts"]]
_all_scen = [s2 for s in OR.FORMS for s2 in s["scenarios"]]
_all_assert = [a for s in OR.FORMS for a in s["assertions"]]

for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in _all_rules]),
    (FormRule, "title", [r["title"] for r in _all_rules]),
    (FormLine, "line_number", [l["line_number"] for l in _all_lines]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in _all_assert]),
    (FlowAssertion, "title", [a["title"] for a in _all_assert]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in _all_diag]),
    (FormDiagnostic, "title", [d["title"] for d in _all_diag]),
    (FormFact, "fact_key", [f["fact_key"] for f in _all_facts]),
    (FormFact, "label", [f["label"] for f in _all_facts]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in _all_scen]),
    (AuthorityTopic, "topic_name", [n for _c, n in OR.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in OR.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in OR.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in OR.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structural integrity -- and the D-25/O4 point
# ======================================================================
for fn, ents in (("OR_AP", OR.AP_ENTITY_TYPES), ("OR_ASC_CORP", OR.ASC_ENTITY_TYPES)):
    f = TaxForm.objects.filter(form_number=fn).first()
    check(f is not None, f"{fn} EXISTS as a first-class form (this is the D-25/O4 fix)",
          f"{fn} was not created -- the dangling reference is NOT fixed")
    if f:
        check(f.jurisdiction == "OR" and f.tax_year == 2025,
              f"{fn} identity: OR / TY2025", f"{fn} identity wrong")
        check(f.entity_types == ents, f"{fn} entity_types == {ents}",
              f"{fn} entity_types wrong: {f.entity_types}")

# OR-AP is shared with partnerships; OR-ASC-CORP is corporation-only.
check("1065" in OR.AP_ENTITY_TYPES,
      "OR_AP serves 1065 too -- it is shared with OR-65 (one physical form, five returns)",
      "OR_AP omits 1065 despite being shared with OR-65")
check("1065" not in OR.ASC_ENTITY_TYPES,
      "OR_ASC_CORP excludes 1065 -- 'this schedule is for corporation filers only'",
      "OR_ASC_CORP wrongly includes 1065")

for label, values in (("rule_id", [r["rule_id"] for r in _all_rules]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in _all_diag]),
                      ("assertion_id", [a["assertion_id"] for a in _all_assert]),
                      ("fact_key", [f["fact_key"] for f in _all_facts])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label} across both schedules", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in _all_rules}
_srcs = {s["source_code"] for s in OR.AUTHORITY_SOURCES} | set(OR.EXISTING_SOURCES_TO_REFERENCE)
for spec in OR.FORMS:
    bad_r = [rl[0] for rl in spec["rule_links"] if rl[0] not in _declared]
    bad_s = [rl[1] for rl in spec["rule_links"] if rl[1] not in _srcs]
    check(not bad_r, f"{spec['identity']['form_number']}: rule_links resolve to declared rules",
          f"undefined rules in rule_links: {bad_r}")
    check(not bad_s, f"{spec['identity']['form_number']}: rule_links resolve to declared sources",
          f"undeclared sources in rule_links: {bad_s}")

check(RuleAuthorityLink.objects.count() > 0, "authority links persisted", "no authority links persisted")

# ⚠ The loader must REFUSE an unresolvable referenced source -- the very defect
# this spec exists to fix. Prove the check bites.
_saved_refs = OR.EXISTING_SOURCES_TO_REFERENCE
# Second proof of the same guard, this time with a code that could never exist.
OR.EXISTING_SOURCES_TO_REFERENCE = ["OR_DOES_NOT_EXIST"]
try:
    call_command("load_or_shared_schedules", verbosity=0)
    FAILURES.append("⚠ the loader ACCEPTED an unresolvable source code -- dangling refs can still ship")
except CommandError as exc:
    check("DANGLING REFERENCE" in str(exc),
          "⚠ the loader REFUSES an unresolvable source code, naming the D-25/O4 defect",
          f"refused, but without naming the defect: {str(exc)[:120]!r}")
OR.EXISTING_SOURCES_TO_REFERENCE = _saved_refs

# ======================================================================
# 3. ARITHMETIC ORACLES -- through the loader's own helpers
# ======================================================================
check(OR._yk(OR.OR_APPORT_DECIMALS) == 4,
      "the apportionment percentage rounds to FOUR decimal places",
      f"wrong precision: {OR.OR_APPORT_DECIMALS}")

check(approx(OR._or_single_sales_factor(1234567, 10000000), 12.3457),
      "standard: (1,234,567/10,000,000) x 100 = 12.3457 at four decimals",
      "standard single sales factor arithmetic wrong")
check(approx(OR._or_single_sales_factor(4000000, 4000000), 100.0),
      "standard: an all-Oregon filer computes exactly 100.0000",
      "the all-Oregon case is wrong")
check(OR._or_single_sales_factor(500000, 0) is None,
      "standard: a ZERO denominator yields NO factor (None), never a substitute",
      "a zero denominator produced a factor -- silent substitution")
check(OR._or_single_sales_factor(500000, None) is None,
      "standard: a MISSING denominator yields NO factor",
      "a missing denominator produced a factor")

# ⚠⚠ The alternative worksheet's LIVE divisor -- the trap.
_all_live = [(200000, 1000000), (300000, 1000000), (400000, 2000000), (400000, 2000000)]
check(approx(OR._or_alternative_apportionment(_all_live), 22.5),
      "alternative: all four factors live -> (20+30+20+20)/4 = 22.5000",
      f"alternative all-live wrong: {OR._or_alternative_apportionment(_all_live)}")

_prop_missing = [(0, 0), (300000, 1000000), (400000, 2000000), (400000, 2000000)]
_got = OR._or_alternative_apportionment(_prop_missing)
check(approx(_got, 23.3333),
      "⚠⚠ alternative: a factor with NO 'everywhere' drops from BOTH sides -> (30+20+20)/3 = 23.3333",
      f"THE LIVE-DIVISOR RULE IS BROKEN: got {_got}, want 23.3333")
check(not approx(_got, 17.5),
      "⚠ the divisor is NOT hard-coded to 4 (which would give 17.5000 and overstate Oregon income)",
      "the alternative divisor behaves like the constant 4 -- worksheet line 6 was ignored")
check(OR._or_alternative_apportionment([(0, 0), (0, 0), (0, 0), (0, 0)]) is None,
      "alternative: no live factors at all yields None, not a divide-by-zero",
      "the all-empty alternative case is wrong")

# TY-keying must refuse an unverified year.
try:
    OR._yk(OR.OR_APPORT_DECIMALS, 2026)
    FAILURES.append("_yk returned a TY2026 value that was never verified")
except CommandError:
    PASSES.append("_yk REFUSES an unverified tax year")

# ======================================================================
# 4. The rulings are ENCODED, not assumed
# ======================================================================
# Form-gating: C and E are unavailable to OR-20-S.
for sec in ("A", "B", "D"):
    check(OR._asc_section_allowed(sec, "OR_20_S"),
          f"Section {sec} IS available to OR-20-S", f"Section {sec} wrongly gated from OR-20-S")
for sec in ("C", "E"):
    check(not OR._asc_section_allowed(sec, "OR_20_S"),
          f"⚠ Section {sec} is correctly GATED AWAY from OR-20-S",
          f"Section {sec} is available to OR-20-S -- the form-gating is broken")
    check(OR._asc_section_allowed(sec, "OR_20"),
          f"Section {sec} IS available to OR-20", f"Section {sec} wrongly gated from OR-20")
check(all(OR._asc_section_allowed(s, "OR_20") for s in "ABCDE"),
      "OR-20 is the ONLY corporate form using all five sections",
      "OR-20 cannot use all five sections")
try:
    OR._asc_section_allowed("F", "OR_20")
    FAILURES.append("_asc_section_allowed accepted a non-existent section 'F'")
except CommandError:
    PASSES.append("_asc_section_allowed REFUSES an unknown section")

# The four Appendix A namespaces, and the union.
check(OR.ASC_APPENDIX_A_COUNTS == {"OR_20": 93, "OR_20_INC": 90, "OR_20_INS": 62, "OR_20_S": 50},
      "the FOUR Appendix A code counts are 93/90/62/50 as re-counted positionally",
      f"Appendix A counts wrong: {OR.ASC_APPENDIX_A_COUNTS}")
check(OR.ASC_CODE_UNION == 105, "the code union is 105", f"union wrong: {OR.ASC_CODE_UNION}")
check(OR.ASC_APPENDIX_A_COUNTS["OR_20"] > OR.ASC_APPENDIX_A_COUNTS["OR_20_S"],
      "OR-20's list is larger than OR-20-S's -- and is NOT a subset of anything",
      "the OR-20 / OR-20-S relationship is wrong")

_text = " ".join([d["message"] + d["title"] for d in _all_diag]
                 + [r["description"] + r["title"] for r in _all_rules]
                 + [a["description"] for a in _all_assert])

for label, needle in (
    ("the live divisor is stated, not the constant 4", "LIVE"),
    ("the Schedule-SM inertness is recorded", "Schedule SM"),
    ("the forest-products orphan is recorded (U9)", "forest-products"),
    ("Section D's expiry ordering is recorded", "expire"),
    ("the enter-each-code-once rule is recorded", "only once"),
):
    check(needle.lower() in _text.lower(), label, f"MISSING from the spec text: {label}")

check("D_ORASC_S_NO_C_OR_E" in [d["diagnostic_id"] for d in _all_diag],
      "OR-20-S's C/E gating has a hard diagnostic",
      "no diagnostic enforces the OR-20-S C/E gating")
check("D_ORAP_NO_DENOMINATOR" in [d["diagnostic_id"] for d in _all_diag],
      "the missing-denominator case has a hard diagnostic",
      "no diagnostic for a missing apportionment denominator")

# G4 -- namespaced BY SECTION, never by a consuming form's line numbers.
_asc_lines = [l["line_number"] for s in OR.FORMS if s["identity"]["form_number"] == "OR_ASC_CORP"
              for l in s["lines"]]
check(all(l.startswith("ASC-") for l in _asc_lines),
      "G4: OR_ASC_CORP lines are namespaced BY SECTION (ASC-A..ASC-E), not by a consumer's line numbers",
      f"G4 violation -- a consuming form's line numbering leaked in: {_asc_lines}")
_ap_lines = [l["line_number"] for s in OR.FORMS if s["identity"]["form_number"] == "OR_AP"
             for l in s["lines"]]
check(all(l.startswith("AP-") for l in _ap_lines),
      "G4: OR_AP lines are namespaced AP-<part>-<line> off the OR-AP face",
      f"G4 violation in OR_AP lines: {_ap_lines}")

# ======================================================================
# 4b. The consolidation: excerpts land on the SURVIVING sources
# ----------------------------------------------------------------------
# An earlier version of this loader created OR_2025_SCH_AP / OR_2025_SCH_ASC_C
# alongside the pre-existing OR_2025_SCH_OR_AP / OR_2025_SCH_ASC_CORP - two
# records for one document. The campaign rule is EXTEND, DON'T DUPLICATE. These
# checks pin that the loader now references the survivors and still contributes
# its derived verbatim text to them.
# ======================================================================
check("OR_2025_SCH_OR_AP" in OR.EXISTING_SOURCES_TO_REFERENCE
      and "OR_2025_SCH_ASC_CORP" in OR.EXISTING_SOURCES_TO_REFERENCE,
      "the loader REFERENCES the pre-existing OR-AP / OR-ASC-CORP sources",
      "the loader does not reference the surviving source codes")
_declared_codes = {x["source_code"] for x in OR.AUTHORITY_SOURCES}
check("OR_2025_SCH_AP" not in _declared_codes and "OR_2025_SCH_ASC_C" not in _declared_codes,
      "the duplicate source codes are no longer declared - they cannot be recreated",
      "the loader still declares the duplicate source codes")
check(len(OR.EXCERPTS_FOR_EXISTING) == 2,
      "the verbatim excerpts derived this pass attach to the SURVIVING sources, not lost with the duplicates",
      f"expected 2 excerpts for existing sources, found {len(OR.EXCERPTS_FOR_EXISTING)}")
for _code, _exc in OR.EXCERPTS_FOR_EXISTING:
    _n = AuthorityExcerpt.objects.filter(
        authority_source__source_code=_code, excerpt_label=_exc["excerpt_label"]).count()
    check(_n == 1, f"{_code}: the derived excerpt is attached exactly once",
          f"{_code}: derived excerpt attached {_n} times")

# ======================================================================
# 5. Report
# ======================================================================
print("\n" + "=" * 74)
for fn in ("OR_AP", "OR_ASC_CORP"):
    f = TaxForm.objects.filter(form_number=fn).first()
    if f:
        print(f"  {fn}: facts {FormFact.objects.filter(tax_form=f).count()} / "
              f"rules {FormRule.objects.filter(tax_form=f).count()} / "
              f"lines {FormLine.objects.filter(tax_form=f).count()} / "
              f"diag {FormDiagnostic.objects.filter(tax_form=f).count()} / "
              f"tests {TestScenario.objects.filter(tax_form=f).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-OR').count()}")
print(f"  authority sources (OR): {AuthoritySource.objects.filter(jurisdiction_code='OR').count()}")
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
