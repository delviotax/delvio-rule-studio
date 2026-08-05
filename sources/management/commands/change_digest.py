"""change_digest — render and deliver the weekly change-register digest (funnel Phase 2).

This is what turns register rows into a process Ken actually runs: the Friday email. It is
READ-ONLY against the register — rendering and delivery only; triage happens in the RS admin the
email links to.

Delivery ladder:
  --email        send via Resend (RESEND_API_KEY; from rules@delviotax.com, to DIGEST_EMAIL_TO
                 or ken@delviotax.com), plus a Pushover count ping when configured. If the API
                 key is missing the digest falls back to stdout and says so — a missing key must
                 not silently eat the week's findings, but it also should not page Render red.
  (no --email)   print the text digest to stdout.

A Resend REJECTION (key present, send failed) exits non-zero so the Friday cron shows red —
that is a real delivery outage.

Usage:
  manage.py change_digest                          # print to stdout
  manage.py change_digest --since-days 7 --email   # the Friday cron line
  manage.py change_digest --threshold 40 --to me@example.com --email
"""
from django.core.management.base import BaseCommand, CommandError

from sources import digest as dg
from sources.emailer import EmailNotConfigured, send_digest_email
from sources.management.commands.poll_change_feeds import _notify
from sources.relevance import DEFAULT_DIGEST_THRESHOLD


class Command(BaseCommand):
    help = "Render (and optionally email) the weekly change-register digest. Read-only."

    def add_arguments(self, parser):
        parser.add_argument("--since-days", type=int, default=7,
                            help="Window for new items (default 7 — the Friday cadence).")
        parser.add_argument("--threshold", type=int, default=DEFAULT_DIGEST_THRESHOLD,
                            help=f"Above/below-the-line display split (default {DEFAULT_DIGEST_THRESHOLD}). "
                                 "Display only — every item is shown somewhere regardless.")
        parser.add_argument("--email", action="store_true", help="Deliver via Resend (else stdout).")
        parser.add_argument("--to", help="Override recipient(s), comma-separated.")

    def handle(self, *args, **o):
        if o["since_days"] < 1:
            raise CommandError("--since-days must be >= 1.")

        data = dg.collect(since_days=o["since_days"], threshold=o["threshold"])
        text = dg.render_text(data)
        subject = dg.subject_line(data)

        if not o["email"]:
            self.stdout.write(text)
            return

        html = dg.render_html(data)
        try:
            recipients = send_digest_email(subject, html, text, to=o.get("to"))
        except EmailNotConfigured:
            self.stdout.write(self.style.WARNING(
                "RESEND_API_KEY is not set — printing the digest instead of emailing it. "
                "Set it (sync:false) on the Render cron to enable delivery.\n"))
            self.stdout.write(text)
            return
        except Exception as e:  # noqa: BLE001 — a real delivery failure must page
            raise CommandError(f"Digest email delivery failed: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Digest sent to {', '.join(recipients)} — {subject}"))
        if _notify(subject):
            self.stdout.write("Pushover: sent")
