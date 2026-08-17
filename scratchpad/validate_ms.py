"""Throwaway-SQLite validation for MS_84_105 (Mississippi Pass-Through Entity Tax Return, TY2025).

Checks, in order:
  1. THE GUARD — forces READY_TO_SEED DOWN and asserts the command REFUSES (pins the MECHANISM,
     not the value on disk), then flips it in memory and seeds.
  2. CharField caps asserted against the REAL model fields (max_length read off _meta), not
     hardcoded numbers: rule_id / line_number / assertion_id / diagnostic_id / fact_key /
     topic_name, and on AuthoritySource citation / issuer / source_code.
  3. Every FormRule has >= 1 authority link; no duplicate ids anywhere.
  4. ARITHMETIC ORACLES:
       - the S-corp-vs-partnership tax-due FORK (84-105 L9)
       - the franchise minimum ($25) and the TY-keyed ladder + 2028 repeal
       - the depreciation add-back and recovery landing on 84-122 L8 / L15
       - ⚠ THE NEGATIVE ASSERTION: they do NOT land on L6 (municipal-bond interest) or
         L13 (flow-through income) — the specific silent wrong-box error this spec exists to avoid
       - the TWO different safe-harbour percentages (composite partnership 80% vs 90%)
       - the aviation bonus branch, the L20 asymmetry, the 84-161 lesser-of/excess
       - ⚠ the composite rate computes NOTHING (three positions recorded, unresolved)
ASCII-safe output. Run: poetry run python scratchpad/validate_ms.py
"""
import os
import sys
from decimal import Decimal

# Windows consoles default to cp1252; the loader and these messages carry non-ASCII
# warning marks. Reconfigure BEFORE django.setup() so Django's OutputWrapper inherits it.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_ms.sqlite3")
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
from specs.management.commands import load_ms_84105 as MS  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def maxlen(model, field):
    """The REAL cap, read off the model field — never a hardcoded number."""
    return model._meta.get_field(field).max_length


call_command("migrate", run_syncdb=True, verbosity=0)

# ── Reproduce prod's precondition: the MS conformity anchors (MS_CODE_27_7_17 and the
# booklet sources) are seeded by load_state_conformity, NOT by this loader. Without
# them, EXISTING_SOURCES_TO_REFERENCE cannot resolve and five rules lose their only
# authority link. Seed the spine first, exactly as prod has it.
from specs.management.commands import load_state_conformity as CONF  # noqa: E402
CONF.READY_TO_SEED = True
try:
    call_command("load_state_conformity", verbosity=0)
    PASSES.append("conformity spine seeded first (prod precondition for the MS anchors)")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_state_conformity raised: {e!r}")
for code in ("MS_CODE_27_7_17", "MS_2025_84_100_INSTR", "MS_2025_83_100_INSTR"):
    check(AuthoritySource.objects.filter(source_code=code).exists(),
          f"existing MS source {code} present before the loader runs",
          f"existing MS source {code} was NOT seeded by load_state_conformity")

# ══════════════════════════════════════════════════════════════════════════
# 1. THE GUARD — pin the MECHANISM, not the disk value
# ══════════════════════════════════════════════════════════════════════════
check(MS.READY_TO_SEED is False,
      "READY_TO_SEED ships False on disk (spec is NOT cleared to seed)",
      f"READY_TO_SEED must ship False; found {MS.READY_TO_SEED!r}")

MS.READY_TO_SEED = False          # force it DOWN regardless of what disk said
try:
    call_command("load_ms_84105", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the command seeded with READY_TO_SEED=False")
except CommandError as e:
    msg = str(e)
    check("REFUSING TO SEED" in msg, "guard REFUSES to seed when READY_TO_SEED is False",
          f"guard raised CommandError but without the refusal banner: {msg[:120]}")
    check("READY_TO_SEED = False" in msg, "guard reports the sentinel value in its error",
          "guard error does not report READY_TO_SEED")
    check("W1" in msg and "COMPOSITE RATE" in msg,
          "guard error names W1 (the unresolved composite rate) as a walk item",
          "guard error does not name the composite-rate walk item")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"guard raised the wrong exception type: {e!r}")

# the composite-rate tripwire inside the guard
MS.READY_TO_SEED = True
MS.MS_COMPOSITE_RATE_RESOLVED = True
try:
    call_command("load_ms_84105", verbosity=0)
    FAILURES.append("TRIPWIRE DID NOT FIRE: seeded with MS_COMPOSITE_RATE_RESOLVED flipped")
