# -*- coding: utf-8 -*-
"""Apply D-16's Alabama half to load_al_passthrough.py.

Ruled 2026-08-22 (D-16, "Approve all four as recommended"); never applied.
Every claim re-verified 2026-08-29 against the TY2025 ALDOR FINAL PDFs before
this script was written.

PROSE ONLY. No formula operand, condition, input, output or expected_output
moves. The assertions at the bottom prove that.
"""
import io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\dev\delvio-rule-studio\specs\management\commands\load_al_passthrough.py"
s0 = io.open(P, encoding="utf-8").read()
s = s0

EDITS = []  # (label, old, new, expected_count)

# ---------------------------------------------------------------- AL-1
# Schedule EPT-C is the ELECTING ENTITY's incentive-credit schedule
# ("Electing Pass-Through Credits ... ATTACH TO FORM EPT"; Sec C -> EPT line 3,
# Sec D -> EPT line 5e). It is NOT the owner's refundable-credit vehicle.
# EPT line 5d verbatim: "Current Year's Composite Payment(s)/Electing
# Pass-Through Entity Credit(s) from Schedule CP-B, line 3".
EDITS += [
 ("AL-1 header",
  "5% and the owner-side is a REFUNDABLE CREDIT (Schedule EPT-C). The EPT tax is computed/paid on Form",
  "5% and the owner-side is a REFUNDABLE CREDIT claimed on the OWNER's own AL return (NOT Schedule\n"
  "EPT-C, which is the electing ENTITY's incentive-credit schedule). The EPT tax is computed/paid on Form", 1),

 ("AL-1 W4 bless item",
  "W4. AL Electing PTE = 5% on AL taxable income (Form EPT); owner side = REFUNDABLE CREDIT (Sch EPT-C), NOT a",
  "W4. AL Electing PTE = 5% on AL taxable income (Form EPT); owner side = REFUNDABLE CREDIT on the OWNER's\n"
  "    own AL return (upper-tier PTE: Sch CP-B -> Form EPT L5d); NOT Sch EPT-C, and NOT a", 1),

 ("AL-1 excerpt_text",
  "Alabama income tax paid by the electing pass-through entity' (Schedule EPT-C) \u2014 a credit, NOT a ",
  "Alabama income tax paid by the electing pass-through entity' \u2014 a credit, NOT a ", 1),

 ("AL-1 summary_text",
  "owner = REFUNDABLE CREDIT (Sch EPT-C), not a deduction;",
  "owner = REFUNDABLE CREDIT on the owner's own AL return (NOT Sch EPT-C), not a deduction;", 1),

 ("AL-1 rule formula",
  "owner_side = each owner takes a REFUNDABLE CREDIT for its share of ept_tax (Schedule EPT-C)",
  "owner_side = each owner takes a REFUNDABLE CREDIT for its share of ept_tax, claimed on the "
  "owner's own AL return (upper-tier PTE owner: Schedule CP-B -> Form EPT line 5d)", 1),

 ("AL-1 rule description",
  "Owner side = a REFUNDABLE CREDIT for the owner's share (Schedule EPT-C), NOT a deduction (contrast NC).",
  "Owner side = a REFUNDABLE CREDIT for the owner's share, claimed on the owner's OWN Alabama return "
  "(an upper-tier PTE owner carries it via Schedule CP-B -> Form EPT line 5d, verbatim: “Current Year's "
  "Composite Payment(s)/Electing Pass-Through Entity Credit(s) from Schedule CP-B, line 3”). "
  "NOT a deduction (contrast NC). "
  "[CORRECTED 2026-08-29 per D-16 AL-1] It is NOT Schedule EPT-C: the 2025 Schedule EPT-C is "
  "“Electing Pass-Through Credits ... ATTACH TO FORM EPT”, the ELECTING ENTITY's own incentive-credit "
  "schedule (2017 Historic Rehabilitation; Railroad Modernization Act of 2019), feeding Form EPT line 3 "
  "(Sec C) and line 5e (Sec D). [UNVERIFIED] the individual owner's exact Form 40 line \u2014 ALDOR's "
  "Electing-PTE page states the entitlement but does not name the line.", 1),

 ("AL-1 diagnostic message",
  "REFUNDABLE CREDIT for their pro-rata share of the tax (Schedule EPT-C) \u2014 a credit, NOT a deduction",
  "REFUNDABLE CREDIT for their pro-rata share of the tax on their OWN Alabama return \u2014 an upper-tier "
  "PTE owner carries it via Schedule CP-B to Form EPT line 5d. (It is NOT claimed on Schedule EPT-C, "
  "which is the electing ENTITY's own incentive-credit schedule.) A credit, NOT a deduction", 1),

 ("AL-1 F65-A notes",
  "Owners take a refundable credit for their share (Sch EPT-C).",
  "Owners take a refundable credit for their share on their own AL return (not Sch EPT-C).", 1),

 ("AL-1 F20S-A notes",
  "shareholders take a refundable credit (Sch EPT-C).",
  "shareholders take a refundable credit on their own AL return (not Sch EPT-C).", 1),

 ("AL-1 AL_FORM_65 notes",
  "owner-side REFUNDABLE CREDIT via Sch EPT-C \u2014 NOT a deduction)",
  "owner-side REFUNDABLE CREDIT on the owner's own AL return, NOT via Sch EPT-C \u2014 and NOT a deduction)", 1),

 ("AL-1 FA-AL65-EPT description",
  "each owner takes a refundable credit for their share (Sch EPT-C).",
  "each owner takes a refundable credit for their share on their own AL return (not Sch EPT-C).", 1),
]

