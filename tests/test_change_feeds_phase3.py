"""Tests for the Phase-3 detection arms: fetch_irs_drafts, fetch_irs_form_checksums,
fetch_court_opinions — plus their registration in the poll_change_feeds registry.

Network is monkeypatched at each module's isolated fetch seam. The named regressions from the
plan live here: a draft RE-POSTED under the same filename with a new date opens a SECOND item,
and a first checksum run against null baselines opens NOTHING.
"""
import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

import sources.irs_directory as ix
import sources.management.commands.fetch_court_opinions as court_mod
import sources.management.commands.fetch_irs_form_checksums as chk_mod
from sources.models import (
    AuthoritySource, AuthorityVersion, ChangeRegisterItem, ItemKind, SourceFeedDefinition,
)
from specs.models import TaxForm
from tests.fixtures_feeds import CL_SEARCH_CA11_JSON, CL_SEARCH_TAX_JSON, DFT_ROWS, dft_page


def run(*args, **kwargs):
    out = StringIO()
    call_command(*args, stdout=out, stderr=out, **kwargs)
    return out.getvalue()


@pytest.fixture
def spec_4797(db):
    return TaxForm.objects.create(
        jurisdiction="federal", form_number="4797", form_title="Sales of Business Property",
        entity_types=["1120S", "1065", "1040"], tax_year=2025, version=1, status="draft")


@pytest.fixture
def dft_net(monkeypatch):
    monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: dft_page())


# ══════════════════════════════════════════════════════════════════════════
# fetch_irs_drafts
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestFetchIrsDrafts:
    def test_perimeter_filter_keeps_specced_and_entity_forms_only(self, dft_net, spec_4797):
        # Fixture rows: 8615, 9465(sp), 1062(SchA), 1040(SchR), 4797, 8997.
        # Perimeter = specced {4797} + entity families {1040,1120S,1065,1041}.
        run("fetch_irs_drafts")
        refs = set(ChangeRegisterItem.objects.values_list("external_ref", flat=True))
        assert "DFT:f4797--dft.pdf@2026-08-04" in refs
        assert "DFT:i1040sr--dft.pdf@2026-08-04" in refs
        assert len(refs) == 2

    def test_dropped_drafts_are_logged_not_silent(self, dft_net, spec_4797):
        out = run("fetch_irs_drafts")
        assert "dropped 4 out-of-perimeter draft(s)" in out
        assert "8615" in out and "8997" in out

    def test_all_forms_disables_the_filter(self, dft_net, spec_4797):
        run("fetch_irs_drafts", all_forms=True)
        assert ChangeRegisterItem.objects.count() == len(DFT_ROWS)

    def test_repost_same_filename_new_date_opens_a_second_item(self, monkeypatch, spec_4797):
        """Regression #4: the same draft re-posted on each revision — every re-post is a change."""
        first = [("f4797--dft.pdf", "2026-08-04", "19:10:49", "180.78 KB",
                  "2026 Form 4797                           (PDF)")]
        second = [("f4797--dft.pdf", "2026-08-20", "09:00:00", "181.02 KB",
                   "2026 Form 4797                           (PDF)")]
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: dft_page(first))
        run("fetch_irs_drafts")
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: dft_page(second))
        run("fetch_irs_drafts")
        refs = sorted(ChangeRegisterItem.objects.values_list("external_ref", flat=True))
        assert refs == ["DFT:f4797--dft.pdf@2026-08-04", "DFT:f4797--dft.pdf@2026-08-20"]

    def test_item_carries_kind_year_and_affected_forms(self, dft_net, spec_4797):
        run("fetch_irs_drafts")
        item = ChangeRegisterItem.objects.get(external_ref="DFT:f4797--dft.pdf@2026-08-04")
        assert item.item_kind == ItemKind.DRAFT_FORM
        assert item.tax_year == 2026
        assert item.affected_forms == ["4797"]

    def test_idempotent(self, dft_net, spec_4797):
        run("fetch_irs_drafts")
        first = ChangeRegisterItem.objects.count()
        out = run("fetch_irs_drafts")
        assert ChangeRegisterItem.objects.count() == first
        assert "already-known" in out

    def test_dry_run_writes_nothing_at_all(self, dft_net, spec_4797):
        out = run("fetch_irs_drafts", dry_run=True)
        assert ChangeRegisterItem.objects.count() == 0
        assert not SourceFeedDefinition.objects.filter(feed_code="IRS_DFT").exists()
        assert "would open" in out

    def test_layout_change_raises(self, monkeypatch, spec_4797):
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: "<html>maintenance</html>")
        with pytest.raises(CommandError):
            run("fetch_irs_drafts")


# ══════════════════════════════════════════════════════════════════════════
# fetch_irs_form_checksums
# ══════════════════════════════════════════════════════════════════════════

SHA_A = "a" * 64
PDF_BYTES_1 = b"%PDF-1.7 original"
PDF_BYTES_2 = b"%PDF-1.7 revised!!"


