"""Captured real markup for the detection-arm parsers.

Every fixture here was taken VERBATIM from the live page on the date noted, then trimmed to a
handful of rows. When a parser test fails, the first question is "did irs.gov change?" — so these
must stay recognisably real. Do not hand-simplify the markup to make a regex easier.

Captured 2026-08-05 from:
  https://www.irs.gov/downloads/irs-drop
  https://www.irs.gov/downloads/irs-dft
"""

# The real 4-cell row template, whitespace-for-whitespace. `%s`-substituted by _row().
_ROW_TEMPLATE = (
    '<tr>\n'
    '                                                                                      '
    '<td headers="view-uri-table-column" class="views-field views-field-uri">'
    '<a href="https://www.irs.gov/pub/%(slug)s/%(filename)s">%(filename)s</a>          </td>\n'
    '                                                                                      '
    '<td headers="view-field-pup-posted-table-column" class="views-field '
    'views-field-field-pup-posted is-active">%(posted)s %(time)s          </td>\n'
    '                                                                                      '
    '<td headers="view-filesize-table-column" class="views-field views-field-filesize">'
    '%(size)s          </td>\n'
    '                                                                                      '
    '<td headers="view-name-table-column" class="views-field views-field-name">'
    '%(desc)s          </td>\n'
    '              </tr>'
)

_PAGE_TEMPLATE = (
    '<html><body><table class="views-table tablesaw cols-4" data-tablesaw-mode="stack">\n'
    '<thead><tr>'
    '<th id="view-uri-table-column" class="views-field views-field-uri" scope="col">'
    '<a href="?order=uri&amp;sort=desc" title="sort by Name">Name</a></th>'
    '<th id="view-field-pup-posted-table-column" class="views-field views-field-field-pup-posted '
    'is-active" scope="col"><a href="?order=field_pup_posted&amp;sort=asc" title="sort by Date">Date</a></th>'
    '<th id="view-filesize-table-column" class="views-field views-field-filesize" scope="col">'
    '<a href="?order=filesize&amp;sort=desc" title="sort by Size">Size</a></th>'
    '<th id="view-name-table-column" class="views-field views-field-name" scope="col">'
    '<a href="?order=name&amp;sort=desc" title="sort by Description">Description</a></th>'
    '</tr></thead>\n<tbody>\n%s\n</tbody></table></body></html>'
)


def _row(slug, filename, posted, time, size, desc):
    return _ROW_TEMPLATE % {
        "slug": slug, "filename": filename, "posted": posted,
        "time": time, "size": size, "desc": desc,
    }


def page(slug, rows):
    """Wrap (filename, posted, time, size, desc) tuples into a full listing page."""
    return _PAGE_TEMPLATE % "\n".join(_row(slug, *r) for r in rows)


# ── irs-drop: the six newest rows as of 2026-08-05, verbatim values ────────
# Note the description inconsistency this fixture deliberately preserves:
#   'Rev. Proc.  2026-28' (two spaces) / 'RR-2026-13' / 'N-2026-44'
# — which is exactly why the parsers derive designation from the FILENAME.
DROP_ROWS = [
    ("rp-26-28.pdf",            "2026-07-24", "10:00:00", "88.05 KB",  "Rev. Proc.  2026-28"),
    ("rp-26-26.pdf",            "2026-07-21", "10:00:00", "104.3 KB",  "Rev. Proc. 2026-26"),
    ("rr-26-13.pdf",            "2026-07-15", "10:00:00", "87.07 KB",  "RR-2026-13"),
    ("n-26-44.pdf",             "2026-07-14", "10:00:00", "190.43 KB", "N-2026-44"),
    ("n-26-39-appendix-2.xlsx", "2026-07-10", "10:00:00", "17.83 KB",  "N-2026-39 Appendix 2"),
    ("rp-26-25.pdf",            "2026-06-29", "10:00:00", "75.98 KB",  "Rev. Proc. 2026-25"),
]

# ── irs-dft: the six newest rows as of 2026-08-05, verbatim values ─────────
# Preserves the heavy internal space padding and the two `lead` forms:
# a tax year ('2026') and an MMYY revision stamp ('1226' = Dec 2026).
DFT_ROWS = [
    ("i8615--dft.pdf",   "2026-08-04", "19:10:49", "329.79 KB", "2026 Inst 8615                           (PDF)"),
    ("f9465sp--dft.pdf", "2026-08-04", "19:10:49", "280.39 KB", "1226 Form 9465 (sp)                      (PDF)"),
    ("f1062sa--dft.pdf", "2026-08-04", "19:10:49", "124.16 KB", "1226 Form 1062 (Schedule A)              (PDF)"),
    ("i1040sr--dft.pdf", "2026-08-04", "19:10:49", "284.8 KB",  "2026 Inst 1040 (Schedule R)              (PDF)"),
    ("f4797--dft.pdf",   "2026-08-04", "19:10:49", "180.78 KB", "2026 Form 4797                           (PDF)"),
    ("f8997--dft.pdf",   "2026-08-04", "19:10:49", "180.78 KB", "2026 Form 8997                           (PDF)"),
]


def drop_page(rows=None):
    return page("irs-drop", DROP_ROWS if rows is None else rows)


def dft_page(rows=None):
    return page("irs-dft", DFT_ROWS if rows is None else rows)


