"""Throwaway-SQLite validation for the TX Franchise (margin) tax specs [WO-W02-ENT].

TX_05_158 (long form + EZ branch) / TX_05_102 PIR / TX_05_167 OIR — the TEXAS 2026
REPORT, due 05/15/2026, which is Delvio TY2025. (A "2025 Texas report" is TY2024.)

Checks: READY_TO_SEED ships False; ALL CharField caps (rule_id 20, line_number 20,
assertion_id 20, diagnostic_id 40, fact_key 100, topic_name 255, form_number 50,
source_code 100, form_title 255, label 255, scenario_name 255); every rule >= 1
authority link; rule_link coverage both ways; no duplicate ids anywhere; and
ARITHMETIC ORACLES for all five filing outcomes (especially that <= $2,650,000 emits
a PIR/OIR and NO franchise report), the four-way margin minimum INCLUDING a case
where the revenue-$1M branch wins, the $480,000 cap on Item 15 but not Item 16,
SIC-blank -> 0.75%, the EZ path at <= $20M, and tax < $1,000 -> no payment but the
report is still required. Also asserts that NO rule encodes an asset-level bonus
date key (W1) and NO rule hard-codes a federal form line number (W6).

ASCII-safe prints. Run: poetry run python scratchpad/validate_tx.py
"""
import io
import os
import re
import sys

# Loader NOTES/DESCRIPTIONS legitimately carry non-ASCII (verbatim quotes, warning
# glyphs). Those strings surface in failure messages, so widen the console rather
# than strip them. Command-class console output is separately ASCII-only.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

LOADER_PATH = os.path.join(PROJECT_ROOT, "specs", "management", "commands", "load_tx_franchise.py")
SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_tx.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def close(a, b, tol=0.01):
    return abs(float(a) - float(b)) <= tol


# ══════════════════════════════════════════════════════════════════════════
# 0. SAFETY GUARD — the shipped file must carry READY_TO_SEED = False
#    (read the SOURCE TEXT before importing, so nothing can mask it)
# ══════════════════════════════════════════════════════════════════════════
SRC = io.open(LOADER_PATH, encoding="utf-8").read()
check(re.search(r"^READY_TO_SEED\s*=\s*False\s*$", SRC, re.M) is not None,
      "SAFETY GUARD: loader ships READY_TO_SEED = False",
      "SAFETY GUARD VIOLATION: loader does NOT ship READY_TO_SEED = False")
# Only a MODULE-LEVEL assignment can flip the sentinel; the guard's own instructional
# text ("then set READY_TO_SEED = True") is prose inside a string and is harmless.
_assigns = re.findall(r"^READY_TO_SEED\s*=\s*(\w+)", SRC, re.M)
check(_assigns == ["False"],
      "SAFETY GUARD: exactly one module-level assignment, and it is False",
      f"SAFETY GUARD VIOLATION: module-level READY_TO_SEED assignments = {_assigns}")

# ── Year mapping must be stated in the docstring ──
check("2026" in SRC[:20000] and "05/15/2026" in SRC[:20000],
      "docstring carries the 2026-report / 05/15/2026 year mapping",
      "docstring is missing the 2026-report year mapping")
check("TY2024" in SRC[:20000],
      "docstring warns that a '2025 Texas report' is TY2024",
      "docstring does not warn about the TY2024 trap")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from sources.models import AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.management.commands import load_tx_franchise as TX  # noqa: E402

# ── The guard must actually refuse while the sentinel is False ──
call_command("migrate", run_syncdb=True, verbosity=0)
try:
    call_command("load_tx_franchise", verbosity=0)
    FAILURES.append("guard did NOT refuse to seed while READY_TO_SEED is False")
except Exception as e:  # noqa: BLE001
    check("REFUSING TO SEED" in str(e),
          "guard refuses to seed while READY_TO_SEED is False",
          f"guard raised the wrong error: {e!r}")

# ── Flip in memory ONLY (never on disk) and seed the throwaway DB ──
TX.READY_TO_SEED = True
try:
    call_command("load_tx_franchise", verbosity=0)
    PASSES.append("load_tx_franchise ran + seeded into throwaway SQLite without error")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_tx_franchise raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)

FORM_NUMBERS = ["TX_05_158", "TX_05_102", "TX_05_167"]

# ══════════════════════════════════════════════════════════════════════════
# 1. CharField caps — enforced by Postgres but NOT by SQLite, so assert them
# ══════════════════════════════════════════════════════════════════════════
def cap_check(label, pairs, cap):
    viol = [f"{v!r} (len {len(v)})" for v in pairs if len(v) > cap]
    check(not viol, f"CAP {label} <= {cap}: OK ({len(pairs)} checked)",
          f"CAP {label} > {cap}: " + "; ".join(viol))