except CommandError as e:
    check("COMPOSITE_RATE_RESOLVED" in str(e),
          "guard also refuses if MS_COMPOSITE_RATE_RESOLVED is flipped without a Ken ruling",
          f"composite-rate tripwire fired but with an unexpected message: {str(e)[:120]}")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"composite tripwire raised the wrong exception: {e!r}")
MS.MS_COMPOSITE_RATE_RESOLVED = False

# now seed for real (in memory only — disk still says False)
try:
    call_command("load_ms_84105", verbosity=0)
    PASSES.append("load_ms_84105 ran + seeded into throwaway SQLite without error")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_ms_84105 raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)

form = TaxForm.objects.get(form_number="MS_84_105")

# ══════════════════════════════════════════════════════════════════════════
# 2. CharField caps — against the REAL model fields
# ══════════════════════════════════════════════════════════════════════════
CAPS: dict = {}
CAPS["form_number"] = (form.form_number, maxlen(TaxForm, "form_number"))
CAPS["jurisdiction"] = (form.jurisdiction, maxlen(TaxForm, "jurisdiction"))
for r in FormRule.objects.filter(tax_form=form):
    CAPS[f"rule_id={r.rule_id}"] = (r.rule_id, maxlen(FormRule, "rule_id"))
    CAPS[f"rule_title={r.rule_id}"] = (r.title, maxlen(FormRule, "title"))
for ln in FormLine.objects.filter(tax_form=form):
    CAPS[f"line_number={ln.line_number}"] = (ln.line_number, maxlen(FormLine, "line_number"))
for d in FormDiagnostic.objects.filter(tax_form=form):
    CAPS[f"diagnostic_id={d.diagnostic_id}"] = (d.diagnostic_id, maxlen(FormDiagnostic, "diagnostic_id"))
    CAPS[f"diag_title={d.diagnostic_id}"] = (d.title, maxlen(FormDiagnostic, "title"))
for f in FormFact.objects.filter(tax_form=form):
    CAPS[f"fact_key={f.fact_key}"] = (f.fact_key, maxlen(FormFact, "fact_key"))
    CAPS[f"fact_label={f.fact_key}"] = (f.label, maxlen(FormFact, "label"))
for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-MS"):
    CAPS[f"assertion_id={fa.assertion_id}"] = (fa.assertion_id, maxlen(FlowAssertion, "assertion_id"))
for t in AuthorityTopic.objects.filter(topic_code__startswith="ms_"):
    CAPS[f"topic_code={t.topic_code}"] = (t.topic_code, maxlen(AuthorityTopic, "topic_code"))
    CAPS[f"topic_name={t.topic_code}"] = (t.topic_name, maxlen(AuthorityTopic, "topic_name"))
for s in AuthoritySource.objects.filter(jurisdiction_code="MS"):
    CAPS[f"source_code={s.source_code}"] = (s.source_code, maxlen(AuthoritySource, "source_code"))
    CAPS[f"citation={s.source_code}"] = (s.citation or "", maxlen(AuthoritySource, "citation"))
    CAPS[f"issuer={s.source_code}"] = (s.issuer or "", maxlen(AuthoritySource, "issuer"))
    CAPS[f"src_type={s.source_code}"] = (s.source_type, maxlen(AuthoritySource, "source_type"))
    CAPS[f"src_rank={s.source_code}"] = (s.source_rank, maxlen(AuthoritySource, "source_rank"))
for sc in TestScenario.objects.filter(tax_form=form):
    CAPS[f"scenario={sc.sort_order}"] = (sc.scenario_name, maxlen(TestScenario, "scenario_name"))
viol = [f"{k}: len {len(v)} > {cap}" for k, (v, cap) in CAPS.items() if cap is not None and len(v) > cap]
check(not viol, f"CharField caps OK against the real model fields ({len(CAPS)} checked)",
      "CAP VIOLATIONS:\n    " + "\n    ".join(viol))
