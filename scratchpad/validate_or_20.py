"""Throwaway-SQLite validation for OR_20 (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name.

Everything that matters is PROVED, not asserted:
  * the statute's bracket and the DOR's base-plus-excess agree ACROSS A RANGE
  * the minimum-tax ladder is exhaustive, non-overlapping, and matches at every boundary
  * a LOSS corporation still owes minimum tax - line 14 is a greater-of, not a floor
  * ⚠⚠ the credit clamp binds at THREE lines: a single end-clamp gives the same TAX
    but destroys carryforward, which is the actual damage
  * ⚠⚠ O1: the bonus add-back is ZERO, and the prong-(a) misreading is shown to cost
    up to sixty points of basis
  * TY2026 REFUSES rather than rolling forward
  * ⚠⚠ the NOL (4)(b) intervening-income rule vs the naive "track what was used" model
  * defect D1 - plus and minus differ by the whole of line 2
  * ⚠⚠ raw string equality fails on a code label that normalised matching passes

⚠⚠ Hardened two-writers guard (every module in the commands directory, both quote
styles). ⚠ This spec deliberately does NOT reuse `load_or_pte.py`'s four
code-collision constants - they describe the 50-code OR-20-S surface and are stale
for OR-20 - and the harness asserts that non-reuse.

Run:  .venv/Scripts/python.exe scratchpad/validate_or_20.py
"""
import io as io2
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_or_20.sqlite3")
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
from sources.models import AuthoritySource, AuthorityTopic  # noqa: E402
from specs.management.commands import load_or_20 as OR  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []
COMMANDS_DIR = os.path.join(PROJECT_ROOT, "specs", "management", "commands")


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.01):
    return a is not None and abs(float(a) - float(b)) <= tol


def declares_source(text, code):
    return bool(re.search(r"""['"]source_code['"]\s*:\s*['"]%s['"]""" % re.escape(code), text))


call_command("migrate", run_syncdb=True, verbosity=0)

# ⚠ PREREQUISITE: OR_20 references seven rows the seeded Oregon PTE loaders own.
# ⚠ `load_state_conformity` owns OR_ORS_317_010_CONFORMITY and OR_ORS_317_301_DEPR -
# the SHARED conformity module again, exactly as in the Colorado work.
for _prereq in ("load_state_conformity", "load_or_pte", "load_or_shared_schedules"):
    try:
        call_command(_prereq, verbosity=0)
    except Exception as exc:  # noqa: BLE001
        print(f"  (prerequisite {_prereq}: {type(exc).__name__})")

# ======================================================================
# 0. THE SEED GUARD
# ======================================================================
check(OR.READY_TO_SEED is False, "READY_TO_SEED ships as False (D-25 closed the WALK, not the seed gate)",
      f"⚠⚠ READY_TO_SEED SHIPPED AS {OR.READY_TO_SEED!r}")

