"""fetch_ecfr_title26 — FEED_POLL leg 3 of the change-register funnel.

Tracks SECTION-LEVEL amendments to 26 CFR (Treasury regulations) via the free eCFR versioner API
(no key). Complements `fetch_federal_register`: the FR tells you a rule DOCUMENT published; this
tells you which regulation SECTIONS actually moved as a result — and `identifier` ('1.199A-3')
maps straight onto `AuthoritySource.citation`, so the relevance scorer can match exactly rather
than by keyword.

Volume is trivial: 46 section-versions for all of Title 26 in the first seven months of 2026.

⚠ FILTER ON `amendment_date`, NOT `issue_date`. eCFR re-issues unamended sections, so `issue_date`
moves without anything changing. Verified live 2026-08-05: §1.0-1 carries issue_date 2026-04-03
with amendment_date 2016-12-19 — filtering on issue_date would report a 2016 amendment as a 2026
change, four times over in one year. The API query still uses issue_date[gte] because that is the
only server-side date filter available, and since issue_date >= amendment_date always holds, the
query returns a SUPERSET which we then narrow client-side.

Verified 2026-08-05 against the live API:
  GET /api/versioner/v1/titles.json                 -> titles[] with {number, latest_amended_on, ...}
  GET /api/versioner/v1/versions/title-26.json      -> {'content_versions': [...], 'meta': {...}}
  content_versions[] keys: date, amendment_date, issue_date, identifier, name, part, substantive,
                           removed, subpart, title, type

Usage:
  manage.py fetch_ecfr_title26                       # amendments in the last 30 days, perimeter parts
  manage.py fetch_ecfr_title26 --since 2026-01-01
  manage.py fetch_ecfr_title26 --parts 1,301,602 --include-nonsubstantive
  manage.py fetch_ecfr_title26 --all-parts
  manage.py fetch_ecfr_title26 --dry-run             # report; open nothing
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sources.change_register_helpers import open_detected, parse_csv
from sources.models import FeedType, ItemKind, SourceFeedDefinition
from sources.relevance import build_perimeter_index, score_summary

TITLES_API = "https://www.ecfr.gov/api/versioner/v1/titles.json"
VERSIONS_API = "https://www.ecfr.gov/api/versioner/v1/versions/title-26.json"
SECTION_URL = "https://www.ecfr.gov/current/title-26/section-{identifier}"
USER_AGENT = "sherpa-tax-rule-studio change-register (+https://kenlill.com)"

FEED_CODE = "ECFR_TITLE26"
DEFAULT_LOOKBACK_DAYS = 30

# 26 CFR parts inside the perimeter:
#   1   — income tax (the overwhelming majority of what we file)
#   301 — procedure and administration
#   602 — OMB control numbers (moves when a form's paperwork burden changes)
# Deliberately excluded by default: 20 (estate), 25 (gift), 48/53/54/58 (excise, pensions),
# 300 (user fees). Live sample: part 1 = 20 records, 54 = 10, 20 = 6, 48 = 4, 301 = 3.
DEFAULT_PARTS = ("1", "301", "602")


def _http_get_json(url: str) -> dict:
    """Isolated network call — monkeypatched in tests so the suite never hits the network."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as resp:  # noqa: S310 (fixed https host)
        return json.loads(resp.read().decode("utf-8"))


def title26_latest_amended_on() -> str | None:
    """The cheap pre-check: one small request telling us whether Title 26 moved at all."""
    data = _http_get_json(TITLES_API)
    for t in data.get("titles", []):
        if t.get("number") == 26:
            return t.get("latest_amended_on")
    return None


def fetch_versions(since: str) -> list[dict]:
    """Return content_versions[] for Title 26 with issue_date >= since (a superset — see module docs)."""
    url = f"{VERSIONS_API}?{urllib.parse.urlencode({'issue_date[gte]': since})}"
    return _http_get_json(url).get("content_versions", [])