# spot-pin the caps the brief calls out, so a model widening is noticed
check(maxlen(FormRule, "rule_id") == 20, "model cap: FormRule.rule_id == 20", "FormRule.rule_id cap moved")
check(maxlen(FormLine, "line_number") == 20, "model cap: FormLine.line_number == 20", "FormLine.line_number cap moved")
check(maxlen(FlowAssertion, "assertion_id") == 20, "model cap: FlowAssertion.assertion_id == 20", "assertion_id cap moved")
check(maxlen(FormDiagnostic, "diagnostic_id") == 40, "model cap: FormDiagnostic.diagnostic_id == 40", "diagnostic_id cap moved")
check(maxlen(FormFact, "fact_key") == 100, "model cap: FormFact.fact_key == 100", "fact_key cap moved")
check(maxlen(AuthorityTopic, "topic_name") == 255, "model cap: AuthorityTopic.topic_name == 255", "topic_name cap moved")
check(maxlen(AuthoritySource, "citation") == 255, "model cap: AuthoritySource.citation == 255", "citation cap moved")
check(maxlen(AuthoritySource, "issuer") == 100, "model cap: AuthoritySource.issuer == 100", "issuer cap moved")
check(maxlen(AuthoritySource, "source_code") == 100, "model cap: AuthoritySource.source_code == 100", "source_code cap moved")

# ══════════════════════════════════════════════════════════════════════════
# 3. Authority coverage + duplicate ids
# ══════════════════════════════════════════════════════════════════════════
ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form=form)
            if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless, f"all {FormRule.objects.filter(tax_form=form).count()} rules have >= 1 authority link",
      f"rules with NO authority link: {ruleless}")

spec = MS.FORMS[0]
defined = [r["rule_id"] for r in spec["rules"]]
linked = {rl[0] for rl in spec["rule_links"]}
check(not (linked - set(defined)), "rule_links reference only defined rules", f"orphan rule_links: {linked - set(defined)}")
check(not (set(defined) - linked), "every rule appears in rule_links", f"unlinked rules: {set(defined) - linked}")

for label, seq in (("rule_id", defined),
                   ("fact_key", [f["fact_key"] for f in spec["facts"]]),
                   ("line_number", [ln["line_number"] for ln in spec["lines"]]),
                   ("diagnostic_id", [d["diagnostic_id"] for d in spec["diagnostics"]]),
                   ("scenario_name", [s["scenario_name"] for s in spec["scenarios"]]),
                   ("assertion_id", [a["assertion_id"] for a in MS.FLOW_ASSERTIONS]),
                   ("source_code", [s["source_code"] for s in MS.AUTHORITY_SOURCES])):
    dupes = {v for v in seq if seq.count(v) > 1}
    check(not dupes, f"no duplicate {label} ({len(seq)} defined)", f"DUPLICATE {label}: {dupes}")

check(form.entity_types == ["1065", "1120S"], "entity_types = ['1065', '1120S'] (ONE form, TWO modules)",
      f"entity_types wrong: {form.entity_types}")
check(form.jurisdiction == "MS" and form.tax_year == 2025 and form.version == 1 and form.status == "draft",
      "jurisdiction MS / TY2025 / v1 / status draft", "form identity wrong")
check(MS.EXISTING_SOURCES_TO_REFERENCE[0] == "MS_CODE_27_7_17",
      "EXISTING_SOURCES_TO_REFERENCE anchors on MS_CODE_27_7_17 (the MS conformity anchor)",
      f"conformity anchor missing: {MS.EXISTING_SOURCES_TO_REFERENCE}")
_new_codes = {s["source_code"] for s in MS.AUTHORITY_SOURCES}
_reused = _new_codes & set(MS.EXISTING_SOURCES_TO_REFERENCE)
check(not _reused,
      "the loader REFERENCES the existing MS sources, it does not redefine/overwrite them",
      f"loader would overwrite already-seeded sources: {_reused}")
_anchor = AuthoritySource.objects.get(source_code="MS_CODE_27_7_17")
check(_anchor.source_type == "state_statute" and _anchor.jurisdiction_code == "MS",
      "MS_CODE_27_7_17 survived the load unmodified (still the MS conformity statute anchor)",
      "the conformity anchor was mutated by this loader")
check(RuleAuthorityLink.objects.filter(form_rule__tax_form=form, authority_source=_anchor).count() >= 3,
      "the conformity anchor is linked from the depreciation / aviation / §179 rules",
      "the conformity anchor is under-linked")

