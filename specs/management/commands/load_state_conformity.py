"""Load the STATE CONFORMITY spine — one JurisdictionConformitySource row per state-year.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
The single writer of `JurisdictionConformitySource`. One row per (state, tax year),
enforced by a unique constraint (migration sources.0006). Every module spec for a state
— individual / 1065 / 1120S / 1120 / 1041 — exports THIS row as the package's
`state_conformity` block, instead of each loader re-deriving the state's posture in prose.

Authored for the 45-state campaign (Tax Shelter Future D-030, delvio-states D-8). Going
forward the conformity row for a new state is authored FIRST, before any of that state's
form specs; the per-form loaders then reuse its AuthoritySource rows via
EXISTING_SOURCES_TO_REFERENCE.

═══════════════════════════════════════════════════════════════════════════
WHY THIS EXISTS (the gap it closes)
═══════════════════════════════════════════════════════════════════════════
Before this loader, GA/2025 was the ONLY conformity row in the DB — written inline by
`load_remaining_1120s.py`. SC, AL and NC had no row at all, so every SC/AL/NC spec package
exported `"state_conformity": null` and the downstream consumer (delvio-tax) saw no
structured conformity for three of the four built states. Their conformity was encoded
only as AuthoritySource rows + FormRules + loader prose — real and Gate-1-verified, but
not machine-readable at the package level.

The GA row's inline creation is REMOVED from `load_remaining_1120s.py` in the same commit:
two writers of one row is the reconstructability hazard the 2026-07-05 delta audit was
about. This loader is the only writer.

═══════════════════════════════════════════════════════════════════════════
PROVENANCE — no new tax research (important)
═══════════════════════════════════════════════════════════════════════════
Every figure and characterization below is TRANSCRIBED from the already-Gate-1-approved
state loaders in this repo and cited to the SAME AuthoritySource rows those loaders seed.
Nothing here is authored from memory, and nothing extends scope:

  GA  ← load_remaining_1120s.py (the row this replaces, verbatim) + DECISIONS D-8
  SC  ← load_sc1040.py W1/W5 + SC_ACT63_2025_CONFORMITY excerpt + DECISIONS D-6
  AL  ← load_al_form20c.py W5 + AL_CODE_40_18 excerpt (§40-18-1.1) + DECISIONS D-14
  NC  ← load_nc_d400.py W2/W3 + NC_GS_105_153_6 + D-401 booklet p.17 + DECISIONS D-7

Per the Authoritative-Source Rule this is a RESTRUCTURING of verified content, not new
authoring. It still crosses Gate 1 because it changes what the export endpoints serve.

⚠ TY-KEYED. Every row is TY2025. A new tax year staleness-invalidates all of them until
re-verified against that year's DOR sources — conformity dates move (SC's is a rolling
legislative act; NC's freeze date has been advanced repeatedly).

═══════════════════════════════════════════════════════════════════════════
CANONICAL decoupled_items SHAPE (campaign D-8)
═══════════════════════════════════════════════════════════════════════════
    {item, federal_treatment, state_treatment, authority_source_code, notes}

The model docstring previously documented a 5-key shape while the only real row used a
2-key {item, treatment}. Normalized here to the 5-key shape, with `authority_source_code`
(the AuthoritySource.source_code STRING) rather than the documented `authority_source_id`
— UUIDs differ per environment and the rest of the export package resolves authority by
code. delvio-tax's state-registry refactor consumes this shape.

═══════════════════════════════════════════════════════════════════════════
SAFETY GUARD — READY_TO_SEED stays False until Ken approves the walk in-session.
DO NOT relax the guard to silence the error.
═══════════════════════════════════════════════════════════════════════════
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import AuthoritySource, JurisdictionConformitySource

# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False

TAX_YEAR = 2025

# ═══════════════════════════════════════════════════════════════════════════
# THE ROWS
# ═══════════════════════════════════════════════════════════════════════════
# `authority_source` is the FK anchor (the state's controlling conformity authority).
# `authority_source_code` inside each decoupled item cites the specific support.

CONFORMITY_ROWS: list[dict] = [
    # ── GEORGIA ────────────────────────────────────────────────────────────
    # Transcribed verbatim from load_remaining_1120s.py (the row this supersedes).
    {
        "jurisdiction_code": "GA",
        "conformity_type": "partial",
        "authority_source_code": "GA_2025_600S_INSTR",
        "federal_reference_note": (
            "IRC conformity advanced to January 1, 2026 by HB 1199, retroactive to tax years "
            "beginning on or after January 1, 2025 — so OBBBA (P.L. 119-21) IS in the GA base "
            "for TY2025, except where separately decoupled."
        ),
        "summary": (
            "Georgia partially conforms to federal tax law (IRC conformity Jan 1, 2026 via HB 1199, "
            "retroactive to TY2025). Does NOT conform to IRC 168(k)/(n) bonus depreciation (full "
            "addback). DOES conform to the OBBBA Section 179 limit: $2,500,000/$4,000,000, equal to "
            "federal. PTET at 5.19% (TY2025) is elective."
        ),
        "decoupled_items": [
            {
                "item": "IRC §168(k)/(n) bonus depreciation",
                "federal_treatment": "100% bonus for property acquired and placed in service after 1/19/2025 (OBBBA, permanent).",
                "state_treatment": "NOT adopted — full add-back required on GA Schedule 1; GA basis recovers over the asset life.",
                "authority_source_code": "GA_2025_600S_INSTR",
                "notes": "The GA add-back is separate from §179 — GA conforms to §179 but not to bonus.",
            },
            {
                "item": "IRC §179 expensing limits",
                "federal_treatment": "$2,500,000 limit / $4,000,000 phaseout (OBBBA).",
                "state_treatment": "CONFORMS — same $2,500,000 / $4,000,000 via HB 1199, retroactive to TY2025.",
                "authority_source_code": "GA_2025_600S_INSTR",
                "notes": (
                    "HB 1199 supersedes both HB 290 (Jan 1 2025 conformity) and the Aug-2025 GA Form 4562, "
                    "which still printed the pre-OBBBA figure. Ken-ruled 2026-07-06."
                ),
            },
        ],
        "notes": (
            "Home state; all five module specs seeded. PTET is elective at 5.19% (TY2025) and is "
            "IRREVOCABLE for the year — do not treat other states' PTET regimes as GA clones."
        ),
    },
    # ── SOUTH CAROLINA ─────────────────────────────────────────────────────
    # Source: load_sc1040.py W1/W5 + the SC_ACT63_2025_CONFORMITY excerpt.
    {
        "jurisdiction_code": "SC",
        "conformity_type": "static",
        "authority_source_code": "SC_ACT63_2025_CONFORMITY",
        "federal_reference_note": (
            "IRC as amended through December 31, 2024 (SC Code §12-6-40(A)(1), as amended by Act 63 "
            "of 2025 / S.507, signed 5/22/2025). The conformity date PREDATES OBBBA (signed 7/4/2025), "
            "so SC did NOT adopt OBBBA for TY2025. §12-6-40(A)(1)(c) extends IRC sections that expired "
            "12/31/2024 and were extended (not otherwise amended) by Congress during 2025."
        ),
        "summary": (
            "South Carolina is a STATIC-date conformity state: the IRC as amended through 12/31/2024. "
            "OBBBA is NOT adopted for TY2025. §12-6-50 lists the non-adopted IRC sections — including "
            "§168(k) bonus depreciation, §163(j), and §199A. §179 is NOT on that list, so SC conforms "
            "to §179 at the 12/31/2024 level (pre-OBBBA $1,250,000 / $3,130,000)."
        ),
        "decoupled_items": [
            {
                "item": "IRC §168(k) bonus depreciation",
                "federal_treatment": "100% bonus for property acquired and placed in service after 1/19/2025 (OBBBA, permanent).",
                "state_treatment": "NOT adopted (§12-6-50) — add back federal depreciation minus depreciation-without-bonus in the placed-in-service year; SC recovers the difference over the asset life, with a basis-difference adjustment on disposition.",
                "authority_source_code": "SC_ACT63_2025_CONFORMITY",
                "notes": "Computed on SC1040 line e; the later-year SC subtraction rides line v. See SC_RR_05_2_DEPR.",
            },
            {
                "item": "IRC §179 expensing limits",
                "federal_treatment": "$2,500,000 limit / $4,000,000 phaseout (OBBBA).",
                "state_treatment": "Conforms at the 12/31/2024 IRC level: $1,250,000 limit / $3,130,000 phaseout (pre-OBBBA, Rev. Proc. 2024-40). The §179 excess is added back and recovered over the asset life.",
                "authority_source_code": "SC_ACT63_2025_CONFORMITY",
                "notes": (
                    "§179 is NOT on the §12-6-50 non-adopted list, so it conforms — but at the FROZEN "
                    "date, not to OBBBA. Ken (depreciation CPA) confirmed the figures 2026-07-04. "
                    "Do NOT cross-apply the federal/GA $2.5M figure."
                ),
            },
            {
                "item": "IRC §163(j) business interest limitation",
                "federal_treatment": "30% of ATI limitation on business interest, EBITDA basis for TY2025.",
                "state_treatment": "NOT adopted (§12-6-50).",
                "authority_source_code": "SC_ACT63_2025_CONFORMITY",
                "notes": "Listed among the non-adopted sections; not modeled in the SC1040 v1 spec.",
            },
            {
                "item": "IRC §199A qualified business income deduction",
                "federal_treatment": "20% QBI deduction.",
                "state_treatment": "NOT adopted (§12-6-50).",
                "authority_source_code": "SC_ACT63_2025_CONFORMITY",
                "notes": "SC starts from federal TAXABLE income, so a non-adopted §199A is an addition item.",
            },
        ],
        "notes": (
            "⚠ MID-CHANGE RISK (SC1040 W5): a 2026 SC session could retroactively adopt parts of OBBBA "
            "— re-verify next season. A possible SC DOR information letter (~1/30/2026) on OBBBA "
            "non-conformity was referenced by a secondary source but NOT verified; pull it if it exists. "
            "PTET: 3% active-trade-or-business election (I-335), annual and non-binding, owner-side "
            "EXCLUSION — NOT a GA-style credit."
        ),
    },
    # ── ALABAMA ────────────────────────────────────────────────────────────
    # Source: load_al_form20c.py W5 + the AL_CODE_40_18 excerpt (§40-18-1.1).
    {
        "jurisdiction_code": "AL",
        "conformity_type": "rolling",
        "authority_source_code": "AL_CODE_40_18",
        "federal_reference_note": (
            "Code of Ala. §40-18-1.1 defines the IRC as amended and in effect — ROLLING conformity, "
            "so OBBBA flows through automatically for TY2025 without legislative action."
        ),
        "summary": (
            "Alabama is a ROLLING conformity state — the opposite posture from GA, SC and NC. It "
            "CONFORMS to both §168(k) bonus depreciation and §179 (so AL §179 = $2,500,000/$4,000,000 "
            "for 2025, following OBBBA), and there is NO general depreciation add-back. The decouples "
            "are GILTI (§40-18-35.2) and §174 R&E (§40-18-62). Alabama's signature individual feature "
            "is the FEDERAL INCOME TAX DEDUCTION, constitutionally protected by Amendment 662."
        ),
        "decoupled_items": [
            {
                "item": "GILTI (IRC §951A)",
                "federal_treatment": "GILTI included in income with the §250 deduction.",
                "state_treatment": "DECOUPLED — Code of Ala. §40-18-35.2; the §250 FDII/GILTI deduction is added back on Form 20C Schedule A line 9.",
                "authority_source_code": "AL_CODE_40_18",
                "notes": "C-corp lane; see load_al_form20c.py.",
            },
            {
                "item": "IRC §174 research & experimental expenditures",
                "federal_treatment": "Federal amortization of R&E under §174.",
                "state_treatment": "DECOUPLED — Code of Ala. §40-18-62; the federally-amortized R&E is added back on Form 20C Schedule A line 10.",
                "authority_source_code": "AL_CODE_40_18",
                "notes": "C-corp lane.",
            },
            {
                "item": "2008 Economic Stimulus Act basis difference (legacy)",
                "federal_treatment": "Bonus depreciation allowed under the 2008 Economic Stimulus Act.",
                "state_treatment": "The ONLY legacy depreciation decouple that survives — a residual basis difference reported on Form 20C Schedule A line 21.",
                "authority_source_code": "AL_2025_20C_INSTR",
                "notes": "Legacy only. Does NOT create a current-year §168(k)/§179 add-back for 2025 assets.",
            },
        ],
        "notes": (
            "⚠ AL is the counter-example that keeps the campaign honest: an add-back that is mandatory "
            "in GA/SC/NC is WRONG in AL. D_AL20C_DEPR exists to say so explicitly. PTET: 5% on Form EPT, "
            "owner-side REFUNDABLE CREDIT via Schedule EPT-C (Act 2021-1)."
        ),
    },
    # ── NORTH CAROLINA ─────────────────────────────────────────────────────
    # Source: load_nc_d400.py W2/W3 + NC_GS_105_153_6 + the D-401 booklet p.17.
    {
        "jurisdiction_code": "NC",
        "conformity_type": "static",
        "authority_source_code": "NC_GS_105_153_6",
        "federal_reference_note": (
            "IRC conformity FROZEN at January 1, 2023 (D-401 booklet p.17). OBBBA does NOT apply for "
            "TY2025. The booklet warns to check the Department's website for conformity updates."
        ),
        "summary": (
            "North Carolina is a STATIC-date conformity state frozen at January 1, 2023. It adopted "
            "neither §168(k)/(n) bonus depreciation nor the increased §179, and handles the difference "
            "through an 85% ADD-BACK mechanism on D-400 Schedule S Part A, recovered at 20% per year "
            "over the following five years. NC's own §179 limits are $25,000 / $200,000."
        ),
        "decoupled_items": [
            {
                "item": "IRC §168(k)/(n) bonus depreciation",
                "federal_treatment": "100% bonus for property acquired and placed in service after 1/19/2025 (OBBBA, permanent).",
                "state_treatment": "NOT adopted — 85% of the federal bonus deduction is added back (D-400 Schedule S Part A line 3), then recovered at 20% per year over the FOLLOWING five tax years.",
                "authority_source_code": "NC_GS_105_153_6",
                "notes": "A TY2025 add-back first recovers on the TY2026 return. The 20% prior-year (2020-2024) installments are direct-entry — they need historical records the spec cannot reach.",
            },
            {
                "item": "IRC §179 expensing limits",
                "federal_treatment": "$2,500,000 limit / $4,000,000 phaseout (OBBBA).",
                "state_treatment": "NC limits are $25,000 / $200,000. 85% of the §179 excess over the NC limits is added back (Schedule S Part A line 4), recovered at 20% per year over the following five years.",
                "authority_source_code": "NC_GS_105_153_6",
                "notes": "Year-keyed; booklet p.17. nc_sec179 = min(federal §179, $25,000), with a phaseout flag at $200,000.",
            },
        ],
        "notes": (
            "The 85%/20%-over-five-years mechanism is NC-specific — it is neither GA's full add-back nor "
            "SC's life-recovery. PTET: 4.25% Taxed PTE election, owner-side DEDUCTION via NC-PE. "
            "NC's corporate lane (CD-405) carries a separate net-worth franchise tax."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed the per-state JurisdictionConformitySource spine (one row per state-year)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would be written without touching the DB (bypasses the seed guard).",
        )

    @transaction.atomic
    def handle(self, *_args, **opts):
        dry_run = opts["dry_run"]

        if not dry_run and not READY_TO_SEED:
            raise CommandError(
                "READY_TO_SEED is False — this loader is gated behind Gate 1.\n"
                "Ken must approve the conformity spine walk in-session before it seeds.\n"
                "Use --dry-run to inspect the planned rows. DO NOT relax the guard to silence this."
            )

        written = 0
        for row in CONFORMITY_ROWS:
            code = row["authority_source_code"]
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src is None:
                # A missing anchor means the state's own loader has not run — on a fresh
                # rebuild that is an ordering fault worth surfacing, not swallowing.
                self.stdout.write(self.style.WARNING(
                    f"  {row['jurisdiction_code']}: authority source {code} not found — "
                    f"row will be written with a null FK (run the state's loader first)."
                ))

            # Every cited source_code inside decoupled_items should also resolve.
            for item in row["decoupled_items"]:
                item_code = item.get("authority_source_code")
                if item_code and not AuthoritySource.objects.filter(source_code=item_code).exists():
                    self.stdout.write(self.style.WARNING(
                        f"  {row['jurisdiction_code']}: decoupled item cites unknown source {item_code}"
                    ))

            if dry_run:
                self.stdout.write(
                    f"  [dry-run] {row['jurisdiction_code']} TY{TAX_YEAR} "
                    f"({row['conformity_type']}, {len(row['decoupled_items'])} decoupled items)"
                )
                continue

            _, created = JurisdictionConformitySource.objects.update_or_create(
                jurisdiction_code=row["jurisdiction_code"], tax_year=TAX_YEAR,
                defaults={
                    "conformity_type": row["conformity_type"],
                    "authority_source": src,
                    "federal_reference_note": row["federal_reference_note"],
                    "summary": row["summary"],
                    "decoupled_items": row["decoupled_items"],
                    "notes": row["notes"],
                },
            )
            written += 1
            verb = "created" if created else "updated"
            self.stdout.write(
                f"  {row['jurisdiction_code']} TY{TAX_YEAR} {verb} "
                f"({row['conformity_type']}, {len(row['decoupled_items'])} decoupled items)"
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"Dry run — {len(CONFORMITY_ROWS)} rows planned, nothing written."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"State conformity spine seeded: {written} rows."
            ))
