"""Load the Maryland Form 500 spec — Corporation Income Tax Return (TY2025).

WO-W05-CCORP, the 45-state campaign's C-corp sweep. Maryland is the first of the
seven states to be fully walked (campaign D-19 + D-20, 2026-08-23).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
`MD_500` is Maryland's C-corporation return: a FLAT 8.25% tax (§10-105(b)) on
Maryland taxable income, built from federal taxable income before NOL and
special deductions, adjusted through two distinct modification blocks, then
apportioned by a SINGLE SALES FACTOR (phase-in complete for TY2025).

⚠ THE DEFINING STRUCTURAL FACT — Form 500 has NO ELECTION and NO BRANCH.
Neither Form 500D nor Form 500E carries an election checkbox (their only box is
`Check here if you are a first time filer or your name has changed.`). There is
exactly ONE corporate return. **Do NOT port the PTE module's 510-vs-511
election-state machinery** — the irrevocable-lock workflow has no corporate
analogue and must not be inherited by reflex.

⚠ THERE IS NO LOCAL/COUNTY CORPORATE INCOME TAX. The whole county-rate engine
that Maryland's individual and 511 modules need has NO application here.
Line 14 is the entire tax.

═══════════════════════════════════════════════════════════════════════════
KEN'S RULINGS THIS SPEC IMPLEMENTS (campaign D-19, D-20 — 2026-08-23)
═══════════════════════════════════════════════════════════════════════════
D3  WORLDWIDE-HQ THREE-FACTOR FORMULA IS AN **ELECTION**, NOT A REQUIREMENT.
    §10-402(d)(3)(i) says `may elect`; AR 43 says `may elect` / `optional`; the
    TY2025 Corporate Booklet says `must use` / `required to use`.
    ⚠ THE BOOKLET ROUTES THE READER TO AR 43 — THE DOCUMENT THAT REFUTES IT.
    The same sentence sits verbatim in BOTH TY2025 PTE booklets, so it is a
    package-wide Comptroller erratum, not a typo. RULED: build elective, made
    annually, NEVER forced and NEVER inferred. RED-defer in v1.
W9  FORM 500CR **DEFERRED** from v1 (Ken's business decision). Paper 500CR no
    longer exists and Form 500 must be e-filed to claim any business credit, so
    every MD business-credit client files a waiver in v1. The RED diagnostic
    MUST name Form 500CRW reason B as the remedy.
W6  The §10-305(b) net capital loss carryback addition goes on **line 7f with NO
    code letter** plus a required attached schedule, with a v1 diagnostic.
    ⚠ DO NOT INVENT A CODE LETTER.
D2  COMBINED REPORTING: the NEGATIVE is a RULING. Maryland has none for TY2025,
    of any kind. Schedule B Q6/Q7 wire to NOTHING. The recorded reason is
    "no operative rule found" — NEVER "the rule expired" (unitary status is live
    in §10-402(d); the vestigial rationale was withdrawn as unsourced).
D4  ZERO FACTOR IS `.000000` ON FORM 500 — Forms 510/511 use `.000001`.
    Parameterised here, NEVER harmonised across the two.
D5  NEVER AUTO-REWEIGHT a factor whose denominator is missing.
D6  NAM: line 24 = line 9, NEVER line 9 ± the ADJUSTMENTS block.
D7  TWO DECOUPLING MECHANISMS WITH DIFFERENT LIFESPANS, encoded separately.
W8  Line 23's "Carryforward 20 years" is built AS PRINTED with NO expiry
    encoded; its support is INFERENTIAL (AR 18 is a July-2013, pre-TCJA doc).

═══════════════════════════════════════════════════════════════════════════
⚠ G4 — NEVER CLONE A SIBLING FORM'S LINE NUMBERS (campaign D-18)
═══════════════════════════════════════════════════════════════════════════
Every line map here is transcribed from the FORM 500 FACE (`COM/RAD-001 06/25`,
read positionally), NOT ported from the seeded `load_md_pte.py`. Maryland is
itself one of the three proofs behind that standing convention: its zero factor
is `.000001` on 510/511 but `.000000` on 500.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE
═══════════════════════════════════════════════════════════════════════════
COMPUTES: the full 1a→14 spine (federal TI → adjustments → NOL → modifications →
apportionment → 8.25%), the Schedule A single sales factor, the payments and
settlement block (15a–21), and the informational NOL/NAM lines 23/24.
DIRECT-ENTRY: the Form 500DM decoupling totals (2b/3d) — the depreciation shadow
book is NOT built in v1; diagnostics carry Maryland's own §179 figures.
RED-DEFERRED: Form 500CR credits (W9); the worldwide-HQ election (D3); the
§10-305(b) capital-loss-carryback addition placement (W6, diagnosed not computed).

═══════════════════════════════════════════════════════════════════════════
CARRIED OPEN ITEMS
═══════════════════════════════════════════════════════════════════════════
U4  The page-2 apportionment gate ("factor is less than 1") and the booklet's
    gate ("unistate corporations skip to line 13") DISAGREE for a multistate
    corporation whose computed factor is exactly 1.000000. Built to the
    BOOKLET's unistate/multistate test; the face's phrasing treated as
    descriptive.
U5  Line 21 double-counts line 18 against line 20's own cap. Both transcribed
    literally; they reconcile only when line 20 sits at its cap.
[!] The face prints NO floor on line 14, but a negative line 13 would otherwise
    manufacture a refund through lines 17/21. The zero floor on the TAX is an
    INFERENCE, marked as such and diagnosed — it is not printed anywhere.

SAFETY GUARD — READY_TO_SEED stays False until Ken's Gate-1 SEED approval.
D-20 approved the SCOPE; the SEED is a separate gate.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import (
    AuthorityExcerpt, AuthorityFormLink, AuthoritySource, AuthoritySourceTopic,
    AuthorityTopic, RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)

# ═══════════════════════════════════════════════════════════════════════════
# GATE 1 CLEARED — flipped 2026-08-23 on Ken's DIRECT seed approval.
#
# Ken, in-session, in his own words: "approve the MD_500 seed."
#
# ⚠ Campaign D-20 approved the walk SCOPE (all 14 Maryland items). That was NOT
# this gate. This is the separate Gate-1 SEED approval, and it was answered
# DIRECTLY to the session doing the work — a relayed approval would not have
# opened it, per the standing campaign rule (D-17).
#
# Pre-flight run against PROD before flipping (campaign D-17 lessons):
#   · every CharField value measured against the REAL model max_length — CLEAN
#     (worst case topic_name 240/255; the class that fails ONLY on the live DB)
#   · MD TY2025 JurisdictionConformitySource row CONFIRMED PRESENT (rolling,
#     8 decoupled items) — D-8's "the row precedes the forms" order is intact
#     here, unlike Louisiana where it had to be inverted
#   · EXISTING_SOURCES_TO_REFERENCE codes verified to RESOLVE in prod — this
#     caught `MD_2025_500DM`, which does not exist; the real code is
#     `MD_2025_FORM_500DM`. Left uncorrected it would have been a dangling
#     reference, the D-25/O4 defect class.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_JURISDICTION = "MD"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# ── Verified constants, all TY-keyed ───────────────────────────────────────
# §10-105(b) verbatim: "The State income tax rate for a corporation is 8.25% of
# Maryland taxable income." Confirmed three more ways: Form 500 L14, Corporate
# Booklet Instruction 4, Form 500D worksheet L2.
# ⚠ VINTAGE CHECK: the 2025 BRFA (HB 352, Ch. 604) added a 6.50% top INDIVIDUAL
# bracket — that is what moved the PTET to 8.75% on the 511. It did NOT touch
# §10-105(b). The corporate rate is unchanged for TY2025.
MD_CORP_RATE: dict[int, str] = {2025: "0.0825"}

# Schedule A Column 3: "rounded to six places". Form 500's zero-factor entry is
# `.000000` — ⚠ Forms 510/511 print `.000001`. D-4: parameterised, NEVER
# harmonised. This constant is FORM-500-NAMESPACED for that reason.
MD500_APPORT_DECIMALS: dict[int, int] = {2025: 6}
MD500_ZERO_FACTOR: dict[int, str] = {2025: "0.000000"}

# §10-210.1(b)(3)(i)(1)/(2), restated on the Form 500DM face and re-read
# verbatim: "a taxpayer only is allowed to expense up to $25,000, reduced
# dollar-for-dollar by the amount over $200,000, of the cost of Section 179
# property."
# ⚠⚠ THESE ARE NOT THE FEDERAL OBBBA $2,500,000 / $4,000,000 AND NOT GEORGIA'S.
MD_179_LIMIT: dict[int, int] = {2025: 25000}
MD_179_PHASEOUT: dict[int, int] = {2025: 200000}


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed constant lookup. A new tax year staleness-invalidates every
    figure in this spec until re-verified (campaign CLAUDE.md)."""
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} — re-verify before extending the year.")
    return table[year]


def _md500_apportionment_factor(receipts_md, receipts_everywhere, year: int = FORM_TAX_YEAR):
    """Schedule A line 1 Column 3 → line 4 → page-2 line 11.

    TY2025 is a SINGLE SALES FACTOR: the phase-in completed after 12/31/2021, so
    there are NO weights to compute and no divisor to reduce. Schedule A still
    PRINTS property (block 2) and payroll (block 3), but for TY2025 they feed
    nothing on Form 500 — the face says, verbatim, "Report this factor on line 4
    unless you use a special apportionment formula or alternative apportionment
    formula", pointing at line 1 Column 3 (receipts) alone.

    ⚠ D-5 — NEVER AUTO-REWEIGHT. If the denominator is missing there is no
    factor to compute; return None and let the caller diagnose it. Do NOT
    silently substitute property/payroll, and do NOT fall back to 1.0.

    ⚠ D-4 — the ZERO factor is `.000000` on Form 500. Forms 510/511 print
    `.000001`. That divergence is REAL and deliberate; never harmonise them.
    """
    if receipts_everywhere is None or float(receipts_everywhere) == 0:
        return None
    factor = float(receipts_md) / float(receipts_everywhere)
    return round(factor, _yk(MD500_APPORT_DECIMALS, year))


def _md500_line6(line4, nol_carryforward):
    """Form 500 line 6, verbatim: "(If line 4 is less than or equal to zero,
    enter amount from line 4.) (If line 4 is greater than zero, subtract line 5
    from line 4 and enter result. If result is less than zero, enter zero.)"

    ⚠ The asymmetry is the point: a loss passes through UNTOUCHED (so it can
    reach lines 23/24), but a profit reduced by the NOL floors at zero.
    """
    l4 = float(line4)
    if l4 <= 0:
        return l4
    return max(0.0, l4 - float(nol_carryforward or 0))


