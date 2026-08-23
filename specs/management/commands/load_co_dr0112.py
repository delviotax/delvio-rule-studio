"""Load the Colorado Form DR 0112 spec - C Corporation Income Tax Return (TY2025).

WO-W05-CCORP. Colorado's walk closed at campaign **D-27**, which also completed
Wave 5 Layer 2 (seven of seven states walked).

═══════════════════════════════════════════════════════════════════════════
⚠⚠ C2 - WHERE THE SIX TESTS DIVERGE, THE BUILD ORDER IS:
       BUILD THE STATUTE · PROMPT WITH THE FORM · DIAGNOSE THE GUIDE
═══════════════════════════════════════════════════════════════════════════
The six tests of unity diverge **THREE ways** - § 39-22-303(11)(a) C.R.S., the
Corporate Income Tax Guide, and the DR 0112C face - and **in BOTH directions**,
so "just build the form's wording" was never available:

  test 1  statute/Guide say `gross OPERATING receipts`; the form says
          `gross receipts` - BROADER
  test 2  the form adds `the total annual value of EACH OF` - NARROWEST
  test 3  the Guide drops `or more` from `twenty percent or more`
  test 4  statute is ONE-directional; the Guide is BIDIRECTIONAL; the form is
          one-directional AND drops `substantially`
  test 5  statute one-directional; Guide bidirectional; form one-directional

A build that picked any single text would be wrong on at least two tests, in
opposite directions. **The statute is built; the form's wording is what the
preparer is PROMPTED with; the Guide's divergences are DIAGNOSED.**

⚠ Schedule C is triggered by **§ 303(12) affiliated-group membership**, NOT by
the Section B box. ⚠ The partnership look-through covers **tests 1-4 only**.
⚠ **Combined-group-as-taxpayer and joint-and-several liability are TY2026-ONLY**
- do NOT model the TY2025 group as an entity.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ TY2026 IS A RATIFIED RE-AUTHORING EVENT - AND THE CLIFF IS FOUR CHANGES
═══════════════════════════════════════════════════════════════════════════
D-27 ratified TY2026 as a re-authoring event, not a rate bump:
  1. the **HB 24-1134 combined regime** replaces the six tests of unity;
  2. the **listed jurisdictions** rule;
  3. the **§ 250 FDDEI add-back**;
  4. **removal of the $150,000 line-17 cap** - § 39-22-304(3)(p)(II)(B), C.R.S.
     *(the fourth was added by the verification pass.)*
§ 39-22-303(11) itself opens `For tax years beginning before January 1, 2026:`.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ W5 - THE DEPRECIATION "NEGATIVE" IS AN AFFIRMATIVE RULING WITH A CITATION
═══════════════════════════════════════════════════════════════════════════
A **class-(b) correction** - "we found no rule" masquerading as "the rule says
no" - caught by the verification pass and confirmed first-hand.

**§ 39-22-304(3)(p)(III), C.R.S., verbatim:**
  "A taxpayer that applies the subtraction allowed in this subsection (3)(p)
   with respect to qualified improvement property shall calculate the gain or
   loss on a sale of such qualified improvement property for purposes of the
   subtraction in subsection (3)(c) of this section using the basis reported on
   their federal income tax return at the time of the sale."

It does TWO things at once:
  1. it **DIRECTS the use of FEDERAL basis** for QIP - so "federal basis governs"
     is a POSITIVE statutory instruction, not an absence; and
  2. it **expressly cross-references § 304(3)(c)**, which proves that subsection
     is **LIVE LAW, not archaeology** - the legislature legislated about it in 2021.

⚠ And the `acquired prior to January 1, 1965` condition is a **GUIDE GLOSS**. The
statutory text of § 39-22-304(3)(c) was read in full from CRS 2024 and carries
**NO date limitation of any kind**. Two prior readings of this brief were wrong.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ THE $5,000 QUESTION IS **TWO** PREDICATES, NOT ONE (Layer 1, campaign D-18)
═══════════════════════════════════════════════════════════════════════════
The apparent "3-2 source split" was a CATEGORY ERROR, not a source conflict.
There are two different rules with two different thresholds, and they are not in
conflict because they are not the same rule:

  RULE 1 - the OBLIGATION to remit. `greater than` / `exceeds` $5,000.
           DR 0112 p.1, DR 0112EP and Guide Part 9 are unanimous.
  RULE 2 - the PENALTY exception. `less than` $5,000, at STATUTE level:
           § 39-22-606(6)(a)(I), C.R.S.: "No addition to tax shall be imposed ...
           if the tax ... is LESS THAN five thousand dollars."

**So penalty exposure begins AT $5,000, while the payment obligation begins
ABOVE it.** A taxpayer with net tax of exactly $5,000 owes no estimates and is
still exposed to the penalty. Encoding one predicate for both is wrong at
exactly one point - and that point is a round number taxpayers land on.

SAFETY GUARD - READY_TO_SEED stays False until Ken's Gate-1 SEED approval.
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
# SAFETY GUARD - flip ONLY on Ken's Gate-1 SEED approval, given DIRECTLY.
# D-27 approved the walk SCOPE. That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True   # ⚠ OPENED 2026-08-23 on Ken's DIRECT Gate-1 SEED approval ("seed all three"), given unmediated in session. Pre-flight clean: prod 164 forms, no two-writers hazard, all references resolve.


FORM_JURISDICTION = "CO"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# ───────────────────────────────────────────────────────────────────────────
# THE RATE - § 39-22-301(1)(d)(I)(K), C.R.S., with the override named INSIDE
# the rate statute itself ("Except as otherwise provided in section 39-22-627").
# ⚠ W9: the year is selected from the DEEMED COMMENCEMENT DATE, never the
# calendar start date. Guide Part 10: "the tax year is deemed to have commenced
# on the first day of the calendar month beginning nearest to the first day of
# the 52-53 week year", and Part 3: the rate follows that deemed January 1.
# So a DECEMBER-starting 52-53 week year takes the FOLLOWING year's rate.
# ⚠⚠ TY2027/28 are DELIBERATELY ABSENT. Legislative Council Staff PROJECT 4.33%
# and 4.29%, but a projection is not an enacted rate and this campaign does not
# fill gaps with plausible figures. Extending the year must re-verify § 39-22-627.
# ───────────────────────────────────────────────────────────────────────────
CO_CCORP_RATE: dict[int, str] = {
    2022: "0.044",
    2023: "0.044",
    2024: "0.0425",   # a ONE-OFF directive in § 39-22-627(1)(c) naming TY2024 only
    2025: "0.044",
    2026: "0.044",
}
CO_RATE_OVERRIDE_AUTHORITY = "§ 39-22-627, C.R.S. (TABOR) - named inside § 39-22-301 itself"

# § 39-22-608(2)(b), C.R.S., enacted by HB 23-1277 (ch. 290, p.1753, § 3, eff.
# 2023-08-07) - an EXCEPTION carved out of (2)(a)'s general fourth-month rule.
CO_RETURN_DUE_MONTH: dict[int, int] = {2025: 5}     # fifteenth day of the FIFTH month
CO_RETURN_DUE_DAY: dict[int, int] = {2025: 15}
CO_EXTENSION_MONTHS: dict[int, int] = {2025: 6}     # automatic, ALL C corporations
CO_EXTENSION_IS_PAYMENT_EXTENSION = False           # "there is not an extension to the payment"

# ⚠⚠ TWO PREDICATES, NOT ONE (campaign D-18 / D-12 B2 as corrected).
CO_ESTIMATED_OBLIGATION_THRESHOLD: dict[int, int] = {2025: 5000}   # Rule 1: liability > this
CO_ESTIMATED_PENALTY_EXCEPTION_THRESHOLD: dict[int, int] = {2025: 5000}  # Rule 2: tax < this
# They carry the SAME number and DIFFERENT comparison operators. Keeping them as
# two constants is the point: a future year could move one and not the other, and
# a single constant would hide that.

# C3 - the NOL ledger is VINTAGED. § 39-22-504(3), C.R.S. + Guide Part 8.
# ⚠ The post-2020 reversion to 20 years is COLORADO-ONLY - federal post-2017 NOLs
# carry forward indefinitely. None => unlimited.
CO_NOL_CARRYFORWARD_BY_VINTAGE: tuple = (
    # (first_loss_year_inclusive, last_loss_year_inclusive, carryforward_years)
    (None, 2017, 20),
    (2018, 2020, None),        # unlimited
    (2021, None, 20),
)
# § 39-22-504(4) - a financial-institution special rule the Guide's table OMITS.
# "financial institution" means any institution to which IRC § 585 or § 593 applies.
# ⚠ Still live for 2006-2020 vintages on a TY2025 return.
CO_NOL_FINANCIAL_INSTITUTION_YEARS: int = 15
CO_NOL_FINANCIAL_INSTITUTION_RANGE: tuple = (1984, 2020)
# § 39-22-504(3)(b): "Net operating losses of corporations may not be carried back
# to an earlier tax year." No carryback in ANY year.
CO_NOL_CARRYBACK_YEARS: dict[int, int] = {2025: 0}
# § 39-22-504(1)(b): the 80% limitation applies "without regard to the amendments
# made in section 2303 of the ... CARES Act" - Colorado DECOUPLED from CARES relief.
CO_NOL_80PCT_LIMIT: dict[int, str] = {2025: "0.80"}

# Line 17 - the HB21-1002 CARES-Act carryforward subtraction.
# ⚠ § 39-22-304(3)(p)(II)(B) REMOVES this cap for TY2026 - cliff item 4 of 4.
CO_HB21_1002_CAP: dict[int, int | None] = {2025: 150000, 2026: None}

# C2 - the six tests of unity. ⚠ These are the STATUTORY formulations
# (§ 39-22-303(11)(a)); the form's wording is carried separately for PROMPTING and
# the Guide's divergences are DIAGNOSED. Never collapse the three.
CO_UNITY_TESTS_REQUIRED: int = 3          # "at least three of the six tests"
CO_UNITY_TESTS_TOTAL: int = 6
CO_UNITY_LOOKBACK_YEARS: int = 2          # "for the current and two preceding tax years"
CO_FOREIGN_EXCLUSION_PCT: str = "0.80"    # 80%+ property and payroll outside the US
# § 39-22-303(8)(a): "'United States' is RESTRICTED TO THE FIFTY STATES AND THE
# DISTRICT OF COLUMBIA." ⚠ Territories are NOT the United States for this test.
CO_US_DEFINITION = "the fifty states and the District of Columbia only"
# ⚠ The partnership look-through reaches tests 1-4 ONLY.
CO_PARTNERSHIP_LOOKTHROUGH_TESTS: tuple = (1, 2, 3, 4)

# ⚠⚠ TY2026 re-authoring event - FOUR changes, not three (D-27).
CO_TY2026_REAUTHORING_CHANGES: tuple = (
    "the HB 24-1134 combined regime replaces the six tests of unity",
    "the listed jurisdictions rule",
    "the § 250 FDDEI add-back",
    "removal of the $150,000 line-17 cap (§ 39-22-304(3)(p)(II)(B), C.R.S.)",
)

# ⚠⚠ W5 - AN AFFIRMATIVE RULING, NOT AN ABSENCE. See the module docstring.
CO_DEPRECIATION_MODIFICATION_EXISTS = False
CO_DEPRECIATION_RULING_AUTHORITY = (
    "§ 39-22-304(3)(p)(III), C.R.S. - it DIRECTS the use of federal basis for qualified improvement "
    "property AND cross-references § 304(3)(c), proving that subsection is live law. 'Federal basis "
    "governs' is therefore a cited positive instruction, not a failure to find a rule."
)
# ⚠ The "acquired prior to January 1, 1965" condition is a GUIDE GLOSS. The
# statutory text of § 39-22-304(3)(c) carries NO date limitation of any kind.
CO_304_3C_HAS_1965_CUTOFF_IN_STATUTE = False

# C4/C5 and the deferrals - each names what it refuses.
CO_DEFERRED_ITEMS: tuple = (
    "tax-haven inclusion (§ 39-22-303(8)(b))",
    "§ 1502 consolidated-return elimination",
    "§ 382 ownership-change limitation",
    "§ 860E REMIC excess-inclusion limitation",
    "SRLY (26 CFR § 1.1502-21)",
    "the 2011-2013 NOL suspension gross-up (§ 39-22-504(6))",
    "DR 0112X amended returns (the Box-H 180-day trigger IS built)",
)


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(
            f"No TY{year} value in {table!r} - re-verify before extending the year. ⚠ For the RATE "
            "this is deliberate: Legislative Council Staff PROJECT 4.33% (TY2027) and 4.29% "
            "(TY2028), but a projection is not an enacted rate and § 39-22-627 must be re-read."
        )
    return table[year]


def _co_rate_year_from_deemed_commencement(deemed_commencement_year: int) -> int:
    """⚠ W9 - the rate follows the DEEMED commencement date, not the calendar start.

    Guide Part 10: "the tax year is deemed to have commenced on the first day of
    the calendar month beginning nearest to the first day of the 52-53 week year."
    Guide Part 3: "In the case of a 52-53 week tax year that actually begins in
    December, but is deemed to have commenced January 1 of the following year for
    Colorado income tax purposes, THE TAX RATE IS DETERMINED BASED ON THE JANUARY 1
    DATE ON WHICH THE TAX YEAR IS DEEMED TO BEGIN."

    So a December-starting 52-53 week year takes the FOLLOWING year's rate. With
    the rate moving between years this is a live rate-selection bug, not a nicety.
    """
    return deemed_commencement_year


def _co_tax(colorado_taxable_income, rate_year: int = FORM_TAX_YEAR):
    """DR 0112 line 19 `Tax, 4.4% of the amount on line 18`."""
    return max(0.0, float(colorado_taxable_income)) * float(_yk(CO_CCORP_RATE, rate_year))


def _co_line19_with_pl86272(computed_tax, claims_pl86_272: bool):
    """⚠ P.L. 86-272 overrides LINE 19, not line 18.

    DR 0112 Section A instruction, verbatim: "A taxpayer filing a return claiming
    exemption from Colorado taxation under P.L. 86-272 must complete the return and
    applicable schedules, but ENTER $0 TAX ON LINE 19."

    The computed value is RETAINED upstream - line 18 still carries Colorado taxable
    income. Zeroing line 18 instead would corrupt the NOL ledger and the
    apportionment reconciliation, and would look identical on the printed return.
    """
    return 0.0 if claims_pl86_272 else float(computed_tax)


def _co_nol_carryforward_years(loss_year: int, is_financial_institution: bool = False):
    """C3 - the vintaged ledger. Returns None for an unlimited carryforward.

    ⚠ Colorado is NOT federal here. Federal post-2017 NOLs carry forward
    indefinitely; Colorado reverts to twenty years for losses from 2021 onward.
    """
    lo, hi = CO_NOL_FINANCIAL_INSTITUTION_RANGE
    if is_financial_institution and lo <= loss_year <= hi:
        return CO_NOL_FINANCIAL_INSTITUTION_YEARS
    for first, last, years in CO_NOL_CARRYFORWARD_BY_VINTAGE:
        if (first is None or loss_year >= first) and (last is None or loss_year <= last):
            return years
    raise CommandError(f"No Colorado NOL vintage rule covers a {loss_year} loss.")


def _co_nol_deduction(line15, pre2018_losses, post2017_losses, year: int = FORM_TAX_YEAR):
    """DR 0112 line 16(a)-(d), computed AS PRINTED.

    (a) pre-2018 losses; (b) line 15 less (a), "if zero skip to 16(d)";
    (c) post-2017 losses; (d) the sum of (a) and (c).

    ⚠ The 80% limitation applies to Colorado taxable income AFTER deducting the
    pre-2018 losses - which is exactly why (b) exists as a printed line. Applying
    80% to line 15 instead over-limits every return that has pre-2018 vintages.
    """
    limit_pct = float(_yk(CO_NOL_80PCT_LIMIT, year))
    a = min(float(pre2018_losses), max(0.0, float(line15)))
    b = max(0.0, float(line15) - a)
    c = min(float(post2017_losses), b * limit_pct)
    return {"16a": a, "16b": b, "16c": c, "16d": a + c}


def _co_line17_hb21_1002(claimed, year: int = FORM_TAX_YEAR):
    """Line 17 - the HB21-1002 CARES-Act carryforward subtraction.

    ⚠ TY2025 caps it at $150,000; § 39-22-304(3)(p)(II)(B) REMOVES the cap for
    TY2026 - cliff item 4 of 4 in the re-authoring event. `None` means uncapped.
    """
    cap = _yk(CO_HB21_1002_CAP, year)
    return float(claimed) if cap is None else min(float(claimed), float(cap))


def _co_must_remit_estimates(net_tax_liability, year: int = FORM_TAX_YEAR) -> bool:
    """RULE 1 - the OBLIGATION. `greater than` / `exceeds` $5,000. STRICTLY greater."""
    return float(net_tax_liability) > float(_yk(CO_ESTIMATED_OBLIGATION_THRESHOLD, year))


def _co_penalty_exception_applies(tax_shown, year: int = FORM_TAX_YEAR) -> bool:
    """RULE 2 - the PENALTY exception, at STATUTE level.

    § 39-22-606(6)(a)(I), C.R.S., verbatim: "No addition to tax shall be imposed
    under subsection (3) of this section for any taxable year if the tax imposed
    under part 3 of this article shown on the return for such taxable year or, if
    no return is filed, the tax, is LESS THAN five thousand dollars."

    ⚠ So penalty exposure begins AT $5,000 while the obligation begins ABOVE it.
    At exactly $5,000 a taxpayer owes no estimates AND has no exception.
    """
    return float(tax_shown) < float(_yk(CO_ESTIMATED_PENALTY_EXCEPTION_THRESHOLD, year))


def _co_combined_inclusion_required(is_affiliated_group_member: bool,
                                    pct_property_payroll_outside_us,
                                    unity_tests_met_all_three_years: int) -> bool:
    """§ 39-22-303(11) / Guide Part 2 - all THREE conditions must hold.

    ⚠ Condition 2 is the mirror of the statutory EXCLUSION at § 39-22-303(8)(a):
    a corporation with 80% OR MORE of property and payroll outside the United
    States is excluded, so inclusion needs strictly LESS than 80%.
    ⚠ "United States" is restricted to the fifty states and DC - territories are
    outside it.
    ⚠ The unity count must hold for the CURRENT AND TWO PRECEDING tax years, not
    just the current one. A single-year test over-includes.
    """
    if not is_affiliated_group_member:
        return False
    if float(pct_property_payroll_outside_us) >= float(CO_FOREIGN_EXCLUSION_PCT):
        return False
    return int(unity_tests_met_all_three_years) >= CO_UNITY_TESTS_REQUIRED


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it (campaign D-17).
    ("co_ccorp_dr0112", "Colorado Form DR 0112: the 4.4% rate keyed to the DEEMED commencement date, "
     "the fifth-month due date, the six tests of unity built from statute, the vintaged NOL ledger, "
     "and the two distinct $5,000 estimated-tax predicates."),
]

# ⚠⚠ TWO-WRITERS GUARD (D-31): these rows are OWNED elsewhere - CO_CRS_39_22_103
# by the shared conformity module `_state_conformity_tier1.py`, the rest by the
# seeded DR 0106 loader. This spec REFERENCES them and never re-declares them.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "CO_CRS_39_22_103",          # rolling conformity + the Title 39 depreciation negative
    "CO_CRS_39_22_301_RATE",     # ⚠ the CORPORATE rate statute - primary here, not a cross-reference
    "CO_CRS_39_22_608_DUE",      # (2)(b) IS the C-corp fifth-month rule
    "CO_CORP_TAX_GUIDE_2026",    # ⚠ 'governs' on the C-corp side; it only 'informed' the PTE
    "CO_CRS_39_22_347_CREDIT",   # SALT Parity owner credit -> DR 0112 line 34
    "CO_2025_DR0106K",           # the Colorado K-1; lines 16 and 25 feed DR 0112 line 34
    "CO_ITT_SALT_PARITY_2025",
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "CO_2025_DR0112", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "2025 Colorado Form DR 0112 - C Corporation Income Tax Return (rev. 10/03/25)",
        "citation": "DR 0112 (10/03/25)", "issuer": "Colorado Department of Revenue",
        "official_url": "https://tax.colorado.gov/corporate-income-tax-forms",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [
            {
                "excerpt_label": "The computational spine, lines 1-19 (verbatim labels)",
                "excerpt_text": (
                    "1 'Federal taxable income from Federal form 1120 line 30 or Form 990-T, Part I, line "
                    "11.'; 2 'Federal taxable income of companies not included in this return'; 3 'Net "
                    "federal taxable income, subtract line 2 from line 1'; 4 'Federal net operating loss "
                    "deduction'; 5 'Colorado income tax deduction'; 6 'Business meals deducted pursuant to "
                    "section 274(k)'; 7 'Other additions, submit explanation'; 8 'Sum of lines 3 through "
                    "7'; 9 'Exempt federal interest'; 10 'Excludable foreign source income'; 11 'Colorado "
                    "Marijuana and Natural Medicine Business Deduction'; 12 'Other subtractions, "
                    "explanation required below'; 13 'Sum of lines 9 through 12'; 14 'Modified federal "
                    "taxable income, subtract line 13 from line 8'; 15 'Colorado taxable income before net "
                    "operating loss deduction'; 16(a) 'Colorado net operating losses carried forward from "
                    "tax years beginning before January 1, 2018' (b) 'Subtract line 16(a) from line 15, if "
                    "zero skip to 16(d)' (c) '... on or after January 1, 2018' (d) 'Colorado net operating "
                    "loss deduction, sum of (a) and (c)'; 17 'Carryforward deduction from Income Tax Year "
                    "2021, subtractions from HB21-1002'; 18 'Colorado taxable income, subtract the sum of "
                    "lines 16(d) and 17 from line 15'; 19 'Tax, 4.4% of the amount on line 18'."
                ),
                "summary_text": "⚠ Line 2 is the whole federal/Colorado group reconciliation compressed "
                                "into one number, with NO supporting schedule - the Schedule C lists who is "
                                "in the group but carries no dollar amounts at all.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ P.L. 86-272 zeroes LINE 19, not line 18 (verbatim)",
                "excerpt_text": (
                    "DR 0112 Section A instruction, verbatim: 'A taxpayer filing a return claiming "
                    "exemption from Colorado taxation under P.L. 86-272 must complete the return and "
                    "applicable schedules, but ENTER $0 TAX ON LINE 19.' ⚠ Identical in shape to the DR "
                    "0106 rule but the LINE NUMBER DIFFERS - the campaign's standing convention (never "
                    "clone a sibling form's line numbers, even within one state) applies directly."
                ),
                "summary_text": "A post-computation override of line 19 with the computed value retained "
                                "upstream. Zeroing line 18 instead would corrupt the NOL ledger and the "
                                "apportionment reconciliation while looking identical on the printed return.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The due date and the two $5,000 rules, from the form itself",
                "excerpt_text": (
                    "p.1 Due Date, verbatim: 'You must file this return and pay any amount due by the "
                    "fifteenth day of the fifth month following the close of the taxable year, which is May "
                    "15 for calendar year filers. For filing there is an automatic extension of six months, "
                    "or until November 15 for calendar year filers, BUT NO EXTENSION IS AVAILABLE FOR "
                    "PAYMENT. Use form DR 0158-C to make an extension payment before filing. If the due "
                    "date or extension date falls on a weekend or legal holiday, filing or payment will be "
                    "due the next business day.' p.1, estimated tax: 'If next year's Colorado tax liability "
                    "will be GREATER THAN $5,000 after subtracting credits, you must make estimated tax "
                    "payments using the DR 0112EP.'"
                ),
                "summary_text": "⚠ The form states RULE 1 (the obligation, 'greater than'). RULE 2 (the "
                                "penalty exception, 'less than') lives in § 39-22-606(6)(a)(I) and is a "
                                "different rule, not a conflicting source.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0112C", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0112 Schedule C - Colorado Affiliations Schedule (06/20/25)",
        "citation": "DR 0112 Schedule C (06/20/25)", "issuer": "Colorado Department of Revenue",
        "official_url": "https://tax.colorado.gov/corporate-income-tax-forms",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ The six tests as the FORM words them - and where that differs",
            "excerpt_text": (
                "The DR 0112C prints the six tests as yes/no checkboxes 1-6 in the Guide's order, but NOT "
                "in the Guide's or the statute's words. Test 1, form: 'is 50% or more of the corporation's "
                "GROSS RECEIPTS from sales or leases to other affiliates or is 50% or more of the "
                "corporation's cost of goods sold or leased from other affiliates?' - statute and Guide "
                "both say 'gross OPERATING receipts', so the form is BROADER. Test 2, form: 'Does the "
                "corporation receive 50% or more of the TOTAL ANNUAL VALUE OF EACH OF five or more of the "
                "following services from other affiliates ... Do not count services which are provided at "
                "an \"arm's length charge.\"' - the statute deems a service provided if 50% or more of it "
                "is without an arm's-length charge within Treas. Reg. 1.482-2(b)(3), so the form is the "
                "NARROWEST of the three. Test 3, form: BIDIRECTIONAL. Test 4, form: 'Does the corporation "
                "USE patents ... owned by other affiliates?' - one-directional AND drops 'substantially'. "
                "Test 5, form: one-directional; the Guide is bidirectional. Test 6 agrees everywhere."
            ),
            "summary_text": "⚠⚠ A three-way divergence running in BOTH directions. No single text is a "
                            "safe default, which is why D-27 ruled: build the STATUTE, prompt with the "
                            "FORM, diagnose the GUIDE.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "CO_CRS_39_22_303_COMBINED", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "§ 39-22-303, C.R.S. - combined returns, the six tests, and the foreign exclusion",
        "citation": "§ 39-22-303(8), (10), (11), (12), C.R.S. (CRS 2024)",
        "issuer": "Colorado General Assembly",
        "official_url": "https://leg.colorado.gov/agencies/office-legislative-legal-services/colorado-revised-statutes",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ The statutory tests, the 80% exclusion, and the TY2026 sunset",
            "excerpt_text": (
                "§ 39-22-303(11) opens, verbatim: 'FOR TAX YEARS BEGINNING BEFORE JANUARY 1, 2026:' - the "
                "six-tests regime is itself dated. § 39-22-303(8)(a), verbatim: 'neither the taxpayer nor "
                "the executive director shall include in a combined report any C corporation that conducts "
                "business outside the United States if EIGHTY PERCENT OR MORE of the C corporation's "
                "property and payroll ... is assigned to locations outside the United States. For the "
                "purpose of this subsection (8), \"United States\" is RESTRICTED TO THE FIFTY STATES AND "
                "THE DISTRICT OF COLUMBIA.' The statutory tests are one-directional at 4 and 5, say 'gross "
                "OPERATING receipts' at 1, and say 'TWENTY PERCENT OR MORE' at 3. Property and payroll are "
                "averaged per § 24-60-1301, C.R.S. Inclusion also requires the tests to be met 'for the "
                "CURRENT AND TWO PRECEDING tax years'."
            ),
            "summary_text": "⚠ Territories are outside 'the United States' for this test. ⚠ Schedule C is "
                            "triggered by § 303(12) affiliated-group membership, NOT by the Section B box.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "CO_CRS_39_22_304_MODS", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "§ 39-22-304, C.R.S. - additions, subtractions, and the QIP basis direction",
        "citation": "§ 39-22-304(2), (3)(c), (3)(p), (3)(q), C.R.S. (CRS 2024)",
        "issuer": "Colorado General Assembly",
        "official_url": "https://leg.colorado.gov/agencies/office-legislative-legal-services/colorado-revised-statutes",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ W5 - the QIP basis direction, verbatim, and what it PROVES",
                "excerpt_text": (
                    "§ 39-22-304(3)(p)(III), C.R.S., verbatim: 'A taxpayer that applies the subtraction "
                    "allowed in this subsection (3)(p) with respect to qualified improvement property shall "
                    "calculate the gain or loss on a sale of such qualified improvement property for "
                    "purposes of the subtraction in subsection (3)(c) of this section USING THE BASIS "
                    "REPORTED ON THEIR FEDERAL INCOME TAX RETURN at the time of the sale.' ⭐ It does TWO "
                    "things: it DIRECTS federal basis for QIP - so 'federal basis governs' is a positive "
                    "statutory instruction, not an absence - and it expressly cross-references § 304(3)(c), "
                    "proving that subsection is LIVE LAW, legislated about in 2021, not archaeology. "
                    "⚠ The 'acquired prior to January 1, 1965' condition appears ONLY in the Department's "
                    "Guide; the statutory text of § 39-22-304(3)(c) was read in full from CRS 2024 and "
                    "carries NO date limitation of any kind."
                ),
                "summary_text": "⚠⚠ A class-(b) correction: 'we found no rule' had been masquerading as "
                                "'the rule says no'. Two prior readings of this brief were wrong.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ The write-in lines are NARROWER on the form than in the statute",
                "excerpt_text": (
                    "The DR 0112 line-7 instruction enumerates THREE additions (bond interest, foreign "
                    "taxes, gross conservation easement charitable contribution). § 39-22-304(2) enumerates "
                    "(a) through (k) and adds the CARES-Act-related add-back at (2)(i); the Guide Part 4 "
                    "adds unauthorized alien labor services (§ 39-22-529), clubs that restrict membership, "
                    "and the TY2022-only food-and-beverage add-back. The line-12 gap is LARGER: beyond the "
                    "form's three, § 39-22-304(3)(q) adds a subtraction that appears in NEITHER the form "
                    "NOR the Guide's Part 5 body - Subpart F income under IRC § 951(a) AND GILTI under "
                    "§ 951A(a) 'with respect to a controlled foreign corporation that is a C corporation "
                    "incorporated in a foreign jurisdiction for the purpose of tax avoidance pursuant to "
                    "section 39-22-303 (8)(b)(II)', GILTI net of the § 250(a)(1)(B) deduction."
                ),
                "summary_text": "⚠ § 304(3)(q) is the paired relief for a tax-haven CFC dragged into the "
                                "combined group - a live combined-return item with NO home on the printed "
                                "form. Build lines 7 and 12 off the STATUTORY lists, not the form's three.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_504_NOL", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "§ 39-22-504, C.R.S. - Colorado net operating losses for corporations",
        "citation": "§ 39-22-504(1)(b), (3), (4), (6), C.R.S. (CRS 2024)",
        "issuer": "Colorado General Assembly",
        "official_url": "https://leg.colorado.gov/agencies/office-legislative-legal-services/colorado-revised-statutes",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [{
            "excerpt_label": "⚠ The vintaged ledger, the CARES decoupling, and the rule the Guide omits",
            "excerpt_text": (
                "§ 39-22-504(3)(b), verbatim: 'Net operating losses of corporations generated in income tax "
                "years commencing on or after January 1, 2021, may be carried forward for TWENTY YEARS.' "
                "And: 'Net operating losses of corporations MAY NOT BE CARRIED BACK to an earlier tax "
                "year.' Vintages: pre-2018 = 20 years; 2018 through 2020 = UNLIMITED; 2021 onward = 20 "
                "years. ⚠ The post-2020 reversion is COLORADO-ONLY - federal post-2017 NOLs carry forward "
                "indefinitely. § 39-22-504(1)(b), verbatim: 'For losses incurred after December 31, 2017, "
                "the eighty percent limitation set forth in section 172 (a)(2) of the internal revenue code "
                "shall apply WITHOUT REGARD TO THE AMENDMENTS MADE IN SECTION 2303 of the March 2020 "
                "\"Coronavirus Aid, Relief, and Economic Security Act\"' - Colorado decoupled from CARES "
                "NOL relief. § 39-22-504(4), a FINANCIAL-INSTITUTION rule the Guide's table OMITS: losses "
                "for years beginning on/after 1984 and before 2021 carry forward FIFTEEN years, where "
                "'financial institution' means any institution to which IRC § 585 or § 593 applies - still "
                "live for 2006-2020 vintages on a TY2025 return. § 39-22-504(6): for 2011-2013 the maximum "
                "subtraction was $250,000, each capped year buys one extra carryforward year, and the "
                "suspended amount is grossed up at 'three and one-quarter percent per annum'."
            ),
            "summary_text": "⚠ The DR 0112 line-16 instruction admits its own limits, verbatim: 'The "
                            "following instructions account for the 80% limitation, BUT DO NOT ACCOUNT FOR "
                            "OTHER LIMITATIONS THAT MAY APPLY.' Three of the four limitations, the "
                            "twenty-year expiry, the financial-institution rule and the 2011-2013 gross-up "
                            "have NO representation on the form - they are ledger logic, not line logic.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "CO_CRS_39_22_606_EST", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "§ 39-22-606, C.R.S. - estimated tax and the penalty exception",
        "citation": "§ 39-22-606(6)(a)(I), C.R.S.", "issuer": "Colorado General Assembly",
        "official_url": "https://leg.colorado.gov/agencies/office-legislative-legal-services/colorado-revised-statutes",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ RULE 2 at statute level - and why the '3-2 split' was a category error",
            "excerpt_text": (
                "§ 39-22-606(6)(a)(I), C.R.S., verbatim: 'NO ADDITION TO TAX SHALL BE IMPOSED under "
                "subsection (3) of this section for any taxable year if the tax imposed under part 3 of "
                "this article shown on the return for such taxable year or, if no return is filed, the tax, "
                "is LESS THAN FIVE THOUSAND DOLLARS.' ⚠ The PTE brief recorded a live 3-2 source split "
                "between 'exceeds $5,000' and 'less than $5,000' sources. It is not a split: the three "
                "'exceeds' sources (DR 0112 p.1, DR 0112EP, Guide Part 9) describe RULE 1, the obligation "
                "to remit; the two 'less than' sources (Guide Part 9 closing sentence, DR 0205 Part 1) "
                "describe RULE 2, the penalty exception - and this statute settles Rule 2. Because "
                "§ 39-22-344(2) routes an electing PTE through § 39-22-606, the same statute governs the "
                "PTE penalty."
            ),
            "summary_text": "⚠⚠ Penalty exposure begins AT $5,000; the payment obligation begins ABOVE it. "
                            "At exactly $5,000 a taxpayer owes no estimates and has no exception. Encoding "
                            "one predicate for both is wrong at exactly one point - a round number.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "CO_HB24_1134_TY2026", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "CO",
        "title": "HB 24-1134 - the TY2026 combined-reporting replacement",
        "citation": "HB 24-1134 (2024); § 39-22-303.5, C.R.S.", "issuer": "Colorado General Assembly",
        "official_url": "https://leg.colorado.gov/bills/hb24-1134",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["co_ccorp_dr0112"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ TY2026 is a RE-AUTHORING event, and the cliff is FOUR changes",
            "excerpt_text": (
                "§ 39-22-303(11) is expressly limited to 'tax years beginning before January 1, 2026'. From "
                "TY2026 FOUR things change together: (1) the HB 24-1134 combined regime replaces the six "
                "tests of unity; (2) the listed-jurisdictions rule arrives; (3) the § 250 FDDEI add-back "
                "arrives; and (4) the $150,000 line-17 cap is REMOVED by § 39-22-304(3)(p)(II)(B), C.R.S. "
                "⚠ Also TY2026-ONLY: combined-group-as-taxpayer and joint-and-several liability - so the "
                "TY2025 group must NOT be modelled as an entity."
            ),
            "summary_text": "⚠⚠ Ratified at D-27 as a re-authoring event, not a rate bump. The fourth "
                            "change was added by the verification pass - a three-item cliff would have "
                            "left the line-17 cap silently in place.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple] = [
    ("CO_2025_DR0112", "CO_DR0112", "governs"),
    ("CO_2025_DR0112C", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_303_COMBINED", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_304_MODS", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_504_NOL", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_606_EST", "CO_DR0112", "governs"),
    ("CO_HB24_1134_TY2026", "CO_DR0112", "informs"),
    ("CO_CRS_39_22_301_RATE", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_608_DUE", "CO_DR0112", "governs"),
    ("CO_CORP_TAX_GUIDE_2026", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_103", "CO_DR0112", "governs"),
    ("CO_CRS_39_22_347_CREDIT", "CO_DR0112", "governs"),
    ("CO_2025_DR0106K", "CO_DR0112", "informs"),
    ("CO_ITT_SALT_PARITY_2025", "CO_DR0112", "informs"),
]

F_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "L1 Federal taxable income (1120 L30 or 990-T Part I L11)",
     "data_type": "decimal", "required": True, "sort_order": 1,
     "notes": "Both federal lines verified against the FINAL TY2025 IRS PDFs."},
    {"fact_key": "fti_of_companies_not_included", "label": "L2 Federal taxable income of companies not in this return",
     "data_type": "decimal", "required": False, "sort_order": 2,
     "notes": "⚠ The whole federal/Colorado group reconciliation compressed into ONE number, with NO "
              "supporting schedule - the Schedule C lists who is in the group but carries no dollars."},
    {"fact_key": "federal_nol_deduction", "label": "L4 Federal net operating loss deduction (add-back)",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "Structural, not optional: 1120 line 30 is already NET of line 29a."},
    {"fact_key": "colorado_income_tax_deducted", "label": "L5 Colorado income tax deduction (add-back)",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "meals_274k", "label": "L6 Business meals deducted pursuant to IRC § 274(k)",
     "data_type": "decimal", "required": False, "sort_order": 5},
    {"fact_key": "other_additions", "label": "L7 Other additions (categorised multi-instance write-in)",
     "data_type": "decimal", "required": False, "sort_order": 6,
     "notes": "⚠ W4: the picklist is the STATUTORY list (§ 39-22-304(2)(a)-(k) incl. the CARES add-back at "
              "(2)(i), plus § 39-22-529 unauthorized alien labor and restricted-membership clubs), NOT the "
              "form's three. Explanation required via Revenue Online E-Filer Attachment, DR 1778, or a "
              "written statement."},
    {"fact_key": "exempt_federal_interest", "label": "L9 Exempt federal interest",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "foreign_source_income_excluded", "label": "L10 Excludable foreign source income",
     "data_type": "decimal", "required": False, "sort_order": 8,
     "notes": "⚠ C5: direct-entry per § 39-22-303(10) and its rule, then AUTO-PROPAGATED to the Schedule "
              "RF denominator with a reconciliation assertion. Excluding it from income but not from the "
              "denominator overstates the Colorado fraction."},
    {"fact_key": "marijuana_280e_deduction", "label": "L11 Colorado Marijuana and Natural Medicine Business Deduction",
     "data_type": "decimal", "required": False, "sort_order": 9,
     "notes": "Requires pro forma federal schedules computed as if § 280E did not apply, the actual "
              "schedules, AND the MED/NMD license number."},
    {"fact_key": "other_subtractions", "label": "L12 Other subtractions (categorised multi-instance write-in)",
     "data_type": "decimal", "required": False, "sort_order": 10,
     "notes": "⚠ W4: the gap here is LARGER than line 7's. § 39-22-304(3)(q) - Subpart F and GILTI for a "
              "tax-haven CFC under § 303(8)(b)(II) - appears in NEITHER the form NOR the Guide's Part 5 "
              "body, and is a live combined-return item with no home on the printed form."},
    {"fact_key": "is_apportioning", "label": "L15 - apportioning? (else line 14 carries straight through)",
     "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "⚠ The default is FORMULARY apportionment, not direct sourcing - the PTE fork does NOT carry "
              "over. Apportioning takes line 14 of the DR 0112RF."},
    {"fact_key": "nol_pre2018", "label": "L16(a) Colorado NOLs from years beginning before 2018-01-01",
     "data_type": "decimal", "required": False, "sort_order": 12},
    {"fact_key": "nol_post2017", "label": "L16(c) Colorado NOLs from years beginning on/after 2018-01-01",
     "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "⚠ Subject to the 80% limitation, applied to line 16(b) - i.e. AFTER the pre-2018 losses."},
    {"fact_key": "is_financial_institution", "label": "Is the taxpayer an IRC § 585 / § 593 financial institution?",
     "data_type": "boolean", "required": False, "sort_order": 14,
     "notes": "⚠ § 39-22-504(4) gives 1984-2020 vintages a FIFTEEN-year carryforward - a rule the Guide's "
              "own table omits, and still live for 2006-2020 vintages on a TY2025 return."},
    {"fact_key": "hb21_1002_carryforward", "label": "L17 HB21-1002 CARES-Act carryforward subtraction",
     "data_type": "decimal", "required": False, "sort_order": 15,
     "notes": "⚠ Capped at $150,000 for TY2025; § 39-22-304(3)(p)(II)(B) REMOVES the cap for TY2026 - "
              "cliff item 4 of 4. The computation lives in the CDOR CARES Act Guidance, not on the form."},
    {"fact_key": "claims_pl86_272", "label": "Section A - claiming exemption under P.L. 86-272?",
     "data_type": "boolean", "required": False, "sort_order": 16,
     "notes": "⚠ Zeroes LINE 19, not line 18. The computed value is retained upstream."},
    {"fact_key": "deemed_commencement_year", "label": "⚠ W9 - the DEEMED commencement year (52-53 week trap)",
     "data_type": "integer", "required": False, "sort_order": 17,
     "notes": "⚠ The rate follows the deemed commencement date, not the calendar start. A "
              "DECEMBER-starting 52-53 week year is deemed to commence the FOLLOWING January 1 and takes "
              "that year's rate."},
    {"fact_key": "is_affiliated_group_member", "label": "§ 303(12) affiliated-group member? (triggers Schedule C)",
     "data_type": "boolean", "required": False, "sort_order": 18,
     "notes": "⚠⚠ Schedule C is triggered by § 303(12) MEMBERSHIP, not by the Section B box."},
    {"fact_key": "pct_property_payroll_outside_us", "label": "Property + payroll assigned outside the US (averaged)",
     "data_type": "decimal", "required": False, "sort_order": 19,
     "notes": "⚠ Averaged per § 24-60-1301. 80% OR MORE excludes the corporation (§ 303(8)(a)). ⚠ 'United "
              "States' is restricted to the fifty states and DC - territories are OUTSIDE it."},
    {"fact_key": "unity_tests_met_all_three_years", "label": "Count of the six unity tests met in ALL THREE years",
     "data_type": "integer", "required": False, "sort_order": 20,
     "notes": "⚠ 'the current AND TWO PRECEDING tax years' - a single-year test over-includes. ⚠ The six "
              "answers are DIRECT-ENTRY (C2); the ≥3-of-6 arithmetic and the row structure are computed."},
    {"fact_key": "combined_election_year", "label": "Combined/consolidated election year (client record)",
     "data_type": "integer", "required": False, "sort_order": 21,
     "notes": "⚠ C2: the election year lives on the CLIENT RECORD, not on the return."},
    {"fact_key": "net_tax_liability", "label": "Net Colorado tax liability, for the two $5,000 predicates",
     "data_type": "decimal", "required": False, "sort_order": 22,
     "notes": "⚠⚠ TWO predicates: the obligation to remit (> $5,000) and the penalty exception "
              "(< $5,000). Different rules, different operators, same number."},
    {"fact_key": "salt_parity_credit", "label": "L34 SALT Parity owner credit (DR 0106K lines 16 and 25)",
     "data_type": "decimal", "required": False, "sort_order": 23,
     "notes": "⚠ W6: multi-instance DR 0106K intake with a unitary-overlap diagnostic."},
    {"fact_key": "amended_box_h_date", "label": "Box H - the amended-return 180-day trigger date",
     "data_type": "string", "required": False, "sort_order": 24,
     "notes": "⚠ W12: DR 0112X itself is RED-deferred, but the Box-H 180-day trigger IS built."},
]

F_RULES: list[dict] = [
    {"rule_id": "R-CO0112-SPINE", "title": "L3/L8/L13/L14 - the modification spine",
     "rule_type": "calculation",
     "formula": "L3 = L1 - L2 ; L8 = L3 + L4 + L5 + L6 + L7 ; L13 = L9 + L10 + L11 + L12 ; L14 = L8 - L13",
     "inputs": ["federal_taxable_income", "fti_of_companies_not_included", "federal_nol_deduction",
                "colorado_income_tax_deducted", "meals_274k", "other_additions",
                "exempt_federal_interest", "foreign_source_income_excluded",
                "marijuana_280e_deduction", "other_subtractions"],
     "outputs": ["L3", "L8", "L13", "L14"], "sort_order": 1,
     "description": "L1 is federal 1120 line 30 (or 990-T Part I line 11), verified against the FINAL "
                    "TY2025 IRS forms. ⚠ The line-4 federal NOL add-back is STRUCTURAL, not optional: "
                    "1120 line 30 is already net of line 29a, so omitting the add-back double-counts the "
                    "federal loss. ⚠ Lines 7 and 12 are categorised multi-instance write-ins built off the "
                    "STATUTORY lists, not the form's three enumerated items each - the line-12 gap in "
                    "particular hides § 39-22-304(3)(q), which appears in neither the form nor the Guide."},
    {"rule_id": "R-CO0112-NOL", "title": "⚠ L16(a)-(d) over a VINTAGED ledger, 80% applied to 16(b)",
     "rule_type": "calculation",
     "formula": "16a = min(pre2018, L15) ; 16b = L15 - 16a ; 16c = min(post2017, 16b * 0.80) ; 16d = 16a + 16c",
     "inputs": ["nol_pre2018", "nol_post2017"], "outputs": ["L16a", "L16b", "L16c", "L16d"], "sort_order": 2,
     "description": "⚠ C3. The 80% limitation applies to Colorado taxable income AFTER deducting pre-2018 "
                    "losses - which is exactly why line 16(b) exists as a printed line. Applying 80% to "
                    "line 15 instead over-limits every return carrying pre-2018 vintages. ⚠ The vintages "
                    "are Colorado-only: pre-2018 = 20 years, 2018-2020 = UNLIMITED, 2021 onward = 20 years, "
                    "against federal indefinite carryforward for everything post-2017. No carryback in any "
                    "year. § 39-22-504(4) gives IRC § 585/§ 593 financial institutions FIFTEEN years for "
                    "1984-2020 vintages - a rule the Guide's table omits. ⚠ The form's own line-16 "
                    "instruction says it 'do[es] not account for other limitations that may apply'; "
                    "§ 382, § 860E, SRLY and the 2011-2013 gross-up are RED-deferred ledger logic."},
    {"rule_id": "R-CO0112-L17", "title": "L17 HB21-1002 carryforward - capped at $150,000 for TY2025 only",
     "rule_type": "limitation", "formula": "L17 = min(claimed, 150000) for TY2025; uncapped from TY2026",
     "inputs": ["hb21_1002_carryforward"], "outputs": ["L17"], "sort_order": 3,
     "description": "⚠⚠ The cap is REMOVED for TY2026 by § 39-22-304(3)(p)(II)(B), C.R.S. - the FOURTH "
                    "item on the TY2026 cliff, added by the verification pass. A three-item cliff would "
                    "have left this cap silently in place on TY2026 returns."},
    {"rule_id": "R-CO0112-TAX", "title": "⚠ L19 Tax at 4.4% - the year from the DEEMED commencement date",
     "rule_type": "calculation", "formula": "L18 = L15 - (L16d + L17) ; L19 = L18 * rate(deemed_year)",
     "inputs": ["deemed_commencement_year"], "outputs": ["L18", "L19"], "sort_order": 4,
     "description": "§ 39-22-301(1)(d)(I)(K), C.R.S.: 'Except as otherwise provided in section 39-22-627, "
                    "for income tax years commencing on or after January 1, 2022, FOUR AND FORTY "
                    "ONE-HUNDREDTHS PERCENT of the Colorado net income' - and the imposing sentence reaches "
                    "'each domestic C corporation, foreign C corporation, AND COMBINED GROUP'. ⚠ § 39-22-627 "
                    "(TABOR) is named INSIDE the rate statute, so the override is first-class, not "
                    "external; TY2024's 4.25% came from a one-off directive at § 39-22-627(1)(c) naming "
                    "TY2024 only. ⚠ W9: a DECEMBER-starting 52-53 week year is deemed to commence the "
                    "FOLLOWING January 1 and takes that year's rate. ⚠ No corporate AMT - § 39-22-105 "
                    "reaches only individuals, estates and trusts."},
    {"rule_id": "R-CO0112-PL86272", "title": "⚠ P.L. 86-272 zeroes LINE 19, never line 18",
     "rule_type": "calculation", "formula": "L19 = 0 if claims_pl86_272 else computed_tax",
     "inputs": ["claims_pl86_272"], "outputs": ["L19"], "sort_order": 5,
     "description": "Section A instruction, verbatim: 'must complete the return and applicable schedules, "
                    "but ENTER $0 TAX ON LINE 19.' A post-computation override with the computed value "
                    "retained upstream. ⚠ Zeroing line 18 instead would corrupt the NOL ledger and the "
                    "apportionment reconciliation while looking IDENTICAL on the printed return. ⚠ The DR "
                    "0106 carries the same rule at a DIFFERENT line number - the campaign's standing "
                    "convention (never clone a sibling form's line numbers, even within one state) applies."},
    {"rule_id": "R-CO0112-COMBINED", "title": "⚠⚠ Combined inclusion - three conditions, built from STATUTE",
     "rule_type": "eligibility",
     "formula": "include iff affiliated_group_member AND pct_outside_us < 0.80 AND unity_tests_met >= 3 "
                "(current and two preceding years)",
     "inputs": ["is_affiliated_group_member", "pct_property_payroll_outside_us",
                "unity_tests_met_all_three_years"],
     "outputs": ["COMBINED_INCLUDE"], "sort_order": 6,
     "description": "⚠⚠ C2. The six tests diverge THREE ways - statute, Guide, DR 0112C - and in BOTH "
                    "directions, so no single text is a safe default. D-27 ruled: BUILD THE STATUTE, "
                    "PROMPT WITH THE FORM, DIAGNOSE THE GUIDE. ⚠ Condition 2 mirrors the statutory "
                    "EXCLUSION at § 303(8)(a) (80% OR MORE excludes), so inclusion needs strictly less than "
                    "80%; and 'United States' is restricted to the fifty states and DC, so territories are "
                    "outside it. ⚠ The unity count must hold for the CURRENT AND TWO PRECEDING years. "
                    "⚠ The partnership look-through covers tests 1-4 ONLY. ⚠ Schedule C is triggered by "
                    "§ 303(12) membership, NOT by the Section B box. ⚠⚠ Combined-group-as-taxpayer and "
                    "joint-and-several liability are TY2026-ONLY - do not model the TY2025 group as an "
                    "entity."},
    {"rule_id": "R-CO0112-EST", "title": "⚠⚠ TWO $5,000 predicates - obligation vs penalty exception",
     "rule_type": "eligibility",
     "formula": "must_remit iff net_tax > 5000 ; penalty_exception iff tax_shown < 5000",
     "inputs": ["net_tax_liability"], "outputs": ["MUST_REMIT", "PENALTY_EXCEPTION"], "sort_order": 7,
     "description": "⚠⚠ Campaign D-18 / D-12 B2 as corrected. The apparent 3-2 source split was a CATEGORY "
                    "ERROR: the three 'exceeds' sources describe the OBLIGATION, the two 'less than' "
                    "sources describe the PENALTY EXCEPTION, and § 39-22-606(6)(a)(I) settles the latter at "
                    "statute level. So penalty exposure begins AT $5,000 while the obligation begins ABOVE "
                    "it - at exactly $5,000 a taxpayer owes no estimates and has no exception. A single "
                    "predicate is wrong at exactly one point, and that point is a round number taxpayers "
                    "land on."},
    {"rule_id": "R-CO0112-DUE", "title": "The fifteenth day of the FIFTH month, and no payment extension",
     "rule_type": "deadline", "formula": "due = 15th day of the 5th month after year end; extension = +6 months, FILING ONLY",
     "inputs": [], "outputs": ["DUE_DATE"], "sort_order": 8,
     "description": "§ 39-22-608(2)(b), C.R.S., enacted by HB 23-1277 (eff. 2023-08-07), is an EXCEPTION "
                    "carved out of (2)(a)'s general fourth-month rule and applies 'for taxable years "
                    "beginning on and after January 1, 2024'. May 15 for calendar-year filers, extended to "
                    "November 15. ⚠ 'While there is an extension to file, THERE IS NOT AN EXTENSION TO THE "
                    "PAYMENT DUE DATE' - use DR 0158-C. Weekend/holiday rolls to the next business day."},
    {"rule_id": "R-CO0112-DEPR", "title": "⚠⚠ W5 - federal basis governs, as an AFFIRMATIVE ruling",
     "rule_type": "calculation", "formula": "no Colorado depreciation modification; no Colorado basis ledger",
     "inputs": [], "outputs": ["DEPRECIATION"], "sort_order": 9,
     "description": "⚠⚠ A class-(b) correction - 'we found no rule' masquerading as 'the rule says no'. "
                    "§ 39-22-304(3)(p)(III), C.R.S. DIRECTS the use of the federal basis for qualified "
                    "improvement property, so 'federal basis governs' is a POSITIVE statutory instruction; "
                    "and it cross-references § 304(3)(c), proving that subsection is LIVE LAW legislated "
                    "about in 2021, not archaeology. ⚠ The 'acquired prior to January 1, 1965' condition is "
                    "a GUIDE GLOSS - the statutory text of § 39-22-304(3)(c) carries NO date limitation of "
                    "any kind, and two prior readings of this brief said otherwise."},
]

F_RULE_LINKS: list[tuple] = [
    ("R-CO0112-SPINE", "CO_2025_DR0112", "governs", "The printed lines 1-14."),
    ("R-CO0112-SPINE", "CO_CRS_39_22_304_MODS", "governs", "⚠ The STATUTORY modification lists behind the "
     "line-7 and line-12 write-ins, which are broader than the form's three items each."),
    ("R-CO0112-NOL", "CO_CRS_39_22_504_NOL", "governs", "The vintaged carryforward periods, the CARES "
     "decoupling, the financial-institution rule and the no-carryback rule."),
    ("R-CO0112-NOL", "CO_CORP_TAX_GUIDE_2026", "informs", "⚠ Guide Part 8's table OMITS the "
     "financial-institution rule - recorded as informing, not governing."),
    ("R-CO0112-L17", "CO_CRS_39_22_304_MODS", "governs", "§ 39-22-304(3)(p)(II)(B) removes the $150,000 "
     "cap for TY2026 - cliff item 4 of 4."),
    ("R-CO0112-TAX", "CO_CRS_39_22_301_RATE", "governs", "⚠ The primary rate authority on the C-corp side, "
     "not a cross-reference as it was for the PTE. It names § 39-22-627 inside itself."),
    ("R-CO0112-TAX", "CO_CORP_TAX_GUIDE_2026", "governs", "⚠ W9 - Parts 3 and 10 supply the 52-53 week "
     "deeming rule that selects the rate year."),
    ("R-CO0112-PL86272", "CO_2025_DR0112", "governs", "Section A: 'enter $0 tax on line 19'."),
    ("R-CO0112-COMBINED", "CO_CRS_39_22_303_COMBINED", "governs", "⚠⚠ The STATUTE is what is built - the "
     "six tests diverge three ways and in both directions."),
    ("R-CO0112-COMBINED", "CO_2025_DR0112C", "informs", "⚠ The form's wording is what the preparer is "
     "PROMPTED with; it is broader on test 1 and narrowest on test 2."),
    ("R-CO0112-COMBINED", "CO_CORP_TAX_GUIDE_2026", "informs", "⚠ The Guide's divergences are DIAGNOSED, "
     "not built - it is bidirectional at tests 4 and 5 where the statute is not."),
    ("R-CO0112-COMBINED", "CO_HB24_1134_TY2026", "informs", "⚠⚠ The whole regime sunsets for tax years "
     "beginning on or after 2026-01-01."),
    ("R-CO0112-EST", "CO_CRS_39_22_606_EST", "governs", "⚠⚠ § 39-22-606(6)(a)(I) settles the PENALTY "
     "exception at statute level: 'less than five thousand dollars'."),
    ("R-CO0112-EST", "CO_2025_DR0112", "governs", "The form states the OBLIGATION: 'greater than $5,000'."),
    ("R-CO0112-DUE", "CO_CRS_39_22_608_DUE", "governs", "(2)(b) IS the C-corp fifth-month rule, an "
     "exception to (2)(a)'s general fourth-month rule."),
    ("R-CO0112-DEPR", "CO_CRS_39_22_304_MODS", "governs", "⚠⚠ § 39-22-304(3)(p)(III) - the QIP federal-basis "
     "DIRECTION, which makes this an affirmative ruling rather than an absence."),
    ("R-CO0112-DEPR", "CO_CRS_39_22_103", "governs", "Rolling conformity and the Title 39 depreciation "
     "negative, already established for Colorado."),
]

F_LINES: list[dict] = [
    {"line_number": "CO0112-3", "description": "L3 Net federal taxable income (L1 - L2)",
     "line_type": "subtotal", "source_rules": ["R-CO0112-SPINE"], "sort_order": 1},
    {"line_number": "CO0112-8", "description": "L8 Sum of lines 3 through 7 (additions)",
     "line_type": "subtotal", "source_rules": ["R-CO0112-SPINE"], "sort_order": 2},
    {"line_number": "CO0112-13", "description": "L13 Sum of lines 9 through 12 (subtractions)",
     "line_type": "subtotal", "source_rules": ["R-CO0112-SPINE"], "sort_order": 3},
    {"line_number": "CO0112-14", "description": "L14 Modified federal taxable income - the DR 0112RF L1 feed",
     "line_type": "subtotal", "source_rules": ["R-CO0112-SPINE"], "sort_order": 4},
    {"line_number": "CO0112-15", "description": "L15 Colorado taxable income before the NOL deduction",
     "line_type": "calculated", "source_rules": ["R-CO0112-SPINE"], "sort_order": 5},
    {"line_number": "CO0112-16A", "description": "L16(a) Pre-2018 Colorado NOLs",
     "line_type": "calculated", "source_rules": ["R-CO0112-NOL"], "sort_order": 6},
    {"line_number": "CO0112-16B", "description": "L16(b) L15 less 16(a) - the 80% base",
     "line_type": "calculated", "source_rules": ["R-CO0112-NOL"], "sort_order": 7},
    {"line_number": "CO0112-16C", "description": "L16(c) Post-2017 Colorado NOLs, limited to 80% of 16(b)",
     "line_type": "calculated", "source_rules": ["R-CO0112-NOL"], "sort_order": 8},
    {"line_number": "CO0112-16D", "description": "L16(d) Colorado NOL deduction, sum of (a) and (c)",
     "line_type": "subtotal", "source_rules": ["R-CO0112-NOL"], "sort_order": 9},
    {"line_number": "CO0112-17", "description": "L17 HB21-1002 carryforward - $150,000 cap, TY2025 only",
     "line_type": "calculated", "source_rules": ["R-CO0112-L17"], "sort_order": 10},
    {"line_number": "CO0112-18", "description": "L18 Colorado taxable income (L15 - (L16d + L17))",
     "line_type": "subtotal", "source_rules": ["R-CO0112-TAX"], "sort_order": 11},
    {"line_number": "CO0112-19", "description": "L19 Tax at 4.4% - ⚠ zeroed by P.L. 86-272, line 18 is not",
     "line_type": "calculated", "source_rules": ["R-CO0112-TAX", "R-CO0112-PL86272"], "sort_order": 12},
    {"line_number": "CO0112-34", "description": "L34 SALT Parity owner credit (multi-instance DR 0106K)",
     "line_type": "calculated", "source_rules": ["R-CO0112-SPINE"], "sort_order": 13},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_CO0112_TY2026_REAUTHOR", "severity": "error",
     "title": "⚠⚠ TY2026 replaces four rules at once - this spec is TY2025 only",
     "condition": "tax_year >= 2026",
     "message": "This spec encodes the TY2025 Colorado regime and must NOT be rolled forward. § 39-22-303(11) "
                "opens 'For tax years beginning before January 1, 2026', and FOUR things change together "
                "from TY2026: (1) the HB 24-1134 combined regime replaces the six tests of unity; (2) the "
                "listed-jurisdictions rule arrives; (3) the § 250 FDDEI add-back arrives; and (4) the "
                "$150,000 line-17 cap is removed by § 39-22-304(3)(p)(II)(B), C.R.S. ⚠ Also TY2026-only: "
                "combined-group-as-taxpayer and joint-and-several liability. Campaign D-27 ratified TY2026 "
                "as a RE-AUTHORING event, not a rate bump - every dependent rule is stale until re-verified.",
     "notes": "⚠⚠ The fourth change was added by the verification pass. A three-item cliff would have left "
              "the line-17 cap silently in place on TY2026 returns."},
    {"diagnostic_id": "D_CO0112_UNITY_TEST_WORDING", "severity": "warning",
     "title": "⚠⚠ The six unity tests are worded three different ways - answer the STATUTE",
     "condition": "is_affiliated_group_member == True",
     "message": "The six tests of unity are worded differently by § 39-22-303(11)(a), by the Corporate "
                "Income Tax Guide, and on the DR 0112C face - and the differences run in BOTH directions, "
                "so no single text is a safe default. Test 1: the form says 'gross receipts' where statute "
                "and Guide say 'gross OPERATING receipts' - the form is BROADER. Test 2: the form adds 'the "
                "total annual value of EACH OF' - the NARROWEST of the three. Test 3: the Guide drops 'or "
                "more'. Tests 4 and 5: the statute is one-directional, the Guide is bidirectional, and on "
                "test 4 the form also drops 'substantially'. Delvio computes the ≥3-of-6 arithmetic from "
                "the STATUTORY formulation; the prompts you see are the form's wording. Where your answer "
                "would differ between the two, follow the statute and note it.",
     "notes": "⚠⚠ C2 - 'build the statute, prompt with the form, diagnose the Guide' is the ruling, and "
              "this diagnostic is the 'diagnose' half."},
    {"diagnostic_id": "D_CO0112_UNITY_LOOKBACK", "severity": "error",
     "title": "⚠ The unity tests must hold for the current AND TWO PRECEDING years",
     "condition": "is_affiliated_group_member == True and unity_lookback_years_supplied < 3",
     "message": "Combined inclusion requires at least three of the six tests of unity to be satisfied 'for "
                "the CURRENT AND TWO PRECEDING tax years' (§ 39-22-303(11); Guide Part 2). Answers for all "
                "three years are required. ⚠ Testing the current year alone OVER-INCLUDES: a group that "
                "became unitary this year is not brought in by that fact alone, and including it changes "
                "every member's apportionment.",
     "notes": "The lookback is the part most easily dropped, and dropping it fails toward inclusion."},
    {"diagnostic_id": "D_CO0112_US_DEFINITION", "severity": "warning",
     "title": "⚠ 'United States' here means the fifty states and DC only",
     "condition": "pct_property_payroll_outside_us != 0",
     "message": "The 80% foreign property-and-payroll exclusion turns on § 39-22-303(8)(a), which states: "
                "'For the purpose of this subsection (8), \"United States\" is RESTRICTED TO THE FIFTY "
                "STATES AND THE DISTRICT OF COLUMBIA.' ⚠ Puerto Rico, Guam, the U.S. Virgin Islands and "
                "the other territories are OUTSIDE the United States for this test - property and payroll "
                "there count toward the 80%. Property and payroll are averaged per § 24-60-1301, C.R.S.",
     "notes": "A definition that reads as boilerplate and is not."},
    {"diagnostic_id": "D_CO0112_COMBINED_NOT_AN_ENTITY", "severity": "warning",
     "title": "⚠⚠ For TY2025 the combined group is NOT a taxpayer",
     "condition": "is_affiliated_group_member == True",
     "message": "Combined-group-as-taxpayer and joint-and-several liability arrive with HB 24-1134 and are "
                "TY2026-ONLY. For TY2025 the group must not be modelled as an entity - the members remain "
                "the taxpayers. ⚠ Tax-haven inclusion (§ 39-22-303(8)(b)) and § 1502 consolidated-return "
                "elimination are RED-DEFERRED in this version (campaign D-27, C2), and the six unity "
                "answers are DIRECT-ENTRY: Delvio computes the Schedule C row structure and the ≥3-of-6 "
                "arithmetic, not the answers themselves.",
     "notes": "⚠ C2. Modelling the group as an entity a year early would change who is liable."},
    {"diagnostic_id": "D_CO0112_SCHEDULE_C_TRIGGER", "severity": "warning",
     "title": "⚠ Schedule C is triggered by § 303(12) membership, not by the Section B box",
     "condition": "is_affiliated_group_member == True",
     "message": "The Colorado Affiliations Schedule (DR 0112C) is required because the corporation is a "
                "member of an affiliated group as defined in § 39-22-303(12), C.R.S. ⚠ It is NOT triggered "
                "by the Section B checkbox - a return that leaves Section B unticked can still require "
                "Schedule C, and relying on the box will omit it. ⚠ Note also that Schedule C lists WHO is "
                "in the group but carries NO dollar amounts: the entire federal-to-Colorado group "
                "reconciliation is compressed into line 2, unsupported.",
     "notes": "⚠ C2 - a trigger that looks like it lives on the form and does not."},
    {"diagnostic_id": "D_CO0112_PARTNERSHIP_LOOKTHROUGH", "severity": "info",
     "title": "The partnership look-through reaches tests 1-4 only",
     "condition": "is_affiliated_group_member == True",
     "message": "Where a partnership sits between affiliates, the look-through applies to unity tests 1 "
                "through 4 only. Tests 5 (Board of Directors) and 6 (Officers) are answered at the "
                "corporate level without look-through.",
     "notes": "⚠ C2 - carried explicitly because a uniform look-through is the natural wrong assumption."},
    {"diagnostic_id": "D_CO0112_NOL_LIMITS_DEFERRED", "severity": "warning",
     "title": "⚠ Three NOL limitations and two vintage rules have no home on the form",
     "condition": "nol_pre2018 != 0 or nol_post2017 != 0",
     "message": "The DR 0112 line-16 instruction says so itself: 'The following instructions account for "
                "the 80% limitation, BUT DO NOT ACCOUNT FOR OTHER LIMITATIONS THAT MAY APPLY.' Delvio "
                "computes lines 16(a)-(d) and the 80% limitation over a vintaged ledger. RED-DEFERRED "
                "(campaign D-27, C3): the § 382 ownership-change limitation, the § 860E REMIC "
                "excess-inclusion limitation, the SRLY limitation, and the 2011-2013 suspension gross-up "
                "at § 39-22-504(6) (which grosses up at 3.25% per annum and buys one extra carryforward "
                "year per capped year). ⚠ Also verify the twenty-year expiry by vintage yourself: Colorado "
                "reverts to 20 years for 2021-onward losses where federal law is indefinite.",
     "notes": "C3 - the deferred items are precisely those needing facts from outside the return."},
    {"diagnostic_id": "D_CO0112_NOL_FINANCIAL_INSTITUTION", "severity": "warning",
     "title": "⚠ A financial institution's 1984-2020 losses carry forward FIFTEEN years",
     "condition": "is_financial_institution == True and (nol_pre2018 != 0 or nol_post2017 != 0)",
     "message": "§ 39-22-504(4), C.R.S. gives an IRC § 585 or § 593 financial institution a FIFTEEN-year "
                "carryforward for losses in years beginning on or after January 1, 1984 and before January "
                "1, 2021 - shorter than the twenty years the general rule allows, and shorter than the "
                "unlimited period the 2018-2020 vintages otherwise get. ⚠ The Corporate Income Tax Guide's "
                "carryforward table OMITS this rule entirely, so a preparer working from the Guide will "
                "over-state the available carryforward. Still live for 2006-2020 vintages on a TY2025 "
                "return.",
     "notes": "A statute-over-Guide item found by reading the statute rather than the table."},
    {"diagnostic_id": "D_CO0112_RATE_52_53_WEEK", "severity": "warning",
     "title": "⚠ A 52-53 week year takes the rate of its DEEMED commencement date",
     "condition": "deemed_commencement_year != tax_year",
     "message": "Guide Part 10: 'the tax year is deemed to have commenced on the first day of the calendar "
                "month beginning nearest to the first day of the 52-53 week year.' Guide Part 3: 'In the "
                "case of a 52-53 week tax year that actually begins in December, but is deemed to have "
                "commenced January 1 of the following year for Colorado income tax purposes, THE TAX RATE "
                "IS DETERMINED BASED ON THE JANUARY 1 DATE ON WHICH THE TAX YEAR IS DEEMED TO BEGIN.' ⚠ So "
                "a December-starting 52-53 week year takes the FOLLOWING year's rate. Colorado's rate has "
                "moved once already (TY2024's 4.25% under a one-off § 39-22-627(1)(c) directive), so this "
                "is a live rate-selection question, not a formality.",
     "notes": "⚠ W9 - the rate year is driven from the deemed date, never the calendar start."},
    {"diagnostic_id": "D_CO0112_PL86272_LINE19", "severity": "info",
     "title": "P.L. 86-272 zeroes line 19 - line 18 keeps the computed income",
     "condition": "claims_pl86_272 == True",
     "message": "Section A instruction: 'A taxpayer filing a return claiming exemption from Colorado "
                "taxation under P.L. 86-272 must complete the return and applicable schedules, but enter "
                "$0 tax on line 19.' Delvio retains the computed Colorado taxable income on line 18 and "
                "overrides only line 19. ⚠ Zeroing line 18 instead would corrupt the NOL ledger and the "
                "apportionment reconciliation - and the printed return would look identical either way.",
     "notes": "⚠ The DR 0106 carries the same rule at a different line number."},
    {"diagnostic_id": "D_CO0112_EST_TWO_PREDICATES", "severity": "warning",
     "title": "⚠⚠ At exactly $5,000 you owe no estimates AND have no penalty exception",
     "condition": "net_tax_liability == 5000",
     "message": "Colorado's two $5,000 rules use different comparisons and they are different rules, not "
                "conflicting sources. The OBLIGATION to remit estimated payments arises only if liability "
                "is GREATER THAN $5,000 (DR 0112 p.1, DR 0112EP, Guide Part 9 - unanimous). The PENALTY "
                "EXCEPTION applies only if the tax shown is LESS THAN $5,000 (§ 39-22-606(6)(a)(I), "
                "C.R.S. - statute). ⚠ At exactly $5,000 both fail: no obligation arose, and no exception "
                "protects you. Review whether estimated payments should have been made anyway.",
     "notes": "⚠⚠ Campaign D-18 corrected D-12 B2: the apparent 3-2 source split was a category error. A "
              "single predicate is wrong at exactly one point - and it is a round number."},
    {"diagnostic_id": "D_CO0112_NO_PAYMENT_EXTENSION", "severity": "warning",
     "title": "⚠ The six-month extension is to FILE, never to PAY",
     "condition": "True",
     "message": "Colorado C corporation returns are due the fifteenth day of the FIFTH month after year end "
                "(§ 39-22-608(2)(b), C.R.S., enacted by HB 23-1277 - an exception to (2)(a)'s general "
                "fourth-month rule) - May 15 for calendar-year filers. All C corporations get an automatic "
                "six-month extension to November 15. ⚠ 'While there is an extension to file, THERE IS NOT "
                "AN EXTENSION TO THE PAYMENT DUE DATE.' Use DR 0158-C to pay by May 15. A weekend or legal "
                "holiday rolls to the next business day.",
     "notes": "⚠ The fifth-month rule is Colorado-specific and recent; a fourth-month assumption is a "
              "month early and would look like an on-time filing."},
    {"diagnostic_id": "D_CO0112_WRITEIN_STATUTORY_LIST", "severity": "info",
     "title": "⚠ Lines 7 and 12 are built off the STATUTORY lists, not the form's three items",
     "condition": "other_additions != 0 or other_subtractions != 0",
     "message": "The DR 0112 enumerates three additions on line 7 and three subtractions on line 12. Both "
                "lists are incomplete. § 39-22-304(2) enumerates (a) through (k) plus the CARES add-back at "
                "(2)(i); the Guide adds unauthorized alien labor services (§ 39-22-529) and "
                "restricted-membership clubs. On the subtraction side the gap is larger: § 39-22-304(3)(q) "
                "provides a subtraction for Subpart F income and GILTI from a tax-haven CFC under "
                "§ 39-22-303(8)(b)(II) that appears in NEITHER the form NOR the Guide's Part 5 body - a "
                "live combined-return item with no home on the printed form. Delvio's picklists follow the "
                "statute.",
     "notes": "⚠ W4 - a spec that follows the form's enumeration silently drops real modifications."},
    {"diagnostic_id": "D_CO0112_FOREIGN_SOURCE_RF", "severity": "warning",
     "title": "⚠ Excluded foreign source income must also leave the apportionment denominator",
     "condition": "foreign_source_income_excluded != 0",
     "message": "Line 10 excludes foreign source income under § 39-22-303(10), C.R.S. and its rule. Delvio "
                "propagates the same amount to the Schedule RF (DR 0112RF) denominator and reconciles the "
                "two. ⚠ Excluding income from the base while leaving it in the denominator overstates the "
                "Colorado fraction and therefore the tax - and the return still foots.",
     "notes": "⚠ C5 - direct-entry at line 10 with auto-propagation and a reconciliation assertion."},
    {"diagnostic_id": "D_CO0112_AMENDED_DEFERRED", "severity": "error",
     "title": "⚠ DR 0112X amended returns are not supported - but the 180-day trigger is built",
     "condition": "amended_box_h_date not in ('', None)",
     "message": "Colorado amended C corporation returns are filed on the DR 0112X, which is RED-DEFERRED in "
                "this version (campaign D-27, W12). The Box-H 180-day trigger IS built and is what raised "
                "this message: a federal change generally requires a Colorado amended return within 180 "
                "days. Prepare the DR 0112X outside Delvio and do not miss the window.",
     "notes": "W12 - defer the form, build the deadline, because the deadline is the part that expires."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "CO0112-A - the spine and the 4.4% rate", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"federal_taxable_income": 2000000, "fti_of_companies_not_included": 0,
                "federal_nol_deduction": 0, "colorado_income_tax_deducted": 50000,
                "meals_274k": 0, "other_additions": 0, "exempt_federal_interest": 100000,
                "is_apportioning": False},
     "expected_outputs": {"CO0112-14": 1950000, "CO0112-18": 1950000, "CO0112-19": 85800.0},
     "notes": "2,000,000 + 50,000 - 100,000 = 1,950,000 x 4.4% = 85,800."},
    {"scenario_name": "CO0112-B - ⚠ the 80% NOL limit applies to 16(b), not to line 15",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"line15": 1000000, "nol_pre2018": 400000, "nol_post2017": 900000},
     "expected_outputs": {"CO0112-16A": 400000, "CO0112-16B": 600000,
                          "CO0112-16C": 480000, "CO0112-16D": 880000},
     "notes": "⚠ 16(b) = 1,000,000 - 400,000 = 600,000; 80% of THAT is 480,000. Applying 80% to line 15 "
              "instead would cap 16(c) at 800,000 and give a 16(d) of 1,200,000 - MORE than line 15 - so "
              "the wrong base is not merely different, it is impossible. That is why 16(b) is printed."},
    {"scenario_name": "CO0112-C - ⚠ P.L. 86-272 zeroes line 19 and LEAVES line 18 standing",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"colorado_taxable_income": 1950000, "claims_pl86_272": True},
     "expected_outputs": {"CO0112-18": 1950000, "CO0112-19": 0.0},
     "notes": "⚠ The computed tax (85,800) is overridden to zero at line 19 only. Zeroing line 18 would "
              "give the same printed tax while corrupting the NOL ledger and the apportionment "
              "reconciliation - the two errors are indistinguishable on the filed return."},
    {"scenario_name": "CO0112-D - ⚠⚠ the two $5,000 predicates disagree at exactly $5,000",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"net_tax_liability": 5000},
     "expected_outputs": {"must_remit_estimates": False, "penalty_exception_applies": False},
     "notes": "⚠⚠ THE POINT OF D-18. The obligation needs tax GREATER THAN 5,000 - it is not. The penalty "
              "exception needs tax LESS THAN 5,000 - it is not. So at exactly 5,000 the taxpayer owed no "
              "estimates and is still exposed to the penalty. A single shared predicate is wrong at "
              "exactly this point, and it is a round number taxpayers land on."},
    {"scenario_name": "CO0112-E - the obligation and the exception at 5,001 and 4,999",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"above": 5001, "below": 4999},
     "expected_outputs": {"must_remit_at_5001": True, "penalty_exception_at_4999": True},
     "notes": "Either side of the boundary the two rules behave normally; only the exact $5,000 point "
              "separates them. That is why both constants are kept, with different operators."},
    {"scenario_name": "CO0112-F - ⚠ W9: a December 52-53 week year takes the FOLLOWING year's rate",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"calendar_start_year": 2023, "deemed_commencement_year": 2024},
     "expected_outputs": {"rate_used": 0.0425, "rate_if_calendar_start_used": 0.044},
     "notes": "⚠ A year starting late December 2023 is deemed to commence 1 January 2024 and takes "
              "TY2024's 4.25% - not TY2023's 4.4%. On 2,000,000 of Colorado taxable income that is a "
              "3,000 difference, and the wrong rate looks entirely plausible on the printed return."},
    {"scenario_name": "CO0112-G - combined inclusion needs all THREE conditions",
     "scenario_type": "edge", "sort_order": 7,
     "inputs": {"is_affiliated_group_member": True, "pct_property_payroll_outside_us": 0.80,
                "unity_tests_met_all_three_years": 6},
     "expected_outputs": {"combined_include": False},
     "notes": "⚠ Six of six unity tests met, and the corporation is STILL excluded: § 39-22-303(8)(a) "
              "excludes at 80% OR MORE outside the US, so inclusion needs strictly less. At 79.99% the "
              "same corporation comes in. ⚠ And 'United States' is the fifty states and DC only - "
              "territories count toward the 80%."},
    {"scenario_name": "CO0112-H - two of six unity tests is not enough",
     "scenario_type": "edge", "sort_order": 8,
     "inputs": {"is_affiliated_group_member": True, "pct_property_payroll_outside_us": 0.10,
                "unity_tests_met_all_three_years": 2},
     "expected_outputs": {"combined_include": False},
     "notes": "At least three of the six, for the current AND two preceding years. A single-year test "
              "over-includes and changes every member's apportionment."},
    {"scenario_name": "CO0112-I - ⚠ the line-17 cap is TY2025-only",
     "scenario_type": "edge", "sort_order": 9,
     "inputs": {"hb21_1002_carryforward": 400000},
     "expected_outputs": {"L17_ty2025": 150000.0, "L17_ty2026": 400000.0},
     "notes": "⚠⚠ § 39-22-304(3)(p)(II)(B) removes the cap for TY2026 - the FOURTH item on the re-authoring "
              "cliff, added by the verification pass. A three-item cliff would have carried the 150,000 "
              "cap silently into TY2026 and under-claimed this subtraction by 250,000."},
    {"scenario_name": "CO0112-J - NOL vintages: Colorado is not federal",
     "scenario_type": "edge", "sort_order": 10,
     "inputs": {"loss_2017": 2017, "loss_2019": 2019, "loss_2021": 2021},
     "expected_outputs": {"cf_2017": 20, "cf_2019": None, "cf_2021": 20},
     "notes": "⚠ 2018-2020 losses carry forward without limit; 2021-onward losses revert to TWENTY years "
              "while federal law leaves them indefinite. A federal assumption over-states every "
              "2021-onward Colorado carryforward."},
    {"scenario_name": "CO0112-K - ⚠ a financial institution gets FIFTEEN years, not twenty",
     "scenario_type": "edge", "sort_order": 11,
     "inputs": {"loss_year": 2015, "is_financial_institution": True},
     "expected_outputs": {"carryforward_years": 15, "general_rule_would_give": 20},
     "notes": "⚠ § 39-22-504(4) - a rule the Corporate Income Tax Guide's carryforward table OMITS, so a "
              "preparer working from the Guide over-states the available carryforward by five years. Still "
              "live for 2006-2020 vintages on a TY2025 return."},
]

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "CO_DR0112",
            "form_title": "Colorado Form DR 0112 - C Corporation Income Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-27, which completed Wave 5 Layer 2. Colorado's "
                "C-corp return: federal TI (1120 L30 / 990-T Part I L11) -> statutory modifications -> "
                "apportionment -> a VINTAGED NOL ledger -> 4.4%. ⚠⚠ C2: the six tests of unity diverge "
                "THREE ways (statute / Guide / DR 0112C) and in BOTH directions, so the ruling is BUILD THE "
                "STATUTE, PROMPT WITH THE FORM, DIAGNOSE THE GUIDE. Schedule C is triggered by § 303(12) "
                "membership, not the Section B box; the partnership look-through covers tests 1-4 only; and "
                "combined-group-as-taxpayer is TY2026-ONLY. ⚠⚠ TY2026 is a ratified RE-AUTHORING event "
                "with a FOUR-change cliff. ⚠⚠ The $5,000 estimated-tax question is TWO predicates with "
                "different operators - the obligation is 'greater than', the penalty exception is 'less "
                "than' at statute level - so at exactly $5,000 neither applies. ⚠⚠ W5: 'no Colorado "
                "depreciation modification, federal basis governs' is an AFFIRMATIVE ruling citing "
                "§ 39-22-304(3)(p)(III), not an absence, and the 'prior to 1965' condition is a Guide "
                "gloss the statute does not carry. ⚠ P.L. 86-272 zeroes LINE 19, not line 18."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-CO0112-UNITY", "title": "⚠⚠ Build the statute, prompt with the form, diagnose the Guide",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "⚠⚠ The six tests of unity are worded three ways and the differences run in BOTH "
                    "directions - the DR 0112C is broader than the statute on test 1 and narrower on test "
                    "2, while the Guide is bidirectional on tests 4 and 5 where the statute is not. Any "
                    "build that picked a single text would be wrong on at least two tests, in opposite "
                    "directions. The arithmetic follows § 39-22-303(11)(a); the preparer sees the form's "
                    "wording; the Guide's divergences raise a diagnostic.",
     "definition": {"rule": "R-CO0112-COMBINED",
                    "check": ">=3 of 6 on the STATUTORY formulation, over current + 2 preceding years"}},
    {"assertion_id": "FA-CO0112-NOL80", "title": "⚠ The 80% limit applies to line 16(b), never to line 15",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "⚠ The 80% limitation bites on Colorado taxable income AFTER the pre-2018 losses are "
                    "deducted - which is precisely why line 16(b) is printed as its own line. Applying 80% "
                    "to line 15 can produce a line 16(d) LARGER than line 15, so the wrong base is not "
                    "merely different: it is impossible. Colorado decoupled from the CARES suspension by "
                    "§ 39-22-504(1)(b).",
     "definition": {"rule": "R-CO0112-NOL", "check": "16c == min(post2017, 16b * 0.80)"}},
    {"assertion_id": "FA-CO0112-5000", "title": "⚠⚠ Two $5,000 predicates, different operators",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠⚠ The obligation to remit needs tax GREATER THAN $5,000; the penalty exception needs "
                    "tax LESS THAN $5,000 (§ 39-22-606(6)(a)(I), C.R.S.). They are different rules, not "
                    "conflicting sources - the apparent 3-2 split was a category error corrected at "
                    "campaign D-18. At exactly $5,000 neither applies, so a single shared predicate is "
                    "wrong at exactly one point - and that point is a round number.",
     "definition": {"rule": "R-CO0112-EST",
                    "check": "must_remit == (tax > 5000) and exception == (tax < 5000)"}},
    {"assertion_id": "FA-CO0112-PL86", "title": "⚠ P.L. 86-272 overrides line 19; line 18 keeps its value",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠ Section A: 'enter $0 tax on line 19'. Zeroing line 18 instead prints the same tax "
                    "while corrupting the NOL ledger and the apportionment reconciliation - the two "
                    "errors are indistinguishable on the filed return, and only one of them is right. "
                    "⚠ The DR 0106 carries the same rule at a DIFFERENT line number.",
     "definition": {"rule": "R-CO0112-PL86272", "check": "L18 retained; only L19 overridden to 0"}},
    {"assertion_id": "FA-CO0112-RATE", "title": "⚠ The rate year comes from the DEEMED commencement date",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "⚠ W9. A 52-53 week year beginning in December is deemed to commence the following "
                    "January 1 and takes THAT year's rate (Guide Parts 3 and 10). Colorado's rate has "
                    "already moved once - TY2024's 4.25% under a one-off § 39-22-627(1)(c) directive - so "
                    "selecting the rate from the calendar start date is a live bug, not a formality. "
                    "⚠ TY2027/28 rates are deliberately ABSENT: Legislative Council Staff projections are "
                    "not enacted rates.",
     "definition": {"rule": "R-CO0112-TAX", "check": "rate_year == deemed_commencement_year"}},
    {"assertion_id": "FA-CO0112-DEPR", "title": "⚠⚠ Federal basis governs - a CITED affirmative, not an absence",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 6,
     "description": "⚠⚠ A class-(b) correction. § 39-22-304(3)(p)(III), C.R.S. DIRECTS the use of federal "
                    "basis for qualified improvement property and cross-references § 304(3)(c), proving "
                    "that subsection is live law legislated about in 2021. So 'no Colorado depreciation "
                    "modification, no Colorado basis ledger' is a ruling with a citation, not a failure to "
                    "find a rule. ⚠ The 'acquired prior to January 1, 1965' condition is a Guide gloss - "
                    "the statute carries no date limitation at all, and two prior readings said otherwise.",
     "definition": {"rule": "R-CO0112-DEPR",
                    "check": "no CO depreciation modification; authority recorded, not blank"}},
    {"assertion_id": "FA-CO0112-TY2026", "title": "⚠⚠ TY2026 changes FOUR things at once",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 7,
     "description": "⚠⚠ Ratified at D-27 as a re-authoring event: the HB 24-1134 combined regime, the "
                    "listed-jurisdictions rule, the § 250 FDDEI add-back, AND removal of the $150,000 "
                    "line-17 cap. The fourth was added by the verification pass; a three-item cliff would "
                    "have carried the cap silently into TY2026. § 39-22-303(11) dates itself.",
     "definition": {"rule": "R-CO0112-L17", "check": "len(CO_TY2026_REAUTHORING_CHANGES) == 4"}},
]


class Command(BaseCommand):
    help = ("Load the CO_DR0112 spec (Colorado C Corporation Income Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad CO_DR0112 spec (Colorado C Corporation Income Tax Return, TY2025)\n"))
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
        """Pinned to the GATE MECHANISM, not the sentinel's value (D-17)."""
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
                "\nREFUSING TO SEED CO_DR0112: not cleared to seed.\n\n"
                "Campaign D-27 approved the Colorado walk SCOPE. That is NOT the seed gate. Ken\n"
                "must give the Gate-1 SEED approval DIRECTLY - a relayed approval never opens a\n"
                "human gate.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\nEmpty:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            if len(name) > 255:
                raise CommandError(f"topic_name for {code!r} is {len(name)} chars - the column is 255 "
                                   "(fails ONLY on the live database; campaign D-17).")
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
        missing = [c for c in EXISTING_SOURCES_TO_REFERENCE
                   if not AuthoritySource.objects.filter(source_code=c).exists()]
        if missing:
            raise CommandError(
                f"Referenced source codes do not resolve: {', '.join(missing)}. A code that does not "
                "resolve becomes a DANGLING REFERENCE - campaign D-25/O4, and D-29 where I made that "
                "mistake myself. Correct the code before seeding."
            )
        for code in EXISTING_SOURCES_TO_REFERENCE:
            sources[code] = AuthoritySource.objects.get(source_code=code)
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
        """Delete rows this loader no longer declares (campaign D-16)."""
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
        self.stdout.write("CO_DR0112 loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  CO_DR0112: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! The six unity tests are BUILT FROM STATUTE - the form prompts, the Guide")
        self.stdout.write("     diagnoses. Never collapse the three wordings.")
        self.stdout.write("  !! TY2026 is a RE-AUTHORING event with FOUR changes - do not roll forward.")
        self.stdout.write("=" * 66)
