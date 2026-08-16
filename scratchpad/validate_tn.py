"""Throwaway-SQLite validation for TN_FAE170 (Tennessee Franchise & Excise Tax Return, TY2025).

Checks, in order:
  1. the loader runs and seeds into a throwaway SQLite DB;
  2. **CharField caps** -- rule_id 20 / line_number 20 / assertion_id 20 /
     diagnostic_id 40 / fact_key 100 / topic_name 255 / form_number 50 /
     citation 255 / issuer 100. **Postgres enforces these; SQLite does NOT**,
     so the harness is the only thing standing between an authored spec and a
     pre-seed failure. This is the single most common way this repo breaks.
  3. no duplicate rule_id / line_number / fact_key / diagnostic_id / assertion_id;
  4. every FormRule carries >= 1 authority link (a link-less rule shows a
     warning badge in RS), and rule_links reference only defined rules;
  5. **arithmetic oracles** for every TestScenario -- the MAX(L1,L2) franchise
     pick, the $100 minimum, 'major fraction thereof' rounding, 6.5% excise,
     the J1-vs-J3 CLONE TRAP difference, and the Schedule J ORDERING
     ($50k-then-apportion != apportion-then-$50k);
  6. the safety guard: READY_TO_SEED must ship False, and no computed rule may
     pick the W1 bonus key or compute the W2/U1 OBBBA differential.

ASCII-only prints. Run:  poetry run python scratchpad/validate_tn.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_tn.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.management.commands import load_tn_fae170 as TN  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def near(a, b, tol=0.005):
    return abs(float(a) - float(b)) <= tol


# ══════════════════════════════════════════════════════════════════════════
# 0. SAFETY GUARD — must ship False, and must actually refuse
# ══════════════════════════════════════════════════════════════════════════
_shipped_ready = TN.READY_TO_SEED
check(_shipped_ready is False,
      "SAFETY GUARD: READY_TO_SEED ships False (W1-W10 not yet walked with Ken)",
      f"SAFETY GUARD BREACH: READY_TO_SEED = {_shipped_ready} -- must ship False")

call_command("migrate", run_syncdb=True, verbosity=0)

try:
    call_command("load_tn_fae170", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the loader seeded with READY_TO_SEED=False")
except Exception as e:  # noqa: BLE001
    check("REFUSING TO SEED TN_FAE170" in str(e),
          "SAFETY GUARD: loader refuses to seed while the sentinel is False",
          f"guard raised the wrong error: {e!r}")

# Now flip IN MEMORY ONLY (never on disk) so the spec objects can be inspected.
TN.READY_TO_SEED = True
try:
    call_command("load_tn_fae170", verbosity=0)
    PASSES.append("load_tn_fae170 ran + seeded into throwaway SQLite without error")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_tn_fae170 raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)

# Idempotency — update_or_create throughout means a second run must be clean.
try:
    call_command("load_tn_fae170", verbosity=0)
    PASSES.append("loader is IDEMPOTENT (second run clean; update_or_create throughout)")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"second run raised (not idempotent): {e!r}")

FORM = TaxForm.objects.get(form_number="TN_FAE170")

# ══════════════════════════════════════════════════════════════════════════
# 1. Form identity
# ══════════════════════════════════════════════════════════════════════════
check(FORM.jurisdiction == "TN", "jurisdiction = TN", f"jurisdiction wrong: {FORM.jurisdiction!r}")
check(FORM.tax_year == 2025, "tax_year = 2025", f"tax_year wrong: {FORM.tax_year}")
check(FORM.version == 1, "version = 1", f"version wrong: {FORM.version}")
check(FORM.status == "draft", "status = draft", f"status wrong: {FORM.status!r}")
check(FORM.entity_types == ["1065", "1120S", "1120"],
      "entity_types = ['1065','1120S','1120'] -- ONE form serves THREE federal entity types",
      f"entity_types wrong: {FORM.entity_types}")
check("1040" not in FORM.entity_types,
      "'1040' correctly ABSENT from entity_types (the J2 filer is the SMLLC, not the 1040 -- W10)",
      "'1040' must not be in entity_types: FAE170 is never filed by a 1040")

# ══════════════════════════════════════════════════════════════════════════
# 2. CHARFIELD CAPS — Postgres enforces, SQLite does not. THE BIG ONE.
# ══════════════════════════════════════════════════════════════════════════
CAPS: dict = {}
CAPS["form_number"] = (FORM.form_number, 50)
for r in FormRule.objects.filter(tax_form=FORM):
    CAPS[f"rule_id={r.rule_id}"] = (r.rule_id, 20)
for ln in FormLine.objects.filter(tax_form=FORM):
    CAPS[f"line_number={ln.line_number}"] = (ln.line_number, 20)
for d in FormDiagnostic.objects.filter(tax_form=FORM):
    CAPS[f"diagnostic_id={d.diagnostic_id}"] = (d.diagnostic_id, 40)
for fct in FormFact.objects.filter(tax_form=FORM):
    CAPS[f"fact_key={fct.fact_key}"] = (fct.fact_key, 100)
for ts in TestScenario.objects.filter(tax_form=FORM):
    CAPS[f"scenario_name={ts.scenario_name[:24]}"] = (ts.scenario_name, 255)
for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-TN"):
    CAPS[f"assertion_id={fa.assertion_id}"] = (fa.assertion_id, 20)
for t in AuthorityTopic.objects.filter(topic_code__startswith="tn_"):
    CAPS[f"topic_name={t.topic_code}"] = (t.topic_name, 255)
    CAPS[f"topic_code={t.topic_code}"] = (t.topic_code, 100)
for src in AuthoritySource.objects.filter(source_code__startswith="TN_"):
    CAPS[f"source_code={src.source_code}"] = (src.source_code, 100)
    CAPS[f"citation={src.source_code}"] = (src.citation or "", 255)
    CAPS[f"issuer={src.source_code}"] = (src.issuer or "", 100)
    CAPS[f"jurisdiction_code={src.source_code}"] = (src.jurisdiction_code, 10)

viol = [f"{k}: len {len(v)} > {cap}" for k, (v, cap) in CAPS.items() if len(v) > cap]
check(not viol, f"CHARFIELD CAPS OK ({len(CAPS)} values checked against Postgres limits)",
      "CAP VIOLATIONS (would fail on Postgres, silently pass on SQLite):\n    " + "\n    ".join(viol))

# Spot-assert the four caps that bite most often, individually.
check(max(len(r.rule_id) for r in FormRule.objects.filter(tax_form=FORM)) <= 20,
      "every rule_id <= 20 chars", "a rule_id exceeds 20 chars")
check(max(len(l.line_number) for l in FormLine.objects.filter(tax_form=FORM)) <= 20,
      "every line_number <= 20 chars", "a line_number exceeds 20 chars")
check(max(len(d.diagnostic_id) for d in FormDiagnostic.objects.filter(tax_form=FORM)) <= 40,
      "every diagnostic_id <= 40 chars", "a diagnostic_id exceeds 40 chars")
check(max(len(f.fact_key) for f in FormFact.objects.filter(tax_form=FORM)) <= 100,
      "every fact_key <= 100 chars", "a fact_key exceeds 100 chars")
check(all(len(a.assertion_id) <= 20 for a in FlowAssertion.objects.filter(assertion_id__startswith="FA-TN")),
      "every assertion_id <= 20 chars", "an assertion_id exceeds 20 chars")

# ══════════════════════════════════════════════════════════════════════════
# 3. No duplicates in the authored lists (unique_together would mask these by
#    silently collapsing rows, so check the SOURCE lists, not the DB)
# ══════════════════════════════════════════════════════════════════════════
for label, seq, cap_note in (
    ("rule_id", [r["rule_id"] for r in TN.TN170_RULES], None),
    ("line_number", [l["line_number"] for l in TN.TN170_LINES], None),
    ("fact_key", [f["fact_key"] for f in TN.TN170_FACTS], None),
    ("diagnostic_id", [d["diagnostic_id"] for d in TN.TN170_DIAGNOSTICS], None),
    ("scenario_name", [s["scenario_name"] for s in TN.TN170_SCENARIOS], None),
    ("assertion_id", [a["assertion_id"] for a in TN.FLOW_ASSERTIONS], None),
    ("source_code", [s["source_code"] for s in TN.AUTHORITY_SOURCES], None),
):
    dupes = sorted({x for x in seq if seq.count(x) > 1})
    check(not dupes, f"no duplicate {label} ({len(seq)} authored)", f"DUPLICATE {label}: {dupes}")

# Authored lists survived the DB round trip (nothing silently collapsed).
check(FormRule.objects.filter(tax_form=FORM).count() == len(TN.TN170_RULES),
      f"all {len(TN.TN170_RULES)} rules persisted", "rule count mismatch after seed")
check(FormLine.objects.filter(tax_form=FORM).count() == len(TN.TN170_LINES),
      f"all {len(TN.TN170_LINES)} lines persisted", "line count mismatch after seed")
check(FormFact.objects.filter(tax_form=FORM).count() == len(TN.TN170_FACTS),
      f"all {len(TN.TN170_FACTS)} facts persisted", "fact count mismatch after seed")

# ══════════════════════════════════════════════════════════════════════════
# 4. Authority linkage
# ══════════════════════════════════════════════════════════════════════════
ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form=FORM)
            if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless,
      f"all {FormRule.objects.filter(tax_form=FORM).count()} rules carry >= 1 authority link",
      f"rules with ZERO authority links (warning badge in RS): {ruleless}")

defined = {r["rule_id"] for r in TN.TN170_RULES}
linked = {rl[0] for rl in TN.TN170_RULE_LINKS}
check(not (linked - defined), "rule_links reference only defined rules", f"orphan rule_links: {linked - defined}")
check(not (defined - linked), "every rule appears in rule_links", f"rules missing from rule_links: {defined - linked}")

src_defined = {s["source_code"] for s in TN.AUTHORITY_SOURCES} | set(TN.EXISTING_SOURCES_TO_REFERENCE)
src_linked = {rl[1] for rl in TN.TN170_RULE_LINKS} | {fl[0] for fl in TN.AUTHORITY_FORM_LINKS}
check(not (src_linked - src_defined), "all linked source_codes are defined or declared existing",
      f"undeclared source_codes: {src_linked - src_defined}")

check("TN_TCA_67_4_2004_IRC_DEF" in TN.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE includes the Tier-1 conformity anchor TN_TCA_67_4_2004_IRC_DEF",
      "the Tier-1 conformity anchor is missing from EXISTING_SOURCES_TO_REFERENCE")
check(not AuthoritySource.objects.filter(source_code="TN_TCA_67_4_2004_IRC_DEF").exists(),
      "TN_TCA_67_4_2004_IRC_DEF absent (GATED in _state_conformity_tier1) -- the 'NOT FOUND' warning is EXPECTED",
      "unexpected: the conformity anchor exists in this throwaway DB")
# Rules that link to the gated anchor must still be linked via a seeded source.
for rid in ("R-TN-FILING", "R-TN-DEPR-REGIME"):
    r = FormRule.objects.get(tax_form=FORM, rule_id=rid)
    check(RuleAuthorityLink.objects.filter(form_rule=r).exists(),
          f"{rid} still has an authority link despite the gated anchor being skipped",
          f"{rid} lost all links when the gated anchor was skipped")

# ══════════════════════════════════════════════════════════════════════════
# 5. ARITHMETIC ORACLES
# ══════════════════════════════════════════════════════════════════════════

# --- Schedule A: the greater-of, rounding, the $100 minimum, the cap ---
base, tax = TN._tn_franchise_tax(4_000_000, 0)
check(base == 4_000_000 and near(tax, 10_000.0),
      "FRANCHISE: 4,000,000 net worth -> 40,000 units x $0.25 = $10,000 (= 0.25%)",
      f"franchise wrong: base {base} tax {tax}")

base, tax = TN._tn_franchise_tax(300_000, 1_200_000)
check(base == 1_200_000 and near(tax, 3_000.0),
      "MAX(L1,L2) PICK: Sch. G 1,200,000 beats net worth 300,000 -> $3,000 (L1-only would give $750)",
      f"greater-of wrong: base {base} tax {tax}")

base, tax = TN._tn_franchise_tax(1_200_000, 300_000)
check(base == 1_200_000 and near(tax, 3_000.0),
      "MAX(L1,L2) PICK: symmetric -- net worth wins when it is larger",
      f"greater-of (reversed) wrong: base {base} tax {tax}")

_, tax = TN._tn_franchise_tax(12_000, 0)
check(near(tax, 100.0), "$100 MINIMUM: 12,000 net worth computes $30 -> floored to $100",
      f"$100 minimum not applied: {tax}")

_, tax = TN._tn_franchise_tax(1_000_051, 0)
check(near(tax, 2_500.25),
      "MAJOR FRACTION: remainder 51 (> $50) rounds up -> 10,001 units = $2,500.25",
      f"major-fraction round-up wrong: {tax}")
_, tax = TN._tn_franchise_tax(1_000_050, 0)
check(near(tax, 2_500.00),
      "MAJOR FRACTION: remainder exactly 50 does NOT round up -> 10,000 units = $2,500.00",
      f"major-fraction boundary wrong: {tax}")
check(TN._tn_hundreds_major_fraction(1_000_051) == 10_001
      and TN._tn_hundreds_major_fraction(1_000_050) == 10_000
      and TN._tn_hundreds_major_fraction(0) == 0,
      "MAJOR FRACTION helper: 51->up, 50->down, 0->0", "major-fraction helper wrong")

_, tax = TN._tn_franchise_tax(30_000, 0, proration=0.5)
check(near(tax, 100.0), "PRORATION: $75 x 0.5 = $37.50 -> floored to the $100 minimum",
      f"prorated floor wrong: {tax}")
_, tax = TN._tn_franchise_tax(200_000, 0, proration=0.5)
check(near(tax, 250.0), "PRORATION: 200,000 -> $500 x 0.5 = $250 (above the floor)",
      f"proration wrong: {tax}")
_, tax = TN._tn_franchise_tax(200_000, 0, proration=0.5, is_5253_week_filer=True)
check(near(tax, 500.0), "PRORATION: 52/53-week filer gets NO proration -> full $500",
      f"52/53-week no-proration rule wrong: {tax}")

f1 = TN._tn_f1_net_worth(5_000_000_000, 0, 1.0, is_manufacturer=True)
check(near(f1, 2_000_000_000), "MANUFACTURER CAP: 5B net worth capped at $2B (67-4-2121)",
      f"manufacturer cap wrong: {f1}")
_, tax = TN._tn_franchise_tax(f1, 0)
check(near(tax, 5_000_000.0), "MANUFACTURER CAP: capped base -> $5,000,000 (uncapped would be $12.5M)",
      f"capped franchise tax wrong: {tax}")
f1b = TN._tn_f1_net_worth(1_000_000, 250_000, 0.40)
check(near(f1b, 500_000.0), "SCHEDULE F1: (1,000,000 + 250,000 affiliate add-back) x 0.40 = 500,000",
      f"F1 wrong: {f1b}")
f1c = TN._tn_f1_net_worth(1_000_000, -250_000, 1.0)
check(near(f1c, 1_000_000.0), "SCHEDULE F1: L2 is ONE-WAY -- a negative affiliate figure cannot deduct",
      f"F1 one-way add-back wrong: {f1c}")

# --- Schedule B: 6.5% excise ---
check(near(TN._tn_excise_tax(800_000), 52_000.0), "EXCISE: 800,000 x 6.5% = $52,000",
      f"excise wrong: {TN._tn_excise_tax(800_000)}")
check(near(TN._tn_excise_tax(-250_000), 0.0), "EXCISE: a loss on Line 4 gives ZERO excise tax",
      f"excise loss floor wrong: {TN._tn_excise_tax(-250_000)}")
_, min_tax = TN._tn_franchise_tax(12_000, 0)
check(near(TN._tn_excise_tax(-250_000) + min_tax, 100.0),
      "LOSS YEAR: excise 0 but the $100 minimum franchise tax is still due (C L8 = $100)",
      "loss-year minimum wrong")

# --- THE CLONE TRAP: J1 vs J3 on identical economics ---
j1_l4, j1_l10, j1_l11 = TN._tn_j1_total(500_000, 100_000, 0, 40_000, 150_000, 25_000, 0, 0)
j3_l3, j3_l6, j3_l7 = TN._tn_j3_total(500_000, 100_000, 40_000, 0)
check(near(j1_l4, 600_000) and near(j1_l10, 215_000) and near(j1_l11, 385_000),
      "CLONE TRAP / J1: 600,000 additions - 215,000 deductions = 385,000",
      f"J1 wrong: {j1_l4}/{j1_l10}/{j1_l11}")
check(near(j3_l3, 600_000) and near(j3_l6, 40_000) and near(j3_l7, 560_000),
      "CLONE TRAP / J3: 600,000 additions - 40,000 deductions = 560,000 (NO SE, NO pension)",
      f"J3 wrong: {j3_l3}/{j3_l6}/{j3_l7}")
gap = j3_l7 - j1_l11
check(near(gap, 175_000),
      "CLONE TRAP: the J3-minus-J1 gap is EXACTLY J1 L6 + L7 (150,000 + 25,000 = 175,000)",
      f"clone-trap gap wrong: {gap}")
check(near(TN._tn_excise_tax(j3_l7) - TN._tn_excise_tax(j1_l11), 11_375.0),
      "CLONE TRAP: cloning J1 into J3 would understate excise tax by $11,375 (175,000 x 6.5%)",
      "clone-trap tax difference wrong")
import inspect  # noqa: E402
_j3_params = set(inspect.signature(TN._tn_j3_total).parameters)
check(not any("self_employment" in p or "pension" in p or "qualified_plan" in p for p in _j3_params),
      "CLONE TRAP: _tn_j3_total's signature has NO self-employment / pension parameter",
      f"_tn_j3_total exposes a forbidden parameter: {_j3_params}")
check(len([l for l in TN.TN170_LINES if l["line_number"].startswith("J3-")]) == 7,
      "J3 has exactly 7 lines (1,2,3,4,5,6,7) -- no extra deduction line crept in",
      "J3 line count wrong")

# --- Schedule J2 and J4 entry points ---
j2_l7, j2_l9 = TN._tn_j2_total(120_000, -15_000, 30_000, 0, 5_000, 0, 90_000)
check(near(j2_l7, 140_000) and near(j2_l9, 50_000),
      "J2 SMLLC: 140,000 additions - 90,000 self-employment = 50,000",
      f"J2 wrong: {j2_l7}/{j2_l9}")
j4_l2c, j4_l7, j4_l10, j4_l11 = TN._tn_j4_total(500_000, 0, 0, 0, 0, 40_000, 25_000, 70_000, 30_000)
check(near(j4_l7, 565_000) and near(j4_l10, 100_000) and near(j4_l11, 465_000),
      "J4 DECOUPLING: carryovers used federally added back (565,000); TN full-year deductions (100,000) -> 465,000",
      f"J4 wrong: {j4_l7}/{j4_l10}/{j4_l11}")
j4_l2c2, _, _, _ = TN._tn_j4_total(0, 900_000, 350_000, 0, 0, 0, 0, 0, 0)
check(near(j4_l2c2, 550_000), "J4 REIT: L2c = L2a 900,000 - L2b 350,000 = 550,000",
      f"J4 REIT block wrong: {j4_l2c2}")

# --- THE ORDERING: $50k pre-apportionment vs apportion-first ---
j = TN._tn_schedule_j(1_000_000, 0, 0, 0, 0.30, 0, 0)
check(near(j["L32"], 50_000) and near(j["L34"], 950_000) and near(j["L36"], 285_000) and near(j["L39"], 285_000),
      "ORDERING: 1,000,000 - 50,000 = 950,000; x 0.30 = 285,000 (standard deduction PRE-apportionment)",
      f"ordering wrong: {j}")
correct_tax = TN._tn_excise_tax(j["L39"])
wrong_tax = TN._tn_excise_tax(1_000_000 * 0.30 - 50_000)
check(near(correct_tax, 18_525.0), "ORDERING: correct path -> $18,525 excise",
      f"correct-path tax wrong: {correct_tax}")
check(near(wrong_tax, 16_250.0), "ORDERING: apportion-first path -> $16,250 excise",
      f"apportion-first tax wrong: {wrong_tax}")
check(not near(correct_tax, wrong_tax) and near(correct_tax - wrong_tax, 2_275.0),
      "ORDERING PROVEN DIFFERENT: $50k-then-apportion exceeds apportion-then-$50k by $2,275 "
      "(= 50,000 x (1 - 0.30) x 6.5%) -- apportion-first is WRONG",
      f"the two orderings did NOT differ as expected: {correct_tax} vs {wrong_tax}")

j2 = TN._tn_schedule_j(400_000, 0, 0, 0, 0.50, 60_000, 90_000)
check(near(j2["L36"], 175_000) and near(j2["L39"], 145_000),
      "ORDERING: nonbusiness 60,000 added POST-apportionment, NOL 90,000 LAST -> L39 = 145,000",
      f"post-apportionment ordering wrong: {j2}")
check(near(TN._tn_excise_tax(j2["L39"]), 9_425.0), "ORDERING: 145,000 x 6.5% = $9,425",
      "post-apportionment tax wrong")
j2_wrong = (400_000 - 50_000 + 60_000) * 0.50 - 90_000
check(not near(j2["L39"], j2_wrong),
      "ORDERING PROVEN DIFFERENT: apportioning the nonbusiness allocation gives a different answer",
      "apportioning nonbusiness earnings did not change the result -- ordering not encoded")

j3 = TN._tn_schedule_j(-80_000, 0, 0, 0, 1.0, 0, 0)
check(near(j3["L32"], 0.0) and near(j3["L39"], -80_000),
      "STANDARD DEDUCTION: negative L31 -> L32 = 0 (cannot create or increase a loss)",
      f"standard-deduction floor wrong: {j3}")
j4 = TN._tn_schedule_j(30_000, 0, 0, 0, 1.0, 0, 0)
check(near(j4["L32"], 30_000) and near(j4["L34"], 0.0),
      "STANDARD DEDUCTION: L31 30,000 -> L32 = 30,000 (the LESSER of L31 or $50,000)",
      f"standard-deduction lesser-of wrong: {j4}")
j5 = TN._tn_schedule_j(1_000_000, 0, 0, 75_000, 0.30, 0, 0)
check(near(j5["L34"], 1_025_000), "L33 optional addback is ADDED at L34 (PC 343 (2025))",
      f"L33 optional addback wrong: {j5}")

# --- Schedule M spillover / Schedule K reversals ---
m10, m11 = TN._tn_schedule_m_spillover(75_000, 20_000)
check(near(m10, 30_000) and near(m11, 45_000),
      "SCHEDULE M: spillover = min(50,000 - 20,000, 75,000) = 30,000; L11 = 45,000",
      f"Schedule M spillover wrong: {m10}/{m11}")
m10b, _ = TN._tn_schedule_m_spillover(12_000, 0)
check(near(m10b, 12_000), "SCHEDULE M: spillover capped at Line 9 (12,000), not $50,000",
      f"Schedule M Line 9 cap wrong: {m10b}")
m10c, _ = TN._tn_schedule_m_spillover(75_000, 50_000)
check(near(m10c, 0.0), "SCHEDULE M: spillover never negative when L32 already used the full $50,000",
      f"Schedule M negative floor wrong: {m10c}")

k4, k6 = TN._tn_schedule_k_loss_carryover(-100_000, 15_000, 10_000, 0, 60_000, 0.40)
check(near(k4, -15_000) and near(k6, -6_000),
      "SCHEDULE K: -100,000 + 25,000 + 60,000 = -15,000; x 0.40 = -6,000 (L31 alone would carry -40,000)",
      f"Schedule K wrong: {k4}/{k6}")
k4b, k6b = TN._tn_schedule_k_loss_carryover(-30_000, 50_000, 0, 0, 0, 1.0)
check(near(k4b, 0.0) and near(k6b, 0.0),
      "SCHEDULE K: reversals producing a POSITIVE net -> zero (never turns a loss into income)",
      f"Schedule K positive-to-zero floor wrong: {k4b}/{k6b}")

# --- Schedule N: one ratio, both taxes ---
ratio = TN._tn_sales_factor(2_000_000, 8_000_000)
check(near(ratio, 0.25), "SCHEDULE N: 2,000,000 / 8,000,000 = 0.25 -- ONE ratio to F1 L4 AND J L35",
      f"sales factor wrong: {ratio}")
check(near(TN._tn_sales_factor(500_000, 0), 1.0),
      "SCHEDULE N: zero everywhere-denominator falls back to the form's 'or 100%'",
      "zero-denominator fallback wrong")
n_lines = [l for l in TN.TN170_LINES if l["line_number"].startswith("N-")]
check(len(n_lines) == 1, "SCHEDULE N is ONE LINE on the TY2025 form (no property, no payroll, no 11x/13)",
      f"Schedule N has {len(n_lines)} lines -- must be exactly 1")

# --- Schedule C: credit cap + Green Energy exception ---
c = TN._tn_schedule_c(10_000, 52_000, 70_000, 0, 0, green_energy_credit=5_000)
check(near(c["L8"], 62_000) and near(c["L9"], 67_000) and near(c["L10"], 0.0),
      "SCHEDULE C: non-green credits capped at L8 (62,000) + uncapped Green Energy (5,000) = 67,000; L10 = 0",
      f"Schedule C credit cap wrong: {c}")
c2 = TN._tn_schedule_c(10_000, 52_000, 70_000, 0, 0, green_energy_credit=0)
check(near(c2["L9"], 62_000), "SCHEDULE C: without a Green Energy credit the cap binds hard at L8",
      f"Schedule C hard cap wrong: {c2}")
c3 = TN._tn_schedule_c(100, 0, 5_000, 0, 0, 0)
check(near(c3["L10"], 0.0),
      "U8/W8: credits DO drive net tax below the $100 minimum on the form's own arithmetic (flagged, not assumed)",
      f"U8 arithmetic wrong: {c3}")
c4 = TN._tn_schedule_c(10_000, 52_000, 0, 70_000, 0, 0)
check(near(c4["refund"], 8_000.0) and near(c4["amount_due"], 0.0),
      "SCHEDULE C: payments 70,000 against 62,000 net tax -> 8,000 overpayment",
      f"Schedule C refund wrong: {c4}")

# --- Schedule T Part 1 ---
t11 = TN._tn_schedule_t_part1(3_000_000, 0.01, 10_000, 10_000, 52_000, 5_000)
check(near(t11, 31_000.0),
      "SCHEDULE T: min(L5 40,000, L7 31,000, L10 57,000) = 31,000 -- the 50% limitation binds",
      f"Schedule T wrong: {t11}")
t11b = TN._tn_schedule_t_part1(500_000, 0.01, 0, 10_000, 52_000, 0)
check(near(t11b, 5_000.0), "SCHEDULE T: min(L5 5,000, L7 31,000, L10 62,000) = 5,000 -- the credit itself binds",
      f"Schedule T (credit binds) wrong: {t11b}")

# --- Schedule G rent multiples ---
g15 = TN._tn_schedule_g_total(500_000, 100_000, 50_000, 20_000, 10_000)
check(near(g15, 1_500_000.0),
      "SCHEDULE G: 500,000 + (100,000 x8) + (50,000 x3) + (20,000 x2) + (10,000 x1) = 1,500,000",
      f"Schedule G total wrong: {g15}")
mults = TN._yk(TN.TN_SCHED_G_RENT_MULTIPLES, 2025)
check((mults["real_property"], mults["mfg_machinery_equipment"],
       mults["furniture_office_equipment"], mults["delivery_mobile_equipment"]) == (8, 3, 2, 1),
      "SCHEDULE G multipliers are 8/3/2/1 (printed on the current form face)",
      f"Schedule G multipliers wrong: {mults}")
check(near(TN._tn_schedule_g_total(0, -50_000, 0, 0, 0), 0.0),
      "SCHEDULE G: net annual rental is FLOORED AT ZERO (sub-rent netting never goes negative)",
      "Schedule G negative-rent floor wrong")

# --- Estimates and extension ---
check(TN._tn_estimate_required(6_000, 8_000) is True,
      "ESTIMATES: prior 6,000 and current 8,000 -> required (BOTH years clear $5,000)",
      "estimate test wrong (both-years case)")
check(TN._tn_estimate_required(4_000, 20_000) is False,
      "ESTIMATES: prior 4,000 -> NOT required (one big year does not trigger estimates)",
      "estimate test wrong (prior below threshold)")
check(TN._tn_estimate_required(20_000, 4_000) is False,
      "ESTIMATES: current 4,000 -> NOT required (the test is conjunctive)",
      "estimate test wrong (current below threshold)")
check(near(TN._tn_installment_standard(6_000, 8_000), 1_500.0),
      "ESTIMATES: min(25% x 6,000 = 1,500; 25% x 80% x 8,000 = 1,600) = 1,500",
      f"installment wrong: {TN._tn_installment_standard(6_000, 8_000)}")
check(near(TN._tn_extension_payment_required(20_000, 0), 100.0),
      "EXTENSION: prior-year liability of ZERO -> the required payment is $100",
      "extension $100 prior-zero rule wrong")
check(near(TN._tn_extension_payment_required(20_000, 15_000), 15_000.0),
      "EXTENSION: min(90% x 20,000 = 18,000; 100% x 15,000 = 15,000) = 15,000",
      "extension 90/100 test wrong")

# --- Verified constants ---
check(TN._yk(TN.TN_EXCISE_RATE, 2025) == "0.065", "constant: excise rate 6.5%", "excise rate constant wrong")
check(TN._yk(TN.TN_FRANCHISE_PER_HUNDRED, 2025) == "0.25", "constant: 25c per $100", "franchise rate constant wrong")
check(TN._yk(TN.TN_FRANCHISE_MINIMUM, 2025) == 100, "constant: $100 minimum franchise tax", "minimum constant wrong")
check(TN._yk(TN.TN_EXCISE_STANDARD_DEDUCTION, 2025) == 50_000, "constant: $50,000 excise standard deduction",
      "standard deduction constant wrong")
check(TN._yk(TN.TN_MANUFACTURER_BASE_CAP, 2025) == 2_000_000_000, "constant: $2B manufacturer cap",
      "manufacturer cap constant wrong")
check(TN._yk(TN.TN_NOL_CARRYFORWARD_YEARS, 2025) == 15, "constant: 15-year TN NOL carryforward",
      "NOL years constant wrong")
check(TN._yk(TN.TN_179_LIMIT, 2025) == 2_500_000 and TN._yk(TN.TN_179_PHASEOUT, 2025) == 4_000_000,
      "constant: §179 CONFORMS at the full OBBBA $2,500,000 / $4,000,000",
      "§179 constants wrong -- TN conforms via rolling conformity")
check(len(TN._yk(TN.TN_EXEMPTIONS_REQUIRING_FAE183, 2025)) == 10
      and TN._yk(TN.TN_EXEMPTION_COUNT, 2025) == 17,
      "constant: 17 exemptions, exactly 10 requiring FAE183",
      "exemption counts wrong")

# --- W1/U2: the bonus percentages are verified; the KEY must NOT be picked ---
check(near(TN._tn_tcja_bonus_pct(2025), 0.40) and near(TN._tn_tcja_bonus_pct(2024), 0.60)
      and near(TN._tn_tcja_bonus_pct(2023), 0.80) and near(TN._tn_tcja_bonus_pct(2026), 0.20)
      and near(TN._tn_tcja_bonus_pct(2027), 0.00) and near(TN._tn_tcja_bonus_pct(2022), 1.00),
      "TCJA PHASE-DOWN: 2022 100% / 2023 80% / 2024 60% / 2025 40% / 2026 20% / 2027+ 0%",
      "TCJA phase-down table wrong")
check(TN._tn_tcja_bonus_pct(None) is None,
      "W1/U2: _tn_tcja_bonus_pct REFUSES to derive a key -- no key_year, no answer",
      "the bonus helper invented a key year")
_pct_sig = set(inspect.signature(TN._tn_tcja_bonus_pct).parameters)
check("key_year" in _pct_sig and not any(k in _pct_sig for k in ("acquired_date", "placed_in_service_date")),
      "W1/U2: the helper takes a caller-supplied key_year, never a date it would have to key itself",
      f"the bonus helper takes a date parameter (would force a key): {_pct_sig}")
_depr = FormRule.objects.get(tax_form=FORM, rule_id="R-TN-DEPR-REGIME")
check(_depr.rule_type == "classification",
      "W1/W2: R-TN-DEPR-REGIME is a CLASSIFICATION rule -- it encodes structure, not a computed differential",
      f"R-TN-DEPR-REGIME must not be a calculation rule: {_depr.rule_type}")
check(not any(r["rule_type"] == "calculation" and "bonus" in " ".join(r.get("outputs", [])).lower()
              for r in TN.TN170_RULES),
      "W2/U1: NO calculation rule outputs a TN bonus differential (RED-deferred R13)",
      "a calculation rule computes the OBBBA bonus differential -- must be RED-deferred")

# ══════════════════════════════════════════════════════════════════════════
# 6. RED-defer coverage — the house rule: every defer gets its own diagnostic
# ══════════════════════════════════════════════════════════════════════════
REQUIRED_DIAGS = [
    "D_TN170_SCHED_G",          # R1
    "D_TN170_SCHED_F2",         # R2
    "D_TN170_SCHED_N1",         # R3
    "D_TN170_SCHED_OPR",        # R4
    "D_TN170_FAE174",           # R5
    "D_TN170_SCHED_X",          # R6
    "D_TN170_SCHED_QP",         # R7
    "D_TN170_SCHED_BP",         # R8
    "D_TN170_SCHED_T_RECAP",    # R9
    "D_TN170_CERT_DIST_SALES",  # R10
    "D_TN170_ANNUALIZED_EST",   # R11
    "D_TN170_FAE183",           # R12
    "D_TN170_OBBBA_BONUS_DIFF", # R13
    "D_TN170_FORM_IE",          # R14
    "D_TN170_BUS_428",          # R15
]
present = set(FormDiagnostic.objects.filter(tax_form=FORM).values_list("diagnostic_id", flat=True))
missing = [d for d in REQUIRED_DIAGS if d not in present]
check(not missing, "RED-DEFER COVERAGE: all 15 defers (R1-R15) have their own diagnostic -- no silent gap",
      f"RED-defers with NO diagnostic: {missing}")

for did, why in (
    ("D_TN170_J3_NO_SE_PENSION", "the J1->J3 clone trap"),
    ("D_TN170_J_ORDERING", "the Schedule J ordering"),
    ("D_TN170_BONUS_KEY_W1", "the W1 acquired-vs-placed-in-service escalation"),
    ("D_TN170_MIN_TAX_VS_CREDITS", "U8 credits below the $100 minimum"),
    ("D_TN170_SHORT_PERIOD_APPT", "U3 short 2025 periods"),
    ("D_TN170_L13_L28A_ERRATUM", "U4 the Line 27a erratum"),
    ("D_TN170_SMLLC_J2_TRIGGER", "W10 the SMLLC trigger"),
    ("D_TN170_NO_PTET_NO_1040", "no PTET / no individual return"),
):
    check(did in present, f"diagnostic present for {why} ({did})", f"MISSING diagnostic {did} ({why})")

_g = FormDiagnostic.objects.get(tax_form=FORM, diagnostic_id="D_TN170_SCHED_G")
check("MeF" not in _g.message and "accepted-forms" not in _g.message,
      "R1 diagnostic text carries NO refuted MeF claim (verification C1)",
      "R1 diagnostic still asserts the REFUTED 'not in the MeF accepted-forms list' rationale")
_fi = FormDiagnostic.objects.get(tax_form=FORM, diagnostic_id="D_TN170_FAE174")
check(_fi.severity == "error" and "FAE174" in _fi.message,
      "R5 FAE174 is a HARD STOP (severity=error), per the verbatim 'instead of Form FAE170'",
      "R5 FAE174 must be a hard stop")

# ══════════════════════════════════════════════════════════════════════════
# 7. Structural coverage — the four entry points and the flow assertions
# ══════════════════════════════════════════════════════════════════════════
for pre, n, label in (("J1-", 11, "J1 (1065)"), ("J2-", 9, "J2 (SMLLC)"),
                      ("J3-", 7, "J3 (1120S)"), ("J4-", 13, "J4 (1120)")):
    got = len([l for l in TN.TN170_LINES if l["line_number"].startswith(pre)])
    check(got == n, f"entry point {label}: {n} lines mapped", f"{label} has {got} lines, expected {n}")
check(len([l for l in TN.TN170_LINES if l["line_number"].startswith("J-")]) == 40,
      "Schedule J: 40 lines (L1, 27 numbered modifications as 28 fields incl. 28a/28b, L15, L30, L31-L39)",
      f"Schedule J line count wrong: {len([l for l in TN.TN170_LINES if l['line_number'].startswith('J-')])}")
check(len(TN.J_ADDITIONS) == 13 and len(TN.J_DEDUCTIONS) == 15,
      "Schedule J modifications: 13 additions (L2-L14) and 14 deduction lines in 15 fields (28a/28b)",
      f"modification table sizes wrong: {len(TN.J_ADDITIONS)}/{len(TN.J_DEDUCTIONS)}")
check(any(l["line_number"] == "J-28a" for l in TN.TN170_LINES)
      and any(l["line_number"] == "J-28b" for l in TN.TN170_LINES),
      "Schedule J Line 28 SPLITS into 28a and 28b", "the 28a/28b split is missing")
check("excluding 28b" in next(l["description"] for l in TN.TN170_LINES if l["line_number"] == "J-30"),
      "Schedule J Line 30 description records that Line 28b is EXCLUDED",
      "L30 does not record the 28b exclusion")

fa_ids = set(FlowAssertion.objects.filter(assertion_id__startswith="FA-TN").values_list("assertion_id", flat=True))
for fid in ("FA-TN-J-ENTRY", "FA-TN-J1J3", "FA-TN-ORDER", "FA-TN-FRANCH-MAX",
            "FA-TN-MIN100", "FA-TN-EXCISE", "FA-TN-SCHN-ONE", "FA-TN-J30-28B",
            "FA-TN-SCHK-REV", "FA-TN-J4-BASIS", "FA-TN-NO-PTET", "FA-TN-DEPR-OPEN"):
    check(fid in fa_ids, f"flow assertion {fid} present", f"MISSING flow assertion {fid}")

# ══════════════════════════════════════════════════════════════════════════
# 8. Report
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print(f"  TN_FAE170: facts {FormFact.objects.filter(tax_form=FORM).count()} / "
      f"rules {FormRule.objects.filter(tax_form=FORM).count()} / "
      f"lines {FormLine.objects.filter(tax_form=FORM).count()} / "
      f"diag {FormDiagnostic.objects.filter(tax_form=FORM).count()} / "
      f"tests {TestScenario.objects.filter(tax_form=FORM).count()} / "
      f"FA {len(fa_ids)} / sources {AuthoritySource.objects.filter(source_code__startswith='TN_').count()}")
print(f"  authority links: {RuleAuthorityLink.objects.count()}   "
      f"entity_types: {FORM.entity_types}   READY_TO_SEED shipped: {_shipped_ready}")
print("=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
for f in FAILURES:
    print(f"  FAIL  {f}")
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