# ── eCFR versioner API, captured verbatim 2026-08-05 ──────────────────────
ECFR_TITLES_JSON = {
    "titles": [
        {"number": 25, "name": "Indians", "latest_amended_on": "2026-07-30",
         "latest_issue_date": "2026-07-30", "up_to_date_as_of": "2026-08-03", "reserved": False},
        {"number": 26, "name": "Internal Revenue", "latest_amended_on": "2026-08-03",
         "latest_issue_date": "2026-08-03", "up_to_date_as_of": "2026-08-03", "reserved": False},
    ]
}

# `1.0-1` is THE regression case: a recent issue_date carrying a 2016 amendment_date.
# Filtering on issue_date would report a ten-year-old amendment as this year's news.
ECFR_VERSIONS_JSON = {
    "content_versions": [
        {"date": "2016-12-19", "amendment_date": "2016-12-19", "issue_date": "2026-04-03",
         "identifier": "1.0-1", "name": "§ 1.0-1   Internal Revenue Code of 1954 and regulations.",
         "part": "1", "substantive": False, "removed": False, "subpart": None,
         "title": "26", "type": "section"},
        {"date": "2026-07-09", "amendment_date": "2026-07-09", "issue_date": "2026-07-09",
         "identifier": "1.101-1",
         "name": "§ 1.101-1   Exclusion from gross income of proceeds of life insurance contracts.",
         "part": "1", "substantive": True, "removed": False, "subpart": None,
         "title": "26", "type": "section"},
        {"date": "2026-07-24", "amendment_date": "2026-07-24", "issue_date": "2026-07-24",
         "identifier": "20.2056A-2", "name": "§ 20.2056A-2   Requirements for qualified domestic trust.",
         "part": "20", "substantive": True, "removed": False, "subpart": None,
         "title": "26", "type": "section"},
        {"date": "2026-07-30", "amendment_date": "2026-07-30", "issue_date": "2026-07-30",
         "identifier": "301.7701-3", "name": "§ 301.7701-3   Classification of certain business entities.",
         "part": "301", "substantive": True, "removed": False, "subpart": None,
         "title": "26", "type": "section"},
        {"date": "2026-08-03", "amendment_date": "2026-08-03", "issue_date": "2026-08-03",
         "identifier": "1.199A-3", "name": "§ 1.199A-3   Qualified business income.",
         "part": "1", "substantive": True, "removed": False, "subpart": None,
         "title": "26", "type": "section"},
        {"date": "2026-08-03", "amendment_date": "2026-08-03", "issue_date": "2026-08-03",
         "identifier": "1.9999-9", "name": "§ 1.9999-9   Obsolete provision.",
         "part": "1", "substantive": False, "removed": True, "subpart": None,
         "title": "26", "type": "section"},
    ],
    "meta": {"title": "26"},
}


# ── CourtListener v4 search, response-shaped per the documented v4 search schema ──
# (Search endpoint verified 200 unauthenticated 2026-08-05; /opinions/ 401s.)
CL_SEARCH_TAX_JSON = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {"cluster_id": 9911001, "caseName": "Smith v. Commissioner of Internal Revenue",
         "court": "United States Tax Court", "court_id": "tax", "dateFiled": "2026-07-28",
         "snippet": "…the section 179 deduction claimed on Form 4562 for the passenger automobile…",
         "absolute_url": "/opinion/9911001/smith-v-commissioner/"},
        {"cluster_id": 9911002, "caseName": "Estate of Doe v. Commissioner",
         "court": "United States Tax Court", "court_id": "tax", "dateFiled": "2026-07-21",
         "snippet": "…valuation of closely held stock for estate tax purposes…",
         "absolute_url": "/opinion/9911002/estate-of-doe-v-commissioner/"},
        # A row missing its cluster_id — must be counted unusable, not crash the arm.
        {"caseName": "Malformed Row v. Commissioner", "dateFiled": "2026-07-20",
         "snippet": "", "absolute_url": ""},
    ],
}

CL_SEARCH_CA11_JSON = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {"cluster_id": 9922001, "caseName": "United States v. Jones",
         "court": "Court of Appeals for the Eleventh Circuit", "court_id": "ca11",
         "dateFiled": "2026-07-30",
         "snippet": "…conviction under 26 U.S.C. § 7201 for evasion of the qualified business income…",
         "absolute_url": "/opinion/9922001/us-v-jones/"},
    ],
}


# ── A real excerpt of extracted rp-26-28 text ─────────────────────────────
# Verbatim output of pdf_text.extract_text() on the live PDF, 2026-08-05. Kern-split exactly as
# the extractor produces it. This is the canonical "scores LOW" relevance case: exempt
# organizations / Form 990 territory, nothing to do with the 1040/1065/1120-S perimeter.
RP_26_28_EXTRACT = (
    "Arial Arial Adobe UCS 1     P a r t III       A dm i ni s t r at i v e,   P r oc e d ur al ,  "
    "an d M i s c el l an eou s         26 C F R  1. 603 3 - 2 :   R et ur ns  by   ex e m pt  "
    "or ga ni z at i ons   and  r et ur ns  by   c er t ai n n on ex e m pt   or gani z a t i ons . "
    "        R e v.   P r o c.    20 26 - 28         S E CT I O N 1 .  P URP O S E         "
    "T hi s  r ev en ue  p r oc ed ur e  p r ov i d es  gu i d an c e  t o  ex e m pt  "
    "or ga ni z at i ons  f i l i ng  F or m  990 ."
)