def make_watched(url="https://www.irs.gov/pub/irs-pdf/f4797.pdf", checksum=None):
    src = AuthoritySource.objects.create(
        source_code="IRS_2025_4797_FORM", source_type="official_form", source_rank="primary_official",
        jurisdiction_code="US", title="Form 4797", issuer="IRS", official_url=url)
    version = AuthorityVersion.objects.create(
        authority_source=src, version_label="TY2025", retrieval_url=url,
        file_type="pdf", checksum_sha256=checksum, is_current=True)
    return src, version


@pytest.fixture
def chk_net(monkeypatch):
    state = {"head": {"etag": '"abc"', "last_modified": "Mon, 04 Aug 2026", "content_length": "17"},
             "body": PDF_BYTES_1, "gets": []}
    monkeypatch.setattr(chk_mod, "_http_head", lambda url: dict(state["head"]))

    def get(url):
        state["gets"].append(url)
        return state["body"]

    monkeypatch.setattr(chk_mod, "_http_get_bytes", get)
    return state


@pytest.mark.django_db
class TestFetchIrsFormChecksums:
    def test_first_run_with_null_checksum_baselines_and_opens_nothing(self, chk_net):
        """Regression #3: baseline, not false positives."""
        _, version = make_watched(checksum=None)
        out = run("fetch_irs_form_checksums")
        assert ChangeRegisterItem.objects.count() == 0
        version.refresh_from_db()
        assert version.checksum_sha256 is not None
        assert "BASELINE" in out

    def test_unchanged_head_skips_the_get(self, chk_net):
        make_watched(checksum=None)
        run("fetch_irs_form_checksums")           # baseline (1 GET)
        first_gets = len(chk_net["gets"])
        run("fetch_irs_form_checksums")           # HEAD unchanged -> no GET
        assert len(chk_net["gets"]) == first_gets

    def test_changed_content_opens_one_item_with_authority_linkage(self, chk_net):
        src, version = make_watched(checksum=None)
        run("fetch_irs_form_checksums")           # baseline
        chk_net["head"]["etag"] = '"def"'
        chk_net["body"] = PDF_BYTES_2
        run("fetch_irs_form_checksums")
        item = ChangeRegisterItem.objects.get()
        assert item.external_ref.startswith("CHK:IRS_2025_4797_FORM@")
        assert item.authority_source_id == src.id
        assert item.item_kind == ItemKind.FINAL_FORM
        # The authority record itself is NOT silently overwritten by the arm.
        version.refresh_from_db()
        assert item.external_ref.split("@")[1] not in version.checksum_sha256

    def test_same_new_content_does_not_double_open(self, chk_net):
        make_watched(checksum=None)
        run("fetch_irs_form_checksums")
        chk_net["head"]["etag"] = '"def"'
        chk_net["body"] = PDF_BYTES_2
        run("fetch_irs_form_checksums")
        chk_net["head"]["etag"] = '"ghi"'         # headers move again, same bytes
        run("fetch_irs_form_checksums")
        assert ChangeRegisterItem.objects.count() == 1

    def test_dry_run_writes_nothing_including_baselines(self, chk_net):
        _, version = make_watched(checksum=None)
        run("fetch_irs_form_checksums", dry_run=True)
        version.refresh_from_db()
        assert version.checksum_sha256 is None
        assert ChangeRegisterItem.objects.count() == 0
        assert not SourceFeedDefinition.objects.filter(feed_code="IRS_FORM_CHECKSUMS").exists()

    def test_draft_urls_are_excluded(self, chk_net):
        make_watched(url="https://www.irs.gov/pub/irs-dft/f4797--dft.pdf", checksum=SHA_A)
        out = run("fetch_irs_form_checksums")
        assert "1 draft URL(s) excluded" in out
        assert chk_net["gets"] == []

    def test_seed_manifest_matches_on_official_url_and_reports_unmatched(self, tmp_path, db):
        src, version = make_watched(checksum=None)
        manifest = {"forms": [
            {"form_code": "4797", "irs_url": src.official_url, "sha256": SHA_A, "tax_year": 2025},
            {"form_code": "9999", "irs_url": "https://www.irs.gov/pub/irs-pdf/f9999.pdf",
             "sha256": SHA_A, "tax_year": 2025},
        ]}
        path = tmp_path / "forms_manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        out = run("fetch_irs_form_checksums", seed_manifest=str(path))
        version.refresh_from_db()
        assert version.checksum_sha256 == SHA_A
        assert "1 manifest entr(ies) with no matching AuthoritySource" in out
        assert "9999" in out


