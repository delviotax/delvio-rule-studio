# -*- coding: utf-8 -*-
"""GA-500 spec amendment for 1040 BATCH-014 items 2 and 5 (Ken, 2026-09-05, s332).

Gate 1, Ken direct, both in one message:
  item 2 — "worksheet approach"   (RIE capital-gain allocation between spouses)
  item 5 — "go ahead with the spec" (IND-CR 212 community based faculty preceptor credit)

SOURCE, fetched fresh 2026-09-05: the 2025 IT-511 Individual Income Tax Booklet
(dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download).
  p.24 (Retirement Income Exclusion):  "Income or losses should be allocated to the
        person who owns the item. If any item is held jointly, the income or loss
        should be allocated to each taxpayer at 50%."
  p.64 (Form IND-CR 212, Rev. 07/09/25): O.C.G.A. § 48-7-29.22; TY 2019-2026; physician
        $500 x rotations 1-3 (<= $1,500) + $1,000 x rotations 4-10 (<= $7,000), total
        <= $8,500; APRN / PA $375 x 1-3 (<= $1,125) + $750 x 4-10 (<= $5,250), total
        <= $6,375; no more than ten rotations per calendar year; no carryforward, no
        carryback; AHEC (Augusta University) certification enclosed; the filer certifies
        no payment was received for the training. C1 "credit used this year (enter no
        more than the total of A3 and B3)" -> IND-CR Summary Worksheet line 10 ->
        Form 500 line 20.
  p.67 (IND-CR Summary Worksheet): line 10 = "Community Based Faculty Preceptor
        Credit (IND-CR 212, Line C1)"; line 13 total -> Form 500 page 3 line 20.

Edits the OWNING LOADER (load_ga500_form_500.py, update_or_create-safe) and the
independent math gate (check_ga500_integrity.py). Every anchor must match EXACTLY
ONCE; a miss aborts before anything is written (the s232/s253 discipline).
"""
import io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "specs", "management", "commands", "load_ga500_form_500.py")
H = os.path.join(ROOT, "check_ga500_integrity.py")

s0 = io.open(P, encoding="utf-8").read()
s = s0

ALLOC = (
    "─── ALLOCATION BETWEEN SPOUSES DEFINED 2026-09-05 (Ken, Gate-1 direct, 1040 BATCH-014 #2: "
    "“worksheet approach”). SOURCE, VERBATIM (2025 IT-511 p.24, Retirement Income Exclusion): "
    "“Income or losses should be allocated to the person who owns the item. If any item is held "
    "jointly, the income or loss should be allocated to each taxpayer at 50%.” THIS IS ITEM-LEVEL "
    "ALLOCATION: each item of income or loss goes to its OWNER, signed; only a JOINTLY-held item splits "
    "50/50 (under the vendor-aware rounding convention above). It is NOT a proportional share of a "
    "return-level total by weight. CAPITAL GAINS (worksheet L9) in particular: each spouse’s L9 = "
    "that spouse’s own signed current-year results (Form 8949 rows, capital-gain distributions, K-1 "
    "capital items) PLUS that spouse’s own prior-year loss carryover component, joint items 50/50 "
    "— so a joint return whose owners net 431 − 939 = −508 and 475 − 2,145 = −1,670 "
    "prints exactly those two columns (the BATCH-014 fixture; the weight proration the engine used "
    "gave −894 / −1,284 and was WRONG by the worksheet). A carryover pool therefore carries a "
    "PER-OWNER component, not one owner tag. ⚠ THE §1211(b) $3,000 CAP: when the federal cap "
    "binds, the sum of the owners’ signed nets is MORE negative than 1040 line 7 and the booklet "
    "does NOT say how the disallowed portion is attributed — UNSPECIFIED. The engine applies "
    "item-level allocation only when the owners’ nets re-add to line 7 exactly (no cap binding, "
    "every source owner-attributed); otherwise it keeps its return-level allocation and D_GA500_017 "
    "names the columns as preparer-entered. NOT a rounding rule: the 50/50 vendor clause governs "
    "only genuinely joint items."
)