all_rule_ids, all_line_numbers, all_diag_ids, all_fact_keys = [], [], [], []
all_form_numbers, all_form_titles, all_labels, all_scenario_names = [], [], [], []
for fn in FORM_NUMBERS:
    form = TaxForm.objects.get(form_number=fn)
    all_form_numbers.append(form.form_number)
    all_form_titles.append(form.form_title)
    all_rule_ids += [r.rule_id for r in FormRule.objects.filter(tax_form=form)]
    all_line_numbers += [ln.line_number for ln in FormLine.objects.filter(tax_form=form)]
    all_diag_ids += [d.diagnostic_id for d in FormDiagnostic.objects.filter(tax_form=form)]
    all_fact_keys += [f.fact_key for f in FormFact.objects.filter(tax_form=form)]
    all_labels += [f.label for f in FormFact.objects.filter(tax_form=form)]
    all_scenario_names += [t.scenario_name for t in TestScenario.objects.filter(tax_form=form)]

fa_ids = [fa.assertion_id for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-TX")]
topic_names = [t.topic_name for t in AuthorityTopic.objects.all()]
topic_codes = [t.topic_code for t in AuthorityTopic.objects.all()]
source_codes = [s["source_code"] for s in TX.AUTHORITY_SOURCES]

cap_check("rule_id", all_rule_ids, 20)
cap_check("line_number", all_line_numbers, 20)
cap_check("assertion_id", fa_ids, 20)
cap_check("diagnostic_id", all_diag_ids, 40)
cap_check("fact_key", all_fact_keys, 100)
cap_check("topic_name", topic_names, 255)
cap_check("topic_code", topic_codes, 100)
cap_check("form_number", all_form_numbers, 50)
cap_check("form_title", all_form_titles, 255)
cap_check("fact label", all_labels, 255)
cap_check("scenario_name", all_scenario_names, 255)
cap_check("source_code", source_codes, 100)

# ══════════════════════════════════════════════════════════════════════════
# 2. Authority links, rule-link coverage, and duplicate ids
# ══════════════════════════════════════════════════════════════════════════
for spec in TX.FORMS:
    fn = spec["identity"]["form_number"]
    form = TaxForm.objects.get(form_number=fn)
    rules = list(FormRule.objects.filter(tax_form=form))
    ruleless = [r.rule_id for r in rules if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
    check(not ruleless, f"{fn}: all {len(rules)} rules have >= 1 authority link",
          f"{fn}: rules with ZERO authority links: {ruleless}")

    defined = {r["rule_id"] for r in spec["rules"]}
    linked = {rl[0] for rl in spec["rule_links"]}
    check(not (linked - defined), f"{fn}: rule_links reference only defined rules",
          f"{fn}: orphan rule_links {sorted(linked - defined)}")
    check(not (defined - linked), f"{fn}: every rule appears in rule_links",
          f"{fn}: unlinked rules {sorted(defined - linked)}")

    for key, field in (("rules", "rule_id"), ("lines", "line_number"),
                       ("diagnostics", "diagnostic_id"), ("facts", "fact_key"),
                       ("scenarios", "scenario_name")):
        vals = [d[field] for d in spec[key]]
        dupes = sorted({v for v in vals if vals.count(v) > 1})
        check(not dupes, f"{fn}: no duplicate {field} ({len(vals)} entries)",
              f"{fn}: DUPLICATE {field}: {dupes}")

fa_defined = [a["assertion_id"] for a in TX.FLOW_ASSERTIONS]
check(len(fa_defined) == len(set(fa_defined)),
      f"no duplicate assertion_id ({len(fa_defined)} flow assertions)",
      f"DUPLICATE assertion_id: {sorted({a for a in fa_defined if fa_defined.count(a) > 1})}")
check(len(source_codes) == len(set(source_codes)),
      f"no duplicate source_code ({len(source_codes)} sources)", "DUPLICATE source_code")

# every rule_link source must be a defined source or an EXISTING_SOURCES_TO_REFERENCE entry
known_sources = set(source_codes) | set(TX.EXISTING_SOURCES_TO_REFERENCE)
bad_src = set()
for spec in TX.FORMS:
    bad_src |= {rl[1] for rl in spec["rule_links"]} - known_sources
check(not bad_src, "every rule_link names a known authority source", f"unknown sources in rule_links: {sorted(bad_src)}")
check("TX_STAR_202603002M_IRC_CONFORMITY" in TX.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE includes TX_STAR_202603002M_IRC_CONFORMITY",
      "TX_STAR_202603002M_IRC_CONFORMITY missing from EXISTING_SOURCES_TO_REFERENCE")

# ══════════════════════════════════════════════════════════════════════════
# 3. Form identity
# ══════════════════════════════════════════════════════════════════════════
for fn in FORM_NUMBERS:
    form = TaxForm.objects.get(form_number=fn)
    check(form.jurisdiction == "TX", f"{fn}: jurisdiction = TX", f"{fn}: jurisdiction {form.jurisdiction!r}")
    check(form.tax_year == 2025, f"{fn}: tax_year = 2025 (Delvio TY2025 = the TEXAS 2026 report)",
          f"{fn}: tax_year {form.tax_year}")
    check(form.version == 1 and form.status == "draft", f"{fn}: version 1 / status draft",
          f"{fn}: version {form.version} status {form.status!r}")
    check(form.entity_types == ["1065", "1120S", "1120"],
          f"{fn}: entity_types = ['1065','1120S','1120'] (margin tax reaches most entities)",
          f"{fn}: entity_types {form.entity_types}")

check(TX.FORM_TAX_YEAR == 2025 and TX.TX_REPORT_YEAR == 2026 and TX.TX_REPORT_DUE_DATE == "05/15/2026",
      "year mapping constants: FORM_TAX_YEAR 2025 / TX_REPORT_YEAR 2026 / due 05/15/2026",
      "year mapping constants wrong")

# ══════════════════════════════════════════════════════════════════════════
# 4. Verified constants
# ══════════════════════════════════════════════════════════════════════════
check(TX._yk(TX.TX_NO_TAX_DUE_THRESHOLD, 2025) == 2_650_000,
      "constant: no tax due threshold $2,650,000 (2026 report)", "threshold constant wrong")
check(TX._yk(TX.TX_EZ_REVENUE_CEILING, 2025) == 20_000_000,
      "constant: EZ ceiling $20,000,000", "EZ ceiling constant wrong")
check(TX._yk(TX.TX_COMP_CAP_PER_PERSON, 2025) == 480_000,
      "constant: compensation cap $480,000 per person (2026 report)", "comp cap constant wrong")
check(TX._yk(TX.TX_MARGIN_1M_DEDUCTION, 2025) == 1_000_000,
      "constant: margin branch 4 = revenue less $1,000,000", "$1M margin constant wrong")
check(TX._yk(TX.TX_ECONOMIC_NEXUS_RECEIPTS, 2025) == 500_000,
      "constant: economic nexus $500,000", "economic nexus constant wrong")
check(TX._yk(TX.TX_MIN_PAYMENT_FLOOR, 2025) == 1_000,
      "constant: no-payment floor $1,000 (strictly less than)", "payment floor constant wrong")
check((TX._yk(TX.TX_RATE_STANDARD, 2025), TX._yk(TX.TX_RATE_RETAIL_WHOLESALE, 2025),
       TX._yk(TX.TX_RATE_EZ, 2025)) == ("0.0075", "0.00375", "0.00331"),
      "constants: rates 0.75% / 0.375% retail-wholesale / 0.331% EZ", "rate constants wrong")

# ══════════════════════════════════════════════════════════════════════════
# 5. ORACLE — THE FILING GATE, all five outcomes
# ══════════════════════════════════════════════════════════════════════════
g = TX._tx_filing_outcome(is_taxable_entity=False, legal_form="general_partnership")
check(g["outcome"] == "A_NOTHING" and g["franchise_report"] is None and g["info_report"] is None,
      "GATE (A): not a taxable entity -> NOTHING (no report, no PIR, no OIR)",
      f"GATE (A) not-taxable wrong: {g}")

g = TX._tx_filing_outcome(has_nexus=False, legal_form="llc", annualized_total_revenue=9_000_000)
check(g["outcome"] == "A_NOTHING" and g["info_report"] is None,
      "GATE (A): no nexus -> NOTHING even at $9M of revenue", f"GATE (A) no-nexus wrong: {g}")

g = TX._tx_filing_outcome(is_new_veteran_owned=True, legal_form="llc", annualized_total_revenue=8_000_000)
check(g["outcome"] == "A_NOTHING" and g["info_report"] is None,
      "GATE (A): new veteran-owned -> NOTHING, including NO PIR/OIR", f"GATE (A) veteran wrong: {g}")

g = TX._tx_filing_outcome(is_passive_entity=True, legal_form="limited_partnership",
                          annualized_total_revenue=9_000_000)
check(g["outcome"] == "B_STUB" and g["franchise_report"] == "TX_05_158" and g["info_report"] is None,
      "GATE (B): passive LP -> STUB report and NO PIR/OIR (carve-out 2)",
      f"GATE (B) passive wrong: {g}")

g = TX._tx_filing_outcome(is_qualifying_reit=True, legal_form="corporation",
                          annualized_total_revenue=40_000_000)
check(g["outcome"] == "B_STUB" and g["info_report"] == "TX_05_102",
      "GATE (B): REIT -> STUB report AND a PIR (the REIT/passive asymmetry)",
      f"GATE (B) REIT wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=1_200_000)
check(g["outcome"] == "C_INFO_ONLY" and g["franchise_report"] is None
      and g["render_target"] is None and g["info_report"] == "TX_05_102",
      "GATE (C) ***<= $2,650,000 emits a PIR/OIR and NO FRANCHISE REPORT AT ALL***",
      f"GATE (C) wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=2_650_000)
check(g["outcome"] == "C_INFO_ONLY" and g["franchise_report"] is None,
      "GATE (C) boundary: EXACTLY $2,650,000 is still info-only ('less than OR EQUAL TO')",
      f"GATE (C) boundary wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=2_650_001)
check(g["outcome"] == "E_LONG" and g["franchise_report"] == "TX_05_158"
      and g["render_target"] == "05-158-A/B",
      "GATE (E) boundary: $2,650,001 triggers the long form", f"GATE (E) boundary wrong: {g}")

g = TX._tx_filing_outcome(legal_form="general_partnership", annualized_total_revenue=900_000)
check(g["outcome"] == "C_INFO_ONLY" and g["info_report"] == "TX_05_167",
      "GATE (C): a below-threshold GP emits the OIR (not the PIR) and no franchise report",
      f"GATE (C) OIR routing wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=18_000_000, ez_elected=True)
check(g["outcome"] == "D_EZ" and g["render_target"] == "05-169" and g["info_report"] == "TX_05_102",
      "GATE (D): <= $20M with the EZ elected -> EZ path, render target 05-169",
      f"GATE (D) wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=20_000_001, ez_elected=True)
check(g["outcome"] == "E_LONG",
      "GATE (D) boundary: $20,000,001 makes the EZ unavailable even when elected",
      f"GATE (D) boundary wrong: {g}")

g = TX._tx_filing_outcome(legal_form="llc", annualized_total_revenue=2_000_000,
                          tiered_partnership_election=True)
check(g["outcome"] == "E_LONG",
      "GATE: a tiered-partnership election defeats the threshold branch (long form at $2M)",
      f"GATE tiered override wrong: {g}")

# ── Nexus ──
check(TX._tx_has_nexus(texas_receipts_this_accounting_period=400_000) is False,
      "NEXUS: $400,000 of Texas receipts and no presence -> no nexus", "nexus below-threshold wrong")
check(TX._tx_has_nexus(texas_receipts_this_accounting_period=500_000) is True,
      "NEXUS: exactly $500,000 creates nexus ('$500,000 or more')", "nexus at-threshold wrong")
check(TX._tx_has_nexus(organized_in_texas=True) is True,
      "NEXUS: organized in Texas creates nexus regardless of receipts", "nexus organized wrong")

# ══════════════════════════════════════════════════════════════════════════
# 6. ORACLE — PIR vs OIR routing and the three carve-outs
# ══════════════════════════════════════════════════════════════════════════
routes = {lf: TX._tx_info_report(lf) for lf in
          ("limited_partnership", "llp", "trust", "general_partnership", "llc",
           "s_corporation", "joint_venture", "professional_association", "financial_institution")}
check(routes["limited_partnership"] == "TX_05_102", "PIR/OIR: LP -> PIR (expressly enumerated)",
      f"LP routed to {routes['limited_partnership']}")
check(routes["llp"] == "TX_05_167", "PIR/OIR: LLP -> OIR (an LLP is NOT an 'LP')",
      f"LLP routed to {routes['llp']}")
check(routes["trust"] == "TX_05_167", "PIR/OIR: trust -> OIR", f"trust routed to {routes['trust']}")
check(routes["general_partnership"] == "TX_05_167", "PIR/OIR: GP -> OIR", "GP routing wrong")
check(routes["joint_venture"] == "TX_05_167", "PIR/OIR: joint venture -> OIR", "JV routing wrong")
check(routes["llc"] == "TX_05_102" and routes["s_corporation"] == "TX_05_102",
      "PIR/OIR: LLC and S corporation -> PIR", "LLC/S-corp routing wrong")
check(routes["professional_association"] == "TX_05_102" and routes["financial_institution"] == "TX_05_102",
      "PIR/OIR: professional association and financial institution -> PIR", "PA/FI routing wrong")
check(TX._tx_info_report("llc", is_final_report=True) is None,
      "PIR/OIR carve-out 1: NO information report with a FINAL report", "final-report carve-out wrong")
check(TX._tx_info_report("limited_partnership", is_passive_entity=True) is None,
      "PIR/OIR carve-out 2: passive entity files neither", "passive carve-out wrong")
check(TX._tx_info_report("llc", is_new_veteran_owned=True) is None,
      "PIR/OIR carve-out 3: new veteran-owned files neither", "veteran carve-out wrong")

# ══════════════════════════════════════════════════════════════════════════
# 7. ORACLE — annualization
# ══════════════════════════════════════════════════════════════════════════
check(close(TX._tx_annualized_revenue(1_500_000, 180), 3_041_666.67),
      "ANNUALIZE: 1,500,000 / 180 x 365 = 3,041,666.67 (above the threshold)",
      f"annualize wrong: {TX._tx_annualized_revenue(1_500_000, 180)}")
check(close(TX._tx_annualized_revenue(1_000_000, 180), 2_027_777.78),
      "ANNUALIZE: 1,000,000 / 180 x 365 = 2,027,777.78 (below the threshold)", "annualize short wrong")
check(TX._tx_annualized_revenue(4_000_000, 365) == 4_000_000,
      "ANNUALIZE: a 365-day period is an identity", "annualize identity wrong")
_ann = TX._tx_annualized_revenue(1_500_000, 180)
_m = TX._tx_margin(1_500_000, 0, 0)   # tax computation uses Item 10, NOT annualized revenue
check(_m["item19"] == 1_050_000 and _ann > 3_000_000,
      "ANNUALIZE: annualized revenue drives the gate only; Item 10 (1,500,000) drives the computation",
      "annualized revenue leaked into the margin computation")

# ══════════════════════════════════════════════════════════════════════════
# 8. ORACLE — THE FOUR-WAY MARGIN MINIMUM
# ══════════════════════════════════════════════════════════════════════════
m = TX._tx_margin(3_000_000, 0, 400_000)
check(m["item19"] == 2_100_000 and m["item20"] == 3_000_000 and m["item21"] == 2_600_000
      and m["item22"] == 2_000_000 and m["item23"] == 2_000_000 and m["winning_branch"] == "22_million",
      "MARGIN ***the revenue-less-$1,000,000 branch WINS*** (service entity: 2,000,000)",
      f"MARGIN $1M branch wrong: {m}")
three_way = 3_000_000 - max(0, 400_000, 0.30 * 3_000_000)   # the shorthand that drops Item 22
check(three_way == 2_100_000 and m["item23"] == 2_000_000,
      "MARGIN: the three-way shorthand returns 2,100,000 and OVERSTATES margin by 100,000",
      "three-way shorthand comparison wrong")

m = TX._tx_margin(5_000_000, 4_200_000, 500_000)
check(m["item23"] == 800_000 and m["winning_branch"] == "20_cogs",
      "MARGIN: the COGS branch wins (5,000,000 - 4,200,000 = 800,000)", f"MARGIN COGS wrong: {m}")

m = TX._tx_margin(10_000_000, 1_000_000, 500_000)
check(m["item23"] == 7_000_000 and m["winning_branch"] == "19_70pct",
      "MARGIN: the 70% branch wins (10,000,000 x 0.70 = 7,000,000)", f"MARGIN 70% wrong: {m}")

m = TX._tx_margin(4_000_000, 0, 3_500_000)
check(m["item23"] == 500_000 and m["winning_branch"] == "21_comp",
      "MARGIN: the compensation branch wins (4,000,000 - 3,500,000 = 500,000)", f"MARGIN comp wrong: {m}")

m = TX._tx_margin(1_000_000, 1_800_000, 1_200_000)
check(m["item20"] == 0 and m["item21"] == 0 and m["item22"] == 0 and m["item19"] == 700_000
      and m["item23"] == 0,
      "MARGIN: each branch floors at zero BEFORE the minimum; margin = 0", f"MARGIN floors wrong: {m}")

m = TX._tx_margin(2_000_000, 0, 0)
check(m["item22"] == 1_000_000 and m["item19"] == 1_400_000 and m["item23"] == 1_000_000,
      "MARGIN: below $3,333,333 the $1M branch beats the 70% branch", f"MARGIN crossover wrong: {m}")
m = TX._tx_margin(4_000_000, 0, 0)
check(m["item19"] == 2_800_000 and m["item22"] == 3_000_000 and m["item23"] == 2_800_000,
      "MARGIN: above $3,333,333 the 70% branch beats the $1M branch", "MARGIN crossover-2 wrong")

# ══════════════════════════════════════════════════════════════════════════
# 9. ORACLE — COMPENSATION: the $480,000 cap on Item 15 only
# ══════════════════════════════════════════════════════════════════════════
c = TX._tx_compensation([600_000, 600_000, 600_000], employee_benefits_item16=200_000)
check(c["item15"] == 1_440_000,
      "COMP: the $480,000 cap applies PER PERSON on Item 15 (3 x 480,000 = 1,440,000)",
      f"COMP Item 15 cap wrong: {c}")
check(c["item16"] == 200_000,
      "COMP ***the $480,000 cap does NOT apply to Item 16 benefits*** (200,000 passes through)",
      f"COMP Item 16 was capped: {c}")
check(c["item18"] == 1_640_000, "COMP: Item 18 = 1,440,000 + 200,000 = 1,640,000", f"COMP total wrong: {c}")
check(c["item15"] != 1_800_000 and c["item15"] != 480_000,
      "COMP: the cap is neither ignored (1,800,000) nor applied entity-wide once (480,000)",
      "COMP cap applied at the wrong level")

c = TX._tx_compensation([600_000, -50_000])
check(c["item15"] == 430_000,
      "COMP: negative NDI is UNCAPPED (480,000 + (-50,000) = 430,000)", f"COMP negative NDI wrong: {c}")

c = TX._tx_compensation([600_000], cap_proration_factor=0.5)
check(c["item15"] == 240_000 and c["cap_applied"] == 240_000,
      "COMP: the short-period proration factor is direct-entry (0.5 -> cap 240,000)",
      f"COMP proration wrong: {c}")

c = TX._tx_compensation([100_000, 200_000], employee_benefits_item16=0)
check(c["item15"] == 300_000, "COMP: wages under the cap pass through unchanged", "COMP under-cap wrong")

# ══════════════════════════════════════════════════════════════════════════
# 10. ORACLE — COGS
# ══════════════════════════════════════════════════════════════════════════
k = TX._tx_cogs(2_000_000, 500_000, 0)
check(k["item12"] == 20_000 and k["item14"] == 2_020_000,
      "COGS: Item 12 = 4% of the overhead base (0.04 x 500,000 = 20,000); Item 14 = 2,020,000",
      f"COGS 4% cap wrong: {k}")
k = TX._tx_cogs(1_000_000, 0, -75_000)
check(k["item14"] == 925_000,
      "COGS: Item 13 may be negative (undocumented-worker compensation) and is not floored",
      f"COGS negative Item 13 wrong: {k}")

# ══════════════════════════════════════════════════════════════════════════
# 11. ORACLE — RATE selection (SIC-driven, blank defaults to 0.75%)
# ══════════════════════════════════════════════════════════════════════════
check(TX._tx_rate("", False) == "0.0075",
      "RATE ***a BLANK SIC code defaults to 0.75%***", f"blank SIC -> {TX._tx_rate('', False)}")
check(TX._tx_rate(None, True) == "0.0075",
      "RATE: a missing SIC defaults to 0.75% even when retail conditions are affirmed",
      "None SIC default wrong")
check(TX._tx_rate("   ", False) == "0.0075", "RATE: a whitespace-only SIC defaults to 0.75%",
      "whitespace SIC default wrong")
check(TX._tx_rate("5411", True) == "0.00375",
      "RATE: a qualifying retailer with an affirmed SIC gets 0.375%", "retail rate wrong")
check(TX._tx_rate("5411", False) == "0.0075",
      "RATE: a retail SIC without the three-condition affirmation stays at 0.75%",
      "unaffirmed retail rate wrong")

# ══════════════════════════════════════════════════════════════════════════
# 12. ORACLE — APPORTIONMENT
# ══════════════════════════════════════════════════════════════════════════
check(TX._tx_apportionment_factor(750_000, 2_000_000) == 0.375,
      "APPORT: 750,000 / 2,000,000 = 0.3750", "apportionment ratio wrong")
check(TX._tx_apportionment_factor(0, 2_000_000) == 0.0,
      "APPORT: zero Texas receipts -> factor 0.0000", "apportionment zero rule wrong")
check(TX._tx_apportionment_factor(900_000, 900_000) == 1.0,
      "APPORT: equal and > 0 -> 1.0000", "apportionment equal rule wrong")
check(TX._tx_apportionment_factor(1_000_000, 900_000) == 1.0,
      "APPORT: Texas MORE than everywhere and both > 0 -> 1.0000", "apportionment excess rule wrong")
check(TX._tx_apportionment_factor(1, 3) == 0.3333,
      "APPORT: rounded to 4 decimal places (1/3 -> 0.3333)", "apportionment rounding wrong")

# ══════════════════════════════════════════════════════════════════════════
# 13. ORACLE — LONG-FORM TAX, no discount, no minimum tax
# ══════════════════════════════════════════════════════════════════════════
t = TX._tx_long_form_tax(2_000_000, 1.0, 0, "0.0075", 0)
check(t["item31"] == 15_000 and t["item35"] == 15_000,
      "TAX: 2,000,000 taxable margin x 0.0075 = 15,000", f"long-form tax wrong: {t}")
check(t["item34"] == 0 and t["item35"] == t["item33"],
      "TAX: Item 34 discount is identically 0 and Item 35 == Item 33", f"discount/total wrong: {t}")
t0 = TX._tx_long_form_tax(0, 1.0, 0, "0.0075", 0)
check(t0["item35"] == 0,
      "TAX: NO MINIMUM TAX — zero margin produces zero tax, not a floor amount", f"minimum tax wrong: {t0}")
tc = TX._tx_long_form_tax(1_000_000, 1.0, 0, "0.0075", 50_000)
check(tc["item33"] == 0,
      "TAX: Item 33 floors at zero when credits exceed the tax (7,500 - 50,000 -> 0)",
      f"Item 33 floor wrong: {tc}")
td = TX._tx_long_form_tax(1_000_000, 1.0, 2_000_000, "0.0075", 0)
check(td["item29"] == 0,
      "TAX: Item 28 deductions may not reduce apportioned margin below zero", f"Item 29 floor wrong: {td}")
tr = TX._tx_long_form_tax(4_000_000, 0.5, 0, "0.00375", 0)
check(tr["item27"] == 2_000_000 and tr["item31"] == 7_500,
      "TAX: apportioned margin 2,000,000 at the 0.375% retail rate = 7,500", f"retail-rate tax wrong: {tr}")
tz = TX._tx_long_form_tax(5_600_000, 0.0, 0, "0.0075", 0)
check(tz["item27"] == 0 and tz["item35"] == 0,
      "TAX: a zero apportionment factor produces zero tax (report still filed)", "zero-factor tax wrong")

# ══════════════════════════════════════════════════════════════════════════
# 14. ORACLE — the <$1,000 branch vs the threshold branch
# ══════════════════════════════════════════════════════════════════════════
m = TX._tx_margin(3_000_000, 0, 2_900_000)
t = TX._tx_long_form_tax(m["item23"], 1.0, 0, "0.0075", 0)
check(m["item23"] == 100_000 and t["item35"] == 750,
      "NOPAY setup: margin 100,000 x 0.0075 = 750", f"nopay setup wrong: {m} {t}")
check(TX._tx_payment_required(750, 3_000_000, False) is False,
      "NOPAY ***tax of 750 (< $1,000) -> NO PAYMENT***", "under-$1,000 payment rule wrong")
check(TX._tx_report_still_required(750, "E_LONG") is True,
      "NOPAY ***the FULL report is still required when tax < $1,000***", "report-still-required wrong")
check(TX._tx_payment_required(1_000, 5_000_000, False) is True,
      "NOPAY: exactly $1,000 IS payable (the test is STRICTLY less than)", "exactly-$1,000 wrong")
check(TX._tx_payment_required(999.99, 5_000_000, False) is False,
      "NOPAY: $999.99 is not payable", "just-under-$1,000 wrong")
check(TX._tx_payment_required(5_000, 2_000_000, False) is False,
      "NOPAY: below the threshold no payment is due (and no report was produced at all)",
      "threshold branch payment wrong")
check(TX._tx_report_still_required(0, "C_INFO_ONLY") is False,
      "NOPAY: outcome (C) produces NO franchise report — only the PIR/OIR",
      "outcome (C) report-required wrong")
check(TX._tx_payment_required(400, 2_000_000, True) is True,
      "NOPAY: a tiered-partnership election defeats BOTH no-tax branches ($400 is due)",
      "tiered override wrong")
check(TX._tx_report_still_required(0, "B_STUB") is True and TX._tx_report_still_required(0, "A_NOTHING") is False,
      "NOPAY: outcomes (B)/(D)/(E) produce a report; (A)/(C) do not", "outcome report-map wrong")

# ══════════════════════════════════════════════════════════════════════════
# 15. ORACLE — THE EZ PATH
# ══════════════════════════════════════════════════════════════════════════
ez = TX._tx_ez_tax(18_000_000, 0.5)
check(ez["ez14"] == 9_000_000 and close(ez["ez15"], 29_790) and close(ez["ez17"], 29_790),
      "EZ: 18,000,000 x 0.5 = 9,000,000 apportioned revenue x 0.00331 = 29,790", f"EZ tax wrong: {ez}")
check(ez["ez16"] == 0 and ez["ez17"] == ez["ez15"], "EZ: Item 16 discount is 0 and Item 17 == Item 15",
      "EZ discount wrong")
mlong = TX._tx_margin(18_000_000, 12_000_000, 2_000_000)
tlong = TX._tx_long_form_tax(mlong["item23"], 0.5, 0, "0.0075", 0)
check(mlong["item23"] == 6_000_000 and tlong["item35"] == 22_500,
      "EZ compare: the long form on the same facts costs 22,500 (margin 6,000,000)",
      f"EZ compare long form wrong: {mlong} {tlong}")
check(tlong["item35"] < ez["ez17"],
      "EZ compare: at a 33.3% margin ratio the EZ is MORE expensive -> recommend the long form",
      "EZ recommendation comparison wrong")
check(close(TX._tx_ez_breakeven("0.0075"), 0.4413333, 1e-6),
      "EZ break-even vs 0.75% = 44.13% of revenue", f"EZ breakeven 0.75 wrong: {TX._tx_ez_breakeven('0.0075')}")
check(close(TX._tx_ez_breakeven("0.00375"), 0.8826667, 1e-6),
      "EZ break-even vs 0.375% = 88.27% of revenue", "EZ breakeven 0.375 wrong")
check(TX._tx_ez_breakeven("0.00375") > 0.70,
      "EZ: 88.27% > the 70% margin ceiling, so a qualifying retailer can NEVER benefit from the EZ",
      "EZ retailer conclusion wrong")

# ══════════════════════════════════════════════════════════════════════════
# 16. W1 / W6 — nothing guessed
# ══════════════════════════════════════════════════════════════════════════
rule_text = " ".join(
    (r.get("formula", "") or "") for spec in TX.FORMS for r in spec["rules"]
)
bad_date = re.findall(r"(?:january|jan\.?)\s*19|1/19/2025|01/19/2025|placed[_ ]in[_ ]service\s*(?:on|>=)",
                      rule_text, re.I)
check(not bad_date,
      "W1: NO rule formula encodes an asset-level bonus date key (diagnostic only)",
      f"W1 VIOLATION — a rule formula picks a bonus date key: {bad_date}")
bad_fed = re.findall(r"\b(?:1120S?|1065|1041)\s*(?:line|l)\s*\d|schedule\s+k\s+line\s+\d|form\s+8825\s+line",
                     rule_text, re.I)
check(not bad_fed,
      "W6: NO rule formula hard-codes a federal form line number (named facts only)",
      f"W6 VIOLATION — a rule formula hard-codes a federal line: {bad_fed}")

f158 = TaxForm.objects.get(form_number="TX_05_158")
diag_ids = set(FormDiagnostic.objects.filter(tax_form=f158).values_list("diagnostic_id", flat=True))
RED_DEFERS = ["D_TX_DEPR_CATCHUP", "D_TX_COMBINED", "D_TX_TIERED", "D_TX_CREDITS", "D_TX_FINAL",
              "D_TX_EXT", "D_TX_TRUST", "D_TX_SPECIAL_APPT", "D_TX_SPECIAL_ENTITY", "D_TX_AMENDED"]
missing = [d for d in RED_DEFERS if d not in diag_ids]
check(not missing, "RED-DEFERS: all 10 (R1-R10) have their own diagnostic", f"missing RED-defers: {missing}")
sev = dict(FormDiagnostic.objects.filter(tax_form=f158, diagnostic_id__in=RED_DEFERS)
           .values_list("diagnostic_id", "severity"))
check(all(v == "error" for v in sev.values()),
      "RED-DEFERS: every RED-defer diagnostic is severity=error", f"RED-defer severities: {sev}")
for did in ("D_TX_BONUS_DATE_GATE", "D_TX_FED_LINE_MAP", "D_TX_YEAR_MAPPING",
            "D_TX_SIC_RATE_DEFAULT", "D_TX_COMP_CAP_ITEM15_ONLY", "D_TX_MARGIN_FOUR_WAY",
            "D_TX_NTD_THRESHOLD_INFO_ONLY", "D_TX_UNDER_1000_NO_PAYMENT",
            "D_TX_COGS_DIRECT_ENTRY", "D_TX_GILTI_NOT_EXCLUDABLE", "D_TX_NO_TAX_DUE_REPORT_GONE",
            "D_TX_COMP_CAP_PRORATION", "D_TX_ZERO_TEXAS_RECEIPTS", "D_TX_DISREGARDED_ENTITY"):
    check(did in diag_ids, f"diagnostic present: {did}", f"MISSING diagnostic: {did}")
check(FormDiagnostic.objects.get(tax_form=f158, diagnostic_id="D_TX_FED_LINE_MAP").severity == "error",
      "W6: D_TX_FED_LINE_MAP is severity=error (blocking)", "D_TX_FED_LINE_MAP is not an error")
check(FormDiagnostic.objects.get(tax_form=f158, diagnostic_id="D_TX_BONUS_DATE_GATE").severity == "error",
      "W1: D_TX_BONUS_DATE_GATE is severity=error (escalated)", "D_TX_BONUS_DATE_GATE is not an error")

# no rule computes the depreciation catch-up
depr_rule = [r for spec in TX.FORMS for r in spec["rules"] if r["rule_id"] == "R-TX-DEPRDEFER"][0]
check("NO COMPUTATION" in depr_rule["formula"] and depr_rule["rule_type"] == "validation",
      "R1: the depreciation catch-up rule is a VALIDATION carrying NO COMPUTATION",
      "R1 depreciation rule computes something")

# docstring must carry W1..W9 and all nine UNVERIFIED items
doc = SRC[:40000]
check(all(f"W{i}" in doc for i in range(1, 10)), "docstring carries walk items W1..W9",
      "docstring is missing one or more of W1..W9")
check(all(f"U{i}" in doc for i in range(1, 10)), "docstring carries all nine [UNVERIFIED] items U1..U9",
      "docstring is missing one or more of U1..U9")
check("Rev. 4-26/2" in doc and "Rev.8-25/11" in doc and "Rev.9-23/9" in doc
      and "Rev.2-24/35" in doc and "Rev.2-24/8" in doc,
      "docstring provenance block carries the exact form revisions",
      "docstring provenance block is missing a form revision")

# ══════════════════════════════════════════════════════════════════════════
# Report
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print("TX Franchise (margin) tax — TEXAS 2026 REPORT = Delvio TY2025, due 05/15/2026")
print("=" * 74)
for fn in FORM_NUMBERS:
    form = TaxForm.objects.get(form_number=fn)
    print(f"  {fn}: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {len(fa_ids)}   authority sources: {len(source_codes)}")
print("=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
for b in FAILURES:
    print(f"  FAIL  {b}")
print("=" * 74)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