def _md500_line24_nam(line6, line9):
    """Form 500 line 24, verbatim: "NAM generated in Current Year - Carried
    Forward/Back with Loss on Line 23 per Section 10-205(e) (If line 6 is less
    than zero AND line 9 is greater than zero, enter the amount from line 9 on
    line 24.)"

    ⚠⚠ D-6 — line 24 = LINE 9, and never line 9 ± the ADJUSTMENTS block. The
    bare-statute reading of §10-205(e)(1)(iii) ("the amount by which the sum of
    the addition modifications ... exceeds the sum of the subtraction
    modifications required under this title") looks like it sweeps in lines
    2a–3d as well, and it does NOT: AR 18 and AR 38 exclude the decoupling and
    §10-306.1/§10-307 items, and the form's own layout already encodes the
    answer by putting the modification blocks at 7a–8c and pointing line 24
    straight at line 9. Informational only — it is the input to a FUTURE year's
    line 7c, not to this year's tax.
    """
    return float(line9) if (float(line6) < 0 and float(line9) > 0) else 0.0


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # ⚠ Keep under 255 chars — the column is varchar(255) and Postgres enforces
    # it while SQLite does not (campaign D-17). The loader guards this too.
    ("md_corp_tax", "Maryland Form 500 C-corp: the flat 8.25% tax (Tax-Gen §10-105(b)), the §10-304 "
     "modified-income base, §10-310/§10-210.1 decoupling, the §10-402 single sales factor and "
     "worldwide-HQ election, §10-205(e) NAM, and the Form 500CR e-file mandate."),
]

