"""Tests for sources.irs_directory — the shared irs-drop / irs-dft listing parser.

No database and no network: every test drives parse_index()/decode_*() directly, or
monkeypatches irs_directory.fetch_index.
"""
import datetime as dt

import pytest

from sources import irs_directory as ix
from tests.fixtures_feeds import DFT_ROWS, DROP_ROWS, dft_page, drop_page


class TestParseIndex:
    def test_parses_every_row_of_a_real_drop_page(self):
        rows = ix.parse_index(drop_page())
        assert len(rows) == len(DROP_ROWS)
        first = rows[0]
        assert first.filename == "rp-26-28.pdf"
        assert first.url == "https://www.irs.gov/pub/irs-drop/rp-26-28.pdf"
        assert first.posted_at == dt.date(2026, 7, 24)
        assert first.size == "88.05 KB"
        # The Drupal padding and the real double-space are collapsed, not preserved.
        assert first.description == "Rev. Proc. 2026-28"

    def test_parses_every_row_of_a_real_dft_page(self):
        rows = ix.parse_index(dft_page())
        assert len(rows) == len(DFT_ROWS)
        assert rows[0].filename == "i8615--dft.pdf"
        assert rows[0].description == "2026 Inst 8615 (PDF)"

    def test_zero_rows_raises_rather_than_returning_empty(self):
        """A silently-empty scrape is indistinguishable from 'nothing new published'.

        That is the worst failure mode this system has — an arm that has quietly stopped
        detecting. Layout drift must be loud.
        """
        with pytest.raises(ix.IndexLayoutError):
            ix.parse_index("<html><body><p>Service unavailable</p></body></html>")

    def test_zero_rows_raises_on_empty_string(self):
        with pytest.raises(ix.IndexLayoutError):
            ix.parse_index("")


class TestIterRows:
    def test_dedupes_across_pages_and_sorts_newest_first(self, monkeypatch):
        page0 = drop_page(DROP_ROWS[:3])
        page1 = drop_page(DROP_ROWS[2:])          # row index 2 overlaps both pages
        monkeypatch.setattr(ix, "fetch_index", lambda slug, page=0: [page0, page1][page])

        rows = ix.iter_rows(ix.DROP, pages=2)
        names = [r.filename for r in rows]
        assert len(names) == len(set(names)) == len(DROP_ROWS)
        assert rows == sorted(rows, key=lambda r: r.posted_at, reverse=True)

    def test_later_page_failure_keeps_earlier_pages(self, monkeypatch):
        def flaky(slug, page=0):
            if page == 0:
                return drop_page(DROP_ROWS[:3])
            raise TimeoutError("upstream hiccup")

        monkeypatch.setattr(ix, "fetch_index", flaky)
        rows = ix.iter_rows(ix.DROP, pages=3)
        assert len(rows) == 3          # partial coverage beats none

    def test_first_page_failure_propagates(self, monkeypatch):
        def dead(slug, page=0):
            raise TimeoutError("down")

        monkeypatch.setattr(ix, "fetch_index", dead)
        with pytest.raises(TimeoutError):
            ix.iter_rows(ix.DROP, pages=2)


class TestDecodeDrop:
    @pytest.mark.parametrize("filename,expected", [
        ("rp-26-28.pdf", "Rev. Proc. 2026-28"),
        ("rr-26-13.pdf", "Rev. Rul. 2026-13"),
        ("n-26-44.pdf", "Notice 2026-44"),
        ("a-26-5.pdf", "Announcement 2026-5"),
        ("n-26-39-appendix-2.xlsx", "Notice 2026-39 (appendix 2)"),
    ])
    def test_designation_comes_from_filename_not_description(self, filename, expected):
        row = ix.Row(filename=filename, url="u", posted_at=dt.date(2026, 7, 1), size="1 KB",
                     description="whatever the description says")
        assert ix.decode_drop(row)["designation"] == expected

    def test_appendix_flagged(self):
        row = ix.Row("n-26-39-appendix-2.xlsx", "u", dt.date(2026, 7, 10), "1 KB", "")
        d = ix.decode_drop(row)
        assert d["is_appendix"] is True and d["ext"] == "xlsx"

    def test_non_guidance_filename_returns_none(self):
        row = ix.Row("some-index.html", "u", dt.date(2026, 7, 1), "1 KB", "")
        assert ix.decode_drop(row) is None

    def test_every_real_row_decodes(self):
        for row in ix.parse_index(drop_page()):
            assert ix.decode_drop(row) is not None, row.filename


class TestDecodeDft:
    def test_tax_year_lead(self):
        row = ix.Row("i8615--dft.pdf", "u", dt.date(2026, 8, 4), "1 KB", "2026 Inst 8615 (PDF)")
        d = ix.decode_dft(row)
        assert d["kind"] == "Instructions" and d["form"] == "8615"
        assert d["tax_year"] == 2026 and d["revision"] is None

    def test_mmyy_revision_lead_is_not_a_tax_year(self):
        """'1226' is a Dec-2026 revision stamp, not tax year 1226."""
        row = ix.Row("f1062--dft.pdf", "u", dt.date(2026, 8, 4), "1 KB", "1226 Form 1062 (PDF)")
        d = ix.decode_dft(row)
        assert d["tax_year"] is None and d["revision"] == "1226"

    def test_schedule_and_spanish(self):
        sched = ix.decode_dft(ix.Row("i1040sr--dft.pdf", "u", dt.date(2026, 8, 4), "1 KB",
                                     "2026 Inst 1040 (Schedule R) (PDF)"))
        assert sched["form"] == "1040" and sched["schedule"] == "Schedule R"
        sp = ix.decode_dft(ix.Row("f9465sp--dft.pdf", "u", dt.date(2026, 8, 4), "1 KB",
                                  "1226 Form 9465 (sp) (PDF)"))
        assert sp["is_spanish"] is True

    def test_falls_back_to_filename_when_description_is_unparseable(self):
        row = ix.Row("f4797--dft.pdf", "u", dt.date(2026, 8, 4), "1 KB", "garbled")
        d = ix.decode_dft(row)
        assert d is not None and d["form"] == "4797"

    def test_every_real_row_decodes(self):
        for row in ix.parse_index(dft_page()):
            assert ix.decode_dft(row) is not None, row.filename
