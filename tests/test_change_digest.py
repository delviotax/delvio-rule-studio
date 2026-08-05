"""Tests for the Phase-2 digest: sources.digest collection/rendering and the change_digest command.

All read-only against fixture rows; email delivery is monkeypatched at sources.emailer's seam.
"""
import datetime as dt
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

import sources.management.commands.change_digest as digest_cmd
from sources import digest as dg
from sources.emailer import EmailNotConfigured
from sources.models import ChangeRegisterItem, ChangeStatus, SourceFeedDefinition
from specs.models import FormRule, TaxForm


def run(*args, **kwargs):
    out = StringIO()
    call_command(*args, stdout=out, stderr=out, **kwargs)
    return out.getvalue()


def make_item(code, *, score=None, signals=None, status=ChangeStatus.DETECTED,
              detected_days_ago=0, title=None, **extra):
    item = ChangeRegisterItem.objects.create(
        change_code=code, title=title or f"Item {code}", summary="s", status=status,
        relevance_score=score, relevance_signals=signals or [], **extra)
    if detected_days_ago:
        ChangeRegisterItem.objects.filter(pk=item.pk).update(
            detected_at=timezone.now() - dt.timedelta(days=detected_days_ago))
        item.refresh_from_db()
    return item


@pytest.fixture
def form_4797_with_rule(db):
    form = TaxForm.objects.create(
        jurisdiction="federal", form_number="4797", form_title="Sales of Business Property",
        entity_types=["1120S", "1065", "1040"], tax_year=2025, version=1, status="draft")
    rule = FormRule.objects.create(
        tax_form=form, rule_id="R001", title="Part I gain netting",
        rule_type="calculation", inputs=[], outputs=[])
    return form, rule


@pytest.mark.django_db
class TestCollect:
    def test_threshold_splits_above_and_below(self):
        make_item("CR-2026-001", score=80)
        make_item("CR-2026-002", score=10)
        data = dg.collect(since_days=7, threshold=25)
        assert [i.change_code for i in data["above"]] == ["CR-2026-001"]
        assert [i.change_code for i in data["below"]] == ["CR-2026-002"]

    def test_unscored_rides_above_the_line_and_floats_to_top(self):
        make_item("CR-2026-001", score=99)
        make_item("CR-2026-002", score=None)
        data = dg.collect(since_days=7, threshold=25)
        assert [i.change_code for i in data["above"]] == ["CR-2026-002", "CR-2026-001"]

    def test_aging_lists_old_detected_but_not_old_promoted(self):
        make_item("CR-2026-001", score=50, detected_days_ago=20)
        make_item("CR-2026-002", score=50, detected_days_ago=20, status=ChangeStatus.PROMOTED)
        data = dg.collect()
        assert [i.change_code for i in data["aging"]] == ["CR-2026-001"]

    def test_window_excludes_older_items_from_above_but_not_from_aging(self):
        make_item("CR-2026-001", score=90, detected_days_ago=20)
        data = dg.collect(since_days=7)
        assert data["above"] == [] and len(data["aging"]) == 1

    def test_arm_health_flags_stale_and_zero_rows(self):
        SourceFeedDefinition.objects.create(
            feed_code="A", feed_name="a", jurisdiction_code="US", source_family="X",
            feed_type="json_api", refresh_frequency="daily", parser_strategy="p",
            arm_command="fetch_a", last_polled_at=timezone.now(),
            last_result_note="ok · 0 rows / 0 opened")
        SourceFeedDefinition.objects.create(
            feed_code="B", feed_name="b", jurisdiction_code="US", source_family="X",
            feed_type="json_api", refresh_frequency="daily", parser_strategy="p",
            arm_command="fetch_b")   # never polled
        # A feed with NO arm_command is documentation-only and stays out of arm health.
        SourceFeedDefinition.objects.create(
            feed_code="C", feed_name="c", jurisdiction_code="US", source_family="X",
            feed_type="json_api", refresh_frequency="daily", parser_strategy="p")
        data = dg.collect()
        by_code = {a["feed_code"]: a for a in data["arms"]}
        assert set(by_code) == {"A", "B"}
        assert by_code["A"]["zero_rows"] and not by_code["A"]["stale"]
        assert by_code["B"]["stale"] and by_code["B"]["note"] == "(never ran)"

    def test_blast_radius_from_relevance_signals(self, form_4797_with_rule):
        item = make_item("CR-2026-001", score=60,
                         signals=[{"kind": "form", "value": "4797", "via": "text", "weight": 40}])
        br = dg.blast_radius(item)
        assert br.total == 1
        assert br.shown[0]["rule_id"] == "R001"
        assert br.shown[0]["reason"] == "on_affected_form"


