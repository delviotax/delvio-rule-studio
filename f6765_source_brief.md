# Form 6765 source brief — Credit for Increasing Research Activities (§41)

*Research pass 2026-08-04 (s212, delvio-tax CC loop session). Sources fetched and
read VERBATIM this date — nothing below is from memory.*

## Trigger

CC batch-005 #2 (packet 227, GOLD FUSION PROMOTIONS LLC): a real Form 6765 with
$53,704 of QREs and a $4,243 research credit flowing to Schedule K. RS lookup
`/api/forms/lookup/6765/export/` = **404 (GAP)**. Ken's go to author: 2026-08-04
("run the form 6765 rule studio spec").

## Sources in hand (scratchpad, fetched from irs.gov 2026-08-04)

| Source | Revision | Notes |
|---|---|---|
| `f6765.pdf` (form face, 4 pp) | **Rev. December 2024** | Lines A/B, 1-48 + Section G 49-56. |
| `i6765.pdf` (instructions, 12 pp) | **Rev. December 2025** — "For use with the January 2025 revision of Form 6765" | ⚠ revision-label mismatch vs the served face (12-2024); every line reference in the instructions matches the 12-2024 face as extracted — treated as the same structural revision. Flag for re-check when IRS posts a face stamped Jan-2025. |
| `i1120ssk.pdf` (Shareholder's Instructions for Schedule K-1) | current | Box 13 **code M** = "Credit for increasing research activities. Report this amount on Section C, line 29, of Form 6765" (verbatim). |

## Structure of the Rev. 12-2024 face (verified line-by-line)

- **Item A** — "Are you electing the reduced credit under section 280C?" Yes/No.
  Election is made HERE, on the original timely filed return incl. extensions
  (instructions "Reminders", verbatim).
- **Item B** — controlled group / common control Yes/No; Yes ⇒ required statement
  attachment (group credit computed at group level, member shares reported).
- **Section A — Regular credit (lines 1-13).** 1 energy consortia; 2-4 basic
  research payments over base; 5 total QREs (= line 48); 6 fixed-base percentage
  (**max 16%**); 7 average annual gross receipts (prior 4 years); 8 = 7 × 6;
  9 = 5 − 8 (floor 0); 10 = 5 × 50%; 11 = smaller of 9 or 10; 12 = 1 + 4 + 11;
  **13 = 12 × 15.8% if 280C elected, else × 20%** (+ required statement if not
  electing — see §280C below).
- **Section B — ASC (lines 14-26).** 14 energy consortia; 15-17 basic research
  over base; 18 = 14 + 17; 19 = 18 × 20%; 20 total QREs (= line 48); 21 prior-3-
  year total QREs; **22 = 21 ÷ 6.0**; 23 = 20 − 22 (floor 0); **24 = 23 × 14%**,
  or **20 × 6% if the taxpayer had no QREs in ANY one of the prior 3 years**
  (lines 22/23 skipped); 25 = 19 + 24; **26 = 25 × 79% if 280C elected, else
  = 25**.
- **Section C — Current year credit (lines 27-32).** 27 = Form 8932 wage overlap;
  28 = (13 or 26) − 27, floor 0; 29 = pass-through research credits received;
  30 = 28 + 29. Routing text verbatim: *"Partnerships and S corporations not
  electing the payroll tax credit, stop here and report this amount on
  Schedule K."* Eligible small businesses → Form 3800 Part III 4i; others →
  3800 Part III 1c. Estates/trusts: 31 allocation to beneficiaries, 32 = 30 − 31.
- **Section D — QSB payroll tax election (33a-36).** ≤$500,000 on line 34;
  partnerships/S corps line 36 = smaller of 28 or 34 → Form 8974; the Schedule K
  amount is line 30 REDUCED by line 36.
- **Section E — Other information (37-41).** REQUIRED whenever line 48 carries
  QREs (instructions "Reminders", verbatim): 37 number of business components;
  38 officers' wages included in line 42; 39 acquisition/disposition Y/N;
  40 new categories of expenses Y/N; 41 ASC-730 directive Y/N + amount (≥$10M
  assets, GAAP audited statements).
- **Section F — QRE summary (42-48).** 42 wages for qualified services;
  43 supplies; 44 computer rental/lease; 45 applicable contract research;
  46 applicable basic research payments; 47 = 45 + 46; **48 = 42 + 43 + 44 + 47
  → enter on line 5 or line 20**. Item A of Section F asks whether Section G is
  required.
- **Section G — business component detail (49-56).** **OPTIONAL for ALL filers
  for tax years beginning before 2026** (instructions "What's New", verbatim);
  required (subject to guidelines) for tax years beginning after 2025. ⚠ Spec
  goes stale at TY2026 — re-verify then.

## Law notes (from the Dec-2025 instructions)

- **ASC election**: made by completing Section B on a timely filed (incl.
  extensions) ORIGINAL return; applies to the current year and ALL later years;
  a current-year ASC election may not be revoked; revoke for a later year by
  completing Section A on a timely original return (Reg. §1.41-9(b)(3)).
- **§280C interplay (OBBBA-era)**: P.L. 119-21 added §174A (domestic research
  expenditures deductible for TYs beginning after 12/31/2024). Line 13
  instructions verbatim: *"If you don't elect the reduced credit, you must
  reduce your domestic research or experimental expenditures under section 174A
  otherwise taken into account as a deduction or charged to a capital account by
  the amount of the research credit."* Plus a required statement attachment when
  not electing (e-file naming "Form6765ItemASection280C.pdf" family).
- **Controlled groups**: group credit computed as a single taxpayer; member
  shares proportional to member QREs; Item B attachment categories; only the
  common parent elects §280C for a consolidated group.
- **QSB payroll election**: $500,000 cap; controlled-group members treated as a
  single taxpayer for the $5M-gross-receipts QSB test.

## Packet-227 arithmetic check (ASC, no 280C — INFERRED priors)

QREs 53,704; credit 4,243. 4,243 ÷ 0.14 = 30,307 (= line 23) ⇒ line 22 =
53,704 − 30,307 = 23,397 ⇒ prior-3-year QREs total (line 21) = 140,382.
14% × 30,307 = 4,242.98 → 4,243 ✓ (whole-dollar). The 280C-elected shape
(÷0.79) does not land on clean numbers — packet 227 appears to be a
**no-280C ASC** return. The REAL prior-year QREs must come off the packet's
printed Section B when Codex authors it; the spec scenario marks these values
INFERRED.

## Open scope questions for Ken (Gate-1 walk)

1. Line 6 fixed-base percentage: preparer-entered (recommended — derivation
   needs 1984-88 history / multi-year start-up tracking) vs computed?
2. §280C no-election deduction reduction: diagnostic-only (recommended — the
   8941 D_8941_004 precedent; never silently mutate a book number; entity M-1
   interplay) vs auto-reduce?
3. Section D payroll election: defer with a HOLD diagnostic (recommended;
   packet 227 doesn't use it) vs build now?
4. Controlled groups (Item B Yes): HOLD diagnostic (recommended) vs model
   member-share math?