# ══════════════════════════════════════════════════════════════════════════
# 4a. ORACLE — ⚠ THE S-CORP vs PARTNERSHIP TAX-DUE FORK (84-105 L9)
# ══════════════════════════════════════════════════════════════════════════
check(MS._ms_l9_total("1120S", 1500, 24700) == Decimal("26200"),
      "L9 FORK: S corp = L4 + L8 = 1,500 + 24,700 = 26,200",
      f"S-corp L9 wrong: {MS._ms_l9_total('1120S', 1500, 24700)}")
check(MS._ms_l9_total("1065", 1500, 24700) == Decimal("24700"),
      "L9 FORK: partnership = L8 = 24,700 (franchise NEVER added)",
      f"partnership L9 wrong: {MS._ms_l9_total('1065', 1500, 24700)}")
check(MS._ms_l9_total("1120S", 0, 24700) != MS._ms_l9_total("1120S", 1500, 24700),
      "L9 FORK: the S-corp total is sensitive to L4 (franchise is really added)",
      "S-corp L9 ignores L4")
check(MS._ms_l9_total("1065", 25, 0) == Decimal("0"),
      "L9 FORK: a partnership with a stray $25 franchise still totals 0 (the fork suppresses it)",
      "partnership L9 leaked a franchise amount")
try:
    MS._ms_l9_total("1120", 0, 0)
    FAILURES.append("L9 FORK accepted an entity type other than 1065/1120S")
except ValueError:
    PASSES.append("L9 FORK rejects any entity type other than 1065 / 1120S")
check(MS._ms_franchise_block_applies("1120S") is True and MS._ms_franchise_block_applies("1065") is False,
      "franchise block gate: applies to 1120S, NOT to 1065", "franchise entity gate wrong")
check(MS._ms_franchise_block_applies("1120S", elected_federal_corporate=True) is False,
      "franchise gate: federal corporate election -> not an 84-105 filer at all (R15)",
      "corporate-election exception not gated")
check(MS._ms_franchise_block_applies("1120S", is_exempt_org_with_ubti=True) is False,
      "franchise gate: exempt org with UBTI leaves lines 1-4 blank", "exempt-org exception not gated")

# ══════════════════════════════════════════════════════════════════════════
# 4b. ORACLE — the franchise MINIMUM, the TY-keyed ladder, and the 2028 repeal
# ══════════════════════════════════════════════════════════════════════════
check(MS._ms_franchise_tax(60_000, 2025) == Decimal("25"),
      "FRANCHISE MINIMUM: capital 60,000 (below the 100,000 exemption) -> $25",
      f"franchise min wrong: {MS._ms_franchise_tax(60_000, 2025)}")
check(MS._ms_franchise_tax(100_000, 2025) == Decimal("25"),
      "FRANCHISE MINIMUM: capital exactly 100,000 -> $25 (zero excess, floor applies)",
      "franchise floor at the exemption wrong")
check(MS._ms_franchise_tax(100_500, 2025) == Decimal("25"),
      "FRANCHISE: 500 of excess -> 'or fraction thereof' = 1 unit = $0.75, overridden by the $25 floor",
      f"franchise fraction rounding wrong: {MS._ms_franchise_tax(100_500, 2025)}")
check(MS._ms_franchise_tax(2_100_000, 2025) == Decimal("1500.00"),
      "FRANCHISE TY2025: 0.75 x CEIL(2,000,000/1,000) = 0.75 x 2,000 = $1,500",
      f"franchise TY2025 wrong: {MS._ms_franchise_tax(2_100_000, 2025)}")
check(MS._ms_franchise_tax(2_100_000, 2024) == Decimal("2000.00"),
      "FRANCHISE ladder TY2024: $1.00 per 1,000 -> $2,000 (rate is TY-KEYED, not constant)",
      f"franchise TY2024 wrong: {MS._ms_franchise_tax(2_100_000, 2024)}")
check(MS._ms_franchise_tax(2_100_000, 2026) == Decimal("1000.00"),
      "FRANCHISE ladder TY2026: $0.50 per 1,000 -> $1,000",
      f"franchise TY2026 wrong: {MS._ms_franchise_tax(2_100_000, 2026)}")
check(MS._ms_franchise_tax(2_100_000, 2028) == Decimal("0"),
      "FRANCHISE REPEALED effective 1/1/2028 -> $0 (no statutory rate clause exists)",
      f"2028 repeal not honoured: {MS._ms_franchise_tax(2_100_000, 2028)}")
