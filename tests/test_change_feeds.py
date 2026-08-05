"""Tests for the Phase-1 detection arms: fetch_ecfr_title26, fetch_irs_drop, and the
poll_change_feeds registry.

Network is monkeypatched at each module's isolated fetch helper, so the suite never leaves the
machine. The tests that matter most are the four regressions at the bottom — each encodes a trap
found while verifying the live endpoints on 2026-08-05.
"""
import copy
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

import sources.irs_directory as ix
import sources.management.commands.fetch_ecfr_title26 as ecfr
import sources.management.commands.fetch_irs_drop as drop
import sources.pdf_text as pdf_text
from sources.models import ChangeRegisterItem, ItemKind, SourceFeedDefinition
from tests.fixtures_feeds import (
    DROP_ROWS, ECFR_TITLES_JSON, ECFR_VERSIONS_JSON, RP_26_28_EXTRACT, drop_page,
)


def run(*args, **kwargs):
    out = StringIO()
    call_command(*args, stdout=out, stderr=out, **kwargs)
    return out.getvalue()


@pytest.fixture
def ecfr_net(monkeypatch):
    """Serve the captured eCFR payloads for both endpoints the arm calls."""
    def fake(url):
        if "titles.json" in url:
            return copy.deepcopy(ECFR_TITLES_JSON)
        return copy.deepcopy(ECFR_VERSIONS_JSON)

    monkeypatch.setattr(ecfr, "_http_get_json", fake)


@pytest.fixture
def drop_net(monkeypatch):
    """Serve the captured irs-drop listing, and readable PDF text for every file."""
    monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: drop_page())
    monkeypatch.setattr(pdf_text, "text_for_url", lambda url, max_chars=20_000: RP_26_28_EXTRACT)


