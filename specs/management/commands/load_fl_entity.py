"""Load the FL entity specs — Florida Forms F-1120 and F-1065 (TY2025).

TWO FORMS, ONE LOADER (the load_sc_passthrough.py precedent): FL_F1120 and
FL_F1065 ride a single FORMS list because Florida's F-1065 exists ONLY to feed a
corporate partner's F-1120 — the two are one computational unit.

===========================================================================
WHAT THIS IS
===========================================================================
Florida is an ENTITY-ONLY lane: no individual income tax, no PTET, no
fiduciary return. One substantive return (F-1120, corporate income/franchise
tax at 5.5%) plus one information return (F-1065, no tax, no payment).

UNLIKE every state spec that precedes it, Florida's hardest problem is NOT
computing a return -- it is DECIDING WHETHER A RETURN EXISTS AT ALL. Most
Florida pass-throughs file nothing. A default "generate a state return because
there is a federal return" rule produces WRONG OUTPUT for the majority of
Florida entities. The FILING-OBLIGATION GATE is therefore the first-class
artifact in this spec, not an afterthought:

  * S corporation files F-1120 ONLY when federal 1120S Line 23c > 0
    (Rule 12C-1.022(1)(b)1; F-1120N p.2).
  * Partnership files F-1065 ONLY if a partner is subject to ch. 220 -- AND
    NOT if the only such partner is an S corporation (Rule 12C-1.022(6)(b)).
    An ALL-INDIVIDUAL partnership files NOTHING.
  * A foreign (out-of-state) corporate partner SEPARATELY files its own
    F-1120 (F-1120N p.1; Rule 12C-1.022(2)(e), (6)(g)) -- so ONE Florida
    partnership with ONE out-of-state corporate partner generates TWO returns.
  * Charitable trusts STILL file F-1120 for TY2025 (the ch. 2025-208
    exclusion reaches only tax years beginning on/after 1/1/2026, and the
    2025 statute text already MISLEADINGLY prints them as excluded).

The four worked examples in Rule 12C-1.022(6)(c) are shipped verbatim as
TestScenarios -- they are ready-made fixtures for the gate.

The F-1120 spine: federal taxable income -> + state income tax -> + Schedule I
(26 addition lines) -> - Schedule II (13 subtraction lines) -> adjusted federal
income -> Schedule III/IV apportionment -> $50,000 exemption -> 5.5% ->
Schedule V credits (25 lines, statutory order) -> payments.

NO prior RS spec exists (lookup/FL_F1120/export/ -> 404;
lookup/FL_F1065/export/ -> 404). NEW forms. Campaign D-9 namespacing:
FL_F1120 / FL_F1065.

===========================================================================
v1 SCOPE (from fl_entity_source_brief.md Sec.12 -- FOR KEN'S WALK)
===========================================================================
COMPUTES (v1):
  * THE FILING-OBLIGATION GATE -- file_F1120 / file_F1065 / file_nothing from
    entity type, federal form type, 1120S Line 23c, and the partner roster.
    Emits an explicit "No Florida return required" determination with reason
    and citation: a POSITIVE output, never silence.
  * F-1120 face Lines 1-19, incl. the $50,000 exemption (lesser-of,
    short-year proration x days/365, one per Sec.1563 controlled group) and
    5.5% at Line 11 ("Tax due: 5.5% of Line 10", form face, verbatim).
  * Schedule I Lines 1-6, 21-26 and Schedule II Lines 1-13.
  * THE TWO DEPRECIATION TRACKS -- they recover differently and CANNOT share
    a line: Sch I L21 -> Sch II L9 (Sec.168(k) bonus, 1/7 per year over 7
    years) and Sch I L22 -> Sch II L10 (QIP, hypothetical depreciation under
    the IRC in effect 1/1/2020 WITHOUT the CARES Act retroactive fix, and
    IGNORING any sale or disposition). The L21 addition MUST be tagged
    QIP/non-QIP at entry -- the L9 attached schedule demands the split and
    NEITHER HALF IS DERIVABLE FROM THE FEDERAL 4562.
  * Business meals (Sch I L23) and Sec.181 film/TV/theatrical
    (Sch I L24 -> Sch II L11) -- both in force for TY2025, both expire TY2026.
  * Schedule III-A/B/C apportionment: 25/25/50, six-decimal rounding,
    8 x net annual rent, original-cost property, beginning/end averaging, and
    ZERO-DENOMINATOR reweighting only (33-1/3 / 66-2/3; 50/50; 100%).
  * Schedule IV Lines 1-9 and the Schedule II <-> Schedule IV CARRYOVER FORK.
  * Florida NOL two-tier limitation (pre-2018 at 100% first, then post-2017
    at 80% of the remainder); no carryback.
  * Schedule R allocation and its L1 -> F-1120 L8 / L3 -> Sch II L7 asymmetry.
  * F-1065 Parts I-IV.
  * Due dates (the later-of test, the June-30 carve-out, F-1065's 4th-month
    date), the $2,500 estimated-tax threshold, four equal installments.

DIRECT-ENTRY (line exists, diagnostic prompts, no computation):
  * F-1120 Line 1 federal taxable income -- WITH A MANDATORY PREPARER
    CONFIRMATION that it is the PRE-OBBBA figure. Never silently recomputed.
  * F-1120 Line 2 state income taxes deducted (+ required schedule).
  * Schedule V Lines 1-24 -- all 24 credits as amount + attachment reference,
    statutory Sec.220.02(8) order PRESERVED; the L25 cap at L11 is computed.
  * Schedule I Lines 7-20 -- credit add-backs auto-populated from the
    Schedule V entries, SINGLE PASS, preparer-visible.
  * Schedule I L25 / Schedule II L12 "Other" -- the proposed landing zone for
    the TY2025 OBBBA recompute pending W1.
  * Schedule III-D insurance / transportation special fractions.
  * Nonbusiness income typing on Schedule R.
  * Line 14 penalty/interest (a-d) and Line 16a/16b payment credits.

RED-DEFERS -- EACH GETS ITS OWN DIAGNOSTIC so there is no silent gap:
  R1  Fiscal-year TY2025 straddling 1/1/2026   D_FL1120_R1_FISCAL_STRADDLE (BLOCK)
  R2  The pre-OBBBA recompute itself           D_FL1120_R2_OBBBA_RECOMPUTE (BLOCK)
  R3  Apportionment gate failure (PL 86-272)   D_FL1120_R3_APPORT_GATE
  R4  Florida AMT credit (Sch V L8)            D_FL1120_R4_AMT_CREDIT
  R5  Consolidated FL returns (F-1122/F-851)   D_FL1120_R5_CONSOLIDATED
  R6  Sec.163(j) FL-only carryforward 2019-20  D_FL1120_R6_163J_CARRYFWD
  R7  Election A / Election B depreciation     D_FL1120_R7_ELECTION_AB
  R8  Financial-organization apportionment     D_FL1120_R8_FINANCIAL_ORG
  R9  Insurance/transportation/citrus formulas D_FL1120_R9_SPECIAL_APPORT
  R10 Tiered partnership F-1065 determination  D_FL1065_R10_TIERED_PARTNERSHIP
  R11 F-1120A short form                       D_FL1120_R11_F1120A
  R12 F-1120X amended / F-2220 underpayment    D_FL1120_R12_AMENDED_F2220

===========================================================================
requires_human_review WALK ITEMS W1..W9 (Ken, before seeding)
W1 IS FIRST BECAUSE IT GATES THE LOADER.
===========================================================================
W1. *** THE TY2025 PRE-OBBBA RECOMPUTE HAS NO HOME ON THE RETURN. ***
    Settled law: Florida's TY2025 conformity date is 1/1/2025, so OBBBA
    (P.L. 119-21, 7/4/2025) is NOT adopted for TY2025 -- ch. 2026-137 moved
    conformity to 1/1/2026 but "operate[s] retroactively to January 1, 2026"
    only, and s. 220.03(3) is not self-executing ("when expressly authorized
    by law"). So F-1120 Line 1 must carry federal taxable income recomputed
    under the PRE-OBBBA Code -- and NO LINE, SCHEDULE, INSTRUCTION, TIP OR
    RULE CARRIES IT. Confirmed at RULE level: Rule 12C-1.013 ("Adjusted
    Federal Income Defined") has not been amended since 10/27/2022, and the
    TY2026 DRAFT F-1120 has no such line either.
    => This loader encodes a HARD NO-SILENT-RECOMPUTE RULE ON LINE 1
    (R-FL-L1-NOSILENT) plus a BLOCKING diagnostic (D_FL1120_R2_OBBBA_RECOMPUTE
    and D_FL1120_W1_NO_SILENT_RECALC). NO LINE WAS INVENTED. Ken must
    choose the presentation: (a) restated Line 1, (b) Sch I L25 + Sch II L12
    with an explanatory schedule (the brief's recommendation, encoded here as
    the proposed landing zone), or (c) a pro forma federal return attached.
W2. The Schedule I <-> Schedule V credit circularity. Adding back a credit
    raises Florida net income, which raises the Line 11 cap, which can admit
    more credit. BUT the circle does NOT literally close: the cap lands on
    Sch V LINE 25 only, while Sch I L7-L20 read the INDIVIDUAL Sch V lines.
    SINGLE PASS IS THE LITERALLY CORRECT READING and is encoded as the loader
    convention (see R-FL-SCHI-CREDITS notes). Ken to ratify -- the
    alternative (add back only the USED portion) yields a different Line 10.
W3. S-corp filing trigger WIDTH. Rule 12C-1.022(1)(b)1 and F-1120N key on
    federal liability / 1120S Line 23c, which carries Sec.1374 built-in gains,
    Sec.1375 excess net passive income AND LIFO RECAPTURE. But s. 220.13(2)(i)
    defines the base as Sec.1374/Sec.1375 amounts ONLY. "1374" and "1375"
    appear ZERO times on any Florida form or instruction. A LIFO-recapture-only
    S corp appears to owe a return with a ZERO BASE. Ken to rule.
W4. "INSIGNIFICANT DENOMINATOR" reweighting. s. 220.15(1) verbatim: a factor
    "has a denominator that is zero OR IS DETERMINED BY THE DEPARTMENT TO BE
    INSIGNIFICANT." INSIGNIFICANCE IS THE DEPARTMENT'S DETERMINATION, NOT THE
    PREPARER'S. This loader computes ONLY the zero-denominator branch; a
    small-but-nonzero denominator raises a diagnostic that ASKS
    (D_FL1120_INSIGNIFICANT_DEN), never a computation. Confirm.
W5. *** FISCAL TY2025 STRADDLING 1/1/2026 IS UNADDRESSED BY THE STATUTE. ***
    ch. 2026-137 s. 3(1) says the amendments "operate retroactively to
    January 1, 2026" -- it does NOT say "for tax years beginning on or after."
    A calendar TY2025 is unambiguous; FYE 6/30/2026 is not. Different answer
    => different Line 1 recompute AND a different Sec.179 limit. Encoded as a
    HARD BLOCK (R-FL-FISCAL-BLOCK / D_FL1120_R1_FISCAL_STRADDLE). Approve.
W6. F-1065 federal-return attachment conflict. F-1065N R.01/24 p.1: "Do not
    attach a copy of the federal return." Rule 12C-1.022(6)(d) (eff.1/1/2026):
    "A copy of the related U.S. Partnership Return of Income, Form 1065, must
    be attached" -- then defers to the instructions that forbid it. Both texts
    confirmed verbatim; self-referentially circular. Decide paper and MeF.
W7. THE APPORTIONMENT GATE COSTS 100%. Rule 12C-1.015(1)(d) says in terms
    "There is no throwback rule in Florida" -- but (2) taxes 100% OF ADJUSTED
    FEDERAL INCOME where the out-of-state footprint is only P.L. 86-272
    protected solicitation. That is functionally MORE ADVERSE than throwback
    and it is counter-intuitive. Confirm Delvio never auto-apportions on a
    sales-only out-of-state footprint (R-FL-APPORT-GATE + a loud RED).
W8. CHARITABLE TRUSTS FILE F-1120 FOR TY2025 while the 2025 statute already
    prints them as excluded. Confirm the TY2025 behaviour AND the TY2026 flip.
W9. Client-book scope check before authoring: (a) any FL entity client in a
    TIERED PARTNERSHIP (R10), (b) any FINANCIAL ORGANIZATION (R8), (c) whether
    any Schedule V credits actually appear. These decide how much of the
    RED-defer list is theoretical.

===========================================================================
OPEN [UNVERIFIED] ITEMS CARRIED FROM THE BRIEF -- 6 OPEN, 0 CLOSED
===========================================================================
U1. How FL DOR expects TY2025 filers to effect the pre-OBBBA recompute.
    HARDENED negative: nine OBBBA-related strings return ZERO hits across all
    six TY2025 documents; Rule 12C-1.013 unamended since 10/27/2022; no TIP
    between 2026-08-06 and 2026-08-16; the TY2026 draft form has no such line.
    -> W1. DO NOT INVENT A LINE.
U2. Which IRC applies to a FISCAL TY2025 straddling 1/1/2026. -> W5 / R1.
U3. TIERED PARTNERSHIP F-1065 obligation. Rule 12C-1.022(6) is SILENT on
    partnership partners: (6)(a) reaches only a s. 220.03(1)(z) taxpayer or a
    corporation taxed "solely by virtue of its membership in A Florida
    partnership" (singular, direct); all four (6)(c) examples involve only
    individuals and corporations; (1)(b)2 uses "directly or indirectly" for
    disregarded entities and (6) uses no such phrase anywhere. The
    expressio-unius argument rests on real drafting asymmetry BUT REMAINS AN
    ARGUMENT, NOT AUTHORITY. Do not fill the gap. -> R10 / W9.
U4. Computation order for the Sch I <-> Sch V circularity. F-1120N never
    states an order of operations; s. 220.02(8) orders only AMONG credits.
    -> W2.
U5. S-corp trigger width: 1120S Line 23c vs Sec.1374/Sec.1375. -> W3.
U6. *** F-1065 FEDERAL-RETURN ATTACH-THE-RETURN CONFLICT: F-1065N says "Do
    not attach"; Rule 12C-1.022(6)(d) says "must be attached." Both verbatim,
    both confirmed, unresolved. *** -> W6.

===========================================================================
VERIFIED-STRUCTURE PROVENANCE (READ 2026-08-16 from FINAL FL DOR PDFs fetched
live from floridarevenue.com -- NOT memory, NOT training data, NO mirrors.
Full source brief: delvio-states/research/fl_entity_source_brief.md, Status
VERIFIED, adversarial pass 2026-08-16, zero wrong line numbers found.)
===========================================================================
  F-1120        R. 01/26, Rule 12C-1.051 F.A.C., Effective 01/26, 6 pp.
                ModDate 2025-12-17T12:53:19-05:00, SHA-256[:16] 05f72e7d56949e1b
                Page-1 scanline "9100 0 20259999 0002005037 6" -> PERIOD 2025.
  F-1120N       R. 01/26, Effective 01/26, 17 pp., "for taxable years
                beginning on or after January 1, 2025"
                ModDate 2025-10-22T13:43:01-04:00, SHA-256[:16] c04cad389ea50cfa
  F-1065/1065N  R. 01/24, Effective 01/24, 6 pp.
                ModDate 2023-12-18T14:47:45-05:00, SHA-256[:16] 2c609110ddaa4473
  F-1120A       R. 01/24, TC 04/24 (R11 defer; scanline reads period 2023)
  Rule 12C-1.022  Returns; Filing Requirement -- adopted EFFECTIVE 1/1/2026,
                history "...10-2-01, 6-19-03, 8-4-05, 1-1-26" (official OLE2
                .doc from flrules.org readFile.asp; every quote re-verified)
  Rule 12C-1.015  Apportionment of Adjusted Federal Income -- EFFECTIVE
                3/18/1996 (STALE: do NOT source the 25/25/50 weights from it;
                it defers to s. 220.15(1) and carries a 1986 example)
  Rule 12C-1.013  Adjusted Federal Income Defined -- EFFECTIVE 10/27/2022,
                NOT AMENDED SINCE (the W1 negative)
  2025 Fla. Stat. ch. 220  ss. 220.02(8), 220.03, 220.11, 220.13, 220.14,
                220.15, 220.16, 220.131, 220.22, 220.807
  TIP 25C01-01  issued 12/1/2025 (TY2025 conformity; OBBBA not addressed)
  Rev. Proc. 2024-40 Sec.2.25  the PRE-OBBBA TY2025 Sec.179 figures

===========================================================================
*** TY2026 FIREWALL -- READ THIS BEFORE COPYING THIS FILE FORWARD ***
===========================================================================
THIS LOADER IS TY2025 ONLY. EVERY LINE NUMBER IN IT IS TY2025-KEYED AND MUST
NOT BE CARRIED FORWARD.

The TY2026 DRAFT F-1120 (rules/pdf/F-1120_2026.pdf, ModDate 2026-07-01,
revision block "R. XX/XX 01/26") RENUMBERS SCHEDULES I AND V:
  * a NEW "Home Away From Home Tax Credit" is inserted at Schedule I Line 15
    AND Schedule V Line 15, pushing EVERY LATER LINE DOWN ONE;
  * the business-meals line (Sch I L23) and the s. 181 film lines (Sch I L24 /
    Sch II L11) are DELETED (they expire for TYs beginning on/after 1/1/2026),
    taking Schedule I from 26 lines to 23 and Schedule II from 13 to 12;
  * the June-30 due date moves to the 5th month (per TIP 26C01-01).
Also for TY2026: conformity moves to 1/1/2026 with ss. 168(k), 174(a), 163(j),
274 and 179 pinned at 1/1/2025 and ss. 168(n) / 174A excluded entirely, plus a
MANDATORY PRO FORMA FEDERAL RETURN -- a different regime end to end.
TY2026 IS ITS OWN SPEC UNIT. A NEW TAX YEAR STALENESS-INVALIDATES EVERYTHING
HERE UNTIL RE-VERIFIED.

===========================================================================
SAFETY GUARD -- READY_TO_SEED stays False until Ken approves the review walk
(W1-W9) in-session. Until then the command refuses to write to the DB.
W1 IN PARTICULAR GATES THIS LOADER: the TY2025 OBBBA recompute has no home on
the return and no line may be invented for it.
DO NOT RELAX THE GUARD TO SILENCE THE ERROR.
===========================================================================
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import (
    AuthorityExcerpt,
    AuthorityFormLink,
    AuthoritySource,
    AuthoritySourceTopic,
    AuthorityTopic,
    RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion,
    FormDiagnostic,
    FormFact,
    FormLine,
    FormRule,
    TaxForm,
    TestScenario,
)

# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD — flip ONLY after Ken's in-session review walk (W1-W9 above).
# W1 (the TY2025 pre-OBBBA recompute has no home on the return) GATES this
# loader. Ships False.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "FL"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS (year-keyed; cited in fl_entity_source_brief.md; never memory)
# ═══════════════════════════════════════════════════════════════════════════

# s. 220.11(2)(a) "5 1/2 percent"; s. 220.1105 fixes 5.5% for TYs on/after
# 1/1/2022; F-1120 L11 face reads verbatim "Tax due: 5.5% of Line 10".
FL_TAX_RATE: dict[int, str] = {2025: "0.055"}

# s. 220.14; F-1120 L9. Lesser of $50,000 or (L7 + L8); zero floor; ONE per
# Sec.1563 controlled group; short year prorated x days / 365.
FL_EXEMPTION: dict[int, int] = {2025: 50000}
FL_SHORT_YEAR_DAYS: dict[int, int] = {2025: 365}

# s. 220.13(1)(e)1.b; F-1120N p.8 Sch II L9 — "over a seven-year period of one
# seventh of the amount of the addition, beginning with the tax year of the
# addition." QIP bonus is CARVED OUT (1.c) and recovers on Sch II L10 instead.
FL_BONUS_RECOVERY_YEARS: dict[int, int] = {2025: 7}
# s. 220.13(1)(e)1 add-back window: PIS after 12/31/2007 and before 1/1/2027.
FL_BONUS_PIS_WINDOW: dict[int, tuple] = {2025: ("2007-12-31", "2027-01-01")}
# Sch I L22 / Sch II L10 QIP track: PIS on or after 1/1/2018; the L10
# subtraction is the depreciation allowable under the IRC IN EFFECT 1/1/2020
# WITHOUT the CARES Act retroactive change, IGNORING sale or disposition.
FL_QIP_PIS_FLOOR: dict[int, str] = {2025: "2018-01-01"}
FL_QIP_HYPO_IRC_DATE: dict[int, str] = {2025: "2020-01-01"}

# s. 220.15(1) verbatim + F-1120N p.9. Florida is NOT single-sales-factor.
FL_APPORT_WEIGHTS: dict[int, dict] = {2025: {"property": 0.25, "payroll": 0.25, "sales": 0.50}}
FL_APPORT_DECIMALS: dict[int, int] = {2025: 6}
# Rented property enters the property factor at 8 x net annual rent.
FL_RENT_MULTIPLIER: dict[int, int] = {2025: 8}

# NO Florida Sec.179 add-back for TY2025 — "THE RULE SAYS NO."
# s. 220.13(1)(e)2 reaches only TYs beginning after 12/31/2007 and before
# 1/1/2015. Sec.179 enters Florida ONLY through federal taxable income at
# Line 1, at the PRE-OBBBA figure fixed by the 1/1/2025 conformity date
# (Rev. Proc. 2024-40 Sec.2.25). DO NOT encode $2,500,000 / $4,000,000.
FL_179_ADDBACK_EXISTS: dict[int, bool] = {2025: False}
FL_179_PRE_OBBBA: dict[int, dict] = {
    2025: {"limit": 1250000, "phaseout": 3130000, "suv_sublimit": 31300},
}

# Florida NOL: no carryback. Pre-1/1/2018 losses carry 20 years and offset
# 100%; post-12/31/2017 losses carry forward indefinitely and, for TYs
# beginning after 12/31/2020, offset 80% OF THE REMAINDER after the pre-2018
# carryovers are applied FIRST. Order is mandatory. (F-1120N p.4.)
FL_NOL_POST2017_PCT: dict[int, float] = {2025: 0.80}

# s. 220.03(1)(n) — "as amended and in effect on January 1, 2025."
# OBBBA (P.L. 119-21, 7/4/2025) IS NOT ADOPTED FOR TY2025.
FL_CONFORMITY_DATE: dict[int, str] = {2025: "2025-01-01"}
FL_OBBBA_ADOPTED: dict[int, bool] = {2025: False}

# F-1120N p.3 / F-1120ES. Estimated tax required if expected liability exceeds
# $2,500; four EQUAL installments (0.25 each); DO NOT ANNUALIZE.
FL_ESTIMATED_THRESHOLD: dict[int, int] = {2025: 2500}
FL_ESTIMATED_INSTALLMENTS: dict[int, int] = {2025: 4}

# The two forms have DIFFERENT due dates. F-1120: later of (1st day of the 4th
# month for JUNE 30 year ends / 5th month for all others) or (15th day
# following the unextended federal due date). F-1065: 1st day of the FOURTH
# month, ALL year ends. Calendar year: F-1120 May 1, 2026 / F-1065 April 1, 2026.
FL_F1120_DUE_MONTH_JUN30: dict[int, int] = {2025: 4}
FL_F1120_DUE_MONTH_OTHER: dict[int, int] = {2025: 5}
FL_F1065_DUE_MONTH: dict[int, int] = {2025: 4}

# Extension F-7004: 6 months (7 for a June 30 FYE), one only; VOID if the
# tentative tax is unpaid or underpaid by the GREATER of $2,000 or 30%.
FL_EXT_VOID_DOLLARS: dict[int, int] = {2025: 2000}
FL_EXT_VOID_PCT: dict[int, float] = {2025: 0.30}

# Partner kinds that are "subject to the Florida Income Tax Code" for the
# F-1065 trigger (Rule 12C-1.022(6)(a)). NOTE an S-corp partner IS subject —
# but (6)(b) excuses the filing when it is the ONLY such partner.
FL_CH220_PARTNER_KINDS = ("c_corp", "foreign_corp", "s_corp")


def _yk(d: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed lookup with a TY2025 fallback."""
    return d.get(year) if d.get(year) is not None else d[2025]


# ═══════════════════════════════════════════════════════════════════════════
# ARITHMETIC HELPERS — the executable form of the encoded rules.
# The validation harness (scratchpad/validate_fl.py) drives its oracles through
# these, so a spec change and a test change cannot silently diverge.
# ═══════════════════════════════════════════════════════════════════════════


def _fl_file_f1120_scorp(fed_1120s_line_23c) -> bool:
    """S corp files F-1120 ONLY when federal 1120S Line 23c > 0.

    Rule 12C-1.022(1)(b)1: "'S' corporations are not subject to the tax, except
    for taxable years when they are liable for the federal tax under the
    Internal Revenue Code."  F-1120N p.2: "S corporations that pay federal
    income tax on Line 23c of federal Form 1120S."

    W3: Line 23c also carries LIFO recapture tax, while s. 220.13(2)(i) names
    only Sec.1374 / Sec.1375. A LIFO-recapture-only filer trips this gate with a
    ZERO Florida base — see D_FL1120_W3_LIFO_RECAPTURE. Not resolved here.
    """
    return (fed_1120s_line_23c or 0) > 0


def _fl_file_f1065(partner_kinds, is_florida_partnership: bool = True):
    """F-1065 filing determination. Returns True / False / None.

    None = UNDETERMINED (a partnership partner => tiered structure, R10). The
    obligation for tiered structures is a true statutory/rule SILENCE; the
    software must refuse to answer rather than infer.

    Rule 12C-1.022(6)(a): "Every Florida partnership having any partner subject
    to the Florida Income Tax Code is required to make an information return...
    A partner subject to the Florida Income Tax Code includes a taxpayer, as
    defined in Section 220.03(1)(z), F.S., and any corporation subject to the
    tax solely by virtue of its membership in a Florida partnership."
    Rule 12C-1.022(6)(b): "The partnership will not be required to file a
    partnership return if the only partner subject to the Florida Income Tax
    Code is an S corporation."
    """
    if not is_florida_partnership:
        return False
    kinds = list(partner_kinds or [])
    if any(k == "partnership" for k in kinds):
        return None  # R10 — tiered; unresolved (U3). DO NOT GUESS.
    subject = [k for k in kinds if k in FL_CH220_PARTNER_KINDS]
    if not subject:
        return False  # Example 1 (AB, all individuals) — files NOTHING.
    if all(k == "s_corp" for k in subject):
        return False  # Example 4 (DE) — 12C-1.022(6)(b) carve-out.
    return True  # Examples 2 (BC) and 3 (CD).


def _fl_foreign_corp_partner_files_f1120(partner_kinds) -> bool:
    """A foreign (out-of-state) corporate partner SEPARATELY files its own F-1120.

    F-1120N p.1 / F-1065N p.1 verbatim: "A foreign (out-of-state) corporation
    that is a partner in a Florida partnership or a member of a Florida joint
    venture is subject to the Florida Income Tax Code and must file a Florida
    Corporate Income/Franchise Tax Return (Florida Form F-1120)."
    Rule 12C-1.022(6)(g): corporate members file F-1065 "as well as, Form F-1120."
    """
    return any(k == "foreign_corp" for k in (partner_kinds or []))


def _fl_bonus_recovery(vintages: dict, current_year: int, year: int = FORM_TAX_YEAR) -> float:
    """Sec.168(k) bonus recovery on Sch II L9 — 1/7 per year over SEVEN years.

    ``vintages`` maps {addition_year: NON-QIP Sch I L21 addition}. QIP bonus is
    CARVED OUT of this track (s. 220.13(1)(e)1.c) and recovers on Sch II L10
    instead — pass only the non-QIP half.

    Year N subtraction = sum over OPEN vintages of (addition_v / 7), where a
    vintage is open for the 7 years beginning WITH the year of the addition.
    """
    n = _yk(FL_BONUS_RECOVERY_YEARS, year)
    total = 0.0
    for add_year, amount in (vintages or {}).items():
        if add_year <= current_year <= add_year + n - 1:
            total += (amount or 0) / n
    return round(total, 2)


def _fl_apportionment(prop, pay, sales, year: int = FORM_TAX_YEAR):
    """Schedule III-A apportionment fraction — 25/25/50 with ZERO-denominator
    reweighting ONLY. Each argument is a (numerator, denominator) pair.

    s. 220.15(1) verbatim: "...a sales factor representing 50 percent of the
    fraction, a property factor representing 25 percent of the fraction, and a
    payroll factor representing 25 percent of the fraction. If any factor...
    has a denominator that is zero OR IS DETERMINED BY THE DEPARTMENT TO BE
    INSIGNIFICANT, the relative weights of the other factors...shall be as
    follows: (a) ...any two factors are zero or are insignificant...the
    remaining factor shall be 100 percent. (b) ...the sales factor...the
    property and payroll factors shall change from 25 percent to 50 percent...
    (c) ...either the property or payroll factor...the other shall be
    33 1/3 percent, and...the sales factor 66 2/3 percent."

    *** W4 — INSIGNIFICANCE IS THE DEPARTMENT'S DETERMINATION, NOT THE
    PREPARER'S. This function reweights ONLY on a denominator of EXACTLY ZERO.
    A small-but-nonzero denominator keeps the 25/25/50 weights and raises
    D_FL1120_INSIGNIFICANT_DEN — a question, never a computation. ***

    Returns the fraction rounded to six decimals, or None when every
    denominator is zero (no apportionment fraction exists).
    """
    dec = _yk(FL_APPORT_DECIMALS, year)
    named = (("property", prop), ("payroll", pay), ("sales", sales))
    zeros = [name for name, (_, den) in named if not den]
    if len(zeros) >= 3:
        return None
    if len(zeros) == 2:
        w = {"property": 0.0, "payroll": 0.0, "sales": 0.0}
        w[next(k for k in w if k not in zeros)] = 1.0
    elif "sales" in zeros:
        w = {"property": 0.5, "payroll": 0.5, "sales": 0.0}
    elif "property" in zeros:
        w = {"property": 0.0, "payroll": 1.0 / 3.0, "sales": 2.0 / 3.0}
    elif "payroll" in zeros:
        w = {"property": 1.0 / 3.0, "payroll": 0.0, "sales": 2.0 / 3.0}
    else:
        w = dict(_yk(FL_APPORT_WEIGHTS, year))
    factors = {name: (0.0 if not den else round(num / den, dec)) for name, (num, den) in named}
    return round(sum(w[k] * factors[k] for k in w), dec)


def _fl_property_factor(begin_fl, end_fl, begin_ew, end_ew, rent_fl=0, rent_ew=0,
                        year: int = FORM_TAX_YEAR):
    """Schedule III-B — average value of OWNED property at ORIGINAL COST (no
    accumulated depreciation), beginning/end averaged, PLUS rented property at
    8 x net annual rent. Returns (numerator, denominator) for Sch III-A L1.
    """
    mult = _yk(FL_RENT_MULTIPLIER, year)
    num = (begin_fl + end_fl) / 2.0 + mult * (rent_fl or 0)
    den = (begin_ew + end_ew) / 2.0 + mult * (rent_ew or 0)
    return (num, den)


def _fl_florida_portion(l6, doing_business_outside_fl: bool, fraction=None):
    """F-1120 Line 7. THE APPORTIONMENT GATE COSTS 100%.

    Rule 12C-1.015(1): corporations apportion "only if they are doing business
    within and without Florida."  (1)(d): "There is no throwback rule in
    Florida."  BUT (2): "If a taxpayer is not considered to be doing business
    within and without Florida under subsection (1), ALL OF ITS ADJUSTED
    FEDERAL INCOME will be subject to Florida corporate income/franchise tax."

    F-1120N p.9: "Making only sales in another state without property or
    payroll in that state does not automatically indicate a taxpayer is 'doing
    business' in a state other than Florida."  => W7 / R3.
    """
    if not doing_business_outside_fl:
        return l6  # 100% — the gate failed or was never available.
    if fraction is None:
        return None
    return round(l6 * fraction, 2)


def _fl_nol_deduction(tentative_apportioned, pre2018_carryover, post2017_carryover,
                      year: int = FORM_TAX_YEAR):
    """Florida NOL two-tier limitation (F-1120N p.4). ORDER IS MANDATORY.

    Pre-1/1/2018 carryovers apply FIRST against 100% of Florida tentative
    apportioned adjusted federal income; post-12/31/2017 carryovers then apply
    against 80% OF THE REMAINDER. No carryback, ever.
    """
    base = max(0.0, float(tentative_apportioned or 0))
    tier1 = min(float(pre2018_carryover or 0), base)
    remainder = base - tier1
    tier2 = min(float(post2017_carryover or 0), _yk(FL_NOL_POST2017_PCT, year) * remainder)
    return round(tier1 + tier2, 2)


def _fl_exemption(l7, l8, short_year_days=None, controlled_group_share=None,
                  year: int = FORM_TAX_YEAR):
    """F-1120 Line 9 — the $50,000 Florida exemption (s. 220.14).

    Lesser of $50,000 or (Line 7 + Line 8); if that sum is zero or less, ZERO.
    ONE exemption per Sec.1563 controlled group (Question G-1; attaching the
    member list "shows consent to an unequal apportionment"; absent a plan
    F-1120A states the default is division EQUALLY among filing members).
    Short year: $50,000 x (days in the short tax year / 365).
    """
    cap = float(_yk(FL_EXEMPTION, year))
    if short_year_days is not None:
        cap = round(cap * short_year_days / _yk(FL_SHORT_YEAR_DAYS, year), 2)
    if controlled_group_share is not None:
        cap = min(cap, float(controlled_group_share))
    base = (l7 or 0) + (l8 or 0)
    return 0.0 if base <= 0 else round(min(cap, base), 2)


def _fl_net_income(l7, l8, l9):
    """F-1120 Line 10 = L7 + L8 - L9; 'if a loss, enter zero.'"""
    return max(0.0, round((l7 or 0) + (l8 or 0) - (l9 or 0), 2))


def _fl_tax(l10, year: int = FORM_TAX_YEAR):
    """F-1120 Line 11 — form face verbatim: 'Tax due: 5.5% of Line 10.'"""
    return round(float(l10 or 0) * float(_yk(FL_TAX_RATE, year)), 2)


def _fl_credits_allowed(sch_v_lines_1_to_24_total, l11):
    """F-1120 Line 12 <- Schedule V Line 25.

    Form face: "sum of Lines 1 through 24 NOT TO EXCEED the amount on Page 1,
    Line 11." The cap lands on the TOTAL ONLY — Schedule I Lines 7-20 read the
    INDIVIDUAL Schedule V lines, not this capped total (W2 / C2). Credits
    cannot create a refund.
    """
    return round(min(float(sch_v_lines_1_to_24_total or 0), float(l11 or 0)), 2)


def _fl_sch_i_credit_addback(sch_v_entered: dict):
    """Schedule I Lines 7-20 — the credit add-backs, SINGLE PASS (W2).

    LOADER CONVENTION, stated explicitly because the sources do not:
    ``Sch I L7..L20 := the INDIVIDUAL Sch V line AS ENTERED``, evaluated ONCE,
    BEFORE the Line 25 cap is applied. This is the LITERALLY CORRECT reading —
    every one of Sch I L7-L20 says "Enter the amount from Line N of Schedule V,"
    and none reads from the capped Line 25 — so the circle does not close on
    the form's own arithmetic. It closes only through preparer behaviour
    (entering just the usable portion on each Schedule V line).

    Eight Schedule V credits have NO Schedule I add-back and must NOT generate
    one: L2 capital investment, L3 community contribution, L7 hazardous waste,
    L8 Florida AMT, L9 contaminated site, L10 child care, L16 Rural Community
    Investment, L23 individuals with unique abilities.
    """
    v = {k: float((sch_v_entered or {}).get(k, 0) or 0) for k in range(1, 25)}
    return {
        7: v[4],                 # enterprise zone property tax credit (F-1158Z)
        8: v[1] + v[24],         # guaranty association + FLAHIGA inside Sch V L24
        9: v[5] + v[6],          # rural + urban high-crime area job tax credits
        10: v[11],               # state housing tax credit
        11: v[12],               # FL tax credit scholarship (anti-duplication proviso)
        12: v[13],               # new worlds reading initiative
        13: v[14],               # strong families
        14: v[15],               # live local program
        15: v[17],               # new markets
        16: v[18],               # research and development
        17: v[19],               # experiential learning
        18: v[20],               # qualified railroad reconstruction/replacement
        19: v[21],               # residential graywater system
        20: v[22],               # human breast milk derived human milk fortifiers
    }