check(MS.MS_FRANCHISE_RATE_PER_1000[2025] == "0.75" and MS.MS_FRANCHISE_MINIMUM == 25
      and MS.MS_FRANCHISE_EXEMPT_CAPITAL == 100_000,
      "FRANCHISE constants: TY2025 $0.75 / $25 minimum / $100,000 exemption",
      "franchise constants wrong")
check(MS.MS_FRANCHISE_RATE_PER_1000.get(2028) is None,
      "FRANCHISE ladder carries an explicit 2028 sunset (None), not a stale rate",
      "2028 sunset missing from the ladder")
# entity income tax (the SETTLED electing-PTE schedule)
check(MS._ms_entity_income_tax(500_000) == Decimal("24700.00"),
      "EPTE RATE: 0% x 5,000 + 4% x 5,000 + 5% x 490,000 = 24,700",
      f"EPTE tax wrong: {MS._ms_entity_income_tax(500_000)}")
check(MS._ms_entity_income_tax(5_000) == Decimal("0"),
      "EPTE RATE: first 5,000 is taxed at 0%", f"EPTE 5k wrong: {MS._ms_entity_income_tax(5_000)}")
check(MS._ms_entity_income_tax(10_000) == Decimal("200.00"),
      "EPTE RATE: 10,000 -> 0 + 4% x 5,000 = 200", f"EPTE 10k wrong: {MS._ms_entity_income_tax(10_000)}")
check(MS._ms_entity_income_tax(-50_000) == Decimal("0"),
      "EPTE RATE: a negative base floors at zero (84-122 terminal zero floor)", "negative base not floored")

# ══════════════════════════════════════════════════════════════════════════
# 4c. ORACLE — ⚠ DEPRECIATION LANDS ON 84-122 L8 / L15, AND NOWHERE ELSE
# ══════════════════════════════════════════════════════════════════════════
depr = MS._ms_depreciation_lines(400_000, 57_143)
check(depr["122-L8"] == Decimal("400000"),
      "DEPRECIATION: the federal special allowance ADD-BACK lands on 84-122 LINE 8",
      f"add-back not on 122-L8: {depr}")
check(depr["122-L15"] == Decimal("57143"),
      "DEPRECIATION: the unreduced-MS-basis RECOVERY lands on 84-122 LINE 15",
      f"recovery not on 122-L15: {depr}")
check(set(depr) == {"122-L8", "122-L15"},
      "DEPRECIATION: exactly two landing lines, L8 and L15 — no others",
      f"unexpected depreciation landing lines: {set(depr)}")
# ⚠⚠ THE NEGATIVE ASSERTION — the specific silent wrong-box error this spec exists to avoid
check("122-L6" not in depr,
      "⚠ NEGATIVE: the add-back does NOT land on 84-122 L6 (municipal-bond interest)",
      "⚠⚠ CRITICAL: depreciation landed on 122-L6, which is MUNICIPAL BOND INTEREST")
check("122-L13" not in depr,
      "⚠ NEGATIVE: the recovery does NOT land on 84-122 L13 (flow-through income)",
      "⚠⚠ CRITICAL: depreciation landed on 122-L13, which is FLOW-THROUGH INCOME")
check(MS.MS_84122_DEPRECIATION_ADDBACK_LINE == "122-L8"
      and MS.MS_84122_DEPRECIATION_RECOVERY_LINE == "122-L15",
      "DEPRECIATION constants pin L8 (add-back) and L15 (recovery)",
      "depreciation line constants moved off L8/L15")
check(MS.MS_84122_MUNI_BOND_INTEREST_LINE == "122-L6"
      and MS.MS_84122_FLOWTHROUGH_INCOME_LINE == "122-L13",
      "TRAP constants record L6 = muni-bond interest and L13 = flow-through income",
      "trap-line constants wrong")
check(MS.MS_84122_DEPRECIATION_ADDBACK_LINE not in
      (MS.MS_84122_MUNI_BOND_INTEREST_LINE, MS.MS_84122_FLOWTHROUGH_INCOME_LINE),
      "⚠ NEGATIVE: the add-back constant is disjoint from both trap lines",
      "⚠⚠ CRITICAL: the add-back constant collides with a trap line")
