# -*- coding: utf-8 -*-
"""R-GA500-RIE: define the RIE worksheet line-10 components.

Gate 1: Ken, direct to this session, 2026-08-30 --
"approve the GA RIE amendment, statute primary".

STATUTE PRIMARY is his explicit instruction and it is load-bearing, not a
formality: the reg's "other similar income" tail invites ejusdem generis
against a list of investment income, and neither ruled component is investment
income. O.C.G.A. §48-7-27(a)(5)(E)(i)'s "shall include but not be limited to"
is an express open-ended grant that does not constrain by similarity at all.
The same reg sentence is also provably stale ($4,000 where statute, the printed
2025 worksheet and RS all say $5,000), which is recorded here as the reason for
the ranking.
"""
import io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\dev\delvio-rule-studio\specs\management\commands\load_ga500_form_500.py"
s0 = io.open(P, encoding="utf-8").read()
s = s0

L10_DEF = (
    "RIE worksheet line 10 (unearned). COMPONENTS DEFINED 2026-08-30 (Ken, Gate-1 direct: "
    "\u201capprove the GA RIE amendment, statute primary\u201d): the \u00a7111 taxable state-tax refund "
    "AND unemployment compensation, each at its GEORGIA-TAXABLE amount. \u26a0 The refund enters at "
    "the federal Schedule 1 line 1 figure \u2014 the \u00a7111 benefit-limited amount \u2014 NEVER gross "
    "1099-G box 2. Unemployment enters at box 1 NET of any same-year repayment (the Schedule 1 "
    "line 7 quantity). \u26a0 \u201cline 10\u201d here is the RIE WORKSHEET line 10, not Form 500 line 10 "
    "(Georgia AGI) and not Schedule 1 line 10 (U.S.-obligation interest) \u2014 three different "
    "line 10s live in this spec."
)