EDITS = [
    # ── item 2: R-GA500-RIE formula ──────────────────────────────────────────
    ("RIE formula — allocation sentence",
     '"Each spouse qualifies separately; jointly-owned income split 50/50. "',
     '"Each spouse qualifies separately. EACH ITEM OF INCOME OR LOSS GOES TO ITS OWNER, SIGNED; only a "\n'
     '                 "jointly-held item splits 50/50 (IT-511 p.24 verbatim; Ken 2026-09-05 ‘worksheet approach’, "\n'
     '                 "BATCH-014 #2) — L9 capital gains = the spouse’s own current results + own carryover component, "\n'
     '                 "never a weight-prorated share of 1040 line 7. Cap-binding attribution UNSPECIFIED (see description). "', 1),

    # ── item 2: R-GA500-RIE description addendum ─────────────────────────────
    ("RIE description addendum",
     '"this ruling — flagged, not adopted.")},',
     '"this ruling — flagged, not adopted. "\n'
     '                     "%s")},' % ALLOC, 1),

    # ── item 2: the two L9 facts stop being undefined ────────────────────────
    ("TP L9 fact notes",
     '"notes": "RIE worksheet line 9 (unearned)."},',
     '"notes": "RIE worksheet line 9 (unearned). ITEM-LEVEL (IT-511 p.24; Ken 2026-09-05): the taxpayer’s own '
     'signed current-year capital results + the taxpayer’s own carryover component; joint items at 50%. '
     'Never a weight-prorated share of 1040 line 7."},', 1),
    ("SP L9 fact notes",
     '"notes": "Spouse RIE worksheet line 9."},',
     '"notes": "Spouse RIE worksheet line 9. ITEM-LEVEL (IT-511 p.24; Ken 2026-09-05): the spouse’s own signed '
     'current-year capital results + the spouse’s own carryover component; joint items at 50%."},', 1),

    # ── item 5: the IND-CR 212 authority excerpt, in the IT-511 source ──────
    ("212 excerpt (IT-511 source)",
     '            {\n                "excerpt_label": "Low Income Credit table + worksheet (IT-511 p35, 2025)",',
     '            {\n'
     '                "excerpt_label": "Form IND-CR 212 Community Based Faculty Preceptor Tax Credit (IT-511 p64, Rev. 07/09/25)",\n'
     '                "excerpt_text": (\n'
     '                    "O.C.G.A. § 48-7-29.22 provides an income tax credit for a community based faculty "\n'
     '                    "preceptor that conducts a preceptorship rotation(s). This tax credit is applicable for "\n'
     '                    "taxable years beginning on or after January 1, 2019 and ending on or before December 31, "\n'
     '                    "2026. For a community based faculty preceptor who is a physician as defined in O.C.G.A. "\n'
     '                    "§ 43-34-21, the credit shall accrue on a per preceptorship rotation basis in the amount of "\n'
     '                    "$500 for the first, second, or third preceptorship rotation and $1,000 for the fourth, "\n'
     '                    "fifth, sixth, seventh, eighth, ninth, or tenth preceptorship rotation completed in one "\n'
     '                    "calendar year. For a community based faculty preceptor who is an advanced practice "\n'
     '                    "registered nurse as defined in O.C.G.A. § 43-26-3 or a physician assistant as defined in "\n'
     '                    "O.C.G.A. § 43-34-102, the credit shall accrue on a per preceptorship rotation basis in the "\n'
     '                    "amount of $375 for the first, second, or third preceptorship rotation and $750 for the "\n'
     '                    "fourth, fifth, sixth, seventh, eighth, ninth, or tenth preceptorship rotation completed "\n'
     '                    "in one calendar year. An individual shall not accrue credit for more than ten "\n'
     '                    "preceptorship rotations in one calendar year. The credit cannot be carried forward and "\n'
     '                    "cannot be carried back. Certification from the Area Health Education Centers Program "\n'
     '                    "Office at Augusta University must be enclosed with the return. By filing this form I "\n'
     '                    "certify that I did not receive payment during such tax year from any source for the "\n'
     '                    "training of a medical student, advanced practice registered nurse student, or physician "\n'
     '                    "assistant student. A1 rotations 1-3 (no more than 3) x $500 (not to exceed $1,500); A2 "\n'
     '                    "rotations 4-10 (no more than 7) x $1,000 (not to exceed $7,000); A3 = A1 + A2 (cannot "\n'
     '                    "exceed $8,500). B1 x $375 (not to exceed $1,125); B2 x $750 (not to exceed $5,250); B3 = "\n'
     '                    "B1 + B2 (cannot exceed $6,375). C1 credit used this year (enter no more than the total "\n'
     '                    "of Line A3 and Line B3) -> IND-CR Summary Worksheet Line 10 (p.67) -> Form 500 line 20."\n'
     '                ),\n'
     '                "summary_text": "IND-CR 212: per-rotation credit ($500/$1,000 physician; $375/$750 APRN/PA), 3 + 7 rotation caps, no carryforward, AHEC certification -> Summary L10 -> Form 500 L20.",\n'
     '                "is_key_excerpt": True,\n'
     '            },\n'
     '            {\n                "excerpt_label": "Low Income Credit table + worksheet (IT-511 p35, 2025)",', 1),

    # ── item 5: the other-credits residual now EXCLUDES the preceptor credit ─
    ("g_indcr_other_credits notes",
     '"notes": "Form 500 line 20 (IND-CR Summary), excluding the computed child-care credit. Direct-entry."},',
     '"notes": "Form 500 line 20 (IND-CR Summary) RESIDUAL: every IND-CR credit EXCEPT the computed child-care '
     'credit (IND-CR 202) and the computed preceptor credit (IND-CR 212, 2026-09-05). Direct-entry."},\n'
     '\n'
     '    # — Community based faculty preceptor credit (IND-CR 212) — Ken 2026-09-05, BATCH-014 #5 —\n'
     '    {"fact_key": "g_preceptor_role", "label": "IND-CR 212 preceptor role (none / physician / aprn_pa)", "data_type": "choice", "default_value": "none", "sort_order": 146, "notes": "Form IND-CR 212 (IT-511 p.64): Part A = physician (O.C.G.A. § 43-34-21); Part B = advanced practice registered nurse (§ 43-26-3) or physician assistant (§ 43-34-102). One role per filer; none = no credit."},\n'
     '    {"fact_key": "g_preceptor_rotations_1_3", "label": "IND-CR 212 line A1/B1 — preceptorship rotations 1-3 completed (max 3)", "data_type": "integer", "default_value": "0", "sort_order": 147, "notes": "Count of the first through third rotations completed in the calendar year (0-3). x $500 physician / x $375 APRN-PA."},\n'
     '    {"fact_key": "g_preceptor_rotations_4_10", "label": "IND-CR 212 line A2/B2 — preceptorship rotations 4-10 completed (max 7)", "data_type": "integer", "default_value": "0", "sort_order": 148, "notes": "Count of the fourth through tenth rotations (0-7); nonzero only when rotations 1-3 = 3. x $1,000 physician / x $750 APRN-PA. Ten rotations per calendar year is the statutory ceiling."},\n'
     '    {"fact_key": "g_preceptor_credit_used", "label": "IND-CR 212 line C1 — credit used this year (blank = the computed total)", "data_type": "decimal", "default_value": "", "sort_order": 149, "notes": "Form line C1: ‘enter no more than the total of Line A3 and Line B3’. Blank = A3 + B3; a keyed figure above the total is refused (D_GA500_018). No carryforward and no carryback — an unused remainder is lost."},\n'
     '    {"fact_key": "g_preceptor_certification_enclosed", "label": "IND-CR 212 — AHEC Program Office (Augusta University) certification enclosed", "data_type": "boolean", "default_value": "False", "sort_order": 150, "notes": "Required enclosure per the form; unasserted with a nonzero credit -> D_GA500_018 warning."},', 1),

    # ── item 5: R-GA500-CC's line-20 composition names the new component ───
    ("R-GA500-CC description",
     '"description": "O.C.G.A. §48-7-29.10. Computed from the federal Form 2441 result."},',
     '"description": "O.C.G.A. §48-7-29.10. Computed from the federal Form 2441 result. LINE 20 COMPOSITION (2026-09-05): '
     'line 20 = CC-3 (this rule) + 212-C1 (R-GA500-PRECEPTOR) + g_indcr_other_credits (the residual for every other IND-CR credit)."},\n'
     '\n'
     '    {"rule_id": "R-GA500-PRECEPTOR", "title": "Line 20 — IND-CR 212 community based faculty preceptor credit", "rule_type": "calculation", "precedence": 9, "sort_order": 16,\n'
     '     "formula": ("Physician (Part A): A1 = min(rotations_1_3, 3) x $500 (<= $1,500); A2 = min(rotations_4_10, 7) x $1,000 (<= $7,000); "\n'
     '                 "A3 = A1 + A2 (<= $8,500). APRN / PA (Part B): B1 = min(rotations_1_3, 3) x $375 (<= $1,125); B2 = min(rotations_4_10, 7) x $750 "\n'
     '                 "(<= $5,250); B3 = B1 + B2 (<= $6,375). Exactly one part applies (g_preceptor_role). C1 = g_preceptor_credit_used when keyed "\n'
     '                 "(refused if > A3 + B3), else A3 + B3. C1 -> IND-CR Summary Worksheet line 10 -> Form 500 line 20 (nonrefundable; "\n'
     '                 "the line-22 cap against line 16 applies). NO carryforward, NO carryback. Window: taxable years beginning on/after "\n'
     '                 "2019-01-01 and ending on/before 2026-12-31 — ZERO outside it, never a latest-year fallback (the HB 463 precedent)."),\n'
     '     "inputs": ["g_preceptor_role", "g_preceptor_rotations_1_3", "g_preceptor_rotations_4_10", "g_preceptor_credit_used", "g_preceptor_certification_enclosed"],\n'
     '     "outputs": ["212-A1", "212-A2", "212-A3", "212-B1", "212-B2", "212-B3", "212-C1", "20"],\n'
     '     "description": "O.C.G.A. § 48-7-29.22 via Form IND-CR 212 (Rev. 07/09/25) transcribed from the 2025 IT-511 p.64 — the per-rotation amounts, the 3 + 7 rotation caps and the ten-per-year ceiling, the no-carry rule and the AHEC certification are the form’s own words (see the excerpt). Authored 2026-09-05 on Ken’s Gate-1 direct (BATCH-014 #5: ‘go ahead with the spec’). ⚠ The statute text itself was NOT fetched — the form is the primary transcription; if § 48-7-29.22 is later read to differ from the form, the statute governs and this rule is stale."},', 1),

    # ── item 5: the lines ────────────────────────────────────────────────────
    ("212 lines after CC-3",
     '    {"line_number": "CC-3", "description": "IND-CR 202: GA child & dependent care credit = 50% of the federal §21 credit", "line_type": "calculated"},',
     '    {"line_number": "CC-3", "description": "IND-CR 202: GA child & dependent care credit = 50% of the federal §21 credit", "line_type": "calculated"},\n'
     '\n'
     '    # — Community based faculty preceptor credit (IND-CR 212) —\n'
     '    {"line_number": "212-A1", "description": "IND-CR 212 A1: physician rotations 1-3 x $500 (not to exceed $1,500)", "line_type": "calculated"},\n'
     '    {"line_number": "212-A2", "description": "IND-CR 212 A2: physician rotations 4-10 x $1,000 (not to exceed $7,000)", "line_type": "calculated"},\n'
     '    {"line_number": "212-A3", "description": "IND-CR 212 A3: physician current-year credit = A1 + A2 (cannot exceed $8,500)", "line_type": "calculated"},\n'
     '    {"line_number": "212-B1", "description": "IND-CR 212 B1: APRN/PA rotations 1-3 x $375 (not to exceed $1,125)", "line_type": "calculated"},\n'
     '    {"line_number": "212-B2", "description": "IND-CR 212 B2: APRN/PA rotations 4-10 x $750 (not to exceed $5,250)", "line_type": "calculated"},\n'
     '    {"line_number": "212-B3", "description": "IND-CR 212 B3: APRN/PA current-year credit = B1 + B2 (cannot exceed $6,375)", "line_type": "calculated"},\n'
     '    {"line_number": "212-C1", "description": "IND-CR 212 C1: credit used this year (<= A3 + B3) -> IND-CR Summary Worksheet line 10 -> Form 500 line 20", "line_type": "calculated"},', 1),

    # ── item 5: the diagnostic ───────────────────────────────────────────────
    ("D_GA500_018 before 017",
     '    {"diagnostic_id": "D_GA500_017", "title"',
     '    {"diagnostic_id": "D_GA500_018", "title": "IND-CR 212 preceptor credit — caps, window, certification", "severity": "error",\n'
     '     "condition": "g_preceptor_role != none AND (g_preceptor_rotations_1_3 > 3 OR g_preceptor_rotations_4_10 > 7 OR (g_preceptor_rotations_4_10 > 0 AND g_preceptor_rotations_1_3 < 3) OR g_preceptor_credit_used > 212-A3 + 212-B3 OR tax_year outside 2019-2026); WARNING when 212-C1 > 0 AND NOT g_preceptor_certification_enclosed",\n'
     '     "message": "IND-CR 212: no more than three first-through-third rotations and seven fourth-through-tenth rotations (ten per calendar year); rotations 4-10 presuppose three completed; the credit used cannot exceed A3 + B3 and cannot be carried forward or back; the credit exists only for taxable years 2019-2026; the AHEC Program Office certification must be enclosed.",\n'
     '     "notes": "Error on a cap, window or overclaim; warning on the missing certification. Authored 2026-09-05 (BATCH-014 #5) from IT-511 p.64."},\n'
     '    {"diagnostic_id": "D_GA500_017", "title"', 1),

    # ── item 5: scenario T21 (before T20 in the list; sort_order orders it) ──
    ("T21 scenario",
     '{"scenario_name": "GA500-T20 — LIC counts children only',
     '{"scenario_name": "GA500-T21 — IND-CR 212 physician preceptor, 3 + 5 rotations (2025)", "scenario_type": "normal", "sort_order": 21,\n'
     '     "inputs": {"tax_year": 2025, "g_residency_status": "full_year", "g_filing_status": "A", "g_num_dependents": 0, "g_federal_agi": 200000, "g_preceptor_role": "physician", "g_preceptor_rotations_1_3": 3, "g_preceptor_rotations_4_10": 5, "g_preceptor_certification_enclosed": True},\n'
     '     "expected_outputs": {"13": 188000, "15c": 188000, "16": 9757, "212-A1": 1500, "212-A2": 5000, "212-A3": 6500, "212-C1": 6500, "20": 6500, "22": 6500, "23": 3257},\n'
     '     "notes": "A1 = 3 x 500 = 1,500; A2 = 5 x 1,000 = 5,000; A3 = 6,500; C1 blank -> 6,500 -> line 20. Tax 188,000 x 5.19% = 9,757.20 -> 9,757; balance 3,257. IT-511 p.64."},\n'
     '    {"scenario_name": "GA500-T22 — IND-CR 212 APRN preceptor, 2 rotations, credit keyed below the total (2025)", "scenario_type": "edge_case", "sort_order": 22,\n'
     '     "inputs": {"tax_year": 2025, "g_residency_status": "full_year", "g_filing_status": "A", "g_num_dependents": 0, "g_federal_agi": 60000, "g_preceptor_role": "aprn_pa", "g_preceptor_rotations_1_3": 2, "g_preceptor_rotations_4_10": 0, "g_preceptor_credit_used": 500, "g_preceptor_certification_enclosed": True},\n'
     '     "expected_outputs": {"13": 48000, "16": 2491, "212-B1": 750, "212-B3": 750, "212-C1": 500, "20": 500, "22": 500, "23": 1991},\n'
     '     "notes": "B1 = 2 x 375 = 750; the filer keys C1 = 500 (<= 750) -> line 20 = 500; the unused 250 is LOST (no carryforward). Tax 48,000 x 5.19% = 2,491.20 -> 2,491."},\n'
     '    {"scenario_name": "GA500-T20 — LIC counts children only', 1),

    # ── item 5: rule links ───────────────────────────────────────────────────
    ("212 rule links",
     '    ("R-GA500-CC", "GA_OCGA_48_7", "primary", "§48-7-29.10 child & dependent care credit (50%)"),',
     '    ("R-GA500-CC", "GA_OCGA_48_7", "primary", "§48-7-29.10 child & dependent care credit (50%)"),\n'
     '    ("R-GA500-PRECEPTOR", "GA_2025_IT511", "primary", "Form IND-CR 212 (IT-511 p.64) — per-rotation amounts, caps, window, no-carry, certification"),\n'
     '    ("R-GA500-PRECEPTOR", "GA_OCGA_48_7", "primary", "§48-7-29.22 community based faculty preceptor credit"),', 1),

    # ── item 5: FA-GA500-15 ──────────────────────────────────────────────────
    ("FA-15 before FA-14",
     '    {"assertion_id": "FA-GA500-14", "assertion_type": "reconciliation"',
     '    {"assertion_id": "FA-GA500-15", "assertion_type": "flow_assertion", "entity_types": ["1040"], "sort_order": 15,\n'
     '     "title": "IND-CR 212 preceptor credit used -> Form 500 line 20", "description": "Validates R-GA500-PRECEPTOR. The credit used (212-C1, <= A3 + B3) reaches Form 500 line 20 through the IND-CR Summary Worksheet line 10, once.",\n'
     '     "definition": {"kind": "flow_assertion", "form": "500", "source_line": "212-C1", "must_write_to": ["500.20"]}},\n'
     '    {"assertion_id": "FA-GA500-14", "assertion_type": "reconciliation"', 1),

    # ── identity notes ───────────────────────────────────────────────────────
    ("identity notes",
     '"changes; not a CHANGE_REGISTER item."',
     '"changes; not a CHANGE_REGISTER item. AMENDED 2026-09-05 (s332, 1040 BATCH-014 #2 + #5, Ken Gate-1 "\n'
     '                "direct): R-GA500-RIE allocation between spouses is ITEM-LEVEL per IT-511 p.24 verbatim (cap-binding "\n'
     '                "attribution unspecified); NEW R-GA500-PRECEPTOR — IND-CR 212 community based faculty preceptor "\n'
     '                "credit (5 facts, 7 lines 212-A1..C1, D_GA500_018, T21/T22, FA-GA500-15; line 20 = CC-3 + 212-C1 + "\n'
     '                "the g_indcr_other_credits residual)."', 1),
]