# ══════════════════════════════════════════════════════════════════════════
# fetch_ecfr_title26
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestFetchEcfr:
    def test_opens_items_for_in_perimeter_amendments(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        items = ChangeRegisterItem.objects.all()
        idents = {i.external_ref for i in items}
        assert "CFR26:1.199A-3@2026-08-03" in idents
        assert "CFR26:301.7701-3@2026-07-30" in idents
        assert all(i.item_kind == ItemKind.CFR_SECTION for i in items)

    def test_external_ref_is_namespaced_and_carries_the_amendment_date(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        ref = ChangeRegisterItem.objects.get(source_url__endswith="1.199A-3").external_ref
        assert ref.startswith("CFR26:") and ref.endswith("@2026-08-03")

    def test_publication_metadata_populated(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        item = ChangeRegisterItem.objects.get(external_ref="CFR26:1.199A-3@2026-08-03")
        assert item.published_date.isoformat() == "2026-08-03"
        assert item.source_url == "https://www.ecfr.gov/current/title-26/section-1.199A-3"
        assert item.status == "detected"

    def test_out_of_perimeter_parts_excluded_by_default(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        # part 20 = estate tax
        assert not ChangeRegisterItem.objects.filter(external_ref__contains="20.2056A-2").exists()

    def test_all_parts_includes_them(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01", all_parts=True)
        assert ChangeRegisterItem.objects.filter(external_ref__contains="20.2056A-2").exists()

    def test_removed_sections_always_surface(self, ecfr_net):
        """1.9999-9 is substantive=false but removed=true — a removal is always news."""
        run("fetch_ecfr_title26", since="2026-01-01")
        item = ChangeRegisterItem.objects.get(external_ref="CFR26:1.9999-9@2026-08-03")
        assert "REMOVED" in item.title

    def test_idempotent(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        first = ChangeRegisterItem.objects.count()
        out = run("fetch_ecfr_title26", since="2026-01-01", force=True)
        assert ChangeRegisterItem.objects.count() == first
        assert "already-known" in out

    def test_dry_run_opens_nothing(self, ecfr_net):
        out = run("fetch_ecfr_title26", since="2026-01-01", dry_run=True)
        assert ChangeRegisterItem.objects.count() == 0
        assert "would open" in out

    def test_dry_run_writes_nothing_at_all_not_even_the_feed_row(self, ecfr_net):
        """'Report, change nothing' has to be literally true or the flag isn't trustworthy."""
        run("fetch_ecfr_title26", since="2026-01-01", dry_run=True)
        assert not SourceFeedDefinition.objects.filter(feed_code="ECFR_TITLE26").exists()

    def test_http_failure_raises_command_error(self, monkeypatch):
        def boom(url):
            raise TimeoutError("eCFR down")

        monkeypatch.setattr(ecfr, "_http_get_json", boom)
        with pytest.raises(CommandError):
            run("fetch_ecfr_title26")

    def test_short_circuits_when_title26_has_not_moved(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        feed = SourceFeedDefinition.objects.get(feed_code="ECFR_TITLE26")
        assert feed.last_content == "2026-08-03"
        out = run("fetch_ecfr_title26", since="2026-01-01")
        assert "short-circuit" in out.lower() or "unchanged" in out.lower()

    def test_force_defeats_the_short_circuit(self, ecfr_net):
        run("fetch_ecfr_title26", since="2026-01-01")
        out = run("fetch_ecfr_title26", since="2026-01-01", force=True)
        assert "already-known" in out


# ══════════════════════════════════════════════════════════════════════════
# fetch_irs_drop
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestFetchIrsDrop:
    def test_opens_one_item_per_guidance_file(self, drop_net):
        run("fetch_irs_drop")
        assert ChangeRegisterItem.objects.count() == len(DROP_ROWS)

    def test_designation_comes_from_filename_not_description(self, drop_net):
        """The live index writes 'RR-2026-13'; the register should say 'Rev. Rul. 2026-13'."""
        run("fetch_irs_drop")
        item = ChangeRegisterItem.objects.get(external_ref="DROP:rr-26-13.pdf")
        assert item.title.startswith("Rev. Rul. 2026-13")

    def test_item_kind_mapped_per_prefix(self, drop_net):
        run("fetch_irs_drop")
        by_ref = {i.external_ref: i.item_kind for i in ChangeRegisterItem.objects.all()}
        assert by_ref["DROP:rp-26-28.pdf"] == ItemKind.REV_PROC
        assert by_ref["DROP:n-26-44.pdf"] == ItemKind.NOTICE
        assert by_ref["DROP:rr-26-13.pdf"] == ItemKind.REV_RUL

    def test_kinds_filter(self, drop_net):
        run("fetch_irs_drop", kinds="rr")
        assert ChangeRegisterItem.objects.count() == 1

    def test_since_filter(self, drop_net):
        run("fetch_irs_drop", since="2026-07-14")
        assert ChangeRegisterItem.objects.count() == 4      # 07-24, 07-21, 07-15, 07-14

    def test_idempotent(self, drop_net):
        run("fetch_irs_drop")
        first = ChangeRegisterItem.objects.count()
        out = run("fetch_irs_drop")
        assert ChangeRegisterItem.objects.count() == first
        assert "already-known" in out

    def test_dry_run_opens_nothing(self, drop_net):
        out = run("fetch_irs_drop", dry_run=True)
        assert ChangeRegisterItem.objects.count() == 0
        assert "would open" in out

    def test_dry_run_writes_nothing_at_all_not_even_the_feed_row(self, drop_net):
        run("fetch_irs_drop", dry_run=True)
        assert not SourceFeedDefinition.objects.filter(feed_code="IRS_DROP").exists()

    def test_no_text_skips_pdf_download(self, monkeypatch):
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: drop_page())
        calls = []
        monkeypatch.setattr(pdf_text, "text_for_url",
                            lambda url, max_chars=20_000: calls.append(url) or "x")
        run("fetch_irs_drop", no_text=True)
        assert calls == []
        assert ChangeRegisterItem.objects.count() == len(DROP_ROWS)

    def test_already_known_items_do_not_redownload_pdfs(self, monkeypatch):
        """Re-downloading 50 PDFs every daily run would be rude to irs.gov and pointless."""
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: drop_page())
        calls = []

        def counting(url, max_chars=20_000):
            calls.append(url)
            return RP_26_28_EXTRACT

        monkeypatch.setattr(pdf_text, "text_for_url", counting)
        run("fetch_irs_drop")
        first_round = len(calls)
        assert first_round > 0
        run("fetch_irs_drop")
        assert len(calls) == first_round      # second run downloaded nothing

    def test_unreadable_pdf_scores_unscoreable_not_zero(self, monkeypatch):
        """An item we could not read is exactly the item a human must see."""
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: drop_page([DROP_ROWS[0]]))
        monkeypatch.setattr(pdf_text, "text_for_url", lambda url, max_chars=20_000: None)
        run("fetch_irs_drop")
        item = ChangeRegisterItem.objects.get()
        # Description text still scores, but the summary must flag the extraction failure.
        assert "could not be extracted" in item.summary

    def test_layout_change_raises_rather_than_reporting_nothing_new(self, monkeypatch):
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: "<html>maintenance</html>")
        with pytest.raises(CommandError):
            run("fetch_irs_drop")

    def test_bad_kinds_argument_rejected(self, drop_net):
        with pytest.raises(CommandError):
            run("fetch_irs_drop", kinds="rp,zzz")


# ══════════════════════════════════════════════════════════════════════════
# poll_change_feeds registry
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestPollChangeFeeds:
    def test_one_arm_failing_does_not_stop_the_others(self, monkeypatch, ecfr_net, drop_net):
        import sources.management.commands.fetch_irb as irb

        def boom(url):
            raise TimeoutError("irs.gov down")

        monkeypatch.setattr(irb, "_http_get_text", boom)
        monkeypatch.setattr(
            "sources.management.commands.fetch_federal_register._http_get_json",
            lambda url: {"results": [], "next_page_url": None})

        out = run("poll_change_feeds")                     # must NOT raise
        assert "FAILED" in out or "ERR" in out
        assert ChangeRegisterItem.objects.filter(external_ref__startswith="DROP:").exists()

    def test_all_arms_failing_raises(self, monkeypatch):
        import sources.management.commands.fetch_irb as irb

        def boom(*a, **k):
            raise TimeoutError("everything is down")

        monkeypatch.setattr(irb, "_http_get_text", boom)
        monkeypatch.setattr(ecfr, "_http_get_json", boom)
        monkeypatch.setattr(ix, "fetch_index", boom)
        monkeypatch.setattr(
            "sources.management.commands.fetch_federal_register._http_get_json", boom)
        import sources.management.commands.fetch_court_opinions as court
        import sources.management.commands.fetch_irs_form_checksums as chk
        monkeypatch.setattr(court, "_http_get_json", boom)
        monkeypatch.setattr(chk, "_http_head", boom)
        # chk is skipped rather than boomed: with zero watched URLs it succeeds without any
        # network, which is correct behavior — an empty watch list is not an outage.
        with pytest.raises(CommandError):
            run("poll_change_feeds", no_chk=True)

    def test_only_runs_a_single_arm(self, ecfr_net, drop_net):
        run("poll_change_feeds", only="drop")
        refs = ChangeRegisterItem.objects.values_list("external_ref", flat=True)
        assert all(r.startswith("DROP:") for r in refs)
        assert len(refs) > 0

    def test_only_rejects_unknown_key(self):
        with pytest.raises(CommandError):
            run("poll_change_feeds", only="nope")

    def test_generated_skip_flags_work(self, ecfr_net, drop_net, monkeypatch):
        monkeypatch.setattr(
            "sources.management.commands.fetch_federal_register._http_get_json",
            lambda url: {"results": [], "next_page_url": None})
        import sources.management.commands.fetch_irb as irb
        monkeypatch.setattr(irb, "_http_get_text", lambda url: "<html></html>")

        out = run("poll_change_feeds", no_irb=True, no_fr=True, no_ecfr=True)
        assert "fetch_irb: skipped" in out and "fetch_federal_register: skipped" in out
        assert not ChangeRegisterItem.objects.filter(external_ref__startswith="CFR26:").exists()

    def test_dry_run_does_not_report_a_misleading_zero(self, ecfr_net, drop_net, monkeypatch):
        monkeypatch.setattr(
            "sources.management.commands.fetch_federal_register._http_get_json",
            lambda url: {"results": [], "next_page_url": None})
        import sources.management.commands.fetch_irb as irb
        monkeypatch.setattr(irb, "_http_get_text", lambda url: "<html></html>")

        out = run("poll_change_feeds", dry_run=True, no_irb=True, no_fr=True)
        assert "dry-run" in out
        assert "0 new item(s) opened" not in out
        assert ChangeRegisterItem.objects.count() == 0


# ══════════════════════════════════════════════════════════════════════════
# The four regressions — each encodes a trap found verifying live endpoints
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestLiveEndpointRegressions:
    def test_recent_issue_date_with_old_amendment_date_is_filtered_out(self, ecfr_net):
        """§1.0-1: issue_date 2026-04-03, amendment_date 2016-12-19.

        eCFR re-issues unamended sections. Filtering on issue_date would have reported a
        ten-year-old amendment as this year's news — four times in 2026 alone.
        """
        run("fetch_ecfr_title26", since="2026-01-01", include_nonsubstantive=True, all_parts=True)
        assert not ChangeRegisterItem.objects.filter(external_ref__startswith="CFR26:1.0-1").exists()

    def test_inconsistent_drop_descriptions_still_decode(self, drop_net):
        """Live rows carry 'Rev. Proc.  2026-28', 'RR-2026-13' and 'N-2026-44' interchangeably."""
        run("fetch_irs_drop")
        titles = set(ChangeRegisterItem.objects.values_list("title", flat=True))
        assert "Rev. Proc. 2026-28 published" in titles
        assert "Rev. Rul. 2026-13 published" in titles
        assert "Notice 2026-44 published" in titles

    def test_xlsx_appendix_gets_its_own_item(self, drop_net):
        """An appendix IS a separate publication, and .xlsx has no extractable PDF text."""
        run("fetch_irs_drop")
        item = ChangeRegisterItem.objects.get(external_ref="DROP:n-26-39-appendix-2.xlsx")
        assert "appendix 2" in item.title.lower()

    def test_kern_split_pdf_text_reaches_the_scorer(self, monkeypatch):
        """The extractor emits '26 C F R  1. 603 3 - 2'; scoring must survive it."""
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: drop_page([DROP_ROWS[0]]))
        monkeypatch.setattr(pdf_text, "text_for_url", lambda url, max_chars=20_000: RP_26_28_EXTRACT)
        run("fetch_irs_drop")
        item = ChangeRegisterItem.objects.get()
        # rp-26-28 is exempt-organization guidance: it must score, and score LOW.
        assert item.relevance_score is not None
        assert item.relevance_score < 25
