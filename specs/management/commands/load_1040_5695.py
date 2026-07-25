"""Load the FORM_5695 spec — Residential Energy Credits (§25D + §25C).

VERSION 2 (2026-07-25, s110) — THE "LIGHT 2025 FACE" AMENDMENT.
Ken's scope call this session, verbatim: "I think this form goes away for 2026 so
you can do a light version. something good enough to complete the tax return."
v1 modelled 17 cost boxes and nothing else; the 2025 face additionally REQUIRES
eligibility answers, home addresses and Qualified Manufacturer ID numbers, and
its doors arithmetic is not the one v1 used. v2 adds exactly what is needed to
produce a FILABLE 2025 Form 5695, and no more:
  (a) THE ELIGIBILITY GATES that can deny a credit — 5a (battery ≥3 kWh),
      7a (fuel cell in the main home), 17a/b/c (main home in the US / original
      user / 5-year use), 21a/b (US residence / originally placed in service by
      you), 25a (enabling property installed in 2025), 26a (qualifying audit).
      An explicit NO denies its branch exactly as the face directs. An
      UNANSWERED gate does NOT deny — it fires D_5695_GATE_OPEN. See the note on
      E_RULES R-5695-GATE for why that deviation from the face is deliberate.
  (b) THE QM PIN (§25C(h)) — first required for property placed in service after
      Dec 31, 2024, i.e. TY2025 is the FIRST year it bites. Without it the IRS
      disallows the §25C credit, so a 5695 that omits it is not a filable form.
      One PIN per §25C category (the face's per-item PIN slots are the deferred
      part of "light"): doors/windows/AC/water heater/furnace/enabling/heat pump.
  (c) THE HOME ADDRESS — one main-home address, rendered into all four address
      blocks the face carries (Part I, 7b, 17d, 21c). "You can only have one main
      home at a time" (face caution), so one address is the honest model.
  (d) THE DOORS ARITHMETIC CORRECTED — the face caps the MOST EXPENSIVE door at
      $250 on its own (19c) before the $500 aggregate (19h). v1's
      min(30%×all_doors, 500) OVERSTATES: $2,000 of doors gave $500 where the
      face gives $250. One new fact (the most expensive door's cost) fixes it.

DELIBERATELY STILL DEFERRED IN v2 (the "light" boundary, all preparer-visible):
  - The per-item PIN slots (19d two next doors, 20a four windows, 23a two water
    heaters, 25d(i)(ii), 29a/c/e each). The ARITHMETIC is unaffected — 19f =
    19d + 19e and 20c = 20a + 20b, so folding the sibling costs into the "all
    other" box produces the identical credit; only the extra PIN boxes go blank.
  - The joint-occupancy allocation (7c / 32a) — still D_5695_JOINT.
  - The construction-related split (17e) — Yes fires a warning, no auto-split.
  - The precise Credit Limit Worksheet credit-ordering (v1's simplified limit).

v1 header follows.
--------------------------------------------------------------------------
Load the FORM_5695 spec — Residential Energy Credits (§25D + §25C), minimal v1.

Phase 2, third common form. Ken: "do the very least we can do on 5695 for 2025"
(2026-06-15). Form 5695 carries two nonrefundable credits:
  Part I  — Residential Clean Energy Credit (§25D) → line 15 → Schedule 3 line 5a.
            30% of solar/wind/geothermal/battery + fuel cell (min(30%×cost,
            $1,000×kW)). Nonrefundable, carries forward (line 16).
  Part II — Energy Efficient Home Improvement Credit (§25C) → line 32 → Sch 3 5b.
            30% with annual caps; no carryforward (excess lost).

KEN'S 2 SCOPE DECISIONS (2026-06-15, AskUserQuestion):
  (1) Both parts, the caps modeled; the worksheet/edge detail deferred.
  (2) Model the tax-liability limit (Credit Limit Worksheet) + the §25D carryforward.

LAW VERIFIED 2026-06-15 (brief tts-tax-app server/specs/_5695_source_brief.md):
  - §25D: 30%, fuel cell capped $500 per ½ kW (= $1,000 × kW). Carries forward.
  - §25C: 30%; doors $250 each/$500 all, windows $600, each energy-property item
    $600, home energy audit $150, the Section A+B AGGREGATE $1,200; heat pumps /
    HP water heaters / biomass a SEPARATE $2,000. §25C annual max $3,200.
  - OBBBA TERMINATES BOTH after Dec 31, 2025 — TY2025 is the last year; a TY2026
    return fires a RED (D_5695_2026).

SAFETY GUARD: READY_TO_SEED stays False until Ken's review walk (the §25D/§25C
caps + the carryforward + the tax-liability limit + the OBBBA termination).
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


READY_TO_SEED = True  # FLIPPED 2026-06-15 — Ken approved the review walk ("Approved — seed it, include render").


FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 2  # v2 2026-07-25 — the light 2025 face (gates + QM PINs + address + doors split).
FORM_ENTITY_TYPES = ["1040"]
FORM_STATUS = "draft"


# ═══════════════════════════════════════════════════════════════════════════
# THE MATH (the integrity gate re-types this independently; they share no math).
# ═══════════════════════════════════════════════════════════════════════════

RATE = 0.30
FUEL_CELL_PER_KW = 1000      # $500 per ½ kW
DOOR_TOP_CAP = 250           # line 19c — the MOST EXPENSIVE door, on its own
DOORS_CAP = 500              # line 19h — all doors, aggregate
WINDOWS_CAP = 600
ITEM_CAP = 600               # each Section-B energy-property item
AUDIT_CAP = 150
AGG_25C = 1200               # the Section A+B aggregate
HEATPUMP_CAP = 2000          # heat pumps / HP water heaters / biomass (separate)

# The gates are TRI-STATE. False denies; None (unanswered) does not — see R-5695-GATE.
def _denied(gate) -> bool:
    """True only when the preparer explicitly answered No."""
    return gate is False


def _r0(x) -> int:
    return int(round(x))


def credit_25d(solar_elec, solar_water, small_wind, geothermal, battery,
               fuel_cell_cost, fuel_cell_kw, carryforward_prior, tax_limit,
               battery_ge_3kwh=None, fuel_cell_main_home=None) -> tuple[int, int]:
    """Part I (§25D). Returns (line15 credit → Sch 3 5a, line16 carryforward-out).

    Line 5a No  → the battery cost cannot be claimed (face: "you cannot claim a
                  credit for qualified battery storage technology").
    Line 7a No  → skip lines 7b through 11, i.e. no fuel cell credit.
    """
    claimed_battery = 0 if _denied(battery_ge_3kwh) else battery
    l6b = RATE * (solar_elec + solar_water + small_wind + geothermal + claimed_battery)
    fuel = 0 if _denied(fuel_cell_main_home) else min(RATE * fuel_cell_cost,
                                                      FUEL_CELL_PER_KW * fuel_cell_kw)
    l13 = _r0(l6b + fuel + carryforward_prior)
    l15 = min(l13, _r0(tax_limit))
    return (l15, l13 - l15)


def credit_25c(insulation, doors_top, doors_other, windows, central_ac, water_heater,
               furnace, panelboard, audit, heat_pump_biomass, tax_limit,
               section_a=None, section_b=None, enabling=None, audit_ok=None) -> int:
    """Part II (§25C). Returns line32 credit → Sch 3 5b (no carryforward).

    `section_a` is the AND of lines 17a/17b/17c, `section_b` the AND of 21a/21b —
    each is False only when the preparer answered No to at least one of them.
    A denied Section A zeroes lines 18b/19h/20d; a denied Section B zeroes
    22d/23d/24d/25e AND line 29 (the face: "Skip lines 22 through 25 and line 29");
    `enabling` (25a) gates line 25e alone and `audit_ok` (26a) line 26c alone.

    DOORS (the v1 correction): line 19c caps the most expensive door at $250 by
    itself, line 19g is 30% of every other door uncapped per item, and line 19h
    caps their sum at $500.
    """
    a_ok = not _denied(section_a)
    b_ok = not _denied(section_b)

    l18b = min(RATE * insulation, AGG_25C) if a_ok else 0
    l19c = min(RATE * doors_top, DOOR_TOP_CAP)
    l19g = RATE * doors_other
    l19h = min(l19c + l19g, DOORS_CAP) if a_ok else 0
    l20d = min(RATE * windows, WINDOWS_CAP) if a_ok else 0

    l22d = min(RATE * central_ac, ITEM_CAP) if b_ok else 0
    l23d = min(RATE * water_heater, ITEM_CAP) if b_ok else 0
    l24d = min(RATE * furnace, ITEM_CAP) if b_ok else 0
    l25e = min(RATE * panelboard, ITEM_CAP) if (b_ok and not _denied(enabling)) else 0
    l26c = min(RATE * audit, AUDIT_CAP) if not _denied(audit_ok) else 0

    l27 = l18b + l19h + l20d + l22d + l23d + l24d + l25e + l26c
    l28 = min(l27, AGG_25C)
    l29h = min(RATE * heat_pump_biomass, HEATPUMP_CAP) if b_ok else 0
    l30 = _r0(l28 + l29h)
    return min(l30, _r0(tax_limit))


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("residential_energy_credits", "Residential energy credits (§25D clean energy + §25C home improvement) — Form 5695 → Schedule 3 line 5a/5b; OBBBA terminates both after 2025"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "IRS_2025_1040_FORM",
    "IRS_2025_1040_INSTR",
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRS_2025_F5695_INSTR",
        "source_type": "official_instructions",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "2025 Instructions for Form 5695 — Residential Energy Credits",
        "citation": "Instructions for Form 5695 (2025), Parts I and II",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/instructions/i5695",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 9.50,
        "requires_human_review": True,
        "notes": "Part I §25D 30% + fuel-cell cap + carryforward; Part II §25C caps ($1,200 aggregate + $2,000 heat-pump group). REQUIRES HUMAN REVIEW: the precise Credit Limit Worksheet credit-ordering is simplified in v1; joint-occupancy + QM-PIN + CEE-tier qualification are preparer-asserted.",
        "topics": ["residential_energy_credits"],
        "excerpts": [
            {
                "excerpt_label": "Part I §25D — 30% + fuel cell + carryforward",
                "location_reference": "i5695 (2025), Part I, lines 1-16",
                "excerpt_text": (
                    "Enter 30% of the costs of qualified solar electric, solar water heating, small wind, "
                    "geothermal heat pump, and battery storage (at least 3 kilowatt hours) property. For fuel "
                    "cell property, the credit is limited to $500 for each one-half kilowatt of capacity. Add "
                    "any credit carryforward from 2024. The credit can't be more than your tax liability; carry "
                    "any unused credit forward to 2026."
                ),
                "summary_text": "§25D = 30% of clean-energy costs (fuel cell $500/½kW) + prior carryforward, limited to tax, excess carries forward.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Part II §25C — the caps",
                "location_reference": "i5695 (2025), Part II, lines 17-32",
                "excerpt_text": (
                    "The energy efficient home improvement credit is 30% of the cost of qualified improvements, "
                    "limited to $1,200 per year in the aggregate, with sub-limits of $250 per exterior door "
                    "($500 total), $600 for exterior windows and skylights, and $600 for each item of qualified "
                    "energy property, and $150 for a home energy audit. A separate $2,000 limit applies to heat "
                    "pumps, heat pump water heaters, and biomass stoves and boilers. There is no carryforward."
                ),
                "summary_text": "§25C = 30% capped: $1,200 aggregate (doors $500/windows $600/item $600/audit $150) + a separate $2,000 heat-pump group; no carryforward.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "OBBBA termination after 2025",
                "location_reference": "i5695 (2025), What's New",
                "excerpt_text": (
                    "You can't claim residential clean energy credits for expenditures made after December 31, "
                    "2025. You can't claim energy efficient home improvement credits for expenditures or "
                    "property placed in service after December 31, 2025."
                ),
                "summary_text": "Both credits terminate after 12/31/2025 (OBBBA) — TY2025 is the last year.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "IRC_25D",
        "source_type": "statute",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §25D — Residential Clean Energy Credit",
        "citation": "26 U.S.C. §25D (30% credit; §25D(c) carryforward; OBBBA termination after 2025)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:25D%20edition:prelim)",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": "30% residential clean energy credit; carries forward to the succeeding year; terminated for property placed in service after 2025 (OBBBA §70506).",
        "topics": ["residential_energy_credits"],
        "excerpts": [
            {
                "excerpt_label": "§25D(a) the 30% credit",
                "location_reference": "26 U.S.C. §25D(a)",
                "excerpt_text": (
                    "There shall be allowed as a credit an amount equal to 30 percent of the qualified solar "
                    "electric, solar water heating, fuel cell, small wind energy, geothermal heat pump, and "
                    "battery storage property expenditures."
                ),
                "summary_text": "§25D = 30% of qualified residential clean-energy expenditures.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "IRC_25C",
        "source_type": "statute",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §25C — Energy Efficient Home Improvement Credit",
        "citation": "26 U.S.C. §25C (30%; §25C(b) the $1,200/$2,000 limits; OBBBA termination after 2025)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:25C%20edition:prelim)",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": "30% home-improvement credit; §25C(b) the $1,200 aggregate + $2,000 heat-pump limits; no carryforward; terminated for property placed in service after 2025 (OBBBA §70505).",
        "topics": ["residential_energy_credits"],
        "excerpts": [
            {
                "excerpt_label": "§25C(b) the annual limitation",
                "location_reference": "26 U.S.C. §25C(b)",
                "excerpt_text": (
                    "The credit allowed shall not exceed $1,200 (the aggregate per-taxpayer annual limit), with "
                    "$250 per exterior door and $500 for all doors, $600 for exterior windows and skylights, and "
                    "$600 per item of qualified energy property; a separate $2,000 limit applies to heat pumps, "
                    "heat pump water heaters, and biomass stoves and boilers."
                ),
                "summary_text": "§25C(b): $1,200 aggregate (with door/window/item sub-caps) + a separate $2,000 heat-pump group.",
                "is_key_excerpt": True,
            },
        ],
    },
]

NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = []

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("IRS_2025_F5695_INSTR", "FORM_5695", "governs"),
    ("IRC_25D", "FORM_5695", "governs"),
    ("IRC_25C", "FORM_5695", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM: FORM_5695
# ═══════════════════════════════════════════════════════════════════════════

E_IDENTITY = {
    "form_number": "FORM_5695",
    "form_title": "Form 5695 Residential Energy Credits (§25D + §25C) (TY2025)",
    "notes": (
        "Ken's 2 scope decisions 2026-06-15 ('the very least'). A return-level "
        "FormDefinition on the 1040 (one home; the Schedule-A / 8889 facts "
        "precedent). Part I §25D (30% clean energy + fuel-cell $500/½kW cap + "
        "carryforward) → line 15 → Schedule 3 line 5a. Part II §25C (30% with the "
        "$1,200 aggregate + the $250/$500 doors / $600 windows / $600-per-item / "
        "$150 audit sub-caps + a separate $2,000 heat-pump/biomass group; no "
        "carryforward) → line 32 → Schedule 3 line 5b. The Credit Limit Worksheet "
        "caps each at available tax. OBBBA TERMINATES both after 2025 — a TY2026 "
        "return fires D_5695_2026. "
        "V2 (2026-07-25, Ken: 'a light version, good enough to complete the tax "
        "return'): the 2025 face's ELIGIBILITY GATES (5a/7a/17a-c/21a-b/25a/26a — "
        "an explicit No denies exactly the branch the form skips; unanswered does "
        "NOT deny), the §25C(h) QM ID NUMBERS (one per category — required for "
        "property placed in service after 12/31/2024, so TY2025 is the first and "
        "only year), ONE MAIN HOME ADDRESS rendered into all four face blocks, and "
        "the DOORS ARITHMETIC CORRECTED to the face (19c caps the most expensive "
        "door at $250 before the $500 aggregate; v1 overstated). Still deferred: "
        "the per-item PIN slots (arithmetic-neutral), joint occupancy / fractional "
        "share allocation, the 17e construction split, CEE-tier qualification."
    ),
}

E_FACTS: list[dict] = [
    # ── Part I §25D inputs ──
    {"fact_key": "e5695_solar_electric", "label": "Qualified solar electric property cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 1, "notes": "Line 1 (30%)."},
    {"fact_key": "e5695_solar_water", "label": "Qualified solar water heating property cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 2, "notes": "Line 2 (30%)."},
    {"fact_key": "e5695_small_wind", "label": "Qualified small wind energy property cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 3, "notes": "Line 3 (30%)."},
    {"fact_key": "e5695_geothermal", "label": "Qualified geothermal heat pump property cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 4, "notes": "Line 4 (30%)."},
    {"fact_key": "e5695_battery", "label": "Qualified battery storage (≥3 kWh) cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 5, "notes": "Line 5b (30%)."},
    {"fact_key": "e5695_fuel_cell_cost", "label": "Qualified fuel cell property cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 6, "notes": "Line 8; min(30%, $1,000×kW)."},
    {"fact_key": "e5695_fuel_cell_kw", "label": "Fuel cell capacity (kilowatts)",
     "data_type": "decimal", "default_value": "0", "sort_order": 7, "notes": "Line 10 cap = $1,000 × kW."},
    {"fact_key": "e5695_25d_carryforward", "label": "§25D credit carryforward from 2024",
     "data_type": "decimal", "default_value": "0", "sort_order": 8, "notes": "Line 12."},
    # ── Part II §25C inputs ──
    {"fact_key": "e5695_insulation", "label": "Insulation / air-sealing cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 9, "notes": "Line 18 (30%, no item sub-cap)."},
    {"fact_key": "e5695_doors_top", "label": "Most expensive exterior door — cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 10,
     "notes": "Line 19a. Line 19c caps 30% of THIS door alone at $250 (v2 — v1 had no per-door cap)."},
    {"fact_key": "e5695_doors", "label": "All other exterior doors — cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 11,
     "notes": ("Lines 19d + 19e (the face splits the two next most expensive out for their PINs; the "
               "arithmetic is identical because 19f = 19d + 19e). 30% uncapped per item, then line 19h "
               "caps 19c + 19g at $500 for all doors."),
     },
    {"fact_key": "e5695_windows", "label": "Exterior windows / skylights cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 12, "notes": "Line 20 (30%, $600)."},
    {"fact_key": "e5695_central_ac", "label": "Central air conditioner cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 13, "notes": "Line 22 (30%, $600)."},
    {"fact_key": "e5695_water_heater", "label": "Gas/propane/oil water heater cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 14, "notes": "Line 23 (30%, $600)."},
    {"fact_key": "e5695_furnace", "label": "Furnace / hot water boiler cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 15, "notes": "Line 24 (30%, $600)."},
    {"fact_key": "e5695_panelboard", "label": "Electrical panelboard / circuit upgrade cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 16, "notes": "Line 25c (30%, $600). Gated by line 25a."},
    {"fact_key": "e5695_home_audit", "label": "Home energy audit cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 17, "notes": "Line 26b (30%, $150). Gated by line 26a."},
    {"fact_key": "e5695_heat_pump_biomass", "label": "Heat pump / HP water heater / biomass cost",
     "data_type": "decimal", "default_value": "0", "sort_order": 18, "notes": "Line 29 (30%, separate $2,000)."},

    # ── v2: THE ELIGIBILITY GATES (tri-state — unanswered is NOT a No) ──
    # Every one of these is a question the 2025 face asks and then uses to DENY a
    # credit. They carry no default_value on purpose: "unanswered" is a real,
    # distinct state that fires D_5695_GATE_OPEN rather than silently zeroing.
    {"fact_key": "e5695_battery_ge_3kwh", "label": "Line 5a — battery storage capacity is at least 3 kWh?",
     "data_type": "boolean", "sort_order": 40,
     "notes": "Line 5a. No → the battery cost cannot be claimed (excluded from line 6a)."},
    {"fact_key": "e5695_fuel_cell_main_home", "label": "Line 7a — fuel cell installed on your main home in the US?",
     "data_type": "boolean", "sort_order": 41,
     "notes": "Line 7a. No → skip lines 7b-11; no fuel cell credit."},
    {"fact_key": "e5695_25c_main_home", "label": "Line 17a — improvements installed in/on your main home in the US?",
     "data_type": "boolean", "sort_order": 42,
     "notes": "Line 17a. No (or 17b/17c No) → no Section A credit at all."},
    {"fact_key": "e5695_25c_original_user", "label": "Line 17b — are you the original user of the improvements?",
     "data_type": "boolean", "sort_order": 43, "notes": "Line 17b. Part of the Section A gate."},
    {"fact_key": "e5695_25c_five_years", "label": "Line 17c — components expected to remain in use at least 5 years?",
     "data_type": "boolean", "sort_order": 44, "notes": "Line 17c. Part of the Section A gate."},
    {"fact_key": "e5695_25c_construction", "label": "Line 17e — were any improvements related to constructing this home?",
     "data_type": "boolean", "sort_order": 45,
     "notes": ("Line 17e. Yes does NOT deny — construction-related costs are simply not eligible, and v2 "
               "does not split them out. Fires D_5695_CONSTRUCT so the preparer excludes them by hand.")},
    {"fact_key": "e5695_energy_prop_residence", "label": "Line 21a — energy property at a US home you use as a residence?",
     "data_type": "boolean", "sort_order": 46,
     "notes": "Line 21a. No (or 21b No) → skip lines 22-25 AND line 29 (heat pumps too)."},
    {"fact_key": "e5695_energy_prop_original_use", "label": "Line 21b — was the energy property originally placed in service by you?",
     "data_type": "boolean", "sort_order": 47, "notes": "Line 21b. Part of the Section B gate."},
    {"fact_key": "e5695_enabling_2025", "label": "Line 25a — enabling and enabled property both installed in 2025?",
     "data_type": "boolean", "sort_order": 48,
     "notes": "Line 25a. No → skip lines 25b-25e; no panelboard/enabling-property credit."},
    {"fact_key": "e5695_enabling_code", "label": "Line 25b — code for the type of enabled property",
     "data_type": "string", "sort_order": 49,
     "notes": "Line 25b. Preparer-supplied per the instructions' code list; not validated."},
    {"fact_key": "e5695_audit_qualified", "label": "Line 26a — audit of your main home with a written report by a certified auditor?",
     "data_type": "boolean", "sort_order": 50,
     "notes": "Line 26a. No → no home energy audit credit."},

    # ── v2: THE QUALIFIED MANUFACTURER ID NUMBERS (§25C(h)) ──
    # Required for property placed in service AFTER Dec 31, 2024 — TY2025 is the
    # first year. Omitting one does not change the arithmetic; it gets the credit
    # DISALLOWED, so D_5695_QM_PIN flags it. One PIN per category is the "light"
    # boundary (the face has a slot per item).
    {"fact_key": "e5695_pin_doors", "label": "QM ID number — most expensive exterior door",
     "data_type": "string", "sort_order": 60, "notes": "Line 19b. §25C(h)."},
    {"fact_key": "e5695_pin_windows", "label": "QM ID number — windows / skylights",
     "data_type": "string", "sort_order": 61, "notes": "Line 20a. §25C(h)."},
    {"fact_key": "e5695_pin_central_ac", "label": "QM ID number — central air conditioner",
     "data_type": "string", "sort_order": 62, "notes": "Line 22a. §25C(h)."},
    {"fact_key": "e5695_pin_water_heater", "label": "QM ID number — gas/propane/oil water heater",
     "data_type": "string", "sort_order": 63, "notes": "Line 23a. §25C(h)."},
    {"fact_key": "e5695_pin_furnace", "label": "QM ID number — furnace / hot water boiler",
     "data_type": "string", "sort_order": 64, "notes": "Line 24a. §25C(h)."},
    {"fact_key": "e5695_pin_panelboard", "label": "QM ID number — enabling property (panelboard)",
     "data_type": "string", "sort_order": 65, "notes": "Line 25d(i). §25C(h)."},
    {"fact_key": "e5695_pin_heat_pump_biomass", "label": "QM ID number — heat pump / HP water heater / biomass",
     "data_type": "string", "sort_order": 66, "notes": "Lines 29a/29c/29e. §25C(h)."},

    # ── v2: THE MAIN HOME ADDRESS ──
    # ONE address. The face carries four address blocks (Part I, 7b, 17d, 21c) but
    # cautions "You can only have one main home at a time", so v2 keys it once and
    # renders it into every block. A second home is the deferred multi-home case.
    {"fact_key": "e5695_home_street", "label": "Main home — number and street",
     "data_type": "string", "sort_order": 70, "notes": "Renders into the Part I, 7b, 17d and 21c address blocks."},
    {"fact_key": "e5695_home_unit", "label": "Main home — unit no.",
     "data_type": "string", "sort_order": 71, "notes": "Same four blocks."},
    {"fact_key": "e5695_home_city", "label": "Main home — city or town",
     "data_type": "string", "sort_order": 72, "notes": "Same four blocks."},
    {"fact_key": "e5695_home_state", "label": "Main home — state",
     "data_type": "string", "sort_order": 73, "notes": "Same four blocks."},
    {"fact_key": "e5695_home_zip", "label": "Main home — ZIP code",
     "data_type": "string", "sort_order": 74, "notes": "Same four blocks."},

    # ── Edge flags ──
    {"fact_key": "e5695_joint_occupancy", "label": "Joint occupancy (allocation needed)?",
     "data_type": "boolean", "default_value": "false", "sort_order": 80,
     "notes": "Lines 7c AND 32a — one fact drives both checkboxes. D_5695_JOINT — allocation not modeled."},
    {"fact_key": "e5695_condo_fractional", "label": "Condominium / cooperative fractional share?",
     "data_type": "boolean", "default_value": "false", "sort_order": 81,
     "notes": "Line 32b checkbox. The fractional-share computation is not modeled — D_5695_FRACTIONAL."},
    # ── Outputs ──
    {"fact_key": "e5695_line15", "label": "§25D credit → Schedule 3 line 5a",
     "data_type": "decimal", "sort_order": 30, "notes": "OUTPUT. Part I credit."},
    {"fact_key": "e5695_line16", "label": "§25D carryforward to 2026",
     "data_type": "decimal", "sort_order": 31, "notes": "OUTPUT. Line 13 − line 15."},
    {"fact_key": "e5695_line32", "label": "§25C credit → Schedule 3 line 5b",
     "data_type": "decimal", "sort_order": 32, "notes": "OUTPUT. Part II credit (no carryforward)."},
]

E_RULES: list[dict] = [
    {"rule_id": "R-5695-25D", "title": "Part I §25D — 30% clean energy + fuel cell + carryforward", "rule_type": "calculation",
     "precedence": 1, "sort_order": 1,
     "formula": ("l6b = 30% × (solar_elec + solar_water + small_wind + geothermal + battery); fuel = "
                 "min(30%×fuel_cost, $1,000×kW); l13 = l6b + fuel + carryforward_2024; l15 = min(l13, "
                 "tax_limit) → Sch 3 line 5a; l16 = l13 − l15 (carryforward to 2026)."),
     "inputs": ["e5695_solar_electric", "e5695_solar_water", "e5695_small_wind", "e5695_geothermal",
                "e5695_battery", "e5695_fuel_cell_cost", "e5695_fuel_cell_kw", "e5695_25d_carryforward"],
     "outputs": ["e5695_line15", "e5695_line16"],
     "description": "§25D the residential clean energy credit, tax-limited, with carryforward."},
    {"rule_id": "R-5695-25C", "title": "Part II §25C — 30% with the $1,200 + $2,000 caps", "rule_type": "calculation",
     "precedence": 2, "sort_order": 2,
     "formula": ("l18b = min(30%×insulation, 1200); DOORS l19c = min(30%×most_expensive_door, 250), "
                 "l19g = 30%×other_doors, l19h = min(l19c+l19g, 500); l20d = min(30%×windows, 600); "
                 "l22d/l23d/l24d/l25e = min(30%×item, 600) each; l26c = min(30%×audit, 150); "
                 "l27 = Σ(18b,19h,20d,22d,23d,24d,25e,26c); l28 = min(l27, 1200); "
                 "l29h = min(30%×heat_pump_biomass, 2000); l30 = l28 + l29h; "
                 "l32 = min(l30, tax_limit) → Sch 3 line 5b. No carryforward."),
     "inputs": ["e5695_insulation", "e5695_doors_top", "e5695_doors", "e5695_windows", "e5695_central_ac",
                "e5695_water_heater", "e5695_furnace", "e5695_panelboard", "e5695_home_audit",
                "e5695_heat_pump_biomass"],
     "outputs": ["e5695_line32"],
     "description": ("§25C the energy efficient home improvement credit, capped, no carryforward. v2 "
                     "corrects the doors arithmetic: the face caps the MOST EXPENSIVE door at $250 on "
                     "its own (line 19c) before the $500 all-doors aggregate (line 19h), so v1's "
                     "min(30%×all_doors, 500) overstated — $2,000 on one door gave $500, not $250.")},
    {"rule_id": "R-5695-GATE", "title": "The eligibility gates — an explicit No denies the branch", "rule_type": "conditional",
     "precedence": 5, "sort_order": 5,
     "formula": ("5a No → battery excluded from line 6a. 7a No → skip 7b-11 (no fuel cell). "
                 "17a/17b/17c any No → no Section A (lines 18b/19h/20d = 0). "
                 "21a/21b either No → skip lines 22-25 AND line 29 (no energy property, no heat pump). "
                 "25a No → skip 25b-25e (no enabling property). 26a No → no audit credit. "
                 "UNANSWERED (null) does NOT deny — it fires D_5695_GATE_OPEN."),
     "inputs": ["e5695_battery_ge_3kwh", "e5695_fuel_cell_main_home", "e5695_25c_main_home",
                "e5695_25c_original_user", "e5695_25c_five_years", "e5695_energy_prop_residence",
                "e5695_energy_prop_original_use", "e5695_enabling_2025", "e5695_audit_qualified"],
     "outputs": ["e5695_line15", "e5695_line32"],
     "description": ("The face's own denial logic, modelled TRI-STATE. Answering No zeroes exactly the "
                     "branch the form says to skip. Leaving a question UNANSWERED deliberately does NOT "
                     "zero it: the app back-enters returns already prepared elsewhere, where the "
                     "eligibility was established off-system, and silently deleting a credit the "
                     "preparer computed is a worse failure than flagging the blank. The unanswered "
                     "state is therefore surfaced as a warning, never resolved by assumption.")},
    {"rule_id": "R-5695-QMPIN", "title": "§25C(h) — the Qualified Manufacturer ID number", "rule_type": "validation",
     "precedence": 6, "sort_order": 6,
     "formula": ("For each §25C category with a PIN box on the face (doors 19b, windows 20a, A/C 22a, "
                 "water heater 23a, furnace 24a, enabling property 25d, heat pump/biomass 29a/c/e): "
                 "cost > 0 AND the PIN is blank → D_5695_QM_PIN. The arithmetic is unaffected."),
     "inputs": ["e5695_pin_doors", "e5695_pin_windows", "e5695_pin_central_ac", "e5695_pin_water_heater",
                "e5695_pin_furnace", "e5695_pin_panelboard", "e5695_pin_heat_pump_biomass"],
     "outputs": [],
     "description": ("§25C(h), added by the Inflation Reduction Act, denies the credit for any item "
                     "whose qualified product identification number is not reported on the return. It "
                     "applies to property placed in service after December 31, 2024, so TY2025 is the "
                     "FIRST year it bites — and the last, since OBBBA terminates §25C after 2025. "
                     "Insulation (line 18) and the home energy audit (line 26) have no PIN box and are "
                     "correctly exempt.")},
    {"rule_id": "R-5695-LIMIT", "title": "Credit Limit Worksheet — tax-liability limit", "rule_type": "calculation",
     "precedence": 3, "sort_order": 3,
     "formula": ("Each credit is limited to the tax available after the credits that precede it (Form 5695 "
                 "lines 14 / 31). v1 supplies the available-tax limit from the 1040; §25D excess carries "
                 "forward, §25C excess is lost."),
     "inputs": [], "outputs": [],
     "description": "The nonrefundable tax-liability limit. v1 uses a simplified available-tax amount."},
    {"rule_id": "R-5695-TERM", "title": "OBBBA termination after 2025", "rule_type": "routing",
     "precedence": 4, "sort_order": 4,
     "formula": "If tax_year >= 2026 → both credits = 0 + D_5695_2026 (terminated; prepare manually).",
     "inputs": [], "outputs": [],
     "description": "OBBBA terminates §25D and §25C for expenditures/property after 12/31/2025."},
]

E_LINES: list[dict] = [
    {"line_number": "l1_5", "description": "Part I lines 1-5b: clean-energy costs (solar/wind/geo/battery)", "line_type": "input"},
    {"line_number": "l6b", "description": "Line 6b: 30% of the clean-energy costs", "line_type": "calculated"},
    {"line_number": "l11", "description": "Line 11: fuel cell credit = min(30%×cost, $1,000×kW)", "line_type": "calculated"},
    {"line_number": "l13", "description": "Line 13: 6b + fuel cell + 2024 carryforward", "line_type": "calculated"},
    {"line_number": "l14", "description": "Line 14: tax-liability limit (Credit Limit Worksheet)", "line_type": "input"},
    {"line_number": "l15", "description": "Line 15: §25D credit (smaller of 13 or 14) → Sch 3 5a", "line_type": "total"},
    {"line_number": "l16", "description": "Line 16: §25D carryforward to 2026 (13 − 15)", "line_type": "calculated"},
    {"line_number": "l5a", "description": "Line 5a: battery storage capacity ≥ 3 kWh? No → no battery credit", "line_type": "input"},
    {"line_number": "l7a", "description": "Line 7a: fuel cell on your main home in the US? No → skip lines 7b-11", "line_type": "input"},
    {"line_number": "l7b", "description": "Line 7b: address of the main home where the fuel cell was installed", "line_type": "input"},
    {"line_number": "l17a_c", "description": "Lines 17a/17b/17c: the Section A gate (main home in US / original user / 5 years)", "line_type": "input"},
    {"line_number": "l17d", "description": "Line 17d: address of the main home where the improvements were made", "line_type": "input"},
    {"line_number": "l17e", "description": "Line 17e: were improvements related to constructing this home?", "line_type": "input"},
    {"line_number": "l18_26", "description": "Part II §25C costs (insulation/doors/windows/AC/WH/furnace/panel/audit)", "line_type": "input"},
    {"line_number": "l19c", "description": "Line 19c: most expensive door = min(30% × line 19a, $250)", "line_type": "calculated"},
    {"line_number": "l19h", "description": "Line 19h: all doors = min(19c + 30% × other doors, $500)", "line_type": "calculated"},
    {"line_number": "l21a_b", "description": "Lines 21a/21b: the Section B gate. Either No → skip lines 22-25 AND line 29", "line_type": "input"},
    {"line_number": "l21c", "description": "Line 21c: address of each home where energy property was installed", "line_type": "input"},
    {"line_number": "l25a", "description": "Line 25a: enabling AND enabled property both installed in 2025? No → skip 25b-25e", "line_type": "input"},
    {"line_number": "l26a", "description": "Line 26a: qualifying home energy audit with a written report? No → no audit credit", "line_type": "input"},
    {"line_number": "l1200", "description": "§25C Section A+B credit capped at $1,200 aggregate (line 28)", "line_type": "calculated"},
    {"line_number": "l29", "description": "Line 29: heat-pump/biomass credit = min(30%×cost, $2,000)", "line_type": "calculated"},
    {"line_number": "l30", "description": "Line 30: §25C total before the tax limit ($1,200 + $2,000 groups)", "line_type": "calculated"},
    {"line_number": "l31", "description": "Line 31: tax-liability limit (Credit Limit Worksheet)", "line_type": "input"},
    {"line_number": "l32", "description": "Line 32: §25C credit (smaller of 30 or 31) → Sch 3 5b", "line_type": "total"},
    {"line_number": "sch3_5a", "description": "§25D credit → Schedule 3 line 5a", "line_type": "total"},
    {"line_number": "sch3_5b", "description": "§25C credit → Schedule 3 line 5b", "line_type": "total"},
]

E_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_5695_2026", "title": "Residential energy credits terminated after 2025", "severity": "error",
     "condition": "tax_year >= 2026 AND any 5695 cost is present",
     "message": ("Not supported for 2026+: OBBBA terminated both the Residential Clean Energy Credit (§25D) "
                 "and the Energy Efficient Home Improvement Credit (§25C) for expenditures/property after "
                 "December 31, 2025. Only a §25D carryforward from 2025 may remain — prepare any 2026 "
                 "carryforward manually."),
     "notes": "OBBBA termination. RED for 2026+."},
    {"diagnostic_id": "D_5695_25C_CAP", "title": "§25C credit capped (the $1,200 / $2,000 limits)", "severity": "info",
     "condition": "the §25C 30% gross exceeds the $1,200 aggregate or the $2,000 heat-pump cap",
     "message": ("The energy efficient home improvement credit was capped: the building-envelope + energy-"
                 "property credits are limited to $1,200 in the aggregate, and heat pumps / heat pump water "
                 "heaters / biomass to a separate $2,000 (annual maximum $3,200)."),
     "notes": "§25C(b)."},
    {"diagnostic_id": "D_5695_25C_LOST", "title": "§25C credit reduced by tax — the excess is LOST", "severity": "warning",
     "condition": "the §25C credit (line 30) exceeds the tax-liability limit (line 31)",
     "message": ("The §25C home improvement credit was reduced by the tax-liability limit. Unlike the §25D "
                 "clean energy credit, §25C does NOT carry forward — the excess is permanently lost. Confirm "
                 "the limit before filing."),
     "notes": "§25C has no carryforward."},
    {"diagnostic_id": "D_5695_25D_CFWD", "title": "§25D clean energy credit carries forward to 2026", "severity": "info",
     "condition": "the §25D credit (line 13) exceeds the tax-liability limit (line 14)",
     "message": ("The §25D residential clean energy credit exceeded this year's tax; the unused amount "
                 "carries forward to 2026 (Form 5695 line 16). The carryforward survives even though the "
                 "credit itself is terminated for new 2026 expenditures."),
     "notes": "§25D(c) carryforward."},
    {"diagnostic_id": "D_5695_FUEL_CELL", "title": "Fuel cell credit capped at $500 per ½ kW", "severity": "info",
     "condition": "30% of the fuel cell cost exceeds $1,000 × the kilowatt capacity",
     "message": ("The fuel cell property credit was limited to $500 for each one-half kilowatt of capacity "
                 "($1,000 × kW), which is less than 30% of the cost."),
     "notes": "§25D fuel-cell cap."},
    {"diagnostic_id": "D_5695_JOINT", "title": "Joint occupancy — allocation not modeled", "severity": "warning",
     "condition": "e5695_joint_occupancy is True",
     "message": ("Joint occupancy is indicated. The per-occupant allocation of the residential energy credits "
                 "(Form 5695 lines 7c / 32a) is not modeled — verify each occupant's share manually."),
     "notes": "Deferred edge case."},
    # ── v2 ──
    {"diagnostic_id": "D_5695_QM_PIN", "title": "Qualified Manufacturer ID number missing (§25C(h))", "severity": "warning",
     "condition": "a §25C category with a PIN box on the face has a cost but no QM ID number",
     "message": ("A §25C cost was entered without its Qualified Manufacturer Identification Number. For "
                 "property placed in service after December 31, 2024, §25C(h) DENIES the credit for any "
                 "item whose QM ID number is not reported on the return — 2025 is the first year this "
                 "applies. Enter the number shown on the manufacturer's certification, or remove the cost."),
     "notes": ("§25C(h). A warning rather than an error: the app cannot verify a PIN, and blocking "
               "transmission on an unverifiable field would stop a return the preparer may have the "
               "number for. Insulation (line 18) and the audit (line 26) have no PIN box and never fire.")},
    {"diagnostic_id": "D_5695_GATE_OPEN", "title": "Eligibility question unanswered", "severity": "warning",
     "condition": "a cost is entered for a branch whose Yes/No eligibility question is still blank",
     "message": ("Form 5695 asks an eligibility question for this credit (lines 5a, 7a, 17a-17c, 21a-21b, "
                 "25a or 26a) and it has not been answered. The credit has been computed as though the "
                 "property qualifies — answer the question to confirm, because a No means the credit "
                 "cannot be claimed at all."),
     "notes": "Tri-state gate: unanswered is a distinct state from No and never silently zeroes a credit."},
    {"diagnostic_id": "D_5695_GATE_NO", "title": "A credit was denied by an eligibility answer", "severity": "info",
     "condition": "an eligibility question was answered No and zeroed its branch",
     "message": ("A 'No' answer on Form 5695 removed part of the credit, exactly as the form directs. "
                 "Line 5a No drops the battery cost; 7a No drops the fuel cell; 17a/b/c No removes the "
                 "whole of Section A; 21a/b No removes the energy property AND the heat pump credit; "
                 "25a No removes the enabling property; 26a No removes the home energy audit."),
     "notes": "INFO, not a warning — the preparer caused it on purpose; this only explains the number."},
    {"diagnostic_id": "D_5695_ADDRESS", "title": "Main home address missing", "severity": "warning",
     "condition": "Form 5695 is engaged and the main home street or city is blank",
     "message": ("Form 5695 requires the complete address of the home where the property was installed "
                 "(the Part I block and lines 7b, 17d and 21c). Enter the main home address."),
     "notes": "The face asks for it in four places; the app keys it once."},
    {"diagnostic_id": "D_5695_CONSTRUCT", "title": "Improvements related to constructing the home", "severity": "warning",
     "condition": "e5695_25c_construction is True",
     "message": ("Line 17e is Yes: some improvements related to constructing this home. Costs related to "
                 "the construction of your main home do NOT qualify, even if the work was done after you "
                 "moved in. Remove those costs — the split is not computed automatically."),
     "notes": "Deliberately not auto-split in v2 (the light boundary)."},
    {"diagnostic_id": "D_5695_FRACTION", "title": "Condominium / cooperative fractional share", "severity": "warning",
     "condition": "e5695_condo_fractional is True",
     "message": ("Line 32b is checked: a fractional share of the improvements in a condominium or "
                 "cooperative. Only your share of the cost qualifies — the allocation is not computed "
                 "automatically, so verify the amounts entered are already your share."),
     "notes": "Deferred edge case, same family as D_5695_JOINT."},
]

E_SCENARIOS: list[dict] = [
    {"scenario_name": "E-T1 — §25D solar 30%", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"tax_year": 2025, "kind": "25d", "solar_electric": 20000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line15": 6000, "e5695_line16": 0},
     "notes": "30% × 20,000 = 6,000; ample tax → full credit, no carryforward."},
    {"scenario_name": "E-T2 — §25C windows capped $600", "scenario_type": "edge_case", "sort_order": 2,
     "inputs": {"tax_year": 2025, "kind": "25c", "windows": 3000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 600},
     "notes": "30% × 3,000 = 900, capped at $600 (windows)."},
    {"scenario_name": "E-T3 — §25C doors: ONE $2,000 door caps at $250, not $500", "scenario_type": "edge_case", "sort_order": 3,
     "inputs": {"tax_year": 2025, "kind": "25c", "doors_top": 2000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 250},
     "notes": ("THE v2 CORRECTION. Line 19c caps 30% × 2,000 = 600 at $250 for the most expensive door; "
               "19h = min(250 + 0, 500) = 250. v1's min(30%×doors, 500) answered 500 — a $250 overstatement "
               "on the commonest doors fact pattern there is (one replaced front door)."),
     },
    {"scenario_name": "E-T4 — §25C $1,200 aggregate cap", "scenario_type": "edge_case", "sort_order": 4,
     "inputs": {"tax_year": 2025, "kind": "25c", "insulation": 5000, "windows": 3000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 1200},
     "notes": "insulation 1,500 + windows min(900,600)=600 → 2,100, capped at $1,200."},
    {"scenario_name": "E-T5 — §25C heat pump separate $2,000", "scenario_type": "edge_case", "sort_order": 5,
     "inputs": {"tax_year": 2025, "kind": "25c", "heat_pump_biomass": 10000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 2000},
     "notes": "30% × 10,000 = 3,000, capped at the separate $2,000 group."},
    {"scenario_name": "E-T6 — §25C annual max $3,200", "scenario_type": "edge_case", "sort_order": 6,
     "inputs": {"tax_year": 2025, "kind": "25c", "insulation": 10000, "heat_pump_biomass": 10000, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 3200},
     "notes": "min(3,000 insulation, 1,200) + min(3,000 heat-pump, 2,000) = 1,200 + 2,000 = 3,200."},
    {"scenario_name": "E-T7 — §25D fuel cell cap", "scenario_type": "edge_case", "sort_order": 7,
     "inputs": {"tax_year": 2025, "kind": "25d", "fuel_cell_cost": 10000, "fuel_cell_kw": 2.0, "tax_limit": 100000},
     "expected_outputs": {"e5695_line15": 2000, "e5695_line16": 0},
     "notes": "min(30%×10,000=3,000, $1,000×2kW=2,000) = 2,000."},
    {"scenario_name": "E-T8 — §25D tax-limited → carryforward", "scenario_type": "edge_case", "sort_order": 8,
     "inputs": {"tax_year": 2025, "kind": "25d", "solar_electric": 20000, "tax_limit": 4000},
     "expected_outputs": {"e5695_line15": 4000, "e5695_line16": 2000},
     "notes": "credit 6,000, tax limit 4,000 → line 15 = 4,000; line 16 carryforward = 2,000."},
    {"scenario_name": "E-G1 — TY2026 terminated → RED", "scenario_type": "diagnostic", "sort_order": 9,
     "inputs": {"tax_year": 2026, "kind": "25c", "windows": 3000},
     "expected_outputs": {"D_5695_2026": True},
     "notes": "OBBBA termination → D_5695_2026 (credit not computed for 2026)."},

    # ── v2 scenarios ──
    {"scenario_name": "E-T9 — §25C doors: the $250 door plus others, aggregate $500", "scenario_type": "edge_case", "sort_order": 10,
     "inputs": {"tax_year": 2025, "kind": "25c", "doors_top": 1200, "doors": 1500, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 500},
     "notes": "19c = min(360,250) = 250; 19g = 30%×1,500 = 450; 19h = min(700,500) = 500 (the aggregate bites)."},
    {"scenario_name": "E-T10 — §25C doors: both boxes under every cap", "scenario_type": "normal", "sort_order": 11,
     "inputs": {"tax_year": 2025, "kind": "25c", "doors_top": 700, "doors": 300, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 300},
     "notes": "19c = min(210,250) = 210; 19g = 90; 19h = min(300,500) = 300 — no cap applies."},
    {"scenario_name": "E-G2 — line 17a No → the whole of Section A is denied", "scenario_type": "diagnostic", "sort_order": 12,
     "inputs": {"tax_year": 2025, "kind": "25c", "insulation": 5000, "windows": 3000, "doors_top": 1000,
                "section_a": False, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 0, "D_5695_GATE_NO": True},
     "notes": "Face: 'If you checked the No box for line 17a, 17b, or 17c... Do not complete Part II, Section A.'"},
    {"scenario_name": "E-G3 — line 21a No → energy property AND the heat pump are denied, the audit survives",
     "scenario_type": "diagnostic", "sort_order": 13,
     "inputs": {"tax_year": 2025, "kind": "25c", "central_ac": 4000, "heat_pump_biomass": 10000,
                "home_audit": 500, "section_b": False, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 150, "D_5695_GATE_NO": True},
     "notes": ("Face: 'Skip lines 22 through 25 and line 29. Go to line 26.' — line 29 (the $2,000 heat "
               "pump group) is inside the skip, which is the easy one to miss; only the audit's "
               "min(30%×500,150) = 150 remains."),
     },
    {"scenario_name": "E-G4 — line 5a No → the battery cost is dropped from §25D", "scenario_type": "diagnostic", "sort_order": 14,
     "inputs": {"tax_year": 2025, "kind": "25d", "solar_electric": 20000, "battery": 10000,
                "battery_ge_3kwh": False, "tax_limit": 100000},
     "expected_outputs": {"e5695_line15": 6000, "e5695_line16": 0, "D_5695_GATE_NO": True},
     "notes": "30% × 20,000 solar only = 6,000; the 10,000 battery is excluded from line 6a."},
    {"scenario_name": "E-G5 — line 26a No → no home energy audit credit", "scenario_type": "diagnostic", "sort_order": 15,
     "inputs": {"tax_year": 2025, "kind": "25c", "home_audit": 500, "audit_ok": False, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 0, "D_5695_GATE_NO": True},
     "notes": "Face: 'If you checked the No box, you cannot claim the home energy audit credit.'"},
    {"scenario_name": "E-G6 — line 25a No → no enabling-property (panelboard) credit", "scenario_type": "diagnostic", "sort_order": 16,
     "inputs": {"tax_year": 2025, "kind": "25c", "panelboard": 4000, "enabling": False, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 0, "D_5695_GATE_NO": True},
     "notes": "Face: 'Skip lines 25b through 25e.' The $600 panelboard credit is denied."},
    {"scenario_name": "E-G7 — a §25C cost with no QM ID number", "scenario_type": "diagnostic", "sort_order": 17,
     "inputs": {"tax_year": 2025, "kind": "25c", "windows": 3000, "pin_windows": "", "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 600, "D_5695_QM_PIN": True},
     "notes": ("§25C(h): the credit is computed but flagged — the IRS disallows an item whose QM ID "
               "number is not on the return for property placed in service after 12/31/2024."),
     },
    {"scenario_name": "E-G8 — costs entered, eligibility question still blank", "scenario_type": "diagnostic", "sort_order": 18,
     "inputs": {"tax_year": 2025, "kind": "25c", "windows": 3000, "section_a": None, "tax_limit": 100000},
     "expected_outputs": {"e5695_line32": 600, "D_5695_GATE_OPEN": True},
     "notes": "Unanswered is NOT a No — the credit stands and the blank is surfaced (R-5695-GATE)."},
]

E_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-5695-25D", "IRC_25D", "primary", "§25D 30% + carryforward"),
    ("R-5695-25D", "IRS_2025_F5695_INSTR", "secondary", "Part I lines 1-16"),
    ("R-5695-25C", "IRC_25C", "primary", "§25C(b) the caps"),
    ("R-5695-25C", "IRS_2025_F5695_INSTR", "secondary", "Part II lines 17-32"),
    ("R-5695-LIMIT", "IRS_2025_F5695_INSTR", "primary", "The Credit Limit Worksheet"),
    ("R-5695-TERM", "IRC_25D", "primary", "OBBBA §70506 termination"),
    ("R-5695-TERM", "IRC_25C", "secondary", "OBBBA §70505 termination"),
    ("R-5695-GATE", "IRS_2025_F5695_INSTR", "primary", "The face's own skip/deny directions (5a, 7a, 17a-c, 21a-b, 25a, 26a)"),
    ("R-5695-QMPIN", "IRC_25C", "primary", "§25C(h) qualified product identification number"),
    ("R-5695-QMPIN", "IRS_2025_F5695_INSTR", "secondary", "The PIN boxes on lines 19b/20a/22a/23a/24a/25d/29a-e"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-1040-5695-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "§25D 30% + the fuel-cell $500/½kW cap",
     "description": "Validates R-5695-25D. Bug it catches: the wrong clean-energy rate, or the fuel-cell capacity cap not applied.",
     "definition": {"kind": "formula_check", "form": "FORM_5695",
                    "formula": "l6b = 0.30×Σcosts; fuel = min(0.30×cost, 1000×kW)"},
     "sort_order": 1},
    {"assertion_id": "FA-1040-5695-02", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "§25C sub-caps + the $1,200 aggregate + the $2,000 heat-pump group",
     "description": "Validates R-5695-25C. Bug it catches: a missing sub-cap (windows $600 / doors $500 / item $600 / audit $150), the $1,200 aggregate not applied, or the $2,000 group not separate.",
     "definition": {"kind": "formula_check", "form": "FORM_5695",
                    "formula": "min(envelope+property,1200) + min(0.30×heatpump,2000); item caps 600/500/600/150"},
     "sort_order": 2},
    {"assertion_id": "FA-1040-5695-03", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "§25D tax-liability limit + the carryforward to 2026",
     "description": "Validates R-5695-25D + R-5695-LIMIT. Bug it catches: the tax limit not applied, or line 16 carryforward ≠ line 13 − line 15.",
     "definition": {"kind": "formula_check", "form": "FORM_5695",
                    "formula": "l15 = min(l13, tax_limit); l16 = l13 − l15"},
     "sort_order": 3},
    {"assertion_id": "FA-1040-5695-04", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "§25D → Sch 3 line 5a; §25C → Sch 3 line 5b",
     "description": "Validates the flow targets. Bug it catches: a credit landing on the wrong Schedule 3 line (5a vs 5b swapped).",
     "definition": {"kind": "flow_assertion", "form": "FORM_5695",
                    "checks": [{"source_line": "l15", "must_write_to": ["SCH_3.5a"]},
                               {"source_line": "l32", "must_write_to": ["SCH_3.5b"]}]},
     "sort_order": 4},
    {"assertion_id": "FA-1040-5695-05", "assertion_type": "reconciliation", "entity_types": ["1040"],
     "title": "§25C total = the $1,200 group + the $2,000 group, tax-limited",
     "description": "Validates R-5695-25C. Bug it catches: the two groups not summed, or the $2,000 heat-pump credit folded into the $1,200 cap.",
     "definition": {"kind": "reconciliation", "form": "FORM_5695",
                    "formula": "l32 = min(min(envelope+property,1200) + min(0.30×heatpump,2000), tax_limit)"},
     "sort_order": 5},
    {"assertion_id": "FA-1040-5695-06", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Gates — OBBBA TY2026 termination RED; §25C no carryforward",
     "description": "Validates R-5695-TERM. Bug it catches: the credit computed for 2026, or §25C excess wrongly carried forward.",
     "definition": {"kind": "gating_check", "form": "FORM_5695", "expect": {"red_fires": True},
                    "blockers": ["obbba_terminated_2026"]},
     "sort_order": 6},
    {"assertion_id": "FA-1040-5695-07", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Doors — the most expensive door caps at $250 before the $500 aggregate",
     "description": ("Validates R-5695-25C's doors arithmetic. Bug it catches: the pre-v2 shape "
                     "min(30%×all_doors, 500), which overstates a single expensive door by up to $250."),
     "definition": {"kind": "formula_check", "form": "FORM_5695",
                    "formula": "l19c = min(0.30×doors_top, 250); l19h = min(l19c + 0.30×doors_other, 500)"},
     "sort_order": 7},
    {"assertion_id": "FA-1040-5695-08", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The eligibility gates deny exactly the branch the face skips",
     "description": ("Validates R-5695-GATE. Bugs it catches: a 21a/21b No that fails to skip LINE 29 "
                     "(the $2,000 heat-pump group sits outside lines 22-25 and is easy to miss), a 17a-c "
                     "No that leaves Section A standing, and — the other direction — an UNANSWERED gate "
                     "being treated as a No and silently deleting a credit."),
     "definition": {"kind": "gating_check", "form": "FORM_5695",
                    "expect": {"denies_only_named_branch": True, "null_never_denies": True},
                    "blockers": ["l5a_no", "l7a_no", "l17a_c_no", "l21a_b_no", "l25a_no", "l26a_no"]},
     "sort_order": 8},
]


FORMS: list[dict] = [
    {"identity": E_IDENTITY, "facts": E_FACTS, "rules": E_RULES, "lines": E_LINES,
     "diagnostics": E_DIAGNOSTICS, "scenarios": E_SCENARIOS, "rule_links": E_RULE_LINKS},
]


class Command(BaseCommand):
    help = "Load the FORM_5695 spec (Residential Energy Credits). Refuses until READY_TO_SEED=True."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING("\nLoad FORM_5695 spec (Residential Energy Credits)\n"))
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
                "\nREFUSING TO SEED FORM_5695: not cleared to seed.\n\n"
                "Gated until Ken's review walk (the §25D/§25C caps + the carryforward\n"
                "+ the tax-liability limit + the OBBBA termination).\n\n"
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
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _load_new_excerpts_on_existing(self, sources):
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if src:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc)

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
        form = TaxForm.objects.filter(form_number="FORM_5695").first()
        if form:
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("FORM_5695: all rules cited" if not uncited
                              else self.style.WARNING(f"FORM_5695 uncited rules: {len(uncited)}"))