OR.READY_TO_SEED = False
try:
    call_command("load_or_20", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

OR.READY_TO_SEED = True
_saved = OR.FLOW_ASSERTIONS
OR.FLOW_ASSERTIONS = []
try:
    call_command("load_or_20", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
OR.FLOW_ASSERTIONS = _saved

try:
    call_command("load_or_20", verbosity=0)
    PASSES.append("load_or_20 ran + seeded into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_or_20 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields (D-17)
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in OR.F_RULES]),
    (FormRule, "title", [r["title"] for r in OR.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in OR.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in OR.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in OR.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in OR.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in OR.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in OR.F_FACTS]),
    (FormFact, "label", [f["label"] for f in OR.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in OR.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in OR.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in OR.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in OR.AUTHORITY_SOURCES]),
    (AuthoritySource, "title", [s["title"] for s in OR.AUTHORITY_SOURCES]),
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
# 2. Structure, dangling refs, HARDENED two-writers, and the STALE-REUSE guard
# ======================================================================
form = TaxForm.objects.filter(form_number="OR_20").first()
check(form is not None, "OR_20 exists", "OR_20 was not created")
if form:
    check(form.jurisdiction == "OR" and form.tax_year == 2025, "identity: OR / TY2025", "identity wrong")
    check(form.entity_types == ["1120"], "entity_types == ['1120']", f"wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in OR.F_RULES]),
                      ("line_number", [l["line_number"] for l in OR.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in OR.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in OR.F_DIAGNOSTICS]),
                      ("scenario_name", [s["scenario_name"] for s in OR.F_SCENARIOS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in OR.F_RULES}
_cited = {rl[0] for rl in OR.F_RULE_LINKS}
check(not sorted(_declared - _cited), "every FormRule carries an authority link",
      f"uncitable rules: {sorted(_declared - _cited)}")
check(not sorted(_cited - _declared), "every authority link names a declared rule",
      f"⚠ DANGLING RULE REFERENCE: {sorted(_cited - _declared)}")

_universe = {s["source_code"] for s in OR.AUTHORITY_SOURCES} | set(OR.EXISTING_SOURCES_TO_REFERENCE)
check(not ({rl[1] for rl in OR.F_RULE_LINKS} - _universe), "every rule link resolves",
      f"⚠ DANGLING SOURCE: {sorted({rl[1] for rl in OR.F_RULE_LINKS} - _universe)}")
check(not ({fl[0] for fl in OR.AUTHORITY_FORM_LINKS} - _universe), "every form link resolves",
      f"⚠ DANGLING SOURCE in form links: "
      f"{sorted({fl[0] for fl in OR.AUTHORITY_FORM_LINKS} - _universe)}")

_declared_here = {s["source_code"] for s in OR.AUTHORITY_SOURCES}
_clashes, _owners = [], {}
for _name in os.listdir(COMMANDS_DIR):
    if not _name.endswith(".py") or _name == "load_or_20.py":
        continue
    _text = io2.open(os.path.join(COMMANDS_DIR, _name), encoding="utf-8").read()
    for _c in _declared_here:
        if declares_source(_text, _c):
            _clashes.append((_c, _name))
    for _c in OR.EXISTING_SOURCES_TO_REFERENCE:
        if declares_source(_text, _c):
            _owners.setdefault(_c, []).append(_name)
check(not _clashes, "⚠⚠ TWO-WRITERS GUARD (hardened): nothing declared here is declared elsewhere",
      f"TWO WRITERS OF ONE ROW: {_clashes}")
_orphans = [c for c in OR.EXISTING_SOURCES_TO_REFERENCE if c not in _owners]
check(not _orphans, "every referenced source is genuinely owned by another module",
      f"⚠ referenced but owned by NOTHING: {_orphans}")
check(not {c: m for c, m in _owners.items() if len(m) > 1}, "no referenced source has two owners",
      f"⚠ DUPLICATE OWNERSHIP: {ic if (ic := {c: m for c, m in _owners.items() if len(m) > 1}) else ''}")

# ⚠⚠ THE STALE-REUSE GUARD, specific to this form. `load_or_pte.py` carries four
# code-collision constants describing the 50-code OR-20-S surface. Campaign G3
# corrected the like-for-like count to 25 for OR-20 and left those constants as a
# deliberate latent edit. This spec must declare its OWN and import none of them.
_or20_src = io2.open(os.path.join(COMMANDS_DIR, "load_or_20.py"), encoding="utf-8").read()
for _stale in ("OR_SEMANTIC_COLLISIONS", "OR_LABEL_ONLY_COLLISIONS", "OR_COLLIDING_CODES",
               "OR_COLLISION_COUNT"):
    check(not re.search(r"^\s*%s\s*[:=]" % _stale, _or20_src, re.M),
          f"⚠ does NOT redefine `{_stale}` (the stale OR-20-S constant)",
          f"⚠⚠ this spec redefines {_stale} - reusing OR-20-S's collision surface for OR-20")
check(OR._yk(OR.OR20_CODES_HAZARDOUS) == 25,
      "⚠⚠ OR-20's OWN hazard surface is 25 (23 divergent + 2 near-twins), NOT the OR-20-S figure of 12",
      f"hazard surface is {OR._yk(OR.OR20_CODES_HAZARDOUS)}, expected 25")
_pte_src = io2.open(os.path.join(COMMANDS_DIR, "load_or_pte.py"), encoding="utf-8").read()
check("OR_COLLISION_COUNT = 12" in _pte_src,
      "⚠ CONFIRMS the latent edit is still outstanding: load_or_pte.py still says 12. Staged for "
      "Ken, deliberately NOT folded into this work (campaign G3).",
      "load_or_pte.py no longer says 12 - the latent-edit note needs updating")

# ======================================================================
# 3. THE RATE - two statements of one rule, proved to agree ACROSS A RANGE
# ======================================================================
check(approx(OR._or_excise_tax(1000000), 66000.0), "at exactly $1,000,000 the tax is $66,000",
      f"got {OR._or_excise_tax(1000000)}")
check(approx(OR._or_excise_tax(1500000), 104000.0), "$1.5m: 66,000 + 7.6% x 500,000 = 104,000",
      f"got {OR._or_excise_tax(1500000)}")
_mismatch = [ti for ti in (0, 1, 250000, 999999, 1000000, 1000001, 2500000, 40000000)
             if abs(OR._or_excise_tax(ti) - OR._or_excise_tax_dor_form(ti)) > 0.005]
check(not _mismatch,
      "⚠ PROVED across eight points: the statute's BRACKET and the DOR's BASE-PLUS-EXCESS are the "
      "same rule - not assumed from a single figure",
      f"the two formulations disagree at: {_mismatch}")

# ======================================================================
# 4. THE MINIMUM-TAX LADDER
# ======================================================================
for sales, want in ((0, 150), (499999, 150), (500000, 500), (999999, 500), (1000000, 1000),
                    (4999999, 2000), (7000000, 7500), (99999999, 75000), (100000000, 100000),
                    (500000000, 100000)):
    got = OR._or_minimum_tax(sales)
    check(approx(got, want), f"minimum tax at Oregon sales {sales:,} -> ${want:,}",
          f"sales {sales} gave {got}, expected {want}")
_ladder = OR._yk(OR.OR_MINIMUM_TAX_LADDER)
check(len(_ladder) == 12, "the ladder has twelve tiers, matching ORS 317.090(2)(a)(A)-(L)",
      f"the ladder has {len(_ladder)} tiers")
_gaps = [(hi1, lo2) for (lo1, hi1, _t1), (lo2, _hi2, _t2) in zip(_ladder, _ladder[1:])
         if hi1 is None or lo2 != hi1 + 1]
check(not _gaps, "the ladder is contiguous and non-overlapping - same partition as the statute",
      f"⚠ ladder boundary defect at {_gaps}")
check(_ladder[0][0] == 0 and _ladder[-1][1] is None, "the ladder is exhaustive (0 -> open top)",
      "the ladder does not cover the whole range")

# ⚠ A LOSS corporation still owes minimum tax.
_l12, _l13 = OR._or_excise_tax(-400000), OR._or_minimum_tax(8000000)
check(approx(_l12, 0.0) and approx(_l13, 7500.0) and approx(OR._or_line14(_l12, _l13), 7500.0),
      "⚠ PROVED: a LOSS corporation with $8m Oregon sales owes $7,500 - line 14 is a GREATER-OF, so "
      "the minimum tax is a sales-based ALTERNATIVE, not a small-taxpayer floor",
      f"loss case gave L12={_l12} L13={_l13}")
check(OR.OR_MIN_TAX_ONE_PER_RETURN is True and OR._yk(OR.OR_MIN_TAX_APPORTIONABLE_SHORT_YEAR) is False,
      "one minimum tax per RETURN, and not apportionable for a short year",
      "the filing-group / short-year rules are not recorded")

# ======================================================================
# 5. ⚠⚠ THE CREDIT CLAMP - three lines, and what a single end-clamp destroys
# ======================================================================
_r = OR._or_apply_credits(20000, 12000, 9000, 4000)
check(approx(_r["L18"], 8000.0), "L18 = 20,000 - 12,000 = 8,000 (above the floor)", f"got {_r['L18']}")
check(approx(_r["L20"], 4000.0), "L20 = 8,000 - 9,000 clamped up to the 4,000 minimum", f"got {_r['L20']}")
_unclamped = 20000 - 12000 - 9000
check(_unclamped < 0 and _r["L20"] > _unclamped,
      "⚠⚠ PROVED: an unclamped computation yields %d - a NEGATIVE excise tax - where Oregon requires "
      "the 4,000 minimum" % _unclamped,
      "the unclamped result is not negative - pick a fixture where the floor bites")
_wasted = OR._or_credits_wasted(20000, 12000, 9000, 4000)
check(approx(_wasted, 5000.0),
      "⚠⚠ ...and it quantifies the real damage: 5,000 of credit is ABSORBED by the floor. The tax is "
      "right either way; what a single end-clamp destroys is the CARRYFORWARD the DOR's ordering rule "
      "exists to preserve.", f"credits absorbed came out {_wasted}, expected 5,000")
check(OR.OR_MIN_TAX_CLAMPED_LINES == (18, 20, 22),
      "the three clamped lines are recorded explicitly, not folded into one end-clamp",
      f"clamped lines recorded as {OR.OR_MIN_TAX_CLAMPED_LINES}")
check("reduced, paid, or otherwise satisfied" in OR.OR_MIN_TAX_CREDIT_PROOF,
      "the constant carries the DOR's verbatim prohibition", "the verbatim prohibition is not recorded")

# ======================================================================
# 6. ⚠⚠ O1 - DEPRECIATION
# ======================================================================
check(approx(OR._or_bonus_addback(1000000), 0.0),
      "⚠⚠ O1: the TY2025 Oregon bonus add-back is ZERO on a $1m federal bonus", "an add-back was applied")
check(OR._yk(OR.OR_SEC_179_STATE_LIMIT) is None and OR._yk(OR.OR_SEC_179_STATE_PHASEOUT) is None,
      "no state § 179 dollar limit and no state phaseout", "a state § 179 limit is encoded")
check("317.010(7)(b)" in OR.OR_DEPRECIATION_AUTHORITY and "317.312" in OR.OR_DEPRECIATION_AUTHORITY,
      "⚠⚠ the position carries its CITATION and corroboration - an asserted ruling, not an absence",
      "the depreciation position has no authority recorded, which is the class-(b) defect itself")
check("SIXTY POINTS OF BASIS" in OR.OR_DEPRECIATION_PRONG_A_MISREADING.upper(),
      "⚠ the REJECTED prong-(a) reading is recorded with what it would have cost",
      "the rejected reading is not recorded, so a future reader cannot see it was considered")
check(OR.OR_SHARES_BONUS_ADDBACK_WITH_GA is False,
      "⚠⚠ ON THE RECORD (D-25 O1 iii): Oregon does NOT share Georgia's bonus add-back",
      "the no-Georgia-clone ruling is not recorded")
check("2017-12-01" in OR.OR_TY2026_SHADOW_BOOK_BASELINE,
      "the TY2026 shadow-book baseline is recorded, so the engine is switch-ready",
      "the shadow-book baseline is missing")

# ======================================================================
# 7. ⚠⚠ TY2026 REFUSES
# ======================================================================
for _fn, _args in ((OR._or_excise_tax, (500000, 2026)), (OR._or_bonus_addback, (100000, 2026))):
    try:
        _fn(*_args)
        FAILURES.append(f"⚠ {_fn.__name__} computed for TY2026 instead of refusing")
    except CommandError as exc:
        check("SB 1507" in str(exc) and "317.010(7)" in str(exc),
              f"{_fn.__name__} REFUSES TY2026 and names SB 1507 + the amended rule",
              f"unexpected TY2026 message from {_fn.__name__}: {str(exc)[:120]!r}")
check(OR.OR_TY2026_BLOCKED.get(2026) is True and OR.OR_TY2026_BLOCKED.get(2025) is False,
      "the tripwire is keyed by year, blocking 2026 and permitting 2025", "the tripwire keying is wrong")

# ======================================================================
# 8. ⚠⚠ THE NOL - (4)(b) vs the naive model
# ======================================================================
_or_avail = OR._or_nol_available(500000, 2020, 180000, 2025)
_naive = OR._or_nol_available_used_only(500000, 0)
check(approx(_or_avail, 320000.0), "ORS 317.476(4)(b): 500,000 - 180,000 intervening income = 320,000",
      f"got {_or_avail}")
check(_naive > _or_avail,
      "⚠⚠ PROVED: a schedule tracking only amounts USED reports %.0f still available where Oregon "
      "allows %.0f - a %.0f overstatement that survives until the Department adjusts it"
      % (_naive, _or_avail, _naive - _or_avail),
      "the naive model agrees here - pick a fixture with intervening income")
check(approx(OR._or_nol_available(500000, 2008, 0, 2025), 0.0),
      "⚠ a 2008 loss has EXPIRED by 2025 - fifteen years, not indefinite", "the expiry did not fire")
check(approx(OR._or_nol_available(500000, 2011, 0, 2025), 500000.0),
      "...while a 2011 loss is still alive in its fifteenth year", "the expiry fired too early")
check(OR._yk(OR.OR_NOL_80PCT_LIMIT) is None and OR._yk(OR.OR_NOL_CARRYBACK_ALLOWED) is False,
      "⚠ NO 80% limitation and NO carryback - two more ways Oregon is not federal",
      "the 80% cap or carryback flags are wrong")
check("317.346" in OR.OR_NOL_CARRYBACK_EXCEPTION and OR.OR_NOL_REIT_EXCLUDED is True,
      "the agricultural carryback exception and the REIT exclusion are carried",
      "the carryback exception or REIT exclusion is missing")

# ======================================================================
# 9. ⚠ DEFECT D1, consolidation, and the code-label normalisation
# ======================================================================
_plus, _minus = OR._or_line3(800000, 150000), OR._or_line3_as_instructed(800000, 150000)
check(approx(_plus, 950000.0) and approx(_minus, 650000.0) and abs(_plus - _minus) > 0,
      "⚠ D1 PROVED: the face's PLUS gives 950,000 and the instructions' MINUS gives 650,000 - a "
      "300,000 swing, i.e. twice the additions. Three sources say plus; only the OR-20 instructions "
      "say minus.",
      f"D1 fixture did not diverge: plus={_plus} minus={_minus}")

check(OR._or_consolidated_return_required(True, True, True) is True,
      "consolidated required when all three conditions hold", "wrong")
for _args, _why in (((True, False, True), "not unitary"), ((True, True, False), "no Oregon nexus"),
                    ((False, True, True), "no federal consolidation")):
    check(OR._or_consolidated_return_required(*_args) is False,
          f"NOT required when {_why} - all three, not any", f"wrongly required when {_why}")

_corp = "Oregon Cultural Trust contribution (ORS 315.675)"
_indiv = "Oregon Cultural Trust contributions"
check(_corp != _indiv,
      "⚠⚠ raw string equality REJECTS a genuinely identical code label", "the fixture labels match raw")
_cite_only = re.sub(r"\s+", " ", re.sub(r"\(ORS[^)]*\)", " ", _corp)).strip().casefold()
check(_cite_only != _indiv.casefold(),
      "⚠⚠ PROVED THE BRIEF'S OWN REMEDY IS INSUFFICIENT: stripping the ORS citation still leaves "
      "SINGULAR against PLURAL on the very example the brief cites. Normalisation needed a plural "
      "fold added during authoring - which is evidence the next pair will break it differently.",
      "cite-stripping alone reconciled the labels - the plural gap this check exists for is absent")
check(OR._or_normalise_code_label(_corp) == OR._or_normalise_code_label(_indiv),
      "...and the full normaliser (cite + case + whitespace + dash + plural) does reconcile it",
      "normalisation did not reconcile the two labels")
check(OR.OR20_LABEL_MATCHING_IS_AUTHORITATIVE is False
      and "curated" in OR.OR20_LABEL_MATCH_RULE.lower(),
      "⭐ ...and the spec records that an EXPLICIT CURATED MAP governs, with normalisation kept only "
      "as a drift cross-check - the MO-C lesson: an explicit map, never a derived rule",
      "the spec still treats label matching as the authoritative mechanism")
check(len(OR.OR20_SAFE_ROWS_FAILING_STRING_EQUALITY) >= 9,
      f"{len(OR.OR20_SAFE_ROWS_FAILING_STRING_EQUALITY)} 'safe' rows are recorded as failing raw equality",
      "the string-equality failure set is under-recorded")
check(OR.OR20_NEAR_TWIN_CODES == (338, 344), "the two near-twin codes are named", "near-twins wrong")
check(OR._yk(OR.OR20_APPENDIX_A_CODE_COUNT) == 93, "93 Appendix A codes", "code count wrong")

# IC-DISC: two rules, two entity tests
check("domestic international sales corporation" in OR.OR_IC_DISC_RATE_SCOPE
      and "INTEREST CHARGE" in OR.OR_IC_DISC_MIN_TAX_EXEMPT_SCOPE,
      "⚠ the IC-DISC RATE and the minimum-tax EXEMPTION are recorded as separate rules with "
      "different entity tests", "the two IC-DISC rules are bundled")
check("REDUCTION" in OR.OR_FARM_LTCG_DELIVERY.upper(),
      "the farm-liquidation 5% is recorded as a line-11 reduction, never a rate",
      "the farm LTCG delivery mechanism is not recorded")

# ======================================================================
# 10. Diagnostics and persisted rows
# ======================================================================
_ids = {d["diagnostic_id"] for d in OR.F_DIAGNOSTICS}
for _need, _why in (("D_OR20_DEPRECIATION_POSITION", "O1 asserted depreciation"),
                    ("D_OR20_TY2026_STALE", "the SB 1507 tripwire"),
                    ("D_OR20_MIN_TAX_ABSORBS_CREDITS", "credits absorbed by the floor"),
                    ("D_OR20_MIN_TAX_FILING_GROUP", "one minimum tax per return"),
                    ("D_OR20_MIN_TAX_SALES_COUNTERFACTUAL", "the counterfactual sales definition"),
                    ("D_OR20_NOL_INTERVENING_INCOME", "the (4)(b) rule"),
                    ("D_OR20_LINE1_START_POINT", "the five federal start points"),
                    ("D_OR20_IC_DISC_TWO_RULES", "the two IC-DISC rules"),
                    ("D_OR20_LOCAL_TAXES_DEFERRED", "O3 Portland/Multnomah/Metro"),
                    ("D_OR20_CODE_LABEL_MATCHING", "the code namespace"),
                    ("D_OR20_CONSOLIDATED_ALL_THREE", "all three consolidation conditions"),
                    ("D_OR20_FARM_LTCG_IS_A_REDUCTION", "the farm LTCG mechanism")):
    check(_need in _ids, f"diagnostic present for {_why}", f"MISSING diagnostic for {_why}")

for _d in OR.F_DIAGNOSTICS:
    if _d["severity"] == "error":
        check(len(_d["message"]) > 200, f"{_d['diagnostic_id']}: the refusal explains itself at length",
              f"{_d['diagnostic_id']}: only {len(_d['message'])} chars")

_local = next(d for d in OR.F_DIAGNOSTICS if d["diagnostic_id"] == "D_OR20_LOCAL_TAXES_DEFERRED")
check(all(f in _local["message"] for f in ("Portland", "Metro", "Multnomah County Business Income")),
      "⚠ O3's refusal NAMES all three local forms, so the preparer knows what they still owe",
      "the local-tax refusal does not name the three forms")
_depr = next(d for d in OR.F_DIAGNOSTICS if d["diagnostic_id"] == "D_OR20_DEPRECIATION_POSITION")
check("Georgia" in _depr["message"] and "surplusage" in _depr["message"],
      "⚠ the depreciation diagnostic carries BOTH the no-Georgia-clone ruling and the structural "
      "SB 1507 argument - so the reasoning survives without the brief",
      "the depreciation diagnostic omits the reasoning it exists to carry")

if form:
    for _model, _decl, _label in ((FormFact, OR.F_FACTS, "facts"), (FormRule, OR.F_RULES, "rules"),
                                  (FormLine, OR.F_LINES, "lines"),
                                  (FormDiagnostic, OR.F_DIAGNOSTICS, "diagnostics"),
                                  (TestScenario, OR.F_SCENARIOS, "scenarios")):
        _n = _model.objects.filter(tax_form=form).count()
        check(_n == len(_decl), f"{_label}: {_n} rows persisted == {len(_decl)} declared",
              f"{_label}: {_n} persisted but {len(_decl)} declared")
_fa_ids = [a["assertion_id"] for a in OR.FLOW_ASSERTIONS]
_fa_n = FlowAssertion.objects.filter(assertion_id__in=_fa_ids).count()
check(_fa_n == len(_fa_ids), f"flow assertions: {_fa_n} of this spec's {len(_fa_ids)} persisted",
      f"flow assertions: {_fa_n} persisted but {len(_fa_ids)} declared")

# ======================================================================
print("\n" + "=" * 78)
for p in PASSES:
    print(f"  PASS  {p}")
if FAILURES:
    print("\n" + "!" * 78)
    for f in FAILURES:
        print(f"  FAIL  {f}")
print("=" * 78)
print(f"OR_20 harness: {len(PASSES)} pass / {len(FAILURES)} fail")
print("=" * 78)
sys.exit(1 if FAILURES else 0)
