"""fetch_irs_form_checksums — the fetcher `detect_source_changes` has been waiting for (Phase 3).

Watches the FINAL form/instruction PDFs our authorities point at (`AuthorityVersion.retrieval_url`
on current versions) and opens a DETECTED item when one's bytes change. HEAD-first: a GET+hash
only happens when ETag / Last-Modified / Content-Length moved (or we hold no HEAD state yet), so
the daily run is a handful of HEAD requests against unchanged files.

State model — three layers, deliberately distinct:
  · `AuthorityVersion.checksum_sha256` — the authority record. Written ONLY when null (first-run
    baseline, logged loudly). A detected CHANGE never overwrites it: the human who triages the
    item updates the version through the proper flow, so the register and the record can't drift
    silently. (Regression #3: a null-checksum first run records baselines and opens NOTHING.)
  · The feed row's `last_content` — JSON HEAD-state per URL ({etag, last_modified, length,
    sha256-last-seen}). Poll bookkeeping, not authority data.
  · The register item — namespaced `CHK:<source_code>@<sha12>`, so the same new content is never
    double-opened, and a THIRD change after triage opens a fresh item.

DRAFTS ARE EXCLUDED by URL shape (`--dft`): a draft cycles weekly by design, and every re-post
would open a bogus "source moved" item. Drafts are `fetch_irs_drafts`'s job.

Seeding (one-time, local): `--seed-manifest D:\\dev\\delvio-tax\\resources\\irs_forms\\forms_manifest.json`
copies each manifest entry's irs_url + sha256 onto the matching AuthoritySource's current version
(matched on `official_url == irs_url`; unmatched entries are REPORTED, never guessed). Render
never depends on a path in another repo.

Usage:
  manage.py fetch_irs_form_checksums                 # poll (HEAD-first)
  manage.py fetch_irs_form_checksums --dry-run
  manage.py fetch_irs_form_checksums --seed-manifest <path>   # local one-time seed
"""
import hashlib
import json
import os
import urllib.request

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sources.change_register_helpers import open_detected
from sources.models import (
    AuthoritySource, AuthorityVersion, ChangeRegisterItem, FeedType, ItemKind, SourceFeedDefinition,
)

FEED_CODE = "IRS_FORM_CHECKSUMS"
USER_AGENT = "Mozilla/5.0 (compatible; delvio-rule-studio change-register; +https://kenlill.com)"
HEAD_KEYS = ("etag", "last_modified", "content_length")


def _http_head(url: str) -> dict:
    """HEAD the URL; returns the comparable header trio. Isolated for tests."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        h = resp.headers
        return {"etag": h.get("ETag") or "", "last_modified": h.get("Last-Modified") or "",
                "content_length": h.get("Content-Length") or ""}


def _http_get_bytes(url: str) -> bytes:
    """GET the full document. Isolated for tests."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
        return resp.read()


