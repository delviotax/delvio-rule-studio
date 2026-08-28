"""Authority source models — the knowledge base that grounds every rule in cited law."""
import uuid

from django.db import models


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceType(models.TextChoices):
    CODE_SECTION = "code_section", "IRC Section"
    REGULATION = "regulation", "Treasury Regulation"
    # ── Added 2026-08-27 (Ken, direct: "add case_law and irs_internal_procedure") ──
    # Found by the D-41 enum ratchet catching a seeding attempt of mine: the vocabulary covered
    # IRS-issued documents, state-issued documents and our own internal notes, and had NO slot for
    # a judicial decision or for the IRM. Haggar Co. v. Helvering (308 U.S. 389) and IRM 21.6.7.4.10
    # were seeded as OFFICIAL_PUBLICATION, a stated misfit — calling a Supreme Court holding an
    # "IRS Publication" is the quiet overstatement D-39 corrected in the other direction. Expect
    # more case law as the state campaign deepens.
    CASE_LAW = "case_law", "Case Law"
    IRS_INTERNAL_PROCEDURE = "irs_internal_procedure", "IRS Internal Procedure (IRM)"
    OFFICIAL_FORM = "official_form", "Official Form"
    OFFICIAL_INSTRUCTION = "official_instruction", "Form Instructions"
    OFFICIAL_PUBLICATION = "official_publication", "IRS Publication"
    OFFICIAL_NOTICE = "official_notice", "IRS Notice"
    OFFICIAL_REVENUE_RULING = "official_revenue_ruling", "Revenue Ruling"
    OFFICIAL_REVENUE_PROCEDURE = "official_revenue_procedure", "Revenue Procedure"
    MEF_SCHEMA = "mef_schema", "MeF XML Schema"
    MEF_BUSINESS_RULE = "mef_business_rule", "MeF Business Rule"
    MEF_RELEASE_MEMO = "mef_release_memo", "MeF Release Memo"
    STATE_STATUTE = "state_statute", "State Statute"
    STATE_REGULATION = "state_regulation", "State Regulation"
    STATE_FORM = "state_form", "State Form"
    STATE_INSTRUCTION = "state_instruction", "State Instructions"
    STATE_EFILE_SPEC = "state_efile_spec", "State E-File Spec"
    STATE_VENDOR_GUIDE = "state_vendor_guide", "State Vendor Guide"
    STATE_CONFORMITY_NOTICE = "state_conformity_notice", "State Conformity Notice"
    INTERNAL_MEMO = "internal_memo", "Internal Memo"
    INTERNAL_EXAMPLE = "internal_example", "Worked Example"
    INTERNAL_TEST_CASE = "internal_test_case", "Internal Test Case"


class SourceRank(models.TextChoices):
    CONTROLLING = "controlling", "Controlling"
    PRIMARY_OFFICIAL = "primary_official", "Primary Official"
    IMPLEMENTATION_OFFICIAL = "implementation_official", "Implementation Official"
    INTERNAL_INTERPRETATION = "internal_interpretation", "Internal Interpretation"
    REFERENCE_ONLY = "reference_only", "Reference Only"


class SourceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUPERSEDED = "superseded", "Superseded"
    DRAFT = "draft", "Draft"
    ARCHIVED = "archived", "Archived"


class LinkType(models.TextChoices):
    GOVERNS = "governs", "Governs"
    INFORMS = "informs", "Informs"
    VALIDATES = "validates", "Validates"
    MAPPING_ONLY = "mapping_only", "Mapping Only"
    OVERRIDES = "overrides", "Overrides"


class SupportLevel(models.TextChoices):
    PRIMARY = "primary", "Primary"
    SECONDARY = "secondary", "Secondary"
    INTERPRETIVE = "interpretive", "Interpretive"
    IMPLEMENTATION = "implementation", "Implementation"


class ConformityType(models.TextChoices):
    ROLLING = "rolling", "Rolling"
    STATIC = "static", "Static"
    PARTIAL = "partial", "Partial"
    DECOUPLED = "decoupled", "Decoupled"