# The state's conformity spine and shared MD sources are already seeded (campaign
# D-8/D-10); reference them rather than re-authoring, per the wave process.
# ⚠ These source_codes are VERIFIED to exist in RS prod (checked 2026-08-23 before
# the seed). A code that does not resolve becomes a DANGLING REFERENCE — the exact
# defect campaign D-25/O4 found in the live seeded `OR_20_S`, which references
# `OR_AP`/`OR_ASC_CORP` in 16 places while neither exists as a form. The Form 500DM
# source is registered as `MD_2025_FORM_500DM`, NOT `MD_2025_500DM`.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "MD_TG_10_210_1",
    "MD_2025_FORM_500DM",
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "MD_2025_500", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "2025 Maryland Form 500 — Corporation Income Tax Return",
        "citation": "Form 500, COM/RAD-001 06/25", "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/500.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["md_corp_tax"],
        "excerpts": [
            {
                "excerpt_label": "The 1a-14 spine, verbatim (FINAL TY2025 face, read positionally)",
                "excerpt_text": (
                    "1a 'Federal Taxable Income (Enter amount from Federal Form 1120 line 28 or Form 1120-C "
                    "line 25c.)' with entity boxes 1120 / 1120-REIT / 990T / Other, and 'IF 1120S, FILE ON "
                    "FORM 510'; 1b 'Special Deductions'; 1c 'Federal Taxable Income before net operating loss "
                    "deduction'. 2a/3a 'Section 10-306.1 related party transactions'; 2b/3d 'Decoupling "
                    "Modification Addition/Subtraction adjustment (Enter code letter(s) from instructions.)'; "
                    "3b dividends for a domestic corporation claiming foreign tax credits; 3c dividends from "
                    "related foreign corporations. 4 'Maryland Adjusted Federal Taxable Income before NOL "
                    "deduction is applied (Add lines 1c and 2c, and subtract line 3e.)'; 5 the adjusted "
                    "federal NOL carry-forward on a separate company basis; 6 'Maryland Adjusted Federal "
                    "Taxable Income (If line 4 is less than or equal to zero, enter amount from line 4.) (If "
                    "line 4 is greater than zero, subtract line 5 from line 4 and enter result. If result is "
                    "less than zero, enter zero.)'. 7a-7f addition modifications -> 7g; 8a-8b subtraction "
                    "modifications -> 8c; 9 'Total Maryland Modifications (Subtract line 8c from 7g. If less "
                    "than zero, enter negative amount.)'; 10 'Maryland Modified Income (Add lines 6 and 9.)'; "
                    "11 'Maryland apportionment factor (from page 4 of this form) (If factor is zero, enter "
                    ".000000.)'; 12 'Maryland apportionment income (Multiply line 10 by line 11.)'; 13 "
                    "'Maryland taxable income (from line 10 or line 12, whichever is applicable.)'; 14 'Tax "
                    "(Multiply line 13 by 8.25%.)'."
                ),
                "summary_text": (
                    "Form 500: 1a fed TI - 1b special deductions = 1c; +2c adjustments -3e = L4; -L5 NOL = L6; "
                    "+/- modifications = L9, L10 modified income; x L11 factor = L12; L13 taxable income x "
                    "8.25% = L14 tax. Zero factor enters as .000000."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule A + the zero-factor rule + the e-file banner (verbatim)",
                "excerpt_text": (
                    "'Schedule A - COMPUTATION OF APPORTIONMENT FACTOR (Applies only to multistate "
                    "corporations. See instructions.)' Columns: 'Column 1 TOTALS WITHIN MARYLAND', 'Column 2 "
                    "TOTALS WITHIN AND WITHOUT MARYLAND', 'Column 3 DECIMAL FACTOR (Column 1 divided by Column "
                    "2 rounded to six places)'. Block 1 Receipts 1(a)-1(g) -> 1(h) total; beneath it 'Report "
                    "this factor on line 4 unless you use a special apportionment formula or alternative "
                    "apportionment formula.' Block 2 Property 2a-2f -> 2g. Block 3 Payroll 3a-3b -> 3c. Line 4 "
                    "'Maryland apportionment factor Enter amount from Line 1 Column 3. ... (If factor is zero, "
                    "enter .000000 on line 11, page 2.)' Page-2 banner: 'You must file this form "
                    "electronically to claim business tax credits from Form 500CR.' Informational lines: 23 "
                    "'NOL generated in Current Year - Carryforward 20 years and carry back 2 years (farming "
                    "loss ONLY).'; 24 'NAM generated in Current Year - Carried Forward/Back with Loss on Line "
                    "23 per Section 10-205(e) (If line 6 is less than zero AND line 9 is greater than zero, "
                    "enter the amount from line 9 on line 24.)'"
                ),
                "summary_text": (
                    "Schedule A is three printed blocks but TY2025 uses receipts alone (line 1 Column 3), six "
                    "decimals, zero entered as .000000 on Form 500. Line 24 NAM = line 9 when line 6 < 0 and "
                    "line 9 > 0."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_105_B", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "Md. Code, Tax-General §10-105(b) — corporate income tax rate",
        "citation": "Md. Code Ann., Tax-Gen. §10-105(b)", "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-105",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["md_corp_tax"],
        "excerpts": [{
            "excerpt_label": "The rate, verbatim",
            "excerpt_text": "The State income tax rate for a corporation is 8.25% of Maryland taxable income.",
            "summary_text": "Flat 8.25% corporate rate. Unchanged for TY2025 — the 2025 BRFA (HB 352, Ch. 604) "
                            "added a 6.50% top INDIVIDUAL bracket and did not touch §10-105(b).",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MD_TG_10_402", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "Md. Code, Tax-General §10-402 — corporate apportionment and the "
                                            "worldwide-headquartered-company election",
        "citation": "Md. Code Ann., Tax-Gen. §10-402(a), (d)(3)", "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-402",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["md_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ D3 — the worldwide-HQ formula is an ELECTION ('may elect'), verbatim",
            "excerpt_text": (
                "(d)(3)(i) 'Each year a worldwide headquartered company that filed a federal corporate income "
                "tax return for the taxable year MAY ELECT to calculate its Maryland modified income ... using "
                "a 3-factor apportionment fraction: 1. the numerator of which is the sum of the property "
                "factor, the payroll factor, and twice the sales factor; and 2. the denominator of which is "
                "4.' (a) defines 'worldwide headquartered company' as a corporation in a group whose parent "
                "'(1) filed a Form 10-Q with the Securities and Exchange Commission for the quarterly period "
                "ending June 30, 2017; (2) has its principal executive office in the State; and (3)(i) employs "
                "at all times between July 1, 2017, and June 30, 2020, at least 500 full-time employees at the "
                "parent corporation's principal executive office that is located within the State; or (ii) if "
                "the parent corporation is a franchisor, ... at least 400 full-time employees'."
            ),
            "summary_text": "The worldwide-HQ three-factor formula is an ANNUAL TAXPAYER ELECTION, on a closed "
                            "2017-2020 eligibility fact pattern. The statute governs eligibility — AR 43's "
                            "summary omits the franchisor 400-FTE branch.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MD_AR_43", "source_type": "state_guidance", "source_rank": "secondary_official",
        "jurisdiction_code": "MD", "title": "Maryland Administrative Release 43 — Corporate Apportionment of Income",
        "citation": "Administrative Release No. 43 (October 27, 2022)", "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/"
                        "administrative-releases/income-and-estate-tax/ar_it43.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.5,
        "topics": ["md_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ D3 — AR 43 agrees the formula is ELECTIVE, twice (verbatim)",
            "excerpt_text": (
                "'Worldwide headquartered companies may elect to continue to use the three-factor formula with "
                "double-weighted sales.' and 'It also added provisions for optional three-factor apportionment "
                "for worldwide headquartered corporations.' AR 43 also records that the single-sales-factor "
                "phase-in ran from tax years 2018 to 2021 and is COMPLETE after 12/31/2021."
            ),
            "summary_text": "AR 43 — the booklet's OWN cited authority — says the worldwide-HQ formula is "
                            "elective/optional, contradicting the booklet that points to it.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MD_2025_CORP_BOOK", "source_type": "official_instructions", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "2025 Maryland Corporate Booklet — Form 500 instructions",
        "citation": "TY2025 Corporate Booklet (ModDate D:20260305113852)", "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/"
                        "corporate-booklet.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.0,
        "topics": ["md_corp_tax"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ D3 ERRATUM — the booklet says 'must use' and routes to AR 43, which refutes it",
                "excerpt_text": (
                    "Schedule A Instruction 2, verbatim: 'Rental/ leasing companies, financial institutions, "
                    "transportation companies, and worldwide headquartered companies MUST USE a Special "
                    "Apportionment Formula (see instruction 3 below), unless the Comptroller has accepted an "
                    "Alternative Apportionment Formula (see instruction 4 below).' Instruction 3, verbatim: "
                    "'... worldwide headquartered companies REQUIRED TO USE a Special Apportionment Formula "
                    "should refer to Administrative Release 43: Corporate Apportionment of Income.' ⚠ AR 43 "
                    "says the formula is OPTIONAL. The same 'must use' sentence appears verbatim in BOTH "
                    "TY2025 PTE booklets — a package-wide erratum, not a typo."
                ),
                "summary_text": "⚠ DO NOT 'CORRECT' THIS SPEC TO THE BOOKLET. The booklet's 'must use' "
                                "contradicts both §10-402(d)(3)(i) and AR 43 — the very release it cites. "
                                "Ken ruled the statute governs (campaign D-20 / walk D3).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The line-6/1c arithmetic, the unistate gate, the line-19 floor, §10-305(b)",
                "excerpt_text": (
                    "Line 1c: 'Subtract line 1b from line 1a. Enter the result in whole dollars.' Line 1a: "
                    "'Use a minus sign (-) in front of the number to indicate a loss.' Line 11 note: 'To be "
                    "completed by multistate corporations - unistate corporations skip to line 13. For "
                    "unistate corporations, all income is allocable to Maryland.' Line 19 adds the clause the "
                    "face omits: 'If negative amount, enter zero.' NET CAPITAL LOSSES: 'If a net capital loss "
                    "carryback is used to reduce federal taxable income, an addition modification is required "
                    "for the amount of the income reduction.' The tax rate: 'The tax rate is 8.25%.'"
                ),
                "summary_text": "Booklet-only rules the face does not print: the 1c whole-dollars rounding, the "
                                "line-1a minus sign for losses, the unistate/multistate gate, the line-19 zero "
                                "floor, and the §10-305(b) capital-loss-carryback addition.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_205_E", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "Md. Code, Tax-General §10-205(e) — net addition modification (NAM)",
        "citation": "Md. Code Ann., Tax-Gen. §10-205(e), via §10-306(b)(3)", "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-205",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["md_corp_tax"],
        "excerpts": [{
            "excerpt_label": "The NAM definition and the lesser-of, verbatim",
            "excerpt_text": (
                "(1)(iii) '\"Net addition modification\" means, for any taxable year, the amount by which the "
                "sum of the addition modifications required under this title exceeds the sum of the "
                "subtraction modifications allowed under this title.' (2) 'If a net operating loss deduction "
                "is allowed for the taxable year, the addition ... includes, for each loss year ... an amount "
                "equal to the LESSER OF: (i) the amount of the net operating loss deduction attributable to "
                "that loss year; or (ii) the amount by which the total net operating loss in the loss year is "
                "less than the sum of: 1. the net addition modification for that loss year; and 2. the "
                "cumulative net operating loss deductions attributable to that loss year allowed for the "
                "taxable year and all prior taxable years.'"
            ),
            "summary_text": "NAM is PER-LOSS-YEAR state carried across returns, with a lesser-of mixing "
                            "cumulative and single-year quantities. Line 7c is the consuming side (v1 "
                            "direct-entry); line 24 is the generating side (informational).",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MD_2025_500CRW", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "MD", "title": "2025 Maryland Form 500CRW — Waiver Request for Electronic Filing "
                                            "of Form 500CR",
        "citation": "Form 500CRW, COM/RAD-007-1 06/25", "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/500crw.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.4,
        "topics": ["md_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ W9 — waiver reason B names our own deferral, verbatim",
            "excerpt_text": (
                "Form 500CRW waiver reason B: 'Software does not support electronic filing of Form 500CR.' "
                "Form 500 page-2 banner: 'You must file this form electronically to claim business tax credits "
                "from Form 500CR.' ⚠ The PAPER Form 500CR no longer exists — 500crw.pdf is the only URL that "
                "serves it; 500cr.pdf 404s."
            ),
            "summary_text": "Because paper 500CR is gone and Form 500 must be e-filed to claim any business "
                            "credit, deferring 500CR from v1 means every MD business-credit client files a "
                            "waiver — citing reason B, which describes us exactly.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("MD_2025_500", "MD_500", "primary_form"),
    ("MD_2025_CORP_BOOK", "MD_500", "instructions"),
    ("MD_TG_10_105_B", "MD_500", "statute"),
    ("MD_TG_10_402", "MD_500", "statute"),
    ("MD_AR_43", "MD_500", "guidance"),
    ("MD_TG_10_205_E", "MD_500", "statute"),
    ("MD_2025_500CRW", "MD_500", "related_form"),
]


F_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "L1a Federal taxable income (1120 L28 / 1120-C L25c)",
     "data_type": "decimal", "required": False, "sort_order": 1,
     "notes": "⚠ MAY BE NEGATIVE. The booklet says 'Use a minus sign (-) in front of the number to indicate a "
              "loss.' The face's '(All entries must be positive amounts.)' banner sits over the ADJUSTMENT "
              "blocks (2a-3e, 7a-8c), NOT over line 1a. A blanket positive-only validation here would break "
              "every loss return."},
    {"fact_key": "federal_special_deductions", "label": "L1b Special deductions (1120 L29b / 1120-C L26b)",
     "data_type": "decimal", "required": False, "sort_order": 2},
    {"fact_key": "federal_entity_form", "label": "L1a entity type box — 1120 / 1120-REIT / 990T / Other",
     "data_type": "string", "required": False, "sort_order": 3,
     "notes": "Drives nothing computational, but 'Other:' is the dual-filing marker for an S corp with "
              "federal corporate-level tax (W10). The face reads 'IF 1120S, FILE ON FORM 510'."},
    {"fact_key": "related_party_addition", "label": "L2a §10-306.1 related party transactions — addition",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "decoupling_addition", "label": "L2b Decoupling Modification ADDITION (Form 500DM, code letters)",
     "data_type": "decimal", "required": False, "sort_order": 5,
     "notes": "v1 DIRECT-ENTRY from Form 500DM — the depreciation shadow book is not built. ⚠ D-7: two "
              "mechanisms with different lifespans feed this one line. Codes e/f (permanent, §10-210.1) and "
              "da/db/dc (ONE-YEAR, §10-108)."},
    {"fact_key": "related_party_subtraction", "label": "L3a §10-306.1 related party transactions — subtraction",
     "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "dividends_foreign_tax_credit", "label": "L3b Dividends, domestic corp claiming FTC (Sch C L18)",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "dividends_related_foreign", "label": "L3c Dividends from related foreign corps (Sch C L14, 16b, 16c)",
     "data_type": "decimal", "required": False, "sort_order": 8},
    {"fact_key": "decoupling_subtraction", "label": "L3d Decoupling Modification SUBTRACTION (Form 500DM, code letters)",
     "data_type": "decimal", "required": False, "sort_order": 9,
     "notes": "⚠ The subtraction code list has NO 'db' at all (codes J, K, CD, DA, DC, DE, DM, DP) and prints "
              "'DC. NEW RESERVED FOR TAX YEARS 2026 AND LATER.' — the booklet's own confirmation of the 500DM "
              "table's N/A for line 6 and Reserved for line 7."},
    {"fact_key": "federal_nol_carryforward", "label": "L5 Adjusted federal NOL carry-forward, separate company basis",
     "data_type": "decimal", "required": False, "sort_order": 10,
     "notes": "Entered as a POSITIVE amount, per the face. Includes FDSC carry-forward. Maryland has no NOL of "
              "its own — this is the federal NOL on a separate-company basis."},
    {"fact_key": "add_state_local_income_tax", "label": "L7a State and local income tax (§10-305(c))",
     "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "add_other_state_obligations", "label": "L7b Dividends/interest from other state or local obligations",
     "data_type": "decimal", "required": False, "sort_order": 12},
    {"fact_key": "add_nol_modification_recapture", "label": "L7c Net operating loss modification recapture (NAM)",
     "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "v1 DIRECT-ENTRY. §10-306(b)(3) → §10-205(e): a per-loss-year lesser-of that mixes cumulative and "
              "single-year quantities across returns. The face warns 'Do not enter NOL carryover.' Computed "
              "separately for EACH loss year and totalled."},
    {"fact_key": "add_domestic_production", "label": "L7d Domestic Production Activities Deduction",
     "data_type": "decimal", "required": False, "sort_order": 14},
    {"fact_key": "add_captive_reit_dividends", "label": "L7e Deduction for dividends paid by captive REIT (§10-306.2(b))",
     "data_type": "decimal", "required": False, "sort_order": 15},
    {"fact_key": "add_other_7f", "label": "L7f Other additions (code letters + attached schedules)",
     "data_type": "decimal", "required": False, "sort_order": 16,
     "notes": "⚠ W6 — this line also carries the §10-305(b) NET CAPITAL LOSS CARRYBACK addition, which has NO "
              "code letter anywhere in Maryland's list (A, B, C, D, G, H). Ken ruled: report here with NO code "
              "plus an attached schedule. DO NOT INVENT A CODE LETTER. ⚠ Code H is the PTET credit add-back "
              "(§10-306(b)(6) → §10-205(m)) — see W11."},
    {"fact_key": "capital_loss_carryback_used", "label": "§10-305(b) net capital loss carryback used to reduce federal TI?",
     "data_type": "boolean", "required": False, "sort_order": 17,
     "notes": "W6 flag. Drives the diagnostic that tells the preparer to include the addition on 7f with an "
              "attached schedule and no code letter."},
    {"fact_key": "sub_us_obligations", "label": "L8a Income from US Obligations",
     "data_type": "decimal", "required": False, "sort_order": 18},
    {"fact_key": "sub_other_8b", "label": "L8b Other subtractions (code letters + attached schedule)",
     "data_type": "decimal", "required": False, "sort_order": 19},
    {"fact_key": "is_multistate", "label": "Multistate corporation? (booklet gate — unistate skips to L13)",
     "data_type": "boolean", "required": False, "sort_order": 20,
     "notes": "⚠ U4 — built to the BOOKLET's unistate/multistate test ('unistate corporations skip to line 13'), "
              "NOT the page-2 banner's 'whose apportionment factor is less than 1'. A multistate corporation "
              "with a factor of exactly 1.000000 satisfies one gate and fails the other."},
    {"fact_key": "receipts_md", "label": "Sch A L1h Column 1 — total receipts WITHIN Maryland",
     "data_type": "decimal", "required": False, "sort_order": 21},
    {"fact_key": "receipts_everywhere", "label": "Sch A L1h Column 2 — total receipts within AND without Maryland",
     "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "special_apportionment_used", "label": "Sch A page-4 footer — special/alternative apportionment used?",
     "data_type": "boolean", "required": False, "sort_order": 23,
     "notes": "⚠ The checkbox sits at the BOTTOM of page 4, BELOW Schedule A line 4 — a page-4 FOOTER control, "
              "not a schedule header control. Same placement on Forms 510/511."},
    {"fact_key": "worldwide_hq_election", "label": "§10-402(d)(3) worldwide-HQ three-factor ELECTION made?",
     "data_type": "boolean", "required": False, "sort_order": 24,
     "notes": "⚠ D3 — an ANNUAL ELECTION, never forced and never inferred. Eligibility rests on a CLOSED "
              "2017-2020 fact pattern the software cannot verify. RED-deferred in v1."},
    {"fact_key": "estimated_tax_paid", "label": "L15a Estimated tax paid (Form 500D) + prior-year credit",
     "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "extension_payment", "label": "L15b Tax paid with an extension request (Form 500E)",
     "data_type": "decimal", "required": False, "sort_order": 26},
    {"fact_key": "nonrefundable_credits_aaa", "label": "L15c Nonrefundable business credits from Form 500CR Part AAA",
     "data_type": "decimal", "required": False, "sort_order": 27,
     "notes": "⚠ W9 — Form 500CR is RED-DEFERRED in v1. Direct-entry only, with a hard diagnostic."},
    {"fact_key": "refundable_credits_ddd", "label": "L15d Refundable business credits from Form 500CR Part DDD",
     "data_type": "decimal", "required": False, "sort_order": 28,
     "notes": "⚠ W11 — the ELECTING-PTE credit lands HERE (via 500CR Part CCC L10 → DDD) and carries a "
              "MANDATORY 7f code H add-back. Do NOT merge it with L15f."},
    {"fact_key": "pte_nonresident_tax_paid", "label": "L15f Nonresident tax paid on the corporation's behalf by PTEs",
     "data_type": "decimal", "required": False, "sort_order": 29,
     "notes": "⚠ W11 — FIVE LINES APART from L15d and treated differently: this one carries NO add-back. Same "
              "Maryland Schedule K-1 (510/511), different statutory section. Never merge the two."},
    {"fact_key": "mw506nrs_withheld", "label": "L15g Amount withheld on Form MW506NRS",
     "data_type": "decimal", "required": False, "sort_order": 30},
    {"fact_key": "amended_prior_payments", "label": "L15h If amending — total payments made with original + after",
     "data_type": "decimal", "required": False, "sort_order": 31},
    {"fact_key": "amended_prior_overpayment", "label": "L17a If amending — prior overpayment (all refunds issued)",
     "data_type": "decimal", "required": False, "sort_order": 32},
    {"fact_key": "interest_and_penalty", "label": "L18 Interest and/or penalty (Form 500UP or late-payment interest)",
     "data_type": "decimal", "required": False, "sort_order": 33},
    {"fact_key": "overpayment_to_estimated", "label": "L20 Overpayment applied to next year's estimated tax",
     "data_type": "decimal", "required": False, "sort_order": 34},
    {"fact_key": "is_amended_return", "label": "Amended return?",
     "data_type": "boolean", "required": False, "sort_order": 35},
    {"fact_key": "files_form_500_and_510", "label": "S corp with federal corporate-level tax (files BOTH 500 and 510/511)?",
     "data_type": "boolean", "required": False, "sort_order": 36,
     "notes": "W10, cross-module. Trigger is federal 1120-S line 23a (excess net passive income / LIFO "
              "recapture) or 23b (tax from Schedule D). ⚠ Neither Maryland booklet names the trigger lines, "
              "and neither addresses the 511-plus-500 case."},
]

F_RULES: list[dict] = [
    {"rule_id": "R-MD500-L1C", "title": "L1c Federal taxable income before NOL deduction", "rule_type": "calculation",
     "formula": "L1c = round(federal_taxable_income - federal_special_deductions)",
     "inputs": ["federal_taxable_income", "federal_special_deductions"], "outputs": ["L1c"], "sort_order": 1,
     "description": "⚠ The parenthetical '(Subtract line 1b from 1a)' is NOT on the form face — the face stops "
                    "at 'deduction'. The arithmetic is the BOOKLET's: 'Subtract line 1b from line 1a. Enter "
                    "the result in whole dollars.' The whole-dollars rounding is a booklet-only rule. L1a may "
                    "be NEGATIVE (booklet: 'Use a minus sign (-) ... to indicate a loss')."},
    {"rule_id": "R-MD500-L2C", "title": "L2c Total Maryland addition adjustments to federal taxable income",
     "rule_type": "calculation", "formula": "L2c = related_party_addition + decoupling_addition",
     "inputs": ["related_party_addition", "decoupling_addition"], "outputs": ["L2c"], "sort_order": 2,
     "description": "L2a §10-306.1(b)(2) related-member interest/intangible expense add-back + L2b the Form "
                    "500DM decoupling additions (§10-310 → §10-210.1). All entries positive."},
    {"rule_id": "R-MD500-L3E", "title": "L3e Total Maryland subtraction adjustments to federal taxable income",
     "rule_type": "calculation",
     "formula": "L3e = related_party_subtraction + dividends_foreign_tax_credit + dividends_related_foreign + decoupling_subtraction",
     "inputs": ["related_party_subtraction", "dividends_foreign_tax_credit", "dividends_related_foreign",
                "decoupling_subtraction"], "outputs": ["L3e"], "sort_order": 3,
     "description": "L3a §10-306.1(f)(1) + L3b §78 gross-up (Sch C L18) + L3c related foreign dividends (Sch C "
                    "L14, 16b, 16c) + L3d the Form 500DM decoupling subtractions. All entries positive."},
    {"rule_id": "R-MD500-L4", "title": "L4 Maryland adjusted federal taxable income before NOL",
     "rule_type": "calculation", "formula": "L4 = L1c + L2c - L3e",
     "inputs": [], "outputs": ["L4"], "sort_order": 4,
     "description": "Face, verbatim: 'Add lines 1c and 2c, and subtract line 3e.' §10-304 is the base."},
    {"rule_id": "R-MD500-L6", "title": "L6 Maryland adjusted federal taxable income (the asymmetric NOL gate)",
     "rule_type": "calculation",
     "formula": "L6 = L4 if L4 <= 0 else max(0, L4 - federal_nol_carryforward)",
     "inputs": ["federal_nol_carryforward"], "outputs": ["L6"], "sort_order": 5,
     "description": "⚠ THE ASYMMETRY IS THE POINT and must not be simplified. Face, verbatim: '(If line 4 is "
                    "less than or equal to zero, enter amount from line 4.) (If line 4 is greater than zero, "
                    "subtract line 5 from line 4 and enter result. If result is less than zero, enter zero.)' "
                    "A LOSS passes through UNTOUCHED so it can reach the informational lines 23/24; a PROFIT "
                    "reduced by the NOL floors at zero. Collapsing both branches into one max() would destroy "
                    "the loss and silently break lines 23 and 24."},
    {"rule_id": "R-MD500-L7G", "title": "L7g Total addition modifications", "rule_type": "calculation",
     "formula": ("L7g = add_state_local_income_tax + add_other_state_obligations + add_nol_modification_recapture "
                 "+ add_domestic_production + add_captive_reit_dividends + add_other_7f"),
     "inputs": ["add_state_local_income_tax", "add_other_state_obligations", "add_nol_modification_recapture",
                "add_domestic_production", "add_captive_reit_dividends", "add_other_7f"],
     "outputs": ["L7g"], "sort_order": 6,
     "description": "§10-305 / §10-306 additions. 7a §10-305(c) state and local income tax · 7b §10-305(d)(1) "
                    "→ §10-204(b) · 7c §10-306(b)(3) → §10-205(e) NAM recapture · 7d §10-305(d)(4) → "
                    "§10-204(i) · 7e §10-306.2(b) captive REIT · 7f other, by code letter. ⚠ 7f also carries "
                    "the §10-305(b) capital-loss carryback, which has NO code (W6), and code H the PTET credit "
                    "add-back §10-306(b)(6) → §10-205(m) (W11)."},
    {"rule_id": "R-MD500-L8C", "title": "L8c Total subtraction modifications", "rule_type": "calculation",
     "formula": "L8c = sub_us_obligations + sub_other_8b",
     "inputs": ["sub_us_obligations", "sub_other_8b"], "outputs": ["L8c"], "sort_order": 7,
     "description": "§10-307 / §10-308 subtractions. 8a US-obligation income; 8b other by code letter (the 8b "
                    "block also carries the free-text Maryland Cannabis Administration licence number field)."},
    {"rule_id": "R-MD500-L9", "title": "L9 Total Maryland modifications (may be negative)", "rule_type": "calculation",
     "formula": "L9 = L7g - L8c",
     "inputs": [], "outputs": ["L9"], "sort_order": 8,
     "description": "Face, verbatim: 'Subtract line 8c from 7g. If less than zero, enter negative amount.' ⚠ "
                    "L9 is the ONLY figure line 24 reads (D-6) — never L9 adjusted by the 2a-3d block."},
    {"rule_id": "R-MD500-L10", "title": "L10 Maryland modified income (§10-304)", "rule_type": "calculation",
     "formula": "L10 = L6 + L9",
     "inputs": [], "outputs": ["L10"], "sort_order": 9,
     "description": "Face: 'Add lines 6 and 9.' Booklet: 'THIS LINE MUST BE COMPLETED.'"},
    {"rule_id": "R-MD500-APPORT", "title": "L11 Maryland apportionment factor — SINGLE SALES FACTOR",
     "rule_type": "calculation",
     "formula": ("L11 = None if receipts_everywhere == 0 else round(receipts_md / receipts_everywhere, 6) ; "
                 "if L11 == 0: enter .000000"),
     "inputs": ["is_multistate", "receipts_md", "receipts_everywhere"], "outputs": ["L11"], "sort_order": 10,
     "description": "TY2025 is a SINGLE SALES FACTOR — the §10-402 phase-in completed after 12/31/2021, so "
                    "there are no weights to compute. Schedule A still PRINTS property (block 2) and payroll "
                    "(block 3); for TY2025 they feed nothing on Form 500. Column 3 is 'Column 1 divided by "
                    "Column 2 rounded to six places'. ⚠ D-4: the zero factor enters as `.000000` on Form 500 "
                    "— Forms 510/511 print `.000001`. NEVER harmonise the two. ⚠ D-5: NEVER auto-reweight — "
                    "a missing denominator yields NO factor, not a substituted one and not 1.0. ⚠ Maryland "
                    "has NO insignificant-denominator rule (searched; none found)."},
    {"rule_id": "R-MD500-L13", "title": "L13 Maryland taxable income (unistate vs multistate)",
     "rule_type": "calculation",
     "formula": "L12 = L10 * L11 ; L13 = L10 if not is_multistate else L12",
     "inputs": ["is_multistate"], "outputs": ["L12", "L13"], "sort_order": 11,
     "description": "Face: 'from line 10 or line 12, whichever is applicable.' ⚠ U4 — built to the BOOKLET's "
                    "gate ('To be completed by multistate corporations - unistate corporations skip to line "
                    "13. For unistate corporations, all income is allocable to Maryland.') and NOT to the "
                    "page-2 banner's 'whose apportionment factor is less than 1'. A multistate corporation "
                    "with a factor of exactly 1.000000 satisfies the booklet and fails the banner; the "
                    "banner's phrasing is treated as descriptive."},
    {"rule_id": "R-MD500-L14", "title": "L14 Tax — flat 8.25% (§10-105(b))", "rule_type": "calculation",
     "formula": "L14 = max(0, L13 * 0.0825)",
     "inputs": [], "outputs": ["L14"], "sort_order": 12,
     "description": "§10-105(b) verbatim: 'The State income tax rate for a corporation is 8.25% of Maryland "
                    "taxable income.' ⚠ THERE IS NO LOCAL OR COUNTY CORPORATE INCOME TAX — line 14 is the "
                    "whole tax. ⚠ THE ZERO FLOOR IS AN INFERENCE, not a printed rule: the face says only "
                    "'Multiply line 13 by 8.25%', but a negative line 13 would otherwise manufacture a refund "
                    "through lines 17 and 21. Flagged and diagnosed rather than assumed silently. ⚠ VINTAGE: "
                    "the 2025 BRFA (HB 352, Ch. 604) added a 6.50% top INDIVIDUAL bracket and moved the PTET "
                    "to 8.75% on the 511 — it did NOT touch §10-105(b)."},
    {"rule_id": "R-MD500-L15I", "title": "L15i Total payments and credits", "rule_type": "calculation",
     "formula": ("L15i = estimated_tax_paid + extension_payment + nonrefundable_credits_aaa + "
                 "refundable_credits_ddd + pte_nonresident_tax_paid + mw506nrs_withheld + amended_prior_payments"),
     "inputs": ["estimated_tax_paid", "extension_payment", "nonrefundable_credits_aaa", "refundable_credits_ddd",
                "pte_nonresident_tax_paid", "mw506nrs_withheld", "amended_prior_payments"],
     "outputs": ["L15i"], "sort_order": 13,
     "description": "Face: 'add lines 15a through 15h'. ⚠ W11 — 15d (electing-PTE credit, MANDATORY 7f code H "
                    "add-back) and 15f (nonresident PTE tax, NO add-back) both land here but are NOT "
                    "interchangeable upstream. 15e is a non-profit CHECKBOX, not an amount."},
    {"rule_id": "R-MD500-SETTLE", "title": "L16/L17 Balance due or overpayment", "rule_type": "calculation",
     "formula": "L16 = max(0, L14 - L15i) ; L17 = max(0, L15i - L14)",
     "inputs": [], "outputs": ["L16", "L17"], "sort_order": 14,
     "description": "Face: L16 'If line 14 exceeds line 15i, enter the difference.'; L17 'If line 15i exceeds "
                    "line 14, enter the difference.' Mutually exclusive by construction."},
    {"rule_id": "R-MD500-L19", "title": "L19 Total balance due — the peculiar arithmetic, transcribed literally",
     "rule_type": "calculation",
     "formula": "L19 = max(0, L14 + amended_prior_overpayment + interest_and_penalty - L15i)",
     "inputs": ["amended_prior_overpayment", "interest_and_penalty"], "outputs": ["L19"], "sort_order": 15,
     "description": "⚠ TRANSCRIBE LITERALLY — do not 'tidy' this. Face, verbatim: 'Add lines 14, 17a, and 18. "
                    "Subtract line 15i.' It re-adds the TAX (line 14), NOT the balance due (line 16), and "
                    "adds back any previously refunded overpayment (17a). The zero floor is the BOOKLET's "
                    "addition, which the face omits: 'If negative amount, enter zero.'"},
    {"rule_id": "R-MD500-L21", "title": "L21 Overpayment to be refunded", "rule_type": "calculation",
     "formula": ("L21 = (L17 - amended_prior_overpayment - interest_and_penalty) if is_amended_return "
                 "else (L17 - (interest_and_penalty + overpayment_to_estimated))"),
     "inputs": ["is_amended_return", "overpayment_to_estimated"], "outputs": ["L21"], "sort_order": 16,
     "description": "⚠ U5 — transcribed literally on BOTH branches, and they are known not to reconcile in "
                    "general. Line 20 is capped at 'lines 17 minus 17a and 18'; line 21 then computes 17 − (18 "
                    "+ 20). Read literally the two agree ONLY when line 20 sits at its cap. Face: 'Add lines "
                    "18 and 20, and subtract the total from line 17. (If amending, subtract lines 17a and 18 "
                    "from line 17.)'"},
    {"rule_id": "R-MD500-L23", "title": "L23 NOL generated in the current year (informational)",
     "rule_type": "calculation", "formula": "L23 = L6 if L6 < 0 else 0",
     "inputs": [], "outputs": ["L23"], "sort_order": 17,
     "description": "Face: 'NOL generated in Current Year - Carryforward 20 years and carry back 2 years "
                    "(farming loss ONLY). (If line 6 is less than zero, enter on line 23.)' ⚠ W8 — BUILT AS "
                    "PRINTED, with NO expiry encoded and no derived carryforward table. The '20 years' text "
                    "conflicts with the booklet's own rule that the Maryland NOL IS the federal NOL "
                    "(indefinite post-TCJA). ⚠ THE SUPPORT IS INFERENTIAL: AR 18 says 'Maryland follows the "
                    "carryback and carryfoward periods under federal law', but AR 18 is a JULY 2013 document, "
                    "five years pre-TCJA — authority for the principle, not for the period. Informational "
                    "only, which limits the damage."},
    {"rule_id": "R-MD500-L24", "title": "L24 NAM generated in the current year (informational)",
     "rule_type": "calculation", "formula": "L24 = L9 if (L6 < 0 and L9 > 0) else 0",
     "inputs": [], "outputs": ["L24"], "sort_order": 18,
     "description": "⚠⚠ D-6 — L24 = LINE 9 EXACTLY, never line 9 ± the ADJUSTMENTS block. The bare-statute "
                    "reading of §10-205(e)(1)(iii) appears to sweep in lines 2a-3d and does NOT: AR 18 and AR "
                    "38 exclude the decoupling and §10-306.1/§10-307 items, and the form's layout already "
                    "encodes the answer. Face, verbatim: '(If line 6 is less than zero AND line 9 is greater "
                    "than zero, enter the amount from line 9 on line 24.)' Informational — it is the input to "
                    "a FUTURE year's line 7c, not to this year's tax."},
]

F_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-MD500-L1C", "MD_2025_500", "primary", "L1a/1b/1c face labels"),
    ("R-MD500-L1C", "MD_2025_CORP_BOOK", "secondary", "the 1c arithmetic + whole-dollars rounding"),
    ("R-MD500-L2C", "MD_2025_500", "primary", "L2a/2b/2c face labels"),
    ("R-MD500-L2C", "MD_2025_FORM_500DM", "secondary", "L2b IS the Form 500DM addition carry-over"),
    ("R-MD500-L2C", "MD_TG_10_210_1", "secondary", "§ 10-210.1 via § 10-310 — the decoupling authority"),
    ("R-MD500-L3E", "MD_2025_500", "primary", "L3a-3e face labels"),
    ("R-MD500-L3E", "MD_2025_FORM_500DM", "secondary", "L3d IS the Form 500DM subtraction carry-over"),
    ("R-MD500-L4", "MD_2025_500", "primary", "L4 'Add lines 1c and 2c, and subtract line 3e.'"),
    ("R-MD500-L6", "MD_2025_500", "primary", "L6 the two-branch NOL gate, verbatim"),
    ("R-MD500-L7G", "MD_2025_500", "primary", "L7a-7g face labels"),
    ("R-MD500-L8C", "MD_2025_500", "primary", "L8a-8c face labels"),
    ("R-MD500-L9", "MD_2025_500", "primary", "L9 'If less than zero, enter negative amount.'"),
    ("R-MD500-L10", "MD_2025_500", "primary", "L10 'Add lines 6 and 9.'"),
    ("R-MD500-APPORT", "MD_TG_10_402", "primary", "§10-402 apportionment"),
    ("R-MD500-APPORT", "MD_2025_500", "secondary", "Schedule A six decimals + the .000000 zero rule"),
    ("R-MD500-APPORT", "MD_AR_43", "secondary", "the phase-in completed after 12/31/2021"),
    ("R-MD500-L13", "MD_2025_CORP_BOOK", "primary", "U4 — the unistate/multistate gate governs"),
    ("R-MD500-L14", "MD_TG_10_105_B", "primary", "the 8.25% rate, verbatim"),
    ("R-MD500-L14", "MD_2025_500", "secondary", "L14 'Multiply line 13 by 8.25%.'"),
    ("R-MD500-L15I", "MD_2025_500", "primary", "L15a-15i face labels"),
    ("R-MD500-SETTLE", "MD_2025_500", "primary", "L16/L17 face labels"),
    ("R-MD500-L19", "MD_2025_CORP_BOOK", "primary", "the 'If negative amount, enter zero' floor"),
    ("R-MD500-L19", "MD_2025_500", "secondary", "L19 'Add lines 14, 17a, and 18. Subtract line 15i.'"),
    ("R-MD500-L21", "MD_2025_500", "primary", "L21 both branches, verbatim (U5)"),
    ("R-MD500-L23", "MD_2025_500", "primary", "L23 as printed — no expiry encoded (W8)"),
    ("R-MD500-L24", "MD_TG_10_205_E", "primary", "§10-205(e) NAM"),
    ("R-MD500-L24", "MD_2025_500", "secondary", "L24 'enter the amount from line 9' (D-6)"),
]

F_LINES: list[dict] = [
    {"line_number": "MD500-1c", "description": "L1c Federal taxable income before NOL deduction",
     "line_type": "subtotal", "source_rules": ["R-MD500-L1C"], "sort_order": 1},
    {"line_number": "MD500-2c", "description": "L2c Total Maryland addition adjustments",
     "line_type": "subtotal", "source_rules": ["R-MD500-L2C"], "sort_order": 2},
    {"line_number": "MD500-3e", "description": "L3e Total Maryland subtraction adjustments",
     "line_type": "subtotal", "source_rules": ["R-MD500-L3E"], "sort_order": 3},
    {"line_number": "MD500-4", "description": "L4 Maryland adjusted federal taxable income before NOL",
     "line_type": "subtotal", "source_rules": ["R-MD500-L4"], "sort_order": 4},
    {"line_number": "MD500-6", "description": "L6 Maryland adjusted federal taxable income (after NOL gate)",
     "line_type": "subtotal", "source_rules": ["R-MD500-L6"], "sort_order": 5},
    {"line_number": "MD500-7g", "description": "L7g Total addition modifications",
     "line_type": "subtotal", "source_rules": ["R-MD500-L7G"], "sort_order": 6},
    {"line_number": "MD500-8c", "description": "L8c Total subtraction modifications",
     "line_type": "subtotal", "source_rules": ["R-MD500-L8C"], "sort_order": 7},
    {"line_number": "MD500-9", "description": "L9 Total Maryland modifications (may be negative)",
     "line_type": "subtotal", "source_rules": ["R-MD500-L9"], "sort_order": 8},
    {"line_number": "MD500-10", "description": "L10 Maryland modified income",
     "line_type": "subtotal", "source_rules": ["R-MD500-L10"], "sort_order": 9},
    {"line_number": "MD500-11", "description": "L11 Maryland apportionment factor (six decimals; zero = .000000)",
     "line_type": "calculated", "source_rules": ["R-MD500-APPORT"], "sort_order": 10},
    {"line_number": "MD500-12", "description": "L12 Maryland apportionment income (L10 x L11)",
     "line_type": "calculated", "source_rules": ["R-MD500-L13"], "sort_order": 11},
    {"line_number": "MD500-13", "description": "L13 Maryland taxable income (L10 or L12, whichever applies)",
     "line_type": "subtotal", "source_rules": ["R-MD500-L13"], "sort_order": 12},
    {"line_number": "MD500-14", "description": "L14 Tax (L13 x 8.25%) — the entire Maryland corporate tax",
     "line_type": "calculated", "source_rules": ["R-MD500-L14"], "sort_order": 13},
    {"line_number": "MD500-15i", "description": "L15i Total payments and credits",
     "line_type": "subtotal", "source_rules": ["R-MD500-L15I"], "sort_order": 14},
    {"line_number": "MD500-16", "description": "L16 Balance of tax due",
     "line_type": "calculated", "source_rules": ["R-MD500-SETTLE"], "sort_order": 15},
    {"line_number": "MD500-17", "description": "L17 Overpayment",
     "line_type": "calculated", "source_rules": ["R-MD500-SETTLE"], "sort_order": 16},
    {"line_number": "MD500-19", "description": "L19 Total balance due (L14 + L17a + L18 - L15i, floored at zero)",
     "line_type": "calculated", "source_rules": ["R-MD500-L19"], "sort_order": 17},
    {"line_number": "MD500-21", "description": "L21 Amount of overpayment TO BE REFUNDED",
     "line_type": "calculated", "source_rules": ["R-MD500-L21"], "sort_order": 18},
    {"line_number": "MD500-23", "description": "L23 NOL generated in current year (INFORMATIONAL ONLY)",
     "line_type": "calculated", "source_rules": ["R-MD500-L23"], "sort_order": 19},
    {"line_number": "MD500-24", "description": "L24 NAM generated in current year (INFORMATIONAL ONLY)",
     "line_type": "calculated", "source_rules": ["R-MD500-L24"], "sort_order": 20},
    {"line_number": "MD500-SchA1h", "description": "Schedule A L1h Total receipts — Columns 1 and 2",
     "line_type": "subtotal", "source_rules": ["R-MD500-APPORT"], "sort_order": 21},
    {"line_number": "MD500-SchA4", "description": "Schedule A L4 Maryland apportionment factor -> page 2 line 11",
     "line_type": "calculated", "source_rules": ["R-MD500-APPORT"], "sort_order": 22},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MD500_500CR_DEFERRED", "severity": "error",
     "title": "⚠ Form 500CR is not supported in v1 — a waiver is required to claim any business credit",
     "condition": "nonrefundable_credits_aaa > 0 or refundable_credits_ddd > 0",
     "message": "This version does not support Form 500CR. Maryland requires Form 500 to be filed "
                "ELECTRONICALLY to claim any business tax credit (Form 500 page-2 banner: 'You must file this "
                "form electronically to claim business tax credits from Form 500CR.'), and the PAPER Form "
                "500CR no longer exists. To claim these credits, file Form 500CRW - Waiver Request for "
                "Electronic Filing of Form 500CR - citing REASON B: 'Software does not support electronic "
                "filing of Form 500CR.' Any amount entered on line 15c or 15d must be computed outside this "
                "software and supported by the 500CR the waiver covers.",
     "notes": "W9 — Ken's business decision (campaign D-20), not a technical limit. The diagnostic names "
              "reason B deliberately so the preparer is handed the remedy instead of finding it at filing."},
    {"diagnostic_id": "D_MD500_WWHQ_ELECTION", "severity": "error",
     "title": "⚠ Worldwide-headquartered-company three-factor ELECTION is not computed in v1",
     "condition": "worldwide_hq_election == True",
     "message": "The §10-402(d)(3) worldwide-headquartered-company three-factor apportionment (property + "
                "payroll + TWICE sales, over 4) is NOT computed in this version. It is an ANNUAL TAXPAYER "
                "ELECTION - §10-402(d)(3)(i) says a qualifying company 'may elect', and Administrative "
                "Release 43 agrees twice ('may elect', 'optional three-factor apportionment'). ⚠ The TY2025 "
                "Corporate Booklet says such companies 'must use' a Special Apportionment Formula and then "
                "refers the reader to AR 43 - which contradicts it. The booklet is in error, and the same "
                "sentence appears in both PTE booklets. Eligibility also rests on a closed 2017-2020 fact "
                "pattern (a Form 10-Q for the quarter ending 6/30/2017, and 500 full-time employees - or 400 "
                "for a franchisor - at the Maryland principal executive office AT ALL TIMES from 7/1/2017 to "
                "6/30/2020) that this software cannot verify. Compute the election manually and enter the "
                "resulting factor as a special apportionment factor.",
     "notes": "D3 / campaign D-20. NEVER force this formula and NEVER infer the election."},
    {"diagnostic_id": "D_MD500_CAPLOSS_CARRYBACK", "severity": "warning",
     "title": "§10-305(b) net capital loss carryback addition — line 7f, no code letter, attach a schedule",
     "condition": "capital_loss_carryback_used == True",
     "message": "§10-305(b) requires an addition modification for a net capital loss carryback used to reduce "
                "federal taxable income, and the Corporate Booklet repeats it - but Maryland's line-7f code "
                "list (A, B, C, D, G, H) contains NO code for it, and no other line fits. Report the amount "
                "on line 7f with NO code letter and attach a schedule identifying it as the §10-305(b) net "
                "capital loss carryback addition. Do not use another code letter to make it fit.",
     "notes": "W6 — Ken ruled the placement (campaign D-20). The standing rule is: never invent a code letter."},
    {"diagnostic_id": "D_MD500_NEGATIVE_TAXABLE", "severity": "info",
     "title": "Maryland taxable income is negative — tax floored at zero (an inference, not a printed rule)",
     "condition": "L13 < 0",
     "message": "Line 13 is negative, so line 14 is reported as zero. ⚠ Note that Maryland prints NO floor on "
                "line 14 - the face says only 'Multiply line 13 by 8.25%'. The zero floor is applied because "
                "a negative line 14 would otherwise flow through lines 17 and 21 and manufacture a refund. "
                "This is a deliberate inference, recorded rather than assumed. The loss itself is carried on "
                "the informational lines 23 and 24.",
     "notes": "Carried open item. Flagged so a future reader knows it is inferred, not transcribed."},
    {"diagnostic_id": "D_MD500_NO_DENOMINATOR", "severity": "error",
     "title": "⚠ Apportionment denominator is zero or missing — no factor computed, and none substituted",
     "condition": "is_multistate == True and (receipts_everywhere is None or receipts_everywhere == 0)",
     "message": "Schedule A Column 2 (total receipts within and without Maryland) is zero or missing, so no "
                "apportionment factor can be computed. This software will NOT substitute the property or "
                "payroll factors and will NOT default the factor to 1.000000 - Maryland's single sales factor "
                "has no re-weighting rule and no insignificant-denominator rule. Supply the Schedule A "
                "receipts, or enter a special/alternative apportionment factor and check the page-4 footer box.",
     "notes": "D-5 — never auto-reweight. Maryland was searched for an insignificance rule; none exists."},
    {"diagnostic_id": "D_MD500_ZERO_FACTOR", "severity": "info",
     "title": "Apportionment factor is zero — enter .000000 on Form 500 (NOT .000001)",
     "condition": "L11 == 0",
     "message": "The computed Maryland apportionment factor is zero. Form 500 line 11 takes '.000000', "
                "verbatim from the face: '(If factor is zero, enter .000000.)' ⚠ Do NOT carry the Forms "
                "510/511 convention here - those forms print '.000001' in the same situation. The divergence "
                "between the corporate and pass-through forms is real and deliberate.",
     "notes": "D-4. The seeded load_md_pte.py holds the .000001 constant correctly and PTE-namespaced; "
              "MD_500 must simply not reuse it."},
    {"diagnostic_id": "D_MD500_UNISTATE_GATE", "severity": "info",
     "title": "Apportionment gate — the form face and the booklet do not use the same test",
     "condition": "is_multistate == True and L11 == 1",
     "message": "This return is multistate with an apportionment factor of exactly 1.000000. Maryland's two "
                "printed gates disagree in precisely this case: the Form 500 page-2 banner applies "
                "apportionment to corporations 'whose apportionment factor is less than 1', while the "
                "Corporate Booklet says 'To be completed by multistate corporations - unistate corporations "
                "skip to line 13.' This software follows the BOOKLET's unistate/multistate test and treats "
                "the 'less than 1' phrasing as descriptive. The computed result is identical either way when "
                "the factor is 1.000000; the note exists so the divergence is visible.",
     "notes": "U4 — carried open, not silently resolved."},
    {"diagnostic_id": "D_MD500_DUAL_FILING", "severity": "warning",
     "title": "S corp with federal corporate-level tax must file BOTH Form 500 and Form 510/511",
     "condition": "files_form_500_and_510 == True or federal_entity_form == 'Other'",
     "message": "An S corporation subject to federal income tax at the corporate level is also subject to "
                "Maryland corporation income tax and must file Form 500 IN ADDITION TO Form 510/511 "
                "(Corporate Booklet Instruction 1). The federal trigger is Form 1120-S line 23a (excess net "
                "passive income or LIFO recapture tax) or line 23b (tax from Schedule D). Use the 'Other:' "
                "entity box on line 1a. ⚠ Maryland's booklets name neither trigger line and neither addresses "
                "the 511-plus-500 combination - confirm the pairing manually.",
     "notes": "W10, cross-module with the PTE side. Both briefs confirm the gap from their own direction."},
    {"diagnostic_id": "D_MD500_PTE_CREDIT_SPLIT", "severity": "warning",
     "title": "⚠ The two PTE credits land five lines apart and only ONE carries an add-back",
     "condition": "refundable_credits_ddd > 0 and pte_nonresident_tax_paid > 0",
     "message": "Maryland has two distinct pass-through credits and they must not be merged. (1) NONRESIDENT "
                "PTE tax paid on the corporation's behalf goes on line 15f and carries NO addition "
                "modification. (2) The ELECTING-PTE (PTET) credit runs through Form 500CR Part CCC line 10 to "
                "Part DDD and onto line 15d, and it carries a MANDATORY addition on line 7f under code H "
                "(§10-306(b)(6) → §10-205(m)). They arrive on the same Maryland Schedule K-1 (510/511) but "
                "under different statutory sections. Claiming the PTET credit without the code H add-back "
                "understates Maryland tax.",
     "notes": "W11. Emitted as a typed modification for MD_500 to consume, not as prose."},
    {"diagnostic_id": "D_MD500_NO_COMBINED", "severity": "info",
     "title": "Maryland has NO combined reporting for TY2025 — separate returns only",
     "condition": "always (informational)",
     "message": "Maryland requires a SEPARATE Maryland return from each member of an affiliated group filing a "
                "consolidated federal return; there is no combined or consolidated Maryland filing of any "
                "kind for TY2025. Schedule B questions 6 and 7 are informational and feed nothing in this "
                "spec. ⚠ The recorded reason is that NO OPERATIVE RULE WAS FOUND - not that any rule expired. "
                "Unitary status remains live in §10-402(d), and mandatory combined reporting has been "
                "repeatedly introduced in Maryland without being enacted. Re-check at each session.",
     "notes": "D2 — Ken blessed the NEGATIVE as a ruling (campaign D-20). The Q7-vestigial rationale was "
              "WITHDRAWN as unsourced; do not restore it."},
    {"diagnostic_id": "D_MD500_DECOUPLE_LIFESPAN", "severity": "warning",
     "title": "⚠ Two decoupling mechanisms with DIFFERENT lifespans feed lines 2b and 3d",
     "condition": "decoupling_addition > 0 or decoupling_subtraction > 0",
     "message": "Form 500DM carries two legally distinct decoupling mechanisms and the Comptroller separated "
                "them on the form face. PART A (500DM lines 1-4: depreciation, NOL, original issue discount, "
                "discharge of business indebtedness) is PERMANENT decoupling under §10-210.1 via §10-310. "
                "PART B (500DM lines 5-7: §174A domestic R&E expensing, the §163(j) business-ATI "
                "calculation, and §168(n) depreciation - the OBBBA items) is a ONE-YEAR AUTOMATIC decoupling "
                "under §10-108, effective only 'for any taxable year that begins in the calendar year in "
                "which the amendment is enacted'. ⚠ ABSENT 2026 LEGISLATION, MARYLAND CONFORMS TO THOSE THREE "
                "PROVISIONS FOR TY2026 AND THE TY2025 ADDITIONS UNWIND AS SUBTRACTIONS - the forms already "
                "print 'RESERVED FOR TAX YEARS 2026 AND LATER'. ⚠⚠ IRC §168(k) and IRC §168(n) are DIFFERENT "
                "PROVISIONS on different footings and must NEVER be merged. Maryland's own §179 limit is "
                "$25,000, reduced dollar-for-dollar above $200,000 (§10-210.1(b)(3)(i)) - NOT the federal "
                "OBBBA $2,500,000/$4,000,000.",
     "notes": "D7 — TY2026 re-spec is calendared. The §168(k)/§168(n) warning is a standing flag for the "
              "depreciation engine."},
    {"diagnostic_id": "D_MD500_NAM_DIRECT_ENTRY", "severity": "info",
     "title": "Line 7c NAM recapture is direct-entry — a per-loss-year computation across returns",
     "condition": "federal_nol_carryforward > 0",
     "message": "An NOL deduction is claimed on line 5, so line 7c may require a net-addition-modification "
                "recapture under §10-306(b)(3) → §10-205(e). This version does not compute it: the rule is a "
                "LESSER-OF that mixes single-year and CUMULATIVE quantities and must be calculated SEPARATELY "
                "FOR EACH loss year and totalled, using per-loss-year state carried across returns. Enter the "
                "smaller of (a) the NOL deduction attributable to the loss year, or (b) the cumulative NOL "
                "deductions attributable to that loss year allowed this year and all prior years, plus the "
                "net addition modification for the loss year, less the total NOL for the loss year - each "
                "treated as positive, and zero if the combination is negative. Note: this is a MODIFICATION, "
                "not the net operating loss itself - do not enter the NOL carryover here.",
     "notes": "The module's second multi-year computation after line 5. Line 24 is the generating side."},
    {"diagnostic_id": "D_MD500_LINE21_U5", "severity": "info",
     "title": "Lines 20 and 21 are internally inconsistent unless line 20 sits at its cap",
     "condition": "overpayment_to_estimated > 0 and interest_and_penalty > 0",
     "message": "Both lines are transcribed exactly as Maryland prints them, and read literally they "
                "reconcile only when line 20 is at its own cap. Line 20 is capped at 'lines 17 minus 17a and "
                "18'; line 21 then computes line 17 less the total of lines 18 and 20 - so line 18 is charged "
                "against the refund twice when line 20 is below its cap. Verify the refund figure against the "
                "Comptroller's own calculation before relying on it.",
     "notes": "U5 — carried open. Do not 'fix' either line; both are literal transcriptions."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "MD500-A — unistate corporation, straight 8.25%", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"federal_taxable_income": 1000000, "federal_special_deductions": 0, "is_multistate": False},
     "expected_outputs": {"L1c": 1000000, "L4": 1000000, "L6": 1000000, "L10": 1000000, "L13": 1000000,
                          "L14": 82500},
     "notes": "The base case. Unistate, so line 11/12 are skipped entirely and L13 comes from L10. "
              "1,000,000 x 8.25% = 82,500. No county tax exists for corporations."},
    {"scenario_name": "MD500-B — multistate, single sales factor to six places", "scenario_type": "normal",
     "sort_order": 2,
     "inputs": {"federal_taxable_income": 5000000, "is_multistate": True, "receipts_md": 1234567,
                "receipts_everywhere": 10000000},
     "expected_outputs": {"L10": 5000000, "L11": 0.123457, "L12": 617285, "L13": 617285, "L14": 50926.01},
     "notes": "Column 1 / Column 2 rounded to SIX places: 1,234,567/10,000,000 = 0.1234567 -> 0.123457. "
              "5,000,000 x 0.123457 = 617,285. x 8.25% = 50,926.01. Property and payroll print on Schedule A "
              "but feed nothing for TY2025."},
    {"scenario_name": "MD500-C — the asymmetric line 6: a LOSS passes through untouched",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"federal_taxable_income": -400000, "federal_nol_carryforward": 250000,
                "add_state_local_income_tax": 60000, "is_multistate": False},
     "expected_outputs": {"L4": -400000, "L6": -400000, "L7g": 60000, "L9": 60000, "L10": -340000,
                          "L13": -340000, "L14": 0, "L23": -400000, "L24": 60000},
     "notes": "⚠ THE CRITICAL ASYMMETRY. L4 <= 0, so L6 = L4 UNTOUCHED and the NOL carryforward is NOT "
              "applied - the loss must survive to reach lines 23 and 24. L6 < 0 AND L9 > 0, so L24 = L9 = "
              "60,000 exactly (D-6: never L9 adjusted by the 2a-3d block). Tax floored at zero."},
    {"scenario_name": "MD500-D — profit reduced by NOL floors at zero", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"federal_taxable_income": 300000, "federal_nol_carryforward": 500000, "is_multistate": False},
     "expected_outputs": {"L4": 300000, "L6": 0, "L10": 0, "L13": 0, "L14": 0, "L23": 0, "L24": 0},
     "notes": "The other branch of line 6: L4 > 0, so L6 = max(0, 300,000 - 500,000) = 0. L6 is NOT negative, "
              "so line 23 stays empty - an unused NOL does not become a current-year loss."},
    {"scenario_name": "MD500-E — zero apportionment factor enters as .000000, never .000001",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"federal_taxable_income": 800000, "is_multistate": True, "receipts_md": 0,
                "receipts_everywhere": 4000000},
     "expected_outputs": {"L11": 0.0, "L12": 0, "L13": 0, "L14": 0, "zero_factor_entry": "0.000000"},
     "notes": "⚠ D-4 — Form 500 prints '.000000'; Forms 510/511 print '.000001' in the identical situation. "
              "The constants are form-namespaced and must never be harmonised."},
    {"scenario_name": "MD500-F — missing denominator yields NO factor (never a reweight, never 1.0)",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"federal_taxable_income": 900000, "is_multistate": True, "receipts_md": 500000,
                "receipts_everywhere": 0},
     "expected_outputs": {"L11": None, "diagnostic": "D_MD500_NO_DENOMINATOR"},
     "notes": "⚠ D-5 — never auto-reweight. Maryland has no insignificant-denominator rule and no re-weighting "
              "rule; a missing Column 2 produces no factor and a hard diagnostic, not a substituted one."},
    {"scenario_name": "MD500-G — modifications net negative", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"federal_taxable_income": 500000, "add_state_local_income_tax": 20000,
                "sub_us_obligations": 75000, "is_multistate": False},
     "expected_outputs": {"L7g": 20000, "L8c": 75000, "L9": -55000, "L10": 445000, "L13": 445000,
                          "L14": 36712.5},
     "notes": "L9 'If less than zero, enter negative amount' - the negative is carried, not floored. "
              "500,000 - 55,000 = 445,000 x 8.25% = 36,712.50."},
    {"scenario_name": "MD500-H — line 19's literal arithmetic on an amended return",
     "scenario_type": "edge", "sort_order": 8,
     "inputs": {"federal_taxable_income": 400000, "is_multistate": False, "is_amended_return": True,
                "estimated_tax_paid": 20000, "amended_prior_payments": 5000,
                "amended_prior_overpayment": 8000, "interest_and_penalty": 1200},
     "expected_outputs": {"L14": 33000, "L15i": 25000, "L16": 8000, "L19": 17200},
     "notes": "⚠ Line 19 re-adds the TAX (L14 33,000), not the balance due (L16 8,000), and adds back the "
              "previously refunded overpayment: 33,000 + 8,000 + 1,200 - 25,000 = 17,200. Transcribed "
              "literally, floored at zero per the booklet."},
    {"scenario_name": "MD500-I — 500CR credits entered while deferred", "scenario_type": "edge", "sort_order": 9,
     "inputs": {"federal_taxable_income": 600000, "is_multistate": False, "nonrefundable_credits_aaa": 15000},
     "expected_outputs": {"L14": 49500, "L15i": 15000, "L16": 34500,
                          "diagnostic": "D_MD500_500CR_DEFERRED"},
     "notes": "W9 — the amount is accepted and carried, but the hard diagnostic fires naming Form 500CRW "
              "reason B. The figure must be computed outside this software."},
    {"scenario_name": "MD500-J — worldwide-HQ election is never forced", "scenario_type": "edge", "sort_order": 10,
     "inputs": {"federal_taxable_income": 2000000, "is_multistate": True, "receipts_md": 500000,
                "receipts_everywhere": 2000000, "worldwide_hq_election": True},
     "expected_outputs": {"L11": 0.25, "L13": 500000, "L14": 41250,
                          "diagnostic": "D_MD500_WWHQ_ELECTION"},
     "notes": "⚠ D3 — the spec computes the ORDINARY single sales factor (0.25) and RED-defers the election "
              "rather than applying the three-factor formula. The booklet's 'must use' is an erratum; the "
              "statute and AR 43 both say 'may elect'. Never forced, never inferred."},
]

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "MD_500",
            "form_title": "Maryland Form 500 — Corporation Income Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP, the 45-state campaign C-corp sweep. Maryland's C-corp return: flat 8.25% "
                "(§10-105(b)) on Maryland taxable income; federal TI before NOL/special deductions -> "
                "§10-306.1 and Form 500DM adjustments -> separate-company federal NOL -> §10-305/306/307/308 "
                "modifications -> SINGLE SALES FACTOR apportionment (§10-402, phase-in complete) -> 8.25%. "
                "⚠ NO election and NO branch — do not port the PTE 510/511 election machinery. ⚠ NO county "
                "or local corporate tax. ⚠ Zero factor is .000000 here and .000001 on 510/511 — never "
                "harmonise. v1 RED-defers Form 500CR (W9) and the worldwide-HQ election (D3); Form 500DM "
                "totals are direct-entry. Walk closed at campaign D-19 + D-20 (2026-08-23)."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MD500-SPINE", "title": "The Form 500 spine: 1c -> 4 -> 6 -> 10 -> 13 -> 14",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "L1c = 1a - 1b; L4 = 1c + 2c - 3e; L6 applies the asymmetric NOL gate; L10 = 6 + 9; L13 "
                    "is 10 or 12; L14 = 13 x 8.25%. §10-105(b) is the only rate and there is no county or "
                    "local corporate income tax in Maryland.",
     "definition": {"rule": "R-MD500-L14", "check": "L14 == max(0, L13 * 0.0825)"}},
    {"assertion_id": "FA-MD500-L6GATE", "title": "Line 6 is ASYMMETRIC — a loss passes through, a profit floors",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "⚠ If L4 <= 0 then L6 = L4 EXACTLY, with the NOL carryforward NOT applied — the loss must "
                    "survive to reach lines 23/24. If L4 > 0 then L6 = max(0, L4 - L5). Collapsing the two "
                    "branches into a single max() destroys the loss and silently empties lines 23 and 24.",
     "definition": {"rule": "R-MD500-L6", "check": "L6 == (L4 if L4 <= 0 else max(0, L4 - L5))"}},
    {"assertion_id": "FA-MD500-NAM", "title": "Line 24 NAM = line 9 exactly, never line 9 +/- the adjustments",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠ D-6. L24 = L9 when L6 < 0 AND L9 > 0, otherwise zero. The bare-statute reading of "
                    "§10-205(e)(1)(iii) appears to sweep in lines 2a-3d and does NOT — AR 18 and AR 38 "
                    "exclude the decoupling and §10-306.1/§10-307 items, and the form's own layout already "
                    "encodes it. Informational: it feeds a FUTURE year's line 7c, never this year's tax.",
     "definition": {"rule": "R-MD500-L24", "check": "L24 == (L9 if (L6 < 0 and L9 > 0) else 0)"}},
    {"assertion_id": "FA-MD500-ZEROFAC", "title": "Zero apportionment factor is .000000 on Form 500",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠ D-4. Form 500 line 11 takes '.000000' when the factor is zero; Forms 510/511 take "
                    "'.000001' in the identical situation. The two constants are form-namespaced and must "
                    "NEVER be harmonised — this is one of the three proofs behind the campaign's standing "
                    "'never clone a sibling form's line numbers' convention (D-18/G4).",
     "definition": {"rule": "R-MD500-APPORT", "check": "L11 == 0 -> printed '.000000' (NOT '.000001')"}},
    {"assertion_id": "FA-MD500-NOREWT", "title": "A missing denominator NEVER reweights and never defaults to 1.0",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "⚠ D-5. Maryland's single sales factor has no re-weighting rule and no "
                    "insignificant-denominator rule (searched; none found). If Schedule A Column 2 is zero or "
                    "missing there is NO factor — the spec returns none and raises a hard diagnostic. It must "
                    "never substitute property or payroll, and never fall back to a factor of 1.0.",
     "definition": {"rule": "R-MD500-APPORT", "check": "receipts_everywhere == 0 -> factor is None + D_MD500_NO_DENOMINATOR"}},
    {"assertion_id": "FA-MD500-PTESPLIT", "title": "The two PTE credits stay on separate lines with separate treatment",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 6,
     "description": "⚠ W11. Nonresident PTE tax -> line 15f, NO add-back. Electing-PTE (PTET) credit -> Form "
                    "500CR Part CCC L10 -> Part DDD -> line 15d, WITH a mandatory line 7f code H addition "
                    "(§10-306(b)(6) → §10-205(m)). Same Maryland Schedule K-1 (510/511), different statutory "
                    "sections. Merging them understates Maryland tax.",
     "definition": {"rule": "R-MD500-L15I", "check": "15d and 15f are distinct inputs; only 15d triggers the 7f code H add-back"}},
]