@pytest.mark.django_db
class TestRendering:
    def test_below_the_line_is_rendered_not_hidden(self):
        make_item("CR-2026-001", score=80, title="Big change")
        make_item("CR-2026-002", score=5, title="Tiny change")
        text = dg.render_text(dg.collect())
        assert "Big change" in text and "Tiny change" in text
        assert "BELOW THE LINE (1)" in text

    def test_blast_radius_inline_in_both_renderings(self, form_4797_with_rule):
        make_item("CR-2026-001", score=60,
                  signals=[{"kind": "form", "value": "4797", "via": "text", "weight": 40}])
        data = dg.collect()
        assert "4797/R001" in dg.render_text(data)
        assert "4797/R001" in dg.render_html(data)

    def test_no_linked_rules_prompts_the_new_rule_question(self):
        make_item("CR-2026-001", score=60)
        assert "NEW rule" in dg.render_text(dg.collect())

    def test_admin_links_present(self):
        item = make_item("CR-2026-001", score=60)
        text = dg.render_text(dg.collect())
        assert f"/admin/sources/changeregisteritem/{item.pk}/change/" in text

    def test_empty_arm_section_is_loud(self):
        assert "pollers have never run" in dg.render_text(dg.collect())

    def test_subject_line_counts(self):
        make_item("CR-2026-001", score=80)
        make_item("CR-2026-002", score=None)
        make_item("CR-2026-003", score=5)
        subject = dg.subject_line(dg.collect())
        assert "2 above the line" in subject and "1 below" in subject and "1 unscored" in subject


@pytest.mark.django_db
class TestChangeDigestCommand:
    def test_stdout_without_email_flag(self):
        make_item("CR-2026-001", score=80, title="Visible on stdout")
        out = run("change_digest")
        assert "Visible on stdout" in out

    def test_email_sends_and_reports(self, monkeypatch):
        make_item("CR-2026-001", score=80)
        sent = {}

        def fake_send(subject, html, text, *, to=None):
            sent.update(subject=subject, html=html, text=text, to=to)
            return ["ken@delviotax.com"]

        monkeypatch.setattr(digest_cmd, "send_digest_email", fake_send)
        out = run("change_digest", email=True)
        assert "Digest sent to ken@delviotax.com" in out
        assert "CR-2026-001" in sent["text"] and "CR-2026-001" in sent["html"]

    def test_missing_api_key_falls_back_to_stdout_exit_zero(self, monkeypatch):
        make_item("CR-2026-001", score=80, title="Fallback content")

        def not_configured(*a, **k):
            raise EmailNotConfigured("no key")

        monkeypatch.setattr(digest_cmd, "send_digest_email", not_configured)
        out = run("change_digest", email=True)      # must NOT raise
        assert "RESEND_API_KEY is not set" in out and "Fallback content" in out

    def test_delivery_failure_raises_command_error(self, monkeypatch):
        def rejected(*a, **k):
            raise RuntimeError("Resend rejected the digest: HTTP 422")

        monkeypatch.setattr(digest_cmd, "send_digest_email", rejected)
        with pytest.raises(CommandError):
            run("change_digest", email=True)

    def test_bad_since_days_rejected(self):
        with pytest.raises(CommandError):
            run("change_digest", since_days=0)