# ---------------------------------------------------------------- AL-2
# 2025 Form 20S instructions verbatim: "NOTE: An EPT would fill out lines 32-37
# ONLY IF they have Excessive net passive income, LIFO Recapture, or Built-in
# Gains Tax."  The trio is not confined to NON-electing S corps.
EDITS += [
 ("AL-2 header bless",
  "non-electing entity taxes (LIFO/BIG/excess-passive, Line 32) = diagnostic + direct-entry (Q3).",
  "entity taxes (LIFO/BIG/excess-passive, Line 32) = diagnostic + direct-entry (Q3).", 1),

 ("AL-2 W6 bless item",
  "W6. Form 20S non-electing entity taxes (Line 32) = LIFO recapture",
  "W6. Form 20S entity taxes (Line 32; ANY 20S filer, electing or not) = LIFO recapture", 1),

 ("AL-2 excerpt_text",
  "Form 20S Line 32 entity-level tax on a NON-electing S-corp = only ",
  "Form 20S Line 32 entity-level tax (ANY 20S filer \u2014 an electing PTE completes lines 32-37 too if it "
  "has them) = only ", 1),

 ("AL-2 summary_text",
  "20S L32 = LIFO/BIG/excess-passive;",
  "20S L32 = LIFO/BIG/excess-passive (any 20S filer, electing or not);", 1),

 ("AL-2 rule title",
  '"title": "Form 20S non-electing entity taxes (Line 32)"',
  '"title": "Form 20S entity taxes (Line 32) \u2014 LIFO / built-in gains / excess passive"', 1),

 ("AL-2 rule description",
  "W6. Form 20S Line 32: the only AL entity-level tax on a NON-electing S-corp = LIFO recapture",
  "W6. Form 20S Line 32: the only AL entity-level tax on an S corporation = LIFO recapture", 1),

 ("AL-2 rule description tail",
  "Direct-entry (these are the federal S-corp-level taxes, not recomputed).",
  "Direct-entry (these are the federal S-corp-level taxes, not recomputed). "
  "[CORRECTED 2026-08-29 per D-16 AL-2] NOT confined to non-electing S corps \u2014 2025 Form 20S "
  "instructions, verbatim: “NOTE: An EPT would fill out lines 32-37 ONLY IF they have Excessive net "
  "passive income, LIFO Recapture, or Built-in Gains Tax.”", 1),

 ("AL-2 D_AL20S_ENTITY message",
  "The only Alabama entity-level tax on a non-electing S-corporation (Form 20S Line 32) is the sum",
  "The only Alabama entity-level tax on an S corporation (Form 20S Line 32) is the sum", 1),

 ("AL-2 D_AL20S_ENTITY message tail",
  "Enter these directly (they are computed on the federal 1120-S). All other income passes through to shareholders.",
  "Enter these directly (they are computed on the federal 1120-S). All other income passes through to "
  "shareholders. This applies to ANY Form 20S filer: an electing PTE completes lines 32-37 as well, if "
  "it has any of the three (2025 Form 20S instructions).", 1),

 ("AL-2 F20S-B notes",
  "The only entity-level AL tax on a non-electing S-corp.",
  "The only entity-level AL tax on an S corp \u2014 electing or not.", 1),

 ("AL-2 AL_FORM_20S notes",
  "Line 32 non-electing entity taxes = LIFO recapture",
  "Line 32 entity taxes (any 20S filer, electing or not) = LIFO recapture", 1),

 ("AL-2 FA-AL20S-ENTITY description",
  "The non-electing S-corp entity tax (Line 32) = LIFO recapture",
  "The S-corp entity tax (Line 32; any 20S filer, electing or not) = LIFO recapture", 1),
]

