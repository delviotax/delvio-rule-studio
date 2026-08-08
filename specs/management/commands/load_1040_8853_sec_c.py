"""Load the 8853_SEC_C spec — Form 8853 Section C, Long-Term Care Insurance Contracts.

Ken ruled the scope at s224 (delvio-tax DECISIONS.md, "Scope + gate rulings" item 4):
**Section C ONLY is in season-one scope.** Form 8853 is two populations stapled
together — Sections A/B (Archer MSA and Medicare Advantage MSA) are nearly
extinct; Section C is driven by a Form 1099-LTC with the per-diem box checked and
is "the half that actually arrives in an aging client base." Build the
1099-LTC → Section C chain; leave the Archer sections out. Ken re-confirmed the
lane at s232 (spec-first, this session).

THE GAP (verify-first, 2026-08-08):
  - No RS spec existed: /api/forms/lookup/8853/export/ 404s, nothing in
    delvio-tax/server/specs/, and no source brief in this repo.
  - The app has NO Form 8853 compute, no model, no field map, no PDF template
    (`resources/irs_forms/2025/` has no f8853; it is absent from
    forms_manifest.json).
  - Schedule 1 line 8e ALREADY EXISTS as a KEYED currency line, seeded
    "Income from Form 8853" (seed_sch_1.py), and form_manifest.py ALREADY
    declares AttachmentRequirement("Form 8853") on it —
    tests/test_form_manifest.py pins the comment "Form 8853 — never generated".
    So today an LTC client's taxable payments must be hand-keyed onto 8e and the
    manifest correctly reports a required attachment the app cannot produce.

⚠⚠ THE CENTRAL DESIGN FINDING — LINE 8e IS A COMPOSED LINE, AND THE IRS'S OWN
SCHEMA SAYS SO. The MeF element behind Schedule 1 line 8e is
`TotArcherMSAMedcrLTCAmt` (efile/composition/mappers/y2025/builder.py) — Total
**Archer MSA / Medcr / LTC** Amount. One line carries Section A, Section B and
Section C. i8853 confirms it from the other direction (an Archer MSA deemed-loan
is also reported "as income on Schedule 1 (Form 1040), line 8e"). This is the
s230 Schedule-K-13g situation exactly, and DECISIONS.md's ruling governs: **a
shared line's writer is a REGISTRY, not whichever form got there first.** v1
therefore composes 8e = (Section C computed component) + (preparer-keyed A/B
residual), so a later Sections A/B build joins as one more component instead of
silently overwriting Section C. Ken confirms this shape at Gate 1.

LAW VERIFIED 2026-08-08 against primary sources (fetched, not memory):
  - IRC §7702B(d)(1) verbatim: the excess of (A) qualified-contract periodic
    payments plus (B) the §101(g) payments, over the per diem limitation, is
    includible "without regard to section 72". (A) + (B) IS face line 20 — the
    statutory reason chronically-ill ADB shares the LTC limitation.
  - **IRC §7702B(d)(2) verbatim — AND IT CORRECTED THIS SPEC.** The limitation is
    "the **excess (if any)** of— (A) the greater of— (i) the dollar amount … or
    (ii) the costs incurred …, over (B) the aggregate payments received as
    reimbursements". That is face lines 21/22 → 23 → less 24 → 25 in one
    sentence — but "excess (if any)" is the Code's floor-at-zero idiom, and the
    FACE PRINTS NO FLOOR ON LINE 25 (it prints one only on line 26).
    ⚠⚠ This spec was first drafted with line 25 UNFLOORED, on the strength of the
    face plus an LII fetch that returned only a paraphrase with the phrase
    dropped. A second fetch from uscode.house.gov caught it. The defect was
    live: with line 20 = 10,000 and reimbursements driving line 25 to −5,000,
    line 26 came out 15,000 — taxing half again more than the taxpayer ever
    received. Pinned by scenario T14 and by the integrity gate.
    *The lesson, again: a paraphrase is not a verbatim, and the face is not the
    statute.*
  - IRC §7702B(d)(3)(A) verbatim: "all persons receiving periodic payments
    described in paragraph (1) with respect to the same insured shall be treated
    as 1 person"; (d)(3)(B) allocates the limitation "first to the insured and
    any remaining limitation shall be allocated among the other such persons in
    such manner as the Secretary shall prescribe."
  - IRC §7702B(d)(4): the statutory baseline is "$175 per day (or the equivalent
    amount in the case of payments on another periodic basis)"; (d)(5) indexes it
    by the §213(d)(10) mechanism.
  - **Rev. Proc. 2024-40, §2.62 verbatim**: "For calendar year 2025, the stated
    dollar amount of the per diem limitation under § 7702B(d)(4) … is $420."
    The 2025 face PRINTS $420 on line 21, and i8853's Example 1 footnote cites
    this exact section. Three independent confirmations of the same constant.
    ⚠ §2.62 is a CALENDAR-year amount while the Rev. Proc.'s §3.01 effective
    date speaks of "taxable years beginning in 2025" — immaterial for individuals
    but recorded rather than smoothed over.
    ⚠ NOT to be confused with §3.28 (eligible LTC PREMIUMS, the §213(d)(10) age
    band table already in delvio-tax DECISIONS.md) — a different provision on the
    other half of the same subject. The premium cap limits a DEDUCTION; §7702B(d)
    limits an EXCLUSION.
  - IRC §101(g)(1): accelerated death benefits on the life of a TERMINALLY ill
    insured are excludable; §101(g)(3) limits the CHRONICALLY ill case to the
    §7702B treatment (costs incurred, not compensated by insurance, for qualified
    LTC services, and the contract must meet §7702B(b)(1)(B)).
  - i8853 (2025) Section C: the Filing Requirements flowchart, both LTC-period
    methods, the Multiple Payees allocation, the pre-August-1-1996 reimbursement
    carve-out, and TWO fully worked published examples (transcribed verbatim into
    scenarios T1-T3 below — an IRS-published answer key is worth more than any
    example I could invent).

v1 SCOPE (every limit is a DECLARED diagnostic, never a silent gap):
  - ONE LTC period per Section C. More than one period requires separate
    Sections C with lines 18-26 duplicated (i8853 line 18 Caution) →
    D_8853C_MULTI_PERIOD holds.
  - Multiple Payees (line 15 = Yes) is NOT computed → D_8853C_MULTIPAYEE_HOLD.
    The aggregate statement, the shared-limitation allocation and the attachment
    are a unit of their own. ⚠ CHECK THE SIGN: computing a FULL limitation for a
    SHARED one would make line 25 too large and line 26 too small — it would
    UNDER-report taxable income. Refusing is the conservative direction.
  - Sections A/B (Archer / Medicare Advantage MSA) are out of scope by Ken's
    ruling; their 8e component stays preparer-keyed. Form 8889 line 4 stays a
    keyed figure guarded by the existing D_8889_ARCHER, which s224 already ruled
    is the correct treatment for a handful of returns.
  - 1040 only. The 1040-NR destination (Schedule NEC line 12, literal "LTC")
    is specced in R-8853C-DEST but not built — D_8853C_NR_UNWIRED.

SAFETY GUARD: READY_TO_SEED stays False until Ken's Gate-1 review walk.
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


READY_TO_SEED = False  # Gate 1: flip ONLY after Ken's review walk. Never unattended.


FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_ENTITY_TYPES = ["1040"]
FORM_STATUS = "draft"


# ═══════════════════════════════════════════════════════════════════════════
# THE MATH — face lines 17-26, straight off the SHA-pinned 2025 f8853.
# The app's build leg re-types this independently; they share no code, so a
# transcription slip on either side shows up as a scenario failure.
#
#   line 20 = line 18 + line 19
#   line 21 = PER_DIEM_RATE_2025 (420) x days in the LTC period
#   line 23 = MAX(line 21, line 22)          <- §7702B(d)(2)(A) "the greater of"
#   line 25 = MAX(0, line 23 - line 24)      <- §7702B(d)(2) "the EXCESS (IF ANY) of
#                                               (A) ... over (B)" = a floor at zero
#   line 26 = MAX(0, line 20 - line 25)      <- §7702B(d)(1) the excess
#
# ⚠⚠ THE FLOOR ON LINE 25 IS STATUTORY AND THE FACE DOES NOT PRINT IT. Line 26
# carries an explicit "If zero or less, enter -0-"; line 25 says only "Subtract
# line 24 from line 23". But §7702B(d)(2) defines the limitation as "the excess
# (if any) of (A) ... over (B)", and "excess (if any)" is the Code's floor-at-zero
# idiom. Without the floor a negative line 25 makes line 26 EXCEED line 20 — i.e.
# it taxes more than the taxpayer ever received (line 20 = 10,000 with line 25 =
# -5,000 gives 15,000 taxable). Reachable whenever reimbursements exceed the
# greater of the dollar limit and the costs, e.g. a 1-day contract period with
# low costs and a large expected reimbursement. Pinned by scenario T14.
#
# The terminally-ill short circuit (face note under line 16): if line 16 = Yes
# AND the only payments received were accelerated death benefits paid BECAUSE
# the insured was terminally ill, skip lines 17-25 and enter -0- on line 26.
# ═══════════════════════════════════════════════════════════════════════════

from decimal import Decimal  # noqa: E402

# Rev. Proc. 2024-40 §2.62 — the §7702B(d)(4) per diem limitation for CY2025.
# Also PRINTED on the 2025 face at line 21 and footnoted in i8853 Example 1.
PER_DIEM_RATE_2025 = Decimal("420")

# 2025 is not a leap year. A period cannot be shorter than 1 day (the Contract
# Period method's daily-benefit case) nor longer than the year.
DAYS_IN_YEAR_2025 = 365


def _D(x):
    return Decimal(str(x if x is not None else 0))


def compute_8853_sec_c(
    line18_qualified_per_diem=0,
    line19_adb_chronically_ill=0,
    ltc_period_days=0,
    line22_costs_incurred=0,
    line24_reimbursements=0,
    per_diem_rate=PER_DIEM_RATE_2025,
    terminally_ill_adb_only=False,
) -> dict:
    """Form 8853 Section C lines 20-26 for ONE insured, ONE LTC period.

    Derives nothing the face does not derive. Multiple Payees and multi-period
    returns are refused upstream (R-8853C-MULTIPAYEE / R-8853C-PERIOD), not
    approximated here.
    """
    # Face note under line 16 / i8853 Multiple Payees opening paragraph.
    if terminally_ill_adb_only:
        return {
            "line20": Decimal("0"), "line21": Decimal("0"), "line23": Decimal("0"),
            "line25": Decimal("0"), "line26": Decimal("0"), "skipped_17_25": True,
        }

    line20 = _D(line18_qualified_per_diem) + _D(line19_adb_chronically_ill)
    line21 = _D(per_diem_rate) * _D(ltc_period_days)
    line23 = max(line21, _D(line22_costs_incurred))       # §7702B(d)(2)(A) greater-of
    # "the EXCESS (IF ANY) of (A) ... over (B)" — statutory floor, not on the face.
    line25 = max(Decimal("0"), line23 - _D(line24_reimbursements))
    line26 = max(Decimal("0"), line20 - line25)           # §7702B(d)(1) the excess
    return {
        "line20": line20, "line21": line21, "line23": line23,
        "line25": line25, "line26": line26, "skipped_17_25": False,
    }


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("ltc_per_diem_exclusion",
     "§7702B(d) per diem limitation on the exclusion for periodic long-term care "
     "benefits; §101(g) accelerated death benefits; the multiple-payee shared "
     "limitation; Form 8853 Section C and its Form 1099-LTC source rows"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "RP_2024_40",         # the $420 (load_1040_spine); §2.62 excerpt added below
    "IRS_2025_SCH1_FORM",  # the line 8e destination
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRC_7702B_D",
        "source_type": "code_section",  # the VALID SourceType — see the enum note in the RS agenda
        "source_rank": "controlling",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §7702B(d) — Aggregate payments in excess of limits (the LTC per diem limitation)",
        "citation": "26 U.S.C. §7702B(d)(1)-(5)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:7702B%20edition:prelim)",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "The operative limit, and it maps 1:1 onto face lines 20-26. (d)(1): the excess of "
            "aggregate periodic payments over the per diem limitation is includible in gross income "
            "'without regard to section 72' (the annuity rules do not apply). (d)(2): the limitation is "
            "the EXCESS (IF ANY) of the GREATER of the dollar amount or actual qualified LTC service "
            "costs, OVER reimbursements — face lines 21/22 → 23 → less 24 → 25, with a statutory floor "
            "at zero the face does not print. (d)(3): all persons receiving payments with respect to the "
            "SAME INSURED are treated as one person, and the limitation is allocated first to the "
            "insured (the statutory root of the face's line 15 and of Multiple Payees). (d)(4): "
            "$175/day statutory baseline. (d)(5): indexed by the §213(d)(10) mechanism → Rev. Proc. "
            "2024-40 §2.62 = $420 for 2025. "
            "VERBATIM STATUS: (d)(1), (d)(2), (d)(3)(A) and (d)(3)(B) all captured verbatim 2026-08-08 "
            "— (d)(1)/(d)(2) from uscode.house.gov after an initial LII fetch returned only paraphrase. "
            "⚠ THE SECOND FETCH EARNED ITS KEEP: the verbatim (d)(2) revealed 'the excess (if any)', "
            "which floors line 25 — this spec had been authored UNFLOORED on the strength of the face "
            "alone, and the paraphrase had silently dropped the phrase. No longer "
            "requires_human_review; the drafting error it caught is recorded in the module docstring."
        ),
        "topics": ["ltc_per_diem_exclusion"],
        "excerpts": [
            {
                "excerpt_label": "§7702B(d)(1) — the excess over the limitation is includible, without regard to §72",
                "location_reference": "26 U.S.C. §7702B(d)(1)",
                "excerpt_text": (
                    "If the aggregate of— (A) the periodic payments received for any period under all "
                    "qualified long-term care insurance contracts which are treated as made for "
                    "qualified long-term care services for an insured, and (B) the periodic payments "
                    "received for such period which are treated under section 101(g) as paid by reason "
                    "of the death of such insured, exceeds the per diem limitation for such period, "
                    "such excess shall be includible in gross income without regard to section 72."
                ),
                "summary_text": (
                    "Face line 26. Note (A) + (B) IS line 20: qualified LTC per-diem benefits plus the "
                    "§101(g) payments (the chronically-ill ADB of line 19) share ONE limitation — which "
                    "is the statutory reason line 19 sits inside the per diem machinery rather than "
                    "beside it. 'Without regard to section 72' rules out annuity treatment of the "
                    "excess."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§7702B(d)(2) — 'the EXCESS (IF ANY) of the greater of ... over reimbursements'",
                "location_reference": "26 U.S.C. §7702B(d)(2)",
                "excerpt_text": (
                    "For purposes of paragraph (1), the per diem limitation for any period is an amount "
                    "equal to the excess (if any) of— (A) the greater of— (i) the dollar amount in "
                    "effect for such period under paragraph (4), or (ii) the costs incurred for "
                    "qualified long-term care services provided for the insured for such period, over "
                    "(B) the aggregate payments received as reimbursements (through insurance or "
                    "otherwise) for qualified long-term care services provided for the insured during "
                    "such period."
                ),
                "summary_text": (
                    "⚠⚠ THE WHOLE OF LINES 21-25 IN ONE SENTENCE, and it carries a floor the FACE DOES "
                    "NOT PRINT. (A)(i) = line 21, (A)(ii) = line 22, 'the greater of' = line 23, (B) = "
                    "line 24, and 'the EXCESS (IF ANY) of ... over ...' = line 25 floored at zero. The "
                    "face prints '-0-' guidance on line 26 only, so a build working from the face alone "
                    "leaves line 25 unfloored — and a negative line 25 makes line 26 exceed line 20, "
                    "taxing more than was received. This spec was drafted with that defect and the "
                    "verbatim caught it."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§7702B(d)(3)(A) — all payees for the same insured are treated as ONE person",
                "location_reference": "26 U.S.C. §7702B(d)(3)(A)",
                "excerpt_text": (
                    "all persons receiving periodic payments described in paragraph (1) with respect to "
                    "the same insured shall be treated as 1 person."
                ),
                "summary_text": (
                    "The statutory basis for face line 15 and Multiple Payees: the per diem limitation "
                    "belongs to the INSURED, not to each policyholder. This is why v1 must REFUSE the "
                    "line-15-Yes case rather than give one payee the whole limitation."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§7702B(d)(3)(B) — allocated first to the insured, remainder as the Secretary prescribes",
                "location_reference": "26 U.S.C. §7702B(d)(3)(B)",
                "excerpt_text": (
                    "allocated first to the insured and any remaining limitation shall be allocated "
                    "among the other such persons in such manner as the Secretary shall prescribe."
                ),
                "summary_text": (
                    "The ordering the i8853 Multiple Payees text implements: insured first (to the "
                    "extent of the payments the insured received), remainder pro rata among the other "
                    "policyholders by payments received."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§7702B(d)(4) — the $175/day statutory baseline before indexing",
                "location_reference": "26 U.S.C. §7702B(d)(4)",
                "excerpt_text": (
                    "$175 per day (or the equivalent amount in the case of payments on another periodic "
                    "basis)."
                ),
                "summary_text": (
                    "The un-indexed statutory figure. Never use it directly — (d)(5) indexes it, and the "
                    "2025 amount is $420 (Rev. Proc. 2024-40 §2.62). Recorded so a future year's build "
                    "can see that the constant is INDEXED and must be re-pulled, not carried forward."
                ),
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "IRC_101_G",
        "source_type": "code_section",
        "source_rank": "controlling",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §101(g) — Treatment of certain accelerated death benefits",
        "citation": "26 U.S.C. §101(g)(1), (3), (4)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:101%20edition:prelim)",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": True,
        "notes": (
            "Why face lines 16 and 19 split the way they do. §101(g)(1): amounts received under a life "
            "insurance contract on the life of an insured who is TERMINALLY ill are treated as paid by "
            "reason of death, hence excludable — which is the face's 'skip lines 17 through 25 and enter "
            "-0- on line 26'. §101(g)(3): for a CHRONICALLY ill insured the exclusion is limited to the "
            "§7702B treatment (payment for costs incurred, not compensated by insurance, for qualified "
            "LTC services; contract must meet §7702B(b)(1)(B)) — which is why chronically-ill ADB lands "
            "on line 19 INSIDE the per diem limitation while terminally-ill ADB is excluded outright. "
            "§101(g)(4)(A): terminally ill = certified by a physician as reasonably expected to result "
            "in death within 24 months of certification; (4)(B): chronically ill takes §7702B(c)(2)'s "
            "definition but EXCLUDES a terminally ill individual (the two categories are disjoint). "
            "REQUIRES HUMAN REVIEW: captured 2026-08-08 via LII as summary with short embedded quotes; "
            "the (g)(3) conditions should be read against statute at the Gate-1 walk before the app "
            "relies on any of them beyond the terminally-ill/chronically-ill routing."
        ),
        "topics": ["ltc_per_diem_exclusion"],
        "excerpts": [
            {
                "excerpt_label": "§101(g)(4)(A) — terminally ill: death reasonably expected within 24 months",
                "location_reference": "26 U.S.C. §101(g)(4)(A)",
                "excerpt_text": (
                    "an individual who has been certified by a physician as having an illness or physical "
                    "condition which can reasonably be expected to result in death in 24 months or less"
                ),
                "summary_text": (
                    "The line-16 test. Certified by a PHYSICIAN (contrast: chronically ill is certified "
                    "by a licensed health care practitioner). i8853 states the same 24-month rule."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§101(g)(4)(B) — chronically ill EXCLUDES a terminally ill individual",
                "location_reference": "26 U.S.C. §101(g)(4)(B)",
                "excerpt_text": (
                    "section 7702B(c)(2); except that such term shall not include a terminally ill "
                    "individual"
                ),
                "summary_text": (
                    "The two statuses are mutually exclusive — which is what makes the line 19 "
                    "instruction workable: on redesignation from chronically to terminally ill mid-year, "
                    "include on line 19 only the payments received BEFORE terminal certification."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "IRS_2025_F8853_FORM",
        "source_type": "official_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Form 8853 (2025) — Archer MSAs and Long-Term Care Insurance Contracts (Section C)",
        "citation": "Form 8853 (2025), Section C, lines 14a-26",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/f8853.pdf",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "The face, read directly on 2026-08-08. SHA256 "
            "5582f8137b70251d6292426ee89b78862412cf48d76577b8407e5f5f8775e5e9; footer reads "
            "'Form 8853 (2025)'. ⚠ The s224 f<form>.pdf trap was CHECKED and does not bite: "
            "irs-pdf/f8853.pdf and irs-prior/f8853--2025.pdf are BYTE-IDENTICAL, so the current "
            "revision IS the 2025 one. Line 21 PRINTS the $420 rate on the face itself rather than "
            "leaving it to the instructions — the single most useful fact for pinning the constant. "
            "Section C is one Section C PER INSURED, with a 'more than one Section C attached' "
            "checkbox above line 14a."
        ),
        "topics": ["ltc_per_diem_exclusion"],
        "excerpts": [
            {
                "excerpt_label": "Line 21 — the rate is printed on the 2025 face",
                "location_reference": "Form 8853 (2025), Section C, line 21",
                "excerpt_text": "Multiply $420 by the number of days in the LTC period",
                "summary_text": (
                    "The 2025 per diem rate, on the face. Agrees with Rev. Proc. 2024-40 §2.62 and with "
                    "i8853 Example 1's footnote — three independent confirmations."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 26 — the destination, and the 1040-NR literal",
                "location_reference": "Form 8853 (2025), Section C, line 26",
                "excerpt_text": (
                    "Taxable payments. Subtract line 25 from line 20. If zero or less, enter -0-. Also "
                    "include this amount in the total on Schedule 1 (Form 1040), line 8e, or, for "
                    "taxpayers filing Form 1040-NR, on Schedule NEC (Form 1040-NR), line 12. For "
                    "taxpayers filing Form 1040-NR, on Schedule NEC (Form 1040-NR), line 12, enter "
                    "“LTC” and the amount"
                ),
                "summary_text": (
                    "⚠ 'include this amount in the TOTAL on line 8e' — the face's own wording says 8e "
                    "is a total that this is one component of, corroborating the "
                    "TotArcherMSAMedcrLTCAmt element name. Floored at zero. The 1040-NR route needs the "
                    "literal 'LTC' (specced, not built: D_8853C_NR_UNWIRED)."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 16 note — the terminally-ill short circuit",
                "location_reference": "Form 8853 (2025), Section C, note under line 16",
                "excerpt_text": (
                    "If “Yes” and the only payments you received in 2025 were accelerated death "
                    "benefits that were paid to you because the insured was terminally ill, skip lines "
                    "17 through 25 and enter -0- on line 26."
                ),
                "summary_text": (
                    "The §101(g)(1) outright exclusion, on the face. Note how NARROW it is: terminally "
                    "ill AND the ONLY payments were ADB paid for that reason. Any per-diem LTC benefit "
                    "in the same year defeats the short circuit and the full computation runs."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 17 Caution — a NON-qualified contract never uses lines 18-26",
                "location_reference": "Form 8853 (2025), Section C, caution under line 17",
                "excerpt_text": (
                    "Don’t use lines 18 through 26 to figure the taxable amount of benefits paid "
                    "under an LTC insurance contract that isn’t a qualified LTC insurance contract. "
                    "Instead, if the benefits aren’t excludable from your income … report the "
                    "amount not excludable as income on Schedule 1 (Form 1040), line 8e"
                ),
                "summary_text": (
                    "The line 17 vs line 18 gap is not a rounding difference — it is a DIFFERENT "
                    "computation the form refuses to do. Non-qualified benefits bypass the per diem "
                    "machinery and land on 8e directly if not otherwise excludable. Drives "
                    "D_8853C_NONQUALIFIED."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "IRS_2025_F8853_INSTR",
        "source_type": "official_instruction",
        "source_rank": "implementation_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Instructions for Form 8853 (2025) — Section C, Long-Term Care Insurance Contracts",
        "citation": "i8853 (2025), pages 8-11",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/i8853.pdf",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "Read directly on 2026-08-08. SHA256 "
            "cefff1410968fd320fa175e1b84d9f6335fb9838f1f3c8b1594e477cbe0ab531. Supplies everything the "
            "face leaves open: the Filing Requirements flowchart (which lines to complete in each of "
            "four populations), both LTC-period methods, the Multiple Payees allocation, the "
            "pre-August-1-1996 reimbursement carve-out, and TWO fully worked examples that scenarios "
            "T1-T3 transcribe verbatim. An IRS-published answer key is stronger evidence than any "
            "example we could construct."
        ),
        "topics": ["ltc_per_diem_exclusion"],
        "excerpts": [
            {
                "excerpt_label": "Line 18 Caution — one Section C PER LTC PERIOD",
                "location_reference": "i8853 (2025), Line 18",
                "excerpt_text": (
                    "If you have more than one LTC period, you must separately calculate the taxable "
                    "amount of the payments received during each LTC period. To do this, complete lines "
                    "18 through 26 on separate Sections C for each LTC period. Enter the total on line "
                    "26 from each separate Section C on the Form 8853 that you attach to your tax return."
                ),
                "summary_text": (
                    "Multi-period returns are multiple Sections C summed at line 26 — a structural "
                    "requirement, not a presentation choice. v1 computes ONE period and holds "
                    "(D_8853C_MULTI_PERIOD) rather than blending periods, which would produce a wrong "
                    "line 21."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 19 — chronically-ill ADB only; the mid-year redesignation rule",
                "location_reference": "i8853 (2025), Line 19",
                "excerpt_text": (
                    "Include only amounts you received while the insured was a chronically ill "
                    "individual. Don't include amounts you received while the insured was a terminally "
                    "ill individual. If the insured was redesignated from chronically ill to terminally "
                    "ill in 2025, only include on line 19 payments received before the insured was "
                    "certified as terminally ill."
                ),
                "summary_text": (
                    "Line 19 is NOT simply box 2 of the 1099-LTC — it is the chronically-ill SLICE of "
                    "box 2, split at the date of terminal certification (1099-LTC box 5 'Date "
                    "certified'). The app must not auto-fill line 19 from box 2."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 21 — the two LTC-period methods",
                "location_reference": "i8853 (2025), Line 21, Methods 1 and 2",
                "excerpt_text": (
                    "Method 1—Contract Period. Under this method, your LTC period is the same period as "
                    "that used by the insurance company under the contract to compute the benefits it "
                    "pays you. For example, if the insurance company computes your benefits on a daily "
                    "basis, your LTC period is 1 day. … Method 2—Equal Payment Rate. Under this method, "
                    "your LTC period is the period during which the insurance company uses the same "
                    "payment rate to compute your benefits."
                ),
                "summary_text": (
                    "The day count is a preparer ELECTION between two defined methods, not a derivable "
                    "figure — so ltc_period_days is an asserted input. Contract Period on a daily-benefit "
                    "contract gives a 1-day period (line 21 = $420), which is the small-limitation, "
                    "high-taxable case; Equal Payment Rate typically gives a much larger period. If "
                    "contracts for one insured use different contract periods, Method 1 forces ALL of "
                    "them to daily."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 24 Caution — the pre-August-1-1996 reimbursement carve-out",
                "location_reference": "i8853 (2025), Line 24",
                "excerpt_text": (
                    "Generally, don't include on line 24 reimbursements for qualified LTC services you "
                    "received under a contract issued before August 1, 1996. However, you must include "
                    "reimbursements if the contract was exchanged or modified after July 31, 1996, to "
                    "increase per diem payments or reimbursements."
                ),
                "summary_text": (
                    "A grandfather rule with a claw-back. ⚠ CHECK THE SIGN: excluding a reimbursement "
                    "from line 24 makes line 25 LARGER and line 26 SMALLER — taxpayer-favourable. So the "
                    "carve-out must be an affirmative preparer assertion that DEFAULTS OFF, and the "
                    "post-7/31/1996 modification must be asked whenever it is claimed."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Multiple Payees — the aggregate statement and the allocation order",
                "location_reference": "i8853 (2025), Multiple Payees",
                "excerpt_text": (
                    "The per diem limitation is allocated first to the insured to the extent of the total "
                    "payments the insured received. … Any remaining limitation is allocated among the "
                    "other policyholders pro rata based on the payments they received in 2025. The "
                    "statement showing the aggregate computation must be attached to the Form 8853 for "
                    "each person who received a payment. … Enter your share of the per diem limitation "
                    "and the taxable payments on lines 25 and 26 of your individual Form 8853. Leave "
                    "lines 21 through 24 blank."
                ),
                "summary_text": (
                    "The v1 refusal is specified here in full, so the follow-on build has its spec "
                    "ready: each payee uses the SAME LTC period (contract-period method forced if they "
                    "disagree), lines 21-24 go BLANK on the individual form, and the aggregate statement "
                    "attaches to every payee's return. ⚠ Example 2 Step 3 allocates on the UNROUNDED "
                    "ratio (33,000/51,000 x 51,480 = 33,311, not 64.7% x 51,480 = 33,308) — the s230 "
                    "'allocate each source in its own right, never split an already-rounded share' rule, "
                    "confirmed by the IRS's own arithmetic."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Filing Requirements for Section C — the four populations",
                "location_reference": "i8853 (2025), Filing Requirements for Section C flowchart",
                "excerpt_text": (
                    "Go through this chart for each insured person for whom you received long-term care "
                    "(LTC) payments. … Complete all of Section C. … Complete only lines 14a, 14b, and 17 "
                    "of Section C. … Complete only lines 14a, 14b, 15, 16, 17 (if applicable), and 26 of "
                    "Section C. … Don't complete Section C."
                ),
                "summary_text": (
                    "⚠ THE FLOWCHART IS PER INSURED, and three of its four outcomes are PARTIAL "
                    "completions — including one that fills line 17 and NOTHING else (per-diem payments "
                    "received but none under a qualified contract). A build that treats Section C as "
                    "all-or-nothing will emit lines the IRS says to leave blank."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "IRS_1099LTC_FORM",
        "source_type": "official_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Form 1099-LTC (Rev. April 2025) — Long-Term Care and Accelerated Death Benefits",
        "citation": "Form 1099-LTC (Rev. 4-2025), boxes 1-5",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/f1099ltc.pdf",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "The source document that feeds Section C. Read directly on 2026-08-08; SHA256 "
            "69623198392f04003e66480c084cac90f920951d830a5fc73f35ad45aefaabdc. ⚠ CONTINUOUS-USE FORM — "
            "it carries a REVISION line ('Rev. April 2025'), not a tax year, so per the s230 rule the "
            "s224 next-revision trap does not apply and the revision must be read out of the PDF. "
            "Boxes: 1 gross LTC benefits paid · 2 accelerated death benefits paid · 3 'Check one: Per "
            "diem / Reimbursed amount' · 4 qualified contract (OPTIONAL for the payer) · 5 'Check, if "
            "applicable (optional)': Chronically ill / Terminally ill / Date certified. Three parties "
            "carry TINs: PAYER, POLICYHOLDER and INSURED — and Section C is keyed by INSURED, not by "
            "policyholder. Per s222 there is no RS spec for an information return; this is the source "
            "document, and the row shape for the import lane is documented in "
            "f8853_1099ltc_source_brief.md in this repo."
        ),
        "topics": ["ltc_per_diem_exclusion"],
        "excerpts": [
            {
                "excerpt_label": "Boxes 3, 4 and 5 are the ROUTERS — and 4 and 5 are optional",
                "location_reference": "Form 1099-LTC (Rev. 4-2025), Instructions for Policyholder, boxes 3-5",
                "excerpt_text": (
                    "Box 3. Shows if the amount in box 1 or 2 was paid on a per diem basis or was "
                    "reimbursement of actual long-term care expenses. If the insured was terminally ill, "
                    "this box may not be checked. Box 4. May show if the benefits were from a qualified "
                    "long-term care insurance contract. Box 5. May show if the insured was certified "
                    "chronically ill or terminally ill and the latest date certified."
                ),
                "summary_text": (
                    "⚠⚠ THE TRAP: boxes 4 and 5 are OPTIONAL ('May show'), and box 3  'may not be "
                    "checked' when the insured was terminally ill. So an UNCHECKED box 4 is NOT evidence "
                    "of a non-qualified contract, and an unchecked box 3 is NOT evidence that payments "
                    "were reimbursement-basis. Every one of these must be a preparer confirmation with a "
                    "diagnostic, never an inference from absence — the s224 'missing column read as a "
                    "missing box' class."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The per diem exclusion limit is allocated among all policyholders",
                "location_reference": "Form 1099-LTC (Rev. 4-2025), Instructions for Policyholder",
                "excerpt_text": (
                    "The per diem exclusion limit must be allocated among all policyholders who own "
                    "qualified long-term care insurance contracts for the same insured."
                ),
                "summary_text": (
                    "§7702B(d)(3) restated on the payee's own copy — corroborates that the shared "
                    "limitation is the norm in multi-contract families, so the Multiple Payees refusal "
                    "will actually be hit in practice rather than being a theoretical edge."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The POLICYHOLDER reports, even if payment went to a third party",
                "location_reference": "i8853 (2025), Section C Definitions — Policyholder",
                "excerpt_text": (
                    "The policyholder is the person who owns the proceeds of the LTC insurance contract, "
                    "life insurance contract, or viatical settlement, and can also be the insured "
                    "individual. The policyholder is required to report the income, even if payment is "
                    "assigned to a third party or parties. In the case of a group contract, the "
                    "certificate holder is considered to be the policyholder."
                ),
                "summary_text": (
                    "Who files: the POLICYHOLDER. Benefits paid straight to a nursing home are still the "
                    "policyholder's to report — a common real-world case where no cash reached the "
                    "client and the 1099-LTC still must be picked up."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
]

# The $420 lands as a NEW excerpt on the EXISTING Rev. Proc. 2024-40 source
# rather than as a fourth duplicate of it — see the RS agenda note about
# RP_2024_40 / REV_PROC_2024_40 / IRS_RP_2024_40 all being the same document.
NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [
    ("RP_2024_40", {
        "excerpt_label": "§2.62 — the 2025 §7702B(d)(4) per diem limitation is $420",
        "location_reference": "Rev. Proc. 2024-40, §2.62",
        "excerpt_text": (
            "Periodic Payments Received Under Qualified Long-Term Care Insurance Contracts or Under "
            "Certain Life Insurance Contracts. For calendar year 2025, the stated dollar amount of the "
            "per diem limitation under § 7702B(d)(4), regarding periodic payments received under a "
            "qualified long-term care insurance contract or periodic payments received under a life "
            "insurance contract that are treated as paid by reason of the death of a chronically ill "
            "individual, is $420."
        ),
        "summary_text": (
            "The 2025 constant, verbatim from the primary source. Agrees with the printed 2025 face "
            "(line 21) and i8853 Example 1's footnote. ⚠ Note the scope words: 'For CALENDAR year 2025' "
            "— while §3.01 of the same Rev. Proc. speaks of 'taxable years beginning in 2025'. "
            "Immaterial for calendar-year individuals; recorded rather than smoothed over. ⚠ Distinct "
            "from §3.28 (eligible LTC PREMIUMS, the §213(d)(10) age bands) — premiums cap a DEDUCTION, "
            "this caps an EXCLUSION."
        ),
        "is_key_excerpt": True,
    }),
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("IRC_7702B_D", "8853_SEC_C", "governs"),
    ("IRC_101_G", "8853_SEC_C", "governs"),
    ("IRS_2025_F8853_FORM", "8853_SEC_C", "governs"),
    ("IRS_2025_F8853_INSTR", "8853_SEC_C", "governs"),
    ("IRS_1099LTC_FORM", "8853_SEC_C", "informs"),
    ("RP_2024_40", "8853_SEC_C", "governs"),
    ("IRS_2025_SCH1_FORM", "8853_SEC_C", "mapping_only"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM: 8853_SEC_C
# ═══════════════════════════════════════════════════════════════════════════

N_IDENTITY = {
    "form_number": "8853_SEC_C",
    "form_title": "Form 8853 Section C (2025) — Long-Term Care Insurance Contracts and Accelerated Death Benefits",
    "notes": (
        "SECTION C ONLY, per Ken's s224 scope ruling — Sections A/B (Archer MSA, Medicare Advantage "
        "MSA) are deliberately NOT specced and the form number 8853_SEC_AB is reserved for them. "
        "⚠ There is deliberately NO spec under the bare form number '8853': a spec claiming the whole "
        "form while describing only half of it is the s231 Form-3800 defect (a line_map that did not "
        "match the real face), and this avoids repeating it. A future CC session that curls "
        "/lookup/8853/ and gets a 404 should read this note and the source brief, not improvise.\n\n"
        "ONE Section C per INSURED (not per policyholder, and not per 1099-LTC) and, when the insured "
        "has more than one LTC period, one per period with the line 26 amounts summed. The chain is "
        "Form 1099-LTC box 1 (where box 3 = Per diem) → line 17 → the qualified slice at line 18; box 2 "
        "chronically-ill slice → line 19; the §7702B(d)(2) greater-of at lines 21/22/23 less "
        "reimbursements at 24 → the per diem limitation at 25; the excess at 26 → Schedule 1 line 8e.\n\n"
        "⚠⚠ Line 8e is a COMPOSED line, not this form's property: its MeF element is "
        "TotArcherMSAMedcrLTCAmt (Archer MSA + Medicare Advantage MSA + LTC), and the face itself says "
        "'include this amount in the TOTAL on line 8e'. Per DECISIONS.md (s230, Schedule K 13g) the "
        "writer is a REGISTRY — v1 contributes the Section C component and leaves the A/B component "
        "preparer-keyed, so a later Sections A/B build joins rather than overwrites."
    ),
}

N_FACTS: list[dict] = [
    # ── Identity / structure (one Section C per insured per LTC period) ──
    {"fact_key": "f8853c_insured_name", "label": "Line 14a — Name of insured",
     "data_type": "string", "sort_order": 1,
     "notes": ("The insured, who is NOT necessarily the taxpayer. Section C is keyed by insured "
               "because §7702B(d)(3) aggregates all payees 'with respect to the same insured'.")},
    {"fact_key": "f8853c_insured_ssn", "label": "Line 14b — Social security number of insured",
     "data_type": "string", "sort_order": 2,
     "notes": ("MeF-typed SSN. The aggregation key for the multiple-payee test; also the join key to "
               "the 1099-LTC INSURED'S TIN (which is a different party from the POLICYHOLDER'S TIN).")},
    {"fact_key": "f8853c_more_than_one_section_c", "label": "Checkbox above line 14a — more than one Section C is attached",
     "data_type": "boolean", "default_value": "false", "sort_order": 3,
     "notes": ("Set when the return carries multiple Sections C (several insureds, or several LTC "
               "periods for one insured). Derived by the app from the number of Section C records — "
               "never keyed, so it cannot disagree with what is actually attached.")},
    {"fact_key": "f8853c_ltc_period_index", "label": "Which LTC period this Section C covers (1-based)",
     "data_type": "integer", "default_value": "1", "sort_order": 4,
     "notes": ("i8853 line 18 Caution: one Section C per LTC period, line 26 amounts summed. v1 "
               "computes index 1 only and holds if more exist (D_8853C_MULTI_PERIOD).")},

    # ── The two face questions ──
    {"fact_key": "f8853c_line15_other_payees", "label": "Line 15 — did anyone other than you receive per-diem or ADB payments for this insured? (Yes/No/unanswered)",
     "data_type": "choice", "default_value": "unanswered", "sort_order": 10,
     "notes": ("Values: yes | no | unanswered. ⚠⚠ MUST NOT DEFAULT TO 'no'. A 'no' gives the taxpayer "
               "the WHOLE per diem limitation; if the truth is 'yes' the limitation is shared, so line "
               "25 would be too large and line 26 too small — an UNDER-report of taxable income. "
               "Unanswered therefore raises D_8853C_PAYEE_UNANSWERED (error) rather than computing. "
               "'yes' routes to the unbuilt Multiple Payees path and holds.")},
    {"fact_key": "f8853c_line16_terminally_ill", "label": "Line 16 — was the insured a terminally ill individual? (Yes/No/unanswered)",
     "data_type": "choice", "default_value": "unanswered", "sort_order": 11,
     "notes": ("Values: yes | no | unanswered. §101(g)(4)(A): certified by a PHYSICIAN, death "
               "reasonably expected within 24 months. ⚠ Unanswered must NOT route to the "
               "terminally-ill zero path — that path is the most taxpayer-favourable outcome on the "
               "form, so guessing into it over-excludes.")},
    {"fact_key": "f8853c_adb_only_because_terminal", "label": "The ONLY payments received were ADB paid because the insured was terminally ill",
     "data_type": "boolean", "default_value": "false", "sort_order": 12,
     "notes": ("The second half of the face's line-16 note, and it is a SEPARATE fact from line 16 "
               "because the short circuit needs BOTH. A terminally ill insured who also received "
               "per-diem LTC benefits does NOT get the short circuit — the full computation runs. "
               "Asserted by the preparer; corroborated by 1099-LTC box 5 / box 3.")},

    # ── Lines 17-19 (inputs, from the 1099-LTC rows) ──
    {"fact_key": "f8853c_line17_gross_per_diem", "label": "Line 17 — gross LTC payments received on a per diem or other periodic basis",
     "data_type": "decimal", "default_value": "0", "sort_order": 17,
     "notes": ("Σ box 1 of every Form 1099-LTC for this insured ON WHICH BOX 3 'Per diem' IS CHECKED. "
               "Reimbursement-basis rows are excluded from line 17 entirely. Engine-fed from the "
               "1099-LTC rows, overridable.")},
    {"fact_key": "f8853c_line18_qualified_per_diem", "label": "Line 18 — the part of line 17 from QUALIFIED LTC insurance contracts",
     "data_type": "decimal", "default_value": "0", "sort_order": 18,
     "notes": ("⚠ NOT derivable from 1099-LTC box 4, which is OPTIONAL for the payer — an unchecked "
               "box 4 is not evidence of non-qualification. Preparer-confirmed. Only line 18 (not line "
               "17) enters line 20: the face's own Caution says a non-qualified contract does not use "
               "lines 18-26 at all.")},
    {"fact_key": "f8853c_line19_adb_chronically_ill", "label": "Line 19 — accelerated death benefits received on a per diem or other periodic basis (chronically ill only)",
     "data_type": "decimal", "default_value": "0", "sort_order": 19,
     "notes": ("The chronically-ill SLICE of 1099-LTC box 2 — never box 2 wholesale. i8853 line 19: "
               "exclude amounts received while the insured was terminally ill; on mid-year "
               "redesignation include only payments received BEFORE terminal certification (1099-LTC "
               "box 5 'Date certified' is the split point). Preparer-asserted.")},

    # ── Lines 21-24 (the limitation inputs) ──
    {"fact_key": "f8853c_per_diem_rate", "label": "The §7702B(d)(4) per diem limitation rate for the year",
     "data_type": "decimal", "default_value": "420", "sort_order": 20,
     "notes": ("$420 for 2025 — Rev. Proc. 2024-40 §2.62, printed on the 2025 face at line 21, "
               "footnoted in i8853 Example 1. INDEXED annually: goes through the _constants_for_year() "
               "pattern with a prior-year regression test; never carried forward to a new tax year "
               "without re-pulling the Rev. Proc.")},
    {"fact_key": "f8853c_ltc_period_method", "label": "LTC-period method elected (contract period / equal payment rate)",
     "data_type": "choice", "default_value": "unanswered", "sort_order": 21,
     "notes": ("Values: contract_period | equal_payment_rate | unanswered. A preparer ELECTION between "
               "two defined methods (i8853 line 21), so the day count cannot be derived. Under "
               "contract_period, differing contract periods for one insured force ALL contracts to a "
               "daily basis.")},
    {"fact_key": "f8853c_ltc_period_days", "label": "Number of days in the LTC period",
     "data_type": "integer", "default_value": "0", "sort_order": 22,
     "notes": ("1-365 for 2025 (not a leap year). A daily-benefit contract under the contract-period "
               "method gives 1 day — the smallest limitation and the most taxable outcome, so a wrong "
               "365 here is materially taxpayer-favourable. Out-of-range → D_8853C_DAYS_RANGE (error).")},
    {"fact_key": "f8853c_line22_costs_incurred", "label": "Line 22 — costs incurred for qualified LTC services during the LTC period",
     "data_type": "decimal", "default_value": "0", "sort_order": 23,
     "notes": ("Qualified LTC services per i8853 line 22: diagnostic, preventive, therapeutic, curing, "
               "treating, mitigating and rehabilitative services, and maintenance or personal care, "
               "required by a chronically ill individual under a licensed practitioner's plan of care. "
               "GROSS costs — reimbursements are subtracted separately at line 24, not netted here.")},
    {"fact_key": "f8853c_line24_reimbursements", "label": "Line 24 — reimbursements received or expected for qualified LTC services",
     "data_type": "decimal", "default_value": "0", "sort_order": 24,
     "notes": ("Received OR EXPECTED to be received, through insurance or otherwise (i8853 line 24). "
               "Typically the 1099-LTC rows with box 3 'Reimbursed amount' checked, plus any other "
               "recovery.")},
    {"fact_key": "f8853c_pre_aug1996_contract", "label": "Reimbursements are under an LTC contract issued before August 1, 1996",
     "data_type": "boolean", "default_value": "false", "sort_order": 25,
     "notes": ("The grandfather carve-out: such reimbursements are generally EXCLUDED from line 24. "
               "⚠ CHECK THE SIGN — excluding them raises line 25 and lowers line 26, so this is "
               "taxpayer-favourable and must be an affirmative assertion that DEFAULTS OFF.")},
    {"fact_key": "f8853c_pre_aug1996_modified", "label": "That pre-Aug-1996 contract was exchanged or modified after July 31, 1996 to increase per diem payments or reimbursements",
     "data_type": "boolean", "default_value": "false", "sort_order": 26,
     "notes": ("The claw-back on the carve-out (i8853 line 24 Caution): if true, the reimbursements go "
               "back INTO line 24. Must be asked whenever the carve-out is claimed — "
               "D_8853C_PRE1996_UNCONFIRMED.")},

    # ── Outputs ──
    {"fact_key": "f8853c_line20_total", "label": "Line 20 — add lines 18 and 19",
     "data_type": "decimal", "sort_order": 40,
     "notes": "OUTPUT. The amount tested against the limitation. Note it starts from line 18, not 17."},
    {"fact_key": "f8853c_line21_dollar_limit", "label": "Line 21 — rate x days in the LTC period",
     "data_type": "decimal", "sort_order": 41,
     "notes": "OUTPUT. $420 x days for 2025. BLANK (not zero) on a Multiple Payees return."},
    {"fact_key": "f8853c_line23_greater", "label": "Line 23 — the larger of line 21 or line 22",
     "data_type": "decimal", "sort_order": 42,
     "notes": ("OUTPUT. §7702B(d)(2)'s 'greater of'. A min-for-max slip here understates the "
               "limitation and OVER-taxes — the opposite sign from most defects on this form, and the "
               "reason FA-1040-8853C-02 pins it with costs deliberately above the dollar limit.")},
    {"fact_key": "f8853c_line25_per_diem_limitation", "label": "Line 25 — per diem limitation = MAX(0, line 23 less line 24)",
     "data_type": "decimal", "sort_order": 43,
     "notes": ("OUTPUT. ⚠⚠ FLOORED AT ZERO by §7702B(d)(2)'s 'the excess (if any) of (A) ... over (B)' "
               "even though the FACE prints no floor on line 25 (it prints one only on line 26). An "
               "unfloored negative line 25 makes line 26 exceed line 20 — taxing more than was "
               "received. On a Multiple Payees return this is instead the taxpayer's ALLOCATED SHARE, "
               "keyed from the aggregate statement with lines 21-24 blank (not built in v1).")},
    {"fact_key": "f8853c_line26_taxable", "label": "Line 26 — taxable payments (line 20 less line 25, floored at zero)",
     "data_type": "decimal", "sort_order": 44,
     "notes": ("OUTPUT, and the form's only export. §7702B(d)(1)'s excess. Floored at zero — a negative "
               "unused limitation neither carries forward nor offsets other income. Contributes to "
               "Schedule 1 line 8e as ONE COMPONENT.")},
    {"fact_key": "f8853c_sch1_8e_component", "label": "The Section C component of Schedule 1 line 8e (Σ line 26 over all Sections C)",
     "data_type": "decimal", "sort_order": 45,
     "notes": ("OUTPUT. Σ line 26 across every Section C on the return (all insureds, all LTC "
               "periods). ⚠ A COMPONENT of 8e, never the whole line — the A/B component stays "
               "preparer-keyed (MeF element TotArcherMSAMedcrLTCAmt).")},
]

N_RULES: list[dict] = [
    {"rule_id": "R-8853C-SCOPE", "title": "Scope — Section C only, one per insured; Sections A/B out of scope", "rule_type": "routing",
     "precedence": 1, "sort_order": 1,
     "formula": ("Engage Section C per INSURED when the return carries a Form 1099-LTC for that insured "
                 "with box 1 or box 2 nonzero, or when Section C amounts are keyed directly. Sections "
                 "A/B (Archer MSA, Medicare Advantage MSA) are NOT computed — their Schedule 1 line 8e "
                 "component stays preparer-keyed and Form 8889 line 4 stays keyed under the existing "
                 "D_8889_ARCHER guard. Entity: 1040. 1040-NR specced, not built."),
     "inputs": ["f8853c_insured_ssn"], "outputs": [],
     "description": ("Ken's s224 ruling: Section C is the half that arrives in an aging client base; "
                     "the Archer sections are nearly extinct and stay manual. The unit of the form is "
                     "the INSURED because §7702B(d)(3) aggregates by insured.")},

    {"rule_id": "R-8853C-FILING", "title": "Filing requirements — three of the four populations complete Section C only PARTIALLY", "rule_type": "conditional",
     "precedence": 2, "sort_order": 2,
     "formula": ("Per the i8853 flowchart, run PER INSURED: (a) per-diem payments under a QUALIFIED LTC "
                 "contract, or per-diem ADB for a chronically ill insured → complete ALL of Section C. "
                 "(b) per-diem payments received but NONE under a qualified contract, and no per-diem "
                 "ADB → complete ONLY lines 14a, 14b and 17. (c) per-diem ADB but all paid for a "
                 "TERMINALLY ill insured → complete ONLY lines 14a, 14b, 15, 16, 17 (if applicable) and "
                 "26. (d) no per-diem payments and no per-diem ADB → do NOT complete Section C. "
                 "Lines outside the applicable set render BLANK, never zero."),
     "inputs": ["f8853c_line17_gross_per_diem", "f8853c_line18_qualified_per_diem",
                "f8853c_line19_adb_chronically_ill", "f8853c_line16_terminally_ill",
                "f8853c_adb_only_because_terminal"],
     "outputs": [],
     "description": ("⚠ The flowchart's partial outcomes are the part a build gets wrong: an "
                     "all-or-nothing Section C emits lines the IRS says to leave blank. Population (b) "
                     "files a Section C with a single amount on line 17 and nothing else.")},

    {"rule_id": "R-8853C-LINE17", "title": "Line 17 gathers ONLY per-diem-basis 1099-LTC box 1 amounts", "rule_type": "calculation",
     "precedence": 3, "sort_order": 3,
     "formula": ("line17 = Σ (1099-LTC box 1) over rows for this insured WHERE box 3 == 'Per diem'. "
                 "Rows with box 3 == 'Reimbursed amount' contribute NOTHING to line 17 (they feed line "
                 "24 instead). An UNCHECKED box 3 is not evidence of reimbursement basis — box 3 'may "
                 "not be checked' when the insured was terminally ill — so an unchecked row is "
                 "preparer-routed, never silently dropped (D_8853C_BOX3_UNCHECKED)."),
     "inputs": ["f8853c_line17_gross_per_diem"], "outputs": ["f8853c_line17_gross_per_diem"],
     "description": ("The per diem machinery exists because per-diem benefits are paid without regard "
                     "to actual expense; reimbursement-basis benefits are already limited by the "
                     "expense itself and are excludable without this computation.")},

    {"rule_id": "R-8853C-LINE20", "title": "Line 20 = line 18 + line 19 — the QUALIFIED slice plus chronically-ill ADB", "rule_type": "calculation",
     "precedence": 4, "sort_order": 4,
     "formula": ("line20 = line18 + line19. ⚠ Line 20 starts from line 18, NOT line 17: the "
                 "non-qualified excess (line 17 − line 18) never enters the per diem computation and "
                 "instead goes to Schedule 1 line 8e directly if not otherwise excludable (the face's "
                 "line 17 Caution) — which the app does NOT do for the preparer "
                 "(D_8853C_NONQUALIFIED)."),
     "inputs": ["f8853c_line18_qualified_per_diem", "f8853c_line19_adb_chronically_ill"],
     "outputs": ["f8853c_line20_total"],
     "description": ("§101(g)(3) is why chronically-ill ADB joins qualified LTC per-diem benefits in "
                     "one pool: it is excludable 'to the same extent' as under a qualified LTC "
                     "contract, so it shares the one limitation.")},

    {"rule_id": "R-8853C-LIMIT", "title": "The §7702B(d)(2) limitation — greater of dollars or costs, less reimbursements", "rule_type": "calculation",
     "precedence": 5, "sort_order": 5,
     "formula": ("line21 = per_diem_rate x ltc_period_days   [2025: 420 x days, 1 <= days <= 365]\n"
                 "line23 = MAX(line21, line22)               [§7702B(d)(2)(A) 'the greater of']\n"
                 "line25 = MAX(0, line23 − line24)           [§7702B(d)(2) 'the EXCESS (IF ANY) of\n"
                 "                                            (A) ... over (B)' — a STATUTORY floor\n"
                 "                                            the face does not print]\n"
                 "Reimbursements under a pre-August-1-1996 contract are EXCLUDED from line 24 unless "
                 "the contract was exchanged or modified after July 31, 1996 to increase per diem "
                 "payments or reimbursements."),
     "inputs": ["f8853c_per_diem_rate", "f8853c_ltc_period_days", "f8853c_line22_costs_incurred",
                "f8853c_line24_reimbursements", "f8853c_pre_aug1996_contract",
                "f8853c_pre_aug1996_modified"],
     "outputs": ["f8853c_line21_dollar_limit", "f8853c_line23_greater",
                 "f8853c_line25_per_diem_limitation"],
     "description": ("A taxpayer with heavy real costs is protected by line 22 rather than capped at "
                     "the per-diem dollars; a taxpayer with light costs still gets the dollar floor. "
                     "⚠⚠ Line 25 IS FLOORED AT ZERO by the statute even though the face does not print "
                     "a floor there (line 26 prints one, line 25 does not): §7702B(d)(2) defines the "
                     "limitation as 'the excess (if any) of (A) ... over (B)', the Code's "
                     "floor-at-zero idiom. Without it, reimbursements above line 23 drive line 25 "
                     "negative and line 26 then EXCEEDS line 20 — taxing more than the taxpayer ever "
                     "received, which is arithmetically impossible. Pinned by T14.")},

    {"rule_id": "R-8853C-LINE26", "title": "Line 26 = MAX(0, line 20 − line 25); the terminally-ill short circuit", "rule_type": "calculation",
     "precedence": 6, "sort_order": 6,
     "formula": ("line26 = MAX(0, line20 − line25). SHORT CIRCUIT: if line16 == 'yes' AND the only "
                 "payments received were ADB paid BECAUSE the insured was terminally ill, skip lines 17 "
                 "through 25 and line26 = 0 (§101(g)(1)). Both conditions are required — a terminally "
                 "ill insured who ALSO received per-diem LTC benefits runs the full computation."),
     "inputs": ["f8853c_line20_total", "f8853c_line25_per_diem_limitation",
                "f8853c_line16_terminally_ill", "f8853c_adb_only_because_terminal"],
     "outputs": ["f8853c_line26_taxable"],
     "description": ("§7702B(d)(1)'s excess. Floored at zero: an unused limitation does not carry "
                     "forward and does not shelter other income.")},

    {"rule_id": "R-8853C-MULTIPAYEE", "title": "Multiple payees (line 15 = Yes) — the limitation is SHARED; v1 REFUSES", "rule_type": "validation",
     "precedence": 7, "sort_order": 7,
     "formula": ("If line15 == 'yes' (and the terminally-ill-ADB-only short circuit does not apply): the "
                 "per diem limitation belongs to the INSURED and is allocated first to the insured to "
                 "the extent of the payments the insured received, with the remainder pro rata among "
                 "the other policyholders by payments received; every payee attaches the same aggregate "
                 "statement, uses the SAME LTC period (contract-period method forced if they "
                 "disagree), leaves lines 21-24 BLANK and keys its own share on lines 25 and 26. NOT "
                 "BUILT in v1 → D_8853C_MULTIPAYEE_HOLD, no line 26 computed, no 8e contribution. "
                 "If line15 == 'unanswered' → D_8853C_PAYEE_UNANSWERED (error); do NOT assume 'no'."),
     "inputs": ["f8853c_line15_other_payees"], "outputs": [],
     "description": ("⚠⚠ CHECK THE SIGN — this is why the refusal is mandatory rather than tidy. "
                     "Computing a FULL limitation for a SHARED one makes line 25 too large and line 26 "
                     "too small: it UNDER-reports taxable income. Refusing is conservative; guessing is "
                     "not. When it is built, allocate on the UNROUNDED payment ratio — i8853 Example 2 "
                     "Step 3 does (33,000/51,000 x 51,480 = 33,311, not 64.7% x 51,480 = 33,308), "
                     "matching the s230 never-split-an-already-rounded-share rule.")},

    {"rule_id": "R-8853C-PERIOD", "title": "One LTC period per Section C; the day count is an ELECTED figure", "rule_type": "validation",
     "precedence": 8, "sort_order": 8,
     "formula": ("The LTC period follows the preparer's elected method: contract_period (the insurer's "
                 "own benefit-computation period; 1 day if benefits are computed daily) or "
                 "equal_payment_rate (the span over which one payment rate applies). More than one "
                 "period for an insured requires separate Sections C for lines 18-26 with the line 26 "
                 "amounts summed → v1 computes period 1 and raises D_8853C_MULTI_PERIOD. "
                 "1 <= ltc_period_days <= 365 for 2025 → otherwise D_8853C_DAYS_RANGE (error)."),
     "inputs": ["f8853c_ltc_period_method", "f8853c_ltc_period_days", "f8853c_ltc_period_index"],
     "outputs": [],
     "description": ("The day count cannot be derived from the 1099-LTC — the form carries no dates "
                     "other than box 5's certification date — so it is asserted, and its range is the "
                     "only arithmetic check available. A 365 keyed where the truth is 1 inflates the "
                     "limitation 365-fold in the taxpayer's favour, which is why the range check is an "
                     "ERROR and not a warning.")},

    {"rule_id": "R-8853C-DEST", "title": "Line 26 is a COMPONENT of Schedule 1 line 8e — a registry, never an owner", "rule_type": "routing",
     "precedence": 9, "sort_order": 9,
     "formula": ("sch1_8e_component = Σ line26 over every Section C on the return (all insureds, all "
                 "LTC periods).\n"
                 "Schedule 1 line 8e = sch1_8e_component + the preparer-keyed Sections A/B residual "
                 "(Archer MSA / Medicare Advantage MSA taxable distributions and MSA deemed-loan "
                 "income, which have no engine).\n"
                 "A return with NO Section C keeps whatever the preparer typed on 8e — unchanged from "
                 "today's keyed behavior (the zero-movement guarantee).\n"
                 "1040-NR: Schedule NEC line 12 with the literal 'LTC' — specced, NOT built "
                 "(D_8853C_NR_UNWIRED)."),
     "inputs": ["f8853c_line26_taxable"], "outputs": ["f8853c_sch1_8e_component"],
     "description": ("⚠⚠ The MeF element for 8e is TotArcherMSAMedcrLTCAmt — Archer MSA + Medicare "
                     "Advantage MSA + LTC in one line — and the face says 'include this amount in the "
                     "TOTAL on line 8e'. DECISIONS.md (s230, Schedule K 13g) governs: a shared line's "
                     "writer is a REGISTRY, not whichever form got there first. Adding Sections A/B "
                     "later must be one more component plus one more share key, nothing else. The "
                     "failure mode this prevents is a DISAPPEARED number, which is exactly why nobody "
                     "would report it.")},

    {"rule_id": "R-8853C-ATTACH", "title": "Form 8853 is an ATTACHED form — the manifest already says so", "rule_type": "validation",
     "precedence": 10, "sort_order": 10,
     "formula": ("A nonzero Schedule 1 line 8e requires Form 8853 attached (already declared: "
                 "form_manifest.py AttachmentRequirement('Form 8853') on line 8e). The render leg needs "
                 "the official 2025 f8853 PDF registered in forms_manifest.json with its SHA256 — it is "
                 "absent today — plus an AcroForm field map for Section C. A Multiple Payees return "
                 "additionally needs the aggregate statement as a statement page (not built)."),
     "inputs": ["f8853c_sch1_8e_component"], "outputs": [],
     "description": ("⚠ Unlike the s226 §704(d) worksheet, this form IS attached and IS transmitted, so "
                     "'rendering and MeF' is a real render leg plus a real MeF leg — not just storing "
                     "and surviving. tests/test_form_manifest.py currently pins the comment 'Form 8853 "
                     "— never generated'; that comment is the acceptance criterion to delete.")},
]

N_LINES: list[dict] = [
    {"line_number": "14a", "description": "Name of insured", "line_type": "input"},
    {"line_number": "14b", "description": "Social security number of insured", "line_type": "input"},
    {"line_number": "15", "description": "Did anyone other than you receive per-diem or ADB payments for this insured? (Yes/No)", "line_type": "input"},
    {"line_number": "16", "description": "Was the insured a terminally ill individual? (Yes/No)", "line_type": "input"},
    {"line_number": "17", "description": "Gross LTC payments received on a per diem or other periodic basis (Σ 1099-LTC box 1 where box 3 = Per diem)", "line_type": "input"},
    {"line_number": "18", "description": "Part of line 17 that is from qualified LTC insurance contracts", "line_type": "input"},
    {"line_number": "19", "description": "Accelerated death benefits received on a per diem or other periodic basis (chronically ill only)", "line_type": "input"},
    {"line_number": "20", "description": "Add lines 18 and 19", "line_type": "subtotal"},
    {"line_number": "21", "description": "Multiply $420 by the number of days in the LTC period", "line_type": "calculated"},
    {"line_number": "22", "description": "Costs incurred for qualified LTC services provided for the insured during the LTC period", "line_type": "input"},
    {"line_number": "23", "description": "Enter the larger of line 21 or line 22", "line_type": "calculated"},
    {"line_number": "24", "description": "Reimbursements for qualified LTC services provided for the insured during the LTC period", "line_type": "input"},
    {"line_number": "25", "description": "Per diem limitation. Subtract line 24 from line 23", "line_type": "calculated"},
    {"line_number": "26", "description": "Taxable payments. Subtract line 25 from line 20; if zero or less, enter -0- → Schedule 1 line 8e", "line_type": "total"},
]

N_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_8853C_PAYEE_UNANSWERED", "title": "Line 15 (other payees) is unanswered", "severity": "error",
     "condition": "Section C engaged AND line15 == 'unanswered' AND NOT terminally-ill-ADB-only",
     "message": ("Form 8853 Section C line 15 has not been answered for this insured: did anyone other "
                 "than you receive per diem or accelerated death benefit payments covering this insured "
                 "in 2025? The per diem limitation belongs to the insured and is shared among all "
                 "payees, so this cannot be assumed — answering 'No' when the answer is 'Yes' would "
                 "understate the taxable payments on line 26."),
     "notes": ("R-8853C-MULTIPAYEE. ERROR, not a warning: the unanswered default would be "
               "taxpayer-favourable (a full limitation instead of a shared one). §7702B(d)(3).")},

    {"diagnostic_id": "D_8853C_MULTIPAYEE_HOLD", "title": "Multiple payees for this insured — shared per diem limitation not computed", "severity": "error",
     "condition": "line15 == 'yes' AND NOT terminally-ill-ADB-only",
     "message": ("Someone other than you also received long-term care or accelerated death benefit "
                 "payments covering this insured, so the per diem limitation must be shared: it is "
                 "allocated first to the insured, then pro rata among the other policyholders, and an "
                 "aggregate statement must be attached to every payee's return. This software does not "
                 "compute the shared allocation. Figure lines 25 and 26 from the aggregate statement "
                 "and enter them directly, leaving lines 21 through 24 blank, or prepare this Form 8853 "
                 "outside the software."),
     "notes": ("R-8853C-MULTIPAYEE. Holds the return rather than computing a full limitation for a "
               "shared one — which would UNDER-report taxable income. i8853 Multiple Payees.")},

    {"diagnostic_id": "D_8853C_MULTI_PERIOD", "title": "More than one LTC period — separate Sections C required", "severity": "error",
     "condition": "ltc_period_index > 1 OR more than one LTC period asserted for one insured",
     "message": ("This insured has more than one long-term care period, and the taxable amount must be "
                 "figured separately for each one on its own Section C, with the line 26 amounts added "
                 "together. This version computes a single LTC period. Prepare the additional periods "
                 "outside the software, or re-check whether one period (the equal payment rate method) "
                 "applies."),
     "notes": ("R-8853C-PERIOD. i8853 line 18 Caution. Blending periods produces a wrong line 21, so "
               "this refuses rather than approximates.")},

    {"diagnostic_id": "D_8853C_DAYS_RANGE", "title": "Days in the LTC period are outside 1-365", "severity": "error",
     "condition": "Section C engaged AND (ltc_period_days < 1 OR ltc_period_days > 365)",
     "message": ("The number of days in the LTC period must be between 1 and 365 for 2025. Check the "
                 "period against the method chosen: under the contract period method the period is the "
                 "insurer's own benefit-computation period (1 day if benefits are computed daily); "
                 "under the equal payment rate method it is the span over which one payment rate "
                 "applies."),
     "notes": ("R-8853C-PERIOD. ERROR — an arithmetically impossible value is never acknowledgable "
               "(house rule, s215). 2025 is not a leap year.")},

    {"diagnostic_id": "D_8853C_NONQUALIFIED", "title": "Part of the per-diem benefits is from a NON-qualified LTC contract", "severity": "warning",
     "condition": "line17 > line18",
     "message": ("Part of the per diem long-term care benefits for this insured is not from a qualified "
                 "long-term care insurance contract (line 17 exceeds line 18). Form 8853 does not "
                 "figure the taxable amount of non-qualified benefits — if that portion is not "
                 "excludable from income, it must be reported on Schedule 1 (Form 1040) line 8e "
                 "separately. This software does not compute it."),
     "notes": ("R-8853C-LINE20. The face's own line 17 Caution. The gap is a different computation, "
               "not a rounding difference.")},

    {"diagnostic_id": "D_8853C_QUALIFIED_UNCONFIRMED", "title": "1099-LTC box 4 is blank — qualified-contract status needs confirming", "severity": "warning",
     "condition": "a 1099-LTC row for this insured has box 4 unchecked AND line18 > 0",
     "message": ("Box 4 (qualified contract) is not checked on a Form 1099-LTC for this insured, but "
                 "the benefits are being treated as from a qualified long-term care insurance contract. "
                 "Box 4 is optional for the payer, so a blank box is not evidence either way — confirm "
                 "the contract's status from the policy before relying on lines 18 through 26."),
     "notes": ("⚠ The s224 'missing column read as a missing box' class, inverted: absence of an "
               "OPTIONAL box must never be read as a negative answer.")},

    {"diagnostic_id": "D_8853C_BOX3_UNCHECKED", "title": "1099-LTC box 3 is blank — per diem vs reimbursement basis unrouted", "severity": "warning",
     "condition": "a 1099-LTC row for this insured has neither box 3 option checked AND (box1 > 0 OR box2 > 0)",
     "message": ("Neither 'Per diem' nor 'Reimbursed amount' is checked in box 3 of a Form 1099-LTC for "
                 "this insured, so the software cannot tell whether the benefits belong on line 17 (per "
                 "diem) or line 24 (reimbursement). Box 3 may be left blank when the insured was "
                 "terminally ill. Indicate the basis for this form."),
     "notes": ("R-8853C-LINE17. The row is NOT silently dropped from line 17 — that would be a silent "
               "understatement of gross benefits.")},

    {"diagnostic_id": "D_8853C_TERMINAL_UNCONFIRMED", "title": "1099-LTC shows terminally ill but line 16 is unanswered", "severity": "warning",
     "condition": "a 1099-LTC row for this insured has box 5 'Terminally ill' checked AND line16 == 'unanswered'",
     "message": ("A Form 1099-LTC for this insured indicates the insured was certified terminally ill, "
                 "but line 16 has not been answered. If the insured was terminally ill and the only "
                 "payments received were accelerated death benefits paid for that reason, the benefits "
                 "are fully excludable and line 26 is zero. Answer line 16 and confirm whether any "
                 "other payments were received."),
     "notes": ("R-8853C-LINE26 / §101(g)(1). Deliberately a WARNING: the software must not route into "
               "the zero path on the strength of an optional box, since that path is the most "
               "favourable outcome on the form.")},

    {"diagnostic_id": "D_8853C_ADB_TERMINAL_INCLUDED", "title": "Line 19 may include terminally-ill accelerated death benefits", "severity": "warning",
     "condition": "line19 > 0 AND line16 == 'yes' AND NOT terminally-ill-ADB-only",
     "message": ("Line 19 should include accelerated death benefits received only while the insured was "
                 "chronically ill. This insured was certified terminally ill, so any benefits received "
                 "after that certification must be excluded from line 19 — if the insured was "
                 "redesignated during 2025, include only the payments received before the terminal "
                 "certification date."),
     "notes": "i8853 line 19; §101(g)(4)(B) makes the two statuses mutually exclusive."},

    {"diagnostic_id": "D_8853C_PRE1996_UNCONFIRMED", "title": "Pre-August-1996 contract claimed — the modification question must be answered", "severity": "warning",
     "condition": "pre_aug1996_contract == True AND pre_aug1996_modified is unanswered",
     "message": ("Reimbursements are being excluded from line 24 because the contract was issued before "
                 "August 1, 1996. That exclusion does not apply if the contract was exchanged or "
                 "modified after July 31, 1996 to increase per diem payments or reimbursements. Confirm "
                 "whether it was — excluding the reimbursements increases the per diem limitation and "
                 "reduces the taxable payments on line 26."),
     "notes": ("R-8853C-LIMIT. ⚠ The carve-out is taxpayer-favourable, so its condition must be "
               "affirmatively confirmed rather than assumed. i8853 line 24 Caution.")},

    {"diagnostic_id": "D_8853C_NO_1099LTC", "title": "Section C amounts keyed with no Form 1099-LTC on the return", "severity": "warning",
     "condition": "Section C engaged AND no 1099-LTC row exists for this insured",
     "message": ("Form 8853 Section C has been completed for this insured, but no Form 1099-LTC has "
                 "been entered. Payers must issue a Form 1099-LTC for long-term care and accelerated "
                 "death benefits; enter it so the gross amounts on lines 17 and 19 can be reconciled "
                 "against the payer's reporting."),
     "notes": "Completeness, not accuracy — a warning. The reconciliation is the QA (s180 lesson)."},

    {"diagnostic_id": "D_8853C_NR_UNWIRED", "title": "1040-NR long-term care payments are not routed", "severity": "error",
     "condition": "return type == 1040-NR AND sch1_8e_component > 0",
     "message": ("Taxable long-term care payments on a Form 1040-NR must be reported on Schedule NEC "
                 "(Form 1040-NR) line 12 with the literal 'LTC' and the amount. This software routes "
                 "them only to Schedule 1 (Form 1040) line 8e and does not support the Form 1040-NR "
                 "destination. Prepare this return's Section C outside the software."),
     "notes": ("R-8853C-DEST. Refuse-don't-omit at the destination seam (the s230 rule): the amount is "
               "real and must not silently vanish because its route is unbuilt.")},
]

N_SCENARIOS: list[dict] = [
    # ── The IRS's own published examples, transcribed verbatim. An IRS answer key
    #    beats any example we could invent, and it independently validates the
    #    $420 rate, the greater-of, and the zero floor all at once.
    {"scenario_name": "8853C-T1 — i8853 Example 1 verbatim (single period, fully excluded)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 24000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 365,
                "line22_costs_incurred": 54750, "line24_reimbursements": 27375,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 24000, "f8853c_line21_dollar_limit": 153300,
                          "f8853c_line23_greater": 153300, "f8853c_line25_per_diem_limitation": 125925,
                          "f8853c_line26_taxable": 0, "f8853c_sch1_8e_component": 0},
     "notes": ("i8853 (2025) Example 1, every line as the IRS prints it: Alex, chronically ill, "
               "$2,000/month for 12 months = $24,000; costs $150/day = $54,750; reimbursed half = "
               "$27,375; equal payment rate method, one period of 365 days. 420 x 365 = 153,300 "
               "confirms the rate. Line 23 takes the DOLLAR amount here (153,300 > 54,750). Nothing "
               "taxable.")},

    {"scenario_name": "8853C-T2 — i8853 Example 2 Step 1 (first LTC period, 181 days)", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 12000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 181,
                "line22_costs_incurred": 27150, "line24_reimbursements": 13575,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 12000, "f8853c_line21_dollar_limit": 76020,
                          "f8853c_line23_greater": 76020, "f8853c_line25_per_diem_limitation": 62445,
                          "f8853c_line26_taxable": 0},
     "notes": ("i8853 Example 2 Step 1 verbatim. 420 x 181 = 76,020. Pins the day count as a real "
               "multiplicand rather than an always-365 constant — 181 + 184 = 365 across the two "
               "periods of the example.")},

    {"scenario_name": "8853C-T3 — i8853 Example 2 Step 2 (aggregate, second period, 184 days)", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 63000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 184,
                "line22_costs_incurred": 27600, "line24_reimbursements": 13800,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 63000, "f8853c_line21_dollar_limit": 77280,
                          "f8853c_line23_greater": 77280, "f8853c_line25_per_diem_limitation": 63480,
                          "f8853c_line26_taxable": 0},
     "notes": ("i8853 Example 2 Step 2 — the AGGREGATE statement for the second period (Alex $2,000 + "
               "Blair $5,500 + Casey $3,000 = $10,500/month x 6). 420 x 184 = 77,280. Run here as the "
               "arithmetic of the aggregate computation; the ALLOCATION that follows it (Step 3) is the "
               "unbuilt Multiple Payees path — see T6.")},

    {"scenario_name": "8853C-T4 — daily contract period: the taxable case", "scenario_type": "normal", "sort_order": 4,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 2000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "contract_period", "ltc_period_days": 1,
                "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 2000, "f8853c_line21_dollar_limit": 420,
                          "f8853c_line23_greater": 420, "f8853c_line25_per_diem_limitation": 420,
                          "f8853c_line26_taxable": 1580, "f8853c_sch1_8e_component": 1580},
     "notes": ("The case the whole form exists for, and the one every other scenario fails to exercise: "
               "line 26 NONZERO. A daily-benefit contract under the contract period method gives a "
               "1-day period, so the limitation is a single $420. 2,000 − 420 = 1,580 to Schedule 1 "
               "line 8e. If a build defaulted days to 365 this would wrongly compute zero.")},

    {"scenario_name": "8853C-T5 — costs exceed the dollar limit: line 23 takes the COSTS", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 250000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 365,
                "line22_costs_incurred": 200000, "line24_reimbursements": 0,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 250000, "f8853c_line21_dollar_limit": 153300,
                          "f8853c_line23_greater": 200000, "f8853c_line25_per_diem_limitation": 200000,
                          "f8853c_line26_taxable": 50000},
     "notes": ("§7702B(d)(2)'s 'greater of' in the direction the IRS examples never show: real costs "
               "(200,000) above the dollar limit (153,300), so line 23 = costs. A min-for-max slip "
               "would give 153,300 and OVER-tax by 46,700 — the opposite sign from most defects on this "
               "form, which is why it gets its own scenario and its own flow assertion.")},

    {"scenario_name": "8853C-T6 — terminally ill, ADB only: skip 17-25, line 26 = -0-", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"tax_year": 2025, "line19_adb_chronically_ill": 0, "adb_terminal_amount": 500000,
                "line15_other_payees": "no", "line16_terminally_ill": "yes",
                "adb_only_because_terminal": True},
     "expected_outputs": {"f8853c_line26_taxable": 0, "f8853c_sch1_8e_component": 0,
                          "skipped_17_25": True},
     "notes": ("§101(g)(1): accelerated death benefits for a terminally ill insured are excludable "
               "outright, however large. Lines 17-25 are SKIPPED (blank, not zero). Note line 19 is "
               "zero — terminally-ill ADB never lands there.")},

    {"scenario_name": "8853C-T7 — terminally ill BUT per-diem LTC benefits too: no short circuit", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 30000, "line19_adb_chronically_ill": 0,
                "adb_terminal_amount": 100000, "ltc_period_method": "contract_period",
                "ltc_period_days": 1, "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "no", "line16_terminally_ill": "yes",
                "adb_only_because_terminal": False},
     "expected_outputs": {"f8853c_line20_total": 30000, "f8853c_line21_dollar_limit": 420,
                          "f8853c_line25_per_diem_limitation": 420, "f8853c_line26_taxable": 29580},
     "notes": ("⚠ THE NARROWNESS OF THE SHORT CIRCUIT, pinned. Line 16 = Yes is NOT sufficient: the "
               "face requires that the ONLY payments were ADB paid because of terminal illness. A "
               "build that short-circuits on line 16 alone would exclude 29,580 of genuinely taxable "
               "per-diem benefits. The terminally-ill ADB itself stays excluded.")},

    {"scenario_name": "8853C-T8 — multiple payees: HOLD, nothing computed", "scenario_type": "failure", "sort_order": 8,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 33000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 184,
                "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "yes", "line16_terminally_ill": "no"},
     "expected_outputs": {"D_8853C_MULTIPAYEE_HOLD": True, "f8853c_sch1_8e_component": None,
                          "f8853c_line26_taxable": None},
     "notes": ("Blair's figures from i8853 Example 2. Left alone the engine would compute a full "
               "77,280 limitation and a zero line 26; the aggregate statement gives Blair an allocated "
               "share of 33,311. Computing the unshared limitation UNDER-reports, so the return holds "
               "and no 8e contribution is made.")},

    {"scenario_name": "8853C-T9 — line 15 unanswered: error, not an assumed 'No'", "scenario_type": "failure", "sort_order": 9,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 24000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 365,
                "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "unanswered", "line16_terminally_ill": "no"},
     "expected_outputs": {"D_8853C_PAYEE_UNANSWERED": True},
     "notes": ("The s231 sign rule applied to a question rather than a row: the permissive answer "
               "('no' → full limitation) must never be the silent default. Pinned as an ERROR so it "
               "blocks the return from Done.")},

    {"scenario_name": "8853C-T10 — pre-Aug-1996 contract: reimbursements out of line 24", "scenario_type": "edge", "sort_order": 10,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 100000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "contract_period", "ltc_period_days": 180,
                "line22_costs_incurred": 0, "line24_reimbursements": 40000,
                "pre_aug1996_contract": True, "pre_aug1996_modified": False,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line21_dollar_limit": 75600, "f8853c_line23_greater": 75600,
                          "f8853c_line24_reimbursements": 0,
                          "f8853c_line25_per_diem_limitation": 75600,
                          "f8853c_line26_taxable": 24400},
     "notes": ("420 x 180 = 75,600. The grandfathered reimbursements drop OUT of line 24, so line 25 "
               "stays 75,600 and taxable = 100,000 − 75,600 = 24,400. With the reimbursements included "
               "line 25 would be 35,600 and taxable 64,400 — a 40,000 swing, which is why the "
               "carve-out defaults OFF and its modification question is asked.")},

    {"scenario_name": "8853C-T11 — days out of range: arithmetically impossible", "scenario_type": "failure", "sort_order": 11,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 24000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "equal_payment_rate", "ltc_period_days": 400,
                "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"D_8853C_DAYS_RANGE": True},
     "notes": ("400 days in a 365-day year. ERROR, never acknowledgable (s215 house rule). The sign "
               "matters: an inflated day count inflates the limitation and under-reports income.")},

    {"scenario_name": "8853C-T12 — 8e is COMPOSED: Section C joins a keyed A/B residual", "scenario_type": "normal", "sort_order": 12,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 2000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "contract_period", "ltc_period_days": 1,
                "line22_costs_incurred": 0, "line24_reimbursements": 0,
                "line15_other_payees": "no", "line16_terminally_ill": "no",
                "sch1_8e_keyed_ab_residual": 3000},
     "expected_outputs": {"f8853c_line26_taxable": 1580, "f8853c_sch1_8e_component": 1580,
                          "sch1_line_8e": 4580},
     "notes": ("⚠⚠ THE REGISTRY PIN (s230 K13g precedent). A return with $3,000 of Archer MSA taxable "
               "distributions keyed on 8e plus $1,580 of Section C must show 8e = 4,580, not 1,580. "
               "The failure mode a single-writer build produces is a DISAPPEARED number — the keyed "
               "3,000 silently overwritten — which is exactly why nobody would ever report it.")},

    {"scenario_name": "8853C-T13 — no Section C: 8e keeps what the preparer typed (zero movement)", "scenario_type": "edge", "sort_order": 13,
     "inputs": {"tax_year": 2025, "sch1_8e_keyed_ab_residual": 3000, "section_c_present": False},
     "expected_outputs": {"sch1_line_8e": 3000, "f8853c_sch1_8e_component": 0},
     "notes": ("The movement guard (s227 pattern): making 8e engine-fed must not disturb the returns "
               "already keyed. Every stored return without a Section C is unchanged — this is the "
               "regression that pins it.")},

    {"scenario_name": "8853C-T14 — reimbursements exceed line 23: line 25 FLOORS at zero", "scenario_type": "edge", "sort_order": 14,
     "inputs": {"tax_year": 2025, "line18_qualified_per_diem": 10000, "line19_adb_chronically_ill": 0,
                "ltc_period_method": "contract_period", "ltc_period_days": 1,
                "line22_costs_incurred": 0, "line24_reimbursements": 5420,
                "line15_other_payees": "no", "line16_terminally_ill": "no"},
     "expected_outputs": {"f8853c_line20_total": 10000, "f8853c_line21_dollar_limit": 420,
                          "f8853c_line23_greater": 420, "f8853c_line25_per_diem_limitation": 0,
                          "f8853c_line26_taxable": 10000, "f8853c_sch1_8e_component": 10000},
     "notes": ("⚠⚠ THE DEFECT THE STATUTE CAUGHT. Reimbursements of 5,420 against a line 23 of 420 "
               "give 420 − 5,420 = −5,000 before the floor. UNFLOORED, line 26 = 10,000 − (−5,000) = "
               "15,000 — taxing 15,000 when only 10,000 was received, which is impossible. "
               "§7702B(d)(2)'s 'excess (if any)' floors line 25 at zero, so all 10,000 (and no more) is "
               "taxable. The FACE prints no floor on line 25, only on line 26, so a face-only build "
               "gets this wrong — and the first draft of this spec did.")},
]

N_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-8853C-SCOPE", "IRS_2025_F8853_FORM", "primary", "Section C is the LTC half of Form 8853"),
    ("R-8853C-SCOPE", "IRC_7702B_D", "secondary", "§7702B(d)(3) aggregates by INSURED — the unit of the section"),
    ("R-8853C-FILING", "IRS_2025_F8853_INSTR", "primary", "The Filing Requirements for Section C flowchart, per insured"),
    ("R-8853C-LINE17", "IRS_2025_F8853_FORM", "primary", "Line 17 = Σ box 1 where box 3 'Per diem' is checked"),
    ("R-8853C-LINE17", "IRS_1099LTC_FORM", "secondary", "Box 3 is the router; it may be blank when the insured was terminally ill"),
    ("R-8853C-LINE20", "IRS_2025_F8853_FORM", "primary", "Line 20 = 18 + 19; the line 17 Caution excludes non-qualified benefits"),
    ("R-8853C-LINE20", "IRC_101_G", "secondary", "§101(g)(3) pools chronically-ill ADB with qualified LTC benefits"),
    ("R-8853C-LIMIT", "IRC_7702B_D", "primary", "§7702B(d)(2) — greater of dollars or costs, less reimbursements"),
    ("R-8853C-LIMIT", "RP_2024_40", "primary", "§2.62 — the 2025 per diem amount is $420"),
    ("R-8853C-LIMIT", "IRS_2025_F8853_INSTR", "secondary", "Line 24's pre-August-1-1996 carve-out and its post-7/31/1996 claw-back"),
    ("R-8853C-LINE26", "IRC_7702B_D", "primary", "§7702B(d)(1) — the excess over the limitation is includible"),
    ("R-8853C-LINE26", "IRC_101_G", "primary", "§101(g)(1) — the terminally-ill outright exclusion (the short circuit)"),
    ("R-8853C-MULTIPAYEE", "IRC_7702B_D", "primary", "§7702B(d)(3) — one person per insured; insured allocated first"),
    ("R-8853C-MULTIPAYEE", "IRS_2025_F8853_INSTR", "primary", "Multiple Payees: the aggregate statement and pro-rata allocation"),
    ("R-8853C-PERIOD", "IRS_2025_F8853_INSTR", "primary", "The two LTC-period methods; one Section C per period"),
    ("R-8853C-DEST", "IRS_2025_F8853_FORM", "primary", "Line 26 → 'the TOTAL on' Schedule 1 line 8e; 1040-NR Sch NEC line 12 'LTC'"),
    ("R-8853C-DEST", "IRS_2025_SCH1_FORM", "implementation", "Line 8e is the composed Archer MSA / Medicare Advantage / LTC line"),
    ("R-8853C-ATTACH", "IRS_2025_F8853_FORM", "implementation", "The form is attached and transmitted — a real render and MeF leg"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-1040-8853C-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Section C line 26 reaches Schedule 1 line 8e as a COMPONENT, never as the whole line",
     "description": ("Validates R-8853C-DEST. Exercises T12: a keyed Sections A/B residual of 3,000 plus "
                     "a Section C line 26 of 1,580 must give 8e = 4,580. Bug it catches: the Section C "
                     "writer OWNING 8e and silently erasing the preparer's Archer MSA figure — the s230 "
                     "K13g failure mode, whose symptom is a DISAPPEARED number that no one reports. "
                     "Also catches the reverse: a Section C component that never reaches 8e at all."),
     "status": "active"},

    {"assertion_id": "FA-1040-8853C-02", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Line 23 takes the GREATER of line 21 and line 22 — in both directions",
     "description": ("Validates R-8853C-LIMIT against §7702B(d)(2). Exercises T1 (dollars 153,300 > "
                     "costs 54,750 → 153,300) AND T5 (costs 200,000 > dollars 153,300 → 200,000), "
                     "because a min-for-max slip passes T1 by luck — the s219 'value that cancels by "
                     "luck' class. In T5 the slip OVER-taxes by 46,700, the opposite sign from most "
                     "defects here."),
     "status": "active"},

    {"assertion_id": "FA-1040-8853C-03", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Line 26 is floored at zero and the day count is a real multiplicand",
     "description": ("Validates R-8853C-LINE26 and R-8853C-PERIOD. Exercises T2/T3 (181 and 184 days, "
                     "so 420 x days is genuinely computed rather than hardcoded to a year) and T4 (1 "
                     "day → 420 → a NONZERO line 26 of 1,580). Bug it catches: days defaulting to 365, "
                     "which silently zeroes the taxable amount on every daily-benefit contract; and a "
                     "negative line 26 flowing into 8e as an offset against other income."),
     "status": "active"},

    {"assertion_id": "FA-1040-8853C-04", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "A refused Section C contributes NOTHING to 8e — and says so",
     "description": ("Validates R-8853C-MULTIPAYEE, R-8853C-PERIOD and R-8853C-DEST's refusal seam. "
                     "Exercises T8 (line 15 = Yes → D_8853C_MULTIPAYEE_HOLD, no 8e contribution), T9 "
                     "(line 15 unanswered → error, not an assumed 'No'), T11 (400 days → error). Bug it "
                     "catches: a hold that still lets a computed full-limitation line 26 reach 8e, "
                     "which would UNDER-report taxable income while the return looks complete."),
     "status": "active"},

    {"assertion_id": "FA-1040-8853C-05", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The terminally-ill short circuit needs BOTH conditions, and 8e does not move without Section C",
     "description": ("Validates R-8853C-LINE26's short circuit and the zero-movement guarantee. "
                     "Exercises T6 (terminally ill, ADB only → line 26 = 0, lines 17-25 blank), T7 "
                     "(terminally ill BUT per-diem benefits too → full computation, 29,580 taxable) and "
                     "T13 (no Section C → 8e keeps the keyed 3,000). Bug it catches: short-circuiting "
                     "on line 16 alone, which excludes genuinely taxable per-diem benefits; and the 8e "
                     "composition disturbing returns that have no Section C at all."),
     "status": "active"},
]


FORMS: list[dict] = [
    {"identity": N_IDENTITY, "facts": N_FACTS, "rules": N_RULES, "lines": N_LINES,
     "diagnostics": N_DIAGNOSTICS, "scenarios": N_SCENARIOS, "rule_links": N_RULE_LINKS},
]


class Command(BaseCommand):
    help = "Load the 8853_SEC_C spec (Form 8853 Section C, long-term care). Refuses until READY_TO_SEED=True."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad 8853_SEC_C spec (Form 8853 Section C — long-term care insurance contracts)\n"))
        self._load_topics()
        sources = self._load_sources()
        self._load_new_excerpts_on_existing(sources)
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
                "\nREFUSING TO SEED 8853_SEC_C: not cleared to seed.\n\n"
                "Gated until Ken's Gate-1 review walk. The items to walk:\n"
                "  1. Schedule 1 line 8e becomes COMPOSED (Section C component + keyed A/B\n"
                "     residual), per the s230 Schedule-K-13g registry ruling.\n"
                "  2. Multiple Payees (line 15 = Yes) is REFUSED, not approximated — computing\n"
                "     an unshared limitation would UNDER-report taxable income.\n"
                "  3. Line 15 and line 16 are three-state (yes/no/unanswered); the permissive\n"
                "     answer is never the silent default.\n"
                "  4. The LTC-period day count is a preparer ELECTION between two methods, with\n"
                "     only a 1-365 range check available.\n"
                "  5. The pre-August-1-1996 reimbursement carve-out defaults OFF.\n"
                "  6. Sections A/B stay out of scope; Form 8889 line 4 stays keyed.\n"
                "  7. requires_human_review verbatims: §7702B(d)(2)'s 'greater of' wording and\n"
                "     the §101(g)(3) conditions.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
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
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
            else:
                self.stdout.write(self.style.WARNING(
                    f"  expected existing source {code} not found — its rule links will be skipped"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _load_new_excerpts_on_existing(self, sources):
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if src:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc)
            else:
                self.stdout.write(self.style.WARNING(
                    f"  cannot attach excerpt to missing source {code}"))

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]})
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
                    defaults={"support_level": level, "relevance_note": note})
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
                    defaults={"note": f"{source_code} -> {form_code}"})

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"TaxForms: {TaxForm.objects.count()} | FlowAssertions: {FlowAssertion.objects.count()}")
        form = TaxForm.objects.filter(form_number="8853_SEC_C").first()
        if form:
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("8853_SEC_C: all rules cited" if not uncited
                              else self.style.WARNING(f"8853_SEC_C uncited rules: {len(uncited)}"))
