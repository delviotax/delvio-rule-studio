"""Tests for sources.relevance — the perimeter scorer.

The two invariants under test are the ones that protect against silent loss:
  1. the score ORDERS, it never gates (nothing here may return "don't record this")
  2. unscoreable input lands MID-band and surfaces to a human, never 0

Mostly DB-free: a hand-seeded PerimeterIndex stands in for the Rule Studio tables so these
run fast and deterministically. One test exercises the real DB-backed index build.
"""
import pytest

from sources.relevance import (
    DEFAULT_DIGEST_THRESHOLD, UNSCOREABLE_SCORE, W_FORM, _form_needles, _irc_needles,
    build_perimeter_index, normalize_jurisdiction, score, score_summary,
)
from sources.pdf_text import squash
from tests.fixtures_feeds import RP_26_28_EXTRACT


@pytest.fixture
def index():
    """A DB-free index hand-seeded with a realistic slice of the perimeter."""
    idx = build_perimeter_index(include_db=False)
    for f in ("4797", "1040", "1065", "1120-S", "Schedule D", "4562", "8812"):
        idx.form_needles[f] = _form_needles(f)
    for s in ("199A", "179", "1231", "461"):
        idx.irc_needles[s] = _irc_needles(s)
    idx.cfr_sections.update({squash("1.199A-3"), squash("1.179-1")})
    return idx


class TestNormalizeJurisdiction:
    @pytest.mark.parametrize("raw,expected", [
        ("FED", "US"), ("fed", "US"), ("Federal", "US"), ("US", "US"), ("us", "US"),
        ("GA", "GA"), ("ga", "GA"), ("", ""), (None, ""),
    ])
    def test_fed_us_alias_collapses(self, raw, expected):
        """AuthoritySource seeds 'FED'; ChangeRegisterItem defaults 'US'. Same thing."""
        assert normalize_jurisdiction(raw) == expected


class TestScoreBands:
    def test_real_out_of_perimeter_guidance_scores_low(self, index):
        """rp-26-28 is exempt-organization/Form 990 territory — must fall below the fold."""
        s, signals = score(RP_26_28_EXTRACT, index=index)
        assert s < DEFAULT_DIGEST_THRESHOLD
        assert any(sig["kind"].startswith("out_of_perimeter") for sig in signals)

    def test_kern_split_text_still_matches(self, index):
        """The extractor emits '26 C F R 1. 603 3 - 2'; matching must survive that."""
        kerned = "T hi s  a m en ds  s ec t i on  1 99 A  an d  F or m  4 797 ."
        s, signals = score(kerned, index=index)
        kinds = {sig["kind"] for sig in signals}
        assert "irc" in kinds and "form" in kinds and s > DEFAULT_DIGEST_THRESHOLD

    def test_in_perimeter_prose_scores_high(self, index):
        s, _ = score(
            "Rev. Proc. 2026-40 sets the standard deduction and tax rate tables. "
            "See Form 1040 and section 179 limits.", index=index)
        assert s >= 80

    def test_structured_hint_alone_scores_without_text(self, index):
        """fetch_ecfr_title26 passes the section identifier directly rather than hoping
        to find it in prose."""
        s, signals = score("Trade or business income", index=index, cfr=["1.199A-3"])
        assert s > 0
        assert signals[0]["kind"] == "cfr" and signals[0]["via"] == "structured"

    def test_score_is_clamped_to_0_100(self, index):
        s, _ = score(
            "Form 1040 Form 1065 Form 4797 Form 4562 section 199A section 179 section 1231 "
            "section 461 standard deduction bonus depreciation section 179 OBBBA "
            "qualified business income earned income credit child tax credit", index=index)
        assert 0 <= s <= 100


class TestUnscoreable:
    def test_none_text_scores_mid_band_not_zero(self, index):
        """An unreadable PDF is exactly the item a person should look at."""
        s, signals = score(None, index=index)
        assert s == UNSCOREABLE_SCORE
        assert signals == [{"kind": "unscoreable", "value": "no readable text",
                            "via": "extractor", "weight": 0}]

    def test_unscoreable_lands_above_the_default_threshold(self):
        """Mid-band must mean VISIBLE — if it sorted below the fold it would be silence."""
        assert UNSCOREABLE_SCORE > DEFAULT_DIGEST_THRESHOLD

    def test_structured_hints_win_over_unscoreable(self, index):
        s, signals = score(None, index=index, cfr=["1.199A-3"])
        assert s > 0 and not any(sig["kind"] == "unscoreable" for sig in signals)


class TestHardNegatives:
    def test_negative_suppressed_when_a_real_anchor_fires(self, index):
        """A Form 990 document that ALSO amends §199A is still our problem."""
        s, signals = score(
            "Form 990 exempt organization returns. This also amends section 199A treatment.",
            index=index)
        assert s > 0
        assert not any(sig["kind"].startswith("out_of_perimeter") for sig in signals)

    def test_negative_applied_once_not_per_marker(self, index):
        """Many out-of-perimeter markers must not bury a weak-but-real signal deeper than one."""
        s, signals = score(
            "Form 990 and Form 706 and Form 709 — gift tax and estate tax return and "
            "exempt organization and private foundation matters.", index=index)
        negatives = [sig for sig in signals if sig["kind"].startswith("out_of_perimeter")]
        assert len(negatives) == 1
        assert s == 0


class TestSignals:
    def test_signals_explain_the_score(self, index):
        _, signals = score("Form 4797 disposition rules", index=index)
        form_sig = next(s for s in signals if s["kind"] == "form")
        assert form_sig["value"] == "4797"
        assert form_sig["weight"] == W_FORM
        assert form_sig["via"] == "text"

    def test_structured_and_text_hit_counted_once(self, index):
        """Double-counting the same token would inflate a single piece of evidence."""
        _, signals = score("Form 4797 disposition rules", index=index, forms=["4797"])
        form_sigs = [s for s in signals if s["kind"] == "form" and s["value"] == "4797"]
        assert len(form_sigs) == 1
        assert form_sigs[0]["via"] == "structured"     # stronger attribution wins

    def test_summary_renders_compactly(self, index):
        _, signals = score("Form 4797 and section 199A", index=index)
        out = score_summary(signals)
        assert "[form 4797]" in out and "[§199A]" in out


class TestFormNeedles:
    def test_bare_number_does_not_match_without_context(self, index):
        """'4797' alone could be a dollar amount or a page number."""
        s, signals = score("The taxpayer reported 4797 dollars of income.", index=index)
        assert not any(sig["kind"] == "form" for sig in signals)

    def test_hyphen_variants_both_match(self, index):
        for text in ("Form 1120-S shareholders", "Form 1120S shareholders"):
            _, signals = score(text, index=index)
            assert any(sig["kind"] == "form" for sig in signals), text


@pytest.mark.django_db
class TestDbBackedIndex:
    def test_builds_from_taxform_and_authority_rows(self):
        from sources.models import AuthoritySource
        from specs.models import TaxForm

        TaxForm.objects.create(jurisdiction="federal", form_number="4797",
                               form_title="Sales of Business Property", tax_year=2025)
        AuthoritySource.objects.create(
            source_code="IRC_199A", source_type="code_section", source_rank="controlling",
            jurisdiction_code="FED", title="QBI deduction", citation="IRC §199A; 26 CFR 1.199A-3",
            issuer="IRS")

        idx = build_perimeter_index()
        assert "4797" in idx.form_needles
        assert "199A" in idx.irc_needles
        assert squash("1.199A-3") in idx.cfr_sections
        assert not idx.is_empty