# ══════════════════════════════════════════════════════════════════════════
# fetch_court_opinions
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def court_net(monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        if "court=tax" in url:
            return json.loads(json.dumps(CL_SEARCH_TAX_JSON))
        return json.loads(json.dumps(CL_SEARCH_CA11_JSON))

    monkeypatch.setattr(court_mod, "_http_get_json", fake)
    return calls


@pytest.mark.django_db
class TestFetchCourtOpinions:
    def test_opens_items_with_namespaced_refs(self, court_net):
        run("fetch_court_opinions", courts="tax")
        refs = set(ChangeRegisterItem.objects.values_list("external_ref", flat=True))
        assert refs == {"CL:9911001", "CL:9911002"}
        assert all(i.item_kind == ItemKind.COURT_OPINION for i in ChangeRegisterItem.objects.all())

    def test_malformed_row_is_counted_unusable_not_fatal(self, court_net):
        out = run("fetch_court_opinions", courts="tax")
        assert "1 unusable row(s)" in out

    def test_tax_court_unfiltered_but_circuits_get_the_tax_query(self, court_net):
        run("fetch_court_opinions", courts="tax,ca11")
        tax_url = next(u for u in court_net if "court=tax" in u)
        ca11_url = next(u for u in court_net if "court=ca11" in u)
        assert "q=" not in tax_url
        assert "q=" in ca11_url and "internal+revenue" in ca11_url.replace("%22", "")

    def test_missing_results_key_raises(self, monkeypatch):
        monkeypatch.setattr(court_mod, "_http_get_json", lambda url: {"detail": "throttled"})
        with pytest.raises(CommandError):
            run("fetch_court_opinions", courts="tax")

    def test_one_court_failing_leaves_the_others(self, monkeypatch):
        def fake(url):
            if "court=ca11" in url:
                raise TimeoutError("ca11 down")
            return json.loads(json.dumps(CL_SEARCH_TAX_JSON))

        monkeypatch.setattr(court_mod, "_http_get_json", fake)
        out = run("fetch_court_opinions", courts="tax,ca11")     # must NOT raise
        assert "FAILED" in out or "failed" in out
        assert ChangeRegisterItem.objects.filter(external_ref="CL:9911001").exists()

    def test_all_courts_failing_raises(self, monkeypatch):
        def boom(url):
            raise TimeoutError("cl down")

        monkeypatch.setattr(court_mod, "_http_get_json", boom)
        with pytest.raises(CommandError):
            run("fetch_court_opinions", courts="tax,ca11")

    def test_idempotent(self, court_net):
        run("fetch_court_opinions", courts="tax")
        first = ChangeRegisterItem.objects.count()
        out = run("fetch_court_opinions", courts="tax")
        assert ChangeRegisterItem.objects.count() == first
        assert "already-known" in out

    def test_dry_run_writes_nothing(self, court_net):
        run("fetch_court_opinions", courts="tax", dry_run=True)
        assert ChangeRegisterItem.objects.count() == 0
        assert not SourceFeedDefinition.objects.filter(feed_code="COURT_OPINIONS").exists()

    def test_unknown_court_rejected(self):
        with pytest.raises(CommandError):
            run("fetch_court_opinions", courts="tax,nope")


# ══════════════════════════════════════════════════════════════════════════
# Registry integration
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestPollRegistryPhase3:
    def test_new_arms_are_registered_with_generated_flags(self):
        from sources.management.commands.poll_change_feeds import ARMS
        keys = {a.key for a in ARMS}
        assert {"dft", "chk", "court"} <= keys

    def test_only_dft_runs_just_that_arm(self, dft_net, spec_4797):
        run("poll_change_feeds", only="dft")
        refs = list(ChangeRegisterItem.objects.values_list("external_ref", flat=True))
        assert refs and all(r.startswith("DFT:") for r in refs)

    def test_no_flags_skip_the_new_arms(self, monkeypatch):
        # Every OTHER arm is stubbed to do nothing; the three new arms are skipped by flag —
        # so the run completes with zero items and zero network.
        monkeypatch.setattr(
            "sources.management.commands.fetch_federal_register._http_get_json",
            lambda url: {"results": [], "next_page_url": None})
        import sources.management.commands.fetch_irb as irb
        monkeypatch.setattr(irb, "_http_get_text", lambda url: "<html></html>")
        import sources.management.commands.fetch_ecfr_title26 as ecfr
        monkeypatch.setattr(ecfr, "_http_get_json",
                            lambda url: {"titles": [{"number": 26, "latest_amended_on": "2020-01-01",
                                                     "latest_issue_date": "2020-01-01"}]})
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: (_ for _ in ()).throw(AssertionError("net!")))
        monkeypatch.setattr(chk_mod, "_http_head", lambda url: (_ for _ in ()).throw(AssertionError("net!")))
        monkeypatch.setattr(court_mod, "_http_get_json", lambda url: (_ for _ in ()).throw(AssertionError("net!")))

        out = run("poll_change_feeds", no_dft=True, no_chk=True, no_court=True, no_drop=True)
        assert "fetch_irs_drafts: skipped" in out
        assert "fetch_irs_form_checksums: skipped" in out
        assert "fetch_court_opinions: skipped" in out
        assert ChangeRegisterItem.objects.count() == 0