class FeedType(models.TextChoices):
    HTML_INDEX = "html_index", "HTML Index"
    PDF_LIST = "pdf_list", "PDF List"
    XML_REPO = "xml_repo", "XML Repository"
    MANUAL_UPLOAD = "manual_upload", "Manual Upload"
    # Added 2026-08-05 with the Phase-0 detection build.
    JSON_API = "json_api", "JSON API"                    # eCFR, Federal Register, CourtListener
    HTML_PAGE = "html_page", "HTML Page (diff)"          # state DOR pages — whole-page checksum/diff
    DIRECTORY_INDEX = "directory_index", "Directory Index"  # irs-drop / irs-dft file listings


class ItemKind(models.TextChoices):
    """What KIND of publication a change-register item represents.

    Set by the detection arms so the digest can group ("3 Rev. Procs, 1 CFR amendment,
    12 draft forms") instead of showing an undifferentiated list. Nullable: the pre-2026-08
    arms (federal_register / irb) predate this field and their historical rows stay null.
    """
    REV_PROC = "rev_proc", "Revenue Procedure"
    NOTICE = "notice", "Notice"
    REV_RUL = "rev_rul", "Revenue Ruling"
    ANNOUNCEMENT = "announcement", "Announcement"
    FEDERAL_REGISTER = "federal_register", "Federal Register Document"
    IRB_BULLETIN = "irb_bulletin", "IRB Bulletin"
    CFR_SECTION = "cfr_section", "26 CFR Section Amendment"
    DRAFT_FORM = "draft_form", "Draft Form/Instruction"
    FINAL_FORM = "final_form", "Final Form/Instruction"
    COURT_OPINION = "court_opinion", "Court Opinion"
    PUBLIC_LAW = "public_law", "Public Law"
    STATE_PAGE = "state_page", "State DOR Page Change"


class ChangeStatus(models.TextChoices):
    """Lifecycle of a change-register item flowing toward a WORK_ORDERS INTAKE order."""
    DETECTED = "detected", "Detected"      # surfaced (manual clip or checksum diff); not yet assessed
    TRIAGED = "triaged", "Triaged"         # assessed: affected forms / tax year / substantive determined
    PROMOTED = "promoted", "Promoted"      # became a WORK_ORDERS INTAKE order (front door takes over)
    DISMISSED = "dismissed", "Dismissed"   # not substantive / no authoring action needed


class ChangeDetectionSource(models.TextChoices):
    """How a change-register item was surfaced."""
    MANUAL_CLIP = "manual_clip", "Manual Clip"        # Ken (or CC on a law change) hand-entered it
    CHECKSUM_DIFF = "checksum_diff", "Checksum Diff"  # a source's AuthorityVersion checksum moved
    FEED_POLL = "feed_poll", "Feed Poll"              # (future) automated feed polling


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AuthoritySource(models.Model):
    """Central record for a tax law source document."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_code = models.CharField(max_length=100, unique=True, help_text="e.g. IRC_1231, IRS_2025_4797_INSTR")
    source_type = models.CharField(max_length=40, choices=SourceType.choices)
    source_rank = models.CharField(max_length=30, choices=SourceRank.choices)
    jurisdiction_code = models.CharField(max_length=10, help_text="FED, GA, CA, etc.")
    tax_year_start = models.IntegerField(blank=True, null=True)
    tax_year_end = models.IntegerField(blank=True, null=True)
    entity_type_code = models.CharField(max_length=20, blank=True, null=True, help_text="1040, 1120S, shared")
    title = models.TextField()
    citation = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. IRC §1231(a)(1)")
    issuer = models.CharField(max_length=100, help_text="IRS, GA DOR, etc.")
    official_url = models.TextField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    effective_date_start = models.DateField(blank=True, null=True)
    effective_date_end = models.DateField(blank=True, null=True)
    superseded_by = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="supersedes")
    current_status = models.CharField(max_length=20, choices=SourceStatus.choices, default=SourceStatus.ACTIVE)
    checksum_sha256 = models.CharField(max_length=64, blank=True, null=True)
    is_substantive_authority = models.BooleanField(default=False)
    is_filing_authority = models.BooleanField(default=False)
    is_internal_only = models.BooleanField(default=False)
    requires_human_review = models.BooleanField(default=True)
    trust_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source_code"]

    def __str__(self):
        return f"{self.source_code}: {self.title[:80]}"


class AuthorityExcerpt(models.Model):
    """Citation-ready chunk of a source — the table the rule builder searches most."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    authority_source = models.ForeignKey(AuthoritySource, on_delete=models.CASCADE, related_name="excerpts")
    excerpt_label = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. 'Part III instructions'")
    location_reference = models.CharField(max_length=255, blank=True, null=True, help_text="Page/section/line/XML path")
    excerpt_text = models.TextField()
    summary_text = models.TextField(blank=True, null=True)
    topic_tags = models.JSONField(default=list, blank=True)
    line_or_page_start = models.CharField(max_length=50, blank=True, null=True)
    line_or_page_end = models.CharField(max_length=50, blank=True, null=True)
    effective_year_start = models.IntegerField(blank=True, null=True)
    effective_year_end = models.IntegerField(blank=True, null=True)
    is_key_excerpt = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["authority_source", "excerpt_label"]

    def __str__(self):
        label = self.excerpt_label or "Excerpt"
        return f"{self.authority_source.source_code} — {label}"


