"""digest — assemble and render the weekly change-register digest.

Pure logic (no I/O beyond the ORM) so `change_digest` stays a thin CLI and tests can call these
functions directly. Section design mirrors the plan:

  · ABOVE THE LINE — this window's items at/above the display threshold, ranked by score, each with
    its relevance signals AND its blast radius inline ("these N authored rules cite it") — the
    payoff line that turns "something changed" into "here is what to re-verify".
  · UNSCORED rides above the line too: an item the scorer couldn't read is exactly the item a
    human must see (relevance invariant #2).
  · BELOW THE LINE — collapsed but NEVER hidden. The threshold is a display knob, not a gate.
  · AGING — anything still DETECTED after AGING_DAYS, however old, so nothing rots un-triaged.
  · ARM HEALTH — every feed with an owning arm_command: when it last ran and what it said,
    including arms that parsed ZERO rows. A silently-dead scraper is this system's worst
    failure mode; this section is where it becomes visible.

Blast radius reuses stale_rules_report's linkage semantics (cites_source > named >
on_affected_form) but sources candidate forms from the item's relevance SIGNALS as well as its
affected_forms — automated arms rarely set affected_forms, but their signals carry the form hits.
"""
from __future__ import annotations

import datetime as dt
import os
from dataclasses import dataclass, field

from django.utils import timezone

from sources.models import ChangeRegisterItem, ChangeStatus, RuleAuthorityLink, SourceFeedDefinition
from sources.relevance import DEFAULT_DIGEST_THRESHOLD, score_summary

AGING_DAYS = 14
STALE_ARM_DAYS = 2          # a daily-polled arm silent this long is flagged in arm health
BLAST_RADIUS_LIMIT = 6      # rules shown per item; the full count is always printed

RS_BASE_URL_DEFAULT = "https://sherpa-tax-rule-studio.onrender.com"


def rs_base_url() -> str:
    return (os.getenv("RS_BASE_URL") or RS_BASE_URL_DEFAULT).rstrip("/")


def admin_url(item: ChangeRegisterItem) -> str:
    return f"{rs_base_url()}/admin/sources/changeregisteritem/{item.pk}/change/"


# ── Blast radius ───────────────────────────────────────────────────────────

@dataclass
class BlastRadius:
    total: int = 0
    shown: list[dict] = field(default_factory=list)   # {rule_id, form_number, reason}


_REASON_RANK = {"cites_source": 0, "named": 1, "on_affected_form": 2}


def blast_radius(item: ChangeRegisterItem, limit: int = BLAST_RADIUS_LIMIT) -> BlastRadius:
    """Which authored rules does this item put in question? Read-only, same semantics as
    stale_rules_report (D-26: report, never auto-edit)."""
    from specs.models import FormRule

    found: dict = {}

    def _add(rule, reason):
        cur = found.get(rule.pk)
        if cur and _REASON_RANK[cur["reason"]] <= _REASON_RANK[reason]:
            return
        found[rule.pk] = {"rule": rule, "reason": reason}

    if item.authority_source_id:
        for link in (RuleAuthorityLink.objects
                     .filter(authority_source_id=item.authority_source_id)
                     .select_related("form_rule", "form_rule__tax_form")):
            _add(link.form_rule, "cites_source")

    if item.affected_rule_ids:
        for rule in FormRule.objects.filter(rule_id__in=item.affected_rule_ids).select_related("tax_form"):
            _add(rule, "named")

    forms = set(item.affected_forms or [])
    for sig in item.relevance_signals or []:
        if sig.get("kind") in {"form", "entity"} and sig.get("value"):
            forms.add(str(sig["value"]))
    if forms:
        for rule in (FormRule.objects.filter(tax_form__form_number__in=forms)
                     .select_related("tax_form")):
            _add(rule, "on_affected_form")

    rows = sorted(found.values(),
                  key=lambda r: (_REASON_RANK[r["reason"]], r["rule"].tax_form.form_number, r["rule"].rule_id))
    return BlastRadius(
        total=len(rows),
        shown=[{"rule_id": r["rule"].rule_id,
                "form_number": r["rule"].tax_form.form_number,
                "reason": r["reason"]} for r in rows[:limit]],
    )


# ── Collection ─────────────────────────────────────────────────────────────