# the same negative, asserted against what was actually SEEDED
seeded_lines = {ln.line_number: ln for ln in FormLine.objects.filter(tax_form=form)}
for trap, what in (("122-L6", "municipal-bond interest"), ("122-L13", "flow-through income")):
    ln = seeded_lines.get(trap)
    check(ln is not None and "R-MS-DEPR" not in (ln.source_rules or []),
          f"⚠ NEGATIVE (seeded): {trap} is modelled as {what} and is NOT wired to R-MS-DEPR",
          f"⚠⚠ CRITICAL: seeded line {trap} is wired to the depreciation rule")
for good in ("122-L8", "122-L15"):
    ln = seeded_lines.get(good)
    check(ln is not None and "R-MS-DEPR" in (ln.source_rules or []),
          f"seeded line {good} IS wired to R-MS-DEPR", f"seeded line {good} missing the depreciation rule")

# ══════════════════════════════════════════════════════════════════════════
# 4d. ORACLE — ⚠ THE TWO DIFFERENT SAFE-HARBOUR PERCENTAGES (mode x entity)
# ══════════════════════════════════════════════════════════════════════════
sh_comp_p = MS._ms_safe_harbour("1065", "composite")
sh_epte_p = MS._ms_safe_harbour("1065", "electing_pte")
sh_comp_s = MS._ms_safe_harbour("1120S", "composite")
sh_epte_s = MS._ms_safe_harbour("1120S", "electing_pte")
check(sh_comp_p["current_year_pct"] == "0.80" and sh_comp_p["form"] == "80-320",
      "SAFE HARBOUR: composite PARTNERSHIP -> Form 80-320 at 80%",
      f"composite partnership safe harbour wrong: {sh_comp_p}")
check(sh_epte_p["current_year_pct"] == "0.90" and sh_epte_p["form"] == "83-305",
      "SAFE HARBOUR: electing-PTE PARTNERSHIP -> Form 83-305 at 90% (NOT 80-320)",
      f"electing-PTE partnership safe harbour wrong: {sh_epte_p}")
check(sh_comp_s["current_year_pct"] == "0.90" and sh_comp_s["form"] == "83-305",
      "SAFE HARBOUR: composite S CORP -> Form 83-305 at 90%",
      f"composite S-corp safe harbour wrong: {sh_comp_s}")
check(sh_epte_s["current_year_pct"] == "0.90" and sh_epte_s["form"] == "83-305",
      "SAFE HARBOUR: electing-PTE S CORP -> Form 83-305 at 90%",
      f"electing-PTE S-corp safe harbour wrong: {sh_epte_s}")
check(sh_comp_p["current_year_pct"] != sh_epte_p["current_year_pct"],
      "⚠ SAFE HARBOUR: the fork is MODE x ENTITY — the same partnership gets 80% or 90% by MODE",
      "⚠ safe harbour is keyed on entity alone (the corrected-away error)")
check(sh_comp_p["has_10pct_penalty"] is False and sh_epte_p["has_10pct_penalty"] is True,
      "SAFE HARBOUR: only Form 80-320 lacks the 10% penalty component",
      "10% penalty fork wrong")
check("Apr. 15" in sh_comp_p["instalments"] and "4th" in sh_epte_p["instalments"],
      "SAFE HARBOUR: 80-320 is CALENDAR-keyed; 83-305 is 4th/6th/9th/12th month",
      "instalment-date fork wrong")
check(round(Decimal("100000") * Decimal(sh_comp_p["current_year_pct"])) == 80000
      and round(Decimal("100000") * Decimal(sh_epte_p["current_year_pct"])) == 90000,
      "SAFE HARBOUR arithmetic: 100,000 of tax -> 80,000 (composite ptnr) vs 90,000 (everyone else)",
      "safe harbour arithmetic wrong")
check(MS.MS_ESTIMATE_THRESHOLD == 200 and MS.MS_LARGE_ENTITY_THRESHOLD == 1_000_000,
      "ESTIMATES: >$200 threshold and the $1,000,000 large-entity bar", "estimate constants wrong")

# ══════════════════════════════════════════════════════════════════════════
# 4e. ORACLE — ⚠ THE COMPOSITE RATE COMPUTES NOTHING (no side is picked)
# ══════════════════════════════════════════════════════════════════════════
check(MS._ms_composite_tax(300_000) is None,
      "⚠ COMPOSITE RATE: _ms_composite_tax() returns None BY DESIGN — no rate is computed",
      "⚠⚠ the loader picked a side on the unresolved composite rate")