class AuthorityTopic(models.Model):
    """Hierarchical topic tag for organizing sources."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic_code = models.CharField(max_length=100, unique=True, help_text="e.g. 'depreciation', '1231'")
    topic_name = models.CharField(max_length=255)
    parent_topic = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="children")
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["topic_code"]

    def __str__(self):
        return self.topic_name


class AuthoritySourceTopic(models.Model):
    """Join table — sources ↔ topics."""

    authority_source = models.ForeignKey(AuthoritySource, on_delete=models.CASCADE, related_name="source_topics")
    authority_topic = models.ForeignKey(AuthorityTopic, on_delete=models.CASCADE, related_name="source_topics")

    class Meta:
        unique_together = [("authority_source", "authority_topic")]

    def __str__(self):
        return f"{self.authority_source.source_code} → {self.authority_topic.topic_code}"


class AuthorityFormLink(models.Model):
    """Connects sources to forms/lines."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    authority_source = models.ForeignKey(AuthoritySource, on_delete=models.CASCADE, related_name="form_links")
    form_code = models.CharField(max_length=50, help_text="e.g. '4797', 'SCH_D', 'GA_600'")
    form_part_code = models.CharField(max_length=50, blank=True, null=True)
    line_code = models.CharField(max_length=20, blank=True, null=True)
    link_type = models.CharField(max_length=20, choices=LinkType.choices)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["form_code", "line_code"]

    def __str__(self):
        return f"{self.authority_source.source_code} → {self.form_code} ({self.link_type})"