class Command(BaseCommand):
    help = "Detect changed final-form PDFs by HEAD-first checksum polling (funnel Phase 3)."

    def add_arguments(self, parser):
        parser.add_argument("--seed-manifest",
                            help="Local one-time seed: path to delvio-tax forms_manifest.json.")
        parser.add_argument("--dry-run", action="store_true", help="Report; write nothing at all.")

    # ── Seeding ────────────────────────────────────────────────────────────

    def _seed(self, path: str, dry_run: bool):
        if not os.path.exists(path):
            raise CommandError(f"Manifest not found: {path}")
        with open(path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        entries = manifest.get("forms")
        if not isinstance(entries, list) or not entries:
            raise CommandError("Manifest has no 'forms' list — wrong file?")

        seeded, already, unmatched = 0, 0, []
        for entry in entries:
            url, sha = entry.get("irs_url"), entry.get("sha256")
            if not url or not sha:
                unmatched.append(f"{entry.get('form_code', '?')} (no url/sha)")
                continue
            src = AuthoritySource.objects.filter(official_url=url).first()
            if src is None:
                unmatched.append(f"{entry.get('form_code', '?')} ({url})")
                continue
            version = AuthorityVersion.objects.filter(authority_source=src, is_current=True).first()
            if version is None:
                if dry_run:
                    seeded += 1
                    continue
                version = AuthorityVersion.objects.create(
                    authority_source=src, version_label=f"TY{entry.get('tax_year', '?')} manifest seed",
                    retrieval_url=url, file_type="pdf", checksum_sha256=sha, is_current=True)
                seeded += 1
                continue
            if version.retrieval_url and version.checksum_sha256:
                already += 1
                continue
            if not dry_run:
                version.retrieval_url = version.retrieval_url or url
                version.checksum_sha256 = version.checksum_sha256 or sha
                version.save(update_fields=["retrieval_url", "checksum_sha256"])
            seeded += 1

        self.stdout.write(f"seed: {seeded} version(s) seeded / {already} already seeded / "
                          f"{len(unmatched)} manifest entr(ies) with no matching AuthoritySource")
        for miss in unmatched:
            self.stdout.write(f"  UNMATCHED (create the AuthoritySource or fix official_url): {miss}")

    # ── Polling ────────────────────────────────────────────────────────────

    def handle(self, *args, **o):
        if o.get("seed_manifest"):
            self._seed(o["seed_manifest"], o["dry_run"])
            return

        self.stdout.write(self.style.MIGRATE_HEADING("\nIRS final-form checksum poll (HEAD-first)\n"))

        if o["dry_run"]:
            feed = SourceFeedDefinition.objects.filter(feed_code=FEED_CODE).first()
        else:
            feed, _ = SourceFeedDefinition.objects.get_or_create(
                feed_code=FEED_CODE,
                defaults={
                    "feed_name": "IRS final form/instruction PDF checksums",
                    "jurisdiction_code": "US", "source_family": "IRS_FORMS",
                    "base_url": "https://www.irs.gov/pub/irs-pdf/", "feed_type": FeedType.PDF_LIST,
                    "refresh_frequency": "daily", "parser_strategy": "head_then_hash",
                    "arm_command": "fetch_irs_form_checksums",
                    "notes": "HEAD-state JSON lives in last_content. Drafts excluded by URL shape.",
                },
            )

        head_state: dict = {}
        if feed is not None and feed.last_content:
            try:
                head_state = json.loads(feed.last_content)
            except ValueError:
                head_state = {}

        versions = (AuthorityVersion.objects
                    .filter(is_current=True, retrieval_url__isnull=False)
                    .exclude(retrieval_url="")
                    .select_related("authority_source"))

        watched = baselined = unchanged = moved = skipped_drafts = errors = 0
        for version in versions:
            url = version.retrieval_url.strip()
            if "--dft" in url:
                skipped_drafts += 1
                continue
            watched += 1
            src = version.authority_source
            prior = head_state.get(url) or {}

            try:
                head = _http_head(url)
            except Exception as e:  # noqa: BLE001 — one bad URL must not kill the sweep
                errors += 1
                self.stderr.write(self.style.ERROR(f"HEAD failed for {src.source_code}: {e!r}"))
                continue

            if prior and all(prior.get(k) == head[k] for k in HEAD_KEYS) and version.checksum_sha256:
                unchanged += 1
                continue

            try:
                body = _http_get_bytes(url)
            except Exception as e:  # noqa: BLE001
                errors += 1
                self.stderr.write(self.style.ERROR(f"GET failed for {src.source_code}: {e!r}"))
                continue
            sha = hashlib.sha256(body).hexdigest()
            head["sha256"] = sha
            head_state[url] = head

            if not version.checksum_sha256:
                # First contact: record the baseline, open NOTHING (regression #3).
                baselined += 1
                self.stdout.write(f"BASELINE {src.source_code}: {sha[:16]} recorded "
                                  f"({'dry-run — not saved' if o['dry_run'] else 'saved'})")
                if not o["dry_run"]:
                    version.checksum_sha256 = sha
                    version.save(update_fields=["checksum_sha256"])
                continue

            if sha == version.checksum_sha256:
                unchanged += 1
                continue

            res = open_detected(
                external_ref=f"CHK:{src.source_code}@{sha[:12]}",
                title=f"Source moved: {src.source_code} — {src.title[:120]}",
                summary=(f"The document at {url} changed.\n"
                         f"Stored checksum (version '{version.version_label}'): {version.checksum_sha256}\n"
                         f"New checksum: {sha}\n"
                         "Re-verify the source; update the AuthorityVersion through the normal flow "
                         "once triage confirms what changed. Dependent rules: see the digest's "
                         "blast radius (stale_rules_report --source works too)."),
                jurisdiction=src.jurisdiction_code or "US",
                item_kind=ItemKind.FINAL_FORM,
                source_url=url,
                authority_source=src,
                authority_version=version,
                feed=feed,
                dry_run=o["dry_run"],
            )
            if res.skipped:
                unchanged += 1
                continue
            moved += 1
            label = "WOULD OPEN" if o["dry_run"] else f"DETECTED {res.change_code}"
            self.stdout.write(self.style.SUCCESS(f"{label}: {src.source_code} checksum moved"))

        if not o["dry_run"] and feed is not None:
            feed.last_polled_at = timezone.now()
            feed.last_content = json.dumps(head_state)
            feed.last_result_note = (f"ok · {watched} watched / {moved} moved / {baselined} baselined / "
                                     f"{unchanged} unchanged / {errors} fetch error(s)")
            feed.save(update_fields=["last_polled_at", "last_content", "last_result_note"])

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"fetch_irs_form_checksums: {watched} watched / {moved} moved / "
                          f"{baselined} baselined / {unchanged} unchanged / "
                          f"{skipped_drafts} draft URL(s) excluded / {errors} error(s)")
        if watched == 0:
            self.stdout.write(self.style.WARNING(
                "  ⚠ Nothing is watched — no current AuthorityVersion carries a retrieval_url. "
                "Run --seed-manifest locally against delvio-tax's forms_manifest.json."))
        self.stdout.write("=" * 60)
        if watched and errors == watched:
            raise CommandError("Every watched URL failed to fetch — treat as an arm outage.")