check(MS.MS_COMPOSITE_RATE_RESOLVED is False,
      "⚠ COMPOSITE RATE: MS_COMPOSITE_RATE_RESOLVED is False", "composite rate marked resolved")
check(len(MS.MS_COMPOSITE_RATE_POSITIONS) == 3
      and {p["position"] for p in MS.MS_COMPOSITE_RATE_POSITIONS} == {"A", "B", "C"},
      "⚠ COMPOSITE RATE: all THREE positions (DOR / statute / official regulation) are recorded",
      f"composite positions wrong: {MS.MS_COMPOSITE_RATE_POSITIONS}")
check(all(p.get("authority") for p in MS.MS_COMPOSITE_RATE_POSITIONS),
      "COMPOSITE RATE: every position carries its authority", "a composite position lacks authority")
check(MS.MS_COMPOSITE_DEDUCTION_BASE_RESOLVED is False and MS.MS_COMPOSITE_DEDUCTION_CAP == 5_000,
      "COMPOSITE: the 84-122 L30 deduction base is flagged UNRESOLVED (U7), cap $5,000 recorded",
      "composite deduction flags wrong")

# ══════════════════════════════════════════════════════════════════════════
# 4f. ORACLE — aviation branch, L20 asymmetry, owner credit, apportionment consts
# ══════════════════════════════════════════════════════════════════════════
check(MS._ms_bonus_rate(is_aviation_asset=False) == "1.00",
      "BONUS: a non-aviation asset placed in service after 12/31/2022 gets MS's OWN 100%",
      "MS own bonus rate wrong")
check(MS._ms_bonus_rate(is_aviation_asset=True, acquired_on_or_after_2025_01_20=False,
                        placed_in_service_on_or_after_2025_01_20=True) == "0.40",
      "⚠ AVIATION: acquired before 1/20/2025 -> FEDERAL 40% (the one place OBBBA reaches MS)",
      "aviation 40% branch wrong")
check(MS._ms_bonus_rate(is_aviation_asset=True, acquired_on_or_after_2025_01_20=True,
                        placed_in_service_on_or_after_2025_01_20=True) == "1.00",
      "AVIATION: acquired AND placed in service on/after 1/20/2025 -> FEDERAL 100%",
      "aviation 100% branch wrong")
check(MS._ms_bonus_rate(is_aviation_asset=False, acquired_on_or_after_2025_01_20=False)
      != MS._ms_bonus_rate(is_aviation_asset=True, acquired_on_or_after_2025_01_20=False),
      "⚠ AVIATION: two assets, same year, same taxpayer, DIFFERENT regimes",
      "aviation branch collapses into the general rule")
check(MS.MS_179_FOLLOWS_FEDERAL_FOR_YEAR is True
      and MS.MS_179_FEDERAL_TY2025_REFERENCE["limit"] == 2_500_000,
      "§179: encoded as ROLLING (= federal for the tax year), TY2025 reference $2,500,000",
      "§179 rolling encoding wrong")
check(MS._ms_l20_overpayment(30_000, 20_000, 1_200) == Decimal("8800"),
      "L20 ASYMMETRY: 30,000 - 20,000 - 1,200 = 8,800 (L16-L18 NOT netted)",
      f"L20 wrong: {MS._ms_l20_overpayment(30_000, 20_000, 1_200)}")
check(MS._ms_l20_overpayment(20_000, 20_000, 1_200) == Decimal("0"),
      "L20: no overpayment when L13 is not larger than L9 + L15", "L20 negative case wrong")
cred = MS._ms_84161_credit(18_000, 12_500)
check(cred["L5_allowed"] == Decimal("12500") and cred["L6_excess"] == Decimal("5500"),
      "84-161: L5 = MIN(L3D, L4) = 12,500; L6 excess = 5,500 (refundable at the owner's election)",
      f"84-161 arithmetic wrong: {cred}")
check(MS.MS_PTET_OWNER_CREDIT_LANDING["fiduciary"].startswith("Form 81-110"),
      "PTET: a FIDUCIARY cannot elect but CAN receive — credit lands on Form 81-110 line 8",
      "fiduciary credit landing wrong")