class Command(BaseCommand):
    help = ("Load the MD_500 spec (Maryland Corporation Income Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval flips READY_TO_SEED.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad MD_500 spec (Maryland Corporation Income Tax Return, TY2025)\n"))
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
        """⚠ Pinned to the GATE MECHANISM, not to the sentinel's current value.

        The campaign has now watched a harness check go red the moment Ken
        approved something FIVE separate times (campaign D-17). The lesson each
        time was identical: assert that the gate WORKS, never what the gate
        currently holds. So this guard refuses on an unset sentinel OR on a
        hollow spec, and the harness tests the refusal itself rather than
        asserting `READY_TO_SEED is False`.
        """
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
                "\nREFUSING TO SEED MD_500: not cleared to seed.\n\n"
                "Campaign D-20 approved the Maryland walk SCOPE (all 14 items). That is NOT the seed\n"
                "gate. Ken must give the Gate-1 SEED approval DIRECTLY — a relayed approval never\n"
                "opens a human gate.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\nEmpty:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            if len(name) > 255:
                raise CommandError(f"topic_name for {code!r} is {len(name)} chars — the column is 255. "
                                   "(This class of overflow passes every local check and fails only on the "
                                   "live database — campaign D-17.)")
            _, created = AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
            ct += 1 if created else 0
        self.stdout.write(f"Topics: {ct} new ({len(AUTHORITY_TOPICS)} in batch)")

    def _load_sources(self) -> dict:
        sources: dict = {}
        for src_data in AUTHORITY_SOURCES:
            src_data = dict(src_data)
            excerpts_data = src_data.pop("excerpts", [])
            topic_codes = src_data.pop("topics", [])
            source, _ = AuthoritySource.objects.update_or_create(
                source_code=src_data["source_code"], defaults=src_data)
            sources[source.source_code] = source
            for exc in excerpts_data:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=source, excerpt_label=exc["excerpt_label"], defaults=exc)
            for tc in topic_codes:
                topic = AuthorityTopic.objects.filter(topic_code=tc).first()
                if topic:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=source, authority_topic=topic)
        missing = []
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
            else:
                missing.append(code)
        if missing:
            self.stdout.write(self.style.WARNING(
                f"  referenced sources not yet in this database: {', '.join(missing)} "
                "(expected when running against a throwaway validation DB)"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]},
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']}")
        return form

    def _upsert_facts(self, form, facts):
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self._prune(FormFact.objects.filter(tax_form=form).exclude(
            fact_key__in=[f["fact_key"] for f in facts]), "facts")
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self._prune(FormRule.objects.filter(tax_form=form).exclude(
            rule_id__in=[r["rule_id"] for r in rules_data]), "rules")
        self.stdout.write(f"  {len(created)} rules")
        return created

    def _upsert_authority_links(self, rules, sources, rule_links):
        ct = 0
        for rule_id, source_code, level, note in rule_links:
            rule, source = rules.get(rule_id), sources.get(source_code)
            if rule and source:
                RuleAuthorityLink.objects.get_or_create(
                    form_rule=rule, authority_source=source,
                    defaults={"support_level": level, "relevance_note": note})
                ct += 1
        self.stdout.write(f"  {ct} authority links")

    def _upsert_lines(self, form, lines):
        for ln in lines:
            ln = dict(ln)
            FormLine.objects.update_or_create(tax_form=form, line_number=ln.pop("line_number"), defaults=ln)
        self._prune(FormLine.objects.filter(tax_form=form).exclude(
            line_number__in=[l["line_number"] for l in lines]), "lines")
        self.stdout.write(f"  {len(lines)} lines")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(
                tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self._prune(FormDiagnostic.objects.filter(tax_form=form).exclude(
            diagnostic_id__in=[d["diagnostic_id"] for d in diagnostics]), "diagnostics")
        self.stdout.write(f"  {len(diagnostics)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(
                tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self._prune(TestScenario.objects.filter(tax_form=form).exclude(
            scenario_name__in=[s["scenario_name"] for s in scenarios]), "test scenarios")
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _prune(self, qs, label):
        """Delete rows this loader no longer declares.

        [Campaign D-16] Every upsert here keys on a NAME (fact_key / rule_id /
        line_number / diagnostic_id / scenario_name) with update_or_create, so
        RENAMING a row creates a second row and leaves the original live — the
        NC reseed shipped a repealed pre-2023 rule ALONGSIDE its replacement
        before this was added. New loaders carry it from birth.
        """
        n = qs.count()
        if n:
            qs.delete()
            self.stdout.write(self.style.WARNING(f"  pruned {n} stale {label}"))

    def _upsert_form_links(self, sources):
        for sc, fc, lt in AUTHORITY_FORM_LINKS:
            src = sources.get(sc) or AuthoritySource.objects.filter(source_code=sc).first()
            if src:
                AuthorityFormLink.objects.get_or_create(
                    authority_source=src, form_code=fc, link_type=lt, defaults={"note": f"{sc} -> {fc}"})

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 66)
        self.stdout.write("MD_500 loaded (TY2025 ONLY — every figure is TY-keyed).")
        self.stdout.write(f"  MD_500: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write(f"  Authority sources: {len(AUTHORITY_SOURCES)} "
                          f"(+{len(EXISTING_SOURCES_TO_REFERENCE)} referenced)")
        self.stdout.write("=" * 66)
