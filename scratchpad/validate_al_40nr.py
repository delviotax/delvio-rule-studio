"""Throwaway-SQLite validation for AL_FORM_40NR (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name.

Everything that matters is PROVED, not asserted - each check shows the WRONG answer
differs, which is the only way a reader can tell the rule was necessary:
  * the tax table reproduces THREE independently known figures (two printed in the
    booklet, one from a real filed return)
  * Head of Family is in the SINGLE column - proved by tax(hof) == tax(single) != tax(mfj)
  * the encoded standard-deduction bands are contiguous and non-overlapping, and the
    chart AS PRINTED is proved AMBIGUOUS at an ordinary AGI
  * the corrected MFJ band is the one that makes the ladder step uniformly by $175
  * the line-10 loss floor - the unfloored value is proved NEGATIVE
  * a real filed return, reconstructed line by line, footing to the filed $174 tax
  * ...and the SAME return with retirement correctly in column B, proving the whole
    cascade moves together and the tax nearly doubles
  * A1's two methods proved identical in one case and divergent in another
  * Alabama multiplies by the PRINTED (2dp) percentage - proved by a $1 difference
    against the filed Schedule A figure

⚠⚠ The two-writers guard here is the HARDENED version (every module in the commands
directory, both quote styles) - the older `load_*.py` + double-quote pattern cannot
see `_state_conformity_tier1.py`, which owns real AuthoritySource rows.

Run:  .venv/Scripts/python.exe scratchpad/validate_al_40nr.py
"""
import io as io2
import math
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_al_40nr.sqlite3")
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
from specs.management.commands import load_al_40nr as AL  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []
COMMANDS_DIR = os.path.join(PROJECT_ROOT, "specs", "management", "commands")


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.01):
    return a is not None and abs(float(a) - float(b)) <= tol


def declares_source(text, code):
    """⚠ Both quote styles - `_state_conformity_tier1.py` uses single quotes."""
    return bool(re.search(r"""['"]source_code['"]\s*:\s*['"]%s['"]""" % re.escape(code), text))


call_command("migrate", run_syncdb=True, verbosity=0)

# ⚠ PREREQUISITE: this spec REFERENCES four rows the seeded AL resident/entity
# loaders OWN. Seed the owners first so the harness proves the references RESOLVE
# rather than merely that they are spelled plausibly.
for _prereq in ("load_al_form40", "load_al_form20c", "load_al_passthrough"):
    try:
        call_command(_prereq, verbosity=0)
    except Exception as exc:  # noqa: BLE001
        print(f"  (prerequisite {_prereq}: {type(exc).__name__})")

# ======================================================================
# 0. THE SEED GUARD - pinned to the GATE MECHANISM, not the sentinel value
# ======================================================================
check(AL.READY_TO_SEED is False, "READY_TO_SEED ships as False (D-32 closed the WALK, not the seed gate)",
      f"⚠⚠ READY_TO_SEED SHIPPED AS {AL.READY_TO_SEED!r} - would seed without Ken's gate")