def _fl_f1065_partner_share(line_e_amount, profit_pct):
    """F-1065 Part II column (c) = column (a) x column (b).

    "Column (a) times Column (b) = partner's share of Line E. Enter here and on
    Florida Form F-1120, Schedule I (if decrease, Schedule II)."
    => increases land on F-1120 Sch I L25; decreases on Sch II L12.
    """
    return round(float(line_e_amount or 0) * float(profit_pct or 0), 2)


def _fl_f1065_factor_flowthrough(corp_fl, corp_ew, pship_fl_share, pship_ew_share):
    """F-1065N p.2 verbatim: "(corporation's Florida sales + share of
    partnership's Florida sales) / (corporation's everywhere sales + share of
    partnership's everywhere sales)" — NUMERATOR-AND-DENOMINATOR ADDITION into
    the partner's OWN factors, NOT a separate fraction.

    Rule 12C-1.015(10): a corporate partner adds its share "regardless of
    whether the partnerships are Florida partnerships."
    """
    return (corp_fl + pship_fl_share, corp_ew + pship_ew_share)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # topic_name is CharField(max_length=255) — keep these short.
    ("fl_corporate_income_tax",
     "FL corporate income/franchise tax (ch. 220): 5.5%, 25/25/50 apportionment, $50,000 exemption, "
     "static 1/1/2025 IRC conformity (OBBBA out for TY2025), the 1/7-over-7 bonus track plus the "
     "separate QIP track, and no Sec.179 add-back."),
    ("fl_filing_obligation",
     "FL filing-obligation gate — whether a Florida return exists at all: the 1120S Line 23c S-corp "
     "switch, the ch.220-partner F-1065 trigger with its S-corp carve-out, foreign corporate partners, "
     "and the TY2025 charitable-trust trap."),
]

