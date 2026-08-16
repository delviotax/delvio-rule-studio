"""Throwaway-SQLite validation for the FL entity batch: FL_F1120 + FL_F1065 (TY2025).

Checks CharField caps (rule_id 20 / line_number 20 / assertion_id 20 / diagnostic_id 40 /
fact_key 100 / topic_name 255 / form_number 50 / label 255 / scenario_name 255 / citation 255 --
Postgres enforces these, SQLite does NOT, so this is the pre-seed gate); every FormRule has >= 1
authority link; no duplicate ids anywhere; rule_links reference defined rules and defined sources;
and ARITHMETIC ORACLES driven through the loader's own helper functions:
  * the four Rule 12C-1.022(6)(c) worked examples for the F-1065 filing gate
  * the S-corp federal 1120S Line 23c trigger (both directions + the W3 LIFO edge)
  * the 1/7-over-7 Sec.168(k) bonus recovery, incl. vintage expiry and the QIP carve-out
  * 25/25/50 apportionment, all three zero-denominator reweights, AND the load-bearing
    NEGATIVE test that a small-but-nonzero denominator is NOT reweighted (W4)
  * the apportionment-gate 100% outcome (W7)
  * the $50,000 exemption (full / lesser-of / zero floor / short-year proration)
  * the 5.5% rate and the Schedule V credit cap
  * the two-tier Florida NOL
  * the Schedule I <-> Schedule V single-pass credit add-back map

ASCII-only output. Run: poetry run python scratchpad/validate_fl.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_fl.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm,
)
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.management.commands import load_fl_entity as FL  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


# ══════════════════════════════════════════════════════════════════════
# 0. The loader must SHIP with READY_TO_SEED = False, and must REFUSE to run.
# ══════════════════════════════════════════════════════════════════════
check(FL.READY_TO_SEED is False,
      "SAFETY GUARD: READY_TO_SEED ships False (W1 gates this loader)",
      f"SAFETY GUARD BREACHED: READY_TO_SEED = {FL.READY_TO_SEED} — must ship False")

call_command("migrate", run_syncdb=True, verbosity=0)

try:
    call_command("load_fl_entity", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: load_fl_entity seeded with READY_TO_SEED False")
except Exception as exc:  # noqa: BLE001
    check("REFUSING TO SEED" in str(exc),
          "Guard refuses to seed while READY_TO_SEED is False",
          f"Guard raised the wrong error: {exc!r}")

# Now flip IN MEMORY ONLY (never on disk) so the content can be validated.
FL.READY_TO_SEED = True
try:
    call_command("load_fl_entity", verbosity=0)
    PASSES.append("load_fl_entity ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_fl_entity raised: {exc!r}")
    print("\n".join(f"  FAIL  {f}" for f in FAILURES))
    sys.exit(1)

FORM_SHAPE = {"FL_F1120": ("FL", ["1120", "1120S"]), "FL_F1065": ("FL", ["1065"])}

# ══════════════════════════════════════════════════════════════════════
# 1. CharField caps — the most common pre-seed failure in this repo.
#    Postgres enforces these; SQLite silently accepts overlong values.
# ══════════════════════════════════════════════════════════════════════
CAPS: dict = {}
for fn in FORM_SHAPE:
    form = TaxForm.objects.get(form_number=fn)
    CAPS[f"form_number={fn}"] = (form.form_number, 50)
    CAPS[f"form_title={fn}"] = (form.form_title, 255)
    CAPS[f"jurisdiction={fn}"] = (form.jurisdiction, 20)
    CAPS[f"status={fn}"] = (form.status, 20)
    for r in FormRule.objects.filter(tax_form=form):
        CAPS[f"rule_id={r.rule_id}"] = (r.rule_id, 20)
        CAPS[f"rule_title={r.rule_id}"] = (r.title, 255)
        CAPS[f"rule_type={r.rule_id}"] = (r.rule_type, 20)
    for d in FormDiagnostic.objects.filter(tax_form=form):
        CAPS[f"diagnostic_id={d.diagnostic_id}"] = (d.diagnostic_id, 40)
        CAPS[f"diag_title={d.diagnostic_id}"] = (d.title, 255)
        CAPS[f"diag_sev={d.diagnostic_id}"] = (d.severity, 20)
    for ln in FormLine.objects.filter(tax_form=form):
        CAPS[f"line_number={fn}:{ln.line_number}"] = (ln.line_number, 20)
        CAPS[f"line_type={fn}:{ln.line_number}"] = (ln.line_type, 20)
    for fct in FormFact.objects.filter(tax_form=form):
        CAPS[f"fact_key={fct.fact_key}"] = (fct.fact_key, 100)
        CAPS[f"fact_label={fct.fact_key}"] = (fct.label, 255)
        CAPS[f"fact_dtype={fct.fact_key}"] = (fct.data_type, 20)
    for ts in form.test_scenarios.all():
        CAPS[f"scenario_name={ts.scenario_name[:30]}"] = (ts.scenario_name, 255)
        CAPS[f"scenario_type={ts.scenario_name[:30]}"] = (ts.scenario_type, 20)
for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-FL"):
    CAPS[f"assertion_id={fa.assertion_id}"] = (fa.assertion_id, 20)
    CAPS[f"assertion_title={fa.assertion_id}"] = (fa.title, 255)
    CAPS[f"assertion_type={fa.assertion_id}"] = (fa.assertion_type, 20)
for t in AuthorityTopic.objects.all():
    CAPS[f"topic_code={t.topic_code}"] = (t.topic_code, 100)
    CAPS[f"topic_name={t.topic_code}"] = (t.topic_name, 255)
for s in AuthoritySource.objects.filter(jurisdiction_code="FL"):
    CAPS[f"source_code={s.source_code}"] = (s.source_code, 100)
    CAPS[f"citation={s.source_code}"] = (s.citation or "", 255)
    CAPS[f"issuer={s.source_code}"] = (s.issuer or "", 100)
    CAPS[f"jurisdiction_code={s.source_code}"] = (s.jurisdiction_code, 10)
    CAPS[f"source_type={s.source_code}"] = (s.source_type, 40)
    CAPS[f"source_rank={s.source_code}"] = (s.source_rank, 30)
    for e in s.excerpts.all():
        CAPS[f"excerpt_label={e.excerpt_label[:30]}"] = (e.excerpt_label or "", 255)

viol = [f"{k}: len {len(v)} > {cap}" for k, (v, cap) in CAPS.items() if len(v) > cap]
check(not viol, f"CharField caps OK ({len(CAPS)} values checked)",
      "CAP VIOLATIONS:\n    " + "\n    ".join(viol))

# Explicit spot assertions on the caps that bite hardest.
check(all(len(r["rule_id"]) <= 20 for s in FL.FORMS for r in s["rules"]),
      "every rule_id <= 20 chars", "rule_id > 20 chars present")
check(all(len(d["diagnostic_id"]) <= 40 for s in FL.FORMS for d in s["diagnostics"]),
      "every diagnostic_id <= 40 chars", "diagnostic_id > 40 chars present")
check(all(len(ln["line_number"]) <= 20 for s in FL.FORMS for ln in s["lines"]),
      "every line_number <= 20 chars", "line_number > 20 chars present")
check(all(len(f["fact_key"]) <= 100 for s in FL.FORMS for f in s["facts"]),
      "every fact_key <= 100 chars", "fact_key > 100 chars present")
check(all(len(a["assertion_id"]) <= 20 for a in FL.FLOW_ASSERTIONS),
      "every assertion_id <= 20 chars", "assertion_id > 20 chars present")

# ══════════════════════════════════════════════════════════════════════
# 2. No duplicate ids; every rule has >= 1 authority link; links resolve.
# ══════════════════════════════════════════════════════════════════════
declared_sources = {s["source_code"] for s in FL.AUTHORITY_SOURCES} | set(FL.EXISTING_SOURCES_TO_REFERENCE)
for spec in FL.FORMS:
    fn = spec["identity"]["form_number"]
    form = TaxForm.objects.get(form_number=fn)
    for key, field in (("facts", "fact_key"), ("rules", "rule_id"),
                       ("lines", "line_number"), ("diagnostics", "diagnostic_id")):
        ids = [row[field] for row in spec[key]]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        check(not dupes, f"{fn}: no duplicate {field} ({len(ids)} rows)", f"{fn}: DUPLICATE {field}: {dupes}")
    names = [t["scenario_name"] for t in spec["scenarios"]]
    check(len(names) == len(set(names)), f"{fn}: no duplicate scenario_name", f"{fn}: duplicate scenario_name")

    ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form=form)
                if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
    check(not ruleless, f"{fn}: all {FormRule.objects.filter(tax_form=form).count()} rules have >= 1 authority link",
          f"{fn}: rules with NO authority link: {ruleless}")

    defined = {r["rule_id"] for r in spec["rules"]}
    linked = {rl[0] for rl in spec["rule_links"]}
    check(not (linked - defined), f"{fn}: rule_links reference defined rules", f"{fn}: orphan rule_links {linked - defined}")
    check(not (defined - linked), f"{fn}: every rule appears in rule_links", f"{fn}: unlinked rules {defined - linked}")
    bad_src = {rl[1] for rl in spec["rule_links"]} - declared_sources
    check(not bad_src, f"{fn}: rule_links reference declared sources", f"{fn}: undeclared sources {bad_src}")
    bad_lvl = {rl[2] for rl in spec["rule_links"]} - {"primary", "secondary", "interpretive", "implementation"}
    check(not bad_lvl, f"{fn}: rule_link support levels valid", f"{fn}: bad support levels {bad_lvl}")

fa_ids = [a["assertion_id"] for a in FL.FLOW_ASSERTIONS]
check(len(fa_ids) == len(set(fa_ids)), "no duplicate assertion_id", "DUPLICATE assertion_id present")
all_diag = [d["diagnostic_id"] for s in FL.FORMS for d in s["diagnostics"]]
check(len(all_diag) == len(set(all_diag)), "no duplicate diagnostic_id across both forms", "duplicate diagnostic_id across forms")
bad_form_links = {fl[1] for fl in FL.AUTHORITY_FORM_LINKS} - set(FORM_SHAPE)
check(not bad_form_links, "AUTHORITY_FORM_LINKS point at FL_F1120 / FL_F1065", f"bad form codes: {bad_form_links}")

# ══════════════════════════════════════════════════════════════════════
# 3. Identity: jurisdiction, tax year, entity_types, status, form numbers.
# ══════════════════════════════════════════════════════════════════════
check(FL.FORM_JURISDICTION == "FL", "FORM_JURISDICTION = FL", f"wrong jurisdiction {FL.FORM_JURISDICTION!r}")
check(FL.FORM_TAX_YEAR == 2025, "FORM_TAX_YEAR = 2025", f"wrong tax year {FL.FORM_TAX_YEAR}")
check(FL.FORM_VERSION == 1 and FL.FORM_STATUS == "draft", "FORM_VERSION = 1, FORM_STATUS = draft", "wrong version/status")
for fn, (juris, ets) in FORM_SHAPE.items():
    form = TaxForm.objects.get(form_number=fn)
    check(form.jurisdiction == juris, f"{fn}: jurisdiction = {juris}", f"{fn}: jurisdiction {form.jurisdiction!r}")
    check(form.tax_year == 2025, f"{fn}: tax_year = 2025", f"{fn}: tax_year {form.tax_year}")
    check(form.entity_types == ets, f"{fn}: entity_types = {ets}", f"{fn}: entity_types {form.entity_types}")
check(FL.EXISTING_SOURCES_TO_REFERENCE == ["FL_FS_220_03_CONFORMITY"],
      "EXISTING_SOURCES_TO_REFERENCE anchors FL_FS_220_03_CONFORMITY (gated/unseeded -> NOT FOUND warning is CORRECT)",
      f"conformity anchor wrong: {FL.EXISTING_SOURCES_TO_REFERENCE}")

# ══════════════════════════════════════════════════════════════════════
# 4. ARITHMETIC ORACLES
# ══════════════════════════════════════════════════════════════════════

# ---- 4a. The four Rule 12C-1.022(6)(c) worked examples (the F-1065 gate) ----
ex1 = FL._fl_file_f1065(["individual", "individual", "individual"])
check(ex1 is False, "12C-1.022(6)(c) Ex.1 AB (three individuals) -> NO F-1065", f"Ex.1 wrong: {ex1}")
ex2 = FL._fl_file_f1065(["individual", "individual", "c_corp"])
check(ex2 is True, "12C-1.022(6)(c) Ex.2 BC (2 individuals + Corporation X) -> F-1065 REQUIRED", f"Ex.2 wrong: {ex2}")
ex3 = FL._fl_file_f1065(["individual", "individual", "foreign_corp"])
check(ex3 is True, "12C-1.022(6)(c) Ex.3 CD (2 individuals + NY corporation) -> REQUIRED (solely by virtue of membership)", f"Ex.3 wrong: {ex3}")
ex4 = FL._fl_file_f1065(["individual", "individual", "s_corp"])
check(ex4 is False, "12C-1.022(6)(c) Ex.4 DE (2 individuals + S corporation) -> NO F-1065 (the (6)(b) carve-out)", f"Ex.4 wrong: {ex4}")
check(FL._fl_file_f1065(["individual", "s_corp", "c_corp"]) is True,
      "(6)(b) carve-out does NOT apply once a C corporation joins the roster", "S+C corp roster wrong")
check(FL._fl_file_f1065(["individual", "partnership"]) is None,
      "R10: a partnership partner yields UNDETERMINED (never a guess)", "tiered case did not return None")
check(FL._fl_file_f1065(["c_corp"], is_florida_partnership=False) is False,
      "a NON-Florida partnership has no F-1065 obligation", "non-FL partnership wrong")
check(FL._fl_foreign_corp_partner_files_f1120(["individual", "foreign_corp"]) is True,
      "foreign corporate partner separately files its own F-1120 (two returns)", "foreign-partner trigger wrong")
check(FL._fl_foreign_corp_partner_files_f1120(["individual", "individual"]) is False,
      "no foreign corporate partner -> no second F-1120", "foreign-partner false positive")

# ---- 4b. The S-corp Line 23c trigger ----
check(FL._fl_file_f1120_scorp(18000) is True, "S corp with 1120S Line 23c = 18,000 -> F-1120 REQUIRED", "23c>0 trigger wrong")
check(FL._fl_file_f1120_scorp(0) is False, "S corp with 1120S Line 23c = 0 -> NO Florida return", "23c=0 trigger wrong")
check(FL._fl_file_f1120_scorp(None) is False, "S corp with no 1120S Line 23c value -> NO Florida return", "23c None trigger wrong")
check(FL._fl_file_f1120_scorp(0.01) is True, "the trigger is strictly > 0 (W3 width tension preserved, not resolved)", "23c boundary wrong")

# ---- 4c. Sec.168(k) bonus: 1/7 per year over SEVEN years ----
check(approx(FL._fl_bonus_recovery({2025: 700000}, 2025), 100000.0),
      "bonus 1/7: 700,000 addition -> 100,000 subtraction in the addition year",
      f"1/7 wrong: {FL._fl_bonus_recovery({2025: 700000}, 2025)}")
check(approx(FL._fl_bonus_recovery({2025: 700000}, 2031), 100000.0),
      "bonus vintage still open in the SEVENTH year (2025 vintage, year 2031)", "seventh-year vintage wrong")
check(approx(FL._fl_bonus_recovery({2025: 700000}, 2032), 0.0),
      "bonus vintage CLOSED in the eighth year (2032)", "vintage did not close after seven years")
check(approx(FL._fl_bonus_recovery({2021: 140000, 2023: 210000, 2025: 700000}, 2025), 150000.0),
      "three open vintages: 20,000 + 30,000 + 100,000 = 150,000",
      f"multi-vintage wrong: {FL._fl_bonus_recovery({2021: 140000, 2023: 210000, 2025: 700000}, 2025)}")
check(approx(FL._fl_bonus_recovery({2018: 700000, 2025: 700000}, 2025), 100000.0),
      "the 2018 vintage (2018-2024) is closed in 2025; only the 2025 vintage contributes", "vintage expiry wrong")
check(approx(FL._fl_bonus_recovery({}, 2025), 0.0), "no vintages -> zero recovery", "empty vintages wrong")
# QIP carve-out: only the NON-QIP half rides the 1/7 track.
_l21, _qip = 1000000, 300000
check(approx(FL._fl_bonus_recovery({2025: _l21 - _qip}, 2025), 100000.0),
      "QIP carve-out: 1,000,000 L21 less 300,000 QIP -> 700,000/7 = 100,000 on Sch II L9",
      "QIP carve-out from the 1/7 track wrong")
check(FL._yk(FL.FL_BONUS_RECOVERY_YEARS) == 7, "recovery period is SEVEN years", "recovery period constant wrong")

# ---- 4d. Apportionment 25/25/50 and the zero-denominator reweights ----
f_all = FL._fl_apportionment((200000, 1000000), (300000, 1000000), (400000, 2000000))
check(approx(f_all, 0.225), "25/25/50: .25(.20) + .25(.30) + .50(.20) = 0.225", f"25/25/50 wrong: {f_all}")
f_nop = FL._fl_apportionment((0, 0), (300000, 1000000), (400000, 2000000))
check(approx(f_nop, 0.233333), "zero PROPERTY denominator -> payroll 33-1/3%, sales 66-2/3% = 0.233333", f"property-zero reweight wrong: {f_nop}")
f_nopay = FL._fl_apportionment((200000, 1000000), (0, 0), (400000, 2000000))
check(approx(f_nopay, 0.2), "zero PAYROLL denominator -> property 33-1/3%, sales 66-2/3% = 0.200000", f"payroll-zero reweight wrong: {f_nopay}")
f_nosale = FL._fl_apportionment((200000, 1000000), (300000, 1000000), (0, 0))
check(approx(f_nosale, 0.25), "zero SALES denominator -> property 50%, payroll 50% = 0.25", f"sales-zero reweight wrong: {f_nosale}")
f_two = FL._fl_apportionment((0, 0), (0, 0), (400000, 2000000))
check(approx(f_two, 0.20), "TWO zero denominators -> the remaining factor at 100% = 0.20", f"two-zero reweight wrong: {f_two}")
check(FL._fl_apportionment((0, 0), (0, 0), (0, 0)) is None,
      "all three denominators zero -> no apportionment fraction exists (None)", "all-zero case wrong")
# *** W4 — the load-bearing NEGATIVE test ***
f_tiny = FL._fl_apportionment((0, 1), (300000, 1000000), (400000, 2000000))
check(approx(f_tiny, 0.175),
      "W4: tiny-but-NONZERO property denominator keeps 25/25/50 (0.175) - NO auto-reweight",
      f"W4 BREACH: software reweighted a nonzero denominator -> {f_tiny} (should be 0.175, NOT 0.233333)")
check(not approx(f_tiny, 0.233333),
      "W4: the nonzero-denominator result is NOT the 33-1/3 / 66-2/3 reweight",
      "W4 BREACH: nonzero denominator produced the insignificance reweight")
check(FL._yk(FL.FL_APPORT_WEIGHTS) == {"property": 0.25, "payroll": 0.25, "sales": 0.50},
      "weights constant is 25 property / 25 payroll / 50 sales", "weights constant wrong")
check(FL._yk(FL.FL_APPORT_DECIMALS) == 6, "apportionment fraction rounds to SIX decimal places", "decimals constant wrong")
# Property factor: original cost, beginning/end averaged, rent at 8x.
pnum, pden = FL._fl_property_factor(100000, 300000, 1000000, 1000000, rent_fl=5000, rent_ew=20000)
check(approx(pnum, 240000) and approx(pden, 1160000),
      "Sch III-B: (100k+300k)/2 + 8x5,000 = 240,000 FL; (1m+1m)/2 + 8x20,000 = 1,160,000 everywhere",
      f"property factor wrong: {pnum} / {pden}")

# ---- 4e. The apportionment gate costs 100% (W7) ----
check(approx(FL._fl_florida_portion(1000000, False), 1000000),
      "W7: gate FAILURE -> Line 7 = Line 6 in full (100% of adjusted federal income)",
      "gate-failure 100% outcome wrong")
check(approx(FL._fl_florida_portion(1000000, True, 0.20), 200000),
      "gate CLEARED -> Line 7 = Line 6 x apportionment fraction (1,000,000 x 0.20 = 200,000)",
      "cleared-gate apportionment wrong")
check(FL._fl_florida_portion(1000000, False) != 200000,
      "a P.L. 86-272-only footprint does NOT get the 20% sales-factor answer", "gate bypassed")

# ---- 4f. The $50,000 exemption ----
check(approx(FL._fl_exemption(400000, 0), 50000), "$50,000 exemption: full amount on a 400,000 base", "exemption full wrong")
check(approx(FL._fl_exemption(30000, 0), 30000), "exemption is the LESSER of 50,000 or (L7 + L8) -> 30,000", "lesser-of wrong")
check(approx(FL._fl_exemption(-75000, 0), 0), "exemption is ZERO when L7 + L8 <= 0", "zero floor wrong")
check(approx(FL._fl_exemption(0, 0), 0), "exemption is ZERO at a base of exactly zero", "zero-base floor wrong")
check(approx(FL._fl_exemption(400000, 0, short_year_days=183), 25068.49),
      "short year: 50,000 x 183 / 365 = 25,068.49",
      f"short-year proration wrong: {FL._fl_exemption(400000, 0, short_year_days=183)}")
check(approx(FL._fl_exemption(400000, 0, controlled_group_share=12500), 12500),
      "controlled group: this member's apportioned share of the SINGLE group exemption",
      "controlled-group share wrong")
check(approx(FL._fl_exemption(200000, 50000), 50000), "L8 nonbusiness income counts toward the exemption base", "L8 in exemption base wrong")
check(FL._yk(FL.FL_EXEMPTION) == 50000, "exemption constant is $50,000", "exemption constant wrong")

# ---- 4g. Florida net income and the 5.5% rate ----
check(approx(FL._fl_net_income(400000, 0, 50000), 350000), "L10 = L7 + L8 - L9 = 350,000", "L10 wrong")
check(approx(FL._fl_net_income(20000, 0, 50000), 0), "L10 floors at zero ('if a loss, enter zero')", "L10 floor wrong")
check(approx(FL._fl_tax(350000), 19250.0), "5.5%: 350,000 x 0.055 = 19,250", f"rate wrong: {FL._fl_tax(350000)}")
check(approx(FL._fl_tax(530000), 29150.0), "5.5%: 530,000 x 0.055 = 29,150", "rate wrong at 530,000")
check(approx(FL._fl_tax(0), 0.0), "5.5% of zero net income is zero tax", "zero-tax case wrong")
check(FL._yk(FL.FL_TAX_RATE) == "0.055", "rate constant is 5.5% (NOT the historical 4.458% / 3.535%)", "rate constant wrong")

# ---- 4h. Schedule V cap and the single-pass Schedule I add-back map ----
check(approx(FL._fl_credits_allowed(25000, 19250), 19250), "Sch V L25 capped at Line 11 (25,000 -> 19,250)", "credit cap wrong")
check(approx(FL._fl_credits_allowed(5000, 19250), 5000), "Sch V L25 below the cap passes through", "uncapped credit wrong")
check(approx(FL._fl_credits_allowed(25000, 0), 0), "credits cannot create a refund (cap of zero tax = zero credit)", "refund-creation guard wrong")
addbacks = FL._fl_sch_i_credit_addback({4: 5000, 5: 3000, 6: 2000, 1: 1000, 24: 500, 2: 40000})
check(approx(addbacks[7], 5000), "Sch I L7 <- Sch V L4 (enterprise zone)", f"SchI L7 map wrong: {addbacks[7]}")
check(approx(addbacks[8], 1500), "Sch I L8 <- Sch V L1 + FLAHIGA inside Sch V L24 (1,000 + 500)", f"SchI L8 map wrong: {addbacks[8]}")
check(approx(addbacks[9], 5000), "Sch I L9 <- Sch V L5 + Sch V L6 (3,000 + 2,000)", f"SchI L9 map wrong: {addbacks[9]}")
check(40000 not in addbacks.values(),
      "Sch V L2 capital investment generates NO Sch I add-back (one of the eight)", "no-add-back credit leaked into Schedule I")
check(set(addbacks) == set(range(7, 21)), "the add-back map covers exactly Sch I Lines 7-20", f"add-back map keys wrong: {sorted(addbacks)}")
check(all(v not in FL.SCHV_TO_SCHI for v in FL.SCHV_NO_ADDBACK),
      "the eight no-add-back Sch V credits are absent from the Sch V -> Sch I map", "no-add-back list inconsistent with the map")

# ---- 4i. Florida NOL two-tier limitation ----
check(approx(FL._fl_nol_deduction(1000000, 200000, 900000), 840000.0),
      "NOL two-tier: 200,000 (pre-2018 at 100%) + min(900,000, 80% x 800,000 = 640,000) = 840,000",
      f"two-tier NOL wrong: {FL._fl_nol_deduction(1000000, 200000, 900000)}")
check(approx(FL._fl_nol_deduction(1000000, 0, 900000), 800000.0),
      "NOL post-2017 only: 80% x 1,000,000 = 800,000 cap", "post-2017-only tier wrong")
check(approx(FL._fl_nol_deduction(1000000, 1500000, 500000), 1000000.0),
      "NOL pre-2018 carryover offsets 100% and can absorb the whole base", "pre-2018 100% tier wrong")
check(approx(FL._fl_nol_deduction(0, 500000, 500000), 0.0), "no income -> no NOL deduction", "zero-base NOL wrong")
check(FL._yk(FL.FL_NOL_POST2017_PCT) == 0.80, "post-2017 NOL limitation constant is 80%", "NOL percentage constant wrong")

# ---- 4j. F-1065 partner distribution and factor flow-through ----
check(approx(FL._fl_f1065_partner_share(125000, 0.40), 50000.0),
      "F-1065 Part II: (a) 125,000 x (b) 40% = (c) 50,000", "Part II (a)x(b) wrong")
n, d = FL._fl_f1065_factor_flowthrough(600000, 3000000, 200000, 1000000)
check(approx(n, 800000) and approx(d, 4000000) and approx(n / d, 0.20),
      "F-1065N p.2 flow-through: (600k+200k)/(3m+1m) = 0.20 - numerator AND denominator addition",
      f"factor flow-through wrong: {n}/{d}")

# ---- 4k. Conformity / Sec.179 constants (the 'rule says no' guards) ----
check(FL._yk(FL.FL_OBBBA_ADOPTED) is False, "OBBBA is NOT adopted for TY2025", "OBBBA adoption flag wrong")
check(FL._yk(FL.FL_CONFORMITY_DATE) == "2025-01-01", "conformity date is January 1, 2025", "conformity date wrong")
check(FL._yk(FL.FL_179_ADDBACK_EXISTS) is False, "NO Florida Sec.179 add-back for TY2025 ('the rule says no')", "Sec.179 add-back flag wrong")
_179 = FL._yk(FL.FL_179_PRE_OBBBA)
check(_179 == {"limit": 1250000, "phaseout": 3130000, "suv_sublimit": 31300},
      "Sec.179 pre-OBBBA figures: $1,250,000 / $3,130,000 / $31,300 (NOT 2.5M/4M)", f"Sec.179 figures wrong: {_179}")
check(_179["limit"] != 2500000 and _179["phaseout"] != 4000000,
      "the OBBBA $2,500,000 / $4,000,000 figures are NOT used for Florida TY2025", "OBBBA Sec.179 figures leaked in")
check(FL._yk(FL.FL_ESTIMATED_THRESHOLD) == 2500 and FL._yk(FL.FL_ESTIMATED_INSTALLMENTS) == 4,
      "estimated tax: $2,500 threshold, four equal installments", "estimated-tax constants wrong")
check(FL._yk(FL.FL_F1065_DUE_MONTH) == 4 and FL._yk(FL.FL_F1120_DUE_MONTH_OTHER) == 5,
      "F-1065 due the 4th month; F-1120 the 5th (non-June-30 year ends)", "due-month constants wrong")
check(FL._yk(FL.FL_RENT_MULTIPLIER) == 8, "rented property enters the property factor at 8 x net annual rent", "rent multiplier wrong")

# ══════════════════════════════════════════════════════════════════════
# 5. Required diagnostics — every RED-defer R1..R12 and the walk-item blocks.
# ══════════════════════════════════════════════════════════════════════
REQUIRED_DIAG = {
    "FL_F1120": [
        "D_FL1120_GATE_NO_RETURN", "D_FL1120_GATE_SCORP_23C", "D_FL1120_W3_LIFO_RECAPTURE",
        "D_FL1120_GATE_FOREIGN_PTR", "D_FL1120_GATE_CHAR_TRUST", "D_FL1120_GATE_1120H",
        "D_FL1120_W1_NO_SILENT_RECALC", "D_FL1120_R1_FISCAL_STRADDLE", "D_FL1120_R2_OBBBA_RECOMPUTE",
        "D_FL1120_R3_APPORT_GATE", "D_FL1120_R4_AMT_CREDIT", "D_FL1120_R5_CONSOLIDATED",
        "D_FL1120_R6_163J_CARRYFWD", "D_FL1120_R7_ELECTION_AB", "D_FL1120_R8_FINANCIAL_ORG",
        "D_FL1120_R9_SPECIAL_APPORT", "D_FL1120_R11_F1120A", "D_FL1120_R12_AMENDED_F2220",
        "D_FL1120_QIP_TAG_REQUIRED", "D_FL1120_BONUS_7YR_SCHED", "D_FL1120_179_NO_ADDBACK",
        "D_FL1120_INSIGNIFICANT_DEN", "D_FL1120_SCHV_CAP_BINDS", "D_FL1120_CARRYOVER_FORK",
    ],
    "FL_F1065": [
        "D_FL1065_GATE_NO_RETURN", "D_FL1065_GATE_ALL_INDIVIDUAL", "D_FL1065_GATE_SCORP_ONLY",
        "D_FL1065_CORP_PARTNER_DUAL", "D_FL1065_R10_TIERED_PARTNERSHIP", "D_FL1065_W6_ATTACH_CONFLICT",
        "D_FL1065_DUE_4TH_MONTH", "D_FL1065_NO_PTET_NO_WH",
    ],
}
for fn, dids in REQUIRED_DIAG.items():
    form = TaxForm.objects.get(form_number=fn)
    missing = [d for d in dids if not FormDiagnostic.objects.filter(tax_form=form, diagnostic_id=d).exists()]
    check(not missing, f"{fn}: all {len(dids)} required diagnostics present", f"{fn}: MISSING diagnostics {missing}")

# All twelve RED-defers R1..R12 have a diagnostic somewhere in the batch.
present = set(all_diag)
red_map = {
    "R1": "D_FL1120_R1_FISCAL_STRADDLE", "R2": "D_FL1120_R2_OBBBA_RECOMPUTE",
    "R3": "D_FL1120_R3_APPORT_GATE", "R4": "D_FL1120_R4_AMT_CREDIT",
    "R5": "D_FL1120_R5_CONSOLIDATED", "R6": "D_FL1120_R6_163J_CARRYFWD",
    "R7": "D_FL1120_R7_ELECTION_AB", "R8": "D_FL1120_R8_FINANCIAL_ORG",
    "R9": "D_FL1120_R9_SPECIAL_APPORT", "R10": "D_FL1065_R10_TIERED_PARTNERSHIP",
    "R11": "D_FL1120_R11_F1120A", "R12": "D_FL1120_R12_AMENDED_F2220",
}
missing_red = [f"{k}({v})" for k, v in red_map.items() if v not in present]
check(not missing_red, "all 12 RED-defers R1-R12 have their own diagnostic", f"RED-defers with no diagnostic: {missing_red}")

# The two hard blocks must be severity 'error'.
for fn, did in (("FL_F1120", "D_FL1120_R1_FISCAL_STRADDLE"), ("FL_F1120", "D_FL1120_R2_OBBBA_RECOMPUTE"),
                ("FL_F1120", "D_FL1120_W1_NO_SILENT_RECALC"), ("FL_F1120", "D_FL1120_R3_APPORT_GATE"),
                ("FL_F1065", "D_FL1065_R10_TIERED_PARTNERSHIP")):
    d = FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).first()
    check(d is not None and d.severity == "error", f"{did} is severity 'error' (a hard block)",
          f"{did} severity is {getattr(d, 'severity', 'MISSING')!r}, expected 'error'")

# ══════════════════════════════════════════════════════════════════════
# 6. Structural spot checks on the encoded line map.
# ══════════════════════════════════════════════════════════════════════
f1120 = TaxForm.objects.get(form_number="FL_F1120")
check(FormLine.objects.filter(tax_form=f1120, line_number__startswith="SchI-").count() == 26,
      "Schedule I has all 26 addition lines", "Schedule I line count wrong")
check(FormLine.objects.filter(tax_form=f1120, line_number__startswith="SchII-").count() == 13,
      "Schedule II has all 13 subtraction lines", "Schedule II line count wrong")
check(FormLine.objects.filter(tax_form=f1120, line_number__startswith="SchV-").count() == 25,
      "Schedule V has all 25 credit lines in statutory order", "Schedule V line count wrong")
check(FormLine.objects.filter(tax_form=f1120, line_number__startswith="SchIV-").count() == 9,
      "Schedule IV has all 9 lines", "Schedule IV line count wrong")
for want in ("SchI-21", "SchI-22", "SchII-9", "SchII-10"):
    check(FormLine.objects.filter(tax_form=f1120, line_number=want).exists(),
          f"the two depreciation tracks are separate lines: {want} present", f"{want} MISSING")
l11 = FormLine.objects.filter(tax_form=f1120, line_number="11").first()
check(l11 is not None and "5.5%" in l11.description, "Line 11 carries the verbatim '5.5% of Line 10'", "Line 11 rate text missing")
check(FormFact.objects.filter(tax_form=f1120, fact_key="schi_l21_bonus_qip_portion").exists(),
      "the QIP/non-QIP tag on Sch I L21 exists as its own fact", "QIP tag fact MISSING")
check(FormFact.objects.filter(tax_form=f1120, fact_key="fti_pre_obbba_confirmed", required=True).exists(),
      "the W1 pre-OBBBA confirmation on Line 1 is a REQUIRED fact", "W1 confirmation fact missing or not required")
f1065 = TaxForm.objects.get(form_number="FL_F1065")
check(not FormLine.objects.filter(tax_form=f1065, description__icontains="tax due").exists(),
      "F-1065 carries NO tax-due line (information return only)", "F-1065 has a tax line")
check(FL.FL_CH220_PARTNER_KINDS == ("c_corp", "foreign_corp", "s_corp"),
      "ch.220 partner kinds include S corps (subject, but carved out by (6)(b) when alone)",
      f"partner kinds wrong: {FL.FL_CH220_PARTNER_KINDS}")

# ══════════════════════════════════════════════════════════════════════
# 7. Report
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
for fn in FORM_SHAPE:
    form = TaxForm.objects.get(form_number=fn)
    print(f"  {fn}: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {form.test_scenarios.count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-FL').count()}")
print(f"  authority sources (FL): {AuthoritySource.objects.filter(jurisdiction_code='FL').count()}")
print(f"  rule authority links: {RuleAuthorityLink.objects.count()}")
print("=" * 72)
for p in PASSES:
    print(f"  PASS  {p}")
for f in FAILURES:
    print(f"  FAIL  {f}")
print("=" * 72)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print("REMINDER: READY_TO_SEED was flipped IN MEMORY ONLY. The file on disk must ship False.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