def select_amendments(records, since: str, parts, include_nonsubstantive: bool) -> list[dict]:
    """Narrow raw content_versions to real, in-perimeter amendments.

    Order matters for auditability, so each filter is explicit rather than one compound
    comprehension: date first (the issue_date trap), then substance, then part.
    """
    out = []
    for r in records:
        amended = r.get("amendment_date")
        if not amended or amended < since:
            continue                                        # ← the issue_date trap
        # A removal is always substantive news, whatever the flag says.
        if not include_nonsubstantive and not r.get("substantive") and not r.get("removed"):
            continue
        if parts and str(r.get("part")) not in parts:
            continue
        out.append(r)
    # Same section can appear twice (different issue_dates, one amendment) — external_ref keys on
    # identifier@amendment_date so those collapse, but de-dup here too for honest counting.
    seen, deduped = set(), []
    for r in out:
        key = (r.get("identifier"), r.get("amendment_date"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    return sorted(deduped, key=lambda r: (r.get("amendment_date") or "", r.get("identifier") or ""), reverse=True)


class Command(BaseCommand):
    help = "Open DETECTED change-register items from recent 26 CFR section amendments (FEED_POLL leg 3)."

    def add_arguments(self, parser):
        parser.add_argument("--since", help="Earliest amendment_date YYYY-MM-DD (default: today - lookback-days).")
        parser.add_argument("--lookback-days", type=int, default=DEFAULT_LOOKBACK_DAYS)
        parser.add_argument("--parts", help=f"Comma 26 CFR parts (default {','.join(DEFAULT_PARTS)}).")
        parser.add_argument("--all-parts", action="store_true", help="Do not filter by part.")
        parser.add_argument("--include-nonsubstantive", action="store_true",
                            help="Include records flagged substantive=false (normally editorial re-issues).")
        parser.add_argument("--force", action="store_true",
                            help="Skip the 'Title 26 unchanged since last poll' short-circuit.")
        parser.add_argument("--dry-run", action="store_true", help="Report; open nothing.")

    def handle(self, *args, **o):
        since = o.get("since") or (timezone.now().date() - timedelta(days=o["lookback_days"])).isoformat()
        parts = () if o["all_parts"] else tuple(parse_csv(o.get("parts")) or DEFAULT_PARTS)

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n26 CFR — section amendments since {since}"
            f"{' · parts ' + ','.join(parts) if parts else ' · all parts'}\n"))

        # --dry-run must write NOTHING, including the feed row — otherwise "report, change
        # nothing" quietly isn't true and the flag stops being trustworthy.
        if o["dry_run"]:
            feed = SourceFeedDefinition.objects.filter(feed_code=FEED_CODE).first()
        else:
            feed, _ = SourceFeedDefinition.objects.get_or_create(
                feed_code=FEED_CODE,
                defaults={
                    "feed_name": "eCFR Title 26 — section version history",
                    "jurisdiction_code": "US", "source_family": "IRS_REGS", "base_url": VERSIONS_API,
                    "feed_type": FeedType.JSON_API, "refresh_frequency": "daily",
                    "parser_strategy": "json_api", "arm_command": "fetch_ecfr_title26",
                    "notes": "Filter on amendment_date, not issue_date — see the command docstring.",
                },
            )

        try:
            latest = title26_latest_amended_on()
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
            raise CommandError(f"eCFR titles.json fetch failed: {e!r}")

        # `last_content` holds the last-seen latest_amended_on for this JSON arm — the API
        # equivalent of the page-diff arms' normalized page text.
        if latest and feed is not None and feed.last_content == latest and not o["force"]:
            self.stdout.write(f"Title 26 unchanged since last poll (latest_amended_on={latest}) — skipping. "
                              f"Use --force to poll anyway.")
            if not o["dry_run"]:
                feed.last_polled_at = timezone.now()
                feed.last_result_note = f"short-circuit · latest_amended_on={latest}"
                feed.save(update_fields=["last_polled_at", "last_result_note"])
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("fetch_ecfr_title26: 0 fetched / 0 opened / short-circuited")
            self.stdout.write("=" * 60)
            return

        try:
            records = fetch_versions(since)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
            raise CommandError(f"eCFR versions fetch failed: {e!r}")

        selected = select_amendments(records, since, parts, o["include_nonsubstantive"])
        index = build_perimeter_index()

        opened = skipped = 0
        for r in selected:
            identifier = r.get("identifier") or ""
            amended = r.get("amendment_date")
            ext_ref = f"CFR26:{identifier}@{amended}"
            name = (r.get("name") or f"26 CFR {identifier}").strip()
            url = SECTION_URL.format(identifier=identifier)
            flag = " [REMOVED]" if r.get("removed") else ""

            res = open_detected(
                external_ref=ext_ref,
                title=f"26 CFR {identifier} amended {amended}{flag}",
                summary=(f"[26 CFR §{identifier} · amended {amended} · part {r.get('part')}]\n{name}\n"
                         f"{'Section REMOVED.' if r.get('removed') else ''}\n"
                         f"Substantive: {r.get('substantive')}. eCFR issue_date {r.get('issue_date')}.\n"
                         f"{url}"),
                index=index, text=name, cfr=[identifier], jurisdiction="US",
                item_kind=ItemKind.CFR_SECTION, source_url=url, published_date=amended,
                dry_run=o["dry_run"],
            )
            if res.skipped:
                skipped += 1
                continue
            opened += 1
            line = f"{identifier:<16} {amended}  score {res.score:>3}  {score_summary(res.signals)}"
            if o["dry_run"]:
                self.stdout.write(self.style.WARNING(f"NEW  {line}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"DETECTED {res.change_code}: {line}"))

        if not o["dry_run"] and feed is not None:
            feed.last_polled_at = timezone.now()
            feed.last_content = latest or feed.last_content
            feed.last_result_note = (f"ok · latest_amended_on={latest} · {len(records)} fetched / "
                                     f"{len(selected)} in perimeter / {opened} opened")
            feed.save(update_fields=["last_polled_at", "last_content", "last_result_note"])

        self.stdout.write("\n" + "=" * 60)
        verb = "would open" if o["dry_run"] else "opened"
        self.stdout.write(f"fetch_ecfr_title26: {len(records)} fetched / {len(selected)} in perimeter / "
                          f"{opened} {verb} / {skipped} already-known")
        dropped = len(records) - len(selected)
        if dropped:
            # Never let a filter be silent — a count you can't see is a count you can't audit.
            self.stdout.write(f"  ({dropped} filtered out: pre-{since} amendment_date, non-substantive, "
                              f"or outside parts {','.join(parts) if parts else '(none)'})")
        self.stdout.write("=" * 60)