AL.READY_TO_SEED = False
try:
    call_command("load_al_40nr", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

AL.READY_TO_SEED = True
_saved = AL.FLOW_ASSERTIONS
AL.FLOW_ASSERTIONS = []
try:
    call_command("load_al_40nr", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
AL.FLOW_ASSERTIONS = _saved

try:
    call_command("load_al_40nr", verbosity=0)
    PASSES.append("load_al_40nr ran + seeded into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_al_40nr raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields (D-17 - Postgres-only failures)
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in AL.F_RULES]),
    (FormRule, "title", [r["title"] for r in AL.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in AL.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in AL.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in AL.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in AL.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in AL.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in AL.F_FACTS]),
    (FormFact, "label", [f["label"] for f in AL.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in AL.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in AL.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in AL.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in AL.AUTHORITY_SOURCES]),
    (AuthoritySource, "title", [s["title"] for s in AL.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in AL.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structure, dangling references, HARDENED two-writers guard
# ======================================================================
form = TaxForm.objects.filter(form_number="AL_FORM_40NR").first()
check(form is not None, "AL_FORM_40NR exists", "AL_FORM_40NR was not created")
if form:
    check(form.jurisdiction == "AL" and form.tax_year == 2025, "identity: AL / TY2025", "identity wrong")
    check(form.entity_types == ["1040"], "entity_types == ['1040']", f"wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in AL.F_RULES]),
                      ("line_number", [l["line_number"] for l in AL.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in AL.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in AL.F_DIAGNOSTICS]),
                      ("scenario_name", [s["scenario_name"] for s in AL.F_SCENARIOS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in AL.F_RULES}
_cited = {rl[0] for rl in AL.F_RULE_LINKS}
check(not sorted(_declared - _cited), "every FormRule carries at least one authority link",
      f"uncitable rules: {sorted(_declared - _cited)}")
check(not sorted(_cited - _declared), "every authority link names a declared rule",
      f"⚠ DANGLING RULE REFERENCE: {sorted(_cited - _declared)}")

_universe = {s["source_code"] for s in AL.AUTHORITY_SOURCES} | set(AL.EXISTING_SOURCES_TO_REFERENCE)
check(not ({rl[1] for rl in AL.F_RULE_LINKS} - _universe), "every rule link resolves",
      f"⚠ DANGLING SOURCE: {sorted({rl[1] for rl in AL.F_RULE_LINKS} - _universe)}")
check(not ({fl[0] for fl in AL.AUTHORITY_FORM_LINKS} - _universe), "every form link resolves",
      f"⚠ DANGLING SOURCE in form links: "
      f"{sorted({fl[0] for fl in AL.AUTHORITY_FORM_LINKS} - _universe)}")

_declared_here = {s["source_code"] for s in AL.AUTHORITY_SOURCES}
_clashes, _owners = [], {}
for _name in os.listdir(COMMANDS_DIR):
    if not _name.endswith(".py") or _name == "load_al_40nr.py":
        continue
    _text = io2.open(os.path.join(COMMANDS_DIR, _name), encoding="utf-8").read()
    for _c in _declared_here:
        if declares_source(_text, _c):
            _clashes.append((_c, _name))
    for _c in AL.EXISTING_SOURCES_TO_REFERENCE:
        if declares_source(_text, _c):
            _owners.setdefault(_c, []).append(_name)
check(not _clashes,
      "⚠⚠ TWO-WRITERS GUARD (hardened): no source declared here is declared by any other module",
      f"TWO WRITERS OF ONE ROW: {_clashes}")
_orphans = [c for c in AL.EXISTING_SOURCES_TO_REFERENCE if c not in _owners]
check(not _orphans, "every referenced source is genuinely owned by another module",
      f"⚠ referenced but owned by NOTHING: {_orphans}")
_multi = {c: m for c, m in _owners.items() if len(m) > 1}
check(not _multi, "no referenced source has two owners", f"⚠ DUPLICATE OWNERSHIP: {_multi}")

# ======================================================================
# 3. THE TAX TABLE - pinned against THREE independently known figures
# ======================================================================
check(AL._al_tax(23050, "single") == 1113,
      "the tax table reproduces its own PRINTED 1,113 for single at the 23,000-23,100 band",
      f"got {AL._al_tax(23050, 'single')}, the booklet prints 1,113")
check(AL._al_tax(23050, "mfj") == 1073,
      "...and the PRINTED 1,073 for married filing jointly on the same band",
      f"got {AL._al_tax(23050, 'mfj')}, the booklet prints 1,073")
check(AL._al_tax(4853, "mfj") == 174,
      "...and 174 on a REAL FILED RETURN's taxable income of 4,853",
      f"got {AL._al_tax(4853, 'mfj')}, the filed return shows 174")

# ⚠⚠ HEAD OF FAMILY IS IN THE SINGLE COLUMN
_hof, _sgl, _mfj = AL._al_tax(23050, "hof"), AL._al_tax(23050, "single"), AL._al_tax(23050, "mfj")
check(_hof == _sgl and _hof != _mfj,
      "⚠⚠ PROVED: Head of Family takes the SINGLE column (%d), NOT the married one (%d) - a "
      "$%d difference on this fixture, despite HOF taking the MFJ-sized $3,000 exemption"
      % (_hof, _mfj, _sgl - _mfj),
      f"HOF={_hof} single={_sgl} mfj={_mfj} - HOF must equal single and differ from mfj")
check(AL.AL_TAX_COLUMN["hof"] == "single_mfs_hof",
      "the HOF column mapping is explicit in a constant, so it cannot be 'tidied' into mfj",
      "HOF is not mapped to the single column")

# over $100,000 uses the PUBLISHED constants
check(approx(AL._al_tax(150000, "single"), 7458.0),
      "over $100,000: (150,000-100,000) x .05 + 4,958.00 = 7,458", f"got {AL._al_tax(150000, 'single')}")
check(approx(AL._al_tax(150000, "mfj"), 7418.0),
      "...and + 4,918.00 = 7,418 for MFJ", f"got {AL._al_tax(150000, 'mfj')}")
_derived_single = 10 + 100 + 0.05 * (150000 - 3000)
check(abs(AL._al_tax(150000, "single") - _derived_single) > 1.0,
      "⚠ PROVED: a DERIVED bracket formula gives %.0f, not the published 7,458 - the worksheet "
      "constants carry the table's own mid-band convention and must be used as published"
      % _derived_single,
      "the derived formula agrees with the published constant - the caution would be moot")

# ======================================================================
# 4. ⚠⚠ U9 - THE DEFECTIVE CHART
# ======================================================================
for status in AL.FILING_STATUSES:
    bands = AL._yk(AL.AL_STANDARD_DEDUCTION)[status]
    gaps = []
    for (lo1, hi1, _a1), (lo2, _hi2, _a2) in zip(bands, bands[1:]):
        if hi1 is None or lo2 != hi1 + 1:
            gaps.append((hi1, lo2))
    check(not gaps, f"{status}: bands are contiguous and non-overlapping",
          f"⚠ {status}: band boundary defect at {gaps}")
    check(bands[0][0] == 0 and bands[-1][1] is None, f"{status}: bands are exhaustive (0 -> open top)",
          f"{status}: bands do not cover the whole range")

_mfj_bands = AL._yk(AL.AL_STANDARD_DEDUCTION)["mfj"]
check(_mfj_bands[2][0] == 26500,
      "⚠⚠ U9: the encoded MFJ band 3 starts at $26,500, not the $25,500 the DOR chart PRINTS",
      f"MFJ band 3 starts at {_mfj_bands[2][0]}")
_steps = {_mfj_bands[i][2] - _mfj_bands[i + 1][2] for i in range(1, len(_mfj_bands) - 2)}
check(_steps == {175},
      "⚠⚠ PROVED the correction is the right one: with $26,500 the MFJ ladder steps UNIFORMLY by "
      "$175 throughout. The printed $25,500 breaks that uniformity, which is corroborating "
      "evidence independent of the withholding booklet.",
      f"the MFJ ladder does not step uniformly: {sorted(_steps)}")

# ⚠ The chart AS PRINTED is genuinely AMBIGUOUS at an ordinary figure.
_printed_lo, _printed_hi, _printed_amt = AL.AL_MFJ_BAND3_AS_PRINTED
_agi = 25700
_band1 = _mfj_bands[0]
check(_band1[0] <= _agi <= _band1[1] and _printed_lo <= _agi <= _printed_hi,
      "⚠⚠ PROVED the defect is real: an AGI of $25,700 falls in BOTH printed band 1 ($8,500) AND "
      "printed band 3 ($8,150) - an ambiguous lookup on an ordinary figure, not an exotic edge case",
      "the printed bands do not actually overlap at 25,700 - re-check the transcription")
check(AL._al_standard_deduction("mfj", 25700) == 8500.0,
      "...and the ENCODED chart returns a single answer, $8,500", "the encoded chart is ambiguous")
check("WITHHOLDING" in AL.AL_U9_DEFECT_NOTE.upper() and "40-18-15" in AL.AL_U9_DEFECT_NOTE,
      "the defect note records BOTH the resolving source and the statutory threshold it duplicates",
      "the defect note does not record how it was resolved")

# spot-check the other three statuses against the printed values
for status, agi, expect in (("mfs", 13300, 4074.0), ("hof", 26700, 4930.0),
                            ("single", 26700, 2950.0), ("mfj", 36000, 5000.0),
                            ("single", 36000, 2500.0)):
    got = AL._al_standard_deduction(status, agi)
    check(approx(got, expect), f"{status} at AGI {agi:,} -> ${expect:,.0f}", f"{status} {agi} gave {got}")

# dependent chart boundaries
for agi, expect in ((50000, 1000.0), (50001, 500.0), (100000, 500.0), (100001, 300.0)):
    got = AL._al_dependent_exemption(agi, 1)
    check(approx(got, expect), f"dependent chart at {agi:,} -> ${expect:,.0f}", f"{agi} gave {got}")

# ======================================================================
# 5. ⚠ LINE 10 - three branches, and the unfloored value is NEGATIVE
# ======================================================================
check(approx(AL._al_line10(17138, 39693), 0.4317638, 1e-6), "ordinary case: C / B", "wrong")
check(approx(AL._al_line10(70000, 60000), 1.0), "capped at 100% when C exceeds B", "wrong")
_floored = AL._al_line10(-8000, 60000)
_unfloored = AL._al_line10_without_floor(-8000, 60000)
check(approx(_floored, 0.0), "⚠ A3: an Alabama loss floors line 10 at 0%", f"got {_floored}")
check(_unfloored < 0,
      "⚠ A3 PROVED: without the booklet's floor the percentage is %.4f - NEGATIVE - and it then "
      "multiplies the personal exemption, the dependent exemption, the federal-tax deduction and "
      "the standard or itemized deduction, turning four deductions into additions" % _unfloored,
      "the unfloored value is not negative - pick a fixture where it is")
check("ONE AUTHORITY" in AL.AL_LINE10_FLOOR_AUTHORITY.upper(),
      "the floor constant records that it rests on a single authority",
      "the single-authority basis is not recorded")

# ======================================================================
# 6. ⚠⚠ THE ROUNDING RULE, established from the filed return
# ======================================================================
_raw = 17138 / 39693
check(approx(AL._al_round_line10(_raw), 0.4318, 1e-9),
      "line 10 rounds to the printed two decimals: 43.17638%% -> 43.18%%", "rounding is wrong")
_rounded_result = AL._al_prorate(21559, _raw)
_raw_result = math.floor(21559 * _raw + 0.5)
check(_rounded_result == 9309,
      "⚠⚠ Schedule A: 21,559 at the PRINTED percentage gives 9,309 - the filed figure",
      f"got {_rounded_result}, the filed return shows 9,309")
check(_raw_result == 9308 and _raw_result != _rounded_result,
      "⚠⚠ PROVED: full precision gives %d, the printed percentage gives %d, and the FILED return "
      "shows 9,309. Alabama multiplies by the printed figure - a rule stated nowhere, recovered "
      "by reconstruction, worth $1 per prorated line on every itemizing nonresident return"
      % (_raw_result, _rounded_result),
      "full precision and the printed percentage agree here - the rule would be unprovable")

# ======================================================================
# 7. ⚠⚠ THE REAL FILED RETURN - reconstructed, then CORRECTED
# ======================================================================
def rebuild(col_b_extra=0):
    col_b = 46511 - 6818 + col_b_extra          # line 9 col B
    col_c = 23956 - 6818                        # line 9 col C
    pct = AL._al_line10(col_c, col_b)
    sched_a = AL._al_prorate(21559, pct)
    fit = AL._al_prorate(3894, pct)
    exemption = AL._al_prorate(3000, pct)
    deductions = sched_a + fit + exemption
    taxable = col_c - deductions
    return {"colB": col_b, "colC": col_c, "pct": AL._al_round_line10(pct), "schedA": sched_a,
            "fit": fit, "exemption": exemption, "deductions": deductions,
            "taxable": taxable, "tax": AL._al_tax(taxable, "mfj")}


filed = rebuild()
for k, want in (("colB", 39693), ("colC", 17138), ("schedA", 9309), ("fit", 1681),
                ("exemption", 1295), ("deductions", 12285), ("taxable", 4853), ("tax", 174)):
    check(filed[k] == want, f"filed return: {k} = {want:,} (matches the return as filed)",
          f"filed return: {k} came out {filed[k]}, the return shows {want}")
check(approx(filed["pct"], 0.4318, 1e-9), "filed return: line 10 = 43.18%", f"got {filed['pct']}")

corrected = rebuild(col_b_extra=16214)
check(corrected["colB"] == 55907 and approx(corrected["pct"], 0.3065, 1e-9),
      "corrected: column B 39,693 -> 55,907 and the percentage 43.18% -> 30.65%",
      f"corrected gave colB={corrected['colB']} pct={corrected['pct']}")
_moved = [k for k in ("schedA", "fit", "exemption") if corrected[k] != filed[k]]
check(len(_moved) == 3,
      "⚠⚠ PROVED THE WHOLE CASCADE MOVES: the itemized deduction (%d->%d), the federal-tax "
      "deduction (%d->%d) AND the personal exemption (%d->%d) all shrink together - which is "
      "exactly why the filed error is invisible: the return still foots perfectly"
      % (filed["schedA"], corrected["schedA"], filed["fit"], corrected["fit"],
         filed["exemption"], corrected["exemption"]),
      f"only {_moved} moved - the cascade is not propagating")
check(corrected["tax"] == 343,
      "⚠⚠ corrected tax = 343 against the filed 174 - very nearly DOUBLE, on retirement income "
      "Alabama never taxes at all", f"corrected tax came out {corrected['tax']}, expected 343")
check(corrected["taxable"] > filed["taxable"],
      "⚠ the error ran AGAINST the client: leaving retirement out of column B UNDERSTATED the tax",
      "the correction did not increase the tax - re-check the direction")

# the categorical rule itself
_b, _c = AL._al_retirement_columns(16214, taxable_to_an_alabama_resident=True)
check(_b == 16214 and _c == 0,
      "⚠⚠ retirement: column B carries it, column C is ZERO", f"got colB={_b} colC={_c}")
_b2, _c2 = AL._al_retirement_columns(16214, taxable_to_an_alabama_resident=False)
check(_b2 == 0 and _c2 == 0, "a plan-type-exempt distribution is in NEITHER column", "wrong")
check("out-of-state" in AL.AL_RETIREMENT_INVALID_EXEMPT_REASONS
      and "OS" in AL.AL_RETIREMENT_INVALID_EXEMPT_REASONS,
      "⚠ the INVALID exemption reasons are enumerated, including the 'OS' code found on a real "
      "filed return", "the invalid reasons are not recorded")
check(any("414(j)" in p for p in AL.AL_RETIREMENT_EXEMPT_PLAN_TYPES),
      "the exempt list names IRC § 414(j) - defined BENEFIT, which is why an IRA is not on it",
      "the § 414(j) qualifier is missing from the exempt list")

# ======================================================================
# 8. ⚠ A1 - the two methods, proved identical then divergent
# ======================================================================
_same_form = AL._al_part4_line7_form(30000, 100000, 100000, 40000 / 100000, True)
_same_reg = AL._al_part4_line7_regulation(30000, 100000, 100000, 40000)
check(approx(_same_form, 6000.0) and approx(_same_reg, 6000.0),
      "⚠ A1: form and regulation AGREE (6,000) when federal AGI equals Alabama all-source income",
      f"form={_same_form} reg={_same_reg}")
_diff_form = AL._al_part4_line7_form(30000, 100000, 100000, 40000 / 80000, True)
_diff_reg = AL._al_part4_line7_regulation(30000, 100000, 80000, 40000)
check(approx(_diff_form, 7500.0) and approx(_diff_reg, 6666.67),
      "⚠ A1: they DIVERGE (7,500 vs 6,667) once column B departs from federal AGI",
      f"form={_diff_form} reg={_diff_reg}")
check(abs(_diff_form - _diff_reg) > 0 and abs(_same_form - _same_reg) < 0.01,
      "⚠⚠ A1 PROVED: the divergence is driven ENTIRELY by column B not being federal AGI - which "
      "is the same fact underlying the retirement rule. That is why the walk could only be put "
      "properly once it was quantified.",
      "the A1 divergence does not behave as the ruling describes")
_rev_form = AL._al_part4_line7_form(30000, 100000, 100000, 40000 / 120000, True)
_rev_reg = AL._al_part4_line7_regulation(30000, 100000, 120000, 40000)
check(_rev_form < _rev_reg,
      "⚠ ...and it runs in BOTH directions: where column B EXCEEDS federal AGI the form gives "
      "LESS deduction (%.0f vs %.0f), i.e. MORE Alabama tax" % (_rev_form, _rev_reg),
      "the divergence does not reverse - the ruling's 'both directions' claim is unsupported")
check(AL._al_part4_line7_form(30000, 100000, 100000, 0.5, False) == 15000.0,
      "without the MFS-on-Alabama gate, Part IV lines 1-3 are omitted entirely",
      "the non-MFS branch is wrong")

# ======================================================================
# 9. ⚠⚠ SCHEDULE A - three floors, TWO columns
# ======================================================================
_med = AL._al_medical_floor(12751, 39693)
check(_med == 11163, "medical floors at 4% of COLUMN B, ROUNDED: 12,751 - 1,588 = 11,163",
      f"got {_med}")
_med_wrong = AL._al_medical_floor(12751, 17138)
check(abs(_med - _med_wrong) > 0,
      "⚠⚠ PROVED: flooring medical on COLUMN C instead gives %.0f - overstating the deduction by "
      "%.0f, and the return would still foot" % (_med_wrong, _med_wrong - _med),
      "the two columns give the same medical floor - pick a fixture where they differ")
_sa = AL._al_schedule_a(21559, 0.4318, 5000, 17138, 3000, 17138)
check(approx(_sa["L23"], 9309.0, 1.0), "Schedule A L23 = L21 x L10", f"got {_sa['L23']}")
check(_sa["L24b"] == 1714, "casualty floors at 10% of COLUMN C, rounded (1,714)",
      f"got {_sa['L24b']}")
check(_sa["L28"] == 343, "job expenses floor at 2% of COLUMN C, rounded (343)",
      f"got {_sa['L28']}")
check(approx(_sa["L30"], _sa["L23"] + _sa["L24c"] + _sa["L29"]),
      "⚠ A4: L30 = L23 + L24c + L29 - the Alabama-only blocks enter UNPRORATED", "L30 is wrong")
check(AL.AL_SCHED_A_PRORATED_LINES == (4, 9, 14, 18, 19, 20)
      and 24 in AL.AL_SCHED_A_UNPRORATED_LINES,
      "⚠ A4: the prorated set is lines 4/9/14/18/19/20 - the booklet's 'lines 1 through 20' scope",
      "the proration scope does not match the booklet's line-21 instruction")
check(AL._yk(AL.AL_CASUALTY_PER_EVENT_FLOOR) == 100,
      "the INSTRUCTION-ONLY $100-per-event casualty floor is carried", "the $100 floor is missing")

# ======================================================================
# 10. A2, the vehicle worksheet, Part II, and the federal handoff
# ======================================================================
_p = AL._al_retirement_exclusion(9000, 67)
_s = AL._al_retirement_exclusion(4000, 66)
check(approx(_p, 6000.0) and approx(_s, 4000.0),
      "⚠ A2: capped at $6,000 AND at each taxpayer's own Alabama-taxable retirement",
      f"primary={_p} spouse={_s}")
check(approx(_p + _s, 10000.0) and (_p + _s) > 6000,
      "⚠ A2 PROVED PER TAXPAYER: the couple's total is 10,000; a per-RETURN reading would allow "
      "only 6,000 and overstate the tax", "the per-taxpayer reading is not producing more than 6,000")
check(approx(AL._al_retirement_exclusion(9000, 64), 0.0), "under 65 gets nothing", "age gate wrong")

_v = AL._al_vehicle_loan_interest(4000, 200050, "mfj")
check(approx(_v, 3800.0),
      "⚠ vehicle loan: $50 over the MFJ threshold rounds UP to one full $1,000 step and costs $200",
      f"got {_v}")
check(approx(AL._al_vehicle_loan_interest(4000, 199000, "mfj"), 4000.0),
      "...and below the threshold nothing is lost", "the phase-out fires too early")
check(approx(AL._al_vehicle_loan_interest(15000, 50000, "single"), 10000.0),
      "the deduction is capped at $10,000 before any phase-out", "the cap is wrong")

_amts = {1: 5000, 2: 900, 4: 1200}
check(approx(AL._al_part2_line8(_amts, "B"), 7100.0), "Part II col B sums lines 1-7", "wrong")
check(approx(AL._al_part2_line8(_amts, "C"), 6200.0),
      "⚠ Part II col C OMITS line 2 - 6,200, not 7,100", "col C is not omitting line 2")
check(2 in AL.AL_PART2_SUM_COL_B and 2 not in AL.AL_PART2_SUM_COL_C,
      "the asymmetry is explicit in the constants, not buried in a formula", "the constants are wrong")

check(approx(AL._al_fit_worksheet(2000, 0, 3500, 1000, 0, 0, 0), 0.0),
      "the FIT worksheet floors at zero - never a negative deduction", "the zero floor is missing")
check(approx(AL._al_fit_worksheet(3894, 0, 0, 0, 0, 0, 0), 3894.0),
      "...and passes the tax straight through when there are no refundable credits", "wrong")

_eic = AL.AL_FIT_WORKSHEET_FEDERAL_LINES["eic"]["forms"]
_aoc = AL.AL_FIT_WORKSHEET_FEDERAL_LINES["aoc"]["forms"]
_actc = AL.AL_FIT_WORKSHEET_FEDERAL_LINES["actc"]["forms"]
check("1040-NR" not in _eic and "1040-NR" not in _aoc,
      "⚠⚠ EIC and AOC are sourced from 1040/1040-SR ONLY - Alabama's omission is precision",
      f"1040-NR wrongly included: eic={_eic} aoc={_aoc}")
check("1040-NR" in _actc,
      "...while the ACTC IS taken from 1040-NR, so the restriction is selective, not blanket",
      "the ACTC is not sourced from 1040-NR")
check("1040-C" in AL.AL_1040NR_LINE29_IS and AL.AL_1040NR_HAS_EIC_LINE is False,
      "⚠⚠ the 1040-NR trap is recorded: line 29 is 'Credit for amount paid with Form 1040-C' and "
      "there is no EIC line at all", "the 1040-NR trap is not recorded")

# ======================================================================
# 11. The diagnostics carry the rulings
# ======================================================================
_ids = {d["diagnostic_id"] for d in AL.F_DIAGNOSTICS}
for _need, _why in (("D_AL40NR_RETIREMENT_NOT_IN_COLB", "the column-B retirement defect"),
                    ("D_AL40NR_RETIREMENT_PLAN_TYPE", "plan type, not location"),
                    ("D_AL40NR_LINE10_LOSS", "A3 the zero floor"),
                    ("D_AL40NR_MFS_FIT_DIVERGENCE", "A1 the form/regulation divergence"),
                    ("D_AL40NR_NRA_DENOMINATOR", "the nonresident-alien denominator"),
                    ("D_AL40NR_STD_DEDUCTION_CHART_DEFECT", "U9 the defective chart"),
                    ("D_AL40NR_HOF_TAX_COLUMN", "HOF in the single column"),
                    ("D_AL40NR_SCHEDA_TWO_COLUMNS", "three floors, two columns"),
                    ("D_AL40NR_CASUALTY_PER_EVENT", "the $100-per-event floor"),
                    ("D_AL40NR_PART2_COLC_OMITS_L2", "the Part II asymmetry"),
                    ("D_AL40NR_FEDERAL_1040NR_LINES", "the 1040-NR line-29 trap"),
                    ("D_AL40NR_STD_DED_PRORATED", "the invisible standard-deduction proration"),
                    ("D_AL40NR_DEPENDENT_NARROWER", "the narrower dependent definition"),
                    ("D_AL40NR_VEHICLE_LOAN_ROUNDING", "the always-up rounding"),
                    ("D_AL40NR_ATTACH_FEDERAL_RETURN", "the face's attachment banner")):
    check(_need in _ids, f"diagnostic present for {_why}", f"MISSING diagnostic for {_why}")

for _d in AL.F_DIAGNOSTICS:
    if _d["severity"] == "error":
        check(len(_d["message"]) > 200,
              f"{_d['diagnostic_id']}: the refusal explains itself at length",
              f"{_d['diagnostic_id']}: only {len(_d['message'])} chars - a hard stop that does not "
              "name what it refuses is a dead end for the preparer")

_retire = next(d for d in AL.F_DIAGNOSTICS if d["diagnostic_id"] == "D_AL40NR_RETIREMENT_NOT_IN_COLB")
for _phrase in ("414(j)", "denominator", "foots"):
    check(_phrase in _retire["message"],
          f"the retirement diagnostic explains '{_phrase}'",
          f"the retirement diagnostic omits '{_phrase}' - the preparer needs the MECHANISM, not "
          "just the verdict")

# ======================================================================
# 12. Persisted-row counts
# ======================================================================
if form:
    for _model, _decl, _label in ((FormFact, AL.F_FACTS, "facts"), (FormRule, AL.F_RULES, "rules"),
                                  (FormLine, AL.F_LINES, "lines"),
                                  (FormDiagnostic, AL.F_DIAGNOSTICS, "diagnostics"),
                                  (TestScenario, AL.F_SCENARIOS, "scenarios")):
        _n = _model.objects.filter(tax_form=form).count()
        check(_n == len(_decl), f"{_label}: {_n} rows persisted == {len(_decl)} declared",
              f"{_label}: {_n} persisted but {len(_decl)} declared")
_fa_ids = [a["assertion_id"] for a in AL.FLOW_ASSERTIONS]
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
print(f"AL_FORM_40NR harness: {len(PASSES)} pass / {len(FAILURES)} fail")
print("=" * 78)
sys.exit(1 if FAILURES else 0)
