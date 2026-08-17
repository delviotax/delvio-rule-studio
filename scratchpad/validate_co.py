"""Throwaway-SQLite validation for the CO DR 0106 spec (WO: Colorado PTE wave).

Checks, in order:
  1. CharField caps -- introspected from the REAL model fields (never hardcoded),
     then every seeded value measured against them. SQLite does NOT enforce
     max_length; Postgres does. This is the only place the truncation risk is caught.
  2. The SEED GUARD -- forced DOWN in memory and asserted to REFUSE. Pins the
     MECHANISM, not whatever value happens to be on disk.
  3. Structural integrity -- every rule has >= 1 authority link; no duplicate ids;
     rule_links reference defined rules; entity_types / jurisdiction / form code.
  4. Arithmetic oracles -- THE SIGN FLIP (incl. proof that an un-inverted
     aggregation gives a DIFFERENT, WRONG answer), both Sec. 179 touchpoints, each
     major fork producing DIFFERENT results for 1065 vs 1120S, the three-mode state
     machine, and the two rate constants.

ASCII-only. Run: poetry run python scratchpad/validate_co.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_co.sqlite3")
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
from specs.management.commands import load_co_dr0106 as CO  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

FORM_CODE = CO.FORM_CODE
M65, MS = CO.M_1065, CO.M_1120S

# ══════════════════════════════════════════════════════════════════════════
# 1. THE SEED GUARD -- force it DOWN and assert it REFUSES.
#    Pins the MECHANISM, not the disk value: whatever ships in the file, the
#    guard must refuse when READY_TO_SEED is False.
# ══════════════════════════════════════════════════════════════════════════
_shipped = CO.READY_TO_SEED
check(_shipped is False,
      "READY_TO_SEED SHIPS FALSE on disk (the spec is gated, as required)",
      f"READY_TO_SEED SHIPPED {_shipped!r} -- it MUST ship False (blocked on [UNV-7]/W13)")

CO.READY_TO_SEED = False
try:
    call_command("load_co_dr0106", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the loader seeded with READY_TO_SEED = False")
except CommandError as e:
    msg = str(e)
    check("REFUSING TO SEED" in msg, "guard REFUSES to seed when READY_TO_SEED is False",
          f"guard raised CommandError but without the refusal banner: {msg[:120]}")
    check("174A" in msg or "UNV-7" in msg,
          "guard message names the [UNV-7] / Sec. 174A BLOCKER",
          "guard message does not mention the blocking item")
    check("READY_TO_SEED = False" in msg, "guard reports the sentinel value it saw",
          "guard message omits the sentinel value")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"guard raised the WRONG exception type: {e!r}")

check(TaxForm.objects.filter(form_number=FORM_CODE).count() == 0,
      "guard left the DB CLEAN -- nothing was written while gated",
      "guard refused but rows were still written")

# Now flip IN MEMORY only (the file on disk stays False) and seed.
CO.READY_TO_SEED = True
try:
    call_command("load_co_dr0106", verbosity=0)
    PASSES.append("loader ran + seeded into throwaway SQLite without error")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_co_dr0106 raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)
finally:
    CO.READY_TO_SEED = _shipped   # never leave the module mutated

form = TaxForm.objects.get(form_number=FORM_CODE)

# ══════════════════════════════════════════════════════════════════════════
# 2. CharField caps -- introspected from the REAL model fields.
# ══════════════════════════════════════════════════════════════════════════
CAP = {
    "TaxForm.form_number":       TaxForm._meta.get_field("form_number").max_length,
    "TaxForm.jurisdiction":      TaxForm._meta.get_field("jurisdiction").max_length,
    "TaxForm.form_title":        TaxForm._meta.get_field("form_title").max_length,
    "FormRule.rule_id":          FormRule._meta.get_field("rule_id").max_length,
    "FormRule.title":            FormRule._meta.get_field("title").max_length,
    "FormLine.line_number":      FormLine._meta.get_field("line_number").max_length,
    "FormFact.fact_key":         FormFact._meta.get_field("fact_key").max_length,
    "FormFact.label":            FormFact._meta.get_field("label").max_length,
    "FormDiagnostic.diagnostic_id": FormDiagnostic._meta.get_field("diagnostic_id").max_length,
    "FormDiagnostic.title":      FormDiagnostic._meta.get_field("title").max_length,
    "FlowAssertion.assertion_id": FlowAssertion._meta.get_field("assertion_id").max_length,
    "FlowAssertion.title":       FlowAssertion._meta.get_field("title").max_length,
    "TestScenario.scenario_name": TestScenario._meta.get_field("scenario_name").max_length,
    "AuthoritySource.source_code": AuthoritySource._meta.get_field("source_code").max_length,
    "AuthoritySource.citation":  AuthoritySource._meta.get_field("citation").max_length,
    "AuthoritySource.issuer":    AuthoritySource._meta.get_field("issuer").max_length,
    "AuthoritySource.title":     AuthoritySource._meta.get_field("title").max_length,
    "AuthorityTopic.topic_code": AuthorityTopic._meta.get_field("topic_code").max_length,
    "AuthorityTopic.topic_name": AuthorityTopic._meta.get_field("topic_name").max_length,
}

# The caps the campaign brief states -- assert the MODEL still agrees with them,
# so a silent migration widening/narrowing a column is caught here too.
EXPECTED = {
    "FormRule.rule_id": 20, "FormLine.line_number": 20, "FlowAssertion.assertion_id": 20,
    "FormDiagnostic.diagnostic_id": 40, "FormFact.fact_key": 100,
    "AuthorityTopic.topic_name": 255, "AuthoritySource.citation": 255,
    "AuthoritySource.issuer": 100, "AuthoritySource.source_code": 100,
}
for k, want in EXPECTED.items():
    check(CAP[k] == want, f"model cap {k} == {want} (as the campaign brief states)",
          f"model cap {k} is {CAP[k]}, brief says {want} -- reconcile before seeding")

viol = []


def measure(label, value, cap_key):
    cap = CAP[cap_key]
    if value is None or cap is None:   # cap is None => TextField, unbounded
        return
    if len(str(value)) > cap:
        viol.append(f"{label}: len {len(str(value))} > {cap} ({cap_key}) :: {str(value)[:60]}")


measure(f"form_number={form.form_number}", form.form_number, "TaxForm.form_number")
measure("jurisdiction", form.jurisdiction, "TaxForm.jurisdiction")
measure("form_title", form.form_title, "TaxForm.form_title")
for r in FormRule.objects.filter(tax_form=form):
    measure(f"rule_id={r.rule_id}", r.rule_id, "FormRule.rule_id")
    measure(f"rule.title[{r.rule_id}]", r.title, "FormRule.title")
for ln in FormLine.objects.filter(tax_form=form):
    measure(f"line_number={ln.line_number}", ln.line_number, "FormLine.line_number")
for fct in FormFact.objects.filter(tax_form=form):
    measure(f"fact_key={fct.fact_key}", fct.fact_key, "FormFact.fact_key")
    measure(f"fact.label[{fct.fact_key}]", fct.label, "FormFact.label")
for d in FormDiagnostic.objects.filter(tax_form=form):
    measure(f"diagnostic_id={d.diagnostic_id}", d.diagnostic_id, "FormDiagnostic.diagnostic_id")
    measure(f"diag.title[{d.diagnostic_id}]", d.title, "FormDiagnostic.title")
for t in TestScenario.objects.filter(tax_form=form):
    measure(f"scenario_name={t.scenario_name[:30]}", t.scenario_name, "TestScenario.scenario_name")
for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-CO"):
    measure(f"assertion_id={fa.assertion_id}", fa.assertion_id, "FlowAssertion.assertion_id")
    measure(f"fa.title[{fa.assertion_id}]", fa.title, "FlowAssertion.title")
for s in AuthoritySource.objects.filter(jurisdiction_code="CO"):
    measure(f"source_code={s.source_code}", s.source_code, "AuthoritySource.source_code")
    measure(f"citation[{s.source_code}]", s.citation, "AuthoritySource.citation")
    measure(f"issuer[{s.source_code}]", s.issuer, "AuthoritySource.issuer")
    measure(f"src.title[{s.source_code}]", s.title, "AuthoritySource.title")
for tp in AuthorityTopic.objects.filter(topic_code__startswith="co_"):
    measure(f"topic_code={tp.topic_code}", tp.topic_code, "AuthorityTopic.topic_code")
    measure(f"topic_name={tp.topic_code}", tp.topic_name, "AuthorityTopic.topic_name")

check(not viol, "CharField caps OK -- every seeded value fits its REAL model field",
      "CAP VIOLATIONS (Postgres would truncate/reject):\n    " + "\n    ".join(viol))

# ══════════════════════════════════════════════════════════════════════════
# 3. Structural integrity
# ══════════════════════════════════════════════════════════════════════════
rules_qs = FormRule.objects.filter(tax_form=form)
ruleless = [r.rule_id for r in rules_qs if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless, f"all {rules_qs.count()} rules carry >= 1 authority link",
      f"rules with NO authority link: {ruleless}")

spec = CO.FORMS[0]
defined = {r["rule_id"] for r in spec["rules"]}
linked = {rl[0] for rl in spec["rule_links"]}
check(not (linked - defined), "rule_links reference only defined rules", f"orphan rule_links: {linked - defined}")
check(not (defined - linked), "every rule appears in rule_links", f"unlinked rules: {defined - linked}")

for label, seq, key in (
    ("rule_id", spec["rules"], "rule_id"),
    ("line_number", spec["lines"], "line_number"),
    ("fact_key", spec["facts"], "fact_key"),
    ("diagnostic_id", spec["diagnostics"], "diagnostic_id"),
    ("scenario_name", spec["scenarios"], "scenario_name"),
    ("assertion_id", CO.FLOW_ASSERTIONS, "assertion_id"),
):
    ids = [x[key] for x in seq]
    dupes = {i for i in ids if ids.count(i) > 1}
    check(not dupes, f"no duplicate {label} ({len(ids)} unique)", f"DUPLICATE {label}: {dupes}")

check(form.entity_types == ["1065", "1120S"],
      "entity_types == ['1065', '1120S'] -- ONE form, TWO modules",
      f"entity_types wrong: {form.entity_types}")
check(form.jurisdiction == "CO" and form.tax_year == 2025 and form.version == 1 and form.status == "draft",
      "jurisdiction CO / TY2025 / v1 / draft", f"identity wrong: {form.jurisdiction} {form.tax_year} v{form.version} {form.status}")
check(form.form_number == "CO_DR0106", "form code is CO_DR0106 (campaign D-9 <ST>_<FORM> namespace)",
      f"form code wrong: {form.form_number}")

# the CO conformity anchor must be referenced and must RESOLVE
check("CO_CRS_39_22_103" in CO.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE includes the CO conformity anchor CO_CRS_39_22_103",
      "CO conformity anchor missing from EXISTING_SOURCES_TO_REFERENCE")
check("CO_2025_INDIV_TAX_GUIDE" in CO.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE includes CO_2025_INDIV_TAX_GUIDE",
      "CO_2025_INDIV_TAX_GUIDE missing from EXISTING_SOURCES_TO_REFERENCE")

# every RED-defer R1..R16 has its own diagnostic
RED_DEFERS = ["D_CO106_R1_DR0619", "D_CO106_R2_DR1305", "D_CO106_R3_ENTZONE", "D_CO106_R4_CHFA",
              "D_CO106_R5_REMEDIATION", "D_CO106_R6_CHILDCARE", "D_CO106_R7_INLIEU", "D_CO106_R8_ALTAPPORT",
              "D_CO106_R9_MUTUALFUND", "D_CO106_R10_DR1079", "D_CO106_R11_DR0108",
              "D_CO106_R12_RETRO_ELECTION", "D_CO106_R13_SHORTPERIOD", "D_CO106_R14_PTP",
              "D_CO106_R15_K1_TRANSMITTAL", "D_CO106_R16_REPORTABLE"]
missing = [d for d in RED_DEFERS if not FormDiagnostic.objects.filter(tax_form=form, diagnostic_id=d).exists()]
check(not missing, f"all 16 RED-defers (R1-R16) have their own diagnostic -- no silent gap",
      f"RED-defers with no diagnostic: {missing}")

blocker = FormDiagnostic.objects.filter(tax_form=form, diagnostic_id="D_CO106_BLOCK_174A_CONFORMITY").first()
check(blocker is not None and blocker.severity == "error",
      "the [UNV-7] Sec. 174A blocker is encoded as a BLOCKING (error) diagnostic",
      "blocking diagnostic D_CO106_BLOCK_174A_CONFORMITY missing or not severity=error")
check(any(r["rule_id"] == "R-CO-174A-BLOCK" for r in spec["rules"]),
      "the blocker also has a rule (R-CO-174A-BLOCK) -- not computed around",
      "R-CO-174A-BLOCK rule missing")

# ══════════════════════════════════════════════════════════════════════════
# 4a. ARITHMETIC ORACLE -- THE SIGN FLIP
# ══════════════════════════════════════════════════════════════════════════
SCHK_65 = {"1": 500000, "2": 20000, "4c": 60000, "5": 10000}
K1A = {"l9": 12000, "l10": 3000, "l11": 5000, "l12": -50000, "l13": -20000}

right = CO.co_part1(M65, SCHK_65, K1A)
wrong = CO.co_part1(M65, SCHK_65, K1A, apply_sign_flip=False)

check(approx(right["L2"], 90000), "L2 (1065) = 20000 + 60000 + 10000 = 90,000", f"L2 wrong: {right['L2']}")
check(approx(right["L3"], 3000), "L3 = K-1 Col.A L10 = 3,000 and is NOT inverted", f"L3 wrong: {right['L3']}")
check(approx(right["L4"], 17000), "L4 = K-1 Col.A L9 + L11 = 17,000 and is NOT inverted", f"L4 wrong: {right['L4']}")
check(approx(right["L5"], 610000), "L5 = L1+L2+L3+L4 = 610,000", f"L5 wrong: {right['L5']}")
check(approx(right["L6"], 50000), "SIGN FLIP: L6 = -(-50,000) = +50,000", f"L6 wrong: {right['L6']}")
check(approx(right["L8"], 20000), "SIGN FLIP: L8 = -(-20,000) = +20,000", f"L8 wrong: {right['L8']}")
check(approx(right["L9"], 70000), "L9 = L6+L7+L8 = 70,000", f"L9 wrong: {right['L9']}")
check(approx(right["L10"], 540000), "L10 = L5 - L9 = 540,000 (CORRECT)", f"L10 wrong: {right['L10']}")

# THE PROOF: the un-inverted aggregation gives a DIFFERENT, WRONG answer.
check(not approx(wrong["L10"], right["L10"]),
      "SIGN-FLIP ORACLE: the un-inverted aggregation gives a DIFFERENT line 10",
      "un-inverted aggregation gave the SAME line 10 -- the oracle proves nothing")
check(approx(wrong["L10"], 680000), "un-inverted (BUGGY) L10 = 680,000", f"buggy L10 unexpected: {wrong['L10']}")
check(approx(wrong["L10"] - right["L10"], 140000),
      "the sign-flip error is exactly 2x the deduction total (140,000), in the wrong direction",
      f"error magnitude unexpected: {wrong['L10'] - right['L10']}")
check(approx(wrong["L6"], -50000) and approx(wrong["L8"], -20000),
      "the buggy path leaves L6/L8 negative -- the visible symptom of the bug",
      "buggy path did not reproduce the negative L6/L8")
# ...and lines 3/4 must be IDENTICAL either way (they are never inverted)
check(approx(wrong["L3"], right["L3"]) and approx(wrong["L4"], right["L4"]),
      "lines 3 and 4 are unaffected by the flip flag -- they are never inverted",
      "lines 3/4 changed with the flip flag -- over-application of the sign flip")

# ══════════════════════════════════════════════════════════════════════════
# 4b. ARITHMETIC ORACLE -- BOTH Sec. 179 touchpoints
# ══════════════════════════════════════════════════════════════════════════
t1 = CO.co_line2(MS, {"2": 15000, "4": 5000}, sec179_disposition_gain=40000)
check(approx(t1, 60000), "Sec.179 TOUCHPOINT (i): disposition gain lifts L2 to 60,000 (1120S)", f"L2 wrong: {t1}")
check(approx(CO.co_line2(MS, {"2": 15000, "4": 5000}), 20000),
      "omitting the disposition gain UNDERSTATES L2 by 40,000 -- the failure mode",
      "disposition-gain oracle did not show the understatement")

t2 = CO.co_part1(MS, {"1": 300000}, {"l12": -125000})
check(approx(t2["L2"], 0),
      "Sec.179 TOUCHPOINT (ii): L2 EXCLUDES the Sec.179 deduction (Sch.K 11/12 not in the L2 set)",
      f"L2 should be 0, got {t2['L2']}")
check(approx(t2["L6"], 125000),
      "Sec.179 TOUCHPOINT (ii): the DEDUCTION arrives at L6 via K-1 L12, sign-inverted",
      f"L6 wrong: {t2['L6']}")
check(approx(t2["L10"], 175000), "Sec.179 touchpoint (ii): L10 = 300,000 - 125,000 = 175,000", f"L10 wrong: {t2['L10']}")
check(CO.CO_179_DEDUCTION_K1_BOX[M65] != CO.CO_179_DEDUCTION_K1_BOX[MS],
      "the Sec.179 deduction box FORKS (1065 K-1 Box 12 vs 1120-S K-1 Box 11)",
      "Sec.179 deduction box did not fork")
check(CO.CO_179_DISPOSITION_SCHK_LINE[M65] != CO.CO_179_DISPOSITION_SCHK_LINE[MS],
      "F5: the Sec.179-disposition statement line FORKS (Sch.K 20c vs 17d)",
      "F5 did not fork")

# ══════════════════════════════════════════════════════════════════════════
# 4c. ARITHMETIC ORACLE -- the FORKS must give DIFFERENT results per module
# ══════════════════════════════════════════════════════════════════════════
check(len(CO.CO_FORKS) == 16 and CO.CO_FORKS_TOTAL == 16,
      "16 forks encoded (F1-F16) -- the verifier's raised count, not the original 12",
      f"fork count wrong: {len(CO.CO_FORKS)}")
differing = [f["fork_id"] for f in CO.CO_FORKS if f[M65] != f[MS]]
check(len(differing) == 16, "every one of the 16 forks carries a DIFFERENT value per module",
      f"forks that do NOT differ: {set(f['fork_id'] for f in CO.CO_FORKS) - set(differing)}")
for fid in ("F13", "F14", "F15", "F16"):
    check(CO.co_fork(fid, M65) != CO.co_fork(fid, MS),
          f"{fid} (added by the adversarial verifier) forks per module",
          f"{fid} does not fork")

# F4 -- the SAME federal Schedule K gives DIFFERENT line 2 per module
SHARED_K = {"1": 100000, "2": 1000, "3c": 2000, "4": 4000, "4c": 8000,
            "5": 16000, "5a": 32000, "6": 64000, "6a": 128000}
l2_65, l2_s = CO.co_line2(M65, SHARED_K), CO.co_line2(MS, SHARED_K)
check(approx(l2_65, 155000), "F4: 1065 L2 = 1000+2000+8000+16000+128000 = 155,000", f"1065 L2 wrong: {l2_65}")
check(approx(l2_s, 103000), "F4: 1120S L2 = 1000+2000+4000+32000+64000 = 103,000", f"1120S L2 wrong: {l2_s}")
check(not approx(l2_65, l2_s), "F4 ORACLE: identical federal input -> DIFFERENT entity income per module",
      "F4 produced the same L2 for both modules -- the fork is not wired")

# F7 -- the state-tax add-back SPLIT AXIS itself forks
nr_indiv = {"residency": "nonresident", "owner_kind": "individual"}
res_indiv = {"residency": "resident", "owner_kind": "individual"}
ccorp = {"residency": "nonresident", "owner_kind": "c_corp"}
check(CO.co_k1_line9_scope(M65, nr_indiv) == "all_states",
      "F7: a nonresident INDIVIDUAL PARTNER gets ALL state taxes (split by partner type)",
      "F7 partnership scope wrong")
check(CO.co_k1_line9_scope(MS, nr_indiv) == "colorado_only",
      "F7: the SAME owner as a nonresident SHAREHOLDER gets COLORADO ONLY (split by residency)",
      "F7 S-corp scope wrong")
check(CO.co_k1_line9_scope(M65, nr_indiv) != CO.co_k1_line9_scope(MS, nr_indiv),
      "F7 ORACLE: identical owner -> DIFFERENT add-back scope, because the SPLIT AXIS forks",
      "F7 gave the same scope for both modules")
check(CO.co_k1_line9_scope(M65, ccorp) == "colorado_only",
      "F7: a C-corporation PARTNER gets Colorado-only", "F7 C-corp partner scope wrong")
check(CO.co_k1_line9_scope(MS, res_indiv) == "all_states",
      "F7: a RESIDENT shareholder gets all state taxes", "F7 resident shareholder scope wrong")

# F15 / F16 -- the modification INVENTORIES differ (verifier C7 / C8, both HIGH)
check(len(CO.CO_K1_L11_ITEMS[MS]) == len(CO.CO_K1_L11_ITEMS[M65]) + 1,
      "F15: the S-corp line-11 inventory has ONE MORE item (the foreign-tax add-back)",
      f"F15 counts wrong: 1065={len(CO.CO_K1_L11_ITEMS[M65])} 1120S={len(CO.CO_K1_L11_ITEMS[MS])}")
check(any("foreign" in i.lower() for i in CO.CO_K1_L11_ITEMS[MS])
      and not any("foreign" in i.lower() for i in CO.CO_K1_L11_ITEMS[M65]),
      "F15 ORACLE: the foreign-tax ADDITION exists ONLY on the S-corp side (C7)",
      "F15 foreign-tax add-back is not S-corp-only")
check(any("39-22-206" in i for i in CO.CO_K1_L13_ITEMS[M65])
      and not any("39-22-206" in i for i in CO.CO_K1_L13_ITEMS[MS]),
      "F16 ORACLE: the export-taxpayer SUBTRACTION exists ONLY on the partnership side (C8)",
      "F16 export-taxpayer subtraction is not partnership-only")
check(any("280C" in i for i in CO.CO_K1_L13_ITEMS[MS])
      and not any("280C" in i for i in CO.CO_K1_L13_ITEMS[M65]),
      "F16 ORACLE: the Sec.280C wages SUBTRACTION exists ONLY on the S-corp side (C8)",
      "F16 Sec.280C subtraction is not S-corp-only")
check(CO.CO_K1_L13_REFUND_SPLIT_AXIS[M65] != CO.CO_K1_L13_REFUND_SPLIT_AXIS[MS],
      "F16: the state-tax-refund split AXIS also forks", "F16 refund split axis did not fork")

# F14 -- K-1 lines 14/15 are NEVER mandatory for an S-corp shareholder (C6)
check(CO.co_k1_lines_14_15_required(M65, ccorp) is True,
      "F14: K-1 lines 14/15 ARE required for a C-corporation partner", "F14 partnership rule wrong")
check(CO.co_k1_lines_14_15_required(MS, ccorp) is False,
      "F14 ORACLE: K-1 lines 14/15 are NEVER required for any S-corp shareholder (C6)",
      "F14 S-corp rule wrong")

# F2 -- Column B population forks for entity owners
check(CO.co_k1_column_b_populated(M65, ccorp, salt_parity_election=False) is False,
      "F2: a partnership leaves Column B BLANK for a corporate partner absent an election",
      "F2 partnership Column B rule wrong")
check(CO.co_k1_column_b_populated(M65, ccorp, salt_parity_election=True) is True,
      "F2: a SALT Parity election turns Column B ON for that same corporate partner",
      "F2 election override wrong")
check(CO.co_k1_column_b_populated(MS, nr_indiv) is True,
      "F2: an S corp completes Column B for EVERY nonresident shareholder", "F2 S-corp rule wrong")
check(CO.co_k1_column_b_populated(M65, res_indiv) is False,
      "F2: no Column B for a resident owner in either module", "F2 resident rule wrong")

# F1 -- sourcing default forks
check(CO.co_sourcing_default(M65) == "direct_sourcing" and CO.co_sourcing_default(MS) == "receipts_factor",
      "F1 ORACLE: partnership defaults to DIRECT SOURCING; S corp is MANDATORY receipts factor",
      "F1 sourcing default did not fork")
check(CO.co_part_v_required(MS, [res_indiv]) is True,
      "Part V is always required for an S corp", "Part V S-corp requirement wrong")
check(CO.co_part_v_required(M65, [ccorp]) is True,
      "Part V is required for a direct-sourcing partnership that has a C-corp partner",
      "Part V partnership/C-corp requirement wrong")
check(CO.co_part_v_required(M65, [nr_indiv]) is False,
      "Part V is not forced for a partnership with only individual partners using direct sourcing",
      "Part V partnership default wrong")

# F11 -- composite carve-outs (verifier C1, HIGH)
check("all_owners_excluded" in CO.CO_COMPOSITE_CARVEOUTS[MS],
      "C1: the all-owners-excluded carve-out EXISTS for S CORPS (Sec. 39-22-601(2.7)(d)(VII)(B))",
      "C1 REGRESSION: the S-corp all-owners-excluded carve-out is missing")
check("publicly_traded_partnership" in CO.CO_COMPOSITE_CARVEOUTS[M65]
      and "publicly_traded_partnership" not in CO.CO_COMPOSITE_CARVEOUTS[MS],
      "F11: only the PTP carve-out is partnership-only", "F11 PTP carve-out placement wrong")

# ══════════════════════════════════════════════════════════════════════════
# 4d. ARITHMETIC ORACLE -- the THREE-MODE state machine
# ══════════════════════════════════════════════════════════════════════════
check(CO.co_mode(False, False) == CO.CO_MODE_A, "MODE A when neither part is used (informational-only)", "mode A wrong")
check(CO.co_mode(False, True) == CO.CO_MODE_B, "MODE B when a composite return is filed", "mode B wrong")
check(CO.co_mode(True, False) == CO.CO_MODE_C, "MODE C when a SALT Parity election is made", "mode C wrong")
try:
    CO.co_mode(True, True)
    FAILURES.append("MODE CONFLICT NOT RAISED: Parts II and III both completed was allowed")
except CO.CoModeConflict:
    PASSES.append("MODE ORACLE: Parts II and III both completed RAISES (hard RED, no silent precedence)")

OWNERS_B = [
    {"residency": "nonresident", "owner_kind": "individual", "col_b": 200000},
    {"residency": "nonresident", "owner_kind": "individual", "col_b": 100000},
    {"residency": "resident", "owner_kind": "individual", "col_a": 500000, "col_b": 0},
    {"residency": "nonresident", "owner_kind": "individual", "dr0107": True, "col_b": 90000},
    {"residency": "nonresident", "owner_kind": "c_corp", "col_b": 400000},
    {"residency": "nonresident", "owner_kind": "individual", "col_b": -60000},
]
base_b = CO.co_composite_base(M65, OWNERS_B)
check(approx(base_b, 300000),
      "MODE B: L12 = 300,000 -- resident, DR 0107 filer, C-corp partner and NEGATIVE owner all excluded",
      f"composite base wrong: {base_b}")
check(approx(CO.co_composite_tax(M65, OWNERS_B), 13200), "MODE B: L13 = 300,000 x 4.4% = 13,200",
      f"composite tax wrong: {CO.co_composite_tax(M65, OWNERS_B)}")
check(CO.co_composite_excluded(M65, OWNERS_B[5]).startswith("negative"),
      "the FIFTH (statutory) exclusion fires on negative Colorado-source income",
      "negative-income exclusion did not fire")
check(CO.co_composite_excluded(M65, OWNERS_B[4]) != "" and CO.co_composite_excluded(MS, {"residency": "nonresident", "owner_kind": "individual", "col_b": 10}) == "",
      "F10: a corporate partner is excluded on the partnership side; an S-corp nonresident individual is included",
      "F10 entity-owner exclusion wrong")

# W4 -- the reconciliation holds ONLY because floor and exclusion are one rule
rate_c = CO.co_rate("composite")
sum_l16 = sum(CO.co_k1_line16(o.get("col_b", 0), rate_c)
              for o in OWNERS_B if not CO.co_composite_excluded(M65, o))
check(approx(sum_l16, CO.co_composite_tax(M65, OWNERS_B)),
      "W4 RECONCILIATION: SUM(K-1 L16) == DR 0106 L13 (13,200)",
      f"reconciliation FAILED: sum K1 L16 = {sum_l16} vs L13 = {CO.co_composite_tax(M65, OWNERS_B)}")
check(approx(CO.co_k1_line16(-80000, rate_c), 0.0),
      "K-1 line 16 FLOORS AT ZERO for a negative owner (never a negative credit)",
      "K-1 line 16 floor failed")
check(approx(CO.co_k1_line16(250000, rate_c), 11000), "K-1 line 16 = 250,000 x 4.4% = 11,000",
      f"K-1 L16 wrong: {CO.co_k1_line16(250000, rate_c)}")
check(approx(CO.co_composite_net_tax(13200, 10000, 8000), 0.0),
      "L16 cap: L14 + L15 may not exceed L13 -- net tax floors at 0",
      "L16 cap failed")

OWNERS_C = [
    {"residency": "resident", "owner_kind": "individual", "col_a": 400000, "col_b": 150000},
    {"residency": "part_year", "owner_kind": "individual", "col_a": 100000, "col_b": 40000},
    {"residency": "nonresident", "owner_kind": "individual", "col_a": 300000, "col_b": 120000},
    {"residency": "nonresident", "owner_kind": "individual", "col_a": 50000, "col_b": -25000},
]
p3 = CO.co_ptet_bases(OWNERS_C)
check(approx(p3["L17"], 500000),
      "MODE C: L17 = residents' COLUMN A (ENTIRE income) = 500,000, PART-YEAR counted as RESIDENT",
      f"L17 wrong: {p3['L17']}")
check(approx(p3["L18"], 120000), "MODE C: L18 = nonresidents' Column B = 120,000, negative owner EXCLUDED entirely",
      f"L18 wrong: {p3['L18']}")
check(approx(p3["L19"], 620000) and approx(CO.co_ptet_tax(OWNERS_C), 27280),
      "MODE C: L19 = 620,000 and L20 = 27,280", f"L19/L20 wrong: {p3['L19']} / {CO.co_ptet_tax(OWNERS_C)}")
check(CO.co_owner_status(OWNERS_C[1]) == "resident",
      "PART-YEAR owners are treated as RESIDENTS for K-1 purposes", "part-year treatment wrong")
check(approx(CO.co_ptet_bases(OWNERS_C + [{"residency": "resident", "owner_kind": "c_corp",
                                           "unitary_ccorp": True, "col_a": 900000}])["L17"], 500000),
      "MODE C: a UNITARY C-corporation partner is excluded from the base entirely",
      "unitary C-corp exclusion failed")

# MODE A -- and the C1 carve-out that makes it correct
OWNERS_A = [{"residency": "resident", "owner_kind": "individual", "col_a": 250000},
            {"residency": "nonresident", "owner_kind": "individual", "dr0107": True, "col_b": 80000}]
check(CO.co_composite_required(MS, OWNERS_A) is False,
      "MODE A / C1 ORACLE: no composite required for an S corp whose nonresidents all filed DR 0107",
      "C1 REGRESSION: the S-corp all-owners-excluded carve-out did not fire (false-positive RED)")
check(CO.co_composite_required(M65, OWNERS_A) is False,
      "MODE A: same carve-out on the partnership side", "partnership all-owners-excluded carve-out failed")
check(CO.co_composite_required(M65, OWNERS_B) is True,
      "composite IS required when an unexcluded nonresident individual exists", "mandatory-composite test failed")
check(CO.co_composite_required(M65, OWNERS_B, is_publicly_traded=True) is False,
      "the PTP carve-out suppresses the requirement on the partnership side",
      "PTP carve-out failed")
check(CO.co_composite_required(MS, OWNERS_B, is_publicly_traded=True) is True,
      "the PTP carve-out does NOT exist for an S corp -- composite still required",
      "PTP carve-out wrongly applied to an S corp")
check(CO.co_composite_required(M65, OWNERS_B, salt_parity_election=True) is False,
      "a SALT Parity election suppresses the composite requirement in BOTH modules",
      "election carve-out failed")

# Mode A / Mode C force DR 0106CR column C to zero
for mode, label in ((CO.CO_MODE_A, "Mode A"), (CO.CO_MODE_C, "Mode C")):
    cols = CO.co_cr_columns(mode, 45000)
    check(cols["B"] == 45000 and cols["C"] == 0.0,
          f"{label}: DR 0106CR column B = column A and column C = 0", f"{label} DR 0106CR column rule wrong")

# ══════════════════════════════════════════════════════════════════════════
# 4e. ARITHMETIC ORACLE -- the TWO RATE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════
check(CO.co_rate("composite", 2025) == "0.044", "composite rate (L13) = 0.044 for TY2025", "composite rate wrong")
check(CO.co_rate("ptet", 2025) == "0.044", "PTET rate (L20) = 0.044 for TY2025", "PTET rate wrong")
check(CO.CO_COMPOSITE_RATE is not CO.CO_PTET_RATE,
      "TWO SEPARATE constants -- CO_COMPOSITE_RATE and CO_PTET_RATE are NOT the same object",
      "RATE COLLAPSE: the two rate constants are the same object")
check("39-22-104" in CO.CO_COMPOSITE_RATE_AUTHORITY and "39-22-301" in CO.CO_PTET_RATE_AUTHORITY,
      "the two rates carry DIFFERENT statutory authorities (Sec. 39-22-104 vs Sec. 39-22-301)",
      "rate authorities not distinct")
check(CO.CO_COMPOSITE_RATE_AUTHORITY != CO.CO_PTET_RATE_AUTHORITY,
      "composite cites the INDIVIDUAL rate statute; PTET cites the CORPORATE rate statute",
      "rate authority strings are identical")
try:
    CO.co_rate("nonsense")
    FAILURES.append("co_rate accepted an unknown rate kind")
except ValueError:
    PASSES.append("co_rate rejects an unknown rate kind")

# ══════════════════════════════════════════════════════════════════════════
# 4f. ARITHMETIC ORACLE -- due date, penalty, estimated tax, DR 0106CR, Part V
# ══════════════════════════════════════════════════════════════════════════
dd = CO.co_due_dates()
check(dd["original_month"] == 4 and dd["original_day"] == 15,
      "DUE DATE: 15th day of the FOURTH month (April 15) -- NOT the C corp's fifth",
      f"due date wrong: month {dd['original_month']} day {dd['original_day']}")
check(dd["extension_months"] == 6 and dd["extension_to_pay"] is False,
      "automatic 6-month extension (October 15), and NO extension to pay", "extension rule wrong")
check(dd["extension_voucher"] == "DR 0158-N", "extension voucher is DR 0158-N (not the C corp's DR 0158-C)",
      "extension voucher wrong")

check(approx(CO.co_delinquency_penalty(10000, 1, 0.5), 500),
      "L29 penalty month 1 = max($5, 10,000 x 5%) = 500", "L29 month-1 penalty wrong")
check(approx(CO.co_delinquency_penalty(10000, 20, 0.5), 1200),
      "L29 penalty CAPS at 12% (20 months -> 1,200, not 1,450)", "L29 12% cap failed")
check(approx(CO.co_delinquency_penalty(10000, 3, 0.95), 0.0),
      "L29 penalty suppressed when 90%+ was paid by the ORIGINAL due date", "L29 90% gate failed")
check(approx(CO.co_delinquency_penalty(20, 1, 0.0), 5.0),
      "L29 penalty floors at the $5 minimum for a tiny balance", "L29 $5 floor failed")

check(CO.co_estimated_payments_required(5000.01) is True and CO.co_estimated_payments_required(5000) is False,
      "W9 RULING: estimated payments required STRICTLY ABOVE $5,000 (exactly $5,000 does not trigger)",
      "W9 threshold not built as strictly-greater-than")
check(approx(CO.co_required_annual_payment(100000, 40000), 40000),
      "DR 0233: required annual = lesser of 70% current (70,000) and 100% prior (40,000) = 40,000",
      "required annual payment wrong")
check(approx(CO.co_required_annual_payment(100000, 40000, making_salt_parity_election=True,
                                           elected_salt_parity_prior_year=False), 70000),
      "DR 0233 line 6: a FIRST-YEAR electing entity LOSES the prior-year leg -> 70,000",
      "first-year-election prior-year block failed")
check(approx(CO.co_required_annual_payment(100000, 40000, prior_3yr_income_1m_or_more=True), 70000),
      "the $1,000,000 large-entity test also blocks the prior-year leg", "large-entity block failed")
check(CO.co_estimated_interest_rate(2025) == "0.12" and CO.co_estimated_interest_rate(2026) == "0.11",
      "DR 0233 split-year interest: 12% for 2025 dates, 11% for 2026 dates", "estimated interest rates wrong")
check(CO._yk(CO.CO_EST_ANNUALIZED_METHOD_AVAILABLE, 2025) is False,
      "PTEs get NO annualized income installment method (C corps do) -- a genuine divergence",
      "annualized-method flag wrong")

check(approx(CO.co_cr_total({"1": 1000, "2": 2000, "3": 3000, "4": 4000, "5": 5000, "37": 7000}), 12000),
      "DR 0106CR L38 sums lines 5..37 ONLY (12,000) -- lines 1-4 excluded",
      "DR 0106CR L38 range wrong")

pv = CO.co_part_v(800000, 0, 0, no_out_of_state_activity=True)
check(approx(pv["L9"], 1.0) and approx(pv["L14"], 800000),
      "Part V: no out-of-state activity -> 100% Colorado (Sec. 39-22-303.6(3)(a))", "Part V 100% path wrong")
pv0 = CO.co_part_v(800000, 100000, 0)
check(pv0["L9"] is None and pv0["L14"] is None,
      "[UNV-9]: a ZERO 'Everywhere' denominator yields an UNDEFINED ratio, never a silent 0",
      "zero-denominator produced a silent value")
pv2 = CO.co_part_v(1000000, 250000, 1000000, nonapportionable_total_l10f=200000, allocable_to_co_l13f=50000)
check(approx(pv2["L9"], 0.25) and approx(pv2["L11"], 800000) and approx(pv2["L12"], 200000)
      and approx(pv2["L14"], 250000),
      "Part V: ratio 25%, L11 = 800,000, L12 = 200,000, L14 = 250,000", f"Part V arithmetic wrong: {pv2}")
pv3 = CO.co_part_v(1000000, 250000, 1000000, nonapportionable_total_l10f=200000,
                   allocable_to_co_l13f=50000, all_income_apportionable=True)
check(approx(pv3["L10f"], 0) and approx(pv3["L13f"], 0),
      "Sec. 39-22-303.6(8) election forces 0 on Part V lines 10 and 13", "all-apportionable election failed")

piv = CO.co_part_iv(CO.CO_MODE_A)
check(approx(piv["L21"], 0), "MODE A: line 21 = 0 (informational-only, still a mandatory filing)", "Mode A L21 wrong")
check(approx(CO.co_part_iv(CO.CO_MODE_B, composite_l16=13200)["L21"], 13200),
      "MODE B: line 21 takes line 16", "Mode B L21 wrong")
check(approx(CO.co_part_iv(CO.CO_MODE_C, ptet_l20=27280)["L21"], 27280),
      "MODE C: line 21 takes line 20", "Mode C L21 wrong")
piv2 = CO.co_part_iv(CO.CO_MODE_B, composite_l16=13200, payments_l25=20000, credited_forward_l34=3000)
check(approx(piv2["L33"], 6800) and approx(piv2["L35"], 3800),
      "Part IV overpayment: L33 = 6,800, L34 = 3,000 credited forward, L35 = 3,800 refunded",
      f"Part IV overpayment wrong: {piv2}")

# guaranteed payments: IN line 2, OUT of every base (W5)
gp_in_l2 = CO.co_line2(M65, {"4c": 60000})
check(approx(gp_in_l2, 60000), "W5: guaranteed payments (Sch.K 4c) ARE inside DR 0106 line 2", "GP not in L2")
check("4" not in CO.CO_K1_L16_LINES,
      "W5: DR 0106K line 4 is SKIPPED by the line-16 summation (and by Parts II and III)",
      "K-1 line 4 was not excluded from the line-16 range")
check(CO.CO_K1_BOX_MAP[MS]["4"] is None and CO.CO_K1_BOX_MAP[M65]["4"] == ["4c"],
      "F3: K-1 line 4 is N/A for an S corp and Box 4c for a partnership", "F3 box map wrong")

# module guard
try:
    CO.co_line2("1120", {"2": 1})
    FAILURES.append("co_line2 accepted an unknown module")
except (ValueError, KeyError):
    PASSES.append("fork helpers reject an unknown module rather than defaulting silently")

# ══════════════════════════════════════════════════════════════════════════
# Report
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print(f"CO_DR0106 validation -- {len(PASSES)} PASS / {len(FAILURES)} FAIL "
      f"({len(PASSES) + len(FAILURES)} assertions)")
print("=" * 72)
if FAILURES:
    print("\nFAILURES:")
    for f in FAILURES:
        print(f"  [FAIL] {f}")
else:
    print("\nAll assertions passed.")
print(f"\nSeeded: facts {FormFact.objects.filter(tax_form=form).count()} / "
      f"rules {FormRule.objects.filter(tax_form=form).count()} / "
      f"lines {FormLine.objects.filter(tax_form=form).count()} / "
      f"diagnostics {FormDiagnostic.objects.filter(tax_form=form).count()} / "
      f"scenarios {TestScenario.objects.filter(tax_form=form).count()} / "
      f"flow assertions {FlowAssertion.objects.filter(assertion_id__startswith='FA-CO').count()} / "
      f"authority links {RuleAuthorityLink.objects.filter(form_rule__tax_form=form).count()}")
print(f"READY_TO_SEED on disk: {CO.READY_TO_SEED} (must be False)")
sys.exit(1 if FAILURES else 0)