class RuleAuthorityLink(models.Model):
    """Connects rules to their supporting authority sources."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_rule = models.ForeignKey("specs.FormRule", on_delete=models.CASCADE, related_name="authority_links")
    authority_source = models.ForeignKey(AuthoritySource, on_delete=models.CASCADE, related_name="rule_links")
    authority_excerpt = models.ForeignKey(
        AuthorityExcerpt, on_delete=models.SET_NULL, blank=True, null=True, related_name="rule_links",
    )
    support_level = models.CharField(max_length=20, choices=SupportLevel.choices)
    relevance_note = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.form_rule.rule_id} ← {self.authority_source.source_code} ({self.support_level})"


class AuthorityVersion(models.Model):
    """Tracks source versions over time — MeF materials can have multiple per filing season."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    authority_source = models.ForeignKey(AuthoritySource, on_delete=models.CASCADE, related_name="versions")
    version_label = models.CharField(max_length=100, help_text="e.g. 'TY2025 v3.0'")
    version_date = models.DateField(blank=True, null=True)
    retrieval_url = models.TextField(blank=True, null=True)
    retrieval_timestamp = models.DateTimeField(blank=True, null=True)
    file_type = models.CharField(max_length=20, help_text="pdf, html, xml, zip, json")
    file_path = models.TextField(blank=True, null=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_date", "-created_at"]

    def __str__(self):
        return f"{self.authority_source.source_code} — {self.version_label}"


class JurisdictionConformitySource(models.Model):
    """State conformity tracking with proper authority citations.

    ONE row per (jurisdiction_code, tax_year) — enforced by the unique constraint below.
    This row is the SHARED conformity spine for a state: every module spec for that state
    (individual / 1065 / 1120S / 1120 / 1041) exports the same block, rather than each
    loader re-deriving the state's posture in prose. `_build_export` in specs/views.py
    attaches it as the package's `state_conformity`.

    The 45-state campaign (Tax Shelter Future D-030) authors this row FIRST for each new
    state, before any of that state's form specs — see delvio-states/CLAUDE.md.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jurisdiction_code = models.CharField(max_length=10, help_text="GA, CA, etc.")
    tax_year = models.IntegerField()
    federal_reference_note = models.TextField(blank=True, null=True)
    conformity_type = models.CharField(max_length=20, choices=ConformityType.choices)
    authority_source = models.ForeignKey(
        AuthoritySource, on_delete=models.SET_NULL, blank=True, null=True, related_name="conformity_records",
    )
    summary = models.TextField(blank=True, null=True)
    decoupled_items = models.JSONField(
        default=list, blank=True,
        help_text=(
            "Structured list of items where the state diverges from federal. Canonical entry shape "
            "(normalized 2026-08-05 — campaign D-8): "
            "{item, federal_treatment, state_treatment, authority_source_code, notes}. "
            "`authority_source_code` is the AuthoritySource.source_code string, NOT a UUID — "
            "UUIDs differ per environment and the downstream consumer (delvio-tax) resolves "
            "authority by code everywhere else in the export package."
        ),
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["jurisdiction_code", "tax_year"]
        verbose_name_plural = "jurisdiction conformity sources"
        constraints = [
            models.UniqueConstraint(
                fields=["jurisdiction_code", "tax_year"],
                name="uniq_conformity_jurisdiction_taxyear",
            ),
        ]

    def __str__(self):
        return f"{self.jurisdiction_code} TY{self.tax_year} ({self.conformity_type})"


class SourceFeedDefinition(models.Model):
    """Where to pull source updates from.

    Originally documentation-only ("where to look"). Since 2026-08-05 these rows also DRIVE the
    detection arms: `arm_command` names the owning management command, `selector_config` carries
    per-feed parser knobs, and the `last_*` fields hold poll state (so a page-diff arm can say what
    changed, and `change_digest` can report which arms ran and which parsed nothing).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_code = models.CharField(max_length=100, unique=True)
    feed_name = models.CharField(max_length=255)
    jurisdiction_code = models.CharField(max_length=10)
    source_family = models.CharField(max_length=50, help_text="IRS_FORMS, IRS_MEF, GA_FORMS, etc.")
    base_url = models.TextField(blank=True, null=True)
    feed_type = models.CharField(max_length=20, choices=FeedType.choices)
    refresh_frequency = models.CharField(max_length=20, help_text="daily, weekly, manual, seasonal")
    parser_strategy = models.CharField(max_length=50, help_text="html_scrape, manual_clip, zip_unpack, pdf_register")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    # ── Arm binding + poll state (added 2026-08-05) ─────────────────────────
    arm_command = models.CharField(
        max_length=60, blank=True, default="",
        help_text="Management command that owns this feed, e.g. 'poll_source_pages'. Blank = documentation-only.")
    selector_config = models.JSONField(
        default=dict, blank=True,
        help_text="Per-feed parser knobs, e.g. {'content_regex': ..., 'strip_patterns': [...], 'max_pages': 2}.")
    last_polled_at = models.DateTimeField(blank=True, null=True)
    last_checksum_sha256 = models.CharField(
        max_length=64, blank=True, null=True,
        help_text="Page-diff state. Deliberately NOT AuthorityVersion.checksum_sha256 — that tracks authority "
                  "DOCUMENTS; this tracks an arbitrary watched page. Null = no baseline yet (first poll opens nothing).")
    last_content = models.TextField(
        blank=True, null=True, help_text="Normalized text of the last poll, so a diff can show what was ADDED.")
    last_result_note = models.TextField(
        blank=True, null=True, help_text="Last run's outcome or error — feeds the digest's arm-health section.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["feed_code"]

    def __str__(self):
        return f"{self.feed_code}: {self.feed_name}"


class ChangeRegisterItem(models.Model):
    """A detected/triaged tax-law change flowing toward a WORK_ORDERS INTAKE order.

    The front-of-the-front-door: a law change TRIGGERS authoring. This record is the funnel's
    ledger row (DETECTED -> TRIAGED -> PROMOTED / DISMISSED). Promotion opens a WORK_ORDERS order;
    it NEVER crosses a gate unattended (Gate 1 = Ken approves the spec; Gate 2 = the tts ingest).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    change_code = models.CharField(max_length=30, unique=True, help_text="e.g. CR-2026-001")
    title = models.CharField(max_length=255)
    summary = models.TextField(help_text="What changed, in the authority's own terms (cite it).")
    jurisdiction_code = models.CharField(max_length=10, default="US", help_text="US, GA, SC, ...")
    tax_year = models.IntegerField(blank=True, null=True, help_text="The tax year the change first affects (year-keyed).")

    detected_via = models.CharField(max_length=20, choices=ChangeDetectionSource.choices, default=ChangeDetectionSource.MANUAL_CLIP)
    status = models.CharField(max_length=20, choices=ChangeStatus.choices, default=ChangeStatus.DETECTED)
    external_ref = models.CharField(
        max_length=120, blank=True, null=True, db_index=True,
        help_text="Stable dedup key for automated detection. NAMESPACE new arms with a prefix so keys from "
                  "different feeds can never collide: 'DROP:rp-26-28.pdf', 'CFR26:1.199A-3@2026-07-09', "
                  "'DFT:f1040--dft.pdf@2026-08-04', 'CL:<cluster_id>', 'PAGE:<feed>@<sha12>'. The two original "
                  "arms are unprefixed (FR document_number, 'IRB-YYYY-NN') and do not collide with the prefixes.")

    # ── Provenance (what authority moved) ───────────────────────────────────
    authority_source = models.ForeignKey(
        AuthoritySource, on_delete=models.SET_NULL, blank=True, null=True, related_name="change_items")
    authority_version = models.ForeignKey(
        AuthorityVersion, on_delete=models.SET_NULL, blank=True, null=True, related_name="change_items",
        help_text="The new version whose checksum diff surfaced this (checksum_diff detection).")
    feed = models.ForeignKey(
        SourceFeedDefinition, on_delete=models.SET_NULL, blank=True, null=True, related_name="change_items")

    # ── Triage output ───────────────────────────────────────────────────────
    affected_forms = models.JSONField(default=list, blank=True, help_text='Form numbers the change touches, e.g. ["3115","4562"].')
    affected_rule_ids = models.JSONField(default=list, blank=True, help_text="Optional: specific FormRule rule_ids implicated.")
    is_substantive = models.BooleanField(blank=True, null=True, help_text="Triage call: does this require authoring? (null until triaged)")
    triage_notes = models.TextField(blank=True, null=True)

    # ── Promotion to the front door ─────────────────────────────────────────
    promoted_work_order = models.CharField(max_length=30, blank=True, null=True, help_text="The WORK_ORDERS order id, e.g. WO-24.")
    promoted_at = models.DateTimeField(blank=True, null=True)

    # ── Publication metadata + relevance (added 2026-08-05) ─────────────────
    item_kind = models.CharField(
        max_length=30, choices=ItemKind.choices, blank=True, null=True,
        help_text="What kind of publication this is — lets the digest group by type.")
    source_url = models.TextField(
        blank=True, null=True,
        help_text="Direct link to the authority document. Previously buried in `summary` prose.")
    published_date = models.DateField(
        blank=True, null=True,
        help_text="When the AUTHORITY published it — distinct from detected_at (when we noticed).")
    relevance_score = models.IntegerField(
        blank=True, null=True, db_index=True,
        help_text="0-100 perimeter relevance. ORDERS the digest; NEVER gates creation — an unscored or "
                  "low-scoring item is still recorded, just below the line. Suppressing a real change at "
                  "write time is the silent error the prime directive forbids. Null = never scored.")
    relevance_signals = models.JSONField(
        default=list, blank=True,
        help_text="Why it scored what it scored: [{'kind':'form','value':'4797','via':'TaxForm','weight':40}]. "
                  "Makes a score auditable instead of a bare number.")

    detected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-detected_at", "change_code"]
        constraints = [
            # external_ref was index-only; with 8 arms writing concurrently, dedup-by-query is racy.
            # Partial so the many manual-clip rows (null external_ref) stay unconstrained.
            models.UniqueConstraint(
                fields=["external_ref"],
                condition=models.Q(external_ref__isnull=False),
                name="uniq_change_register_external_ref",
            ),
        ]

    def __str__(self):
        return f"{self.change_code} [{self.status}]: {self.title}"