def collect(since_days: int = 7, threshold: int = DEFAULT_DIGEST_THRESHOLD) -> dict:
    """Gather everything the digest renders. Queries only; no side effects."""
    now = timezone.now()
    cutoff = now - dt.timedelta(days=since_days)
    aging_cutoff = now - dt.timedelta(days=AGING_DAYS)

    window = list(ChangeRegisterItem.objects.filter(detected_at__gte=cutoff)
                  .select_related("authority_source")
                  .order_by("-relevance_score", "-detected_at"))

    above = [i for i in window if i.relevance_score is None or i.relevance_score >= threshold]
    below = [i for i in window if i.relevance_score is not None and i.relevance_score < threshold]
    # Unscored floats to the top of above-the-line: it needs eyes most.
    above.sort(key=lambda i: (0 if i.relevance_score is None else 1,
                              -(i.relevance_score or 0)))

    aging = list(ChangeRegisterItem.objects
                 .filter(status=ChangeStatus.DETECTED, detected_at__lt=aging_cutoff)
                 .order_by("detected_at"))

    arms = []
    for feed in SourceFeedDefinition.objects.exclude(arm_command="").order_by("feed_code"):
        note = (feed.last_result_note or "").strip()
        stale = (feed.last_polled_at is None
                 or feed.last_polled_at < now - dt.timedelta(days=STALE_ARM_DAYS))
        arms.append({
            "feed_code": feed.feed_code,
            "arm_command": feed.arm_command,
            "last_polled_at": feed.last_polled_at,
            "note": note or "(never ran)",
            "stale": stale,
            "zero_rows": "0 rows" in note,
        })

    radii = {i.pk: blast_radius(i) for i in above}

    return {
        "generated_at": now, "since_days": since_days, "threshold": threshold,
        "above": above, "below": below, "aging": aging, "arms": arms, "radii": radii,
    }


# ── Rendering ──────────────────────────────────────────────────────────────

_REASON_LABEL = {"cites_source": "cites the moved source", "named": "named in triage",
                 "on_affected_form": "on an affected form"}


def _item_head(item: ChangeRegisterItem) -> str:
    score = "unscored" if item.relevance_score is None else f"score {item.relevance_score}"
    kind = f" · {item.get_item_kind_display()}" if item.item_kind else ""
    pub = f" · published {item.published_date}" if item.published_date else ""
    return f"{item.change_code} [{score}]{kind}{pub} — {item.title}"


def render_text(data: dict) -> str:
    lines: list[str] = []
    w = lines.append
    w(f"RULE STUDIO CHANGE DIGEST — {data['generated_at']:%Y-%m-%d} "
      f"(last {data['since_days']} days, display threshold {data['threshold']})")
    w("=" * 72)

    w(f"\nABOVE THE LINE ({len(data['above'])}) — triage these")
    if not data["above"]:
        w("  (nothing this window)")
    for item in data["above"]:
        w(f"\n· {_item_head(item)}")
        if item.relevance_signals:
            w(f"    signals: {score_summary(item.relevance_signals, limit=6)}")
        br = data["radii"].get(item.pk)
        if br and br.total:
            shown = ", ".join(f"{r['form_number']}/{r['rule_id']}" for r in br.shown)
            more = f" (+{br.total - len(br.shown)} more)" if br.total > len(br.shown) else ""
            w(f"    blast radius: {br.total} authored rule(s) — {shown}{more}")
        else:
            w("    blast radius: no authored rules linked — check whether the change implies a NEW rule")
        if item.source_url:
            w(f"    document: {item.source_url}")
        w(f"    triage:   {admin_url(item)}")

    w(f"\nBELOW THE LINE ({len(data['below'])}) — low relevance, recorded not hidden")
    for item in data["below"]:
        w(f"  · {_item_head(item)}")

    if data["aging"]:
        w(f"\nAGING ({len(data['aging'])}) — still DETECTED after {AGING_DAYS}+ days")
        for item in data["aging"]:
            w(f"  · {item.change_code} detected {item.detected_at:%Y-%m-%d} — {item.title}")

    w("\nARM HEALTH")
    for arm in data["arms"]:
        flagged = " ⚠ STALE" if arm["stale"] else ""
        zero = " ⚠ parsed 0 rows" if arm["zero_rows"] else ""
        last = f"{arm['last_polled_at']:%Y-%m-%d %H:%M}" if arm["last_polled_at"] else "never"
        w(f"  {arm['feed_code']:<18} {arm['arm_command']:<26} last {last}{flagged}{zero}")
        w(f"      {arm['note']}")
    if not data["arms"]:
        w("  ⚠ no arm-bound feeds found — the pollers have never run against this database")
    w("")
    return "\n".join(lines)


