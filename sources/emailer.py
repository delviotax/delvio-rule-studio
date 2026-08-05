"""emailer — Resend delivery for the Friday change digest.

One function, stdlib-only (urllib), so the cron needs no new dependency. The Resend account's
verified sending domain is delviotax.com (checked 2026-08-05), hence the defaults below. The
API key comes ONLY from the environment (`RESEND_API_KEY`, set sync:false on the Render cron;
the local copy lives in `D:\\dev\\Passwords & Secrets\\resend-api-key.txt`) — never from a file
inside the repo.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

RESEND_ENDPOINT = "https://api.resend.com/emails"
DEFAULT_FROM = "Delvio Rule Studio <rules@delviotax.com>"
DEFAULT_TO = "ken@delviotax.com"


class EmailNotConfigured(RuntimeError):
    """RESEND_API_KEY is unset — the caller decides whether that is fatal."""


def send_digest_email(subject: str, html: str, text: str, *, to: str | None = None) -> list[str]:
    """Send via Resend. Returns the recipient list on success; raises on failure.

    `to` (or DIGEST_EMAIL_TO) may be a comma-separated list. Raises EmailNotConfigured when no
    API key is present so change_digest can fall back to stdout instead of dying quietly.
    """
    api_key = (os.getenv("RESEND_API_KEY") or "").strip()
    if not api_key:
        raise EmailNotConfigured("RESEND_API_KEY is not set")

    recipients = [a.strip() for a in (to or os.getenv("DIGEST_EMAIL_TO") or DEFAULT_TO).split(",")
                  if a.strip()]
    payload = {
        "from": os.getenv("DIGEST_EMAIL_FROM") or DEFAULT_FROM,
        "to": recipients,
        "subject": subject,
        "html": html,
        "text": text,
    }
    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (fixed https host)
            resp.read()
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:  # noqa: BLE001
            pass
        raise RuntimeError(f"Resend rejected the digest: HTTP {e.code} {body}") from e
    return recipients