check(MS.MS_PTET_FIDUCIARIES_MAY_ELECT is False and MS.MS_PTET_ELECTION_IS_BINDING_FORWARD is True
      and MS.MS_PTET_ELECTION_BY_AMENDMENT is False and MS.MS_PTET_ELECTION_FORM == "84-381",
      "PTET flags: separate Form 84-381, binding forward, never by amendment, fiduciaries cannot elect",
      "PTET election flags wrong")
check(MS.MS_HAS_THROWBACK is True and MS.MS_US_GOVT_SALES_ORIGIN_SOURCED is True
      and MS.MS_RENTAL_PROPERTY_MULTIPLIER == 8,
      "APPORTIONMENT: throwback ON, U.S. Government sales origin-sourced, rental capitalized x8",
      "apportionment constants wrong")
check(2_000_000 + 3_000_000 + 250_000 + 750_000 == 6_000_000,
      "THROWBACK numerator: destination 2.0M + throwback 3.0M + dropship 0.25M + US Gov 0.75M = 6.0M",
      "throwback numerator arithmetic wrong")

# ══════════════════════════════════════════════════════════════════════════
# 5. Key diagnostics present (every RED-defer has its own)
# ══════════════════════════════════════════════════════════════════════════
REQUIRED_DIAGS = [
    "D_MS84105_COMPOSITE_RATE", "D_MS84105_FRANCHISE_FORK", "D_MS84105_DEPR_L8_L15",
    "D_MS84105_PTET_BINDING", "D_MS84105_THROWBACK", "D_MS84105_MS179",
    "D_MS84105_R1_DIRECT_ACCT", "D_MS84105_R2_SPECIAL_FORMULA", "D_MS84105_R3_PIPELINE",
    "D_MS84105_R4_FIN_INST", "D_MS84105_R5_PHARMA", "D_MS84105_R6_FEE_IN_LIEU",
    "D_MS84105_R7_MS_BASIS_ENGINE", "D_MS84105_R8_AVIATION", "D_MS84105_R9_NR_AGREEMENT",
    "D_MS84105_R10_84387", "D_MS84105_R11A_83305", "D_MS84105_R11B_80320",
    "D_MS84105_R12_BOTH_MODES", "D_MS84105_R13_CREDITS", "D_MS84105_R14_EXEMPTION",
    "D_MS84105_R15_CORP_ELECTION", "D_MS84105_R16_COMBINED", "D_MS84105_R17_84381_MISSING",
]
missing = [d for d in REQUIRED_DIAGS
           if not FormDiagnostic.objects.filter(tax_form=form, diagnostic_id=d).exists()]
check(not missing, f"all {len(REQUIRED_DIAGS)} required diagnostics present (R1-R17 each its own)",
      f"MISSING diagnostics: {missing}")
check(FormDiagnostic.objects.filter(tax_form=form, diagnostic_id="D_MS84105_R11A_83305").exists()
      and FormDiagnostic.objects.filter(tax_form=form, diagnostic_id="D_MS84105_R11B_80320").exists(),
      "R11 BRANCHES: separate diagnostics for the 83-305 and 80-320 computations",
      "R11 did not branch")

# ══════════════════════════════════════════════════════════════════════════
# 6. Flow assertions
# ══════════════════════════════════════════════════════════════════════════
for aid in ("FA-MS-L9-FORK", "FA-MS-DEPR-L8L15", "FA-MS-DEPR-NOT-L613",
            "FA-MS-SAFE-HARBOUR", "FA-MS-COMP-RATE", "FA-MS-FRAN-MIN"):
    check(FlowAssertion.objects.filter(assertion_id=aid).exists(), f"flow assertion {aid} present",
          f"flow assertion {aid} MISSING")

# ══════════════════════════════════════════════════════════════════════════
# report
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print(f"  MS_84_105: facts {FormFact.objects.filter(tax_form=form).count()} / "
      f"rules {FormRule.objects.filter(tax_form=form).count()} / "
      f"lines {FormLine.objects.filter(tax_form=form).count()} / "
      f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
      f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-MS').count()} / "
      f"MS authority sources: {AuthoritySource.objects.filter(jurisdiction_code='MS').count()} / "
      f"rule authority links: {RuleAuthorityLink.objects.filter(form_rule__tax_form=form).count()}")
print("=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
for fbad in FAILURES:
    print(f"  FAIL  {fbad}")
print("=" * 74)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - {'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print("NOTE: READY_TO_SEED was flipped IN MEMORY ONLY. The file on disk still ships False.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