def render_html(data: dict) -> str:
    """Deliberately plain HTML — an email client is not a place for a framework."""
    def esc(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    parts: list[str] = []
    p = parts.append
    p(f"<h2 style='margin:0 0 4px'>Rule Studio change digest — {data['generated_at']:%Y-%m-%d}</h2>")
    p(f"<p style='color:#555;margin:0 0 16px'>Last {data['since_days']} days · display threshold "
      f"{data['threshold']} · <a href='{esc(rs_base_url())}/admin/sources/changeregisteritem/'>open the register</a></p>")

    p(f"<h3 style='margin:16px 0 6px'>Above the line ({len(data['above'])})</h3>")
    if not data["above"]:
        p("<p>(nothing this window)</p>")
    for item in data["above"]:
        br = data["radii"].get(item.pk)
        p("<div style='border:1px solid #ccc;border-left:4px solid #2b5f8a;padding:8px 10px;margin:0 0 8px'>")
        p(f"<div><b>{esc(_item_head(item))}</b></div>")
        if item.relevance_signals:
            p(f"<div style='color:#555'>signals: {esc(score_summary(item.relevance_signals, limit=6))}</div>")
        if br and br.total:
            shown = ", ".join(f"{esc(r['form_number'])}/{esc(r['rule_id'])}" for r in br.shown)
            more = f" (+{br.total - len(br.shown)} more)" if br.total > len(br.shown) else ""
            p(f"<div><b>Blast radius: {br.total} authored rule(s)</b> — {shown}{more}</div>")
        else:
            p("<div style='color:#8a4b2b'>No authored rules linked — check whether this implies a NEW rule.</div>")
        links = []
        if item.source_url:
            links.append(f"<a href='{esc(item.source_url)}'>document</a>")
        links.append(f"<a href='{esc(admin_url(item))}'>triage in RS</a>")
        p(f"<div>{' · '.join(links)}</div></div>")

    p(f"<h3 style='margin:16px 0 6px'>Below the line ({len(data['below'])})</h3>")
    if data["below"]:
        p("<ul style='margin:0;color:#555'>")
        for item in data["below"]:
            p(f"<li>{esc(_item_head(item))}</li>")
        p("</ul>")
    else:
        p("<p>(none)</p>")

    if data["aging"]:
        p(f"<h3 style='margin:16px 0 6px;color:#8a2b2b'>Aging — still DETECTED after {AGING_DAYS}+ days "
          f"({len(data['aging'])})</h3><ul style='margin:0'>")
        for item in data["aging"]:
            p(f"<li>{esc(item.change_code)} detected {item.detected_at:%Y-%m-%d} — {esc(item.title)}</li>")
        p("</ul>")

    p(f"<h3 style='margin:16px 0 6px'>Arm health</h3><table style='border-collapse:collapse'>")
    for arm in data["arms"]:
        last = f"{arm['last_polled_at']:%Y-%m-%d %H:%M}" if arm["last_polled_at"] else "never"
        flags = ("<b style='color:#8a2b2b'> STALE</b>" if arm["stale"] else "") + \
                ("<b style='color:#8a2b2b'> 0 ROWS</b>" if arm["zero_rows"] else "")
        p(f"<tr><td style='padding:2px 10px 2px 0'><code>{esc(arm['feed_code'])}</code></td>"
          f"<td style='padding:2px 10px 2px 0'>last {esc(last)}{flags}</td>"
          f"<td style='padding:2px 0;color:#555'>{esc(arm['note'])}</td></tr>")
    p("</table>")
    if not data["arms"]:
        p("<p style='color:#8a2b2b'><b>No arm-bound feeds found — the pollers have never run against this database.</b></p>")
    return "\n".join(parts)


def subject_line(data: dict) -> str:
    unscored = sum(1 for i in data["above"] if i.relevance_score is None)
    bits = [f"{len(data['above'])} above the line", f"{len(data['below'])} below"]
    if unscored:
        bits.append(f"{unscored} unscored")
    if data["aging"]:
        bits.append(f"{len(data['aging'])} aging")
    return f"RS change digest {data['generated_at']:%Y-%m-%d}: " + ", ".join(bits)