EDITS = [
 # ── 1 · the two facts stop being undefined ────────────────────────────────
 ("TP fact notes",
  '"notes": "RIE worksheet line 10 (unearned)."},',
  '"notes": "%s Owner: unemployment follows the 1099-G row\u2019s owner; the refund is JOINT on an MFJ '
  'return whose prior-year return was joint, so the 50/50 split below governs it, else it is the '
  'taxpayer\u2019s."},' % L10_DEF, 1),

 ("spouse fact notes",
  '"notes": "Spouse RIE worksheet line 10."},',
  '"notes": "Spouse RIE worksheet line 10. %s"},' % L10_DEF, 1),

 # ── 2 · the formula names the population ──────────────────────────────────
 # anchor on ONE whole source line: a multi-line anchor made me guess the
 # continuation indent, and guessing whitespace is not a method.
 ("formula",
  '"[interest+dividends+alimony+cap gains+other+IRA+pension+rental]); L15 = L5 + L14; "',
  '"[interest+dividends+alimony+cap gains+other+IRA+pension+rental]); L15 = L5 + L14; "\n'
  '                 "WORKSHEET LINE 10 (\u2018other\u2019) = the \u00a7111 taxable state-tax refund (at the Schedule 1 "\n'
  '                 "line 1 benefit-limited amount, NEVER gross 1099-G box 2) + unemployment compensation "\n'
  '                 "(box 1 net of same-year repayment). Ken, Gate-1 direct 2026-08-30. "', 1),

 # ── 3 · the description carries the authority ranking and WHY ────────────
 ("description",
  '"The delvio-tax engine build (split_conserving going vendor-aware) is tracked there, not here.")},',
  '"The delvio-tax engine build (split_conserving going vendor-aware) is tracked there, not here. "\n'
  '                     "\u2500\u2500\u2500 WORKSHEET LINE 10 DEFINED 2026-08-30 (Ken, Gate-1 direct to the states session: "\n'
  '                     "\u201capprove the GA RIE amendment, statute primary\u201d). Line 10 \u2018Other income (losses)\u2019 "\n'
  '                     "INCLUDES the \u00a7111 taxable state-tax refund and unemployment compensation. "\n'
  '                     "AUTHORITY, RANKED ON HIS INSTRUCTION \u2014 PRIMARY: O.C.G.A. \u00a748-7-27(a)(5)(E)(i), which "\n'
  '                     "provides that retirement income \u2018shall include BUT NOT BE LIMITED TO\u2019 its enumerated "\n'
  '                     "list. That is an EXPRESS OPEN-ENDED GRANT and it does not constrain by similarity. "\n'
  '                     "SECONDARY: Ga. Comp. R. \u0026 Regs. r. 560-7-4-.02(4)(b)1, whose unearned list closes \u2018and "\n'
  '                     "other similar income\u2019. "\n'
  '                     "\u26a0\u26a0 WHY THE REG IS SECOND AND NOT FIRST, because this is the part a later reader will "\n'
  '                     "otherwise undo: (i) \u2018other SIMILAR income\u2019 invites EJUSDEM GENERIS against a list that is "\n'
  '                     "entirely INVESTMENT income (interest, dividends, rents, royalties, capital gains, "\n'
  '                     "pensions/annuities), and NEITHER ruled component is investment income \u2014 a \u00a7111 recovery "\n'
  '                     "is a recovery of a prior deduction and unemployment is wage replacement; and (ii) THE SAME "\n'
  '                     "REG SENTENCE IS PROVABLY STALE, capping earned income at $4,000 where the statute, the "\n'
  '                     "printed 2025 worksheet line 4 and this spec\u2019s GA_RIE_EARNED_CAP all say $5,000. A "\n'
  '                     "sentence wrong about its own adjacent figure is weak footing for a new inclusion. "\n'
  '                     "\u2b50 The statute reaches the same result without either problem, which is why it leads. "\n'
  '                     "\u26a0 THIS IS A JUDGEMENT INSIDE AN OPEN-ENDED STATUTE, NOT A TEXT THAT NAMES THESE ITEMS. "\n'
  '                     "No source found says \u2018state tax refund\u2019 or \u2018unemployment\u2019 is retirement income; the "\n'
  '                     "statute permits their inclusion and KEN RULED THAT THEY ARE INCLUDED. The rule says so "\n'
  '                     "plainly rather than implying the sources settle it. "\n'
  '                     "\u26a0 (3) IS A FILTER, NOT A GRANT \u2014 \u2018Only retirement income that is included in Georgia "\n'
  '                     "taxable income shall be included\u2019 fixes the AMOUNT each component enters at; it never "\n'
  '                     "admits anything. "\n'
  '                     "\u26a0 (4)(b)2 USES \u2018similar income\u2019 A SECOND TIME, TO EXCLUDE (lotteries, gambling, illegal "\n'
  '                     "sources). Never cite the phrase without saying which of the two occurrences is meant. "\n'
  '                     "\u26a0 NOT RULED, RECORDED AS AN OPEN SPEC/ENGINE GAP: the delvio-tax engine also routes "\n'
  '                     "1099-PATR patronage and 1099-MISC box 3 (both federal Schedule 1 line 8z) to this same "\n'
  '                     "worksheet line. That is engine behaviour this spec has never stated and it was NOT part of "\n'
  '                     "this ruling \u2014 flagged, not adopted.")},', 1),
]

for label, old, new, want in EDITS:
    got = s.count(old)
    assert got == want, "%s: expected %d, found %d" % (label, want, got)
    s = s.replace(old, new, want)
    print("  ok  %s" % label)

compile(s, P, "exec")          # content assertions do not imply syntactic validity
assert s.count("48-7-27(a)(5)(E)(i)") == 1
assert s.count("EJUSDEM GENERIS") == 1
io.open(P + ".new", "w", encoding="utf-8", newline="\n").write(s)
os.replace(P + ".new", P)
print("\nload_ga500_form_500.py: %d -> %d chars" % (len(s0), len(s)))