for label, old, new, want in EDITS:
    got = s.count(old)
    assert got == want, "%s: expected %d anchor hit(s), found %d" % (label, want, got)
    s = s.replace(old, new, want)
    print("  ok  %s" % label)
compile(s, P, "exec")
assert s.count('"rule_id": "R-GA500-PRECEPTOR"') == 1
assert s.count('"diagnostic_id": "D_GA500_018"') == 1
assert s.count('"assertion_id": "FA-GA500-15"') == 1
assert s.count("GA500-T21") == 1 and s.count("GA500-T22") == 1
io.open(P + ".new", "w", encoding="utf-8", newline="\n").write(s)
os.replace(P + ".new", P)
print("\nload_ga500_form_500.py: %d -> %d chars" % (len(s0), len(s)))

# ── the independent math gate learns the 212 arithmetic ─────────────────────
h0 = io.open(H, encoding="utf-8").read()
h = h0
old = '    l20 = cc + D(inp.get("g_indcr_other_credits"))\n'
assert h.count(old) == 1
new = (
    '    # — IND-CR 212 preceptor credit (IT-511 p.64; authored 2026-09-05) —\n'
    '    role = inp.get("g_preceptor_role") or "none"\n'
    '    r13 = min(int(D(inp.get("g_preceptor_rotations_1_3"))), 3)\n'
    '    r410 = min(int(D(inp.get("g_preceptor_rotations_4_10"))), 7)\n'
    '    c1 = Decimal(0)\n'
    '    if role == "physician" and 2019 <= year <= 2026:\n'
    '        a1, a2 = Decimal(r13 * 500), Decimal(r410 * 1000)\n'
    '        out["212-A1"], out["212-A2"], out["212-A3"] = a1, a2, a1 + a2\n'
    '        c1 = a1 + a2\n'
    '    elif role == "aprn_pa" and 2019 <= year <= 2026:\n'
    '        b1, b2 = Decimal(r13 * 375), Decimal(r410 * 750)\n'
    '        out["212-B1"], out["212-B2"], out["212-B3"] = b1, b2, b1 + b2\n'
    '        c1 = b1 + b2\n'
    '    keyed = inp.get("g_preceptor_credit_used")\n'
    '    if c1 and keyed not in (None, ""):\n'
    '        c1 = min(c1, D(keyed))\n'
    '    if c1:\n'
    '        out["212-C1"] = c1\n'
    '    l20 = cc + c1 + D(inp.get("g_indcr_other_credits"))\n'
)
h = h.replace(old, new, 1)
compile(h, H, "exec")
io.open(H + ".new", "w", encoding="utf-8", newline="\n").write(h)
os.replace(H + ".new", H)
print("check_ga500_integrity.py: %d -> %d chars (212 recompute added)" % (len(h0), len(h)))
print("\nAPPLIED. Next: run check_ga500_integrity.py, then seed, then verify the export.")