# The FL conformity anchor lives in the GATED, UNSEEDED Tier-1 batch
# (_state_conformity_tier1.py). Expect a "NOT FOUND" warning from _load_sources
# until that batch seeds — THAT IS CORRECT BEHAVIOUR, not a defect.
# Seed order: Ken's Tier-1 Gate 1 -> FL conformity row -> these form specs.
EXISTING_SOURCES_TO_REFERENCE: list[str] = ["FL_FS_220_03_CONFORMITY"]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "FL_2025_F1120_FORM",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "FL",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Florida Corporate Income/Franchise Tax Return, Form F-1120 (R. 01/26) — TY2025",
        "citation": "Fla. Form F-1120, R. 01/26, Rule 12C-1.051 F.A.C., Effective 01/26",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://floridarevenue.com/forms_library/current/f1120.pdf",
        "current_status": "active",
        "checksum_sha256": "05f72e7d56949e1b",
        "is_substantive_authority": True,
        "is_filing_authority": True,
        "trust_score": 9.8,
        "topics": ["fl_corporate_income_tax"],
        "notes": ("READ IN FULL 2026-08-16, including a 150-dpi visual render of page 1. Page-1 scanline "
                  "'9100 0 20259999 0002005037 6' -> PERIOD 2025, confirming this is the TY2025 form. "
                  "The page-1 TEXT LAYER carries STALE TEMPLATE STRINGS ('For calendar year 2015'; 'The "
                  "payment for June 2013 is due on or before June 28, 2013' on p.6) that are NOT PRINTED "
                  "on the form — do not let an automated scrape pick up '2015'. The PDF metadata Title "
                  "says '...Return 2026'; that is the DOR revision-year label, NOT the tax year."),
        "excerpts": [
            {
                "excerpt_label": "F-1120 face Lines 1-19 (verbatim labels)",
                "excerpt_text": (
                    "Computation of Florida Net Income Tax. Lines 1-8 each carry a 'Check here if "
                    "negative' box (Florida encodes sign in a flag, not a minus sign). "
                    "1 Federal taxable income (see instructions). Attach pages 1-6 of federal return. "
                    "2 State income taxes deducted in computing federal taxable income (attach schedule). "
                    "3 Additions to federal taxable income (from Schedule I). 4 Total of Lines 1, 2, and 3. "
                    "5 Subtractions from federal taxable income (from Schedule II). 6 Adjusted federal "
                    "income (Line 4 minus Line 5). 7 Florida portion of adjusted federal income (see "
                    "instructions). 8 Nonbusiness income allocated to Florida (from Schedule R). "
                    "9 Florida exemption. 10 Florida net income (Line 7 plus Line 8 minus Line 9). "
                    "11 Tax due: 5.5% of Line 10. 12 Credits against the tax (from Schedule V). "
                    "13 Total corporate income/franchise tax due (Line 11 minus Line 12). 14 a) Penalty: "
                    "F-2220 b) Other c) Interest: F-2220 d) Other - Line 14 Total. 15 Total of Lines 13 "
                    "and 14. 16 Payment credits: Estimated tax payments 16a / Tentative tax payment 16b. "
                    "17 Total amount due: Subtract Line 16 from Line 15. 18 Credit: overpayment credited "
                    "to next year's estimated tax. 19 Refund: overpayment to be refunded here."
                ),
                "summary_text": ("F-1120 spine: FTI + state tax + Sch I - Sch II = adjusted federal income "
                                 "-> apportioned Florida portion + nonbusiness allocated - $50,000 exemption "
                                 "-> 5.5% -> Sch V credits -> penalties/interest -> payments -> due/refund."),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 11 rate and Line 19 refund trap (verbatim, form face)",
                "excerpt_text": (
                    "Line 11: 'Tax due: 5.5% of Line 10.' (F-1120A Line 6 likewise prints '5.5% of Line 5'; "
                    "the F-1120 page-6 estimated worksheet prints '5.5% of Line 3'.) "
                    "Line 19: 'If Line 19 is left blank, we will credit the entire overpayment to next "
                    "year's estimated tax.' The Line 18 election is IRREVOCABLE."
                ),
                "summary_text": "5.5% printed on the form face at Line 11; a blank Line 19 forfeits the refund to next year's estimate.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule II / Schedule IV carryover fork (printed on the form face)",
                "excerpt_text": (
                    "Printed at Schedule II: 'Taxpayers doing business outside Florida enter zero on Lines "
                    "3 through 6, and complete Schedule IV.' The four carryovers (Florida NOL, net capital "
                    "loss, excess charitable contribution, employee benefit plan contribution) live on "
                    "EITHER Schedule II Lines 3-6 OR Schedule IV Lines 4-7, NEVER BOTH. Printed at "
                    "Schedule III-A: 'If any factor in Column (b) is zero, see note on Page 9 of the "
                    "instructions.' Column (d) prints 'X 25% or ______' (property), 'X 25% or ______' "
                    "(payroll), 'X 50% or ______' (sales) — the blank records a Department determination. "
                    "Schedule V Line 25: 'sum of Lines 1 through 24 not to exceed the amount on Page 1, "
                    "Line 11.'"
                ),
                "summary_text": "The Sch II/Sch IV carryover fork, the Column(b)=0 reweighting pointer with its write-in override, and the Sch V L25 cap at L11.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_2025_F1120N_INSTR",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "FL",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Instructions for Corporate Income/Franchise Tax Return, Form F-1120N (R. 01/26) — TY2025",
        "citation": "Fla. Form F-1120N, R. 01/26, Effective 01/26 ('for taxable years beginning on or after January 1, 2025')",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://floridarevenue.com/rules/pdf/F-1120N_0725.pdf",
        "current_status": "active",
        "checksum_sha256": "c04cad389ea50cfa",
        "is_substantive_authority": True,
        "trust_score": 9.7,
        "topics": ["fl_corporate_income_tax", "fl_filing_obligation"],
        "notes": ("All 17 pages read 2026-08-16. Textually identical to forms_library/current/f1120n.pdf "
                  "(both builds compared byte-for-byte on extracted text)."),
        "excerpts": [
            {
                "excerpt_label": "Sec.168(k) bonus — addition (L21) and the 1/7-over-7 recovery (Sch II L9), verbatim",
                "excerpt_text": (
                    "Schedule I Line 21: 'Enter all amounts claimed as a special depreciation allowance "
                    "under IRC s. 168(k) for property placed in service before January 1, 2027.' "
                    "Schedule II Line 9: 'With the exception of qualified improvement property placed in "
                    "service on or after January 1, 2018, the amount required to be added back for "
                    "s.168(k), IRC, bonus depreciation is provided back to a taxpayer through a "
                    "subtraction over a seven-year period of one seventh of the amount of the addition, "
                    "beginning with the tax year of the addition. Attach a schedule showing the taxable "
                    "year and amount of the original addition, the amount of the original addition for "
                    "qualified improvement property placed in service on or after January 1, 2018, and "
                    "the amount of the subtraction by taxable year.'"
                ),
                "summary_text": ("Bonus added back 100% on Sch I L21 and recovered 1/7 per year over 7 years on "
                                 "Sch II L9; the attached schedule DEMANDS the QIP portion as a separate figure."),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "QIP — the SEPARATE PARALLEL TRACK (Sch I L22 -> Sch II L10), verbatim",
                "excerpt_text": (
                    "Schedule I Line 22: 'Enter the depreciation taken in the computation of federal "
                    "taxable income on qualified improvement property placed in service on or after "
                    "January 1, 2018. If bonus depreciation was taken on the qualified improvement "
                    "property and the bonus depreciation was included on Line 21, it should not be added "
                    "back again on this line.' "
                    "Schedule II Line 10: 'The recovery of amounts required to be added back...for "
                    "qualified improvement property placed in service on or after January 1, 2018 "
                    "(Schedule I, Line 22, and the portion related to such property added back on "
                    "Schedule I, Line 21) is provided back...on this line. The subtraction is limited to "
                    "the depreciation that would have been allowed under the IRC in effect on January 1, "
                    "2020, without retroactive changes made by the CARES Act, and without taking into "
                    "account any sale or other disposition of the property.'"
                ),
                "summary_text": ("QIP bonus rides Sch I L21, QIP regular depreciation rides Sch I L22; BOTH recover "
                                 "on Sch II L10 as HYPOTHETICAL 1/1/2020-IRC-without-CARES depreciation (QIP as "
                                 "39-year nonresidential real property), IGNORING disposition. Not a 1/7 fraction — "
                                 "a shadow depreciation book."),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Who must file — the filing matrix (pp. 1-2, verbatim list)",
                "excerpt_text": (
                    "'S corporations that pay federal income tax on Line 23c of federal Form 1120S' must "
                    "file. 'A foreign (out-of-state) corporation that is a partner in a Florida "
                    "partnership or a member of a Florida joint venture is subject to the Florida Income "
                    "Tax Code and must file a Florida Corporate Income/Franchise Tax Return (Florida Form "
                    "F-1120).' All corporations INCLUDING tax-exempt organizations doing business, "
                    "earning income, or existing in Florida file F-1120; banks and savings associations "
                    "file (ch. 220 Part VII, same 5.5% rate); LLCs classified as corporations file; LLCs "
                    "classified as partnerships with a corporate owner file F-1065 and the corporate "
                    "owner separately files F-1120; a disregarded SMLLC files no separate return but its "
                    "corporate owner reports its income 'even if the only activity of the corporation is "
                    "ownership of the single member LLC'; a homeowner/condominium association filing "
                    "federal Form 1120 files F-1120 REGARDLESS of whether any tax may be due, but one "
                    "filing federal Form 1120-H files NO Florida return; political organizations filing "
                    "1120-POL file; tax-exempt orgs with UBTI file. 'You must file a return, even if no "
                    "tax is due' — a late no-tax return still draws $50/month up to $300."
                ),
                "summary_text": "The full F-1120 filing matrix including the 1120-H no-return rule and the foreign-corporate-partner nexus trigger.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Apportionment weights, the gate, and zero-factor reweighting (p.9, verbatim)",
                "excerpt_text": (
                    "'The apportionment factors are weighted as follows: 25% to property, 25% to payroll, "
                    "and 50% to sales.' 'Florida does not allow a taxpayer to apportion income if it is "
                    "not doing business outside the state. Making only sales in another state without "
                    "property or payroll in that state does not automatically indicate a taxpayer is "
                    "\"doing business\" in a state other than Florida.' Zero-factor note: if property OR "
                    "payroll (Column b) is zero, the OTHER of those two becomes 33-1/3% and sales becomes "
                    "66-2/3%; if SALES is zero, property and payroll each become 50%; if ANY TWO factors "
                    "are zero, the remaining factor becomes 100%. 'All amounts related to nonbusiness "
                    "income, income related to ss. 78, 862, 951, and 951A, IRC, and any other income not "
                    "included in the adjusted federal income (Florida Form F-1120, Line 6) must be "
                    "excluded from the apportionment factors.'"
                ),
                "summary_text": "25/25/50; apportionment barred unless doing business outside Florida; the three zero-factor reweighting cases.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Florida NOL two-tier limitation and the $50,000 exemption mechanics",
                "excerpt_text": (
                    "NOL: no carryback, ever; carried forward 'in the same manner, to the same extent, and "
                    "for the same time periods prescribed in s. 172, IRC'; limited to the federal NOL x the "
                    "Florida apportionment fraction. Pre-1/1/2018 losses carry forward 20 years; "
                    "post-12/31/2017 losses carry forward indefinitely. For tax years beginning after "
                    "12/31/2020, PRE-2018 carryovers apply FIRST against 100% of Florida tentative "
                    "apportioned adjusted federal income, then POST-2017 carryovers apply against 80% OF "
                    "THE REMAINDER. Order is mandatory. 'If you have other Florida carryover deductions, "
                    "apply them first before applying your Florida NOLD.' "
                    "Exemption (Line 9): lesser of $50,000 or (Line 7 + Line 8); if that sum is zero or "
                    "less, enter zero. ONE $50,000 exemption per controlled group as defined in Sec.1563, "
                    "IRC. Short year: $50,000 x (days in the short tax year / 365). Question G-1: attach a "
                    "member list with FEIN, address and apportioned amount — 'Attaching the list shows "
                    "consent to an unequal apportionment of the Florida exemption.'"
                ),
                "summary_text": "Two-tier NOL (pre-2018 at 100% first, post-2017 at 80% of the remainder) and the $50,000 lesser-of exemption with controlled-group and short-year mechanics.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Sec.220.02(8) credit ordering; Schedule I anti-duplication; FICA-tip 'rule says no'",
                "excerpt_text": (
                    "'Section 220.02(8), F.S., provides for an order of application for the credits against "
                    "corporate income tax. The credits are listed in Schedule V in the order they must be "
                    "applied.' Schedule I Line 11 proviso: 'if the credit taken has previously been added "
                    "to taxable income in a prior taxable year, and is taken as a deduction for federal tax "
                    "purposes in the current taxable year, the amount of the deduction allowed shall not be "
                    "added to taxable income in the current year.' Schedule II header: 'Taxpayers may not "
                    "subtract from federal taxable income for Social Security and Medicare taxes paid on "
                    "certain employee tip income when such taxes are taken as a credit on their federal "
                    "corporate income tax return as part of the federal General Business Credit. Florida "
                    "Statutes do not provide a similar credit...nor is there a provision for a subtraction.'"
                ),
                "summary_text": "Schedule V line order IS the statutory credit-ordering rule; the L11 anti-duplication proviso; NO FICA-tip subtraction (rule says no).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Sec.163(j) filer-level with a Florida-only carryforward (p.5, verbatim)",
                "excerpt_text": (
                    "'The interest limitation under s.163(j), IRC, is computed at the filer level. Florida "
                    "did not follow the CARES Act's temporary increase in the interest limitation from 30% "
                    "to 50%...for taxable years beginning on or after January 1, 2019, and before January "
                    "1, 2021. Any addition(s) required on Florida returns for taxable years 2019-2020 "
                    "because of this decoupling is treated as a disallowed business interest expense "
                    "carryforward from prior years for purposes of computing the subsequent year's "
                    "business interest expense.'"
                ),
                "summary_text": "A Florida-only Sec.163(j) disallowed-interest carryforward from TY2019-2020 can still be live in TY2025 (R6).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 1 federal handoff and the required attachments (pp. 3, 5)",
                "excerpt_text": (
                    "Line 1 = 'the amount shown on Line 30 of federal Form 1120' or the corresponding "
                    "taxable-income line of the related federal return. S corporations 'should enter only "
                    "the amount of income subject to federal income tax at the corporate level.' A "
                    "separate Florida filer inside a federal consolidated group computes federal taxable "
                    "income as if it had filed a separate federal return and attaches the consolidated "
                    "return, a reconciliation statement, and a pro forma federal return. "
                    "'Attach a copy of the actual federal income tax return filed with the IRS...You must "
                    "also attach copies of federal Forms 4562, 851 (or Florida Form F-851), 1122, 1125-A, "
                    "Schedule D, Schedule M-3, and any supporting details for Schedules M-1 and M-2.' "
                    "A return without the federal return attached is INCOMPLETE: penalty the greater of "
                    "$300 or 10% of tax finally determined due, capped at $10,000."
                ),
                "summary_text": "Line 1 <- federal 1120 Line 30 AS FILED; S corps enter only the corporate-level taxed income; the federal return and Form 4562 are mandatory attachments.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Due dates, extension voiding, estimated tax (pp. 2-3)",
                "excerpt_text": (
                    "F-1120 is due the LATER OF: (1) 'For tax years ending June 30, the due date is on or "
                    "before the first day of the fourth month...For all other tax year endings, the due "
                    "date is on or before the first day of the fifth month following the close of the tax "
                    "year. For example, for a taxpayer with a tax year that ends December 31, 2025, the "
                    "Florida Form F-1120 is due on or before May 1, 2026'; or (2) 'the 15th day following "
                    "the due date, without extension, for the filing of the related federal return.' "
                    "Extension: F-7004 only — 'A copy of your federal extension alone will not extend the "
                    "time for filing your Florida return.' Six months (seven for a June 30 year end), one "
                    "only. An extension is VOID if '1) Your tentative tax due is not paid. 2) You underpay "
                    "your tax by the greater of $2,000 or 30% of the tax shown on Florida Form F-1120 when "
                    "filed.' Estimated tax required if liability is expected to exceed $2,500; FOUR EQUAL "
                    "installments, DO NOT ANNUALIZE; calendar-year due dates May 31, June 30, September "
                    "30, December 31; underpayment penalty 12%/yr on F-2220."
                ),
                "summary_text": "F-1120 later-of due date with a June-30 carve-out; F-7004 required and VOID on underpayment by the greater of $2,000 or 30%; $2,500 estimated-tax threshold, four equal installments.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_2024_F1065_FORM",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "FL",
        "title": "Florida Partnership Information Return, Form F-1065 + Instructions F-1065N (R. 01/24)",
        "citation": "Fla. Form F-1065 / F-1065N, R. 01/24, Effective 01/24",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://floridarevenue.com/forms_library/current/f1065.pdf",
        "current_status": "active",
        "checksum_sha256": "2c609110ddaa4473",
        "is_substantive_authority": True,
        "is_filing_authority": True,
        "trust_score": 9.6,
        "topics": ["fl_filing_obligation", "fl_corporate_income_tax"],
        "notes": "Year-neutral form; OPERATIVE FOR TY2025. All 6 pages read 2026-08-16.",
        "excerpts": [
            {
                "excerpt_label": "Who must file F-1065 (F-1065N p.1, verbatim)",
                "excerpt_text": (
                    "'Every Florida partnership having any partner subject to the Florida Corporate Income "
                    "Tax Code must file Florida Form F-1065. A limited liability company with a corporate "
                    "partner, if classified as a partnership for federal tax purposes, must also file "
                    "Florida Form F-1065. A Florida partnership is a partnership doing business, earning "
                    "income, or existing in Florida.' "
                    "Attachments and Statements: 'Do not attach a copy of the federal return.' "
                    "'An original signature is required. We will not accept a photocopy, facsimile, or "
                    "stamp.' 'If the partnership ceases to exist, write \"FINAL RETURN\" at the top of the "
                    "form.'"
                ),
                "summary_text": "F-1065 required only where a partner is subject to ch. 220; F-1065N FORBIDS attaching the federal return (conflicts with Rule 12C-1.022(6)(d) — W6).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F-1065 Parts I-IV structure (verbatim labels)",
                "excerpt_text": (
                    "Part I Florida Adjustment to Partnership Income: A.1 Federal tax-exempt interest "
                    "(total interest excluded from federal ordinary income LESS associated expenses not "
                    "deductible) = Net Interest; A.2 State income taxes deducted in computing federal "
                    "ordinary income (exclude taxes based on gross receipts or revenues); A.3 Other "
                    "additions; A Total; B Subtractions from federal income ('For example, s. 220.13(1)(e), "
                    "F.S., provides for a subtraction taken equally over a seven year period corresponding "
                    "to the add back...for the special bonus depreciation'); C Subtotal (Line A less Line "
                    "B); D Net adjustment from other partnerships or joint ventures (attach a schedule); "
                    "E.1 Partnership income adjustment - Increase (total of Lines C and D); E.2 - Decrease. "
                    "Part II Distribution of Partnership Income Adjustment, per partner: (a) Amount shown "
                    "on Line E, Part I; (b) Partner's percentage of profits; (c) 'Column (a) times Column "
                    "(b) = partner's share of Line E. Enter here and on Florida Form F-1120, Schedule I "
                    "(if decrease, Schedule II).' Printed note: 'If there is no adjustment on Line E, show "
                    "partner's percentage of profits in Column (b) and leave Columns (a) and (c) blank.' "
                    "Part III-A (within and without Florida): 1 Average value of property per Schedule "
                    "III-C (Line 8); 2 Salaries, wages, commissions and other compensation paid or "
                    "accrued; 3 Sales. Part III-B transportation revenue miles. Part III-C average value "
                    "of property (8 times net annual rent). Part IV Apportionment of Partners' Share, by "
                    "percent of interest, paired Within-Florida / Everywhere columns for Property, Payroll "
                    "and Sales data. Printed: 'NOTE: Transfer data to Schedule III-A, Florida Form F-1120.'"
                ),
                "summary_text": "Part I computes the Florida partnership income adjustment; Part II distributes it (a x b = c); Parts III/IV distribute the apportionment factor data to corporate partners.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Partner factor flow-through formula (F-1065N p.2, verbatim)",
                "excerpt_text": (
                    "'(corporation's Florida sales + share of partnership's Florida sales) / "
                    "(corporation's everywhere sales + share of partnership's everywhere sales)' "
                    "F-1065 is due the FIRST DAY OF THE FOURTH MONTH following the close of the taxable "
                    "year — NOT the fifth. Extension via F-7004, six months, one only. F-1065 may be filed "
                    "through the IRS Modernized e-File (MeF) Program."
                ),
                "summary_text": "NUMERATOR-AND-DENOMINATOR ADDITION into the corporate partner's own factors, not a separate fraction; F-1065 due the 4th month (F-1120 the 5th).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_RULE_12C_1_022",
        "source_type": "state_regulation",
        "source_rank": "controlling",
        "jurisdiction_code": "FL",
        "title": "Fla. Admin. Code r. 12C-1.022 — Returns; Filing Requirement",
        "citation": "Fla. Admin. Code r. 12C-1.022 (eff. 1/1/2026); hist. ...10-2-01, 6-19-03, 8-4-05, 1-1-26",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://www.flrules.org/gateway/readFile.asp?sid=0&tid=30312129&type=1&file=12C-1.022.doc",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["fl_filing_obligation"],
        "notes": ("Obtained 2026-08-16 as the official OLE2 .doc from flrules.org readFile.asp (no mirrors); "
                  "every quotation re-verified by regex against the extracted text. RULE-STALENESS ARTIFACTS "
                  "PRESENT AND MUST NOT BE BUILT: (1)(b)1 still recites the legacy title 'Florida Corporate "
                  "Income/Franchise and Emergency Excise Tax Return' (the emergency excise tax is DEAD); "
                  "(5) still requires a 'Florida alternative minimum tax schedule' (there is NO Florida AMT "
                  "for TYs beginning on/after 1/1/2018 and no such schedule on F-1120 R. 01/26). "
                  "The charitable-trust exclusion in this adopted text is EFFECTIVE 1/1/2026 — NOT TY2025."),
        "excerpts": [
            {
                "excerpt_label": "(1)(a) no general exception; (1)(b)1 S corps; (1)(b)2 SMLLC/QSub — verbatim",
                "excerpt_text": (
                    "(1)(a): 'The Florida Income Tax Code does not specifically provide for an exception "
                    "from the filing requirements for any organization, association, or legal entity...It "
                    "is the burden of a corporation that is existing in Florida or incorporated under the "
                    "Laws of Florida to establish that it is not required to file a federal corporate "
                    "income tax return and, therefore, does not have a Florida filing requirement.' "
                    "(1)(b)1: '\"S\" corporations are not subject to the tax, except for taxable years when "
                    "they are liable for the federal tax under the Internal Revenue Code. An \"S\" "
                    "corporation must file a Florida Corporate Income/Franchise and Emergency Excise Tax "
                    "Return (Form F-1120...) for taxable years when it is liable for federal tax under the "
                    "Internal Revenue Code.' "
                    "(1)(b)2 extends the disregarded-SMLLC treatment to a qualified subchapter S "
                    "corporation, using the phrase 'directly or indirectly'."
                ),
                "summary_text": "The default is hard the OTHER way — the burden is on the corporation to establish it need not file. S corps file only when liable for federal tax.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "(6)(a)-(b) the F-1065 trigger and the S-CORP-PARTNER CARVE-OUT — verbatim",
                "excerpt_text": (
                    "(6)(a): 'Every Florida partnership having any partner subject to the Florida Income "
                    "Tax Code is required to make an information return...A partner subject to the Florida "
                    "Income Tax Code includes a taxpayer, as defined in Section 220.03(1)(z), F.S., and "
                    "any corporation subject to the tax solely by virtue of its membership in a Florida "
                    "partnership.' "
                    "(6)(b): 'The partnership will not be required to file a partnership return if the "
                    "only partner subject to the Florida Income Tax Code is an S corporation.'"
                ),
                "summary_text": "The F-1065 trigger AND the S-corp-partner carve-out that excuses filing when the only ch.220 partner is an S corporation.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "(6)(c) THE FOUR WORKED EXAMPLES — verbatim, shipped as TestScenarios",
                "excerpt_text": (
                    "Example 1: Partnership AB has three partners, all individuals. AB is NOT required to "
                    "file a Florida partnership information return because it has no corporate partners. "
                    "Example 2: Partnership BC has two individual partners and Corporation X, which is "
                    "subject to the Florida Income Tax Code. BC IS required to file. "
                    "Example 3: Partnership CD has two individual partners and Corporation Y, a New York "
                    "corporation which does no business in Florida. CD IS required to file because "
                    "Corporation Y is subject to the Florida Income Tax Code SOLELY BY VIRTUE OF ITS "
                    "MEMBERSHIP in the Florida Partnership, CD. "
                    "Example 4: Partnership DE has two individual partners and Corporation Z, an 'S' "
                    "Corporation. DE is NOT required to file."
                ),
                "summary_text": "AB no / BC yes / CD yes (solely by virtue of membership) / DE no — the cleanest possible fixtures for the F-1065 gate.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "(2)(e), (6)(d), (6)(f), (6)(g) — attachments, dual filing, worksheet mode",
                "excerpt_text": (
                    "(2)(e): a foreign corporate partner '...must file Form F-1120. A copy of the federal "
                    "Schedule K-1 (Form 1065) should also be attached.' "
                    "(6)(d): 'A copy of the related U.S. Partnership Return of Income, Form 1065, must be "
                    "attached. The instructions for Form F-1065 prescribe the attachments required...' "
                    "— which CONFLICTS with F-1065N's 'Do not attach a copy of the federal return' and "
                    "then defers back to those very instructions. SELF-REFERENTIALLY CIRCULAR (W6). "
                    "(6)(f): a corporation filing F-1120 MAY use F-1065 to report its distributive share "
                    "of income adjustments and factors from a partnership that is NOT a Florida "
                    "partnership (rule example: an Ohio partnership doing no business in Florida) — i.e. "
                    "F-1065 has a NON-FILING, WORKSHEET-ONLY MODE. "
                    "(6)(g): 'Corporations who are members of a Florida partnership or joint venture must "
                    "file Form F-1065...as well as, Form F-1120.'"
                ),
                "summary_text": "The K-1 attachment for foreign corporate partners, the unresolved attach-the-federal-return conflict (W6), the worksheet-only mode, and the dual-filing requirement.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_RULE_12C_1_015",
        "source_type": "state_regulation",
        "source_rank": "controlling",
        "jurisdiction_code": "FL",
        "title": "Fla. Admin. Code r. 12C-1.015 — Apportionment of Adjusted Federal Income",
        "citation": "Fla. Admin. Code r. 12C-1.015 (eff. 3/18/1996); hist. ...5-17-94, 3-18-96",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://www.flrules.org/gateway/readFile.asp?sid=0&tid=1292833&type=1&file=12C-1.015.doc",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.0,
        "topics": ["fl_corporate_income_tax"],
        "notes": ("STALE — last amended 3/18/1996; its worked example carries a 1986 fact pattern and it "
                  "expressly defers to s. 220.15(1). DO NOT SOURCE THE 25/25/50 FACTOR WEIGHTS FROM THIS "
                  "RULE; take them from s. 220.15(1) and F-1120N R. 01/26, which agree. The rule IS the "
                  "authority for the apportionment GATE."),
        "excerpts": [
            {
                "excerpt_label": "(1)-(2) THE GATE: no throwback, but a gate failure costs 100% — verbatim",
                "excerpt_text": (
                    "(1): '...corporations will apportion their adjusted federal income in accordance with "
                    "Section 220.15, F.S., only if they are doing business within and without Florida...' "
                    "(1)(a): a taxpayer is doing business without this state if it is taxable in another "
                    "state, provided 1. that state subjects the business to a net income tax, a franchise "
                    "tax measured by net income, a franchise tax for the privilege of doing business, or a "
                    "corporate stock tax, or 2. that state HAS JURISDICTION to subject the taxpayer to a "
                    "net income tax regardless of whether, in fact, the state does or does not. "
                    "(1)(b)1: 'corporations that have incorporated outside Florida may apportion income in "
                    "accordance with Section 220.15, F.S.' (1)(b)3-5: P.L. 86-272 and de minimis "
                    "exceptions; '5. If no other state may tax a Florida corporation because of "
                    "jurisdictional limitations due to the due process or commerce clauses, Public Law "
                    "86-272, or de minimis exceptions, the corporation will not be considered to be doing "
                    "business within and without Florida.' (1)(b)7: voluntary filing in another state is "
                    "'not...conclusive proof that the state had jurisdiction.' "
                    "(1)(c): 'The denominators of the factors are not limited to only including the "
                    "property, payroll, and sales in states which actually tax or have the jurisdiction to "
                    "tax.' "
                    "(1)(d): 'THERE IS NO THROWBACK RULE IN FLORIDA. For a corporation that is doing "
                    "business within and without Florida, the sales are not considered to be Florida sales "
                    "solely because the corporation is not subject to tax within another state.' "
                    "(2): 'If a taxpayer is not considered to be doing business within and without Florida "
                    "under subsection (1), ALL OF ITS ADJUSTED FEDERAL INCOME WILL BE SUBJECT TO FLORIDA "
                    "CORPORATE INCOME/FRANCHISE TAX.' "
                    "(7)(b): consolidated groups are tested GROUPWIDE — 'the members will be considered as "
                    "one \"person.\"' "
                    "(10): 'The amounts of the property, payroll, and sales of a partnership are "
                    "attributable to the partners...A corporation that is a partner in a partnership must "
                    "add its share of the property, payroll, and sales to its own apportionment factors, "
                    "regardless of whether the partnerships are Florida partnerships.'"
                ),
                "summary_text": ("EXPRESS no-throwback provision AND a gate that, when failed, taxes 100% of "
                                 "adjusted federal income — functionally MORE ADVERSE than throwback. A "
                                 "non-Florida state of incorporation clears the gate on its own."),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_FS_CH220_2025",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "FL",
        "tax_year_start": 2025,
        "title": "2025 Fla. Stat. ch. 220 — Florida Income Tax Code (rate, base, exemption, apportionment, returns)",
        "citation": "2025 Fla. Stat. ss. 220.02(8), 220.03, 220.11, 220.1105, 220.13, 220.14, 220.15, 220.16, 220.131, 220.22, 220.807",
        "issuer": "Florida Legislature",
        "official_url": "https://www.flsenate.gov/Laws/Statutes/2025/Chapter220/All",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["fl_corporate_income_tax", "fl_filing_obligation"],
        "excerpts": [
            {
                "excerpt_label": "s. 220.15(1) apportionment weights and the INSIGNIFICANCE trigger — verbatim",
                "excerpt_text": (
                    "'...by multiplying it by an apportionment fraction composed of a sales factor "
                    "representing 50 percent of the fraction, a property factor representing 25 percent of "
                    "the fraction, and a payroll factor representing 25 percent of the fraction. If any "
                    "factor described in subsection (2), subsection (4), or subsection (5) has a "
                    "denominator that is zero OR IS DETERMINED BY THE DEPARTMENT TO BE INSIGNIFICANT, the "
                    "relative weights of the other factors...shall be as follows: (a) If the denominators "
                    "for any two factors are zero or are insignificant, the weighted percentage for the "
                    "remaining factor shall be 100 percent. (b) If the denominator for the sales factor is "
                    "zero or is insignificant, the weighted percentage for the property and payroll "
                    "factors shall change from 25 percent to 50 percent, respectively. (c) If the "
                    "denominator for either the property or payroll factor is zero or is insignificant, "
                    "the weighted percentage for the other shall be 33 1/3 percent, and the weighted "
                    "percentage for the sales factor shall be 66 2/3 percent.'"
                ),
                "summary_text": ("25/25/50 confirmed IN THE STATUTE. INSIGNIFICANCE IS EXPRESSLY THE DEPARTMENT'S "
                                 "DETERMINATION — not a preparer election and not self-executing. The software "
                                 "computes ONLY the zero-denominator branch (W4)."),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "s. 220.22 returns; filing requirement — verbatim (1)-(4)",
                "excerpt_text": (
                    "'(1) A return with respect to the tax imposed by this code shall be made by every "
                    "taxpayer for each taxable year in which such taxpayer either is liable for tax under "
                    "this code or is required to make a federal income tax return, regardless of whether "
                    "such taxpayer is liable for tax under this code.' "
                    "'(2) Every Florida partnership having any partner subject to tax under this code, "
                    "shall make an information return setting forth: (a) All items of income, gain, loss, "
                    "and deduction; (b) The names and addresses of all partners subject to tax hereunder "
                    "who would be entitled to share in the net income of the partnership if distributed; "
                    "(c) The amount and proportion of the distributive share of each partner-taxpayer; and "
                    "(d) Such other pertinent information as the department may by form or regulation "
                    "prescribe.' "
                    "'(3) Whenever a receiver, trustee in bankruptcy, or assignee, by order of law or "
                    "otherwise, has possession of or holds title to all or substantially all of the "
                    "property or business of a taxpayer...such receiver, trustee, or assignee shall make "
                    "the returns and notices required of such taxpayer.' "
                    "'(4) The department shall designate by rule certain not-for-profit entities and "
                    "others that are not required to file a return under this code, including an initial "
                    "information return, unless the entities have taxable income as defined in s. "
                    "220.13(2). These entities shall include subchapter S corporations, tax-exempt "
                    "entities, and others that do not usually owe federal income tax.'"
                ),
                "summary_text": ("The S-corp and partnership non-filing outcomes are RULE-BASED EXCEPTIONS under "
                                 "s. 220.22(4), not statutory vacuums — and exceptions have edges."),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "s. 220.13(1)(e) depreciation add-backs; s. 220.13(2)(i) S-corp base; rate and exemption",
                "excerpt_text": (
                    "s. 220.13(1)(e)1: the Sec.168(k) bonus add-back for property placed in service after "
                    "December 31, 2007, and before January 1, 2027; 1.b supplies the one-seventh recovery "
                    "'notwithstanding any sale or other disposition'; 1.c CARVES QIP BONUS OUT of that "
                    "track (the statutory basis for the separate Sch II L10 track). "
                    "s. 220.13(1)(e)2 (the Sec.179 add-back) reaches only 'an amount equal to 100 percent "
                    "of any amount in excess of $128,000 deducted for federal income tax purposes for the "
                    "taxable year pursuant to s. 179...for taxable years beginning after December 31, "
                    "2007, and before January 1, 2015' — TY2025 IS OUTSIDE THE WINDOW BY ITS OWN TERMS. "
                    "s. 220.13(2)(i): an S corporation's Florida taxable income 'means the amounts subject "
                    "to tax under s. 1374 or s. 1375 of the Internal Revenue Code for each taxable year.' "
                    "s. 220.11(2)(a): 'an amount equal to 5 1/2 percent of the taxpayer's net income for "
                    "the taxable year'; s. 220.1105 repeals the rate-adjustment mechanism and fixes 5.5% "
                    "for tax years beginning on or after January 1, 2022. "
                    "s. 220.14: the $50,000 exemption. s. 220.02(8): the order of application of credits. "
                    "s. 220.16: nonbusiness income is ALLOCATED, not apportioned."
                ),
                "summary_text": ("The bonus add-back with its 1/7 recovery and QIP carve-out; the Sec.179 add-back "
                                 "EXPIRED after TY2014 (rule says no); the S-corp base is Sec.1374/Sec.1375 only "
                                 "(W3); 5.5%; $50,000; statutory credit ordering."),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_TIP_25C01_01",
        "source_type": "state_conformity_notice",
        "source_rank": "primary_official",
        "jurisdiction_code": "FL",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "TIP 25C01-01 — Florida Corporate Income Tax: Adoption of the 2025 Internal Revenue Code",
        "citation": "FL DOR TIP 25C01-01, issued 12/1/2025",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://floridarevenue.com/taxes/tips/Documents/TIP_25C01-01.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["fl_corporate_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "OBBBA is NOT adopted for TY2025 — DOR's own boxed notice, verbatim",
                "excerpt_text": (
                    "'The new law discussed below does not address the One Big Beautiful Bill Act (Public "
                    "Law 119-21), which was enacted after the 2025 Florida legislative session ended. The "
                    "Florida Legislature will have the opportunity to consider the One Big Beautiful Bill "
                    "Act amendments to the Internal Revenue Code, including the federal treatment of bonus "
                    "depreciation, during its next regular legislative session, which is scheduled to "
                    "begin in January 2026.' "
                    "The TIP also states that charitable trusts 'will no longer be required to file a "
                    "Florida Corporate Income/Franchise Tax Return (Form F-1120) starting with tax year "
                    "2026' — i.e. THEY DO FILE FOR TY2025."
                ),
                "summary_text": ("OBBBA is entirely out for TY2025 and DOR gives NO filing mechanics for the "
                                 "resulting pre-OBBBA recompute (W1). Charitable trusts still file for TY2025 (W8)."),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "FL_RULE_12C_1_013_NEG",
        "source_type": "state_regulation",
        "source_rank": "reference_only",
        "jurisdiction_code": "FL",
        "title": "Fla. Admin. Code r. 12C-1.013 — Adjusted Federal Income Defined (NEGATIVE FINDING for W1)",
        "citation": "Fla. Admin. Code r. 12C-1.013, Effective 10/27/2022; hist. ...1-10-17, 1-8-19, 12-12-19, 10-27-22",
        "issuer": "Florida Department of Revenue",
        "official_url": "https://www.flrules.org/gateway/ruleNo.asp?id=12C-1.013",
        "current_status": "active",
        "is_substantive_authority": False,
        "trust_score": 9.0,
        "topics": ["fl_corporate_income_tax"],
        "notes": "Docket metadata verified 2026-08-16. Cited HERE ONLY as the negative that hardens W1.",
        "excerpts": [
            {
                "excerpt_label": "THE W1 NEGATIVE — the recompute has no home, confirmed at rule level",
                "excerpt_text": (
                    "Rule 12C-1.013 is the rule that would carry any TY2025 pre-OBBBA recompute mechanics. "
                    "Its latest adopted version is EFFECTIVE 10/27/2022 and it HAS NOT BEEN AMENDED SINCE. "
                    "No emergency rule, no proposed amendment, and nothing under the ch. 2026-137 s. 3(3) "
                    "emergency-rule authority touches it. Exhaustive search of the complete TY2025 forms "
                    "package (F-1120, F-1120N, F-1065/F-1065N, F-1120A, F-1120ES, F-7004) for OBBBA, "
                    "119-21, P.L. 119, One Big Beautiful, recompute, recomputed, 174A, 168(n), pro forma "
                    "and proforma returned ZERO relevant hits — the only two 'pro forma' hits are the "
                    "consolidated-subsidiary attachment (F-1120N p.5) and the capital-investment-credit "
                    "attachment (p.12), NEITHER an OBBBA recompute. The TY2026 DRAFT F-1120 carries no "
                    "such line either. NO LINE MAY BE INVENTED FOR THIS."
                ),
                "summary_text": "The TY2025 pre-OBBBA recompute has NO home on the return — confirmed at form, instruction, TIP and RULE level. W1 gates the loader.",
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("FL_2025_F1120_FORM", "FL_F1120", "governs"),
    ("FL_2025_F1120N_INSTR", "FL_F1120", "governs"),
    ("FL_FS_CH220_2025", "FL_F1120", "governs"),
    ("FL_RULE_12C_1_022", "FL_F1120", "governs"),
    ("FL_RULE_12C_1_015", "FL_F1120", "governs"),
    ("FL_TIP_25C01_01", "FL_F1120", "informs"),
    ("FL_RULE_12C_1_013_NEG", "FL_F1120", "informs"),
    ("FL_FS_220_03_CONFORMITY", "FL_F1120", "governs"),
    ("FL_2024_F1065_FORM", "FL_F1065", "governs"),
    ("FL_RULE_12C_1_022", "FL_F1065", "governs"),
    ("FL_RULE_12C_1_015", "FL_F1065", "governs"),
    ("FL_FS_CH220_2025", "FL_F1065", "governs"),
    ("FL_FS_220_03_CONFORMITY", "FL_F1065", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM 1 — FL_F1120 (Florida Corporate Income/Franchise Tax Return, TY2025)
#
# entity_types ["1120", "1120S"]: F-1120 covers C corporations AND the S
# corporations that must file it (federal 1120S Line 23c > 0).
# ═══════════════════════════════════════════════════════════════════════════

# ── Schedule I — Additions (26 lines). (line, verbatim label, fact_key or None)
# Lines 7-20 are COMPUTED from the Schedule V entries (single pass, W2), so no fact.
SCHI_LABELS: list[tuple[int, str, str | None]] = [
    (1, "Interest excluded from federal taxable income (see instructions)", "schi_l1_interest_excluded"),
    (2, "Undistributed net long-term capital gains (see instructions)", "schi_l2_undistributed_ltcg"),
    (3, "Net operating loss deduction (attach schedule)", "schi_l3_fed_nol_deduction"),
    (4, "Net capital loss carryover (attach schedule)", "schi_l4_net_capital_loss_co"),
    (5, "Excess charitable contribution carryover (attach schedule)", "schi_l5_excess_charitable_co"),
    (6, "Employee benefit plan contribution carryover (attach schedule)", "schi_l6_emp_benefit_plan_co"),
    (7, "Ad valorem taxes allowable as an enterprise zone property tax credit (Florida Form F-1158Z)", None),
    (8, "Guaranty association assessment(s) credit", None),
    (9, "Rural and/or urban high-crime area job tax credits", None),
    (10, "State housing tax credit", None),
    (11, "Florida tax credit scholarship program credit (contributions to nonprofit scholarship-funding organizations)", None),
    (12, "New worlds reading initiative credit", None),
    (13, "Strong families tax credit (contributions to eligible charitable organizations)", None),
    (14, "Live Local program credit", None),
    (15, "New markets tax credit", None),
    (16, "Research and development tax credit", None),
    (17, "Experiential learning tax credit program", None),
    (18, "Credit for qualified railroad reconstruction or replacement expenditures", None),
    (19, "Residential graywater system tax credit", None),
    (20, "Credit for manufacturing of human breast milk derived human milk fortifiers", None),
    (21, "s.168(k), IRC, special bonus depreciation", "schi_l21_bonus_depreciation"),
    (22, "Depreciation of qualified improvement property (see instructions)", "schi_l22_qip_depreciation"),
    (23, "Expenses for business meals provided by a restaurant (see instructions)", "schi_l23_business_meals"),
    (24, "Film, television, and live theatrical production expenses (see instructions)", "schi_l24_film_181"),
    (25, "Other additions (attach schedule)", "schi_l25_other_additions"),
    (26, "Total Lines 1 through 25. Enter total on this line and on Page 1, Line 3.", None),
]

# Sch I L7-L20 <- the INDIVIDUAL Sch V lines (F-1120N pp. 6-7, verified line-for-line).
SCHI_CREDIT_ADDBACK_MAP: dict[int, str] = {
    7: "Sch V L4", 8: "Sch V L1 + FLAHIGA inside Sch V L24", 9: "Sch V L5 + Sch V L6",
    10: "Sch V L11", 11: "Sch V L12", 12: "Sch V L13", 13: "Sch V L14", 14: "Sch V L15",
    15: "Sch V L17", 16: "Sch V L18", 17: "Sch V L19", 18: "Sch V L20", 19: "Sch V L21",
    20: "Sch V L22",
}
# Sch V credits with NO Sch I add-back — do NOT generate one for these.
SCHV_NO_ADDBACK: tuple = (2, 3, 7, 8, 9, 10, 16, 23)
# Reverse view: Schedule V line -> the Schedule I line that adds it back.
SCHV_TO_SCHI: dict[int, int] = {
    1: 8, 4: 7, 5: 9, 6: 9, 11: 10, 12: 11, 13: 12, 14: 13, 15: 14,
    17: 15, 18: 16, 19: 17, 20: 18, 21: 19, 22: 20, 24: 8,
}

# ── Schedule II — Subtractions (13 lines).
SCHII_LABELS: list[tuple[int, str, str | None]] = [
    (1, "Gross foreign source income less attributable expenses ((a) s. 78, IRC, income (b) plus s. 862, IRC, dividends (c) plus s. 951A, IRC, income (d) less direct and indirect expenses and related amounts deducted under s. 250, IRC)", "schii_l1_foreign_source_net"),
    (2, "Gross subpart F income less attributable expenses ((a) s. 951, IRC, subpart F income (b) less direct and indirect expenses)", "schii_l2_subpart_f_net"),
    (3, "Florida net operating loss carryover deduction (see instructions)", "schii_l3_fl_nol_deduction"),
    (4, "Florida net capital loss carryover deduction (see instructions)", "schii_l4_fl_capital_loss_co"),
    (5, "Florida excess charitable contribution carryover (see instructions)", "schii_l5_fl_excess_charit_co"),
    (6, "Florida employee benefit plan contribution carryover (see instructions)", "schii_l6_fl_emp_benefit_co"),
    (7, "Nonbusiness income (from Schedule R, Line 3)", None),
    (8, "Eligible net income of an international banking facility (see instructions)", "schii_l8_ibf_net_income"),
    (9, "s. 168(k), IRC, special bonus depreciation (see instructions)", None),
    (10, "Depreciation of qualified improvement property (see instructions)", "schii_l10_qip_recovery"),
    (11, "Film, television, and live theatrical production expenses (see instructions)", "schii_l11_film_181_recovery"),
    (12, "Other subtractions (attach schedule)", "schii_l12_other_subtractions"),
    (13, "Total Lines 1 through 12. Enter total on this line and on Page 1, Line 5.", None),
]

# ── Schedule V — Credits (25 lines), IN THE STATUTORY s. 220.02(8) ORDER.
SCHV_LABELS: list[tuple[int, str, str | None]] = [
    (1, "Florida health maintenance organization consumer assistance assessment credit [assessment notice]", "schv_l01_hmo_assessment"),
    (2, "Capital investment tax credit [certification letter]", "schv_l02_capital_investment"),
    (3, "Community contribution tax credit [certification letter]", "schv_l03_community_contrib"),
    (4, "Enterprise zone property tax credit (from Florida Form F-1158Z attached)", "schv_l04_enterprise_zone"),
    (5, "Rural job tax credit [certification letter]", "schv_l05_rural_job"),
    (6, "Urban high-crime area job tax credit [certification letter]", "schv_l06_urban_high_crime"),
    (7, "Hazardous waste facility tax credit", "schv_l07_hazardous_waste"),
    (8, "Florida alternative minimum tax (AMT) credit", "schv_l08_florida_amt_credit"),
    (9, "Contaminated site rehabilitation tax credit (voluntary cleanup tax credit) [tax credit certificate]", "schv_l09_contaminated_site"),
    (10, "Child care tax credits", "schv_l10_child_care"),
    (11, "State housing tax credit [certification letter]", "schv_l11_state_housing"),
    (12, "Florida tax credit scholarship program credit [certificate]", "schv_l12_scholarship"),
    (13, "New worlds reading initiative credit [certificate]", "schv_l13_new_worlds_reading"),
    (14, "Strong families tax credit [certificate]", "schv_l14_strong_families"),
    (15, "Live local program credit [certificate]", "schv_l15_live_local"),
    (16, "Rural Community Investment Program credit [final order] (NEW for TY2025)", "schv_l16_rural_community_inv"),
    (17, "New markets tax credit", "schv_l17_new_markets"),
    (18, "Research and development tax credit", "schv_l18_research_dev"),
    (19, "Experiential learning tax credit", "schv_l19_experiential_learn"),
    (20, "Credit for qualified railroad reconstruction or replacement expenditures", "schv_l20_railroad"),
    (21, "Residential graywater system tax credit", "schv_l21_graywater"),
    (22, "Credit for manufacturing of human breast milk derived human milk fortifiers", "schv_l22_milk_fortifiers"),
    (23, "Individuals with unique abilities tax credit program", "schv_l23_unique_abilities"),
    (24, "Other credits (attach schedule) - FLAHIGA assessment credit goes here", "schv_l24_other_credits"),
    (25, "Total credits against the tax (sum of Lines 1 through 24 not to exceed the amount on Page 1, Line 11). Enter total credits on Page 1, Line 12", None),
]


FL1120_FACTS: list[dict] = [
    # ── THE FILING-OBLIGATION GATE (the highest-value facts on the form) ──
    {"fact_key": "entity_classification", "label": "Entity classification for ch. 220", "data_type": "choice", "required": True, "sort_order": 1,
     "choices": ["c_corp", "s_corp", "llc_taxed_as_corp", "llc_taxed_as_partnership", "smllc_disregarded",
                 "bank_or_savings_assoc", "homeowners_assoc", "political_org", "tax_exempt_with_ubti",
                 "charitable_trust", "ch609_business_trust", "receiver_trustee", "foreign_corp_fl_partner"],
     "notes": ("s. 220.03(1)(e) EXCLUDES proprietorships, partnerships as such, LLCs taxed as partnerships, "
               "ch. 616 fairs/expositions, estates of decedents or incompetents, testamentary trusts and "
               "private trusts. CHARITABLE TRUSTS ARE EXCLUDED ONLY FROM TY2026 — the 2025 statute text "
               "already prints them as excluded and is MISLEADING for TY2025 (W8).")},
    {"fact_key": "federal_return_type", "label": "Type of federal return filed (Question L)", "data_type": "choice", "required": True, "sort_order": 2,
     "choices": ["1120", "1120S", "1120-H", "1120-POL", "990-T", "1065", "other"],
     "notes": "A homeowners association filing federal 1120-H files NO Florida return; filing federal 1120 it files F-1120 regardless of tax due."},
    {"fact_key": "fed_1120s_line_23c", "label": "Federal Form 1120S Line 23c total tax (the S-corp filing switch)", "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": ("THE S-CORP GATE. > 0 => must file F-1120. W3: Line 23c carries Sec.1374 built-in gains, "
               "Sec.1375 excess net passive income AND LIFO RECAPTURE, but s. 220.13(2)(i) names only "
               "Sec.1374/Sec.1375 — a LIFO-recapture-only filer appears to owe a return with a ZERO base.")},
    {"fact_key": "fed_1120s_lifo_recapture_only", "label": "Is the entire Line 23c amount LIFO recapture tax? (W3)", "data_type": "boolean", "required": False, "sort_order": 4},
    {"fact_key": "has_florida_nexus", "label": "Doing business, earning income, or existing in Florida?", "data_type": "boolean", "required": True, "sort_order": 5,
     "notes": "Rule 12C-1.022(1)(a): it is the CORPORATION'S BURDEN to establish it need not file."},
    {"fact_key": "is_fl_partnership_member", "label": "Member of a Florida partnership or joint venture? (Question I)", "data_type": "boolean", "required": False, "sort_order": 6,
     "notes": "The F-1065 hook. A foreign corporate partner must file F-1120 and attach federal Schedule K-1 (Rule 12C-1.022(2)(e))."},
    {"fact_key": "state_of_incorporation", "label": "State of incorporation (Question A)", "data_type": "string", "required": False, "sort_order": 7,
     "notes": "Rule 12C-1.015(1)(b)1: incorporation OUTSIDE Florida clears the apportionment gate on its own."},
    {"fact_key": "s_election_acceptance_attached", "label": "IRS Notice of Acceptance as an S corporation attached?", "data_type": "boolean", "required": False, "sort_order": 8,
     "notes": "F-1120N p.6 (Line 19): required of a filing Sub S corporation if not already sent to the Department."},
    # ── Tax-year shape (W5 gate) ──
    {"fact_key": "tax_year_begin", "label": "Tax year beginning date", "data_type": "date", "required": True, "sort_order": 10},
    {"fact_key": "tax_year_end", "label": "Tax year ending date", "data_type": "date", "required": True, "sort_order": 11,
     "notes": "A FISCAL TY2025 ENDING IN 2026 IS A HARD BLOCK (W5/R1) — the applicable IRC is unresolved."},
    {"fact_key": "is_short_year", "label": "Short tax year?", "data_type": "boolean", "required": False, "sort_order": 12},
    {"fact_key": "short_year_days", "label": "Days in the short tax year (exemption proration numerator)", "data_type": "integer", "required": False, "sort_order": 13},
    # ── Line 1 / Line 2 ──
    {"fact_key": "federal_taxable_income", "label": "Federal taxable income (Line 1) - federal 1120 Line 30", "data_type": "decimal", "required": True, "sort_order": 20,
     "notes": ("DIRECT-ENTRY ONLY. NEVER SILENTLY RECOMPUTED. Florida's TY2025 IRC is the 1/1/2025 Code, so "
               "OBBBA is NOT adopted and this figure must be the PRE-OBBBA recompute — but NO LINE ON THE "
               "RETURN CARRIES THAT RECOMPUTE (W1). S corps enter ONLY income subject to federal tax at "
               "the corporate level.")},
    {"fact_key": "fti_pre_obbba_confirmed", "label": "Preparer confirms Line 1 is the PRE-OBBBA figure (W1)", "data_type": "boolean", "required": True, "sort_order": 21,
     "notes": "MANDATORY CONFIRMATION. Unconfirmed => blocking diagnostic D_FL1120_W1_NO_SILENT_RECOMPUTE."},
    {"fact_key": "state_income_taxes_deducted", "label": "State income taxes deducted in computing federal taxable income (Line 2, attach schedule)", "data_type": "decimal", "required": False, "sort_order": 22},
    # ── Depreciation tracks ──
    {"fact_key": "schi_l21_bonus_qip_portion", "label": "Sch I L21 portion attributable to QIP placed in service on/after 1/1/2018", "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": ("*** THE TAG. The L21 addition MUST be split QIP vs non-QIP at entry: the non-QIP half "
               "recovers 1/7 per year on Sch II L9, the QIP half recovers as hypothetical depreciation on "
               "Sch II L10. NEITHER HALF IS DERIVABLE FROM THE FEDERAL 4562. The L9 attached schedule "
               "expressly demands this figure as a separate line. ***")},
    {"fact_key": "bonus_addition_vintages", "label": "Sec.168(k) NON-QIP addition vintages (JSON {year: amount}) for the 7-year recovery", "data_type": "string", "required": False, "sort_order": 41,
     "notes": ("MULTI-YEAR STATE. A 7-vintage rolling schedule per addition year; year N subtraction = sum "
               "over open vintages of (addition/7). NOT derivable from the federal 4562 whenever the "
               "taxpayer claimed OBBBA 100% bonus federally — the Florida addition uses the PRE-OBBBA 40% "
               "for calendar-2025 placements. HIGHEST-RISK SILENT-WRONG-ANSWER PATH IN THE FL BUILD.")},
    {"fact_key": "qip_hypo_depr_2020_irc", "label": "QIP hypothetical depreciation under the IRC in effect 1/1/2020 without CARES (Sch II L10)", "data_type": "decimal", "required": False, "sort_order": 42,
     "notes": ("A SHADOW DEPRECIATION BOOK, not a fraction: QIP as 39-year nonresidential real property, "
               "and DISPOSITION IS IGNORED so the schedule keeps running after the asset is sold.")},
    # ── Apportionment gate + factors ──
    {"fact_key": "doing_business_outside_fl", "label": "Doing business WITHIN AND WITHOUT Florida? (the apportionment gate)", "data_type": "boolean", "required": True, "sort_order": 50,
     "notes": "FAILING THE GATE TAXES 100% OF ADJUSTED FEDERAL INCOME (Rule 12C-1.015(2)). W7 / R3."},
    {"fact_key": "gate_basis", "label": "Basis for the doing-business-without-Florida determination", "data_type": "choice", "required": False, "sort_order": 51,
     "choices": ["taxed_in_another_state", "another_state_has_jurisdiction", "incorporated_outside_fl",
                 "pl86272_solicitation_only", "de_minimis_only", "voluntary_filing_only", "none"],
     "notes": ("pl86272_solicitation_only, de_minimis_only and voluntary_filing_only DO NOT clear the gate "
               "(Rule 12C-1.015(1)(b)3-5, 7). incorporated_outside_fl clears it on its own ((1)(b)1).")},
    {"fact_key": "property_fl_beginning", "label": "Sch III-B: property within Florida, beginning of year (original cost)", "data_type": "decimal", "required": False, "sort_order": 52},
    {"fact_key": "property_fl_ending", "label": "Sch III-B: property within Florida, end of year (original cost)", "data_type": "decimal", "required": False, "sort_order": 53},
    {"fact_key": "property_everywhere_beginning", "label": "Sch III-B: property everywhere, beginning of year (original cost)", "data_type": "decimal", "required": False, "sort_order": 54},
    {"fact_key": "property_everywhere_ending", "label": "Sch III-B: property everywhere, end of year (original cost)", "data_type": "decimal", "required": False, "sort_order": 55},
    {"fact_key": "rented_property_fl_net_rent", "label": "Sch III-B L7a: Florida net annual rent (entered at 8x)", "data_type": "decimal", "required": False, "sort_order": 56},
    {"fact_key": "rented_property_ew_net_rent", "label": "Sch III-B L7b: everywhere net annual rent (entered at 8x)", "data_type": "decimal", "required": False, "sort_order": 57},
    {"fact_key": "payroll_fl", "label": "Sch III-A L2 col(a): salaries, wages, commissions and other compensation within Florida", "data_type": "decimal", "required": False, "sort_order": 58},
    {"fact_key": "payroll_everywhere", "label": "Sch III-A L2 col(b): compensation everywhere", "data_type": "decimal", "required": False, "sort_order": 59},
    {"fact_key": "sales_fl", "label": "Sch III-C L4: total sales within Florida (gross receipts, destination/performed-in rules)", "data_type": "decimal", "required": False, "sort_order": 60},
    {"fact_key": "sales_everywhere", "label": "Sch III-C L4: total sales everywhere (gross receipts without regard to returns or allowances)", "data_type": "decimal", "required": False, "sort_order": 61},
    {"fact_key": "dept_insignificance_determination", "label": "Department has DETERMINED a denominator insignificant (s. 220.15(1)) - write-in override", "data_type": "boolean", "required": False, "sort_order": 62,
     "notes": ("W4. INSIGNIFICANCE IS THE DEPARTMENT'S DETERMINATION, NOT THE PREPARER'S. The Column (d) "
               "write-in blank exists to RECORD a determination the Department has ALREADY made. The "
               "software NEVER auto-reweights a nonzero denominator.")},
    {"fact_key": "special_fraction_type", "label": "Sch III-D special apportionment fraction (RED-defer R9)", "data_type": "choice", "required": False, "sort_order": 63,
     "choices": ["none", "insurance", "transportation", "citrus", "s220_152_permission", "s220_153_single_sales"]},
    {"fact_key": "is_financial_organization", "label": "Financial organization? (extended sales definition + intangibles in the property factor) - RED-defer R8", "data_type": "boolean", "required": False, "sort_order": 64},
    # ── Schedule IV carryovers + Florida NOL ──
    {"fact_key": "schiv_l4_nol_apportioned", "label": "Sch IV L4: net operating loss carryover apportioned to Florida (attach schedule)", "data_type": "decimal", "required": False, "sort_order": 70},
    {"fact_key": "schiv_l5_capital_loss_appt", "label": "Sch IV L5: net capital loss carryover apportioned to Florida (attach schedule)", "data_type": "decimal", "required": False, "sort_order": 71},
    {"fact_key": "schiv_l6_charitable_appt", "label": "Sch IV L6: excess charitable contribution carryover apportioned to Florida", "data_type": "decimal", "required": False, "sort_order": 72},
    {"fact_key": "schiv_l7_emp_benefit_appt", "label": "Sch IV L7: employee benefit plan contribution carryover apportioned to Florida", "data_type": "decimal", "required": False, "sort_order": 73},
    {"fact_key": "fl_nol_pre2018_carryover", "label": "Florida NOL carryover from tax years beginning before 1/1/2018 (20-year, 100% offset, applied FIRST)", "data_type": "decimal", "required": False, "sort_order": 74},
    {"fact_key": "fl_nol_post2017_carryover", "label": "Florida NOL carryover from tax years beginning after 12/31/2017 (indefinite, 80% of the remainder)", "data_type": "decimal", "required": False, "sort_order": 75},
    # ── Schedule R nonbusiness ──
    {"fact_key": "schr_l1_nonbusiness_fl", "label": "Sch R L1: nonbusiness income (loss) allocated to Florida -> Page 1 Line 8", "data_type": "decimal", "required": False, "sort_order": 80,
     "notes": "s. 220.16. 'Functionally related dividends are presumed to be BUSINESS income.' 100% Florida => Schedule R not completed."},
    {"fact_key": "schr_l2_nonbusiness_other", "label": "Sch R L2: nonbusiness income (loss) allocated elsewhere", "data_type": "decimal", "required": False, "sort_order": 81},
    # ── Exemption / controlled group ──
    {"fact_key": "is_controlled_group_member", "label": "Member of a controlled group (Sec.1563, IRC)? (Question G-1)", "data_type": "boolean", "required": False, "sort_order": 90},
    {"fact_key": "controlled_group_exempt_share", "label": "This member's apportioned share of the single $50,000 controlled-group exemption", "data_type": "decimal", "required": False, "sort_order": 91,
     "notes": "Attaching the G-1 member list 'shows consent to an unequal apportionment'; absent a plan the default is division EQUALLY."},
    {"fact_key": "is_florida_consolidated", "label": "Florida consolidated return? (Question C) - RED-defer R5", "data_type": "boolean", "required": False, "sort_order": 92},
    {"fact_key": "is_federal_consolidated", "label": "Part of a federal consolidated return? (Question G-2)", "data_type": "boolean", "required": False, "sort_order": 93},
    # ── Penalties, interest, payments ──
    {"fact_key": "l14a_penalty_f2220", "label": "Line 14a: penalty from F-2220", "data_type": "decimal", "required": False, "sort_order": 100},
    {"fact_key": "l14b_penalty_other", "label": "Line 14b: other penalty", "data_type": "decimal", "required": False, "sort_order": 101},
    {"fact_key": "l14c_interest_f2220", "label": "Line 14c: interest from F-2220", "data_type": "decimal", "required": False, "sort_order": 102},
    {"fact_key": "l14d_interest_other", "label": "Line 14d: other interest", "data_type": "decimal", "required": False, "sort_order": 103},
    {"fact_key": "l16a_estimated_payments", "label": "Line 16a: estimated tax payments (F-1120ES)", "data_type": "decimal", "required": False, "sort_order": 104},
    {"fact_key": "l16b_tentative_payment", "label": "Line 16b: tentative tax payment (F-7004)", "data_type": "decimal", "required": False, "sort_order": 105},
    {"fact_key": "l18_credit_to_next_year", "label": "Line 18: overpayment credited to next year's estimated tax (IRREVOCABLE election)", "data_type": "decimal", "required": False, "sort_order": 106},
    {"fact_key": "l19_refund_requested", "label": "Line 19: overpayment to be refunded", "data_type": "decimal", "required": False, "sort_order": 107,
     "notes": "'If Line 19 is left blank, we will credit the entire overpayment to next year's estimated tax.'"},
    {"fact_key": "federal_return_attached", "label": "Copy of the actual federal return as filed (pages 1-6) attached?", "data_type": "boolean", "required": True, "sort_order": 108,
     "notes": "A return without it is INCOMPLETE: penalty the greater of $300 or 10% of tax, capped at $10,000."},
    {"fact_key": "form_4562_attached", "label": "Federal Form 4562 attached?", "data_type": "boolean", "required": False, "sort_order": 109},
    # ── The RED-defer flags that need their own facts ──
    {"fact_key": "has_163j_fl_carryforward", "label": "Florida-only Sec.163(j) disallowed-interest carryforward from TY2019-2020? (R6)", "data_type": "boolean", "required": False, "sort_order": 120},
    {"fact_key": "has_election_a_or_b_depr", "label": "Election A / Election B legacy depreciation adjustment (1981-1986 assets)? (R7)", "data_type": "boolean", "required": False, "sort_order": 121},
    {"fact_key": "schi_l25_partnership_increase", "label": "Sch I L25: partnership income adjustment INCREASE from Florida Form F-1065 Part II col (c)", "data_type": "decimal", "required": False, "sort_order": 122},
    {"fact_key": "schii_l12_partnership_decrease", "label": "Sch II L12: partnership income adjustment DECREASE from Florida Form F-1065 Part II col (c)", "data_type": "decimal", "required": False, "sort_order": 123},
    {"fact_key": "schi_l25_obbba_recompute_add", "label": "Sch I L25: TY2025 pre-OBBBA recompute ADDITION (PROPOSED landing zone, pending W1)", "data_type": "decimal", "required": False, "sort_order": 124,
     "notes": "PROPOSED ONLY. No DOR instruction names OBBBA as an L25 example. DO NOT TREAT AS SETTLED."},
    {"fact_key": "schii_l12_obbba_recompute_sub", "label": "Sch II L12: TY2025 pre-OBBBA recompute SUBTRACTION (PROPOSED landing zone, pending W1)", "data_type": "decimal", "required": False, "sort_order": 125,
     "notes": "PROPOSED ONLY. Pending Ken's W1 ruling."},
]

# Append the mechanical Schedule I / II / V facts from the label tables.
for _n, _label, _fk in SCHI_LABELS:
    if _fk:
        FL1120_FACTS.append({"fact_key": _fk, "label": f"Schedule I Line {_n}: {_label}",
                             "data_type": "decimal", "required": False, "sort_order": 200 + _n})
for _n, _label, _fk in SCHII_LABELS:
    if _fk:
        FL1120_FACTS.append({"fact_key": _fk, "label": f"Schedule II Line {_n}: {_label[:180]}",
                             "data_type": "decimal", "required": False, "sort_order": 300 + _n})
for _n, _label, _fk in SCHV_LABELS:
    if _fk:
        FL1120_FACTS.append({"fact_key": _fk, "label": f"Schedule V Line {_n}: {_label[:180]}",
                             "data_type": "decimal", "required": False, "sort_order": 400 + _n,
                             "notes": ("DIRECT-ENTRY with attachment; NEVER computed. Statutory s. 220.02(8) "
                                       "order preserved." + (" NO Schedule I add-back for this credit."
                                                             if _n in SCHV_NO_ADDBACK else
                                                             f" Adds back on Schedule I Line {SCHV_TO_SCHI[_n]}."))})


FL1120_RULES: list[dict] = [
    # ══════════════ THE FILING-OBLIGATION GATE — FIRST, because it decides
    # whether a return exists at all. Most Florida pass-throughs file NOTHING.
    {"rule_id": "R-FL-GATE-1120", "title": "F-1120 filing obligation — the gate that decides whether a return exists", "rule_type": "routing",
     "formula": ("file_F1120 := has_florida_nexus AND entity_classification NOT IN "
                 "{llc_taxed_as_partnership, smllc_disregarded} AND NOT (federal_return_type == '1120-H') "
                 "AND (entity_classification != 's_corp' OR fed_1120s_line_23c > 0) ; "
                 "emit an EXPLICIT 'No Florida return required' determination with reason + citation when False"),
     "inputs": ["has_florida_nexus", "entity_classification", "federal_return_type", "fed_1120s_line_23c"],
     "outputs": ["file_F1120", "no_return_determination"], "sort_order": 1,
     "description": ("s. 220.22(1) + Rule 12C-1.022(1). The default is hard the OTHER way: '(1)(a) The "
                     "Florida Income Tax Code does not specifically provide for an exception from the "
                     "filing requirements for any organization, association, or legal entity...It is the "
                     "burden of a corporation...to establish that it is not required to file.' Every "
                     "corporation INCLUDING tax-exempt organizations, banks/savings associations, LLCs "
                     "taxed as corporations, homeowners associations filing federal 1120, political "
                     "organizations filing 1120-POL, tax-exempt orgs with UBTI, ch. 609 business trusts "
                     "and (for TY2025 ONLY) CHARITABLE TRUSTS files F-1120. A homeowners association "
                     "filing federal 1120-H files NO Florida return ('rule says no', stated in terms). "
                     "A disregarded SMLLC files no separate return but its corporate owner reports its "
                     "income 'even if the only activity of the corporation is ownership of the single "
                     "member LLC' (Rule 12C-1.022(1)(b)2, extended to a QSub)."),
     "notes": ("A NO-TAX-DUE RETURN STILL MUST BE FILED ('You must file a return, even if no tax is due'); "
               "a late no-tax return draws $50/month up to $300. The determination is a POSITIVE OUTPUT "
               "with a reason and a citation, NEVER SILENCE.")},
    {"rule_id": "R-FL-GATE-SCORP", "title": "S corporation files F-1120 ONLY when federal 1120S Line 23c > 0", "rule_type": "routing",
     "formula": "file_F1120(s_corp) := (fed_1120s_line_23c > 0) ; Line1(s_corp) := ONLY income subject to federal tax at the corporate level",
     "inputs": ["entity_classification", "fed_1120s_line_23c", "fed_1120s_lifo_recapture_only"],
     "outputs": ["file_F1120", "federal_taxable_income"], "sort_order": 2,
     "description": ("Rule 12C-1.022(1)(b)1: \"'S' corporations are not subject to the tax, EXCEPT FOR "
                     "TAXABLE YEARS WHEN THEY ARE LIABLE FOR THE FEDERAL TAX under the Internal Revenue "
                     "Code.\" F-1120N p.2: 'S corporations that pay federal income tax on Line 23c of "
                     "federal Form 1120S.' F-1120N p.5: 'S corporations should enter only the amount of "
                     "income subject to federal income tax at the corporate level.' The non-filing is a "
                     "RULE-BASED EXEMPTION under s. 220.22(4), not a statutory vacuum — exceptions have "
                     "edges. F-1120A p.3 adds a refund exception: 'those S corporations answering no to "
                     "Question D do not have to file a return unless requesting a refund.'"),
     "notes": ("W3 — TRIGGER-WIDTH TENSION, UNRESOLVED. The rule/instructions key on federal liability / "
               "Line 23c, which carries Sec.1374 built-in gains, Sec.1375 excess net passive income AND "
               "LIFO RECAPTURE; s. 220.13(2)(i) defines the base as Sec.1374/Sec.1375 amounts ONLY. "
               "'1374' and '1375' appear ZERO times on any Florida form or instruction. A "
               "LIFO-recapture-only S corp appears to owe a return with a ZERO base. DO NOT SILENTLY "
               "RESOLVE — D_FL1120_W3_LIFO_RECAPTURE.")},
    {"rule_id": "R-FL-GATE-FOREIGN", "title": "Foreign corporate partner in a Florida partnership separately files F-1120", "rule_type": "routing",
     "formula": "if is_fl_partnership_member AND corporation is out-of-state: file_F1120 := True ; attach federal Schedule K-1 (Form 1065)",
     "inputs": ["is_fl_partnership_member", "entity_classification", "state_of_incorporation"],
     "outputs": ["file_F1120"], "sort_order": 3,
     "description": ("F-1120N p.1 / F-1065N p.1 verbatim: 'A foreign (out-of-state) corporation that is a "
                     "partner in a Florida partnership or a member of a Florida joint venture is subject "
                     "to the Florida Income Tax Code and must file a Florida Corporate Income/Franchise "
                     "Tax Return (Florida Form F-1120).' Rule 12C-1.022(2)(e) adds the K-1 attachment; "
                     "(6)(g): corporate members file 'Form F-1065...as well as, Form F-1120.'"),
     "notes": ("A COMMON MISS: ONE Florida partnership with ONE out-of-state corporate partner generates "
               "TWO Florida returns — the partnership's F-1065 AND the corporation's own F-1120.")},
    {"rule_id": "R-FL-GATE-TRUST", "title": "Charitable trusts DO file F-1120 for TY2025; no Florida fiduciary return exists", "rule_type": "routing",
     "formula": "if entity_classification == 'charitable_trust' AND tax_year begins before 1/1/2026: file_F1120 := True",
     "inputs": ["entity_classification", "tax_year_begin"], "outputs": ["file_F1120"], "sort_order": 4,
     "description": ("THERE IS NO FLORIDA FIDUCIARY INCOME TAX RETURN — 'rule says no': s. 220.03(1)(e) "
                     "excludes estates of decedents or incompetents, testamentary trusts and private "
                     "trusts from 'corporation.' BUT CHARITABLE TRUSTS WERE REQUIRED TO FILE F-1120 FOR "
                     "TY2025: the ch. 2025-208 exclusion applies only to tax years beginning on or after "
                     "1/1/2026, and Rule 12C-1.022's charitable-trust amendment was adopted EFFECTIVE "
                     "1/1/2026. Common-law declarations of trust under ch. 609 (Florida business trusts) "
                     "remain INSIDE ch. 220 and file F-1120."),
     "notes": ("W8 — TIMING TRAP. THE 2025 EDITION OF THE STATUTE ALREADY PRINTS 'charitable trusts' IN "
               "THE EXCLUSION LIST, so reading the statute alone gives the WRONG ANSWER for TY2025. "
               "DO NOT ENCODE THE CHARITABLE-TRUST EXCLUSION FOR TY2025.")},
    # ══════════════ W1 / W5 — THE TWO HARD BLOCKS
    {"rule_id": "R-FL-L1-NOSILENT", "title": "Line 1 — NO SILENT RECOMPUTE. Pre-OBBBA federal taxable income is DIRECT-ENTRY ONLY", "rule_type": "validation",
     "formula": ("L1 := federal_taxable_income (DIRECT ENTRY, federal 1120 Line 30 basis) ; "
                 "REQUIRE fti_pre_obbba_confirmed == True ; "
                 "Delvio NEVER computes the pre-OBBBA recompute and NEVER writes L1 from a federal figure "
                 "adjusted for OBBBA ; if unconfirmed -> BLOCKING diagnostic"),
     "inputs": ["federal_taxable_income", "fti_pre_obbba_confirmed"], "outputs": ["L1"], "sort_order": 5,
     "description": ("*** W1 — THIS RULE GATES THE LOADER. *** Florida's TY2025 conformity date is "
                     "1/1/2025 (s. 220.03(1)(n)), so OBBBA (P.L. 119-21, enacted 7/4/2025) IS NOT ADOPTED "
                     "FOR TY2025: ch. 2026-137 moved conformity to 1/1/2026 but 'operate[s] retroactively "
                     "to January 1, 2026' only, and s. 220.03(3) is not self-executing ('when expressly "
                     "authorized by law'). Line 1 must therefore carry federal taxable income RECOMPUTED "
                     "UNDER THE PRE-OBBBA CODE. BUT NO LINE, SCHEDULE, INSTRUCTION, TIP OR RULE CARRIES "
                     "THAT RECOMPUTE — confirmed by exhaustive search of all six TY2025 documents (zero "
                     "hits on nine OBBBA strings), by Rule 12C-1.013 being unamended since 10/27/2022, "
                     "and by the TY2026 draft form having no such line either. NO LINE WAS INVENTED."),
     "notes": ("Ken's call (W1): (a) restated Line 1, (b) Sch I L25 + Sch II L12 with an explanatory "
               "schedule and a Line 1 override — the brief's recommendation, encoded here as the PROPOSED "
               "landing zone only, or (c) a pro forma federal return. Note the tension with F-1120N's own "
               "Line 1 instruction ('enter the amount shown on Line 30 of federal Form 1120' — the "
               "AS-FILED figure) and with the required-attachment reconciliation.")},
    {"rule_id": "R-FL-FISCAL-BLOCK", "title": "HARD BLOCK — fiscal TY2025 straddling 1/1/2026 is not supported", "rule_type": "validation",
     "formula": "if tax_year_begin < 2026-01-01 AND tax_year_end >= 2026-01-01: BLOCK (no computation; prepare manually)",
     "inputs": ["tax_year_begin", "tax_year_end"], "outputs": ["blocking_diagnostic"], "sort_order": 6,
     "description": ("W5 / R1. ch. 2026-137 s. 3(1) says the amendments 'operate retroactively to January "
                     "1, 2026' — it does NOT say 'for tax years beginning on or after January 1, 2026.' A "
                     "calendar TY2025 is unambiguous (the whole year precedes 1/1/2026). A FISCAL TY2025 "
                     "ENDING IN 2026 (the classic FYE 6/30/2026) IS NOT SQUARELY ADDRESSED BY THE "
                     "STATUTE. DOR's working convention elsewhere in TIP 26C01-01 is tax-year-beginning "
                     "based, which would leave FYE 6/30/2026 on the 1/1/2025 Code — but that is "
                     "INFERENCE, NOT HOLDING."),
     "notes": ("A different answer means a DIFFERENT LINE 1 RECOMPUTE AND A DIFFERENT Sec.179 LIMIT. "
               "Florida's due-date and extension rules already single out June-30 year ends, so FYE 6/30 "
               "filers are NOT a rare edge. HARD BLOCK, not a warning.")},
    # ══════════════ THE F-1120 SPINE
    {"rule_id": "R-FL-SPINE", "title": "F-1120 face Lines 3-6 — adjusted federal income", "rule_type": "calculation",
     "formula": ("L3 = Sch I L26 ; L4 = L1 + L2 + L3 ; L5 = Sch II L13 ; L6 = L4 - L5 "
                 "(adjusted federal income). Lines 1-8 each carry a 'Check here if negative' flag — "
                 "Florida encodes SIGN IN A FLAG, not a minus sign."),
     "inputs": ["federal_taxable_income", "state_income_taxes_deducted"], "outputs": ["L3", "L4", "L5", "L6"], "sort_order": 10,
     "description": "F-1120 R. 01/26 page 1, 'Computation of Florida Net Income Tax', verbatim line labels."},
    {"rule_id": "R-FL-SCHI", "title": "Schedule I — Additions and/or Adjustments to Federal Taxable Income (26 lines)", "rule_type": "calculation",
     "formula": "Sch I L26 = sum(L1..L25) -> F-1120 Page 1 Line 3",
     "inputs": ["schi_l1_interest_excluded", "schi_l2_undistributed_ltcg", "schi_l3_fed_nol_deduction",
                "schi_l4_net_capital_loss_co", "schi_l5_excess_charitable_co", "schi_l6_emp_benefit_plan_co",
                "schi_l21_bonus_depreciation", "schi_l22_qip_depreciation", "schi_l23_business_meals",
                "schi_l24_film_181", "schi_l25_other_additions", "schi_l25_partnership_increase"],
     "outputs": ["SchI-26", "L3"], "sort_order": 11,
     "description": ("L1 = Sec.103(a) interest LESS expenses disallowed under Sec.265 (appears in federal "
                     "Sch M-1); L2 RIC/REIT only (Sec.852(b)(3)(D), 857(b)(3)(D)); L3 <- federal 1120 Line "
                     "29(a); L4 <- federal 1120 Schedule D (Sec.1212); L5 Sec.170(d)(2); L6 "
                     "Sec.404(a)(1)(E) and Sec.404(a)(3)(A)(ii). L25 'Other additions' named examples: the "
                     "partnership adjustment from Florida Form F-1065, the (effectively dead) consolidated "
                     "income adjustment requiring a s. 220.131(1) election made within 90 days of December "
                     "20, 1984, and the Election A/B depreciation adjustment."),
     "notes": "L25 is ALSO the PROPOSED (not settled) landing zone for the TY2025 OBBBA recompute addition — W1."},
    {"rule_id": "R-FL-SCHI-CREDITS", "title": "Schedule I Lines 7-20 — credit add-backs, SINGLE PASS (the loader convention)", "rule_type": "calculation",
     "formula": ("Sch I L7 = Sch V L4 ; L8 = Sch V L1 + FLAHIGA within Sch V L24 ; L9 = Sch V L5 + Sch V L6 ; "
                 "L10 = Sch V L11 ; L11 = Sch V L12 ; L12 = Sch V L13 ; L13 = Sch V L14 ; L14 = Sch V L15 ; "
                 "L15 = Sch V L17 ; L16 = Sch V L18 ; L17 = Sch V L19 ; L18 = Sch V L20 ; L19 = Sch V L21 ; "
                 "L20 = Sch V L22 . EVALUATED ONCE, from the INDIVIDUAL Schedule V lines AS ENTERED, "
                 "BEFORE the Schedule V Line 25 cap is applied. NO ITERATION."),
     "inputs": ["schv_l01_hmo_assessment", "schv_l04_enterprise_zone", "schv_l05_rural_job",
                "schv_l06_urban_high_crime", "schv_l11_state_housing", "schv_l12_scholarship",
                "schv_l13_new_worlds_reading", "schv_l14_strong_families", "schv_l15_live_local",
                "schv_l17_new_markets", "schv_l18_research_dev", "schv_l19_experiential_learn",
                "schv_l20_railroad", "schv_l21_graywater", "schv_l22_milk_fortifiers", "schv_l24_other_credits"],
     "outputs": ["SchI-7", "SchI-8", "SchI-9", "SchI-10", "SchI-11", "SchI-12", "SchI-13", "SchI-14",
                 "SchI-15", "SchI-16", "SchI-17", "SchI-18", "SchI-19", "SchI-20"], "sort_order": 12,
     "description": ("W2 — THE CIRCULARITY, AND WHY SINGLE PASS IS CORRECT. Adding back a credit raises "
                     "Florida net income, which raises the Line 11 cap, which can admit more credit. BUT "
                     "THE CIRCLE DOES NOT LITERALLY CLOSE: the cap lands on Schedule V LINE 25 ONLY ('sum "
                     "of Lines 1 through 24 not to exceed the amount on Page 1, Line 11'), while every "
                     "one of Schedule I Lines 7-20 says 'Enter the amount from Line N of Schedule V' — "
                     "NONE reads from Line 25. So the Schedule I add-back is not itself a function of "
                     "Line 11. SINGLE PASS IS THE LITERALLY CORRECT READING, not merely a pragmatic "
                     "shortcut. The loop bites only through preparer behaviour (entering on each Schedule "
                     "V line just the portion usable this year)."),
     "notes": ("EIGHT Schedule V credits have NO Schedule I add-back and MUST NOT generate one: L2 capital "
               "investment, L3 community contribution, L7 hazardous waste, L8 Florida AMT, L9 contaminated "
               "site, L10 child care, L16 Rural Community Investment, L23 individuals with unique "
               "abilities. Sch I L11 carries an ANTI-DUPLICATION PROVISO needing prior-year state: 'if the "
               "credit taken has previously been added to taxable income in a prior taxable year, and is "
               "taken as a deduction for federal tax purposes in the current taxable year, the amount of "
               "the deduction allowed shall not be added to taxable income in the current year.' "
               "Ken to RATIFY the single-pass convention (W2) — the alternative (add back only the USED "
               "portion) produces a DIFFERENT Line 10.")},
    {"rule_id": "R-FL-SCHII", "title": "Schedule II — Subtractions from Federal Taxable Income (13 lines)", "rule_type": "calculation",
     "formula": ("Sch II L1 = (a) s.78 income + (b) s.862 dividends + (c) s.951A income - (d) direct and "
                 "indirect expenses and amounts deducted under s.250 ; L2 = (a) s.951 subpart F - (b) "
                 "expenses ; L7 = Sch R L3 ; L13 = sum(L1..L12) -> F-1120 Page 1 Line 5"),
     "inputs": ["schii_l1_foreign_source_net", "schii_l2_subpart_f_net", "schii_l3_fl_nol_deduction",
                "schii_l4_fl_capital_loss_co", "schii_l5_fl_excess_charit_co", "schii_l6_fl_emp_benefit_co",
                "schii_l8_ibf_net_income", "schii_l10_qip_recovery", "schii_l11_film_181_recovery",
                "schii_l12_other_subtractions", "schii_l12_partnership_decrease"],
     "outputs": ["SchII-13", "L5"], "sort_order": 13,
     "description": ("L2 requires all Form 5471 material attached. L8 = ss. 220.63(5), 220.62(3). "
                     "PRINTED ON THE FORM FACE: 'Taxpayers doing business outside Florida enter zero on "
                     "Lines 3 through 6, and complete Schedule IV' — the Schedule II / Schedule IV fork."),
     "notes": ("'RULE SAYS NO' — DO NOT BUILD A FICA-TIP SUBTRACTION. F-1120N p.8 header: 'Taxpayers may "
               "not subtract from federal taxable income for Social Security and Medicare taxes paid on "
               "certain employee tip income when such taxes are taken as a credit on their federal "
               "corporate income tax return as part of the federal General Business Credit. Florida "
               "Statutes do not provide a similar credit...nor is there a provision for a subtraction.'")},
    # ══════════════ THE TWO DEPRECIATION TRACKS
    {"rule_id": "R-FL-BONUS", "title": "Sec.168(k) bonus — Sch I L21 addition, Sch II L9 recovery at 1/7 per year over SEVEN years", "rule_type": "calculation",
     "formula": ("Sch I L21 = ALL amounts claimed as a Sec.168(k) special depreciation allowance for "
                 "property PIS before 1/1/2027 (add-back 100%; statutory window PIS after 12/31/2007 and "
                 "before 1/1/2027) ; "
                 "NON-QIP portion = L21 - schi_l21_bonus_qip_portion ; "
                 "Sch II L9(year N) = SUM over open vintages v of (non_qip_addition_v / 7), where a "
                 "vintage is open for the 7 tax years BEGINNING WITH the year of the addition"),
     "inputs": ["schi_l21_bonus_depreciation", "schi_l21_bonus_qip_portion", "bonus_addition_vintages"],
     "outputs": ["SchI-21", "SchII-9"], "sort_order": 14,
     "description": ("s. 220.13(1)(e)1 + 1.b; F-1120N p.7 L21 and p.8 L9 verbatim: 'With the exception of "
                     "qualified improvement property placed in service on or after January 1, 2018, the "
                     "amount required to be added back for s.168(k), IRC, bonus depreciation is provided "
                     "back to a taxpayer through a subtraction over a seven-year period of one seventh of "
                     "the amount of the addition, beginning with the tax year of the addition. Attach a "
                     "schedule showing the taxable year and amount of the original addition, THE AMOUNT OF "
                     "THE ORIGINAL ADDITION FOR QUALIFIED IMPROVEMENT PROPERTY placed in service on or "
                     "after January 1, 2018, and the amount of the subtraction by taxable year.' "
                     "s. 220.13(1)(e)1.c CARVES QIP BONUS OUT of this track."),
     "notes": ("*** THE L21 ADDITION MUST BE TAGGED QIP / NON-QIP AT ENTRY — the two halves recover on "
               "DIFFERENT LINES under DIFFERENT FORMULAS, and the L9 attached schedule expressly demands "
               "the split. NEITHER HALF IS DERIVABLE FROM THE FEDERAL 4562. *** Compounding effect: "
               "because Florida's TY2025 Code is the 1/1/2025 Code, the bonus percentage used for the "
               "Florida computation is the PRE-OBBBA 40% for calendar-2025 placements, not OBBBA's 100%. "
               "Net TY2025 Florida result: no current-year bonus benefit either way — but the L21 addition "
               "and the resulting 7-year L9 schedule DIFFER FROM THE FEDERAL FORM 4562 whenever the "
               "taxpayer claimed OBBBA 100% bonus federally. HIGHEST-RISK SILENT-WRONG-ANSWER PATH IN THE "
               "FLORIDA BUILD. MULTI-YEAR STATE REQUIRED.")},
    {"rule_id": "R-FL-QIP", "title": "QIP — the SEPARATE PARALLEL TRACK (Sch I L22 -> Sch II L10 hypothetical depreciation)", "rule_type": "calculation",
     "formula": ("Sch I L22 = federal depreciation taken on QIP placed in service on/after 1/1/2018, "
                 "EXCLUDING any QIP bonus already added back on L21 (anti-double-count) ; "
                 "Sch II L10 = depreciation that WOULD HAVE BEEN ALLOWED under the IRC IN EFFECT ON "
                 "1/1/2020, WITHOUT the CARES Act retroactive changes, and WITHOUT TAKING INTO ACCOUNT ANY "
                 "SALE OR OTHER DISPOSITION — recovering BOTH Sch I L22 AND the QIP portion added back on "
                 "Sch I L21"),
     "inputs": ["schi_l22_qip_depreciation", "schi_l21_bonus_qip_portion", "qip_hypo_depr_2020_irc"],
     "outputs": ["SchI-22", "SchII-10"], "sort_order": 15,
     "description": ("F-1120N p.7 L22 verbatim: 'If bonus depreciation was taken on the qualified "
                     "improvement property and the bonus depreciation was included on Line 21, it should "
                     "not be added back again on this line.' F-1120N p.8 L10 verbatim: the subtraction "
                     "recovers 'Schedule I, Line 22, AND THE PORTION RELATED TO SUCH PROPERTY ADDED BACK "
                     "ON SCHEDULE I, LINE 21' and 'is limited to the depreciation that would have been "
                     "allowed under the IRC in effect on January 1, 2020, without retroactive changes made "
                     "by the CARES Act, and without taking into account any sale or other disposition of "
                     "the property.'"),
     "notes": ("NOT A 1/7 TRACK. This is a SHADOW DEPRECIATION BOOK: QIP as 39-YEAR NONRESIDENTIAL REAL "
               "PROPERTY (the pre-CARES treatment), not 15-year — AND DISPOSITION IS IGNORED, so the "
               "schedule KEEPS RUNNING AFTER THE ASSET IS SOLD. It CANNOT share a line with the bonus "
               "track because the two recover differently.")},
    {"rule_id": "R-FL-179-NOADDBK", "title": "Sec.179 — THERE IS NO FLORIDA ADD-BACK. 'The rule says no.'", "rule_type": "validation",
     "formula": ("Sec.179 add-back := NONE for TY2025. Sec.179 enters Florida ONLY through federal taxable "
                 "income at Line 1, at the PRE-OBBBA limit: $1,250,000 / $3,130,000 phase-out / $31,300 "
                 "SUV sublimit. DO NOT ENCODE $2,500,000 / $4,000,000 FOR FLORIDA TY2025."),
     "inputs": ["federal_taxable_income"], "outputs": ["no_179_addback"], "sort_order": 16,
     "description": ("AN AFFIRMATIVE LEGAL EXCLUSION, NOT A SILENCE. s. 220.13(1)(e)2 contains a Sec.179 "
                     "add-back but it reaches only 'an amount equal to 100 percent of any amount in excess "
                     "of $128,000 deducted for federal income tax purposes for the taxable year pursuant "
                     "to s. 179...FOR TAXABLE YEARS BEGINNING AFTER DECEMBER 31, 2007, AND BEFORE JANUARY "
                     "1, 2015' — TY2025 is outside the window BY ITS OWN TERMS. Verified by exhaustive "
                     "text search: the string '179' does not occur ANYWHERE in F-1120 R. 01/26, F-1120N "
                     "R. 01/26, F-1065/F-1065N R. 01/24 or F-1120A R. 01/24 — not a line, not an "
                     "instruction, not a footnote; Schedule I Lines 1-26 and Schedule II Lines 1-13 were "
                     "each read individually. The pre-OBBBA figures come from Rev. Proc. 2024-40 Sec.2.25, "
                     "which sets the 2025 inflation adjustments for Code provisions 'as in effect on "
                     "October 22, 2024' — the same Code Florida adopted as of January 1, 2025."),
     "notes": ("ENCODED AS AN EXPLICIT INFORMATIONAL DIAGNOSTIC (D_FL1120_179_NO_ADDBACK) SO NOBODY LATER "
               "'HELPFULLY' ADDS AN ADD-BACK. Note this is SEPARATE from bonus: Florida does not conform "
               "to Sec.168(k) but DOES take Sec.179 as it stands in the 1/1/2025 Code.")},
    {"rule_id": "R-FL-MEALS-181", "title": "Business meals (Sch I L23) and s. 181 film/TV/theatrical (Sch I L24 -> Sch II L11)", "rule_type": "calculation",
     "formula": ("Sch I L23 = the business-meal deduction in excess of what would have been allowed without "
                 "P.L. 116-260 Div. EE Title II s. 210 (which made restaurant meals 100% instead of 50% "
                 "deductible) — NO RECOVERY LINE, permanent ; "
                 "Sch I L24 = the s. 181 deduction ; Sch II L11 = 'the deduction that would have been "
                 "allowed without application of s. 181, IRC, if any' (hypothetical, year-by-year schedule)"),
     "inputs": ["schi_l23_business_meals", "schi_l24_film_181", "schii_l11_film_181_recovery"],
     "outputs": ["SchI-23", "SchI-24", "SchII-11"], "sort_order": 17,
     "description": ("Both instructions state the window verbatim and identically: 'This addition applies "
                     "to taxable years beginning on or after January 1, 2021, and before January 1, 2026.' "
                     "IN FORCE FOR TY2025."),
     "notes": "*** BOTH EXPIRE FOR TY2026 and the TY2026 draft form DELETES these lines, renumbering Schedules I and II. TY2026 firewall. ***"},
    # ══════════════ APPORTIONMENT
    {"rule_id": "R-FL-APPORT-GATE", "title": "THE APPORTIONMENT GATE — failing it taxes 100% of adjusted federal income", "rule_type": "conditional",
     "formula": ("apportionment_available := doing_business_outside_fl per Rule 12C-1.015(1) ; "
                 "if NOT available: L7 = L6 (100% of adjusted federal income is Florida income) ; "
                 "gate_basis IN {pl86272_solicitation_only, de_minimis_only, voluntary_filing_only, none} "
                 "DOES NOT CLEAR THE GATE ; gate_basis == incorporated_outside_fl CLEARS IT ON ITS OWN"),
     "inputs": ["doing_business_outside_fl", "gate_basis", "state_of_incorporation"],
     "outputs": ["apportionment_available", "L7"], "sort_order": 20,
     "description": ("*** W7 — COUNTER-INTUITIVE AND THE MOST ADVERSE SILENT OUTCOME IN THE FLORIDA "
                     "BUILD. *** Rule 12C-1.015(1)(d) says IN TERMS 'THERE IS NO THROWBACK RULE IN "
                     "FLORIDA' — but that protects only taxpayers who have ALREADY CLEARED THE GATE. "
                     "(2): 'If a taxpayer is not considered to be doing business within and without "
                     "Florida under subsection (1), ALL OF ITS ADJUSTED FEDERAL INCOME WILL BE SUBJECT TO "
                     "FLORIDA CORPORATE INCOME/FRANCHISE TAX.' A true throwback rule merely reassigns "
                     "untaxed destination sales to the origin numerator; FLORIDA INSTEAD DENIES "
                     "APPORTIONMENT ENTIRELY — functionally MORE ADVERSE than throwback. F-1120N p.9: "
                     "'Making only sales in another state without property or payroll in that state does "
                     "not automatically indicate a taxpayer is \"doing business\" in a state other than "
                     "Florida.' (1)(b)7: voluntary filing elsewhere is 'not...conclusive proof that the "
                     "state had jurisdiction.' (1)(c): once cleared, denominators are FULL-EVERYWHERE. "
                     "(7)(b): consolidated groups are tested GROUPWIDE."),
     "notes": "DELVIO MUST NEVER AUTO-APPORTION ON A SALES-ONLY OUT-OF-STATE FOOTPRINT. Loud RED: D_FL1120_R3_APPORT_GATE."},
    {"rule_id": "R-FL-APPORT", "title": "Schedule III-A — three-factor apportionment, 25% property / 25% payroll / 50% sales", "rule_type": "calculation",
     "formula": ("property factor num/den from Sch III-B L8a/L8b = (beginning + ending)/2 at ORIGINAL COST "
                 "(no accumulated depreciation) PLUS 8 x net annual rent ; payroll from Sch III-A L2 ; "
                 "sales from Sch III-C L4 ; each column (c) = col(a)/col(b) ROUNDED TO SIX DECIMAL PLACES ; "
                 "column (e) = col(c) x weight ; Sch III-A L4 = sum of Lines 1-3 column (e), six decimals "
                 "-> Schedule IV Line 2"),
     "inputs": ["property_fl_beginning", "property_fl_ending", "property_everywhere_beginning",
                "property_everywhere_ending", "rented_property_fl_net_rent", "rented_property_ew_net_rent",
                "payroll_fl", "payroll_everywhere", "sales_fl", "sales_everywhere"],
     "outputs": ["SchIII-A-4"], "sort_order": 21,
     "description": ("s. 220.15(1) verbatim AND F-1120N p.9 — the two agree. FLORIDA IS NOT A "
                     "SINGLE-SALES-FACTOR STATE; a single sales factor is available only by permission "
                     "under s. 220.153. Sourcing (F-1120N p.10): TPP -> DESTINATION ('delivered or "
                     "shipped to a purchaser within Florida'); services -> PERFORMED IN FLORIDA; rentals "
                     "-> property located in Florida; interest on deferred payments -> follows the situs "
                     "of the sale. 'Sales' = GROSS RECEIPTS WITHOUT REGARD TO RETURNS OR ALLOWANCES, not "
                     "limited to TPP. EXCLUDED FROM ALL FACTORS: 'All amounts related to nonbusiness "
                     "income, income related to ss. 78, 862, 951, and 951A, IRC, and any other income not "
                     "included in the adjusted federal income (Florida Form F-1120, Line 6).' Sponsored "
                     "research certified through a Florida state university is excluded from BOTH factors. "
                     "Rule 12C-1.015(10): a corporate partner ADDS its share of a partnership's property, "
                     "payroll and sales to its own factors 'regardless of whether the partnerships are "
                     "Florida partnerships.'"),
     "notes": ("DO NOT SOURCE THE WEIGHTS FROM RULE 12C-1.015 — that rule was last amended 3/18/1996, "
               "carries a 1986 worked example, and expressly defers to s. 220.15(1). Monthly averaging may "
               "be required by the Department where property values fluctuate substantially.")},
    {"rule_id": "R-FL-APPORT-ZERO", "title": "Zero-DENOMINATOR reweighting only — insignificance is the DEPARTMENT'S call", "rule_type": "conditional",
     "formula": ("IF Column (b) denominator == 0 (EXACTLY zero): "
                 "  any TWO factors zero -> the remaining factor 100% ; "
                 "  SALES zero -> property 50%, payroll 50% ; "
                 "  PROPERTY or PAYROLL zero -> the OTHER 33-1/3%, sales 66-2/3% ; "
                 "ELSE keep 25/25/50. "
                 "NEVER reweight a small-but-nonzero denominator — raise a diagnostic instead."),
     "inputs": ["property_everywhere_beginning", "property_everywhere_ending", "payroll_everywhere",
                "sales_everywhere", "dept_insignificance_determination"],
     "outputs": ["apportionment_weights"], "sort_order": 22,
     "description": ("*** W4 — CORRECTED LAW. s. 220.15(1) verbatim: a factor 'has a denominator that is "
                     "zero OR IS DETERMINED BY THE DEPARTMENT TO BE INSIGNIFICANT.' INSIGNIFICANCE IS "
                     "EXPRESSLY RESERVED TO THE DEPARTMENT — it is NOT a preparer election and NOT a "
                     "self-executing de-minimis rule. *** The statute's three reweighting cases match the "
                     "F-1120N p.9 note EXACTLY; there is no width difference in the OUTCOMES, only in the "
                     "TRIGGER. The form itself triggers on Column (b) = 0, which is the only "
                     "self-executing branch. The write-in blank printed in Column (d) ('X 25% or ______') "
                     "exists to RECORD a determination the Department has ALREADY MADE."),
     "notes": ("ABSENT A DEPARTMENT DETERMINATION THE TAXPAYER HAS NO AUTHORITY TO REWEIGHT. The software "
               "must ASK (D_FL1120_INSIGNIFICANT_DEN), never compute.")},
    {"rule_id": "R-FL-SCHIV", "title": "Schedule IV — Florida portion of adjusted federal income, and the CARRYOVER FORK", "rule_type": "calculation",
     "formula": ("Sch IV L1 = F-1120 L6 ; L2 = Sch III-A L4 (or Sch III-D column (c)) ; L3 = L1 x L2 "
                 "(tentative apportioned adjusted federal income) ; L8 = L4 + L5 + L6 + L7 ; "
                 "L9 = L3 - L8 -> F-1120 Line 7. "
                 "THE FORK: if 100% within Florida -> carryovers on Sch II L3-L6 and Sch IV NOT completed ; "
                 "if doing business outside Florida -> Sch II L3-L6 = ZERO and carryovers on Sch IV L4-L7. "
                 "NEVER BOTH."),
     "inputs": ["schiv_l4_nol_apportioned", "schiv_l5_capital_loss_appt", "schiv_l6_charitable_appt",
                "schiv_l7_emp_benefit_appt", "doing_business_outside_fl"],
     "outputs": ["SchIV-9", "L7"], "sort_order": 23,
     "description": ("THE SINGLE MOST COMMON STRUCTURAL ERROR ON THIS RETURN. The four carryovers (NOL, "
                     "net capital loss, excess charitable contribution, employee benefit plan "
                     "contribution) live on EITHER Schedule II OR Schedule IV, NEVER BOTH. Stated THREE "
                     "TIMES in the source: on the form face at Schedule II ('Taxpayers doing business "
                     "outside Florida enter zero on Lines 3 through 6, and complete Schedule IV'), at "
                     "F-1120N p.4 (NOLD) and at F-1120N p.8 (Sch II note). ORDERING: 'If you have other "
                     "Florida carryover deductions, apply them first before applying your Florida NOLD.'"),
     "notes": "Encode a HARD ASSERTION that the four carryovers appear on exactly one of the two schedules."},
    {"rule_id": "R-FL-NOL", "title": "Florida NOL — no carryback, two-tier limitation, mandatory order", "rule_type": "calculation",
     "formula": ("tier1 = min(pre_2018_carryover, 100% of Florida tentative apportioned adjusted federal "
                 "income) ; remainder = base - tier1 ; tier2 = min(post_2017_carryover, 0.80 x remainder) ; "
                 "NOLD = tier1 + tier2. NO CARRYBACK, EVER."),
     "inputs": ["fl_nol_pre2018_carryover", "fl_nol_post2017_carryover"], "outputs": ["SchIV-4", "SchII-3"], "sort_order": 24,
     "description": ("F-1120N p.4. Carried forward 'in the same manner, to the same extent, and for the "
                     "same time periods prescribed in s. 172, IRC'; the carryover is limited to the "
                     "federal NOL x the Florida apportionment fraction, and 'adjustments such as those "
                     "listed in s. 220.13(1)(e), F.S., may increase the amount of the Florida carryover' — "
                     "i.e. THE BONUS/QIP ADD-BACKS FEED THE NOL. Pre-1/1/2018 losses carry forward 20 "
                     "years; post-12/31/2017 losses carry forward INDEFINITELY and never expire. For tax "
                     "years beginning after 12/31/2020 (=> TY2025) PRE-2018 CARRYOVERS APPLY FIRST AGAINST "
                     "100%, THEN POST-2017 AGAINST 80% OF THE REMAINDER. ORDER IS MANDATORY."),
     "notes": ("Required support-schedule columns: Tax Year, Adjusted Federal Income/Loss, Apportionment "
               "Fraction for the Year of Loss, Florida Apportioned Income/Loss, NOLCO Applied, Florida "
               "Portion of Adjusted Federal Income, NOL Carry Forward to Next Year. Two worked examples at "
               "F-1120N p.16 (one apportioning, one 100%-Florida).")},
    # ══════════════ EXEMPTION, RATE, CREDITS, PAYMENTS
    {"rule_id": "R-FL-EXEMPT", "title": "Line 9 — the $50,000 Florida exemption (lesser-of, short-year, one per controlled group)", "rule_type": "calculation",
     "formula": ("L9 = 0 if (L7 + L8) <= 0 else min(cap, L7 + L8) ; "
                 "cap = 50000 ; if short year: cap = 50000 x days_in_short_year / 365 ; "
                 "if controlled group: cap = this member's apportioned share of the SINGLE group exemption"),
     "inputs": ["is_short_year", "short_year_days", "is_controlled_group_member", "controlled_group_exempt_share"],
     "outputs": ["L9"], "sort_order": 30,
     "description": ("s. 220.14; F-1120N p.5. ONE $50,000 exemption PER CONTROLLED GROUP as defined in "
                     "Sec.1563, IRC. Question G-1: if members file separately, attach a member list with "
                     "FEIN, address and the apportioned amount for each corporation — 'Attaching the list "
                     "shows consent to an unequal apportionment of the Florida exemption.' F-1120A states "
                     "the default the long form does not: absent an apportionment plan the exemption 'will "
                     "be divided EQUALLY among all filing members.'"),
     "notes": "Zero floor: if L7 + L8 is zero or less, enter zero."},
    {"rule_id": "R-FL-TAX", "title": "Lines 10-13 — Florida net income, 5.5% tax, credits, total tax due", "rule_type": "calculation",
     "formula": ("L10 = max(0, L7 + L8 - L9)  [if a loss, enter zero] ; "
                 "L11 = 0.055 x L10 ; L12 = Sch V L25 = min(sum of Sch V L1..L24, L11) ; L13 = L11 - L12"),
     "inputs": ["schv_l01_hmo_assessment"], "outputs": ["L10", "L11", "L12", "L13"], "sort_order": 31,
     "description": ("FORM FACE VERBATIM: 'Tax due: 5.5% of Line 10.' (F-1120A Line 6 prints '5.5% of Line "
                     "5'; the page-6 estimated worksheet prints '5.5% of Line 3'.) s. 220.11(2)(a) '5 1/2 "
                     "percent'; s. 220.1105 repealed the rate-adjustment mechanism and FIXED 5.5% for tax "
                     "years beginning on or after 1/1/2022 — the 4.458% (2019-2020) and 3.535% (2021) "
                     "rates are HISTORICAL ONLY. Credits are CAPPED AT LINE 11 and CANNOT CREATE A REFUND."),
     "notes": ("AMT: s. 220.11(3) prescribes 3.3% for taxpayers determining taxable income under "
               "s. 220.13(2)(k), but FOR TAX YEARS BEGINNING ON OR AFTER 1/1/2018 THERE IS NO FLORIDA AMT "
               "and no new Florida AMT credit is created — only pre-2018 carryforwards remain (Sch V L8, "
               "RED-defer R4). Rule 12C-1.022(5) still demands a 'Florida alternative minimum tax "
               "schedule' — A RULE-STALENESS ARTIFACT; there is no such schedule on F-1120 R. 01/26. "
               "DO NOT BUILD IT.")},
    {"rule_id": "R-FL-SCHV", "title": "Schedule V — 25 credit lines in the statutory s. 220.02(8) ORDER; L25 capped at L11", "rule_type": "calculation",
     "formula": "Sch V L25 = min(sum(L1..L24), F-1120 Line 11) -> F-1120 Line 12",
     "inputs": ["schv_l02_capital_investment", "schv_l03_community_contrib", "schv_l07_hazardous_waste",
                "schv_l08_florida_amt_credit", "schv_l09_contaminated_site", "schv_l10_child_care",
                "schv_l16_rural_community_inv", "schv_l23_unique_abilities"],
     "outputs": ["SchV-25", "L12"], "sort_order": 32,
     "description": ("F-1120N p.11 verbatim: 'Section 220.02(8), F.S., provides for an order of "
                     "application for the credits against corporate income tax. THE CREDITS ARE LISTED IN "
                     "SCHEDULE V IN THE ORDER THEY MUST BE APPLIED.' LINE ORDER *IS* THE STATUTORY "
                     "ORDERING RULE — PRESERVE IT. NEW FOR TY2025: Line 16 Rural Community Investment "
                     "Program Credit — 'A credit...to taxpayers who make investor contributions in a rural "
                     "fund, as certified by the Florida Department of Commerce. The credit is equal to 25% "
                     "of the investor contribution'; enter 20% of the approved credit in each of the tax "
                     "years containing the first through fifth credit certification dates, carrying "
                     "forward until the year containing the 11th."),
     "notes": ("NEARLY EVERY CREDIT REQUIRES A DOR PRE-ALLOCATION OR A THIRD-PARTY CERTIFICATE AS AN "
               "ATTACHMENT; several are transferable within an affiliated group via DR-1xxxxx / F-11915T / "
               "F-11991T notices. SCOPE THESE AS DATA-ENTRY-WITH-ATTACHMENT, NEVER AS COMPUTED CREDITS. "
               "Raise D_FL1120_SCHV_CAP_BINDS when the L25 total equals the Line 11 cap (W2).")},
    {"rule_id": "R-FL-SCHR", "title": "Schedule R — nonbusiness income ALLOCATED, and the L1/L3 asymmetry", "rule_type": "calculation",
     "formula": ("Sch R L1 (allocated TO FLORIDA) -> F-1120 Page 1 Line 8 (ADDED) ; "
                 "Sch R L3 = L1 + L2 (Florida AND elsewhere) -> Schedule II Line 7 (SUBTRACTED)"),
     "inputs": ["schr_l1_nonbusiness_fl", "schr_l2_nonbusiness_other"], "outputs": ["SchR-1", "SchR-3", "L8", "SchII-7"], "sort_order": 33,
     "description": ("s. 220.16. NOTE THE ASYMMETRY: Line 1 (Florida only) is ADDED at F-1120 Line 8 while "
                     "Line 3 (Florida PLUS elsewhere) is SUBTRACTED at Schedule II Line 7 — that is what "
                     "removes ALL nonbusiness income from the apportionable base before adding the Florida "
                     "slice back. Definition (F-1120N p.15): 'rents and royalties from real or tangible "
                     "personal property, capital gains, interest, dividends, and patent and copyright "
                     "royalties, TO THE EXTENT THEY DO NOT ARISE FROM TRANSACTIONS AND ACTIVITIES IN THE "
                     "REGULAR COURSE OF A TAXPAYER'S TRADE OR BUSINESS.' 'FUNCTIONALLY RELATED DIVIDENDS "
                     "ARE PRESUMED TO BE BUSINESS INCOME.'"),
     "notes": "'Taxpayers that conduct business entirely within Florida do not need to complete Schedule R.' Business-vs-nonbusiness typing is a JUDGEMENT CALL — direct-entry."},
    {"rule_id": "R-FL-PAYMENTS", "title": "Lines 14-19 — penalties/interest, payment credits, amount due, credit-forward, refund", "rule_type": "calculation",
     "formula": ("L14 = 14a + 14b + 14c + 14d ; L15 = L13 + L14 ; L16 = 16a + 16b ; L17 = L15 - L16 ; "
                 "if L17 < 0 (overpayment) -> Line 18 (credit to next year, IRREVOCABLE) and/or Line 19 (refund)"),
     "inputs": ["l14a_penalty_f2220", "l14b_penalty_other", "l14c_interest_f2220", "l14d_interest_other",
                "l16a_estimated_payments", "l16b_tentative_payment", "l18_credit_to_next_year", "l19_refund_requested"],
     "outputs": ["L14", "L15", "L16", "L17", "L18", "L19"], "sort_order": 34,
     "description": ("Page 1 also carries a PAYMENT COUPON ('Do not detach coupon') repeating Lines 17/18/19 "
                     "and the year-ending date. Penalties (F-1120N pp.2-3): late filing 10%/month max 50% "
                     "of tax due; NO TAX DUE -> $50/month max $300; underpayment of tentative tax 12%/yr; "
                     "underpayment of estimated tax 12%/yr; incomplete return the greater of $300 or 10% "
                     "capped at $10,000; fraudulent 100% of the deficiency; failure to e-file when "
                     "required 5% of tax due per month max $250, or $10 if no tax is due. Interest floats "
                     "under s. 220.807, reset January 1 and July 1."),
     "notes": "*** 'If Line 19 is left blank, we will credit the entire overpayment to next year's estimated tax.' The Line 18 election is IRREVOCABLE. ***"},
    {"rule_id": "R-FL-DUEDATE", "title": "F-1120 due date — the LATER-OF test with a June-30 carve-out; F-7004 extension", "rule_type": "calculation",
     "formula": ("due = LATER OF (1) first day of the 4th month after close for JUNE 30 year ends, or "
                 "first day of the 5th month for ALL OTHER year ends ; and (2) the 15th day following the "
                 "unextended federal due date. Calendar TY2025 -> MAY 1, 2026. "
                 "Saturday/Sunday/federal-or-state holiday -> next business day."),
     "inputs": ["tax_year_end"], "outputs": ["due_date"], "sort_order": 35,
     "description": ("F-1120N p.2. Extension: F-7004 ONLY — 'A copy of your federal extension alone will "
                     "not extend the time for filing your Florida return' (Rule 12C-1.0222); six months, "
                     "SEVEN for a June 30 year end; ONE ONLY; an extension may be granted for Florida even "
                     "if no federal extension was granted. THE EXTENSION IS VOID IF the tentative tax is "
                     "not paid OR the taxpayer underpays by THE GREATER OF $2,000 OR 30% of the tax shown "
                     "on the F-1120 when filed. Underpayment of tentative tax: 12% per year from the "
                     "ORIGINAL due date. F-7004 extends F-1120 AND F-1065 (face: '1065 / 1120S / All other "
                     "federal returns')."),
     "notes": ("*** F-1120 AND F-1065 HAVE DIFFERENT DUE DATES — F-1065 is the FIRST DAY OF THE FOURTH "
               "MONTH for ALL year ends (calendar: April 1 vs May 1). *** TIP 26C01-01 moves June-30 year "
               "ends to the 5th-month rule for TYs beginning on/after 1/1/2026 — A TY2026 CHANGE, DO NOT "
               "APPLY TO TY2025.")},
    {"rule_id": "R-FL-ESTTAX", "title": "Estimated tax — $2,500 threshold, four EQUAL installments, do not annualize", "rule_type": "calculation",
     "formula": ("required if expected Florida income tax liability EXCEEDS $2,500 ; four EQUAL "
                 "installments of 0.25 each ; 1st due the last day of the 4th month (June 30 year end) or "
                 "the 5th month otherwise, 2nd the last day of the 6th month, 3rd the 9th month, 4th the "
                 "LAST DAY OF THE TAXABLE YEAR. Calendar-year: MAY 31, JUNE 30, SEPTEMBER 30, DECEMBER 31. "
                 "DO NOT ANNUALIZE."),
     "inputs": ["l16a_estimated_payments"], "outputs": ["estimated_installments"], "sort_order": 36,
     "description": ("F-1120N p.3 + F-1120ES; the F-1120 page-6 worksheet and F-1120ES agree. Underpayment "
                     "penalty 12%/yr on F-2220 (R. 01/25), from the installment due date to the earlier of "
                     "payment or the unextended annual due date. SAFE HARBOURS: 'At least 90% of the tax "
                     "finally shown to be due for the taxable year; or the tax computed using the prior "
                     "year facts and income and current year rates' — the prior-year-exception installments "
                     "are REDUCED BY credits earned under the Florida Tax Credit Scholarship, New Worlds "
                     "Reading, Strong Families, Live Local, Child Care and Human Milk Fortifiers programs."),
     "notes": ("Short taxable years: a separate F-1120ES is required 'unless the short period is less than "
               "four months or the requirement is first met after the first day of the last month.' For a "
               "short period from an ACCOUNTING-PERIOD CHANGE, ANNUALIZE (income x 12 / months) — note the "
               "tension with the general 'do not annualize': the annualization is for the THRESHOLD TEST, "
               "not the payments. NOTE the F-1120 page-6 estimated worksheet is headed 'For Taxable Years "
               "Beginning On or After January 1, 2026' — it is the PROSPECTIVE TY2026 worksheet bound "
               "into the TY2025 return, exactly as expected.")},
]

FL1120_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-FL-GATE-1120", "FL_RULE_12C_1_022", "primary", "12C-1.022(1)(a)-(b): no general exception; the burden is on the corporation"),
    ("R-FL-GATE-1120", "FL_2025_F1120N_INSTR", "primary", "F-1120N pp.1-2 'Who Must File' matrix, incl. the 1120-H no-return rule"),
    ("R-FL-GATE-1120", "FL_FS_CH220_2025", "secondary", "s. 220.22(1) and (4) — the rule-based exemption regime"),
    ("R-FL-GATE-SCORP", "FL_RULE_12C_1_022", "primary", "12C-1.022(1)(b)1 verbatim — liable for the federal tax"),
    ("R-FL-GATE-SCORP", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.2 'Line 23c of federal Form 1120S'; p.5 corporate-level income only"),
    ("R-FL-GATE-SCORP", "FL_FS_CH220_2025", "secondary", "s. 220.13(2)(i) Sec.1374/Sec.1375 base — the W3 tension"),
    ("R-FL-GATE-FOREIGN", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.1 foreign corporate partner must file F-1120"),
    ("R-FL-GATE-FOREIGN", "FL_RULE_12C_1_022", "primary", "12C-1.022(2)(e) K-1 attachment; (6)(g) dual filing"),
    ("R-FL-GATE-TRUST", "FL_TIP_25C01_01", "primary", "charitable trusts stop filing STARTING WITH TAX YEAR 2026"),
    ("R-FL-GATE-TRUST", "FL_RULE_12C_1_022", "secondary", "the charitable-trust exclusion was adopted EFFECTIVE 1/1/2026"),
    ("R-FL-L1-NOSILENT", "FL_TIP_25C01_01", "primary", "DOR's boxed notice: OBBBA is not addressed for TY2025"),
    ("R-FL-L1-NOSILENT", "FL_RULE_12C_1_013_NEG", "primary", "the recompute has no home — 12C-1.013 unamended since 10/27/2022"),
    ("R-FL-L1-NOSILENT", "FL_FS_220_03_CONFORMITY", "primary", "s. 220.03(1)(n) static 1/1/2025 conformity; (3) not self-executing"),
    ("R-FL-L1-NOSILENT", "FL_2025_F1120N_INSTR", "secondary", "F-1120N p.5: Line 1 = federal 1120 Line 30 AS FILED"),
    ("R-FL-FISCAL-BLOCK", "FL_FS_220_03_CONFORMITY", "primary", "ch. 2026-137 s. 3(1) retroactivity clause — the unresolved straddle"),
    ("R-FL-FISCAL-BLOCK", "FL_TIP_25C01_01", "secondary", "TY2025 conformity posture the straddle would disturb"),
    ("R-FL-SPINE", "FL_2025_F1120_FORM", "primary", "form face Lines 1-19 verbatim"),
    ("R-FL-SCHI", "FL_2025_F1120_FORM", "primary", "Schedule I Lines 1-26 verbatim labels"),
    ("R-FL-SCHI", "FL_2025_F1120N_INSTR", "primary", "F-1120N pp.6-8 line-by-line instructions incl. the L25 named examples"),
    ("R-FL-SCHI-CREDITS", "FL_2025_F1120N_INSTR", "primary", "F-1120N pp.6-7: each of L7-L20 reads an INDIVIDUAL Schedule V line"),
    ("R-FL-SCHI-CREDITS", "FL_2025_F1120_FORM", "primary", "Sch V L25 cap lands on the TOTAL only — the circle does not close"),
    ("R-FL-SCHII", "FL_2025_F1120_FORM", "primary", "Schedule II Lines 1-13 verbatim; the Sch II/Sch IV fork on the form face"),
    ("R-FL-SCHII", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.8 incl. the FICA-tip 'rule says no' header note"),
    ("R-FL-BONUS", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.7 L21 / p.8 L9 verbatim — 1/7 over seven years + the QIP split"),
    ("R-FL-BONUS", "FL_FS_CH220_2025", "primary", "s. 220.13(1)(e)1 and 1.b; PIS window 12/31/2007-1/1/2027"),
    ("R-FL-BONUS", "FL_FS_220_03_CONFORMITY", "secondary", "the pre-OBBBA 40% bonus percentage that makes the vintage table diverge from the 4562"),
    ("R-FL-QIP", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.7 L22 anti-double-count / p.8 L10 hypothetical 1/1/2020 IRC without CARES"),
    ("R-FL-QIP", "FL_FS_CH220_2025", "primary", "s. 220.13(1)(e)1.c — the statutory QIP carve-out from the 1/7 track"),
    ("R-FL-179-NOADDBK", "FL_FS_CH220_2025", "primary", "s. 220.13(1)(e)2 expired after TY2014 by its own terms — 'the rule says no'"),
    ("R-FL-179-NOADDBK", "FL_FS_220_03_CONFORMITY", "primary", "1/1/2025 conformity fixes the PRE-OBBBA $1.25M/$3.13M/$31.3k figures"),
    ("R-FL-179-NOADDBK", "FL_2025_F1120_FORM", "secondary", "exhaustive search: '179' appears nowhere on the form or instructions"),
    ("R-FL-MEALS-181", "FL_2025_F1120N_INSTR", "primary", "both windows verbatim: TYs beginning on/after 1/1/2021 and before 1/1/2026"),
    ("R-FL-APPORT-GATE", "FL_RULE_12C_1_015", "primary", "12C-1.015(1)-(2): no throwback, but a gate failure taxes 100%"),
    ("R-FL-APPORT-GATE", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.9: sales-only out-of-state presence does not establish doing business"),
    ("R-FL-APPORT", "FL_FS_CH220_2025", "primary", "s. 220.15(1) verbatim — 25/25/50 in the statute itself"),
    ("R-FL-APPORT", "FL_2025_F1120N_INSTR", "primary", "F-1120N pp.9-11: weights, sourcing, 8x net annual rent, original cost"),
    ("R-FL-APPORT", "FL_2025_F1120_FORM", "secondary", "Schedule III-A/B/C column layout and six-decimal rounding"),
    ("R-FL-APPORT", "FL_RULE_12C_1_015", "secondary", "12C-1.015(10) partnership factor attribution (NOT the weights — that rule is stale)"),
    ("R-FL-APPORT-ZERO", "FL_FS_CH220_2025", "primary", "s. 220.15(1): 'determined by the department to be insignificant'"),
    ("R-FL-APPORT-ZERO", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.9 zero-factor note — the three reweighting cases"),
    ("R-FL-SCHIV", "FL_2025_F1120_FORM", "primary", "Schedule IV Lines 1-9; the fork printed on the Schedule II face"),
    ("R-FL-SCHIV", "FL_2025_F1120N_INSTR", "primary", "F-1120N pp.4, 8 — the fork stated twice more"),
    ("R-FL-NOL", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.4: two-tier 100%/80%, mandatory order, no carryback, p.16 examples"),
    ("R-FL-EXEMPT", "FL_FS_CH220_2025", "primary", "s. 220.14 — the $50,000 exemption"),
    ("R-FL-EXEMPT", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.5: lesser-of, zero floor, Sec.1563 group, short-year x days/365"),
    ("R-FL-TAX", "FL_2025_F1120_FORM", "primary", "form face Line 11 verbatim 'Tax due: 5.5% of Line 10'"),
    ("R-FL-TAX", "FL_FS_CH220_2025", "primary", "s. 220.11(2)(a) '5 1/2 percent'; s. 220.1105 fixes 5.5% from 1/1/2022"),
    ("R-FL-SCHV", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.11: s. 220.02(8) ordering; p.1 the TY2025 Rural Community Investment credit"),
    ("R-FL-SCHV", "FL_2025_F1120_FORM", "primary", "Schedule V Lines 1-25 and the L25 cap at Page 1 Line 11"),
    ("R-FL-SCHR", "FL_FS_CH220_2025", "primary", "s. 220.16 — nonbusiness income is allocated, not apportioned"),
    ("R-FL-SCHR", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.15 definition and the functionally-related-dividends presumption"),
    ("R-FL-PAYMENTS", "FL_2025_F1120_FORM", "primary", "Lines 14-19 and the payment coupon; the blank-Line-19 trap"),
    ("R-FL-PAYMENTS", "FL_2025_F1120N_INSTR", "secondary", "F-1120N pp.2-3 penalty schedule; s. 220.807 floating interest"),
    ("R-FL-DUEDATE", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.2 later-of due date, June-30 carve-out, F-7004 voiding rules"),
    ("R-FL-ESTTAX", "FL_2025_F1120N_INSTR", "primary", "F-1120N p.3 $2,500 threshold, four equal installments, F-2220 safe harbours"),
]


# ── F-1120 lines: page 1 face, then Schedules I / II / III / IV / V / R ──
FL1120_LINES: list[dict] = [
    {"line_number": "1", "description": "Federal taxable income (see instructions). Attach pages 1-6 of federal return.", "line_type": "input",
     "source_facts": ["federal_taxable_income", "fti_pre_obbba_confirmed"], "source_rules": ["R-FL-L1-NOSILENT"], "sort_order": 1,
     "notes": "DIRECT-ENTRY ONLY. Federal 1120 Line 30 basis; S corps enter only corporate-level taxed income. NEVER SILENTLY RECOMPUTED FOR OBBBA (W1)."},
    {"line_number": "2", "description": "State income taxes deducted in computing federal taxable income (attach schedule)", "line_type": "input",
     "source_facts": ["state_income_taxes_deducted"], "sort_order": 2},
    {"line_number": "3", "description": "Additions to federal taxable income (from Schedule I)", "line_type": "calculated",
     "calculation": "Schedule I Line 26", "source_rules": ["R-FL-SCHI"], "sort_order": 3},
    {"line_number": "4", "description": "Total of Lines 1, 2, and 3", "line_type": "subtotal", "source_rules": ["R-FL-SPINE"], "sort_order": 4},
    {"line_number": "5", "description": "Subtractions from federal taxable income (from Schedule II)", "line_type": "calculated",
     "calculation": "Schedule II Line 13", "source_rules": ["R-FL-SCHII"], "sort_order": 5},
    {"line_number": "6", "description": "Adjusted federal income (Line 4 minus Line 5)", "line_type": "subtotal", "source_rules": ["R-FL-SPINE"], "sort_order": 6},
    {"line_number": "7", "description": "Florida portion of adjusted federal income (see instructions)", "line_type": "calculated",
     "calculation": "100% Florida -> = Line 6; doing business outside Florida -> Schedule IV Line 9",
     "source_rules": ["R-FL-APPORT-GATE", "R-FL-SCHIV"], "sort_order": 7,
     "notes": "GATE FAILURE COSTS 100%: if not doing business within AND without Florida, Line 7 = Line 6 in full (Rule 12C-1.015(2))."},
    {"line_number": "8", "description": "Nonbusiness income allocated to Florida (from Schedule R)", "line_type": "calculated",
     "calculation": "Schedule R Line 1; 100% Florida -> 0", "source_rules": ["R-FL-SCHR"], "sort_order": 8},
    {"line_number": "9", "description": "Florida exemption", "line_type": "calculated",
     "calculation": "lesser of $50,000 or (Line 7 + Line 8); zero if that sum <= 0", "source_rules": ["R-FL-EXEMPT"], "sort_order": 9},
    {"line_number": "10", "description": "Florida net income (Line 7 plus Line 8 minus Line 9). If a loss, enter zero.", "line_type": "subtotal",
     "source_rules": ["R-FL-TAX"], "sort_order": 10},
    {"line_number": "11", "description": "Tax due: 5.5% of Line 10", "line_type": "calculated", "calculation": "0.055 x Line 10",
     "source_rules": ["R-FL-TAX"], "sort_order": 11},
    {"line_number": "12", "description": "Credits against the tax (from Schedule V)", "line_type": "calculated",
     "calculation": "Schedule V Line 25, capped at Line 11; cannot create a refund", "source_rules": ["R-FL-SCHV"], "sort_order": 12},
    {"line_number": "13", "description": "Total corporate income/franchise tax due (Line 11 minus Line 12)", "line_type": "subtotal",
     "source_rules": ["R-FL-TAX"], "sort_order": 13},
    {"line_number": "14", "description": "a) Penalty: F-2220 b) Other c) Interest: F-2220 d) Other - Line 14 Total", "line_type": "input",
     "source_facts": ["l14a_penalty_f2220", "l14b_penalty_other", "l14c_interest_f2220", "l14d_interest_other"],
     "source_rules": ["R-FL-PAYMENTS"], "sort_order": 14},
    {"line_number": "15", "description": "Total of Lines 13 and 14", "line_type": "subtotal", "source_rules": ["R-FL-PAYMENTS"], "sort_order": 15},
    {"line_number": "16", "description": "Payment credits: Estimated tax payments 16a / Tentative tax payment 16b", "line_type": "input",
     "source_facts": ["l16a_estimated_payments", "l16b_tentative_payment"], "source_rules": ["R-FL-PAYMENTS"], "sort_order": 16},
    {"line_number": "17", "description": "Total amount due: Subtract Line 16 from Line 15. If negative (overpayment), enter on Line 18 and/or Line 19.",
     "line_type": "total", "source_rules": ["R-FL-PAYMENTS"], "sort_order": 17},
    {"line_number": "18", "description": "Credit: amount of overpayment credited to next year's estimated tax (IRREVOCABLE)", "line_type": "input",
     "source_facts": ["l18_credit_to_next_year"], "source_rules": ["R-FL-PAYMENTS"], "sort_order": 18},
    {"line_number": "19", "description": "Refund: amount of overpayment to be refunded. IF LEFT BLANK THE ENTIRE OVERPAYMENT IS CREDITED FORWARD.",
     "line_type": "input", "source_facts": ["l19_refund_requested"], "source_rules": ["R-FL-PAYMENTS"], "sort_order": 19},
    # Schedule III-A / III-B / III-C / III-D
    {"line_number": "SchIII-A-1", "description": "Property factor (Schedule III-B Line 8) - Column (d) weight X 25% or ______", "line_type": "calculated",
     "source_rules": ["R-FL-APPORT", "R-FL-APPORT-ZERO"], "sort_order": 300},
    {"line_number": "SchIII-A-2", "description": "Payroll factor - Column (d) weight X 25% or ______", "line_type": "calculated",
     "source_facts": ["payroll_fl", "payroll_everywhere"], "source_rules": ["R-FL-APPORT", "R-FL-APPORT-ZERO"], "sort_order": 301},
    {"line_number": "SchIII-A-3", "description": "Sales factor (Schedule III-C Line 4) - Column (d) weight X 50% or ______", "line_type": "calculated",
     "source_rules": ["R-FL-APPORT", "R-FL-APPORT-ZERO"], "sort_order": 302},
    {"line_number": "SchIII-A-4", "description": "Apportionment fraction (sum of Lines 1, 2 and 3, Column [e]), six decimals. Enter here and on Schedule IV, Line 2.",
     "line_type": "total", "source_rules": ["R-FL-APPORT"], "sort_order": 303},
    {"line_number": "SchIII-B-6", "description": "Average value of property: 6a = (L5 col a + col b)/2 Florida; 6b = (L5 col c + col d)/2 everywhere",
     "line_type": "calculated", "source_facts": ["property_fl_beginning", "property_fl_ending",
                                                 "property_everywhere_beginning", "property_everywhere_ending"],
     "source_rules": ["R-FL-APPORT"], "sort_order": 310, "notes": "Owned property at ORIGINAL COST, without regard to accumulated depreciation."},
    {"line_number": "SchIII-B-7", "description": "Rented property (8 times net annual rent) - 7a Florida / 7b everywhere", "line_type": "calculated",
     "source_facts": ["rented_property_fl_net_rent", "rented_property_ew_net_rent"], "source_rules": ["R-FL-APPORT"], "sort_order": 311},
    {"line_number": "SchIII-B-8", "description": "Total (Lines 6 and 7): 8a -> Sch III-A L1 col (a); 8b -> Sch III-A L1 col (b)", "line_type": "subtotal",
     "source_rules": ["R-FL-APPORT"], "sort_order": 312},
    {"line_number": "SchIII-C-4", "description": "TOTAL SALES (enter on Schedule III-A, Line 3, Columns [a] and [b])", "line_type": "subtotal",
     "source_facts": ["sales_fl", "sales_everywhere"], "source_rules": ["R-FL-APPORT"], "sort_order": 320,
     "notes": "TPP sourced to DESTINATION; services where PERFORMED; rentals where the property is located. Gross receipts without regard to returns or allowances."},
    {"line_number": "SchIII-D-1", "description": "Insurance companies special fraction (attach Schedule T-Annual Report) - RED-defer R9", "line_type": "input",
     "source_facts": ["special_fraction_type"], "sort_order": 330,
     "notes": "III-D BYPASSES III-A entirely and feeds Schedule IV Line 2 directly; the form prints N/A in the weight cells."},
    {"line_number": "SchIII-D-2", "description": "Transportation services: Florida revenue miles / everywhere revenue miles (single factor) - RED-defer R9",
     "line_type": "input", "source_facts": ["special_fraction_type"], "sort_order": 331},
    # Schedule IV
    {"line_number": "SchIV-1", "description": "Apportionable adjusted federal income from Page 1, Line 6", "line_type": "calculated",
     "source_rules": ["R-FL-SCHIV"], "sort_order": 340},
    {"line_number": "SchIV-2", "description": "Florida apportionment fraction (Schedule III-A, Line 4, or Schedule III-D Column [c])", "line_type": "calculated",
     "source_rules": ["R-FL-SCHIV"], "sort_order": 341},
    {"line_number": "SchIV-3", "description": "Tentative apportioned adjusted federal income (multiply Line 1 by Line 2)", "line_type": "subtotal",
     "source_rules": ["R-FL-SCHIV"], "sort_order": 342},
    {"line_number": "SchIV-4", "description": "Net operating loss carryover apportioned to Florida (attach schedule)", "line_type": "input",
     "source_facts": ["schiv_l4_nol_apportioned"], "source_rules": ["R-FL-NOL"], "sort_order": 343},
    {"line_number": "SchIV-5", "description": "Net capital loss carryover apportioned to Florida (attach schedule)", "line_type": "input",
     "source_facts": ["schiv_l5_capital_loss_appt"], "source_rules": ["R-FL-SCHIV"], "sort_order": 344},
    {"line_number": "SchIV-6", "description": "Excess charitable contribution carryover apportioned to Florida (attach schedule)", "line_type": "input",
     "source_facts": ["schiv_l6_charitable_appt"], "source_rules": ["R-FL-SCHIV"], "sort_order": 345},
    {"line_number": "SchIV-7", "description": "Employee benefit plan contribution carryover apportioned to Florida (attach schedule)", "line_type": "input",
     "source_facts": ["schiv_l7_emp_benefit_appt"], "source_rules": ["R-FL-SCHIV"], "sort_order": 346},
    {"line_number": "SchIV-8", "description": "Total carryovers apportioned to Florida (add Lines 4 through 7)", "line_type": "subtotal",
     "source_rules": ["R-FL-SCHIV"], "sort_order": 347},
    {"line_number": "SchIV-9", "description": "Adjusted federal income apportioned to Florida (Line 3 less Line 8) -> Page 1 Line 7", "line_type": "total",
     "source_rules": ["R-FL-SCHIV"], "sort_order": 348},
    # Schedule R
    {"line_number": "SchR-1", "description": "Nonbusiness income (loss) allocated to Florida (Type / Amount) -> Page 1, Line 8", "line_type": "input",
     "source_facts": ["schr_l1_nonbusiness_fl"], "source_rules": ["R-FL-SCHR"], "sort_order": 360},
    {"line_number": "SchR-2", "description": "Nonbusiness income (loss) allocated elsewhere (Type / State or country / Amount)", "line_type": "input",
     "source_facts": ["schr_l2_nonbusiness_other"], "source_rules": ["R-FL-SCHR"], "sort_order": 361},
    {"line_number": "SchR-3", "description": "Total nonbusiness income - Grand total. Total of Lines 1 and 2 -> Schedule II, Line 7", "line_type": "total",
     "source_rules": ["R-FL-SCHR"], "sort_order": 362,
     "notes": "THE ASYMMETRY: Line 1 (Florida only) is ADDED at Page 1 Line 8; Line 3 (Florida + elsewhere) is SUBTRACTED at Schedule II Line 7."},
]

# Schedule I / II / V lines generated from the verbatim label tables.
for _n, _label, _fk in SCHI_LABELS:
    _rules = ["R-FL-SCHI"]
    if _n in SCHI_CREDIT_ADDBACK_MAP:
        _rules = ["R-FL-SCHI-CREDITS"]
    elif _n == 21:
        _rules = ["R-FL-BONUS"]
    elif _n == 22:
        _rules = ["R-FL-QIP"]
    elif _n in (23, 24):
        _rules = ["R-FL-MEALS-181"]
    FL1120_LINES.append({
        "line_number": f"SchI-{_n}", "description": _label,
        "line_type": ("total" if _n == 26 else ("calculated" if _fk is None else "input")),
        "source_facts": ([_fk] if _fk else []), "source_rules": _rules, "sort_order": 100 + _n,
        "notes": (f"<- {SCHI_CREDIT_ADDBACK_MAP[_n]} (single pass, as entered, before the L25 cap - W2)"
                  if _n in SCHI_CREDIT_ADDBACK_MAP else
                  ("MUST be tagged QIP vs non-QIP at entry (schi_l21_bonus_qip_portion) - the halves recover on different lines"
                   if _n == 21 else
                   ("Excludes QIP bonus already added back on Line 21 (anti-double-count)" if _n == 22 else
                    ("Expires for TYs beginning on/after 1/1/2026 - TY2026 firewall" if _n in (23, 24) else
                     ("PROPOSED landing zone for the TY2025 OBBBA recompute addition, pending W1" if _n == 25 else ""))))),
    })
for _n, _label, _fk in SCHII_LABELS:
    _rules = ["R-FL-SCHII"]
    if _n == 9:
        _rules = ["R-FL-BONUS"]
    elif _n == 10:
        _rules = ["R-FL-QIP"]
    elif _n == 11:
        _rules = ["R-FL-MEALS-181"]
    elif _n == 3:
        _rules = ["R-FL-NOL"]
    elif _n == 7:
        _rules = ["R-FL-SCHR"]
    FL1120_LINES.append({
        "line_number": f"SchII-{_n}", "description": _label[:400],
        "line_type": ("total" if _n == 13 else ("calculated" if _fk is None else "input")),
        "source_facts": ([_fk] if _fk else []), "source_rules": _rules, "sort_order": 200 + _n,
        "notes": ("1/7 of each open NON-QIP vintage over seven years, beginning with the year of the addition" if _n == 9 else
                  ("Hypothetical 1/1/2020-IRC-without-CARES depreciation, IGNORING disposition; recovers Sch I L22 AND the QIP portion of L21" if _n == 10 else
                   ("ZERO when doing business outside Florida - carryovers move to Schedule IV (the fork)" if _n in (3, 4, 5, 6) else
                    ("<- Schedule R Line 3 (Florida AND elsewhere)" if _n == 7 else
                     ("PROPOSED landing zone for the TY2025 OBBBA recompute subtraction, pending W1" if _n == 12 else ""))))),
    })
for _n, _label, _fk in SCHV_LABELS:
    FL1120_LINES.append({
        "line_number": f"SchV-{_n}", "description": _label[:400],
        "line_type": ("total" if _n == 25 else "input"),
        "source_facts": ([_fk] if _fk else []), "source_rules": ["R-FL-SCHV"], "sort_order": 400 + _n,
        "notes": ("Capped at Page 1 Line 11; cannot create a refund. THE CAP LANDS HERE ONLY, not on the individual lines (W2)."
                  if _n == 25 else
                  ("RED-defer R4 - pre-2018 Florida AMT carryforward with a multi-schedule limit formula" if _n == 8 else
                   ("NEW for TY2025: 25% of the investor contribution; 20% per year over the 1st-5th certification years" if _n == 16 else
                    ("FLAHIGA assessment credit rides here and adds back on Schedule I Line 8" if _n == 24 else
                     ("Statutory s. 220.02(8) order; DOR pre-allocation or third-party certificate required" ))))),
    })


FL1120_DIAGNOSTICS: list[dict] = [
    # ══════════════ THE GATE — positive determinations, never silence
    {"diagnostic_id": "D_FL1120_GATE_NO_RETURN", "title": "No Florida return required - explicit determination", "severity": "info",
     "condition": "R-FL-GATE-1120 evaluates file_F1120 = False",
     "message": ("No Florida corporate income/franchise tax return is required for this entity. Reason and "
                 "citation are recorded with the determination. This is a POSITIVE OUTPUT, not silence - "
                 "Florida's default is that most pass-throughs file NOTHING, and generating a return "
                 "because a federal return exists produces wrong output for the majority of Florida entities."),
     "notes": "s. 220.22 + Rule 12C-1.022. Never suppress this - the preparer must see the reason."},
    {"diagnostic_id": "D_FL1120_GATE_SCORP_23C", "title": "S corporation: F-1120 required only when 1120S Line 23c > 0", "severity": "warning",
     "condition": "entity_classification = s_corp",
     "message": ("An S corporation files Florida Form F-1120 ONLY for taxable years when it is liable for "
                 "federal tax - i.e. when federal Form 1120S Line 23c is greater than zero (Rule "
                 "12C-1.022(1)(b)1; F-1120N p.2). If it files, Line 1 carries ONLY the income subject to "
                 "federal income tax at the corporate level. Attach the IRS Notice of Acceptance as an S "
                 "corporation if it has not been sent to the Department. A non-liable S corporation MAY "
                 "still file to claim a refund of Florida payment credits."),
     "notes": "The non-filing is a rule-based exemption under s. 220.22(4), not a statutory vacuum."},
    {"diagnostic_id": "D_FL1120_W3_LIFO_RECAPTURE", "title": "W3 UNRESOLVED: Line 23c is LIFO recapture only", "severity": "error",
     "condition": "fed_1120s_line_23c > 0 AND fed_1120s_lifo_recapture_only",
     "message": ("The entire federal 1120S Line 23c amount is LIFO RECAPTURE TAX. The filing trigger (Rule "
                 "12C-1.022(1)(b)1 and F-1120N p.2) keys on federal liability / Line 23c, but s. "
                 "220.13(2)(i) defines an S corporation's Florida taxable income as the amounts subject to "
                 "tax under Sec.1374 or Sec.1375 ONLY - which does not include LIFO recapture. This filer "
                 "appears to owe a return with a ZERO Florida base. UNRESOLVED - do not proceed without a "
                 "ruling. '1374' and '1375' appear nowhere on any Florida form or instruction."),
     "notes": "W3. Settle via Rule 12C-1.013 / 12C-1.022 read for a Sec.1374/Sec.1375 definition, or a DOR reply."},
    {"diagnostic_id": "D_FL1120_GATE_FOREIGN_PTR", "title": "Foreign corporate partner: a SECOND Florida return is required", "severity": "warning",
     "condition": "is_fl_partnership_member AND the corporation is organized outside Florida",
     "message": ("A foreign (out-of-state) corporation that is a partner in a Florida partnership or a "
                 "member of a Florida joint venture IS SUBJECT TO THE FLORIDA INCOME TAX CODE AND MUST "
                 "FILE FORM F-1120 (F-1120N p.1). Attach federal Schedule K-1 (Form 1065) (Rule "
                 "12C-1.022(2)(e)). NOTE: one Florida partnership with one out-of-state corporate partner "
                 "generates TWO Florida returns - the partnership's F-1065 AND this F-1120 "
                 "(Rule 12C-1.022(6)(g))."),
     "notes": "A COMMON MISS and a real nexus trigger."},
    {"diagnostic_id": "D_FL1120_GATE_CHAR_TRUST", "title": "W8: charitable trusts DO file F-1120 for TY2025", "severity": "warning",
     "condition": "entity_classification = charitable_trust AND tax year begins before 1/1/2026",
     "message": ("A charitable trust IS required to file Florida Form F-1120 for TY2025. THE 2025 EDITION "
                 "OF s. 220.03(1)(e) ALREADY PRINTS 'charitable trusts' IN THE EXCLUSION LIST, so reading "
                 "the statute alone gives the WRONG ANSWER: the exclusion added by ch. 2025-208 applies "
                 "only to tax years beginning on or after January 1, 2026, and Rule 12C-1.022's "
                 "charitable-trust amendment was adopted EFFECTIVE 1/1/2026. Charitable trusts stop filing "
                 "STARTING WITH TAX YEAR 2026 (TIP 25C01-01)."),
     "notes": "W8. Confirm the TY2025 behaviour and the TY2026 flip date are both encoded."},
    {"diagnostic_id": "D_FL1120_GATE_1120H", "title": "Federal Form 1120-H: no Florida return required", "severity": "info",
     "condition": "federal_return_type = 1120-H",
     "message": ("A homeowner association filing federal Form 1120-H files NO Florida return - 'the rule "
                 "says no', stated in terms at F-1120N pp.1-2. But an association filing federal Form 1120 "
                 "MUST file F-1120 REGARDLESS of whether any tax may be due."),
     "notes": "The 1120 / 1120-H fork is a clean, stated rule - encode both directions."},
    {"diagnostic_id": "D_FL1120_NO_TAX_STILL_FILE", "title": "A no-tax-due return still must be filed", "severity": "warning",
     "condition": "file_F1120 = True AND Line 13 = 0",
     "message": ("'You must file a return, even if no tax is due' (F-1120N p.2). A late-filed no-tax "
                 "return still draws $50 per month up to $300."),
     "notes": "Rule 12C-1.022(1)(a): the burden is on the corporation to establish it need not file."},
    # ══════════════ W1 / W5 — the blocking pair
    {"diagnostic_id": "D_FL1120_W1_NO_SILENT_RECALC", "title": "BLOCKING: Line 1 pre-OBBBA figure not confirmed", "severity": "error",
     "condition": "fti_pre_obbba_confirmed is not True",
     "message": ("Line 1 must carry federal taxable income RECOMPUTED UNDER THE PRE-OBBBA CODE. Florida's "
                 "TY2025 IRC conformity date is January 1, 2025 (s. 220.03(1)(n)), so OBBBA (P.L. 119-21, "
                 "enacted 7/4/2025) IS NOT ADOPTED FOR TY2025. DELVIO DOES NOT AND WILL NOT COMPUTE THIS "
                 "RECOMPUTE. Confirm that the figure entered on Line 1 is the pre-OBBBA amount and attach "
                 "supporting detail."),
     "notes": "W1. A HARD BLOCK. Do not relax this to a warning."},
    {"diagnostic_id": "D_FL1120_R2_OBBBA_RECOMPUTE", "title": "RED-DEFER R2: the TY2025 pre-OBBBA recompute has NO HOME on the return", "severity": "error",
     "condition": "always, for any TY2025 Florida F-1120",
     "message": ("Florida does not adopt OBBBA for TY2025. Federal taxable income at Line 1 must be "
                 "recomputed under the pre-OBBBA Code - but NO LINE, SCHEDULE, INSTRUCTION, TIP OR RULE "
                 "CARRIES THAT RECOMPUTE. Verified exhaustively: nine OBBBA-related strings return ZERO "
                 "relevant hits across all six TY2025 documents; Rule 12C-1.013 ('Adjusted Federal Income "
                 "Defined') has not been amended since 10/27/2022; no TIP addresses TY2025; and the TY2026 "
                 "DRAFT F-1120 has no such line either. DELVIO DOES NOT COMPUTE THE RECOMPUTE - ENTER THE "
                 "RECOMPUTED FIGURE AND ATTACH SUPPORTING DETAIL. Schedule I Line 25 / Schedule II Line 12 "
                 "are the PROPOSED landing zone ONLY, pending Ken's ruling; NO DOR INSTRUCTION NAMES OBBBA "
                 "AS AN EXAMPLE THERE."),
     "notes": "W1 - the wave's biggest call and it GATES THIS LOADER. No line was invented."},
    {"diagnostic_id": "D_FL1120_R1_FISCAL_STRADDLE", "title": "RED-DEFER R1 / HARD BLOCK: fiscal TY2025 straddling 1/1/2026", "severity": "error",
     "condition": "tax_year_begin < 2026-01-01 AND tax_year_end >= 2026-01-01",
     "message": ("Florida fiscal-year returns are NOT SUPPORTED for TY2025. The applicable IRC conformity "
                 "date for a tax year ending in 2026 is UNRESOLVED: ch. 2026-137 s. 3(1) says the "
                 "amendments 'operate retroactively to January 1, 2026' - it does NOT say 'for tax years "
                 "beginning on or after.' A different answer means a different Line 1 recompute AND a "
                 "different Sec.179 limit. PREPARE MANUALLY."),
     "notes": "W5. HARD BLOCK, not a warning. June-30 FYE filers are structurally common in Florida."},
    # ══════════════ Depreciation
    {"diagnostic_id": "D_FL1120_QIP_TAG_REQUIRED", "title": "Schedule I Line 21 must be split QIP vs non-QIP", "severity": "error",
     "condition": "schi_l21_bonus_depreciation > 0 AND schi_l21_bonus_qip_portion is unset",
     "message": ("The Schedule I Line 21 bonus-depreciation addition MUST be tagged QIP vs non-QIP at "
                 "entry. The two halves recover on DIFFERENT LINES under DIFFERENT FORMULAS: the non-QIP "
                 "half recovers 1/7 per year over seven years on Schedule II Line 9, while the QIP half "
                 "recovers on Schedule II Line 10 as hypothetical 1/1/2020-IRC-without-CARES depreciation. "
                 "The Line 9 attached schedule expressly demands the QIP figure as a separate line. "
                 "NEITHER HALF IS DERIVABLE FROM THE FEDERAL FORM 4562."),
     "notes": "s. 220.13(1)(e)1.c carves QIP bonus out of the 1/7 track."},
    {"diagnostic_id": "D_FL1120_BONUS_7YR_SCHED", "title": "Sec.168(k) 7-year vintage schedule is NOT derivable from the federal 4562", "severity": "warning",
     "condition": "schi_l21_bonus_depreciation > 0 OR bonus_addition_vintages is set",
     "message": ("Attach a schedule showing the taxable year and amount of EACH original addition, the "
                 "portion of each addition attributable to qualified improvement property placed in "
                 "service on or after 1/1/2018, and the subtraction by taxable year. Because Florida's "
                 "TY2025 Code is the 1/1/2025 Code, the bonus percentage used for the Florida computation "
                 "is the PRE-OBBBA 40% for property placed in service in calendar 2025 - NOT OBBBA's 100%. "
                 "THE FLORIDA ADDITION AND ITS SEVEN-YEAR RECOVERY SCHEDULE THEREFORE DIFFER FROM THE "
                 "FEDERAL FORM 4562 WHENEVER OBBBA 100% BONUS WAS CLAIMED FEDERALLY. This is the "
                 "highest-risk silent-wrong-answer path in the Florida build."),
     "notes": "Multi-year state required: a 7-vintage rolling schedule per addition year."},
    {"diagnostic_id": "D_FL1120_QIP_IGNORE_DISPOSAL", "title": "QIP recovery IGNORES sale or disposition", "severity": "info",
     "condition": "schi_l22_qip_depreciation > 0 OR schi_l21_bonus_qip_portion > 0",
     "message": ("The Schedule II Line 10 subtraction is limited to the depreciation that would have been "
                 "allowed under the IRC IN EFFECT ON JANUARY 1, 2020, WITHOUT the retroactive CARES Act "
                 "change (i.e. QIP as 39-year nonresidential real property, not 15-year), AND WITHOUT "
                 "TAKING INTO ACCOUNT ANY SALE OR OTHER DISPOSITION of the property - so the shadow "
                 "schedule KEEPS RUNNING AFTER THE ASSET IS SOLD."),
     "notes": "A shadow depreciation book, not a fraction."},
    {"diagnostic_id": "D_FL1120_179_NO_ADDBACK", "title": "Sec.179: THERE IS NO FLORIDA ADD-BACK - 'the rule says no'", "severity": "info",
     "condition": "always, whenever Sec.179 expensing appears in the federal return",
     "message": ("DO NOT CREATE A FLORIDA Sec.179 ADD-BACK. The add-back in s. 220.13(1)(e)2 EXPIRED BY "
                 "ITS OWN TERMS after tax years beginning before January 1, 2015. The string '179' does "
                 "not occur anywhere in F-1120 R. 01/26, F-1120N R. 01/26, F-1065/F-1065N R. 01/24 or "
                 "F-1120A R. 01/24 - no line, no instruction, no footnote. Sec.179 enters Florida ONLY "
                 "through federal taxable income at Line 1."),
     "notes": "An AFFIRMATIVE legal exclusion, not a silence. Encoded so nobody later 'helpfully' adds an add-back."},
    {"diagnostic_id": "D_FL1120_179_PRE_OBBBA_LIMIT", "title": "Florida TY2025 Sec.179 limit is the PRE-OBBBA figure", "severity": "warning",
     "condition": "Sec.179 expensing claimed federally",
     "message": ("Florida's TY2025 Sec.179 limits are the PRE-OBBBA, inflation-indexed amounts fixed by "
                 "the January 1, 2025 conformity date: $1,250,000 expensing limitation, $3,130,000 "
                 "investment phase-out threshold, $31,300 sport utility vehicle sublimit (Rev. Proc. "
                 "2024-40 Sec.2.25). DO NOT USE $2,500,000 / $4,000,000 FOR FLORIDA TY2025."),
     "notes": "The federal OBBBA figures are wrong for Florida TY2025 in both directions."},
    {"diagnostic_id": "D_FL1120_FICA_TIP_NO_SUB", "title": "No FICA-tip subtraction exists - 'the rule says no'", "severity": "info",
     "condition": "federal General Business Credit includes the employer FICA-tip credit",
     "message": ("Florida provides NO subtraction for Social Security and Medicare taxes paid on employee "
                 "tip income taken as a federal General Business Credit: 'Florida Statutes do not provide "
                 "a similar credit...nor is there a provision for a subtraction' (F-1120N p.8, Schedule II "
                 "header). DO NOT BUILD ONE."),
     "notes": "An affirmative exclusion printed on the Schedule II header."},
    # ══════════════ Apportionment
    {"diagnostic_id": "D_FL1120_R3_APPORT_GATE", "title": "RED-DEFER R3: apportionment gate failure taxes 100% of adjusted federal income", "severity": "error",
     "condition": "doing_business_outside_fl claimed AND gate_basis in {pl86272_solicitation_only, de_minimis_only, voluntary_filing_only, none}",
     "message": ("Apportionment requires doing business WITHIN AND WITHOUT Florida (Rule 12C-1.015(1)-(2)). "
                 "Making only sales in another state WITHOUT PROPERTY OR PAYROLL THERE DOES NOT QUALIFY, "
                 "and neither does a de minimis presence or a voluntarily filed out-of-state return. "
                 "IF THE GATE FAILS, 100% OF ADJUSTED FEDERAL INCOME IS TAXABLE IN FLORIDA. Note the "
                 "counter-intuitive structure: Rule 12C-1.015(1)(d) says in terms 'There is no throwback "
                 "rule in Florida', but that protects only taxpayers who have ALREADY CLEARED THE GATE - "
                 "outright denial of apportionment is FUNCTIONALLY MORE ADVERSE THAN THROWBACK. CONFIRM "
                 "BEFORE APPORTIONING. A non-Florida state of incorporation clears the gate on its own "
                 "(Rule 12C-1.015(1)(b)1)."),
     "notes": "W7. The single most adverse silent outcome in the Florida build."},
    {"diagnostic_id": "D_FL1120_INSIGNIFICANT_DEN", "title": "W4: small-but-nonzero denominator - only the DEPARTMENT may deem it insignificant", "severity": "warning",
     "condition": "any Column (b) denominator is small relative to the others but NOT exactly zero",
     "message": ("A factor denominator is small but NOT zero. s. 220.15(1) reweights where a denominator "
                 "'is zero OR IS DETERMINED BY THE DEPARTMENT TO BE INSIGNIFICANT.' INSIGNIFICANCE IS THE "
                 "DEPARTMENT'S DETERMINATION, NOT THE PREPARER'S, and it is not self-executing. Delvio "
                 "computes ONLY the zero-denominator branch and will NOT reweight this factor. The "
                 "write-in blank in Schedule III-A Column (d) exists to record a determination the "
                 "Department has ALREADY made. Consult s. 220.15(1) and the Department."),
     "notes": "W4. A question, never a computation."},
    {"diagnostic_id": "D_FL1120_APPORT_ZERO_FACTOR", "title": "Zero-denominator reweighting applied", "severity": "info",
     "condition": "any Schedule III-A Column (b) denominator is exactly zero",
     "message": ("A factor denominator is zero and the statutory reweighting has been applied: any TWO "
                 "factors zero -> the remaining factor 100%; SALES zero -> property and payroll each 50%; "
                 "PROPERTY or PAYROLL zero -> the other 33-1/3% and sales 66-2/3% (s. 220.15(1)(a)-(c); "
                 "F-1120N p.9). Otherwise the weights remain 25% property / 25% payroll / 50% sales."),
     "notes": "The only self-executing branch. Florida is NOT a single-sales-factor state."},
    {"diagnostic_id": "D_FL1120_CARRYOVER_FORK", "title": "Carryovers belong on Schedule II OR Schedule IV, NEVER BOTH", "severity": "error",
     "condition": "any of the four carryovers is nonzero on BOTH Schedule II Lines 3-6 and Schedule IV Lines 4-7",
     "message": ("The four carryovers (Florida NOL, net capital loss, excess charitable contribution, "
                 "employee benefit plan contribution) live on EITHER Schedule II Lines 3-6 (100% Florida) "
                 "OR Schedule IV Lines 4-7 (doing business outside Florida) - NEVER BOTH. 'Taxpayers doing "
                 "business outside Florida enter zero on Lines 3 through 6, and complete Schedule IV' "
                 "(form face; repeated at F-1120N pp.4 and 8). Apply other Florida carryover deductions "
                 "BEFORE the Florida NOLD."),
     "notes": "The single most common structural error on this return."},
    {"diagnostic_id": "D_FL1120_NOL_TWO_TIER", "title": "Florida NOL: pre-2018 at 100% FIRST, then post-2017 at 80% of the remainder", "severity": "warning",
     "condition": "fl_nol_pre2018_carryover > 0 OR fl_nol_post2017_carryover > 0",
     "message": ("Florida allows NO NOL CARRYBACK. Pre-1/1/2018 losses carry forward 20 years and offset "
                 "100% of Florida tentative apportioned adjusted federal income; post-12/31/2017 losses "
                 "carry forward indefinitely and offset 80% OF THE REMAINDER AFTER the pre-2018 "
                 "carryovers are applied. THE ORDER IS MANDATORY. The Florida carryover is limited to the "
                 "federal NOL times the Florida apportionment fraction, and the s. 220.13(1)(e) bonus/QIP "
                 "add-backs may INCREASE it."),
     "notes": "Two worked examples at F-1120N p.16 (one apportioning, one 100%-Florida)."},
    # ══════════════ Credits / circularity
    {"diagnostic_id": "D_FL1120_SCHV_CAP_BINDS", "title": "W2: the Schedule V credit cap binds - the preparer is resolving the circularity", "severity": "warning",
     "condition": "Schedule V Line 25 total equals Page 1 Line 11",
     "message": ("Schedule V total credits equal the Line 11 tax cap. Schedule I Lines 7-20 add back the "
                 "credits claimed on Schedule V, which raises Florida net income, which raises the Line 11 "
                 "cap. Delvio evaluates the add-backs in a SINGLE PASS from the individual Schedule V "
                 "lines as entered, before the Line 25 cap - the literally correct reading, since the cap "
                 "lands only on Line 25 and no Schedule I line reads from Line 25. With the cap binding, "
                 "YOU are resolving the loop by choosing what to enter on each Schedule V line. Most of "
                 "these credits carry forward."),
     "notes": "W2. Neither the form nor F-1120N prescribes an iteration order or a convergence rule."},
    {"diagnostic_id": "D_FL1120_SCHI_SINGLE_PASS", "title": "Schedule I credit add-backs are computed SINGLE PASS (loader convention)", "severity": "info",
     "condition": "any Schedule V credit line 1-24 is nonzero",
     "message": ("Schedule I Lines 7-20 are populated once, from the INDIVIDUAL Schedule V lines as "
                 "entered, before the Line 25 cap. Eight Schedule V credits have NO Schedule I add-back "
                 "and none is generated for them: L2 capital investment, L3 community contribution, L7 "
                 "hazardous waste, L8 Florida AMT, L9 contaminated site, L10 child care, L16 Rural "
                 "Community Investment, L23 individuals with unique abilities."),
     "notes": "W2 ratification item. Schedule I Line 11 also carries an anti-duplication proviso needing prior-year state."},
    {"diagnostic_id": "D_FL1120_R4_AMT_CREDIT", "title": "RED-DEFER R4: Florida AMT credit (Schedule V Line 8) - prepare manually", "severity": "warning",
     "condition": "schv_l08_florida_amt_credit > 0",
     "message": ("Pre-2018 Florida AMT credit carryforward with a multi-schedule limit formula - PREPARE "
                 "MANUALLY. For tax years beginning on or after 1/1/2018 there is NO Florida AMT and no "
                 "additional Florida AMT credit is created. The allowable amount is the lesser of the "
                 "unused carryforward and Line 11 tax less the credits on Lines 1-8 minus 3.3% of the "
                 "amount by which additions (Schedule I Lines 1 and 7 through 25) exceed subtractions "
                 "(Schedule II Lines 3 through 12, plus Schedule IV Line 8 if the apportionment fraction "
                 "is not 100% Florida). Note the formula deliberately EXCLUDES Schedule I Lines 2-6 and "
                 "Schedule II Lines 1-2."),
     "notes": "R4. Rule 12C-1.022(5) still demands a 'Florida alternative minimum tax schedule' - A STALE RULE ARTIFACT. Do not build it."},
    # ══════════════ Remaining RED-defers
    {"diagnostic_id": "D_FL1120_R5_CONSOLIDATED", "title": "RED-DEFER R5: Florida consolidated return - prepare manually", "severity": "warning",
     "condition": "is_florida_consolidated OR is_federal_consolidated with a Florida group election",
     "message": ("A Florida consolidated election requires that the PARENT be subject to the Florida Income "
                 "Tax Code, that the group filed a FEDERAL consolidated return, and that THE FLORIDA GROUP "
                 "BE IDENTICAL TO THE FEDERAL GROUP. F-1122 is required for each member in the initial "
                 "year and for each new member thereafter, with F-851 (or federal 851) attached, and the "
                 "election must be made by the due date including extensions. THE ELECTION IS BINDING FOR "
                 "ALL SUBSEQUENT YEARS even if the parent later ceases to be subject to Florida tax. "
                 "PREPARE MANUALLY."),
     "notes": "R5. s. 220.131; Rule 12C-1.0131. Apportionment gate is tested GROUPWIDE (12C-1.015(7)(b))."},
    {"diagnostic_id": "D_FL1120_R6_163J_CARRYFWD", "title": "RED-DEFER R6: Florida-only Sec.163(j) carryforward - verify manually", "severity": "warning",
     "condition": "has_163j_fl_carryforward",
     "message": ("The Sec.163(j) interest limitation is computed AT THE FILER LEVEL. Florida did not follow "
                 "the CARES Act's temporary increase from 30% to 50% for tax years beginning on or after "
                 "1/1/2019 and before 1/1/2021; any addition required on Florida returns for TY2019-2020 "
                 "is treated as a DISALLOWED BUSINESS INTEREST EXPENSE CARRYFORWARD from prior years. A "
                 "Florida-only carryforward may still be live in TY2025 - VERIFY MANUALLY."),
     "notes": "R6. F-1120N p.5, Line 1 note, verbatim."},
    {"diagnostic_id": "D_FL1120_R7_ELECTION_AB", "title": "RED-DEFER R7: Election A / Election B legacy depreciation - prepare manually", "severity": "warning",
     "condition": "has_election_a_or_b_depr",
     "message": ("Pre-1987 depreciation election adjustment - PREPARE MANUALLY. Taxpayers who made "
                 "'Election A' (s. 220.03(5)(b), assets placed in service 1/1/1981-12/31/1981) or "
                 "'Election B' (s. 220.03(5)(c), 1/1/1981-12/31/1986) still owe a depreciation adjustment "
                 "measured against the IRC OF 1954 AS IN EFFECT 1/1/1980, reported on Schedule I Line 25. "
                 "Vanishingly rare."),
     "notes": "R7. DO NOT BUILD FOR IT; DO NOT ASSERT IT IS GONE."},
    {"diagnostic_id": "D_FL1120_R8_FINANCIAL_ORG", "title": "RED-DEFER R8: financial-organization apportionment - prepare manually", "severity": "warning",
     "condition": "is_financial_organization",
     "message": ("Financial organization apportionment is NOT SUPPORTED - PREPARE MANUALLY. Financial "
                 "organizations have an EXTENDED SALES DEFINITION and must include INTANGIBLE PERSONAL "
                 "PROPERTY (except goodwill) in the PROPERTY FACTOR, valued at FEDERAL TAX BASIS, with a "
                 "detailed 11-item Florida-situs list (F-1120N pp.9-10)."),
     "notes": "R8. Check the client book (W9) before deciding this is theoretical."},
    {"diagnostic_id": "D_FL1120_R9_SPECIAL_APPORT", "title": "RED-DEFER R9: special apportionment formula - prepare manually", "severity": "warning",
     "condition": "special_fraction_type != none",
     "message": ("Special apportionment formula - PREPARE MANUALLY. Insurance companies apportion by direct "
                 "premiums written on Florida properties/risks over everywhere (attach Schedule T-Annual "
                 "Report); transportation service companies use a SINGLE FACTOR of Florida revenue miles "
                 "over everywhere revenue miles; citrus processing companies also carve out. s. 220.153 "
                 "single-sales-factor and s. 220.152 alternative-method treatments require DEPARTMENT "
                 "PERMISSION. Schedule III-D bypasses Schedule III-A entirely and feeds Schedule IV Line 2."),
     "notes": "R9."},
    {"diagnostic_id": "D_FL1120_R11_F1120A", "title": "RED-DEFER R11: F-1120A short form not produced in v1", "severity": "info",
     "condition": "the taxpayer meets the F-1120A eligibility criteria",
     "message": ("Delvio always produces the LONG-FORM F-1120. F-1120A is an optional convenience with no "
                 "computational content the F-1120 lacks. Eligibility requires ALL of: Florida net income "
                 "$45,000 or less; 100% of business conducted in Florida; no additions/subtractions other "
                 "than a net operating loss deduction and/or state income taxes; not part of a Florida or "
                 "federal consolidated return; no credits other than tentative or estimated tax payments; "
                 "and tax due under $2,500. NOTE: the F-1120A R. 01/24 page-1 SCANLINE READS PERIOD 2023 "
                 "(20239999) against F-1120's 20259999 - DO NOT BUILD F-1120A WITHOUT CONFIRMING THE "
                 "SCANLINE WITH DOR."),
     "notes": "R11, strengthened by verification-pass finding C5. A stale period marker breaks a machine-read filing."},
    {"diagnostic_id": "D_FL1120_R12_AMENDED_F2220", "title": "RED-DEFER R12: F-1120X amended and F-2220 underpayment are separate units", "severity": "info",
     "condition": "an amended return is required or an estimated-tax underpayment penalty applies",
     "message": ("F-1120X (R. 01/16) is required if an amended federal return is filed OR a redetermination "
                 "of federal income (e.g. an audit adjustment) affects Florida net income. F-2220 "
                 "(R. 01/25) computes the 12%/yr estimated-tax underpayment penalty. BOTH ARE SEPARATE "
                 "FORM UNITS, OUT OF v1 SCOPE - prepare manually."),
     "notes": "R12."},
    # ══════════════ Filing mechanics
    {"diagnostic_id": "D_FL1120_FED_RETURN_ATTACH", "title": "The federal return is a MANDATORY attachment", "severity": "error",
     "condition": "federal_return_attached is not True",
     "message": ("'This return is considered incomplete unless a copy of the federal return is attached.' "
                 "Attach a copy of the ACTUAL FEDERAL INCOME TAX RETURN FILED WITH THE IRS (pages 1-6), "
                 "plus federal Forms 4562, 851 (or Florida Form F-851), 1122, 1125-A, Schedule D, Schedule "
                 "M-3, and supporting details for Schedules M-1 and M-2. INCOMPLETE-RETURN PENALTY: the "
                 "greater of $300 or 10% of the tax finally determined due, capped at $10,000."),
     "notes": "NOTE the opposite rule for F-1065 and F-1120A: 'Do not attach a copy of the federal return.'"},
    {"diagnostic_id": "D_FL1120_EXTENSION_VOID", "title": "F-7004 extension is VOID on underpayment", "severity": "warning",
     "condition": "an extension path is selected",
     "message": ("A copy of the federal extension ALONE WILL NOT EXTEND the Florida return - Form F-7004 "
                 "must be filed, and 100% of the tax tentatively determined due must be paid by the "
                 "original due date. THE EXTENSION IS VOID IF (1) the tentative tax due is not paid, or "
                 "(2) you underpay by THE GREATER OF $2,000 OR 30% of the tax shown on the F-1120 when "
                 "filed. Six months (SEVEN for a June 30 year end), one extension only. Underpayment of "
                 "tentative tax accrues 12% per year FROM THE ORIGINAL DUE DATE."),
     "notes": "Rule 12C-1.0222. One F-7004 extends F-1120 AND F-1065."},
    {"diagnostic_id": "D_FL1120_REFUND_L19_BLANK", "title": "A blank Line 19 forfeits the refund to next year's estimate", "severity": "warning",
     "condition": "Line 17 shows an overpayment AND Line 19 is blank",
     "message": ("'If Line 19 is left blank, we will credit the entire overpayment to next year's "
                 "estimated tax.' The Line 18 credit-forward election is IRREVOCABLE. Enter the refund "
                 "amount on Line 19 if a refund is wanted."),
     "notes": "A quiet, expensive default."},
    {"diagnostic_id": "D_FL1120_EXEMPT_CTRL_GROUP", "title": "ONE $50,000 exemption per Sec.1563 controlled group", "severity": "warning",
     "condition": "is_controlled_group_member",
     "message": ("Only ONE $50,000 Florida exemption is available per controlled group as defined in "
                 "Sec.1563, IRC. If members file separately, answer Question G-1 and attach a member list "
                 "with FEIN, address and the apportioned amount of the $50,000 for each corporation - "
                 "'Attaching the list shows consent to an unequal apportionment of the Florida exemption.' "
                 "Absent an apportionment plan the exemption is divided EQUALLY among all filing members. "
                 "A short tax year prorates the exemption: $50,000 x days in the short year / 365."),
     "notes": "s. 220.14; F-1120N p.5; F-1120A supplies the equal-division default."},
    {"diagnostic_id": "D_FL1120_FINAL_RETURN_TRAP", "title": "Question D: what is NOT a final return", "severity": "info",
     "condition": "Question D 'final return' is marked",
     "message": ("'When a C Corporation elects to become an S corporation, the final C return is NOT "
                 "considered to be a final tax return...A return for a foreign (out-of-state) corporation "
                 "that has ceased doing business in Florida is NOT a final return.' Verify before marking "
                 "Question D."),
     "notes": "A trap worth a diagnostic; F-1120 page 2, Question D."},
    {"diagnostic_id": "D_FL1120_EFILE_MANDATE", "title": "Electronic filing and payment may be mandatory", "severity": "info",
     "condition": "prior-year Florida corporate income tax paid >= $5,000 OR the federal return must be e-filed",
     "message": ("A taxpayer must file AND pay electronically if it paid $5,000 or more in Florida "
                 "corporate income tax during the STATE'S PRIOR FISCAL YEAR (July 1 - June 30), or if it "
                 "was required to file its FEDERAL return electronically. Penalty for not e-filing when "
                 "required: 5% of tax due per month, capped at $250 - or $10 if no tax is due."),
     "notes": "F-1120, F-1120ES and F-7004 file through IRS MeF with transmitters approved by the IRS AND FL DOR."},
]


FL1120_SCENARIOS: list[dict] = [
    {"scenario_name": "S corp with 1120S Line 23c tax - F-1120 IS required", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"entity_classification": "s_corp", "federal_return_type": "1120S", "has_florida_nexus": True,
                "fed_1120s_line_23c": 18000, "fed_1120s_lifo_recapture_only": False},
     "expected_outputs": {"file_F1120": True},
     "notes": ("Rule 12C-1.022(1)(b)1 / F-1120N p.2. Line 1 carries ONLY the income subject to federal tax "
               "at the corporate level (the Sec.1374/Sec.1375 base), NOT total S-corp income.")},
    {"scenario_name": "S corp with zero Line 23c - NO Florida return", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"entity_classification": "s_corp", "federal_return_type": "1120S", "has_florida_nexus": True,
                "fed_1120s_line_23c": 0},
     "expected_outputs": {"file_F1120": False, "diagnostic": "D_FL1120_GATE_NO_RETURN"},
     "notes": ("The overwhelmingly common Florida S-corp case: NOTHING IS FILED. The determination must be "
               "emitted positively with its reason and citation. Exception: an S corp MAY file to claim a "
               "refund of Florida payment credits (F-1120A p.3).")},
    {"scenario_name": "W3 edge - Line 23c is LIFO recapture only (UNRESOLVED)", "scenario_type": "failure", "sort_order": 3,
     "inputs": {"entity_classification": "s_corp", "federal_return_type": "1120S", "has_florida_nexus": True,
                "fed_1120s_line_23c": 9000, "fed_1120s_lifo_recapture_only": True},
     "expected_outputs": {"file_F1120": True, "florida_taxable_base": 0, "diagnostic": "D_FL1120_W3_LIFO_RECAPTURE"},
     "notes": ("W3. The trigger (Line 23c) fires but s. 220.13(2)(i) supplies NO base - Sec.1374/Sec.1375 "
               "only. A return with a ZERO base. DO NOT SILENTLY RESOLVE.")},
    {"scenario_name": "Homeowners association filing federal 1120-H - no Florida return", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"entity_classification": "homeowners_assoc", "federal_return_type": "1120-H", "has_florida_nexus": True},
     "expected_outputs": {"file_F1120": False, "diagnostic": "D_FL1120_GATE_1120H"},
     "notes": "'Rule says no', stated in terms. The same association filing federal Form 1120 WOULD file F-1120 regardless of tax due."},
    {"scenario_name": "Charitable trust TY2025 - STILL FILES F-1120 (W8)", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"entity_classification": "charitable_trust", "federal_return_type": "1120", "has_florida_nexus": True,
                "tax_year_begin": "2025-01-01", "tax_year_end": "2025-12-31"},
     "expected_outputs": {"file_F1120": True, "diagnostic": "D_FL1120_GATE_CHAR_TRUST"},
     "notes": ("THE 2025 STATUTE TEXT ALREADY PRINTS CHARITABLE TRUSTS AS EXCLUDED AND IS WRONG FOR "
               "TY2025 - ch. 2025-208 reaches only TYs beginning on/after 1/1/2026 and Rule 12C-1.022's "
               "amendment was adopted effective 1/1/2026.")},
    {"scenario_name": "$50,000 exemption - full amount, 5.5% tax", "scenario_type": "normal", "sort_order": 10,
     "inputs": {"L7": 400000, "L8": 0, "is_short_year": False},
     "expected_outputs": {"L9": 50000, "L10": 350000, "L11": 19250.0},
     "notes": "Exemption = lesser of 50,000 or (400,000 + 0) = 50,000. L10 = 350,000. L11 = 350,000 x 0.055 = 19,250."},
    {"scenario_name": "$50,000 exemption capped by a small Florida base", "scenario_type": "edge", "sort_order": 11,
     "inputs": {"L7": 30000, "L8": 0},
     "expected_outputs": {"L9": 30000, "L10": 0, "L11": 0.0},
     "notes": "LESSER-OF: the exemption cannot exceed L7 + L8, so it is 30,000 and Florida net income is zero."},
    {"scenario_name": "$50,000 exemption - negative base floors at zero", "scenario_type": "edge", "sort_order": 12,
     "inputs": {"L7": -75000, "L8": 0},
     "expected_outputs": {"L9": 0, "L10": 0},
     "notes": "'If Line 7 plus Line 8 is zero or less, enter zero.' Line 10 is likewise floored: 'if a loss, enter zero.'"},
    {"scenario_name": "Short-year exemption proration (183 days)", "scenario_type": "edge", "sort_order": 13,
     "inputs": {"L7": 400000, "L8": 0, "is_short_year": True, "short_year_days": 183},
     "expected_outputs": {"L9": 25068.49},
     "notes": "50,000 x 183 / 365 = 25,068.49 (F-1120N p.5)."},
    {"scenario_name": "Apportionment 25/25/50 - all three factors present", "scenario_type": "normal", "sort_order": 20,
     "inputs": {"property_fl": 200000, "property_everywhere": 1000000, "payroll_fl": 300000,
                "payroll_everywhere": 1000000, "sales_fl": 400000, "sales_everywhere": 2000000},
     "expected_outputs": {"SchIII-A-4": 0.225},
     "notes": "0.25 x 0.20 + 0.25 x 0.30 + 0.50 x 0.20 = 0.05 + 0.075 + 0.10 = 0.225 (six decimals)."},
    {"scenario_name": "Zero PROPERTY denominator - payroll 33-1/3%, sales 66-2/3%", "scenario_type": "edge", "sort_order": 21,
     "inputs": {"property_fl": 0, "property_everywhere": 0, "payroll_fl": 300000,
                "payroll_everywhere": 1000000, "sales_fl": 400000, "sales_everywhere": 2000000},
     "expected_outputs": {"SchIII-A-4": 0.233333},
     "notes": "(1/3) x 0.30 + (2/3) x 0.20 = 0.1 + 0.133333 = 0.233333 (s. 220.15(1)(c); F-1120N p.9)."},
    {"scenario_name": "Zero SALES denominator - property and payroll each 50%", "scenario_type": "edge", "sort_order": 22,
     "inputs": {"property_fl": 200000, "property_everywhere": 1000000, "payroll_fl": 300000,
                "payroll_everywhere": 1000000, "sales_fl": 0, "sales_everywhere": 0},
     "expected_outputs": {"SchIII-A-4": 0.25},
     "notes": "0.5 x 0.20 + 0.5 x 0.30 = 0.10 + 0.15 = 0.25 (s. 220.15(1)(b))."},
    {"scenario_name": "TWO zero denominators - the remaining factor is 100%", "scenario_type": "edge", "sort_order": 23,
     "inputs": {"property_fl": 0, "property_everywhere": 0, "payroll_fl": 0, "payroll_everywhere": 0,
                "sales_fl": 400000, "sales_everywhere": 2000000},
     "expected_outputs": {"SchIII-A-4": 0.20},
     "notes": "1.00 x 0.20 = 0.20 (s. 220.15(1)(a))."},
    {"scenario_name": "W4: tiny but NONZERO property denominator - NO reweighting", "scenario_type": "failure", "sort_order": 24,
     "inputs": {"property_fl": 0, "property_everywhere": 1, "payroll_fl": 300000,
                "payroll_everywhere": 1000000, "sales_fl": 400000, "sales_everywhere": 2000000},
     "expected_outputs": {"SchIII-A-4": 0.175, "diagnostic": "D_FL1120_INSIGNIFICANT_DEN"},
     "notes": ("W4 - THE LOAD-BEARING NEGATIVE TEST. Weights stay 25/25/50: 0.25 x 0 + 0.25 x 0.30 + 0.50 "
               "x 0.20 = 0.175. If the software had wrongly auto-reweighted to 33-1/3 / 66-2/3 it would "
               "return 0.233333. INSIGNIFICANCE IS THE DEPARTMENT'S DETERMINATION, NOT THE PREPARER'S.")},
    {"scenario_name": "APPORTIONMENT GATE FAILURE - 100% of adjusted federal income", "scenario_type": "failure", "sort_order": 25,
     "inputs": {"L6": 1000000, "doing_business_outside_fl": False, "gate_basis": "pl86272_solicitation_only",
                "sales_fl": 400000, "sales_everywhere": 2000000},
     "expected_outputs": {"L7": 1000000, "diagnostic": "D_FL1120_R3_APPORT_GATE"},
     "notes": ("W7. The taxpayer sells into other states but has no property or payroll there, so it is NOT "
               "doing business within and without Florida (Rule 12C-1.015(1)(b)3-5). Rule 12C-1.015(2) "
               "then taxes ALL of its adjusted federal income - 1,000,000, NOT the 200,000 a 20% sales "
               "factor would have produced. HARSHER THAN THROWBACK, and Florida has NO throwback rule.")},
    {"scenario_name": "Sec.168(k) bonus 1/7 recovery - single vintage", "scenario_type": "normal", "sort_order": 30,
     "inputs": {"bonus_addition_vintages": {"2025": 700000}, "current_year": 2025, "schi_l21_bonus_qip_portion": 0},
     "expected_outputs": {"SchI-21": 700000, "SchII-9": 100000.0},
     "notes": "700,000 / 7 = 100,000 subtracted in EACH of TY2025 through TY2031 (seven years beginning WITH the year of the addition)."},
    {"scenario_name": "Sec.168(k) bonus 1/7 recovery - three open vintages", "scenario_type": "edge", "sort_order": 31,
     "inputs": {"bonus_addition_vintages": {"2021": 140000, "2023": 210000, "2025": 700000}, "current_year": 2025},
     "expected_outputs": {"SchII-9": 150000.0},
     "notes": "140,000/7 + 210,000/7 + 700,000/7 = 20,000 + 30,000 + 100,000 = 150,000. All three vintages are open in 2025."},
    {"scenario_name": "Sec.168(k) vintage EXPIRES after the seventh year", "scenario_type": "edge", "sort_order": 32,
     "inputs": {"bonus_addition_vintages": {"2018": 700000, "2025": 700000}, "current_year": 2025},
     "expected_outputs": {"SchII-9": 100000.0},
     "notes": "The 2018 vintage runs 2018-2024 inclusive and is CLOSED in 2025; only the 2025 vintage contributes 100,000."},
    {"scenario_name": "QIP split - only the NON-QIP half rides the 1/7 track", "scenario_type": "edge", "sort_order": 33,
     "inputs": {"schi_l21_bonus_depreciation": 1000000, "schi_l21_bonus_qip_portion": 300000,
                "bonus_addition_vintages": {"2025": 700000}, "current_year": 2025},
     "expected_outputs": {"SchII-9": 100000.0, "qip_to_schii_l10": 300000},
     "notes": ("The 300,000 QIP portion is EXCLUDED from the Sch II L9 1/7 track and recovers instead on "
               "Sch II L10 as hypothetical 1/1/2020-IRC-without-CARES depreciation, IGNORING disposition. "
               "s. 220.13(1)(e)1.c. NEITHER HALF IS DERIVABLE FROM THE FEDERAL 4562.")},
    {"scenario_name": "Florida NOL two-tier - post-2017 limited to 80% of the remainder", "scenario_type": "edge", "sort_order": 40,
     "inputs": {"tentative_apportioned": 1000000, "fl_nol_pre2018_carryover": 200000, "fl_nol_post2017_carryover": 900000},
     "expected_outputs": {"nol_deduction": 840000.0},
     "notes": ("Pre-2018 applies FIRST against 100%: 200,000. Remainder = 800,000. Post-2017 is capped at "
               "80% x 800,000 = 640,000. Total 840,000. THE ORDER IS MANDATORY.")},
    {"scenario_name": "Schedule V cap binds at Line 11 (W2 circularity trigger)", "scenario_type": "edge", "sort_order": 50,
     "inputs": {"L11": 19250, "sch_v_lines_1_to_24_total": 25000},
     "expected_outputs": {"SchV-25": 19250.0, "L12": 19250.0, "L13": 0.0, "diagnostic": "D_FL1120_SCHV_CAP_BINDS"},
     "notes": ("The cap lands on Line 25 ONLY. Schedule I Lines 7-20 still add back the INDIVIDUAL Schedule "
               "V lines as entered (25,000 worth), single pass - the literally correct reading. Credits "
               "cannot create a refund.")},
    {"scenario_name": "Schedule I credit add-backs map to the individual Schedule V lines", "scenario_type": "normal", "sort_order": 51,
     "inputs": {"schv_l04_enterprise_zone": 5000, "schv_l05_rural_job": 3000, "schv_l06_urban_high_crime": 2000,
                "schv_l01_hmo_assessment": 1000, "schv_l24_other_credits": 500, "schv_l02_capital_investment": 40000},
     "expected_outputs": {"SchI-7": 5000, "SchI-8": 1500, "SchI-9": 5000},
     "notes": ("Sch I L7 <- Sch V L4; L8 <- Sch V L1 + FLAHIGA inside Sch V L24 (1,000 + 500); L9 <- Sch V "
               "L5 + L6 (3,000 + 2,000). The 40,000 capital investment credit (Sch V L2) generates NO "
               "add-back - it is one of the eight with no Schedule I line.")},
    {"scenario_name": "W1 BLOCK - Line 1 pre-OBBBA figure unconfirmed", "scenario_type": "failure", "sort_order": 60,
     "inputs": {"federal_taxable_income": 800000, "fti_pre_obbba_confirmed": False},
     "expected_outputs": {"blocked": True, "diagnostic": "D_FL1120_W1_NO_SILENT_RECALC"},
     "notes": ("W1 GATES THE LOADER. Florida does not adopt OBBBA for TY2025 and NO LINE ON THE RETURN "
               "CARRIES THE RECOMPUTE. Delvio never computes it and never writes Line 1 from an "
               "OBBBA-adjusted federal figure.")},
    {"scenario_name": "W5 BLOCK - fiscal year ending 6/30/2026", "scenario_type": "failure", "sort_order": 61,
     "inputs": {"tax_year_begin": "2025-07-01", "tax_year_end": "2026-06-30"},
     "expected_outputs": {"blocked": True, "diagnostic": "D_FL1120_R1_FISCAL_STRADDLE"},
     "notes": ("W5. ch. 2026-137 s. 3(1) says the amendments 'operate retroactively to January 1, 2026' "
               "without saying 'for tax years beginning on or after.' HARD BLOCK - the applicable IRC, and "
               "therefore the Line 1 recompute and the Sec.179 limit, are unresolved.")},
    {"scenario_name": "Full 100%-Florida C corp end to end", "scenario_type": "normal", "sort_order": 70,
     "inputs": {"entity_classification": "c_corp", "federal_return_type": "1120", "has_florida_nexus": True,
                "federal_taxable_income": 500000, "fti_pre_obbba_confirmed": True,
                "state_income_taxes_deducted": 20000, "doing_business_outside_fl": False,
                "schi_l21_bonus_depreciation": 70000, "schi_l21_bonus_qip_portion": 0},
     "expected_outputs": {"L3": 70000, "L4": 590000, "L5": 10000.0, "L6": 580000.0, "L7": 580000.0,
                          "L9": 50000, "L10": 530000.0, "L11": 29150.0},
     "notes": ("Sch I L26 = 70,000 bonus add-back; Sch II L13 = 70,000/7 = 10,000 first-year recovery. "
               "L4 = 500,000 + 20,000 + 70,000 = 590,000; L6 = 580,000. 100% Florida so L7 = L6 and "
               "Schedule IV is not completed (carryovers would ride Schedule II Lines 3-6). "
               "L10 = 580,000 - 50,000 = 530,000; L11 = 530,000 x 0.055 = 29,150.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM 2 — FL_F1065 (Florida Partnership Information Return, R. 01/24, TY2025)
#
# entity_types ["1065"]. INFORMATION RETURN ONLY: no tax, no payment, no rate.
# It exists for exactly two purposes — to compute the Florida partnership income
# adjustment and distribute it to corporate partners, and to distribute the
# partnership's apportionment factors to those partners' own F-1120s.
# ═══════════════════════════════════════════════════════════════════════════

FL1065_FACTS: list[dict] = [
    # ── THE GATE ──
    {"fact_key": "is_florida_partnership", "label": "Florida partnership? (doing business, earning income, or existing in Florida)", "data_type": "boolean", "required": True, "sort_order": 1,
     "notes": "F-1065N p.1: 'A Florida partnership is a partnership doing business, earning income, or existing in Florida.'"},
    {"fact_key": "partner_kinds", "label": "Partner roster kinds (JSON list: individual / c_corp / foreign_corp / s_corp / partnership / other)", "data_type": "string", "required": True, "sort_order": 2,
     "notes": ("THE GATE INPUT. An ALL-INDIVIDUAL partnership files NOTHING (Example 1). A partnership "
               "whose only ch.220 partner is an S CORPORATION files NOTHING (Rule 12C-1.022(6)(b), "
               "Example 4). A PARTNERSHIP partner => TIERED, UNRESOLVED (R10) - the software must refuse "
               "to answer, not infer.")},
    {"fact_key": "has_tiered_partner", "label": "Any partner is itself a partnership? (tiered structure - R10 UNRESOLVED)", "data_type": "boolean", "required": False, "sort_order": 3},
    {"fact_key": "is_worksheet_only_mode", "label": "Worksheet-only mode: corporate partner reporting a NON-Florida partnership (Rule 12C-1.022(6)(f))", "data_type": "boolean", "required": False, "sort_order": 4,
     "notes": "A corporation filing F-1120 MAY use F-1065 to report its distributive share from a partnership that is NOT a Florida partnership (rule example: an Ohio partnership doing no business in Florida). NOT A FILING."},
    {"fact_key": "num_partners", "label": "Number of partners on the roster", "data_type": "integer", "required": False, "sort_order": 5},
    # ── Part I ──
    {"fact_key": "parti_a1_exempt_interest", "label": "Part I A.1: total interest excluded from federal ordinary income (Sec.103(a))", "data_type": "decimal", "required": False, "sort_order": 10},
    {"fact_key": "parti_a1_related_expenses", "label": "Part I A.1: associated expenses not deductible in computing federal ordinary income (Sec.265)", "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "parti_a2_state_income_taxes", "label": "Part I A.2: state income taxes deducted in computing federal ordinary income", "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "EXCLUDE taxes based on gross receipts or revenues."},
    {"fact_key": "parti_a3_other_additions", "label": "Part I A.3: other additions (the Sec.168(k) bonus add-back rides HERE - no dedicated line)", "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "The F-1065 mirrors only a THIN SLICE of the F-1120 modification set. The bonus add-back and its 1/7 recovery are free-form 'other' amounts with NO dedicated line and NO printed schedule."},
    {"fact_key": "partb_subtractions", "label": "Part I B: subtractions from federal income (incl. the 1/7 bonus recovery)", "data_type": "decimal", "required": False, "sort_order": 14,
     "notes": "Printed on the form: 'For example, s. 220.13(1)(e), F.S., provides for a subtraction taken equally over a seven year period corresponding to the add back...for the special bonus depreciation.'"},
    {"fact_key": "partd_other_pships_adj", "label": "Part I D: net adjustment from other partnerships or joint ventures (attach a schedule)", "data_type": "decimal", "required": False, "sort_order": 15,
     "notes": "THE ONLY TIERING-AWARE LINE ON THE FORM - and it does not resolve the tiered FILING question (R10)."},
    # ── Part III factor data ──
    {"fact_key": "p3_property_fl", "label": "Part III-A L1 col (a): average value of property within Florida (Part III-C Line 8)", "data_type": "decimal", "required": False, "sort_order": 20},
    {"fact_key": "p3_property_everywhere", "label": "Part III-A L1 col (b): average value of property everywhere", "data_type": "decimal", "required": False, "sort_order": 21},
    {"fact_key": "p3_payroll_fl", "label": "Part III-A L2 col (a): salaries, wages, commissions and other compensation within Florida", "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "p3_payroll_everywhere", "label": "Part III-A L2 col (b): compensation everywhere", "data_type": "decimal", "required": False, "sort_order": 23},
    {"fact_key": "p3_sales_fl", "label": "Part III-A L3 col (a): sales within Florida", "data_type": "decimal", "required": False, "sort_order": 24},
    {"fact_key": "p3_sales_everywhere", "label": "Part III-A L3 col (b): sales everywhere", "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "p3_rent_fl_net_annual", "label": "Part III-C L7a: Florida net annual rent (entered at 8x)", "data_type": "decimal", "required": False, "sort_order": 26},
    {"fact_key": "p3_rent_ew_net_annual", "label": "Part III-C L7b: everywhere net annual rent (entered at 8x)", "data_type": "decimal", "required": False, "sort_order": 27},
    {"fact_key": "p3b_revenue_miles_fl", "label": "Part III-B: Florida revenue miles (transportation services)", "data_type": "decimal", "required": False, "sort_order": 28},
    {"fact_key": "p3b_revenue_miles_ew", "label": "Part III-B: everywhere revenue miles (transportation services)", "data_type": "decimal", "required": False, "sort_order": 29},
    # ── Filing mechanics ──
    {"fact_key": "federal_return_attached_1065", "label": "Copy of federal Form 1065 attached? (W6 CONFLICT - do NOT auto-resolve)", "data_type": "boolean", "required": False, "sort_order": 40,
     "notes": ("*** UNRESOLVED CONFLICT. F-1065N p.1: 'Do not attach a copy of the federal return.' Rule "
               "12C-1.022(6)(d): 'A copy of the related U.S. Partnership Return of Income, Form 1065, must "
               "be attached' - and then defers to the instructions that forbid it. SELF-REFERENTIALLY "
               "CIRCULAR. Both texts confirmed verbatim. W6. ***")},
    {"fact_key": "original_signature_present", "label": "Original signature present? (no photocopy, facsimile or stamp)", "data_type": "boolean", "required": False, "sort_order": 41},
    {"fact_key": "is_final_return_1065", "label": "Final return? (write 'FINAL RETURN' at the top if the partnership ceases to exist)", "data_type": "boolean", "required": False, "sort_order": 42},
    {"fact_key": "f1065_tax_year_end", "label": "Tax year ending date (F-1065 is due the FIRST DAY OF THE FOURTH MONTH)", "data_type": "date", "required": True, "sort_order": 43},
]

FL1065_RULES: list[dict] = [
    {"rule_id": "R-FL65-GATE", "title": "F-1065 filing obligation — most Florida partnerships file NOTHING", "rule_type": "routing",
     "formula": ("file_F1065 := is_florida_partnership "
                 "AND EXISTS partner P such that subject_to_ch220(P) "
                 "AND NOT (the only such partners are S corporations) ; "
                 "subject_to_ch220(P) := P is a ch. 220 'taxpayer' (s. 220.03(1)(z)) OR P is a corporation "
                 "subject to tax SOLELY BY VIRTUE OF Florida partnership membership. "
                 "If any partner is itself a PARTNERSHIP -> UNDETERMINED (R10), refuse to answer."),
     "inputs": ["is_florida_partnership", "partner_kinds", "has_tiered_partner"],
     "outputs": ["file_F1065", "no_return_determination"], "sort_order": 1,
     "description": ("s. 220.22(2) + Rule 12C-1.022(6)(a)-(b), both verbatim. (6)(a): 'Every Florida "
                     "partnership having any partner subject to the Florida Income Tax Code is required "
                     "to make an information return...A partner subject to the Florida Income Tax Code "
                     "includes a taxpayer, as defined in Section 220.03(1)(z), F.S., and any corporation "
                     "subject to the tax solely by virtue of its membership in a Florida partnership.' "
                     "(6)(b): 'THE PARTNERSHIP WILL NOT BE REQUIRED TO FILE A PARTNERSHIP RETURN IF THE "
                     "ONLY PARTNER SUBJECT TO THE FLORIDA INCOME TAX CODE IS AN S CORPORATION.' "
                     "AN ALL-INDIVIDUAL PARTNERSHIP FILES NOTHING IN FLORIDA."),
     "notes": ("The four worked examples at Rule 12C-1.022(6)(c) are shipped as TestScenarios: AB (three "
               "individuals) NO; BC (two individuals + Corporation X) YES; CD (two individuals + "
               "Corporation Y, a New York corporation doing no business in Florida) YES 'solely by virtue "
               "of its membership'; DE (two individuals + Corporation Z, an S corporation) NO. "
               "The determination is a POSITIVE OUTPUT with a reason and citation, NEVER SILENCE.")},
    {"rule_id": "R-FL65-NOTAX", "title": "F-1065 is an INFORMATION RETURN — no tax, no payment, no rate", "rule_type": "validation",
     "formula": "F-1065 computes NO tax and carries NO payment line. Florida has NO PTET and NO nonresident withholding.",
     "inputs": ["is_florida_partnership"], "outputs": ["no_tax_due"], "sort_order": 2,
     "description": ("Florida has NO pass-through entity tax — 'the rule says no', not 'no rule found': "
                     "ch. 220 contains no elective or mandatory entity-level tax on partnerships or S "
                     "corporations and no PTE election section. There is no Florida individual income tax "
                     "against which an owner credit could be applied, no composite return, and no "
                     "nonresident withholding. FLORIDA MUST NEVER APPEAR IN A PTET ELECTION UI, A PTET "
                     "CREDIT ALLOCATION, OR A K-1 PTET LINE."),
     "notes": "Florida-sourced income belonging to an INDIVIDUAL owner produces NO Florida owner-level filing obligation of any kind."},
    {"rule_id": "R-FL65-PARTI", "title": "Part I — the Florida partnership income adjustment", "rule_type": "calculation",
     "formula": ("A.1 Net Interest = total interest excluded from federal ordinary income LESS associated "
                 "expenses not deductible ; A = A.1 + A.2 + A.3 ; C = A - B ; "
                 "E.1 Increase = C + D  (or)  E.2 Decrease = C + D"),
     "inputs": ["parti_a1_exempt_interest", "parti_a1_related_expenses", "parti_a2_state_income_taxes",
                "parti_a3_other_additions", "partb_subtractions", "partd_other_pships_adj"],
     "outputs": ["PartI-A", "PartI-C", "PartI-E"], "sort_order": 3,
     "description": ("A.1 = Sec.103(a) interest less Sec.265 expenses. A.2 excludes taxes based on gross "
                     "receipts or revenues. Line B carries the Florida subtractions, the form's own "
                     "example being 's. 220.13(1)(e), F.S....a subtraction taken equally over a seven year "
                     "period corresponding to the add back...for the special bonus depreciation.' Line D "
                     "is the net adjustment from OTHER partnerships or joint ventures (attach a schedule)."),
     "notes": ("*** THE F-1065 MIRRORS ONLY A THIN SLICE of the F-1120 modification set — tax-exempt "
               "interest, state income taxes, and 'other'. The bonus-depreciation add-back and its 1/7 "
               "recovery ride in Line A.3 / Line B AS FREE-FORM 'OTHER' AMOUNTS, with no dedicated line "
               "and no printed schedule. THE 7-YEAR VINTAGE TRACKING STILL HAS TO HAPPEN; THE FORM JUST "
               "DOES NOT HOLD IT. ***")},
    {"rule_id": "R-FL65-PARTII", "title": "Part II — distribution of the adjustment to partners: (a) x (b) = (c)", "rule_type": "calculation",
     "formula": ("per partner: col (c) = col (a) [Part I Line E amount] x col (b) [partner's percentage of "
                 "profits] ; INCREASES -> that partner's F-1120 Schedule I Line 25 ; "
                 "DECREASES -> that partner's F-1120 Schedule II Line 12"),
     "inputs": ["num_partners"], "outputs": ["PartII-c"], "sort_order": 4,
     "description": ("Form face verbatim: 'Column (a) times Column (b) = partner's share of Line E. Enter "
                     "here and on Florida Form F-1120, Schedule I (if decrease, Schedule II).' Rows carry "
                     "the partner's name and address INCLUDING FEIN, per s. 220.22(2)(b)."),
     "notes": ("*** THE RETURN IS STILL FILED WITH AN ALL-ZERO ADJUSTMENT. Printed on the form: 'If there "
               "is no adjustment on Line E, show partner's percentage of profits in Column (b) and leave "
               "Columns (a) and (c) blank.' THE PARTNER ROSTER ITSELF IS THE DELIVERABLE. ***")},
    {"rule_id": "R-FL65-FACTORS", "title": "Parts III-A/B/C — the partnership's apportionment factor data", "rule_type": "calculation",
     "formula": ("Part III-A: 1 average value of property per Part III-C Line 8 ; 2 salaries, wages, "
                 "commissions and other compensation paid or accrued ; 3 sales — each with columns "
                 "(a) Within Florida / (b) Total Everywhere. "
                 "Part III-C mirrors F-1120 Schedule III-B: original cost, beginning/end averaging, "
                 "rented property at 8 x NET ANNUAL RENT. "
                 "Part III-B: transportation services revenue miles."),
     "inputs": ["p3_property_fl", "p3_property_everywhere", "p3_payroll_fl", "p3_payroll_everywhere",
                "p3_sales_fl", "p3_sales_everywhere", "p3_rent_fl_net_annual", "p3_rent_ew_net_annual",
                "p3b_revenue_miles_fl", "p3b_revenue_miles_ew"],
     "outputs": ["PartIII-A"], "sort_order": 5,
     "description": "Structure identical to F-1120 Schedule III-B (Lines 1-8), so the same property-factor engine serves both forms."},
    {"rule_id": "R-FL65-PARTIV", "title": "Part IV — per-partner factor split, added into the partner's OWN factors", "rule_type": "calculation",
     "formula": ("each partner's share = Part III-A amount x that partner's percentage of interest ; "
                 "the corporate partner then computes "
                 "(corporation's Florida sales + share of partnership's Florida sales) / "
                 "(corporation's everywhere sales + share of partnership's everywhere sales) — "
                 "NUMERATOR-AND-DENOMINATOR ADDITION, NOT A SEPARATE FRACTION"),
     "inputs": ["num_partners"], "outputs": ["PartIV"], "sort_order": 6,
     "description": ("F-1065N p.2 verbatim formula. Printed on the form face: 'NOTE: Transfer data to "
                     "Schedule III-A, Florida Form F-1120.' Rule 12C-1.015(10): a corporation that is a "
                     "partner 'must add its share of the property, payroll, and sales to its own "
                     "apportionment factors, REGARDLESS OF WHETHER THE PARTNERSHIPS ARE FLORIDA "
                     "PARTNERSHIPS.'"),
     "notes": "Both INCOME and APPORTIONMENT FACTORS flow through to corporate partners."},
    {"rule_id": "R-FL65-TIERED", "title": "TIERED PARTNERSHIPS — the rule is SILENT; do not infer", "rule_type": "validation",
     "formula": "if any partner is itself a partnership: file_F1065 := UNDETERMINED -> RED-defer R10, determine manually",
     "inputs": ["has_tiered_partner", "partner_kinds"], "outputs": ["undetermined"], "sort_order": 7,
     "description": ("Rule 12C-1.022(6) was obtained in full and IS SILENT ON PARTNERSHIP PARTNERS: (6)(a) "
                     "reaches only a s. 220.03(1)(z) taxpayer or a corporation subject to tax 'solely by "
                     "virtue of its membership in A Florida partnership' (SINGULAR, DIRECT), and all four "
                     "worked examples in (6)(c) involve ONLY individuals and corporations. The strongest "
                     "available argument is EXPRESSIO UNIUS — the drafters wrote a partner-level carve-out "
                     "for S corporations at (6)(b) and wrote NO LOOKTHROUGH for partnership partners, and "
                     "used 'directly or indirectly' at (1)(b)2 for disregarded entities but NOWHERE in "
                     "(6). THAT IS SUGGESTIVE, NOT AUTHORITY."),
     "notes": ("*** DO NOT FILL THE GAP WITH AN INFERENCE. *** What would settle it: a DOR Technical "
               "Assistance Advisement or a written DOR reply. Relevant only if a client sits in a tiered "
               "structure — CHECK THE CLIENT BOOK (W9) before authoring further.")},
    {"rule_id": "R-FL65-DUEDATE", "title": "F-1065 due the FIRST DAY OF THE FOURTH MONTH — not the fifth", "rule_type": "calculation",
     "formula": ("due = first day of the FOURTH month following the close of the taxable year, ALL YEAR "
                 "ENDS. Calendar year -> APRIL 1. Extension: F-7004, six months, one only."),
     "inputs": ["f1065_tax_year_end"], "outputs": ["due_date_1065"], "sort_order": 8,
     "description": ("F-1065N p.1. A federal extension alone does not extend Florida. F-1065 may be filed "
                     "through the IRS Modernized e-File (MeF) Program. An ORIGINAL SIGNATURE is required — "
                     "'We will not accept a photocopy, facsimile, or stamp.' If the partnership ceases to "
                     "exist, write 'FINAL RETURN' at the top of the form."),
     "notes": "*** F-1065 AND F-1120 HAVE DIFFERENT DUE DATES: calendar year APRIL 1 vs MAY 1. ***"},
    {"rule_id": "R-FL65-ATTACH", "title": "W6 — the federal-return attachment conflict is UNRESOLVED", "rule_type": "validation",
     "formula": "F-1065N: 'Do not attach a copy of the federal return.' vs Rule 12C-1.022(6)(d): 'must be attached.' NO AUTOMATIC RESOLUTION.",
     "inputs": ["federal_return_attached_1065"], "outputs": ["attachment_conflict"], "sort_order": 9,
     "description": ("Both texts confirmed VERBATIM. Rule 12C-1.022(6)(d) (effective 1/1/2026) mandates the "
                     "attachment AND THEN DEFERS to 'the instructions for Form F-1065', which forbid it — "
                     "SELF-REFERENTIALLY CIRCULAR. This matters for MeF submission composition."),
     "notes": "W6. Settle via the FL MeF schema/business rules (gated behind FTA SES access) or a DOR reply. Ken decides the paper and MeF behaviours."},
]

FL1065_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-FL65-GATE", "FL_RULE_12C_1_022", "primary", "12C-1.022(6)(a)-(c): the trigger, the S-corp carve-out, the four examples"),
    ("R-FL65-GATE", "FL_2024_F1065_FORM", "primary", "F-1065N p.1 'Every Florida partnership having any partner subject to...'"),
    ("R-FL65-GATE", "FL_FS_CH220_2025", "secondary", "s. 220.22(2) — the statutory information-return duty"),
    ("R-FL65-NOTAX", "FL_2024_F1065_FORM", "primary", "the form carries no tax, rate or payment line"),
    ("R-FL65-NOTAX", "FL_FS_CH220_2025", "primary", "ch. 220 contains no PTE part or section — 'the rule says no'"),
    ("R-FL65-PARTI", "FL_2024_F1065_FORM", "primary", "Part I A.1-A.3, B, C, D, E verbatim labels"),
    ("R-FL65-PARTI", "FL_FS_CH220_2025", "secondary", "s. 220.13(1)(e) — the 7-year bonus subtraction the form names by example"),
    ("R-FL65-PARTII", "FL_2024_F1065_FORM", "primary", "Part II columns (a) x (b) = (c) and the zero-adjustment roster note"),
    ("R-FL65-PARTII", "FL_FS_CH220_2025", "secondary", "s. 220.22(2)(b)-(c) — the partner roster and distributive-share contents"),
    ("R-FL65-FACTORS", "FL_2024_F1065_FORM", "primary", "Parts III-A/B/C structure, 8 x net annual rent"),
    ("R-FL65-PARTIV", "FL_2024_F1065_FORM", "primary", "F-1065N p.2 flow-through formula; 'Transfer data to Schedule III-A'"),
    ("R-FL65-PARTIV", "FL_RULE_12C_1_015", "primary", "12C-1.015(10) partner factor attribution regardless of Florida status"),
    ("R-FL65-TIERED", "FL_RULE_12C_1_022", "primary", "12C-1.022(6) is SILENT on partnership partners — a true gap"),
    ("R-FL65-DUEDATE", "FL_2024_F1065_FORM", "primary", "F-1065N p.1 — first day of the FOURTH month, all year ends"),
    ("R-FL65-ATTACH", "FL_2024_F1065_FORM", "primary", "F-1065N p.1 'Do not attach a copy of the federal return.'"),
    ("R-FL65-ATTACH", "FL_RULE_12C_1_022", "primary", "12C-1.022(6)(d) 'must be attached' — the unresolved conflict"),
]

FL1065_LINES: list[dict] = [
    {"line_number": "PartI-A1", "description": "Federal tax-exempt interest: total interest excluded from federal ordinary income LESS associated expenses not deductible = Net Interest",
     "line_type": "input", "source_facts": ["parti_a1_exempt_interest", "parti_a1_related_expenses"],
     "source_rules": ["R-FL65-PARTI"], "sort_order": 1, "notes": "Sec.103(a) less Sec.265."},
    {"line_number": "PartI-A2", "description": "State income taxes deducted in computing federal ordinary income (exclude taxes based on gross receipts or revenues)",
     "line_type": "input", "source_facts": ["parti_a2_state_income_taxes"], "source_rules": ["R-FL65-PARTI"], "sort_order": 2},
    {"line_number": "PartI-A3", "description": "Other additions", "line_type": "input",
     "source_facts": ["parti_a3_other_additions"], "source_rules": ["R-FL65-PARTI"], "sort_order": 3,
     "notes": "The Sec.168(k) bonus add-back rides HERE as a free-form 'other' amount — no dedicated line, no printed schedule."},
    {"line_number": "PartI-A", "description": "Total additions", "line_type": "subtotal", "source_rules": ["R-FL65-PARTI"], "sort_order": 4},
    {"line_number": "PartI-B", "description": "Subtractions from federal income (e.g. the s. 220.13(1)(e) seven-year bonus recovery)",
     "line_type": "input", "source_facts": ["partb_subtractions"], "source_rules": ["R-FL65-PARTI"], "sort_order": 5},
    {"line_number": "PartI-C", "description": "Subtotal (Line A less Line B)", "line_type": "subtotal", "source_rules": ["R-FL65-PARTI"], "sort_order": 6},
    {"line_number": "PartI-D", "description": "Net adjustment from other partnerships or joint ventures (attach a schedule)",
     "line_type": "input", "source_facts": ["partd_other_pships_adj"], "source_rules": ["R-FL65-PARTI"], "sort_order": 7,
     "notes": "The ONLY tiering-aware line on the form — and it does NOT resolve the tiered FILING question (R10)."},
    {"line_number": "PartI-E1", "description": "Partnership income adjustment - Increase (total of Lines C and D)", "line_type": "total",
     "source_rules": ["R-FL65-PARTI"], "sort_order": 8, "notes": "-> each corporate partner's F-1120 Schedule I Line 25."},
    {"line_number": "PartI-E2", "description": "Partnership income adjustment - Decrease (total of Lines C and D)", "line_type": "total",
     "source_rules": ["R-FL65-PARTI"], "sort_order": 9, "notes": "-> each corporate partner's F-1120 Schedule II Line 12."},
    {"line_number": "PartII-a", "description": "Per partner col (a): amount shown on Line E, Part I", "line_type": "calculated",
     "source_rules": ["R-FL65-PARTII"], "sort_order": 10},
    {"line_number": "PartII-b", "description": "Per partner col (b): partner's percentage of profits", "line_type": "input",
     "source_rules": ["R-FL65-PARTII"], "sort_order": 11,
     "notes": "SHOWN EVEN WHEN THERE IS NO ADJUSTMENT — columns (a) and (c) are left blank but the roster is still filed."},
    {"line_number": "PartII-c", "description": "Per partner col (c) = (a) x (b): partner's share of Line E. Enter on Florida Form F-1120, Schedule I (if decrease, Schedule II).",
     "line_type": "calculated", "source_rules": ["R-FL65-PARTII"], "sort_order": 12},
    {"line_number": "PartIII-A-1", "description": "Average value of property per Part III-C (Line 8) - (a) Within Florida / (b) Total Everywhere",
     "line_type": "input", "source_facts": ["p3_property_fl", "p3_property_everywhere"], "source_rules": ["R-FL65-FACTORS"], "sort_order": 20},
    {"line_number": "PartIII-A-2", "description": "Salaries, wages, commissions and other compensation paid or accrued", "line_type": "input",
     "source_facts": ["p3_payroll_fl", "p3_payroll_everywhere"], "source_rules": ["R-FL65-FACTORS"], "sort_order": 21},
    {"line_number": "PartIII-A-3", "description": "Sales", "line_type": "input",
     "source_facts": ["p3_sales_fl", "p3_sales_everywhere"], "source_rules": ["R-FL65-FACTORS"], "sort_order": 22},
    {"line_number": "PartIII-B", "description": "Transportation services revenue miles (Florida / everywhere)", "line_type": "input",
     "source_facts": ["p3b_revenue_miles_fl", "p3b_revenue_miles_ew"], "source_rules": ["R-FL65-FACTORS"], "sort_order": 23},
    {"line_number": "PartIII-C-8", "description": "Average value of property total (Lines 1-8; original cost, beginning/end averaging, 8 x net annual rent)",
     "line_type": "subtotal", "source_facts": ["p3_rent_fl_net_annual", "p3_rent_ew_net_annual"],
     "source_rules": ["R-FL65-FACTORS"], "sort_order": 24, "notes": "Same structure as F-1120 Schedule III-B."},
    {"line_number": "PartIV", "description": "Apportionment of Partners' Share: partner x percent of interest x paired Within-Florida / Everywhere Property, Payroll and Sales data. NOTE: Transfer data to Schedule III-A, Florida Form F-1120.",
     "line_type": "calculated", "source_rules": ["R-FL65-PARTIV"], "sort_order": 25},
]

FL1065_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_FL1065_GATE_NO_RETURN", "title": "No Florida partnership return required - explicit determination", "severity": "info",
     "condition": "R-FL65-GATE evaluates file_F1065 = False",
     "message": ("No Florida Form F-1065 is required for this partnership. The reason and citation are "
                 "recorded with the determination. MOST FLORIDA PARTNERSHIPS FILE NOTHING - do not "
                 "generate a Florida return merely because a federal Form 1065 exists."),
     "notes": "A POSITIVE OUTPUT, never silence. s. 220.22(2); Rule 12C-1.022(6)."},
    {"diagnostic_id": "D_FL1065_GATE_ALL_INDIVIDUAL", "title": "All-individual partnership files NOTHING in Florida", "severity": "info",
     "condition": "no partner is subject to ch. 220",
     "message": ("This partnership has no corporate partners, so no partner is subject to the Florida "
                 "Income Tax Code and NO FLORIDA RETURN OF ANY KIND IS REQUIRED. Rule 12C-1.022(6)(c) "
                 "Example 1: 'Partnership AB has three partners, all individuals...NOT required to file... "
                 "because it has no corporate partners.' There is no Florida individual income tax, so the "
                 "individual partners have no Florida filing obligation either."),
     "notes": "'Rule says no', with a worked example. THE most common Florida partnership outcome."},
    {"diagnostic_id": "D_FL1065_GATE_SCORP_ONLY", "title": "S-corp-partner carve-out: no F-1065 required", "severity": "info",
     "condition": "the only partners subject to ch. 220 are S corporations",
     "message": ("Rule 12C-1.022(6)(b) verbatim: 'The partnership will not be required to file a "
                 "partnership return if the only partner subject to the Florida Income Tax Code is an S "
                 "corporation.' Worked Example 4: 'Partnership DE has two individual partners and "
                 "Corporation Z, an \"S\" Corporation' - NOT required to file. NOTE: adding ANY C "
                 "corporation or foreign corporation to the roster flips this to REQUIRED."),
     "notes": "The conformity brief MISSED this carve-out; it is confirmed verbatim in the adopted rule."},
    {"diagnostic_id": "D_FL1065_CORP_PARTNER_DUAL", "title": "A corporate partner means TWO Florida returns", "severity": "warning",
     "condition": "file_F1065 = True AND any partner is a c_corp or foreign_corp",
     "message": ("Rule 12C-1.022(6)(g): 'Corporations who are members of a Florida partnership or joint "
                 "venture must file Form F-1065...AS WELL AS, Form F-1120.' A single Florida partnership "
                 "with one out-of-state corporate partner generates TWO FLORIDA RETURNS: this F-1065, and "
                 "that corporation's own F-1120 (with federal Schedule K-1 attached per Rule "
                 "12C-1.022(2)(e)). A corporation is subject to the Code SOLELY BY VIRTUE OF its "
                 "membership even if it does no other business in Florida (Example 3)."),
     "notes": "A COMMON MISS."},
    {"diagnostic_id": "D_FL1065_R10_TIERED_PARTNERSHIP", "title": "RED-DEFER R10: tiered partnership - determine the obligation manually", "severity": "error",
     "condition": "has_tiered_partner OR any partner kind is 'partnership'",
     "message": ("A partner of this partnership is ITSELF A PARTNERSHIP. Florida's F-1065 filing trigger "
                 "for tiered structures IS UNRESOLVED - DETERMINE THE FILING OBLIGATION MANUALLY. Rule "
                 "12C-1.022(6) is SILENT on partnership partners: (6)(a) reaches only a s. 220.03(1)(z) "
                 "taxpayer or a corporation subject to tax 'solely by virtue of its membership in A "
                 "Florida partnership' (singular, direct), and all four worked examples involve only "
                 "individuals and corporations. An expressio-unius argument exists - (6)(b) carves out S "
                 "corporations and (1)(b)2 uses 'directly or indirectly' for disregarded entities, while "
                 "(6) uses no such phrase - BUT THAT IS AN ARGUMENT, NOT AUTHORITY. Settle via a DOR "
                 "Technical Assistance Advisement or a written DOR reply."),
     "notes": "R10 / W9. DO NOT FILL THE GAP WITH AN INFERENCE."},
    {"diagnostic_id": "D_FL1065_W6_ATTACH_CONFLICT", "title": "W6 UNRESOLVED: attach the federal 1065, or not?", "severity": "warning",
     "condition": "file_F1065 = True",
     "message": ("THE SOURCES CONFLICT AND NEITHER RESOLVES THE OTHER. F-1065N R. 01/24 p.1: 'Do not "
                 "attach a copy of the federal return.' Rule 12C-1.022(6)(d) (effective 1/1/2026): 'A copy "
                 "of the related U.S. Partnership Return of Income, Form 1065, must be attached. The "
                 "instructions for Form F-1065 prescribe the attachments required...' - a rule that both "
                 "MANDATES the attachment AND DEFERS to the instructions that FORBID it. Both texts "
                 "confirmed verbatim. This affects MeF submission composition. AWAIT A RULING."),
     "notes": "W6. Settle via the FL MeF schema/business rules (behind FTA SES access) or a DOR reply."},
    {"diagnostic_id": "D_FL1065_ZERO_ADJ_ROSTER", "title": "File the roster even with a zero adjustment", "severity": "info",
     "condition": "file_F1065 = True AND Part I Line E = 0",
     "message": ("Printed on the form: 'If there is no adjustment on Line E, show partner's percentage of "
                 "profits in Column (b) and leave Columns (a) and (c) blank.' THE RETURN IS STILL FILED - "
                 "the partner roster itself is the deliverable (s. 220.22(2)(b): names and addresses of "
                 "all partners subject to tax who would be entitled to share in the net income)."),
     "notes": "An all-zero adjustment does NOT excuse the filing."},
    {"diagnostic_id": "D_FL1065_DUE_4TH_MONTH", "title": "F-1065 is due a MONTH EARLIER than F-1120", "severity": "warning",
     "condition": "file_F1065 = True",
     "message": ("Florida Form F-1065 is due the FIRST DAY OF THE FOURTH MONTH following the close of the "
                 "taxable year - for a calendar year, APRIL 1. Florida Form F-1120 is due the first day of "
                 "the FIFTH month (MAY 1) for the same year end. DO NOT APPLY THE F-1120 DATE. Extension "
                 "via Form F-7004 only, six months, one per tax year; a federal extension alone does not "
                 "extend Florida."),
     "notes": "A genuinely easy miss — the two forms in this loader have different due dates."},
    {"diagnostic_id": "D_FL1065_BONUS_FREEFORM", "title": "Bonus depreciation has NO dedicated F-1065 line", "severity": "warning",
     "condition": "parti_a3_other_additions > 0 OR partb_subtractions > 0",
     "message": ("The F-1065 mirrors only a THIN SLICE of the F-1120 modification set. The Sec.168(k) "
                 "bonus add-back and its one-seventh, seven-year recovery ride in Part I Line A.3 and Line "
                 "B AS FREE-FORM 'OTHER' AMOUNTS, with no dedicated line and no printed schedule. THE "
                 "SEVEN-YEAR VINTAGE TRACKING STILL HAS TO HAPPEN - the form simply does not hold it. "
                 "Maintain the vintage schedule outside the form."),
     "notes": "The form's own Line B example names the s. 220.13(1)(e) seven-year subtraction."},
    {"diagnostic_id": "D_FL1065_WORKSHEET_MODE", "title": "F-1065 worksheet-only mode (non-Florida partnership)", "severity": "info",
     "condition": "is_worksheet_only_mode",
     "message": ("Rule 12C-1.022(6)(f) and F-1065N p.1: a corporation filing F-1120 MAY use Form F-1065 to "
                 "report its distributive share of income adjustments and apportionment factors from a "
                 "partnership that is NOT a Florida partnership (the rule's example is an Ohio partnership "
                 "doing no business in Florida). THIS IS A WORKSHEET, NOT A FILING - do not transmit it as "
                 "a partnership return."),
     "notes": "F-1065 has a genuine non-filing mode."},
    {"diagnostic_id": "D_FL1065_ORIGINAL_SIGNATURE", "title": "An ORIGINAL signature is required on a paper F-1065", "severity": "info",
     "condition": "file_F1065 = True AND paper filing",
     "message": ("F-1065N p.1: 'An original signature is required. We will not accept a photocopy, "
                 "facsimile, or stamp.' If the partnership ceases to exist, write 'FINAL RETURN' at the "
                 "top of the form. F-1065 may alternatively be filed through the IRS Modernized e-File "
                 "(MeF) Program."),
     "notes": "Paper-path requirement."},
    {"diagnostic_id": "D_FL1065_NO_PTET_NO_WH", "title": "Florida has NO PTET, no composite return and no nonresident withholding", "severity": "info",
     "condition": "always",
     "message": ("'The rule says no', not 'no rule found'. Chapter 220 contains no elective or mandatory "
                 "entity-level tax on partnerships or S corporations and no PTE election section. There is "
                 "no Florida individual income tax against which an owner credit could be applied, no "
                 "composite return, and nothing to withhold - a nonresident individual owner of a Florida "
                 "pass-through has NO Florida income tax liability. FLORIDA MUST NEVER APPEAR IN A PTET "
                 "ELECTION UI, A PTET CREDIT ALLOCATION, OR A K-1 PTET LINE."),
     "notes": "A structural absence, encoded so it is never 'helpfully' added."},
]

FL1065_SCENARIOS: list[dict] = [
    {"scenario_name": "Rule 12C-1.022(6)(c) Example 1 - Partnership AB, three individuals: NO return", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "individual", "individual"]},
     "expected_outputs": {"file_F1065": False, "diagnostic": "D_FL1065_GATE_ALL_INDIVIDUAL"},
     "notes": "VERBATIM RULE FIXTURE: 'Partnership AB has three partners, all individuals...not required to file...because it has no corporate partners.' FILES NOTHING IN FLORIDA."},
    {"scenario_name": "Rule 12C-1.022(6)(c) Example 2 - Partnership BC with Corporation X: F-1065 REQUIRED", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "individual", "c_corp"]},
     "expected_outputs": {"file_F1065": True, "diagnostic": "D_FL1065_CORP_PARTNER_DUAL"},
     "notes": "VERBATIM RULE FIXTURE: two individual partners plus Corporation X, which is subject to the Florida Income Tax Code. Corporation X also files its own F-1120 (Rule 12C-1.022(6)(g))."},
    {"scenario_name": "Rule 12C-1.022(6)(c) Example 3 - Partnership CD with a New York corporation: REQUIRED", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "individual", "foreign_corp"]},
     "expected_outputs": {"file_F1065": True, "foreign_corp_files_f1120": True, "diagnostic": "D_FL1065_CORP_PARTNER_DUAL"},
     "notes": ("VERBATIM RULE FIXTURE: 'Corporation Y, a New York corporation which does no business in "
               "Florida' - CD must file 'because Corporation Y is subject to the Florida Income Tax Code "
               "SOLELY BY VIRTUE OF ITS MEMBERSHIP in the Florida Partnership, CD.' TWO Florida returns "
               "result: this F-1065 and Corporation Y's own F-1120 with Schedule K-1 attached.")},
    {"scenario_name": "Rule 12C-1.022(6)(c) Example 4 - Partnership DE with an S corporation: NO return", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "individual", "s_corp"]},
     "expected_outputs": {"file_F1065": False, "diagnostic": "D_FL1065_GATE_SCORP_ONLY"},
     "notes": ("VERBATIM RULE FIXTURE + the 12C-1.022(6)(b) carve-out: 'The partnership will not be "
               "required to file a partnership return if the only partner subject to the Florida Income "
               "Tax Code is an S corporation.' THE CONFORMITY BRIEF MISSED THIS CARVE-OUT.")},
    {"scenario_name": "S corp AND C corp partners - the carve-out does NOT apply", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "s_corp", "c_corp"]},
     "expected_outputs": {"file_F1065": True},
     "notes": "12C-1.022(6)(b) excuses filing only when the ONLY ch.220 partner is an S corporation. Adding a C corporation flips it to REQUIRED."},
    {"scenario_name": "R10 - a partnership partner leaves the obligation UNDETERMINED", "scenario_type": "failure", "sort_order": 6,
     "inputs": {"is_florida_partnership": True, "partner_kinds": ["individual", "partnership"], "has_tiered_partner": True},
     "expected_outputs": {"file_F1065": None, "diagnostic": "D_FL1065_R10_TIERED_PARTNERSHIP"},
     "notes": "Rule 12C-1.022(6) is SILENT on partnership partners. The software returns UNDETERMINED and refuses to infer. R10 / W9."},
    {"scenario_name": "Non-Florida partnership - no filing obligation", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"is_florida_partnership": False, "partner_kinds": ["c_corp", "individual"]},
     "expected_outputs": {"file_F1065": False},
     "notes": ("A 'Florida partnership' is one doing business, earning income, or existing in Florida. A "
               "corporate partner MAY still use F-1065 in WORKSHEET-ONLY MODE to report its distributive "
               "share from such a partnership (Rule 12C-1.022(6)(f)) - that is not a filing.")},
    {"scenario_name": "Part I adjustment and Part II distribution (a) x (b) = (c)", "scenario_type": "normal", "sort_order": 10,
     "inputs": {"parti_a1_exempt_interest": 50000, "parti_a1_related_expenses": 5000,
                "parti_a2_state_income_taxes": 20000, "parti_a3_other_additions": 70000,
                "partb_subtractions": 10000, "partd_other_pships_adj": 0,
                "partner_profit_pct": 0.40},
     "expected_outputs": {"PartI-A": 135000, "PartI-C": 125000, "PartI-E1": 125000, "PartII-c": 50000.0},
     "notes": ("A.1 net interest = 50,000 - 5,000 = 45,000; A = 45,000 + 20,000 + 70,000 = 135,000; "
               "C = 135,000 - 10,000 = 125,000; E.1 = C + D = 125,000. A 40% partner's column (c) = "
               "125,000 x 0.40 = 50,000, entered on that partner's F-1120 SCHEDULE I LINE 25 (an "
               "INCREASE). A decrease would go to Schedule II Line 12.")},
    {"scenario_name": "Zero adjustment - the roster is still filed", "scenario_type": "edge", "sort_order": 11,
     "inputs": {"parti_a1_exempt_interest": 0, "parti_a2_state_income_taxes": 0, "parti_a3_other_additions": 0,
                "partb_subtractions": 0, "partd_other_pships_adj": 0, "partner_kinds": ["individual", "c_corp"],
                "is_florida_partnership": True},
     "expected_outputs": {"file_F1065": True, "PartI-E1": 0, "diagnostic": "D_FL1065_ZERO_ADJ_ROSTER"},
     "notes": "'If there is no adjustment on Line E, show partner's percentage of profits in Column (b) and leave Columns (a) and (c) blank.' The roster IS the deliverable."},
    {"scenario_name": "Part IV factor flow-through: numerator AND denominator addition", "scenario_type": "normal", "sort_order": 12,
     "inputs": {"corp_sales_fl": 600000, "corp_sales_everywhere": 3000000,
                "p3_sales_fl": 400000, "p3_sales_everywhere": 2000000, "partner_interest_pct": 0.50},
     "expected_outputs": {"partner_sales_fl_combined": 800000.0, "partner_sales_ew_combined": 4000000.0,
                          "partner_sales_factor": 0.20},
     "notes": ("F-1065N p.2 verbatim: '(corporation's Florida sales + share of partnership's Florida sales) "
               "/ (corporation's everywhere sales + share of partnership's everywhere sales)'. The 50% "
               "partner adds 200,000 / 1,000,000 to its own 600,000 / 3,000,000, giving 800,000 / "
               "4,000,000 = 0.20. NOT A SEPARATE FRACTION.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + flow assertions
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "FL_F1120",
            "form_title": "FL F-1120 — Florida Corporate Income/Franchise Tax Return (TY2025)",
            "entity_types": ["1120", "1120S"],
            "notes": (
                "Florida's only substantive return, R. 01/26, TY2025 ONLY. entity_types covers BOTH C "
                "corporations AND the S corporations that must file it (federal 1120S Line 23c > 0). "
                "Spine: federal taxable income (DIRECT-ENTRY, pre-OBBBA, never silently recomputed) + "
                "state income tax + Schedule I (26 addition lines) - Schedule II (13 subtraction lines) = "
                "adjusted federal income -> Schedule III/IV apportionment (25/25/50, zero-denominator "
                "reweighting ONLY) -> $50,000 exemption -> 5.5% -> Schedule V credits (25 lines in the "
                "statutory s. 220.02(8) order, capped at Line 11) -> payments. TWO SEPARATE DEPRECIATION "
                "TRACKS: Sch I L21 -> Sch II L9 (bonus, 1/7 over 7 years) and Sch I L22 -> Sch II L10 "
                "(QIP, hypothetical 1/1/2020-IRC-without-CARES depreciation ignoring disposition) — the "
                "L21 addition MUST be tagged QIP/non-QIP. NO Sec.179 add-back ('the rule says no'). "
                "FAILING THE APPORTIONMENT GATE TAXES 100% OF ADJUSTED FEDERAL INCOME. The TY2025 "
                "pre-OBBBA recompute HAS NO HOME ON THE RETURN (W1) and no line was invented for it. "
                "*** TY2026 RENUMBERS SCHEDULES I AND V — do not carry these line numbers forward. ***"
            ),
        },
        "facts": FL1120_FACTS, "rules": FL1120_RULES, "rule_links": FL1120_RULE_LINKS,
        "lines": FL1120_LINES, "diagnostics": FL1120_DIAGNOSTICS, "scenarios": FL1120_SCENARIOS,
    },
    {
        "identity": {
            "form_number": "FL_F1065",
            "form_title": "FL F-1065 — Florida Partnership Information Return (R. 01/24, TY2025)",
            "entity_types": ["1065"],
            "notes": (
                "INFORMATION RETURN ONLY: no tax, no payment, no rate. Florida has NO PTET, no composite "
                "return and no nonresident withholding. F-1065 exists for exactly two purposes — to "
                "compute the Florida partnership income adjustment (Part I) and distribute it to corporate "
                "partners (Part II, (a) x (b) = (c), increases -> the partner's F-1120 Sch I L25, "
                "decreases -> Sch II L12), and to distribute the partnership's apportionment factors "
                "(Parts III-IV) into those partners' OWN factors by numerator-and-denominator addition. "
                "THE GATE IS THE POINT: required only where a partner is subject to ch. 220, and NOT where "
                "the only such partner is an S corporation (Rule 12C-1.022(6)(b)); an ALL-INDIVIDUAL "
                "partnership files NOTHING. Due the FIRST DAY OF THE FOURTH MONTH — a month earlier than "
                "F-1120. Tiered partnerships are UNRESOLVED (R10). The attach-the-federal-return conflict "
                "between F-1065N and Rule 12C-1.022(6)(d) is UNRESOLVED (W6)."
            ),
        },
        "facts": FL1065_FACTS, "rules": FL1065_RULES, "rule_links": FL1065_RULE_LINKS,
        "lines": FL1065_LINES, "diagnostics": FL1065_DIAGNOSTICS, "scenarios": FL1065_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-FL-GATE-SCORP", "title": "S corp files F-1120 only when federal 1120S Line 23c > 0", "assertion_type": "flow_assertion",
     "entity_types": ["1120S"], "status": "draft", "sort_order": 1,
     "description": ("The Florida return exists for an S corporation ONLY when the federal 1120S Line 23c "
                     "total tax is greater than zero (Rule 12C-1.022(1)(b)1; F-1120N p.2). When it does, "
                     "Line 1 carries ONLY income subject to federal tax at the corporate level. Otherwise "
                     "the engine must emit an explicit 'no Florida return required' determination."),
     "definition": {"rule": "R-FL-GATE-SCORP", "check": "file_F1120(s_corp) == (fed_1120s_line_23c > 0)"}},
    {"assertion_id": "FA-FL-GATE-1065", "title": "F-1065 gate: ch.220 partner required, S-corp-only excused", "assertion_type": "flow_assertion",
     "entity_types": ["1065"], "status": "draft", "sort_order": 2,
     "description": ("file_F1065 = is_florida_partnership AND some partner is subject to ch. 220 AND NOT "
                     "(the only such partners are S corporations). Reproduces Rule 12C-1.022(6)(c) "
                     "Examples 1-4 exactly: AB no / BC yes / CD yes / DE no. A partnership partner yields "
                     "UNDETERMINED, never a guess."),
     "definition": {"rule": "R-FL65-GATE", "check": "AB=False, BC=True, CD=True, DE=True->False via (6)(b); tiered=None"}},
    {"assertion_id": "FA-FL-DUAL-RETURN", "title": "One FL partnership + one out-of-state corporate partner = TWO returns", "assertion_type": "flow_assertion",
     "entity_types": ["1065", "1120"], "status": "draft", "sort_order": 3,
     "description": ("Rule 12C-1.022(6)(g) and F-1120N p.1: the partnership files F-1065 AND the foreign "
                     "corporate partner separately files its own F-1120 with federal Schedule K-1 "
                     "attached (Rule 12C-1.022(2)(e))."),
     "definition": {"rule": "R-FL-GATE-FOREIGN", "check": "foreign_corp partner => F-1065 AND that partner's own F-1120"}},
    {"assertion_id": "FA-FL-L1-NOSILENT", "title": "Line 1 is never silently recomputed for OBBBA", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 4,
     "description": ("Florida does not adopt OBBBA for TY2025 and NO LINE ON THE RETURN CARRIES THE "
                     "RECOMPUTE. F-1120 Line 1 is DIRECT-ENTRY, requires an explicit preparer confirmation "
                     "that the figure is pre-OBBBA, and is never written from an OBBBA-adjusted federal "
                     "figure. Unconfirmed => blocking diagnostic. W1."),
     "definition": {"rule": "R-FL-L1-NOSILENT", "check": "L1 direct-entry; fti_pre_obbba_confirmed required; no computed recompute"}},
    {"assertion_id": "FA-FL-BONUS-7TH", "title": "Sec.168(k) recovery = 1/7 per year over seven years, non-QIP only", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 5,
     "description": ("Schedule II Line 9 for year N = sum over open vintages of (non-QIP Schedule I Line 21 "
                     "addition / 7), a vintage being open for the seven tax years beginning WITH the year "
                     "of the addition. The QIP portion is excluded and recovers on Schedule II Line 10."),
     "definition": {"rule": "R-FL-BONUS", "check": "SchII_L9 = sum(add_v/7 for v if v <= N <= v+6), non-QIP only"}},
    {"assertion_id": "FA-FL-QIP-SPLIT", "title": "Schedule I Line 21 splits QIP / non-QIP; the halves recover differently", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 6,
     "description": ("The L21 bonus addition must be tagged QIP vs non-QIP at entry. Sch II L10 recovers "
                     "Sch I L22 AND the QIP portion of L21 as hypothetical depreciation under the IRC in "
                     "effect 1/1/2020 without CARES, ignoring disposition. NEITHER HALF IS DERIVABLE FROM "
                     "THE FEDERAL FORM 4562."),
     "definition": {"rule": "R-FL-QIP", "check": "L21 = qip_portion + non_qip; non_qip -> SchII L9 (1/7); qip + L22 -> SchII L10"}},
    {"assertion_id": "FA-FL-179-NONE", "title": "No Florida Sec.179 add-back exists for TY2025", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 7,
     "description": ("s. 220.13(1)(e)2 expired for tax years beginning on or after 1/1/2015 and '179' "
                     "appears nowhere on the Florida forms or instructions. Sec.179 enters Florida only "
                     "through Line 1, at the pre-OBBBA $1,250,000 / $3,130,000 / $31,300 figures."),
     "definition": {"rule": "R-FL-179-NOADDBK", "check": "no Sec.179 add-back line; pre-OBBBA limits only"}},
    {"assertion_id": "FA-FL-APPORT", "title": "Apportionment fraction = 25% property + 25% payroll + 50% sales", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 8,
     "description": ("Schedule III-A Line 4 = 0.25 x property factor + 0.25 x payroll factor + 0.50 x sales "
                     "factor, each factor rounded to six decimal places (s. 220.15(1); F-1120N p.9). "
                     "Florida is NOT a single-sales-factor state."),
     "definition": {"rule": "R-FL-APPORT", "check": "SchIII_A_4 = round(.25*p + .25*pay + .50*s, 6)"}},
    {"assertion_id": "FA-FL-APPORT-ZERO", "title": "Reweighting fires ONLY on a denominator of exactly zero", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 9,
     "description": ("Two zero denominators -> the remaining factor 100%; sales zero -> property and "
                     "payroll each 50%; property or payroll zero -> the other 33-1/3% and sales 66-2/3%. "
                     "A SMALL-BUT-NONZERO DENOMINATOR MUST NOT BE REWEIGHTED — insignificance is the "
                     "DEPARTMENT'S determination under s. 220.15(1), not the preparer's. W4."),
     "definition": {"rule": "R-FL-APPORT-ZERO", "check": "reweight iff denominator == 0; nonzero -> keep 25/25/50 + diagnostic"}},
    {"assertion_id": "FA-FL-GATE-100PCT", "title": "Apportionment gate failure taxes 100% of adjusted federal income", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 10,
     "description": ("Rule 12C-1.015(2): where the taxpayer is not doing business within AND without "
                     "Florida, Line 7 = Line 6 in full. A sales-only out-of-state footprint protected by "
                     "P.L. 86-272 does NOT clear the gate — functionally more adverse than throwback, and "
                     "Florida has NO throwback rule ((1)(d), express). W7."),
     "definition": {"rule": "R-FL-APPORT-GATE", "check": "not doing_business_outside_fl => L7 == L6"}},
    {"assertion_id": "FA-FL-CARRYFORK", "title": "Carryovers appear on Schedule II OR Schedule IV, never both", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 11,
     "description": ("100% Florida -> the four carryovers ride Schedule II Lines 3-6 and Schedule IV is not "
                     "completed. Doing business outside Florida -> Schedule II Lines 3-6 are ZERO and the "
                     "carryovers ride Schedule IV Lines 4-7. Stated three times in the source."),
     "definition": {"rule": "R-FL-SCHIV", "check": "exactly one of {SchII L3-L6, SchIV L4-L7} is nonzero"}},
    {"assertion_id": "FA-FL-NOL-2TIER", "title": "Florida NOL: pre-2018 at 100% first, then post-2017 at 80% of the remainder", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 12,
     "description": "NOLD = min(pre2018, base) + min(post2017, 0.80 x (base - tier1)). No carryback. The order is mandatory.",
     "definition": {"rule": "R-FL-NOL", "check": "tier1 = min(pre2018, base); tier2 = min(post2017, .8*(base-tier1))"}},
    {"assertion_id": "FA-FL-EXEMPT", "title": "Line 9 = lesser of $50,000 or (L7 + L8), zero floor, short-year prorated", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 13,
     "description": ("s. 220.14. One exemption per Sec.1563 controlled group; short year = $50,000 x days / "
                     "365; if L7 + L8 is zero or less, the exemption is zero."),
     "definition": {"rule": "R-FL-EXEMPT", "check": "L9 = 0 if (L7+L8) <= 0 else min(cap, L7+L8)"}},
    {"assertion_id": "FA-FL-RATE", "title": "Line 11 = 5.5% of Line 10; credits capped at Line 11", "assertion_type": "reconciliation",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 14,
     "description": ("Form face verbatim 'Tax due: 5.5% of Line 10'; s. 220.11(2)(a) and s. 220.1105. "
                     "Schedule V Line 25 = min(sum of Lines 1-24, Line 11); credits cannot create a refund."),
     "definition": {"rule": "R-FL-TAX", "check": "L11 = round(L10 * 0.055, 2); L12 = min(schv_total, L11)"}},
    {"assertion_id": "FA-FL-SCHI-SCHV", "title": "Schedule I add-backs read the INDIVIDUAL Schedule V lines, single pass", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 15,
     "description": ("Sch I L7-L20 are populated once from the individual Sch V lines as entered, BEFORE "
                     "the Line 25 cap — the literally correct reading, since the cap lands only on L25 and "
                     "no Schedule I line reads from L25. Eight Schedule V credits (L2, L3, L7, L8, L9, "
                     "L10, L16, L23) generate NO add-back. W2 ratification item."),
     "definition": {"rule": "R-FL-SCHI-CREDITS", "check": "SchI L7..L20 = individual SchV lines as entered, single pass"}},
    {"assertion_id": "FA-FL-SCHR-ASYM", "title": "Schedule R asymmetry: L1 added at Line 8, L3 subtracted at Sch II L7", "assertion_type": "flow_assertion",
     "entity_types": ["1120", "1120S"], "status": "draft", "sort_order": 16,
     "description": ("Nonbusiness income is ALLOCATED, not apportioned (s. 220.16). Schedule R Line 1 "
                     "(Florida only) is ADDED at Page 1 Line 8 while Line 3 (Florida AND elsewhere) is "
                     "SUBTRACTED at Schedule II Line 7 — removing all nonbusiness income from the "
                     "apportionable base before adding the Florida slice back."),
     "definition": {"rule": "R-FL-SCHR", "check": "SchR_L1 -> L8 (+); SchR_L3 -> SchII L7 (-)"}},
    {"assertion_id": "FA-FL65-PARTNER", "title": "F-1065 Part II (a) x (b) = (c) lands on the partner's F-1120", "assertion_type": "reconciliation",
     "entity_types": ["1065"], "status": "draft", "sort_order": 17,
     "description": ("Each partner's column (c) = Part I Line E x that partner's percentage of profits. "
                     "INCREASES go to that partner's F-1120 Schedule I Line 25; DECREASES to Schedule II "
                     "Line 12. The roster is filed even when the adjustment is zero."),
     "definition": {"rule": "R-FL65-PARTII", "check": "c = a * b; increase -> F1120 SchI L25; decrease -> F1120 SchII L12"}},
    {"assertion_id": "FA-FL65-FACTORS", "title": "F-1065 factors add into the corporate partner's OWN factors", "assertion_type": "reconciliation",
     "entity_types": ["1065", "1120"], "status": "draft", "sort_order": 18,
     "description": ("F-1065N p.2: (corporation's Florida sales + share of partnership's Florida sales) / "
                     "(corporation's everywhere sales + share of partnership's everywhere sales) — "
                     "numerator-and-denominator addition, NOT a separate fraction. Rule 12C-1.015(10) "
                     "applies regardless of whether the partnership is a Florida partnership."),
     "definition": {"rule": "R-FL65-PARTIV", "check": "partner_factor = (corp_fl + share_fl) / (corp_ew + share_ew)"}},
    {"assertion_id": "FA-FL65-NOTAX", "title": "F-1065 carries no tax; Florida has no PTET and no withholding", "assertion_type": "flow_assertion",
     "entity_types": ["1065"], "status": "draft", "sort_order": 19,
     "description": ("Chapter 220 contains no PTE part or section, no composite return and no nonresident "
                     "withholding. Florida must never appear in a PTET election UI, a PTET credit "
                     "allocation, or a K-1 PTET line."),
     "definition": {"rule": "R-FL65-NOTAX", "check": "F-1065 produces no tax, no payment, no PTET artifact"}},
    {"assertion_id": "FA-FL-DUEDATES", "title": "F-1065 is due the 4th month; F-1120 the 5th (June-30 FYE the 4th)", "assertion_type": "flow_assertion",
     "entity_types": ["1065", "1120", "1120S"], "status": "draft", "sort_order": 20,
     "description": ("F-1065: first day of the FOURTH month, all year ends (calendar: April 1). F-1120: the "
                     "LATER of the first day of the 4th month (June 30 year ends) or the 5th month (all "
                     "others), and the 15th day following the unextended federal due date — calendar "
                     "TY2025 May 1, 2026. TIP 26C01-01 moves June-30 ends to the 5th month for TY2026 "
                     "ONLY."),
     "definition": {"rule": "R-FL-DUEDATE", "check": "F1065 = 4th month; F1120 = later-of with the June-30 carve-out"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the FL entity specs (FL_F1120 + FL_F1065, Florida corporate income/franchise tax, "
        "TY2025). Refuses to seed until Ken sets READY_TO_SEED=True after the in-session review "
        "walk (W1-W9). W1 — the TY2025 pre-OBBBA recompute has no home on the return — gates it."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad FL entity specs (FL_F1120 + FL_F1065, Florida corporate income/franchise tax)\n"))
        self._load_topics()
        sources = self._load_sources()
        for spec in FORMS:
            form = self._upsert_form(spec["identity"])
            self._upsert_facts(form, spec["facts"])
            rules = self._upsert_rules(form, spec["rules"])
            self._upsert_authority_links(rules, sources, spec["rule_links"])
            self._upsert_lines(form, spec["lines"])
            self._upsert_diagnostics(form, spec["diagnostics"])
            self._upsert_tests(form, spec["scenarios"])
        self._upsert_form_links(sources)
        self._load_flow_assertions()
        self._report_totals()

    def _guard_against_hollow_seed(self):
        empty = []
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            for key in ("facts", "rules", "lines", "diagnostics", "scenarios", "rule_links"):
                if not spec[key]:
                    empty.append(f"{fn}.{key}")
        if not FLOW_ASSERTIONS:
            empty.append("FLOW_ASSERTIONS")
        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED FL ENTITY SPECS: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken reviews the packet\n"
                "and flips the sentinel:\n"
                "  W1 *** the TY2025 pre-OBBBA recompute HAS NO HOME on the return —\n"
                "         choose the presentation; no line was invented (THIS GATES THE LOADER)\n"
                "  W2  the Schedule I <-> Schedule V credit circularity (ratify single pass)\n"
                "  W3  the S-corp trigger width: 1120S Line 23c vs Sec.1374/Sec.1375 (LIFO recapture)\n"
                "  W4  'insignificant denominator' — the DEPARTMENT'S call, never the preparer's\n"
                "  W5  *** fiscal TY2025 straddling 1/1/2026 — approve the hard block\n"
                "  W6  the F-1065 attach-the-federal-return conflict (F-1065N vs 12C-1.022(6)(d))\n"
                "  W7  the apportionment gate costs 100% of adjusted federal income\n"
                "  W8  charitable trusts DO file F-1120 for TY2025 (the statute text misleads)\n"
                "  W9  client-book scope check: tiered partnerships, financial orgs, Sch V credits\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and\n"
                "delvio-states/research/fl_entity_source_brief.md), then set\n"
                "READY_TO_SEED = True. Idempotent via update_or_create.\n"
                "NOTE: this loader is TY2025 ONLY — the TY2026 draft F-1120 renumbers\n"
                "Schedules I and V and must be authored as its own spec unit."
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            _, created = AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
            if created:
                ct += 1
        self.stdout.write(f"Topics: {ct} new ({len(AUTHORITY_TOPICS)} in batch)")

    def _load_sources(self) -> dict:
        sources: dict = {}
        for src_data in AUTHORITY_SOURCES:
            src_data = dict(src_data)
            excerpts_data = src_data.pop("excerpts", [])
            topic_codes = src_data.pop("topics", [])
            source, _ = AuthoritySource.objects.update_or_create(
                source_code=src_data["source_code"], defaults=src_data,
            )
            sources[source.source_code] = source
            for exc in excerpts_data:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=source, excerpt_label=exc["excerpt_label"], defaults=exc,
                )
            for tc in topic_codes:
                topic = AuthorityTopic.objects.filter(topic_code=tc).first()
                if topic:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=source, authority_topic=topic)
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
            else:
                # EXPECTED until the GATED Tier-1 conformity batch seeds. Not a defect.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND — links to it will be skipped "
                    "(expected: the FL conformity row sits in the gated, unseeded Tier-1 batch)"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"],
                      "entity_types": identity.get("entity_types", ["1120"]),
                      "status": FORM_STATUS, "notes": identity["notes"]},
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']}")
        return form

    def _upsert_facts(self, form, facts):
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self.stdout.write(f"  {len(created)} rules")
        return created

    def _upsert_authority_links(self, rules, sources, rule_links):
        ct = 0
        for rule_id, source_code, level, note in rule_links:
            rule, source = rules.get(rule_id), sources.get(source_code)
            if rule and source:
                RuleAuthorityLink.objects.get_or_create(
                    form_rule=rule, authority_source=source,
                    defaults={"support_level": level, "relevance_note": note},
                )
                ct += 1
        self.stdout.write(f"  {ct} authority links")

    def _upsert_lines(self, form, lines):
        for ln in lines:
            ln = dict(ln)
            FormLine.objects.update_or_create(tax_form=form, line_number=ln.pop("line_number"), defaults=ln)
        self.stdout.write(f"  {len(lines)} lines")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self.stdout.write(f"  {len(diagnostics)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _upsert_form_links(self, sources):
        for source_code, form_code, link_type in AUTHORITY_FORM_LINKS:
            source = sources.get(source_code) or AuthoritySource.objects.filter(source_code=source_code).first()
            if source:
                AuthorityFormLink.objects.get_or_create(
                    authority_source=source, form_code=form_code, link_type=link_type,
                    defaults={"note": f"{source_code} -> {form_code}"},
                )

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("FL entity specs loaded (TY2025 ONLY — TY2026 renumbers Schedules I and V).")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / "
                f"tests {len(spec['scenarios'])} / links {len(spec['rule_links'])}"
            )
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write(f"  Authority sources: {len(AUTHORITY_SOURCES)} (+{len(EXISTING_SOURCES_TO_REFERENCE)} referenced)")
        self.stdout.write("=" * 60)