# ---------------------------------------------------------------- AL-3 + AL-4
EDITS += [
 ("AL-3 source-conflict note",
  '                "of the voting control."\n',
  '                "of the voting control. "\n'
  '                "[SOURCE CONFLICT, recorded 2026-08-29 per D-16 AL-3] The 2025 Form EPT FACE "\n'
  '                "still prints \'Form PTE-E must be electronically filed via My Alabama "\n'
  '                "Taxes(MAT) prior to the filing of this form.\' That is stale boilerplate "\n'
  '                "(both 25fept.pdf and 25feptc.pdf still carry the PDF title \'EPT 2021.qxp\'). "\n'
  '                "CONTROLLING for TY2025 is the checkbox election -- ALDOR: \'For tax periods "\n'
  '                "beginning on or after January 1, 2025, the Electing Pass-Through Entity must "\n'
  '                "check the Electing PTE box on the timely filed Form 65 or Form 20S ... The "\n'
  '                "Electing PTE box must be checked each year the election is in effect.\' Build "\n'
  '                "to the checkbox, not to the PTE-E line."\n', 1),

 ("AL-4 excerpt due date",
  "Due 15th day of 3rd month (Mar 15, 2026).",
  "Due 15th day of 3rd month; for a TY2025 calendar-year filer that lands MONDAY MAR 16, 2026 "
  "(Mar 15, 2026 is a Sunday; instructions: “If the 15th falls on Saturday or Sunday, the following "
  "Monday”).", 1),

 ("AL-4 summary_text",
  "due Mar 15.",
  "due 15th day of 3rd month (TY2025 calendar filers: Mon Mar 16, 2026).", 1),

 ("AL-4 W6 due date",
  "separate (Form PPT). Due Mar 15 (15th day of 3rd month), NOT the extra month. CONFIRM.",
  "separate (Form PPT). Due 15th day of 3rd month, NOT the extra month; TY2025 calendar filers file\n"
  "    Mon Mar 16, 2026 (the 15th is a Sunday). CONFIRM.", 1),

 ("AL-4 AL_FORM_65 notes",
  "composite PTE-C 5% on nonresidents. Due Mar 15.",
  "composite PTE-C 5% on nonresidents. Due 15th day of 3rd month (TY2025 calendar: Mon Mar 16, 2026).", 1),

 ("AL-4 AL_FORM_20S notes",
  "composite PTE-C 5%; BPT separate (Form PPT). Due Mar 15.",
  "composite PTE-C 5%; BPT separate (Form PPT). Due 15th day of 3rd month (TY2025 calendar: Mon Mar 16, 2026).", 1),
]

for label, old, new, want in EDITS:
    got = s.count(old)
    assert got == want, "%s: expected %d occurrence(s), found %d" % (label, want, got)
    s = s.replace(old, new, want)
    print("  ok  %s" % label)

# ---- proof of scope: nothing computational moved -------------------------
for key in ('"formula":', '"condition":', '"inputs":', '"outputs":',
            '"expected_outputs":', '"definition":', '"check":',
            '"rule_id":', '"diagnostic_id":', '"assertion_id":', '"scenario_name":'):
    assert s0.count(key) == s.count(key), "structural key count moved: %s" % key

for tok in ("* 0.05", "50000", "40000", "15000", "10000", "18000",
            "1000000", "800000", "300000", "200000"):
    assert s0.count(tok) == s.count(tok), "numeric token count moved: %s" % tok

print("\n-- surviving 'EPT-C' mentions (each must be a CORRECT one) --")
for i, ln in enumerate(s.split("\n"), 1):
    if "EPT-C" in ln:
        for frag in re.findall(r".{0,70}EPT-C.{0,70}", ln):
            print("  %4d  ...%s..." % (i, frag.strip()))
print("-- 'CP-B' mentions: %d --" % s.count("CP-B"))

# THE invariant that matters: no surviving text routes the OWNER's refundable
# credit through EPT-C. Every remaining mention must be the entity's schedule
# or an explicit negation.
BAD = [r"CREDIT \(Sch(edule)? EPT-C\)", r"credit .{0,40}\(Sch(edule)? EPT-C\)",
       r"via Sch(edule)? EPT-C(?! )", r"REFUNDABLE CREDIT \(Sch"]
for pat in BAD:
    m = re.search(pat, s)
    assert m is None, "owner-credit-via-EPT-C survives: %r" % (m.group(0) if m else None)
assert s.count("READY_TO_SEED = True") == s0.count("READY_TO_SEED = True") == 1
assert re.search(r"non-?electing S-?corp", s, re.I) is None, "a 'non-electing S-corp' claim survives"

# ⭐ The gate this script earned the hard way: a prose edit that injects a raw
# quote into a double-quoted source string produces a file that STILL passes
# every content assertion above and does not parse. Compile BEFORE replacing.
compile(s, P, "exec")

TMP = P + ".new"
io.open(TMP, "w", encoding="utf-8", newline="\n").write(s)
os.replace(TMP, P)
print("\nload_al_passthrough.py: %d -> %d chars, %d edits applied" % (len(s0), len(s), len(EDITS)))
