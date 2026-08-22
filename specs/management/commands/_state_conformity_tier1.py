"""Tier-1 state conformity data — the 15-state Phase 3 scan output (TY2025).

GENERATED 2026-08-06 by transcription from the VERIFIED briefs in
`delviotax/delvio-states` `conformity/<st>_conformity.md`. Each brief carries a
`## 12. Verification` section recording an adversarial pass; where §12 corrected a
figure, the CORRECTED value is what appears here.

⚠ NOT NEW TAX RESEARCH. Every figure traces to a brief; every brief traces to a
primary source with a URL. Nothing here was authored from memory. This module is
DATA ONLY — `load_state_conformity.py` owns the write path and the seed guard.

⚠ Leading underscore is deliberate: Django registers `specs/management/commands/*.py`
as commands, and this is not one.

SCOPE NOTES carried from the scan:
  • NV is deliberately ABSENT — no individual, corporate or fiduciary income tax and
    no PTET (constitutional), so it has no conformity posture to record. Out of
    campaign scope; see conformity/nv_conformity.md.
  • AZ's §179 figure was RULED by Ken on 2026-08-16 (broad reading of §43-105(B)):
    $2,500,000 / $4,000,000. It is a RULING on an interpretive question, not a
    published Arizona figure — AZDOR has never published its OBBBA retroactivity
    mapping, and that [UNVERIFIED] item stands open as a matter of fact. The basis
    is recorded in the row's notes and in delvio-states/GATE1_WALK.md item 1.
  • NY holds the STATE posture only. NYC decoupled differently (S.9009-C amending the
    NYC Admin. Code) and the model's one-row-per-(jurisdiction, tax_year) shape cannot
    express it; the divergence is recorded as a decoupled item + in notes.
  • CO / OR / MO carry verified NEGATIVES — no depreciation modification at all. That
    absence was affirmatively proven, not merely unfound. Do not "helpfully" add an
    add-back item to any of them.
"""

TIER1_SOURCES: list[dict] = [{'source_code': 'CA_SB711_2025_CONFORMITY',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'CA',
  'title': 'SB 711 (McNerney) — Taxation: federal conformity; IRC specified date moved to January '
           '1, 2025',
  'citation': 'Cal. R&TC §17024.5(a)(1)(Q), as added by SB 711 (McNerney), Chapter 231, Statutes '
              'of 2025, chaptered 10/1/2025; corporate date incorporated by cross-reference at '
              'R&TC §23051.5(a)(1)',
  'issuer': 'California Legislature (chaptered); Franchise Tax Board (administering)',
  'official_url': 'https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260SB711',
  'excerpt_label': 'CA specified date 1/1/2025 + corporate cross-reference + OBBBA non-conformity '
                   '(verbatim)',
  'excerpt_text': "R&TC §17024.5(a)(1)(Q), read from the chaptered SB 711 text at leginfo: '(Q) "
                  "For taxable years beginning on or after January 1, 2025 … January 1, 2025'. The "
                  'prior specified date was January 1, 2015. SB 711 does NOT amend R&TC §23051.5 '
                  "and does not need to: §23051.5(a)(1) defines the corporate IRC reference '…as "
                  'enacted on the specified date for the applicable taxable year as defined in '
                  "paragraph (1) of subdivision (a) of Section 17024.5.' FTB states the "
                  "consequence affirmatively and identically across the TY2025 booklets: 'Federal "
                  'Tax Changes Under One Big Beautiful Bill Act (OBBBA) – In general, California '
                  "R&TC does not conform to the OBBBA.'",
  'summary_text': 'California is a static fixed-date conformity state whose date moved 1/1/2015 → '
                  '1/1/2025 via SB 711 (Ch. 231, Stats. 2025), effective for TYs beginning '
                  'on/after 1/1/2025. Because the date pre-dates OBBBA (7/4/2025), OBBBA is not '
                  'adopted for TY2025.'},
 {'source_code': 'FL_FS_220_03_CONFORMITY',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'FL',
  'title': '2025 Fla. Stat. s. 220.03 — Definitions; Florida IRC conformity date (January 1, 2025)',
  'citation': 's. 220.03(1)(n) and (2)(c), F.S. (2025), as set by ss. 60–61, ch. 2025-208, L.O.F.; '
              's. 220.03(3) (automatic-adjustment conduit); s. 220.03(5)(b)–(c) (legacy '
              'depreciation elections)',
  'issuer': 'Florida Legislature (statute); Florida Department of Revenue (TIP 25C01-01, '
            '12/1/2025)',
  'official_url': 'https://www.flsenate.gov/Laws/Statutes/2025/220.03',
  'excerpt_label': "FL conformity date 1/1/2025 + s. 220.03(3) 'expressly authorized' limit + DOR "
                   'OBBBA notice (verbatim)',
  'excerpt_text': "s. 220.03(1)(n), F.S. (2025): 'Internal Revenue Code' means the U.S. Internal "
                  'Revenue Code of 1986, as amended and in effect on January 1, 2025, except as '
                  "provided in subsection (3). s. 220.03(3): 'On or after January 1, 1972, when "
                  'expressly authorized by law, any amendment to the Internal Revenue Code shall '
                  'be given effect under this code in such manner and for such periods as are '
                  'prescribed in the Internal Revenue Code, to the same extent as if such '
                  'amendment had been adopted by the Legislature of this state. However, any such '
                  'amendment shall have effect under this code only to the extent that the amended '
                  'provision of the Internal Revenue Code shall be taken into account in the '
                  "computation of net income subject to tax hereunder.' FL DOR TIP 25C01-01, boxed "
                  "notice: 'The new law discussed below does not address the One Big Beautiful "
                  'Bill Act (Public Law 119-21), which was enacted after the 2025 Florida '
                  "legislative session ended.'",
  'summary_text': 'Florida conforms to the IRC as amended and in effect 1/1/2025 for TY2025, '
                  're-adopted annually. OBBBA is not adopted for TY2025; s. 220.03(3) is not '
                  "self-executing (it operates only 'when expressly authorized by law'), and ch. "
                  "2026-137's move to 1/1/2026 operates retroactively only to 1/1/2026 and does "
                  'not reach TY2025.'},
 {'source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
  'source_type': 'state_conformity_notice',
  'source_rank': 'controlling',
  'jurisdiction_code': 'TX',
  'title': 'STAR memo 202603002M — Conformity of Texas Franchise Tax to the Internal Revenue Code',
  'citation': 'TX Comptroller STAR Doc. 202603002M, Tax Policy Division (Jenny Burleson), March '
              '12, 2026 — updates and replaces STAR 202512012M (Dec. 19, 2025).',
  'issuer': 'Texas Comptroller of Public Accounts, Tax Policy Division',
  'official_url': 'https://star.comptroller.texas.gov/view/202603002M',
  'excerpt_label': 'TX 2007-IRC departure beginning with the 2026 report + bonus placed-in-service '
                   'gate (verbatim)',
  'excerpt_text': "STAR 202603002M: 'Beginning with the 2026 franchise tax report, a taxable "
                  'entity will determine amounts taken from the federal tax return under the '
                  'federal tax law in effect for that federal tax year, unless the statute or rule '
                  'references the IRC. This change applies to all components of the franchise '
                  "tax.' On bonus depreciation in COGS: 'This amount may include any federal bonus "
                  'depreciation claimed on the federal tax return for assets placed in service on '
                  "or after January 19, 2025.' On foreign income: amounts under Section 78 and "
                  "Sections 951-964 'are determined under the 2007 IRC and do not include the "
                  'current IRC Section 951A global intangible low-taxed income (GILTI) as GILTI '
                  "was added to the IRC after January 1, 2007.' Underlying statute, Tex. Tax Code "
                  '§171.0001(9): "\'Internal Revenue Code\' means the Internal Revenue Code of '
                  '1986 in effect for the federal tax year beginning on January 1, 2007, not '
                  'including any changes made by federal law after that date, and any regulations '
                  'adopted under that code applicable to that period."',
  'summary_text': 'Texas has no income tax — the franchise (margin) tax under Tax Code ch. 171 has '
                  'only a definitional IRC tie. Beginning with the 2026 report (= Delvio TY2025), '
                  'federal-return amounts follow then-current federal law except where the Texas '
                  'statute or rule cites the IRC, in which case the 2007 IRC governs. '
                  'Administrative reinterpretation, not a repeal of §171.0001(9). FULL CITATION '
                  '(trimmed to the 255-char field cap): TX Comptroller STAR Doc. 202603002M, Tax '
                  'Policy Division (Jenny Burleson), March 12, 2026 — updates and replaces STAR '
                  '202512012M (Dec. 19, 2025); interpreting Tex. Tax Code §171.0001(9) (IRC of '
                  '1986 as in effect for the federal tax year beginning January 1, 2007)'},
 {'source_code': 'TN_TCA_67_4_2004_IRC_DEF',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'TN',
  'title': 'Tenn. Code Ann. § 67-4-2004 — Franchise & excise tax definitions; rolling IRC '
           'conformity',
  'citation': 'Tenn. Code Ann. § 67-4-2004 (IRC definition at subdivision (27) per the FindLaw '
              "reprint; 'person or taxpayer' at (36)); read together with § 67-4-2006(a)(10) "
              '(pre-TCJA §163(j)), (a)(11) (§174), (a)(12) (§168(k) TCJA lock, Public Chapter 377 '
              '(2023)).',
  'issuer': 'Tennessee General Assembly (statute); Tennessee Department of Revenue (F&E Tax '
            'Manual, Dec. 2025)',
  'official_url': 'https://codes.findlaw.com/tn/title-67-taxes-and-licenses/tn-code-sect-67-4-2004/',
  'excerpt_label': 'TN rolling IRC definition + TCJA §168(k) lock (verbatim from the DOR manual)',
  'excerpt_text': 'Tenn. Code Ann. § 67-4-2004: "\'Internal Revenue Code\' means title 26 of the '
                  'United States Code as effective during the year in which net earnings are '
                  'determined under this part." TN DOR Franchise and Excise Tax Manual (Dec. 2025) '
                  "p. 20, standing reminder: 'for assets purchased on or after January 1, 2023, "
                  'Tennessee remains coupled with the federal bonus depreciation provisions under '
                  'IRC § 168, as amended by the federal Tax Cuts and Jobs Act of 2017 ("TCJA"). If '
                  'the federal bonus depreciation provisions are amended by subsequent enactment '
                  'of federal legislation, Tennessee will nevertheless remain coupled with the '
                  'TCJA bonus depreciation provisions unless conforming state legislation is '
                  "enacted.' Manual p. 270: 'Tennessee conforms to IRC § 179 via the state's "
                  "general rolling conformity with the Internal Revenue Code, as amended.'",
  'summary_text': 'Tennessee has rolling IRC conformity for the franchise & excise tax, so OBBBA '
                  'flows in by default, but §168(k) is statutorily frozen at the TCJA version (40% '
                  'for 2025, §168(n) inapplicable) while §179 conforms at the full OBBBA '
                  '$2.5M/$4M. ⚠ NOTE ON SOURCE ACCESS: the official Tennessee code is not '
                  'reachable by automated retrieval (Justia returns HTTP 403); § 67-4-2004 was '
                  'read from the FindLaw secondary reprint, with every subdivision number '
                  "corroborated by the DOR manual's own footnotes. The substance (rolling) is "
                  'verified directly from the DOR manual. The exact subdivision number for the IRC '
                  'definition was originally flagged [UNVERIFIED] (§10 item 1); no figure depends '
                  'on it. FULL CITATION (trimmed to the 255-char field cap): Tenn. Code Ann. § '
                  "67-4-2004 (IRC definition at subdivision (27) per the FindLaw reprint; 'person "
                  "or taxpayer' at (36)); read together with § 67-4-2006(a)(10) (pre-TCJA "
                  '§163(j)), (a)(11) (§174), (a)(12) (§168(k) TCJA lock, Public Chapter 377 '
                  '(2023)), and (b)(1)(P) / (b)(2)(T) (5% NCTI)'},
 {'source_code': 'VA_CODE_58_1_301',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'VA',
  'title': 'Va. Code § 58.1-301 — Conformity to Internal Revenue Code',
  'citation': 'Va. Code § 58.1-301, as amended by 2026, c. 7 (House Bill 29, 2026 Amendments to '
              'the 2025 Appropriation Act, thirteenth enactment clause, effective February 20, '
              '2026); amendment history also shows 2026, Sp. Sess. I, c. 1',
  'issuer': 'Virginia General Assembly (Code of Virginia, via Virginia Law Portal / LIS)',
  'official_url': 'https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-301/',
  'excerpt_label': '§ 58.1-301 A — fixed IRC date (verbatim fragment as quoted in the brief)',
  'excerpt_text': '[VERBATIM FRAGMENT] "...as they existed on December 31, 2025." [CLOSE '
                  "PARAPHRASE of the brief's characterization — the brief did not reproduce the "
                  'full subsection] § 58.1-301 B enumerates the statutory exceptions to conformity '
                  'as 13 numbered items, including IRC §§ 168(k), 168(l), 168(m), 168(n), 1400L '
                  'and 1400N (exception 1), the new §174A and §179 items — codified by OBBBA '
                  'section number, § 70302 → R&E and § 70306 → expensing limits — and a '
                  'cannabis-business deduction disallowance effective TY2026.',
  'summary_text': "Virginia's conformity statute. Fixes the IRC at December 31, 2025 for TY2025 — "
                  'a date set by the 2026 BUDGET bill (HB 29, Ch. 7 of the 2026 Acts of Assembly, '
                  '13th enactment clause, effective 02/20/2026), not by standalone conformity '
                  'legislation. Because the date post-dates OBBBA (7/4/2025), OBBBA IS IN the '
                  'Virginia base for TY2025, subject to the subsection B exceptions. The second '
                  '2026 chapter in the amendment history (HB 30, Sp. Sess. I, c. 1, approved '
                  '06/29/2026) added only the cannabis-business exception for TY2026+ and did NOT '
                  'disturb the 12/31/2025 date — TY2025 is unaffected, but any TY2026 pass must '
                  'read both chapters.'},
 {'source_code': 'VA_TB_26_1',
  'source_type': 'state_conformity_notice',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'VA',
  'title': "Tax Bulletin 26-1: Virginia's Rolling Conformity to the Internal Revenue Code Replaced "
           'with a Fixed Date of December 31, 2025',
  'citation': 'Va. Dept. of Taxation Tax Bulletin 26-1 (FINAL, dated February 20, 2026)',
  'issuer': 'Virginia Department of Taxation',
  'official_url': 'https://www.tax.virginia.gov/sites/default/files/inline-files/tb-26-1-date-of-irc-conformity-advanced.pdf',
  'excerpt_label': 'TB 26-1 — OBBBA conformity statement and the addition/subtraction recovery '
                   'mechanic',
  'excerpt_text': '[VERBATIM] "Except where specifically noted, Virginia will conform to the '
                  'provisions of 2025 H.R. 1 to the extent that they affect the computation of: '
                  'Federal adjusted gross income or federal itemized deductions for individuals, '
                  'or Federal taxable income for corporations." [VERBATIM, TB 26-1 p.2] "If such '
                  'records indicate that Virginia deductions are smaller than federal deductions '
                  'in a given year (for example, due to federal immediate expensing), a fixed date '
                  'conformity addition will be required for that year in the amount by which the '
                  'federal deduction exceeds the deduction allowed for Virginia purposes. '
                  'Conversely, if such records indicate that Virginia deductions exceed federal '
                  'deductions in later years... a fixed date conformity subtraction will be '
                  'required." [VERBATIM] Taxpayers "must maintain separate Virginia records and '
                  'calculate depreciation, amortization, carryforwards, and adjustments as if the '
                  '2025 H.R. 1 changes had not been enacted."',
  'summary_text': 'The operative Department guidance on the 12/31/2025 fixed date. States that '
                  'Virginia conforms to OBBBA for TY2025 and then deconforms from three business '
                  'provisions — §168(n) qualified production property, §174A domestic R&E '
                  'expensing INCLUDING the retroactive and catch-up provisions, and the §179 '
                  'expensing-limit increases — recovered as a TIMING difference via fixed date '
                  'conformity additions now and subtractions later, requiring a separate Virginia '
                  'depreciation/amortization book. Also carries the eight standing exceptions, the '
                  'Pease/SALT individual treatment, and the §163(j) subtraction cut from 50% to '
                  '20% for TY2025 and thereafter. Cited by name in both the 2026 Legislative '
                  'Summary and the FINAL 2025 Form 500 instructions. NOTE: TB 26-1 publishes NO '
                  'Virginia §179 dollar figure and does not name the form line for the H.R. 1 '
                  'conformity adjustment.'},
 {'source_code': 'CO_CRS_39_22_103',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'CO',
  'title': "C.R.S. § 39-22-103(5.3) — definition of 'Internal revenue code' (rolling conformity)",
  'citation': '§ 39-22-103(5.3), C.R.S. — Colorado Revised Statutes 2024, Title 39 (Taxation), '
              'Office of Legislative Legal Services, p. 366 of the PDF (2025 edition not yet '
              'published as of 2026-08-06)',
  'issuer': 'Colorado General Assembly, Office of Legislative Legal Services',
  'official_url': 'https://leg.colorado.gov/sites/default/files/images/olls/crs2024-title-39.pdf',
  'excerpt_label': '§ 39-22-103(5.3), C.R.S. — rolling conformity definition (verbatim)',
  'excerpt_text': '[VERBATIM] "\'Internal revenue code\' means the provisions of the federal '
                  "'Internal Revenue Code of 1986', as amended, and other provisions of the laws "
                  'of the United States relating to federal income taxes, as the same may become '
                  'effective at any time or from time to time, for the taxable year."',
  'summary_text': "Colorado's rolling-conformity definition — there is NO static 'as of' date to "
                  'encode, so OBBBA flows into Colorado automatically for TY2025 except where the '
                  'legislature bolted on a specific add-back. The same Title 39 text supplies the '
                  'C-corp starting point ("the C corporation\'s federal taxable income, as defined '
                  'in the internal revenue code, for the taxable year, with the modifications '
                  'specified in this section," § 39-22-304(1)(a)) and is the source of the '
                  "campaign's key NEGATIVE finding: a full-text search of Title 39 for 'bonus "
                  "depreciation', 'section 168', '168(k)' and 'section 179 of the internal revenue "
                  "code' returns NO depreciation modification provision — the only two §179 hits "
                  "anywhere in Title 39 are inside credit 'qualifying investment' definitions. ⚠ "
                  '[UNV-1, downgraded to LOW risk, not resolved]: this is the 2024 edition; the '
                  '2025 CRS edition is not yet published (crs2025-title-39.pdf 404s), mitigated by '
                  'reading both 2025 extraordinary-session income tax bills, neither of which '
                  'touches depreciation.'},
 {'source_code': 'CO_2025_INDIV_TAX_GUIDE',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'CO',
  'title': 'Colorado Individual Income Tax Guide',
  'citation': 'Colorado Dept. of Revenue, Individual Income Tax Guide, Rev. January 2026 (current '
              'guidance covering TY2025); corroborated by Book 104 — 2025 Colorado Individual '
              'Income Tax Filing Guide, booklet rev. 10/29/25, DR 0104 rev. 10/03/25',
  'issuer': 'Colorado Department of Revenue',
  'official_url': 'https://tax.colorado.gov/sites/tax/files/documents/Individual_Income_Tax_Guide_January_2026.pdf',
  'excerpt_label': 'Individual Income Tax Guide / Book 104 — the two unusual add-backs and the '
                   'OBBBA treatments',
  'excerpt_text': '[VERBATIM, Part 3] "For tax years 2026 and later, an individual who claims a '
                  'deduction for overtime compensation on their federal income tax return must add '
                  'back the amount of the deduction on their Colorado return." [VERBATIM, Part 3] '
                  '"No addback is required on the taxpayer\'s Colorado return for any deduction '
                  'claimed on their federal return for qualified tips." [VERBATIM, Book 104 line '
                  '3] "You must add back the entire deduction regardless of your adjusted gross '
                  'income. This addback is not limited to the deduction taken with respect to the '
                  'electing partnership." [VERBATIM, guide\'s add-back limit table] "2023–2025 '
                  '$12,000 / $16,000 · 2026 and later $1,000 / $2,000." [CLOSE PARAPHRASE of the '
                  '§199A rule as transcribed in the brief] Add back the §199A deduction in full '
                  'where federal AGI exceeds $500,000 ($1,000,000 filing jointly), regardless of '
                  'the extent to which AGI exceeds the threshold; the add-back does not apply to a '
                  'taxpayer required to file a federal Schedule F.',
  'summary_text': "CDOR's current guidance publication for the individual lane, plus the TY2025 "
                  'Book 104 booklet. Carries the year-by-year rate table (TY2024 4.25%, TY2025 '
                  '4.4%), the two distinguishing Colorado add-backs and their thresholds and '
                  'TY2026 step-down, the federal-taxable-income starting point (DR 0104 line 1 '
                  'takes Form 1040 line 15), and the OBBBA overtime/tips treatment. Also the '
                  "source of a NEGATIVE finding relied on by the conformity row: 'depreciat*' "
                  'returns ZERO hits in this guide, in Book 104, in DR 0112 and in the Corporate '
                  'Income Tax Guide, and Part 3 (additions) was read in full with no depreciation '
                  'item.'},
 {'source_code': 'OH_RC_5701_11',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'OH',
  'title': 'R.C. 5701.11 — application of the Internal Revenue Code (Ohio IRC conformity)',
  'citation': 'Ohio Rev. Code § 5701.11, as amended by Am. Sub. S.B. 9 of the 136th General '
              'Assembly; version header "Effective: March 5, 2026"',
  'issuer': 'Ohio General Assembly (Ohio Revised Code, via codes.ohio.gov)',
  'official_url': 'https://codes.ohio.gov/ohio-revised-code/section-5701.11',
  'excerpt_label': 'R.C. 5701.11(A)(1), (A)(2), (B)(1), (B)(2) — conformity date and gap election',
  'excerpt_text': '[VERBATIM FRAGMENTS as quoted in the brief] (A)(1) any reference in Title LVII '
                  'to the Internal Revenue Code means the IRC "as they exist on the effective '
                  'date" of the section. (A)(2) the rule does not apply where a provision names '
                  '"the Internal Revenue Code as of a date certain specifying the day, month, and '
                  'year." (B)(2) "Elections under prior versions of division (B)(1) of this '
                  'section remain in effect for the taxable years to which they apply." [CLOSE '
                  'PARAPHRASE of (B)(1) as transcribed in the brief] For taxable years ending '
                  'after March 7, 2025 and before the current effective date, a taxpayer may '
                  'IRREVOCABLY ELECT to apply the IRC provisions that would otherwise have '
                  'applied; filing a report that incorporates the federal provisions without '
                  'adjustment CONSTITUTES the election.',
  'summary_text': "Ohio's conformity mechanism: STATIC / fixed-date, refreshed by annual "
                  'conformity legislation, with a taxpayer election covering the gap period — it '
                  "is NOT rolling conformity despite the statute's phrasing. TY2025 conformity "
                  'date is MARCH 5, 2026 (S.B. 9); the prior date was March 7, 2025. Both paths '
                  'through the section land on OBBBA APPLYING for Ohio TY2025, and ODT states this '
                  'directly on its conformity page. The (B)(1) election is ALL-OR-NOTHING and '
                  'return-level — a person cannot selectively incorporate provisions from each IRC '
                  'version. ⚠ The FINAL TY2025 IT 1040 booklet ("accurate as of November 27, '
                  '2025", ModDate 2026-01-23) was NEVER revised for S.B. 9 and still reflects the '
                  'March 7, 2025 date; the mechanical hooks are Ohio Schedule of Adjustments line '
                  '11 (Federal Conformity Additions) and line 31 (Federal Conformity Deductions). '
                  'Conformity is irrelevant to the CAT, which has no federal-taxable-income '
                  'starting point. NOTE: the enrolled S.B. 9 session-law text itself was NOT read '
                  '(legislature.ohio.gov fails TLS verification); the 3/5/2026 date and TY2025 '
                  "retroactivity rest on the R.C. version headers and ODT's plain statement."},
 {'source_code': 'OH_RC_5747_01',
  'source_type': 'state_statute',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'OH',
  'title': 'R.C. 5747.01 — income tax definitions (depreciation add-back and recovery)',
  'citation': 'Ohio Rev. Code § 5747.01(A)(17) (add-back) and (A)(18) (recovery); post-S.B. 9 '
              'version, header "Effective: March 5, 2026 · Latest Legislation: Senate Bill 9 - '
              '136th General Assembly". Transcribed with the FINAL TY2025 Ohio IT 1040 instruction '
              'booklet.',
  'issuer': 'Ohio General Assembly (Ohio Revised Code, via codes.ohio.gov)',
  'official_url': 'https://codes.ohio.gov/ohio-revised-code/section-5747.01',
  'excerpt_label': 'Ohio Schedule of Adjustments lines 9 and 27 — add-back and recovery (booklet '
                   'verbatim)',
  'excerpt_text': '[VERBATIM, IT 1040 booklet p.20, line 9] "Add 5/6 of your bonus depreciation '
                  'allowed under Internal Revenue Code section 168(k). Also add 5/6 of your '
                  'depreciation expense allowed under Internal Revenue Code section 179 less the '
                  'amount that would have been allowed under section 179 as it existed on Dec. 31, '
                  '2002. Replace "5/6" with "2/3" for employers who increased their Ohio income '
                  'taxes withheld by at least 10% over the previous year. Replace "5/6" with "6/6" '
                  'for taxpayers who incur a net operating loss for federal income tax purposes if '
                  'the loss was a result of the 168(k) and/or 179 depreciation expenses. No '
                  'add-back is required for: Employers who increased their Ohio income taxes '
                  'withheld over the previous year by at least their total 168(k) and 179 '
                  'depreciation expenses; OR 168(k) or 179 depreciation from a pass-through entity '
                  'in which the taxpayer owns less than 5%." [VERBATIM, booklet pp.22–23, line 27] '
                  '"Deduct: 1/5 of prior year 5/6 add-backs, 1/2 of prior year 2/3 add-backs, AND '
                  '1/6 of prior year 6/6 add-backs, of Internal Revenue Code sections 168(k) and '
                  '179 depreciation adjustments. The deduction must be taken in equal increments '
                  'in consecutive tax years and any unused portion from any given tax year is not '
                  'eligible to be carried forward. Additionally, in tax years with an NOL, an NOL '
                  'carryback or an NOL carryforward, you cannot claim this deduction. Instead, you '
                  'must carry the deduction forward to the next tax year in which you have no NOL, '
                  'carryback, or carryforward." [VERBATIM statutory fragment, (A)(17)(a)(v)] "The '
                  'tax commissioner, under procedures established by the commissioner, may waive '
                  'the add-backs related to a pass-through entity if the taxpayer owns, directly '
                  'or indirectly, less than five per cent of the pass-through entity."',
  'summary_text': "The Ohio depreciation add-back-and-recover regime. (A)(17) uses 'five-sixths', "
                  "'two-thirds' (taxable years 2012+ where withholding increased at least 10%) and "
                  "'the entire' amount (NOL case), and defines qualifying §179 depreciation "
                  'expense as the excess of current §179 over the amount allowable under §179 AS '
                  'IT EXISTED ON DECEMBER 31, 2002; (A)(18) supplies the 1/5, 1/2 and 1/6 '
                  'recoveries and the NOL-year suspension. Verified triple-sourced (statute, '
                  'booklet, ODT FAQ). Also the source of the §168(n) NEGATIVE: every reference to '
                  "section 168 in the post-S.B. 9 section is qualified as 'subsection (k)' — in "
                  '(A)(17)(a)(i), (a)(iv), (a)(v) and (A)(18)(a)(i), (c) — with NO reference to '
                  'subsection (n) or to qualified production property anywhere in the section. '
                  'FULL CITATION (trimmed to the 255-char field cap): Ohio Rev. Code § '
                  '5747.01(A)(17) (add-back) and (A)(18) (recovery); post-S.B. 9 version, header '
                  '"Effective: March 5, 2026 · Latest Legislation: Senate Bill 9 - 136th General '
                  'Assembly". Transcribed with the FINAL TY2025 Ohio IT 1040 instruction booklet, '
                  'pp. 20, 22–23.'},
 {'source_code': 'OH_FAQ_INCOME_BONUS_DEPR',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'OH',
  'title': 'ODT FAQ: Income – Bonus Depreciation',
  'citation': "Ohio Dept. of Taxation Help Center FAQ, 'Income – Bonus Depreciation' (page dated "
              '2022-05-10; the referent — §179 as it existed on 12/31/2002 — is time-invariant)',
  'issuer': 'Ohio Department of Taxation',
  'official_url': 'https://tax.ohio.gov/faq-IncomeDepreciation',
  'excerpt_label': 'ODT FAQ — the $25,000 §179 baseline and the per-source fraction rule',
  'excerpt_text': '[VERBATIM] "The amount subject to the add-back is the taxpayer\'s total §179 '
                  'expense less $25,000 plus all of the taxpayer\'s §168(k) depreciation expense." '
                  '[VERBATIM worked example] "Depreciation subject to add-back: (§179 - 25,000) + '
                  '§168k" / "Mark\'s depreciation subject to add-back: ($125,000 – 25,000) + '
                  '$80,000 = $180,000". [VERBATIM, Example 2] "Mark must use a different add-back '
                  'fraction for each source of depreciation." [VERBATIM] a person is not required '
                  'to make Ohio\'s depreciation add-back "[if] the person owns less than 5% of the '
                  'entity ... This is true even if the pass-through entity performed the add-back '
                  'on its Ohio filing."',
  'summary_text': 'The only ODT publication that states the 12/31/2002 §179 baseline as a DOLLAR '
                  'FIGURE — $25,000 — which neither the IT 1040 booklet nor R.C. 5747.01(A)(17) '
                  'does. Matches IRC §179(b)(1) as it stood on 12/31/2002 (pre-JGTRRA). ⚠ The ODT '
                  'formula applies a FLAT $25,000 subtraction and specifies NO separate '
                  'investment-limitation phase-out — implement as written, not as a reconstructed '
                  '2002 §179 computation. This FAQ is also the authority for the modelling '
                  'correction that add-back fractions are chosen PER SOURCE of depreciation, not '
                  'per taxpayer, with worked add-back / recovery / NOL examples. Note ODT '
                  'administers the <5% PTE exception as automatic even though the statute frames '
                  'it as a discretionary commissioner waiver. Fetching note: tax.ohio.gov returns '
                  'HTTP 404 to WebFetch but 200 to curl -L with a browser User-Agent.'},
 {'source_code': 'MA_TIR_26_4',
  'source_type': 'state_conformity_notice',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MA',
  'title': 'TIR 26-4: Massachusetts Conformity to Certain Provisions in Public Law No. 119-21',
  'citation': 'Mass. DOR Technical Information Release 26-4 (FINAL, issued 06/23/2026, signed '
              'Geoffrey E. Snyder, Commissioner of Revenue), implementing St. 2026, c. 101 (the '
              'FY2026 mid-year Supplemental Budget), signed June 12, 2026',
  'issuer': 'Massachusetts Department of Revenue',
  'official_url': 'https://www.mass.gov/technical-information-release/tir-26-4-massachusetts-conformity-to-certain-provisions-in-public-law-no-119-21',
  'excerpt_label': 'TIR 26-4 conformity chart — OBBBA provision → c. 62 / c. 63 (key rows, '
                   'transcribed)',
  'excerpt_text': '[VERBATIM CHART ROWS, Act section → c. 62 conformity / c. 63 conformity] '
                  '"70301. Full expensing for certain business property" → No / No. "70306. '
                  'Increased dollar limitations for expensing of certain depreciable business '
                  'assets (§179)" → "Yes, effective TYs beginning on or after 1/1/2027" / same. '
                  '"70307. Special depreciation allowance for qualified production property '
                  '(§168(n))" → "Yes, effective TYs beginning on or after 1/1/2027" / same. '
                  '"70302. Full expensing of domestic R&E (§174A)" → "In part, effective TYs '
                  'beginning on or after 1/1/2026" / same. "70303. Modification of limitation on '
                  'business interest (§163(j))" → Yes, effective 1/1/2027 / same. "70421. '
                  'Permanent renewal and enhancement of opportunity zones (§1400Z-2)" → No / Yes, '
                  'effective 1/1/2027. "70105. §199A QBI deduction" → No / N/A. [VERBATIM, quoted '
                  'in the brief from TIR 26-4] "The Massachusetts income tax generally determines '
                  'Massachusetts gross income based on the Code as amended and in effect on '
                  'January 1, 2024, but conforms to the Code as currently in effect for the '
                  'determination of trade or business expense deductions, with limited exceptions, '
                  'and to certain other specified Code sections."',
  'summary_text': 'The authoritative Massachusetts OBBBA conformity chart, provision by provision, '
                  'separately for the c. 62 personal income tax and the c. 63 corporate excise. '
                  'Implements the retroactive decoupling enacted by St. 2026, c. 101 (signed '
                  '6/12/2026), which delayed conformity to the OBBBA business provisions — §179 '
                  'increased limits, §168(n), §174/§174A, §163(j) ATI and §1400Z-2 — back to '
                  'taxable years beginning on or after 1/1/2025, and left §168(k) bonus '
                  'permanently disallowed in both chapters. FINAL and post-legislation, so it '
                  'supersedes every TY2025 MA form and instruction, none of which was reissued '
                  'after 6/12/2026. ⚠ TIR 26-4 states RULES, not dollar amounts — it publishes no '
                  'Massachusetts §179 figure.'},
 {'source_code': 'MA_GL_C62_S1',
  'source_type': 'state_statute',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MA',
  'title': "G.L. c. 62, § 1(c) — definition of 'Code' (personal income tax conformity date)",
  'citation': 'Mass. G.L. c. 62, § 1(c); companion corporate-excise definition at G.L. c. 63, § 1',
  'issuer': 'Massachusetts General Court (Massachusetts General Laws)',
  'official_url': 'https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section1',
  'excerpt_label': 'G.L. c. 62, § 1(c) and G.L. c. 63, § 1 — the two conformity definitions '
                   '(verbatim)',
  'excerpt_text': '[VERBATIM, c. 62 § 1(c)] "\'\'Code\'\', the Internal Revenue Code of the United '
                  'States, as amended on January 1, 2024 and in effect for the taxable year; but '
                  'Code shall mean the Code as amended and in effect for the taxable year for '
                  'sections 62(a)(1), 72, 105, 106, 108(f)(5), 139C, 223, 274(m), 274(n), 401 '
                  'through 420, inclusive, 457, 529, 529A, 530, 951, 951A, 959, 961, 3401 and 3405 '
                  'but excluding sections 402A and 408(q)." [VERBATIM, c. 63 § 1] "the Internal '
                  'Revenue Code of the United States, as amended and in effect for the taxable '
                  'year, unless otherwise provided."',
  'summary_text': "The statutory basis for Massachusetts' SPLIT conformity: c. 62 personal income "
                  'tax STATIC at January 1, 2024 with an enumerated list of ROLLING carve-out '
                  'sections, versus c. 63 corporate excise fully ROLLING. The carve-out that '
                  'matters most is § 62(a)(1) (trade or business expense deductions) — the channel '
                  'through which current-Code business provisions, including §179, reach the '
                  'Massachusetts PERSONAL income tax despite the 1/1/2024 date. That route was '
                  'then closed for the OBBBA business provisions by St. 2026, c. 101.'},
 {'source_code': 'MA_GL_C62_S2',
  'source_type': 'state_statute',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MA',
  'title': 'G.L. c. 62, § 2 — Massachusetts gross income; § 2(d)(1)(N) §168(k) disallowance',
  'citation': 'Mass. G.L. c. 62, § 2(a) and § 2(d)(1)(N); corporate-excise counterpart at G.L. c. '
              '63, § 30(4). Mechanics in DOR TIR 02-11 and TIR 03-25 (historical, still '
              'operative).',
  'issuer': 'Massachusetts General Court (Massachusetts General Laws)',
  'official_url': 'https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2',
  'excerpt_label': 'G.L. c. 62 § 2(a) starting point and § 2(d)(1)(N) bonus disallowance '
                   '(verbatim)',
  'excerpt_text': '[VERBATIM, § 2(a)] "Massachusetts gross income shall mean the federal gross '
                  'income, modified as required by section six F, with the following further '
                  'modifications." [VERBATIM, § 2(d)(1)(N)] "The deduction allowed by section '
                  '168(k) of the Internal Revenue Code, as amended and in effect for the current '
                  'tax year." [VERBATIM, DOR corporate-excise guidance] "Bonus Depreciation '
                  'allowed as a federal deduction under IRC § 168(k) is not allowed as a deduction '
                  'for purposes of determining Massachusetts taxable net income. Taxpayers must '
                  'adjust their taxable net income to eliminate the effect of IRC § 168(k). The '
                  'adjustment may result in an addition to, or a subtraction from, taxable net '
                  'income. The Massachusetts adjusted basis of depreciable property is also '
                  'determined without regard to IRC § 168(k)."',
  'summary_text': 'Two things at once. (1) The Massachusetts individual starting point is FEDERAL '
                  'GROSS INCOME — not federal AGI — which is why nothing ported from an AGI-based '
                  'state survives contact with the MA individual return (MA gross income then '
                  'splits into Part A / Part B / Part C, each with its own adjustments, '
                  'deductions, exemptions and more than one rate). (2) The statutory hook for the '
                  'permanent §168(k) disallowance in the personal income tax, with G.L. c. 63 § '
                  '30(4) carrying the corporate-excise disallowance. Because MA basis is computed '
                  "WITHOUT §168(k), the adjustment flips sign over the asset's life — a per-asset "
                  'dual-basis ledger is required.'},
 {'source_code': 'NY_DTF_N_26_1',
  'source_type': 'state_conformity_notice',
  'source_rank': 'controlling',
  'jurisdiction_code': 'NY',
  'title': 'N-26-1, Reporting certain depreciation and research and experimental deductions for '
           'tax year 2025',
  'citation': 'NYS Dept. of Taxation and Finance Notice N-26-1, issued June 16, 2026 (page '
              "'Updated: August 3, 2026'); implements the FY2026-27 New York State Budget "
              '(S.9009-C, signed 2026-05-28) response to P.L. 119-21 (OBBBA)',
  'issuer': 'New York State Department of Taxation and Finance',
  'official_url': 'https://www.tax.ny.gov/forms/n-notices/n-26-1.htm',
  'excerpt_label': 'N-26-1 (6/16/2026) — the two NY State OBBBA add-backs and the amended-return '
                   'duty',
  'excerpt_text': "'The full amount of any federal deduction for accelerated depreciation on "
                  "qualified production property under IRC § 168(n) must be added back.' 'The full "
                  'amount of any federal deduction for foreign and domestic R&E expenditures must '
                  "be added back.' Reporting: qualified production property is reported 'by "
                  "including qualified production property in Part 1 of this form' (Form IT-398 — "
                  'the §168(k) form) using codes A-209 / S-213; R&E via A-225 with S-221 '
                  "(post-1/1/2025, amortized over 60 months 'as if the election under IRC § "
                  "174A(c) applied') or S-222 (pre-1/1/2025, 'must continue to be amortized under "
                  "the federal rules in effect on January 1, 2022'). Corporations: CT-399 Part 1 "
                  'Section B then CT-225 / CT-225-A codes A-507 / S-507 for §168(n); A-225 / S-221 '
                  '/ S-222 for R&E. Partnerships filing IT-204.1 use A-507 / S-507 for §168(n). '
                  "'If a 2025 tax return has been filed, an amended return must be filed to report "
                  "the modifications described in this notice.' The add-back reaches deductions "
                  'under IRC §§ 174, 174A, and P.L. 119-21 § 70302(f)(2)(A). Footnote 1 prints '
                  "'Federal Public Law 119-121' (typo) while footnote 3 prints 'Federal Public Law "
                  "119-21, title VII, § 70302(f)(2)(A)' (correct) — cite P.L. 119-21.",
  'summary_text': "The ONLY TY2025 authority carrying New York State's OBBBA decoupling: §168(n) "
                  'and §174/§174A full add-backs, the reporting forms and modification codes, and '
                  'a retroactive amended-return duty. No TY2025 NY form contains a §168(n) code or '
                  'the A-225/S-221/S-222 R&E codes — encode the notice, not the form.'},
 {'source_code': 'NY_TAX_LAW_612',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'NY',
  'title': 'NY Tax Law §612 — New York adjusted gross income of a resident individual',
  'citation': 'N.Y. Tax Law §612(b)(8) (§168(k) add-back, tax years beginning after 12/31/2002); '
              '§612(b)(36) (SUV §179 add-back); §612(b)(44) & §612(c)(48) (§168(n)); §612(b)(45), '
              '§612(c)(49), §612(c)(50) (R&E).',
  'issuer': 'New York State Legislature (via NY Senate)',
  'official_url': 'https://www.nysenate.gov/legislation/laws/TAX/612',
  'excerpt_label': '§612(b)(8) — the legacy §168(k) add-back',
  'excerpt_text': "'for taxable years beginning after December thirty-first, two thousand two, in "
                  'the case of qualified property described in paragraph two of subsection k of '
                  "section 168 of the internal revenue code' — an addition modification for the "
                  "federal bonus deduction. The NY deduction is then 'determined under IRC § 167, "
                  'as that section would have applied to the property if it had been acquired on '
                  "September 10, 2001' (Form IT-398). §612(b)(36) requires an add-back of the §179 "
                  "deduction claimed for an SUV that is not a 'passenger automobile' as defined in "
                  'IRC §280F(d)(5), for taxpayers who are not eligible farmers (codes A-208 / '
                  'S-212, SUV weighing more than 6,000 pounds).',
  'summary_text': "The statutory home of New York's decades-old §168(k) bonus add-back "
                  '(independent of OBBBA), the SUV §179 exception, and the codified §168(n)/R&E '
                  'modifications. Exceptions to the bonus add-back: qualified resurgence zone and '
                  'NY Liberty Zone property. FULL CITATION (trimmed to the 255-char field cap): '
                  'N.Y. Tax Law §612(b)(8) (§168(k) add-back, tax years beginning after '
                  '12/31/2002); §612(b)(36) (SUV §179 add-back); §612(b)(44) & §612(c)(48) '
                  '(§168(n)); §612(b)(45), §612(c)(49), §612(c)(50) (R&E); cf. §208.9(c-4)(2) '
                  '(institutional real estate investor covered property)'},
 {'source_code': 'NY_S9009C_PART_G_NYC',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'NY',
  'title': 'S.9009-C Part G (FY2026-27 New York State Budget) — amendments to the New York City '
           'Administrative Code decoupling NYC from certain OBBBA provisions',
  'citation': 'N.Y. S.B. 9009-C (2026), Part G, signed by Gov. Hochul May 28, 2026, amending NYC '
              'Admin. Code §§11-506(b)&(c) (UBT), 11-602.8(a)&(b) (GCT), 11-641(b)&(e) (Bank Tax), '
              '11-651(e) and 11-652.8(a)&(b) (Business Corporation Tax).',
  'issuer': 'New York State Legislature (NYC Administrative Code sections identified via EY Tax '
            'News)',
  'official_url': 'https://taxnews.ey.com/news/2026-0294-new-york-fy2026-27-proposed-executive-budget-includes-retroactive-business-and-individual-tax-changes-would-decouple-from-certain-obbba-provisions',
  'excerpt_label': 'NYC decoupling — enacted by the STATE budget bill, not by NYC DOF',
  'excerpt_text': 'The NYC decouplings from §168(n), §174/§174A, §163(j) (EBIT-only ATI) and §179 '
                  "(pre-OBBBA limits) 'were enacted by the same New York STATE budget bill, "
                  "amending the NYC Administrative Code'; they are not a separate NYC Department "
                  'of Finance action, and no NYC DOF memorandum implements them. Consequence: '
                  "'DTF's N-26-1 governs the State taxes only and does not reach the City taxes.' "
                  'The specific post-decoupling NYC §179 dollar limit and phaseout for TY2025 are '
                  "stated in NO published source — EY describes the change only as reverting 'to "
                  "the NYC limitations in effect before the OBBBA'.",
  'summary_text': '⚠ SECONDARY SOURCE FOR THE URL ONLY. Per the brief, EY was used solely for the '
                  'NYC Administrative Code section list, the bill number and the enactment date; '
                  'the substance of the State posture is in N-26-1 and Tax Law §612 / §208(9). The '
                  'enacted NYC Admin. Code text itself was NOT retrievable — it is what would '
                  'settle open item U-5 (NYC §179 limits), which blocks any NYC business-tax '
                  'module. FULL CITATION (trimmed to the 255-char field cap): N.Y. S.B. 9009-C '
                  '(2026), Part G, signed by Gov. Hochul May 28, 2026, amending NYC Admin. Code '
                  '§§11-506(b)&(c) (UBT), 11-602.8(a)&(b) (GCT), 11-641(b)&(e) (Bank Tax), '
                  '11-651(e) and 11-652.8(a)&(b) (Business Corporation Tax), for tax years '
                  'beginning on or after 1/1/2025'},
 {'source_code': 'MD_TG_10_108',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MD',
  'title': 'Md. Code, Tax-General §10-108 — Effect of amendment of the Internal Revenue Code',
  'citation': 'Md. Code Ann., Tax-General §10-108(a), (b), (c); read with §10-203 (individual '
              'starting point = federal AGI) and §10-304 (corporate starting point = federal '
              'taxable income)',
  'issuer': 'Maryland General Assembly',
  'official_url': 'https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-108&enactments=false',
  'excerpt_label': '§10-108 — the automatic-decoupling trigger',
  'excerpt_text': "An IRC amendment affecting FAGI/FTI 'does not affect the determination of "
                  "Maryland taxable income' for any taxable year beginning in — or preceding — the "
                  'calendar year the amendment was enacted, unless the Comptroller determines the '
                  "revenue impact is less than $5,000,000. §10-108(b): 'Within 60 days after an "
                  'amendment of the Internal Revenue Code is enacted, THE COMPTROLLER shall '
                  'prepare and submit to the Governor and … the President of the Senate and the '
                  "Speaker of the House a report'. §10-108(c) likewise conditions the exception on "
                  "what 'the Comptroller determines'. The $5,000,000 test is measured against "
                  'State income tax revenue for a fiscal year.',
  'summary_text': "Maryland's rolling conformity plus a one-year rolling brake: an IRC amendment "
                  'is automatically decoupled for the enactment year and prior years unless the '
                  'Comptroller scores the fiscal-year revenue impact below $5,000,000. It fired '
                  'for three OBBBA sections in TY2025. [§12 correction: the statutory actor is the '
                  'Comptroller, not the Bureau of Revenue Estimates.]'},
 {'source_code': 'MD_TG_10_210_1',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MD',
  'title': 'Md. Code, Tax-General §10-210.1 — Decoupling modifications (with §10-310 for '
           'corporations)',
  'citation': 'Md. Code Ann., Tax-General §10-210.1(a)(3), (a)(4), (b)(1)(i)-(ii), (b)(2), '
              '(b)(3)(i)-(ii), (b)(5); §10-310 (applies §10-210.1 to corporations)',
  'issuer': 'Maryland General Assembly',
  'official_url': 'https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-210.1&enactments=false',
  'excerpt_label': '§10-210.1 — §168(k), §179 freeze, the manufacturing carve-out, heavy-duty SUVs',
  'excerpt_text': "(b)(1)(i): depreciation and adjusted basis determined 'without regard to the "
                  "additional allowance under § 168(k)'. (b)(1)(ii) and (b)(3)(ii): the add-back "
                  "'does not apply to property placed in service by a manufacturing entity ON OR "
                  "AFTER JANUARY 1, 2019'. (a)(4): 'manufacturing entity' = a trade or business "
                  "'primarily engaged in activities that, in accordance with the North American "
                  'Industrial Classification System (NAICS), United States Manual, … 2012 Edition, '
                  "would be included in Sector 31, 32, or 33'; it 'does not include a refiner, as "
                  "defined in § 10-101 of the Business Regulation Article'. (b)(3)(i): §179 "
                  "maximum 'without regard to any changes made to that section after December 31, "
                  '2002: 1. increasing above $25,000 the dollar limitation set forth in § '
                  '179(b)(1)…; or 2. increasing above $200,000 the phase-out threshold set forth '
                  "in § 179(b)(2)'. (b)(5): heavy-duty SUV depreciation computed 'as if the heavy "
                  'duty SUV were subject to the limitations of § 280F … as it would be if the '
                  "vehicle were rated at 6,000 pounds gross vehicle weight or less'; (a)(3) heavy "
                  "duty SUV = 4-wheeled, >6,000 but ≤14,000 lb GVW. §10-310: 'the federal taxable "
                  'income of a corporation shall be adjusted as provided for an individual under § '
                  "10-210.1'.",
  'summary_text': "The statutory source of Maryland's permanent §168(k) decoupling, the "
                  '$25,000/$200,000 §179 freeze, the NAICS 31–33 manufacturing carve-out (which '
                  'appears on NO TY2025 Maryland form and must be built from the statute alone), '
                  'and the heavy-duty SUV rule (which has NO manufacturing exception). §10-310 '
                  'extends all of it to corporations.'},
 {'source_code': 'MD_COMP_ALERT_OBBBA_2026',
  'source_type': 'state_conformity_notice',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MD',
  'title': 'Tax Alert — Maryland Impacts of the One Big Beautiful Bill Act (PL 119-21)',
  'citation': 'Comptroller of Maryland, Legal Division, Tax Alert, effective 1/6/2026, §§I–V; '
              'citing the Bureau of Revenue Estimates 60-day report on P.L. 119-21, 9/5/2025',
  'issuer': 'Comptroller of Maryland, Legal Division',
  'official_url': 'https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/alerts/tax-alert-maryland-impacts-of-the-one-big-beautiful-bill-act.pdf',
  'excerpt_label': 'Tax Alert — the three automatically decoupled OBBBA sections, and the four '
                   'that do not flow',
  'excerpt_text': "'As a conformity state, administration of Maryland income tax generally "
                  'conforms to federal income tax laws except when the Maryland General Assembly '
                  "has enacted decoupling legislation, or when automatically decoupled.' "
                  'Automatically decoupled for TY2025 (and preceding years): §70302 (new IRC §174A '
                  'domestic R&E full expensing — Maryland requires 5-year/60-month capitalization '
                  'and will not accept amended 2022–2024 returns claiming the §174A Note (f) '
                  'catch-up); §70303 (§163(j) ATI, IRC §163(j)(8)(A)(v) — recompute ATI on a '
                  'Maryland pro forma WITH depreciation/amortization/depletion deducted, add-back '
                  'only); §70307 (new IRC §168(n) qualified production property — recompute under '
                  'Pub. 946 excluding §168(n), basis difference recovers as later-year '
                  'subtractions). NOT decoupled and NOT flowing to the Maryland return: tips (IRC '
                  '§224; PL 119-21 §70201), overtime (IRC §225; §70202), auto-loan interest (IRC '
                  '§163(h)(4); §70203) and the additional senior deduction (IRC §151(d)(5)(C); '
                  "§70103) — they 'do not impact the calculation of an individual's Maryland tax "
                  "liability and are not reported on the Maryland return,' and cannot be claimed "
                  'as Maryland itemized deductions.',
  'summary_text': "The Comptroller's controlling administrative statement of which OBBBA "
                  'provisions the §10-108 trigger caught for TY2025 (three) and which '
                  'below-the-line federal deductions never reach the Maryland return (four). Also '
                  'the source of the worked recovery examples.'},
 {'source_code': 'MD_2025_FORM_500DM',
  'source_type': 'state_form',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MD',
  'title': '2025 Form 500DM — Decoupling Modification, with instructions (COM/RAD-24, rev. 10/25)',
  'citation': 'Maryland Form 500DM (2025), COM/RAD-24, rev. 10/25 — FINAL TY2025',
  'issuer': 'Comptroller of Maryland',
  'official_url': 'https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/500dm.pdf',
  'excerpt_label': '500DM — the pro forma mechanism and the decoupled-provision list',
  'excerpt_text': "'Separate (pro forma) federal and Maryland returns must be prepared for use in "
                  "completing Form 500DM,' and the pro formas 'are not to be filed with the "
                  "Comptroller of Maryland or the IRS.' Positive difference = addition "
                  "modification; negative = subtraction. §179 restated: 'a taxpayer only is "
                  'allowed to expense up to $25,000, reduced dollar-for-dollar by the amount over '
                  "$200,000, of the cost of Section 179 property.' Heavy-duty SUVs: applies to "
                  'vehicles placed in service after 5/31/2004. Other decoupled items carried on '
                  'the form: CARES Act items (business interest, excess business losses, NOLs, QIP '
                  "bonus), a §172 farming-loss carryback election described as 'a carryback period "
                  "of up to 2 years (Farming loss only)', and §108(i) DOI-income and OID deferral. "
                  'A PTE makes no adjustment on its own Form 510/511 but must attach Form 500DM '
                  'and pass each member their share via Maryland Schedule K-1 (510/511); each '
                  'member then files their own 500DM (line 9).',
  'summary_text': 'The filing surface for every Maryland decoupling modification. ⚠ Two verified '
                  "defects: the form cites 'Technical Bulletin No. 38', which DOES NOT EXIST (the "
                  "real document is Administrative Release No. 38, 'Decoupling from Federal Income "
                  "Tax Laws', PDF rev. 8/11/2025), and its '2 years' farming-loss carryback "
                  "conflicts with §10-210.1(b)(2)'s '5 years' — unresolved open item. The NAICS "
                  '31–33 manufacturing carve-out appears NOWHERE on this form.'},
 {'source_code': 'AZ_HB4168_2026_CH140',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'AZ',
  'title': "H.B. 4168 (2026), Chapter 140 — 'taxation; omnibus; 2026-2027', amending A.R.S. "
           '§43-105 (IRC conformity) and Title 43 modifications',
  'citation': 'H.B. 4168, 57th Leg., 2nd Reg. Sess. (2026), Chapter 140; approved by the Governor '
              'June 13, 2026 and filed with the Secretary of State June 13, 2026. Sec. 12 (§43-105 '
              'conformity); Sec. 14 (§43-1021 ¶17 §168(n), TY2026).',
  'issuer': 'Arizona Legislature',
  'official_url': 'https://www.azleg.gov/legtext/57leg/2R/laws/0140.pdf',
  'excerpt_label': '§43-105(B) as amended — the TY2025 hybrid conformity rule',
  'excerpt_text': "'For the purposes of computing income tax pursuant to this title, for taxable "
                  'years beginning from and after December 31, 2024 THROUGH DECEMBER 31, 2025, '
                  '"internal revenue code" means the United States internal revenue code of 1986, '
                  'as amended, in effect on January 1, 2025, including those provisions that '
                  'became effective during 2024 with the specific adoption of all retroactive '
                  'effective dates, but excluding any changes to the code enacted after January 1, '
                  '2025 AND INCLUDING THOSE PROVISIONS OF PUBLIC LAW 119-21 THAT ARE RETROACTIVELY '
                  'EFFECTIVE DURING TAXABLE YEARS BEGINNING FROM AND AFTER DECEMBER 31, 2024 '
                  "THROUGH DECEMBER 31, 2025.' §43-105(A) (TY2026+): IRC in effect January 1, "
                  "2026, 'BUT EXCLUDING ANY CHANGES TO THE CODE ENACTED AFTER JANUARY 1, 2026.' "
                  "Sec. 35: 'A. Sections 42-1001, 43-105, 43-1022, 43-1041, 43-1121 and 43-1122 … "
                  'apply retroactively to taxable years beginning from and after December 31, '
                  '2024. B. Sections 43-1021, 43-1042, 43-1073.01, 43-1074.01 and 43-1168 … apply '
                  "retroactively to taxable years beginning from and after December 31, 2025.'",
  'summary_text': 'The controlling TY2025 conformity authority. Contains TWO different definitions '
                  '— subsection (A) for TY2026 (Jan 1, 2026) and redesignated subsection (B) for '
                  'TY2025 (Jan 1, 2025 + retroactively-effective OBBBA provisions). ⚠ The '
                  "practitioner headline 'Arizona conformed to January 1, 2026' describes "
                  'subsection (A) only. The carve is BY CATEGORY, NOT BY ENUMERATED LIST — neither '
                  'AZDOR nor the Senate Fact Sheet publishes a provision mapping, which is why the '
                  'applied §179 figure is an open Gate-1 ruling. FULL CITATION (trimmed to the '
                  '255-char field cap): H.B. 4168, 57th Leg., 2nd Reg. Sess. (2026), Chapter 140; '
                  'approved by the Governor June 13, 2026 and filed with the Secretary of State '
                  'June 13, 2026. Sec. 12 (§43-105 conformity); Sec. 14 (§43-1021 ¶17 §168(n), '
                  'TY2026); Sec. 15 (§43-1022 ¶¶31/32/35/36, TY2025); Sec. 16 (§43-1041 standard '
                  'deduction); Sec. 22 (§43-1121 ¶25 §168(n), TY2026); Sec. 23 (§43-1122); Sec. 35 '
                  '(retroactivity split)'},
 {'source_code': 'AZ_ARS_43_1022',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'AZ',
  'title': 'A.R.S. §43-1022 — Subtractions from Arizona gross income (individuals)',
  'citation': 'A.R.S. §43-1022(17)(e) (full-§168(k) depreciation subtraction, property placed in '
              'service in taxable years beginning from and after 12/31/2016) and §43-1022(18) '
              '(disposition true-up); read with the addition at §43-1021(11)',
  'issuer': 'Arizona Legislature',
  'official_url': 'https://www.azleg.gov/ars/43/01022.htm',
  'excerpt_label': '§43-1022(17)(e) — individuals conform to §168(k)',
  'excerpt_text': "'an amount equal to the depreciation allowable pursuant to section 167(a) of "
                  'the internal revenue code for the taxable year as computed as if the additional '
                  'allowance for depreciation had been the full amount allowed pursuant to section '
                  "168(k) of the internal revenue code.' Paired addition, §43-1021(11): 'The "
                  'amount of any depreciation allowance allowed pursuant to section 167(a) of the '
                  "internal revenue code to the extent not previously added.'",
  'summary_text': 'Individuals back out the entire federal §167(a) depreciation deduction and '
                  'subtract depreciation computed as if the FULL §168(k) allowance applied — net '
                  'conformity, but two live line items on Form 140 (line 26 subtraction; AZDOR '
                  'procedure ITP 16-2). Unchanged by H.B. 4168 (Sec. 15 reproduces ¶17(e) without '
                  'strike-through). ⚠ The posted azleg ARS text is the pre-H.B. 4168 version as of '
                  '2026-08-06.'},
 {'source_code': 'AZ_ARS_43_1122',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'AZ',
  'title': 'A.R.S. §43-1122 — Subtractions from Arizona gross income (corporations)',
  'citation': 'A.R.S. §43-1122(20) (depreciation computed as if the §168(k)(7) election out had '
              'been made) and §43-1122(5) (disposition true-up); read with the addition at '
              '§43-1121(4)',
  'issuer': 'Arizona Legislature',
  'official_url': 'https://www.azleg.gov/ars/43/01122.htm',
  'excerpt_label': '§43-1122(20) — corporations decouple from §168(k)',
  'excerpt_text': "'An amount equal to the depreciation allowable pursuant to section 167(a) of "
                  'the internal revenue code for the taxable year computed as if the election '
                  'described in section 168(k)(7) of the internal revenue code had been made for '
                  'each applicable class of property in the year the property was placed in '
                  "service.' (§168(k)(7) is the election OUT of bonus.) Paired addition, "
                  "§43-1121(4): 'The amount of any depreciation allowance allowed pursuant to "
                  'section 167(a) of the internal revenue code to the extent not previously '
                  "added.'",
  'summary_text': 'Corporations must maintain a SEPARATE Arizona depreciation schedule and basis '
                  'with bonus elected out — the exact opposite of the individual regime in the '
                  'same tax year. Unchanged by H.B. 4168 (Sec. 23 reproduces ¶20 without '
                  'strike-through despite the section being reopened and applied retroactively to '
                  'TY2025). ⚠ The posted azleg ARS text is the pre-H.B. 4168 version as of '
                  '2026-08-06.'},
 {'source_code': 'OR_ORS_317_010_CONFORMITY',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'OR',
  'title': 'ORS 317.010(7) and ORS 316.012 — definition of "Internal Revenue Code" (two-pronged '
           'conformity)',
  'citation': 'Or. Rev. Stat. §317.010(7); Or. Rev. Stat. §316.012 (ORS 2025 Edition)',
  'issuer': 'Oregon Legislative Assembly',
  'official_url': 'https://www.oregonlegislature.gov/bills_laws/ors/ors317.html',
  'excerpt_label': 'ORS 317.010(7), ORS 2025 Edition — verbatim',
  'excerpt_text': 'Internal Revenue Code, except where the Legislative Assembly has provided '
                  'otherwise, refers to the laws of the United States or to the Internal Revenue '
                  'Code as they are amended and in effect: (a) On December 31, 2023; or (b) If '
                  'related to the definition of taxable income, as applicable to the tax year of '
                  'the taxpayer.',
  'summary_text': 'The controlling two-pronged conformity definition. ORS 316.012 (personal income '
                  'tax) is word-for-word identical with the prongs numbered (1)/(2) — see '
                  'https://www.oregonlegislature.gov/bills_laws/ors/ors316.html. Prong (b) is the '
                  '"rolling reconnect" / "permanent connection," in force for years beginning on '
                  'or after 1/1/2011. Pulled verbatim from the ORS 2025 Edition at '
                  'oregonlegislature.gov as raw HTML and tag-stripped (verification pass '
                  "2026-08-06); the fetcher's summarizing layer had blocked this on the research "
                  "pass. ORS 316.012's amendment credit line ends at 2024 c.75 §21 — no "
                  '2025-session amendment at all, which is independent proof that HB 2092 (which '
                  'would have suspended the rolling prong for TY2025) did not become law. ⚠ '
                  'STANDING WARNING: do NOT use oregon.public.law for any Oregon conformity date — '
                  'confirmed stale on ORS 316.012, ORS 317.010 AND ORS 317A.100.'},
 {'source_code': 'OR_2025_PUB_OR17',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'OR',
  'title': '2025 Publication OR-17, Oregon Individual Income Tax Guide',
  'citation': '150-101-431 (Rev. 01-29-26) — FINAL TY2025',
  'issuer': 'Oregon Department of Revenue',
  'official_url': 'https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf',
  'excerpt_label': 'Pub. OR-17 p. 7 ("Federal tax law") and pp. 90–91 (Addition code 153)',
  'excerpt_text': 'Federal law connection. Oregon has a rolling tie to changes made to the '
                  'definition of federal taxable income, with the exceptions noted below. For all '
                  'other purposes, Oregon is tied to federal income tax laws as amended and in '
                  'effect on December 31, 2023. || Federal depreciation disconnect [Addition code '
                  '153] — This addition is used for reporting a difference in federal and Oregon '
                  'depreciation deductions due to a new change in federal law from which Oregon '
                  'has disconnected. As of the date this publication was last revised, Oregon had '
                  'not disconnected from any new federal depreciation expense provisions for this '
                  'tax year.',
  'summary_text': "THE DOR AUTHORITY TO CITE for Oregon's TY2025 conformity posture, and the "
                  'source that GOVERNS the conflict with the OR-20 / OR-20-S / OR-20-INC corporate '
                  'instructions (brief §12.3). Revision date 01-29-26 is ~7 months AFTER OBBBA, so '
                  'both the rolling-tie statement and the no-new-depreciation-disconnect statement '
                  'are post-OBBBA statements about TY2025, not stale carryovers. Also carries the '
                  'three standing Oregon decouplings (§139A, §529 K-12, §199A) at p. 7, the '
                  'exhaustive list of situations creating an Oregon/federal depreciation '
                  'difference at p. 90, and the federal tax subtraction Table 9 at pp. 71–72.'},
 {'source_code': 'OR_ORS_317_301_DEPR',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'OR',
  'title': 'ORS 317.301 — modification for IRC §168(k) and §179 (2009–2010 deferral, closed '
           'window)',
  'citation': 'Or. Rev. Stat. §317.301(2)–(3), with applicability note 2011 c.7 §31 (ORS 2025 '
              'Edition)',
  'issuer': 'Oregon Legislative Assembly',
  'official_url': 'https://www.oregonlegislature.gov/bills_laws/ors/ors317.html',
  'excerpt_label': 'Applicability note, 2011 c.7 §31 — verbatim',
  'excerpt_text': 'ORS 316.739 and 317.301 apply to tax years beginning on or after January 1, '
                  '2009, and before January 1, 2011.',
  'summary_text': 'The ONLY §168(k)/§179 disconnect in Oregon law, and its window is CLOSED. It '
                  'required an addition for the difference between §168(k)/§179 as applicable to '
                  'the tax year and the same sections as amended and in effect on December 31, '
                  '2008, for tax years beginning on/after 1/1/2009 and before 1/1/2011 only. The '
                  'resulting HIGHER Oregon basis unwinds as subtractions over the remaining asset '
                  'life, so a legacy 2009/2010 asset can still throw an Oregon subtraction in '
                  'TY2025 — the engine needs the per-asset Oregon-basis mechanism even though no '
                  'NEW TY2025 differences arise. Verbatim-verified from the ORS 2025 Edition on '
                  'the 2026-08-06 pass (replaces the stale oregon.public.law citation).'},
 {'source_code': 'MO_RSMO_143_091',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MO',
  'title': '§143.091 RSMo — Meaning of terms (rolling IRC conformity)',
  'citation': 'Mo. Rev. Stat. §143.091 (eff. 1/1/1990, unamended)',
  'issuer': 'Missouri Revisor of Statutes',
  'official_url': 'https://revisor.mo.gov/main/OneSection.aspx?section=143.091',
  'excerpt_label': '§143.091 RSMo — verbatim',
  'excerpt_text': 'Any reference in sections 143.011 to 143.996 to the laws of the United States '
                  'shall mean the provisions of the Internal Revenue Code of 1986, and amendments '
                  'thereto, and other provisions of the laws of the United States relating to '
                  'federal income taxes, as the same may be or become effective, at any time or '
                  'from time to time, for the taxable year.',
  'summary_text': "Missouri's ROLLING conformity anchor. Pulled in full and verified verbatim on "
                  'the 2026-08-06 adversarial pass; effective 1/1/1990 and unamended. OBBBA '
                  'therefore applies for TY2025 with no adoption act — none was needed and none '
                  'was enacted.'},
 {'source_code': 'MO_RSMO_143_121',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MO',
  'title': '§143.121 RSMo — Missouri adjusted gross income (modifications)',
  'citation': 'Mo. Rev. Stat. §143.121.2(3), .2(4), .3(7), .3(9), .3(14)(a)–(b), .6(2)',
  'issuer': 'Missouri Revisor of Statutes',
  'official_url': 'https://revisor.mo.gov/main/OneSection.aspx?section=143.121',
  'excerpt_label': '§143.121.3(14)(a)–(b) and the JCWAA depreciation window — verbatim',
  'excerpt_text': '(14)(a) For all tax years beginning on or after January 1, 2025, one hundred '
                  'percent of all income reported as a capital gain for federal income tax '
                  'purposes by an individual subject to tax pursuant to section 143.011 ... (b) '
                  '... beginning on or after January first of the tax year following the tax year '
                  'in which the top rate of tax imposed pursuant to section 143.011 is equal to or '
                  'less than four and one-half percent ... by an entity subject to tax pursuant to '
                  'section 143.071. || [.2(3) / .3(7)] property purchased on or after July 1, '
                  '2002, but before July 1, 2003.',
  'summary_text': 'The modifications statute — and the proof of BOTH Missouri negatives. Pulled in '
                  'FULL and searched on the verification pass: ZERO occurrences of the string '
                  '"179," and every §168 reference is tied to the Job Creation and Worker '
                  'Assistance Act of 2002 window (2002–2003), so there is NO §168(k) add-back and '
                  'NO §179 modification for TY2025. Also the home of the TY2025 100% capital gains '
                  'deduction (individuals only; corporate leg trigger-gated at ≤4.5%), the '
                  'excessive NOL carryback/carryforward addition at .2(4), and the '
                  'beginning-farmer farmland tiered subtraction at .6(2).'},
 {'source_code': 'MO_2025_TAX_LEG_CHANGES',
  'source_type': 'state_conformity_notice',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MO',
  'title': '2025 Tax Legislative Changes',
  'citation': 'Missouri DOR, 2025 Tax Legislative Changes (HB 594 & HB 508; §143.121)',
  'issuer': 'Missouri Department of Revenue',
  'official_url': 'https://dor.mo.gov/taxation/individual/tax-types/income/year-changes/documents/2025-Tax-Legislative-Changes.pdf',
  'excerpt_label': 'DOR statement on the capital gains deduction and the TY2025 rate — verbatim',
  'excerpt_text': 'The individual income tax rate for tax year 2025 is 4.7%. || This subtraction '
                  'is effective for individuals starting January 1, 2025. This subtraction will be '
                  'effective for corporations starting January 1st of the tax year following the '
                  'reduction of the individual income tax to 4.5%.',
  'summary_text': "The DOR's own TY2025 legislative-changes notice. Establishes the 4.7% top "
                  'individual rate as a VERIFIED rather than projected figure, and states the '
                  'individual-only / corporate-trigger-gated split of the §143.121.3(14) capital '
                  'gains deduction. Lists NO OBBBA decoupling — corroborating rolling conformity.'},
 {'source_code': 'MO_RSMO_143_436',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MO',
  'title': '§143.436 RSMo — SALT Parity Act (pass-through entity tax)',
  'citation': 'Mo. Rev. Stat. §143.436.3(1), .4(1), .8, .9(2), .10 (eff. 8/28/2024)',
  'issuer': 'Missouri Revisor of Statutes',
  'official_url': 'https://revisor.mo.gov/main/OneSection.aspx?section=143.436',
  'excerpt_label': '§143.436.3(1) — the PTE base import clause (leg 2 of the conflict)',
  'excerpt_text': '...shall be decreased by the percentage deduction that would be allowable to '
                  'the owners under section 143.022, and increased or decreased by any '
                  'modification made pursuant to sections 143.121 and 143.141 that relates to an '
                  "item of the affected business entity's income, gain, loss, or deduction...",
  'summary_text': 'The PTET statute — and one half of the OPEN statute-vs-form conflict escalated '
                  'to Ken as a Gate-1 walk item: on its face §143.436.3(1)/.4(1) imports "any '
                  'modification made pursuant to sections 143.121," which would include the 100% '
                  'capital gain subtraction, while the FINAL TY2025 MO-PTE (reissued 2026-01-08) '
                  'carries no such line. §143.436.8: the owner credit is NON-REFUNDABLE with '
                  'UNLIMITED carryforward; §143.436.9(2): the reciprocal out-of-state credit has '
                  'NO carryforward; §143.436.10: corporate and fiduciary members also get the '
                  'credit, applied after all other credits.'},
 {'source_code': 'MO_2025_PTE_INSTR',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MO',
  'title': 'Form MO-PTE Instructions, 2025',
  'citation': 'Missouri DOR Form MO-PTE Instructions (FINAL TY2025; PDF ModDate 2026-01-08)',
  'issuer': 'Missouri Department of Revenue',
  'official_url': 'https://dor.mo.gov/forms/MO-PTE%20Instructions_2025.pdf',
  'excerpt_label': 'MO-PTE Line 10 rate, and the closed subtraction list',
  'excerpt_text': 'Enter the amount of Line 9 multiplied by 4.7 percent. || [Page 3, Part A '
                  'Subtractions is a closed enumerated list, Lines 6–11 (exempt federal '
                  'obligations / ... / broadband grant / agricultural disaster relief / §163(j) '
                  'interest), totalled at Line 12 — NO capital-gain subtraction line.]',
  'summary_text': 'The FINAL TY2025 PTE instructions — the other half of the §12.4 conflict. These '
                  'carry the LATEST ModDate of the four module forms (2026-01-08), i.e. the '
                  'Department had every opportunity to add a capital-gain line after the 2025 '
                  'session that created §143.121.3(14) and did not. Also the source for the 4.7% '
                  'rate, the annual/irrevocable election, the member opt-out (MO-PTENR / MO-PTE '
                  'Opt-Out, gated on an un-extended deadline on or after 8/28/2025), the 4/15/2026 '
                  'due date, Schedule PTE-BD, and Form MO-MS PTE.'},
 {'source_code': 'MS_CODE_27_7_17',
  'source_type': 'state_statute',
  'source_rank': 'controlling',
  'jurisdiction_code': 'MS',
  'title': 'Miss. Code Ann. §27-7-17 — deductions allowed (depreciation, §179, §174, itemized '
           'deductions)',
  'citation': 'Miss. Code Ann. §27-7-17(1)(a), (1)(d)(ii), (1)(f)(i), (1)(f)(ii)1–6, (1)(k), '
              '(3)(a)–(b), as amended by HB 1733, 2023 Reg. Sess. (eff. 1/1/2023)',
  'issuer': 'Mississippi Legislature / Mississippi Code',
  'official_url': 'https://billstatus.ls.state.ms.us/documents/2023/html/HB/1700-1799/HB1733SG.htm',
  'excerpt_label': '§27-7-17(1)(f)(ii)2 (own 100% bonus), 4.a–b (1/1/2021 freeze), 3 (§179 '
                   'rolling), (1)(f)(i) (aviation)',
  'excerpt_text': 'For the purpose of computing income tax for tax years beginning after December '
                  '31, 2022, expenditures for business assets that are qualified property or '
                  'qualified improvement property shall be eligible for one hundred percent (100%) '
                  'bonus depreciation and may be deducted as an expense incurred by the taxpayer '
                  'during the tax year during which the property is placed in service, '
                  'notwithstanding any changes to federal law related to cost recovery beginning '
                  "on January 1, 2023, or on any other date. || 'Qualified property' means and has "
                  'the same definition as such term has in 26 USCS Section 168(k) as it existed on '
                  "January 1, 2021. || Mississippi's treatment of the deduction shall conform to "
                  'the provisions of 26 USCS Section 179 in effect for that year. || In the case '
                  'of new or used aircraft, equipment, engines, or other parts and tools used for '
                  'aviation, allowance for bonus depreciation conforms with the federal bonus '
                  'depreciation rates and reasonable allowance for depreciation under this section '
                  'is no less than one hundred percent (100%).',
  'summary_text': "Mississippi's cost-recovery and deduction statute — the anchor for a state with "
                  'NO general conformity statute and NO conformity date. Enrolled HB 1733 text '
                  'fetched from the OFFICIAL billstatus.ls.state.ms.us; the CURRENT CODIFIED text '
                  'was separately confirmed unamended for TY2025 via the Findlaw mirror '
                  '(https://codes.findlaw.com/ms/title-27-taxation-and-finance/ms-code-sect-27-7-17/, '
                  'stamped current as of 1/1/2025). ⚠ The mirror-sourced confirmations (current '
                  'codified status, §27-7-17(3)(a) itemized-deduction hook, (3)(b) standard '
                  'deduction) MUST BE RE-PULLED from the official Mississippi Code before specs '
                  'are authored — Justia and sos.ms.gov returned HTTP 403. DOR corroboration: MS '
                  'DOR Depreciation Notice, 10/20/2023, '
                  'https://www.dor.ms.gov/news/depreciation-notice.'},
 {'source_code': 'MS_2025_83_100_INSTR',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MS',
  'title': '2025 Corporate Income and Franchise Tax Instructions',
  'citation': 'Form 83-100-22-1-1-000 (Rev. 01/26, dated November 2025) — FINAL TY2025',
  'issuer': 'Mississippi Department of Revenue, Income and Franchise Tax Bureau',
  'official_url': 'https://www.dor.ms.gov/sites/default/files/tax-forms/business/2025%20CIT%20INSTRUCTIONS%2083-100%20-%20Final%20%2001.14.2026.pdf',
  'excerpt_label': 'Form 83-122 line 6 / line 13 depreciation mechanics, and the non-conformity '
                   'statements',
  'excerpt_text': 'Federal Form 4562 must be completed twice and attached immediately after Form '
                  '83-122. The first submission reflects the deductions taken for federal income '
                  "tax purposes. The second submission should be labeled 'Mississippi' at the top "
                  'of the form and will compute the apportionable and/or allocable depreciation '
                  'deduction according to Mississippi statutes in effect in the year the business '
                  'assets were placed in service. || When a special depreciation allowance is '
                  'taken for federal tax purposes, the depreciable base must be reduced by the '
                  'amount of the allowance. Enter the additional depreciation expense for purposes '
                  'of this state due to the basis adjustment not being made for state purposes. || '
                  'Mississippi does not conform to federal net operating loss rules. || '
                  'Mississippi does not follow federal rules concerning installment sales.',
  'summary_text': 'FINAL TY2025 corporate booklet. Source for the dual-Form-4562 mechanic and the '
                  'separate unreduced Mississippi basis (Form 83-122 lines 6 and 13, which '
                  'cross-reference each other), the NOL non-conformity and the MS '
                  '2-back/20-forward period (p. 9), the installment-sale and '
                  'extraterritorial-income non-conformity (p. 8), the corporate 0%/4%/5% rate '
                  'schedule, the franchise rate and phase-out table, and the apportionment '
                  'authority. Retrieved by direct HTTP client — www.dor.ms.gov serves an '
                  'incomplete TLS chain and WebFetch fails on it.'},
 {'source_code': 'MS_2025_84_100_INSTR',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MS',
  'title': '2025 Pass-Through Entity Income and Franchise Tax Instructions',
  'citation': 'Form 84-100-22-1-1-000 (Rev. 01/26, dated November 2025) — FINAL TY2025',
  'issuer': 'Mississippi Department of Revenue',
  'official_url': 'https://www.dor.ms.gov/sites/default/files/tax-forms/business/2025%20PTE%20INSTRUCTIONS%2084-100%20-%20Final%20%2001.14.2026.pdf',
  'excerpt_label': 'PTE / composite rate schedule, binding election, and the MS §179 K-1 box',
  'excerpt_text': 'Income Tax (Composite and Electing Pass-Through Entity): 0% on the first $5,000 '
                  'of taxable income, 4% on the next $5,000 of taxable income and 5% on all '
                  'taxable income in excess of $10,000. || The election shall be binding for the '
                  'taxable year and all subsequent taxable years unless the election is revoked by '
                  "the electing PTE. || [Form 84-132 Box 13] Enter the owner's share of "
                  'Mississippi Section 179 deduction. Attach a copy of the federal Form 4562. || '
                  'Mississippi Law does not conform to federal with respect to the tax treatment '
                  'of capital gains; therefore, the gain is taxed as ordinary income.',
  'summary_text': 'FINAL TY2025 pass-through booklet. Source for the unreduced 0/4/5 schedule '
                  'applied to composite filers AND electing PTEs (stated in two independent '
                  'places), the binding-for-all-later-years PTET election on Form 84-381, the '
                  'owner-side credit and its refund-or-carryforward election, the $200 estimate '
                  'threshold, the MISSISSIPPI §179 K-1 box (Form 84-132 Box 13 — the correction '
                  'that keeps the K-1 box from being omitted), and the capital-gain character '
                  'non-conformity. Note the PTE depreciation add-back analogue is Form 84-122 LINE '
                  '8, not line 6.'},
 {'source_code': 'MS_2025_80_100_INSTR',
  'source_type': 'state_instruction',
  'source_rank': 'primary_official',
  'jurisdiction_code': 'MS',
  'title': '2025 Resident, Non-Resident and Part-Year Resident Income Tax Instructions',
  'citation': 'Form 80-100-25-1-1-000 (Rev. 12/25) — FINAL TY2025',
  'issuer': 'Mississippi Department of Revenue, Individual Income Tax Bureau',
  'official_url': 'https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf',
  'excerpt_label': 'Schedule A instructions, Lines 3a–3c (Taxes Paid) — the OBBBA SALT note',
  'excerpt_text': 'Note: Per the One Big Beautiful Bill Act, there is a $40,000 limitation '
                  '($20,000 if married filing separately) on this deduction. || Income Tax: 0% on '
                  'the first $10,000.00 of taxable income and 4.4% on taxable income in excess of '
                  '$10,000.00.',
  'summary_text': 'FINAL TY2025 individual booklet. Carries the ONLY explicit OBBBA reference in '
                  'any of the four Mississippi booklets (it appears exactly once) — the $40,000 '
                  'SALT cap on the Mississippi itemized deduction, citing §27-7-17(3)(a)(i). ⚠ '
                  'That note is NOT the whole OBBBA story: §27-7-17(3)(a) adopts the federal '
                  'itemized-deduction AMOUNT by undated, rolling reference, so every OBBBA change '
                  'to federal itemized deductions flows into Form 80-108 Schedule A automatically. '
                  'Also the source for the 0%/4.4% individual rate schedule, the filing thresholds '
                  '($8,300 / $16,600 plus $1,500 per dependent), and the HB 1 (2025) legislative '
                  'summary.'},
 {'source_code': 'LA_RS_47_CONFORMITY',
 'source_type': 'state_statute',
 'source_rank': 'controlling',
 'jurisdiction_code': 'LA',
 'title': 'La. R.S. 47:287.701 / 47:293 / 47:287.744 / 47:297.25 - Louisiana IRC conformity and the state '
          'expensing election',
 'citation': 'La. R.S. 47:287.701(A)-(B); 47:287.65; 47:293(1); 47:287.744; 47:297.25; 47:287.12; 47:32; '
             '47:601',
 'issuer': 'Louisiana Legislature',
 'official_url': 'https://legis.la.gov/legis/Law.aspx?d=101459',
 'current_status': 'active',
 'is_substantive_authority': True,
 'trust_score': 9.6,
 'excerpt_label': "Rolling conformity by 'as amended'; the state election freezes its OWN definitions at "
                  '1/1/2024',
 'excerpt_text': 'R.S. 47:287.701(A): "Federal law means the Internal Revenue Code of 1986, AS AMENDED, '
                 '(Title 26 United States Code) and applicable U.S. Treasury Regulations." No conformity '
                 'DATE exists anywhere in the income-tax chapters. Corporate net income starts from federal '
                 'taxable income (47:287.65); individual from federal AGI (47:293(1)). OBBBA (P.L. 119-21) '
                 'is therefore IN for TY2025 by flow-through. THE ONE DELIBERATE EXCEPTION: the state '
                 'elective full-expensing statutes (47:287.744 corporate / 47:297.25 individual-fiduciary, '
                 'from Acts 5 and 11 of the 2024 Third Extraordinary Session) freeze THEIR IRC references at '
                 'January 1, 2024 - that freeze governs only the STATE ELECTION definitions, never the '
                 'federal starting point.',
 'summary_text': "Rolling ('as amended'), no conformity date; OBBBA in for TY2025; the state expensing "
                 'election freezes only its own definitions at 1/1/2024.'}]

TIER1_ROWS: list[dict] = [{'jurisdiction_code': 'CA',
  'conformity_type': 'static',
  'authority_source_code': 'CA_SB711_2025_CONFORMITY',
  'federal_reference_note': 'IRC conformity date moved from January 1, 2015 to JANUARY 1, 2025 by '
                            'SB 711 (McNerney), Chapter 231, Statutes of 2025, chaptered 10/1/2025 '
                            '— effective for taxable years beginning on or after January 1, 2025. '
                            'The date sits at R&TC §17024.5(a)(1)(Q) (Personal Income Tax Law); '
                            'the Corporation Tax Law picks it up by cross-reference at R&TC '
                            '§23051.5(a)(1) — SB 711 does not amend §23051.5 and does not need to. '
                            'Cite for corporate code comments: R&TC §23051.5(a)(1) → '
                            '§17024.5(a)(1)(Q). Because the new date PRE-DATES OBBBA (P.L. 119-21, '
                            'enacted 7/4/2025), California does NOT conform to OBBBA for TY2025.',
  'summary': 'California is a STATIC (fixed-date) conformity state that jumped its IRC conformity '
             'date from 1/1/2015 to 1/1/2025 via SB 711 (Ch. 231, Stats. 2025), with extensive '
             'selective decoupling on top. OBBBA is NOT adopted for TY2025 — FTB states it '
             "affirmatively across the TY2025 booklets: 'In general, California R&TC does not "
             "conform to the OBBBA.' §168(k)/(n) bonus is not conformed for any entity type and "
             'there is no add-back-then-recover mechanism — California computes its own '
             'depreciation from its own basis, producing a permanent per-asset basis divergence. '
             '§179 is frozen at $25,000 / $200,000. The state-specific hazard: CORPORATIONS (Form '
             '100 / 100W / 100S) do not use MACRS at all — they use pre-ACRS R&TC §§24349–24354 '
             'methods with useful life and salvage value, plus the R&TC §24356 additional '
             'first-year depreciation capped at $2,000.',
  'decoupled_items': [{'item': 'IRC §168(k)/(n) bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent); §168(n) '
                                            '100% election for qualified production property.',
                       'state_treatment': 'NOT conformed for ANY entity type — flat non-adoption. '
                                          'California does NOT use the Georgia-style '
                                          'add-back-then-recover pattern: it computes its own '
                                          'depreciation from its own basis and reports the '
                                          'difference as a federal/state adjustment (Schedule CA '
                                          'for individuals; FTB 3885 / 3885A / 3885P otherwise). '
                                          'Result is a PERMANENT basis divergence tracked per '
                                          'asset, not a scheduled add-back recovery.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': "FTB 3885A lists both 'Additional depreciation (IRC Section "
                                "168(k))' and the '100% depreciation election for qualified "
                                "production property (IRC Section 168(n))' as California/federal "
                                'differences; FTB 3885 lists §168(k) as a corporate nonconformity; '
                                'Form 565 lists §168(k) as a federal/state difference.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': '$25,000 maximum deduction / $200,000 phaseout threshold '
                                          '— frozen at a pre-TCJA level. Statutory cites: PIT R&TC '
                                          '§17255; Corporate R&TC §24356(b)(2) (limit) and '
                                          '§24356(b)(3) (threshold). California also does NOT '
                                          'allow the §179 election for off-the-shelf computer '
                                          'software, and does not conform to the expanded §179 '
                                          'property definition (lodging-related tangible personal '
                                          'property; qualified improvements to nonresidential real '
                                          'property).',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': 'Verified verbatim on BOTH FTB 3885 and FTB 3885A (FINAL TY2025). '
                                '§179 is not deducted at the partnership level — Form 565 line 17a '
                                'excludes it; it passes through separately on Schedule K (565)/K-1 '
                                '(565) line 12. §179 recapture: for an S corporation the recapture '
                                "gain must be included in the S corporation's OWN California "
                                'taxable income (Form 100S Gen. Info. FF, Form 100S line 4).'},
                      {'item': 'MACRS for corporations — the California non-MACRS corporate regime',
                       'federal_treatment': 'MACRS recovery periods, conventions and percentage '
                                            'tables under IRC §168.',
                       'state_treatment': 'CORPORATIONS (Form 100, 100W, 100S) do NOT use MACRS. '
                                          "FTB 3885 lists as a nonconformity: 'The depreciation "
                                          'under Modified Accelerated Cost Recovery System (MACRS) '
                                          'for corporations, except to the extent such '
                                          'depreciation is passed through from a partnership or '
                                          "LLC classified as a partnership.' Corporate methods "
                                          'come from R&TC §§24349–24354: straight-line (net of a '
                                          'reasonable salvage value), declining balance at up to '
                                          '200% of the SL rate, sum-of-the-years-digits, the Class '
                                          'Life ADR System (post-1970 assets), and the Guideline '
                                          'Class Life System (pre-1971) — useful-life and '
                                          'salvage-value based.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': '⚠ §12 RESOLVED THE SCOPE: this dual regime is CORPORATE-ONLY. '
                                "R&TC §17250 opens 'Section 168 of the Internal Revenue Code is "
                                "modified as follows' — the Personal Income Tax Law DOES adopt "
                                'MACRS, carving out §168(j)/(k)/(l)/(m) and overriding grapevines '
                                "(phylloxera/Pierce's disease) to 5-year. So individuals and "
                                'pass-throughs CAN reuse the federal MACRS tables, subject only to '
                                "no §168(k), the $25,000/$200,000 §179 cap, California's own §280F "
                                'limits, and the grapevine class-life override. Only the corporate '
                                'track needs the §24349 engine. Further qualifier per §12: FTB '
                                "3885 states 'Under Cal. Code Regs., tit. 18 section 24349(l), "
                                "California conforms to the federal useful lives of property' per "
                                'IRS Rev. Proc. 87-56 — corporate CLASS LIVES are federal; what '
                                'diverges is the method, the salvage-value floor, and the absence '
                                'of MACRS conventions and tables. The engine can reuse Rev. Proc. '
                                '87-56 class lives for corporations, but NOT the MACRS percentage '
                                'tables. Note: FTB 3885P has no standalone TY2025 instructions '
                                'page (2025-3885p-instructions.html returns HTTP 404); it is '
                                'covered inside the Form 565 booklet — the statutory route '
                                '(§17250) is the durable cite.'},
                      {'item': 'R&TC §24356 additional first-year depreciation (corporations)',
                       'federal_treatment': "No CURRENT federal analogue — this is California's "
                                            'retained version of the pre-1981 federal additional '
                                            'first-year depreciation.',
                       'state_treatment': 'Corporations may deduct up to 20% of the cost of '
                                          "'qualifying property' in the year acquired, in addition "
                                          'to regular depreciation. MAXIMUM DEDUCTION $2,000 (FTB '
                                          '3885 Part II, line 14 column (h)). Qualifying property '
                                          '= tangible personal property used in business with a '
                                          'useful life of at least six years; land, buildings and '
                                          'structural components do not qualify, nor does property '
                                          'converted from personal use or acquired by gift, '
                                          'inheritance, or from a related party. Basis for regular '
                                          'depreciation must be reduced by the amount claimed. '
                                          "MUTUALLY EXCLUSIVE WITH §179: 'The corporation may only "
                                          'elect IRC Section 179 or the additional first year '
                                          "depreciation deduction for the same taxable year.' The "
                                          'election must be made on a timely filed return '
                                          '(including extension) and is revocable only with FTB '
                                          'consent.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': '⚠ The cap has two statutory forms: R&TC §24356(a)(2) caps the '
                                'COST TAKEN INTO ACCOUNT at $10,000; FTB states the resulting '
                                '$2,000 DEDUCTION ceiling (20% × $10,000 = $2,000). ENCODE $2,000; '
                                'CITE $10,000. §12 CORRECTED the framing: the brief originally '
                                "called this 'California-only … no federal analogue', but FTB 3885 "
                                "in fact lists it under 'California law conforms to federal law "
                                "for the following' — it is a retained pre-1981 federal provision, "
                                'not a California invention. Computation unaffected. Mutual '
                                "exclusivity has a statutory anchor at §24356(b)(1) 'In lieu of "
                                "subdivision (a), Section 179 … applies.'"},
                      {'item': 'IRC §280F luxury auto limits',
                       'federal_treatment': 'Federal §280F modifications to the passenger-auto '
                                            'depreciation caps.',
                       'state_treatment': 'NOT conformed — California publishes its own table for '
                                          'calendar-2025 placed-in-service vehicles. Passenger '
                                          'autos (not trucks/vans) / trucks and vans: 1st year '
                                          '$3,860 / $4,360; 2nd year $6,100 / $6,900; 3rd year '
                                          '$3,650 / $4,150; each succeeding year $2,175 / $2,475.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': '§12 RESOLVED ([UNVERIFIED-4]): FTB 3885 really does head the '
                                "truck/van table 'placed in service in the calendar year 2024' on "
                                'the FINAL page, but FTB 3885A (also FINAL TY2025) heads a single '
                                "block '…calendar year 2025' covering both sub-tables with "
                                'IDENTICAL truck/van figures. Two FINAL TY2025 FTB forms agree on '
                                'the figures; only the 3885 heading is stale. ENCODE THE FIGURES '
                                'AS TY2025 and treat the 3885 heading as an FTB typo, not a '
                                'substantive rule.'},
                      {'item': 'IRC §199A qualified business income deduction',
                       'federal_treatment': '20% QBI deduction.',
                       'state_treatment': 'NOT conformed for TY2025.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': 'Listed among the TCJA-era non-conformed items in §2 of the brief; '
                                'also listed as a federal/state difference in the Form 565 '
                                'booklet.'},
                      {'item': 'IRC §163(j) business interest limitation',
                       'federal_treatment': '30%-of-ATI limitation on business interest.',
                       'state_treatment': 'NOT conformed for TY2025.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': 'Listed among the TCJA-era non-conformed items; SB 711 continued '
                                'the decoupling.'},
                      {'item': 'IRC §174 / §174A research & experimental amortization '
                               'modifications',
                       'federal_treatment': 'Federal §174 / §174A R&E amortization rules as '
                                            'modified.',
                       'state_treatment': 'NOT conformed for TY2025.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': 'Listed as a nonconformity on FTB 3885A; SB 711 continued the '
                                'decoupling from §174.'},
                      {'item': 'IRC §951A GILTI',
                       'federal_treatment': 'GILTI inclusion regime.',
                       'state_treatment': 'NOT conformed for TY2025.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': 'Listed among the TCJA-era non-conformed items in §2.'},
                      {'item': 'OBBBA-specific provisions named by FTB as not followed',
                       'federal_treatment': 'OBBBA (P.L. 119-21) 100% bonus depreciation, §168(n) '
                                            'qualified production property, increased individual '
                                            'SALT deduction limitation, expanded §529 qualified '
                                            'expenses (including postsecondary credentialing), '
                                            'expanded §1202 QSBS gain exclusion, and extension of '
                                            'the disaster-related personal casualty loss rules.',
                       'state_treatment': 'NONE of these are adopted for TY2025 — OBBBA was '
                                          'enacted 7/4/2025, after the 1/1/2025 specified date, so '
                                          'it is outside the incorporated Code.',
                       'authority_source_code': 'CA_SB711_2025_CONFORMITY',
                       'notes': "This is a 'the rule says no,' not a 'no rule found' — FTB states "
                                'it affirmatively and identically across the TY2025 booklets. '
                                'Other California non-conformity carried in the same list: §280F '
                                'luxury auto modifications, §1045 and §1202 QSBS '
                                'deferral/exclusion, qualified opportunity zone deferral and '
                                'exclusion, the federal NOL modifications, and §382(n).'}],
  'notes': 'PTET: CALIFORNIA HAS ONE AND IT DID NOT SUNSET. TY2025 runs the ORIGINAL, STRICTER AB '
           '150/SB 113 regime (R&TC §§17052.10, 19900–19906) at 9.3% of qualified net income — '
           'elective, ANNUAL, made only on an original timely filed return, irrevocable for the '
           'year once made, binding on all owners; the June 15 prepayment (greater of $1,000 or '
           "50% of the prior year's PTE elective tax) is MANDATORY and missing it INVALIDATES the "
           'election. SB 132 (Ch. 17, Stats. 2025) extended PTET for TYs beginning on/after '
           '1/1/2026 and before 1/1/2031 under a DIFFERENT scheme (R&TC §§17052.11, 19910, 19912, '
           '19914, 19916) where a missed June 15 payment no longer invalidates the election but '
           "reduces the owner's credit by 12.5% — DO NOT APPLY THE 12.5% RELIEF TO TY2025. "
           'Owner-side treatment is a NONREFUNDABLE CREDIT (9.3%, 5-year carryover, FTB 3804-CR), '
           'not a deduction and not an exclusion; the credit is NOT a pass-through item. '
           'Entity-side: if the entity deducts the PTE elective tax federally, that amount is '
           'ADDED BACK for California purposes. OSTC ordering interaction applies for TYs '
           '2022–2030. Forms: FTB 3804 (calculation, → Form 100S line 29 / Form 565 line 25 / Form '
           '568 line 4), FTB 3893 (payment voucher — never used to make the election), FTB 3804-CR '
           '(owner credit). ⚠ MID-CHANGE / RESIDUAL RISK: [UNVERIFIED-9] the SB 711 Appendix '
           'Conformity Chart (Senate Rev. & Tax., 9/5/2025) was NOT read item by item — a '
           'long-tail TY2025 conformity change displacing a pre-2025 California rule could still '
           'be lurking; this MUST be closed before individual-module specs are authored. Also '
           'still open: [UNVERIFIED-6] the FTB software-developer program calendar is genuinely '
           'unpublished (Ken-only action; the Letter of Intent gates schema access), and '
           '[UNVERIFIED-8] Form 592-PTE distributive-share withholding specifics. SCOPE: '
           "California is the campaign's LARGEST state and runs as its own dedicated pilot wave — "
           'nothing from GA/SC/AL/NC ports here. Newly conformed at TY2025 (changes, not '
           'carryovers): §1031 like-kind exchanges limited to real property, and the alimony '
           '§§71/215 repeal but only for agreements executed after 12/31/2025 (so nil effect on '
           'TY2025 returns — do NOT code the federal post-2018 rule into CA TY2025). Other TY2025 '
           'structural limits: NOL carryover deduction SUSPENDED for TYs 2024–2026 with TWO '
           'different exemption tests (corporations: taxable income < $1,000,000; individuals: net '
           'business income OR modified AGI < $1,000,000 — §12 correction, do not share one '
           'constant), and a $5,000,000 credit limitation (R&TC §§23036.4, 23036.5). No local '
           'income tax exists or may exist — R&TC §17041.5 affirmatively prohibits it; safe to '
           'hard-code zero. ACCESS NOTE: ftb.ca.gov returns HTTP 403 to WebFetch but HTTP 200 to '
           'curl with a normal browser User-Agent; leginfo.legislature.ca.gov serves WebFetch '
           'normally.'},
 {'jurisdiction_code': 'FL',
  'conformity_type': 'static',
  'authority_source_code': 'FL_FS_220_03_CONFORMITY',
  'federal_reference_note': 'IRC as amended and in effect on JANUARY 1, 2025 — s. 220.03(1)(n), '
                            'F.S. (2025), set by ss. 60–61, ch. 2025-208, L.O.F., which adopted '
                            'the IRC retroactively to January 1, 2025. s. 220.03(2)(c) carries the '
                            'same date through to every defined term used in ch. 220. The date is '
                            're-adopted annually by the Legislature. Because it PRE-DATES OBBBA '
                            '(P.L. 119-21, enacted 7/4/2025), OBBBA is NOT adopted for Florida '
                            'TY2025. The 2026 conformity update (HB 7031 = ch. 2026-137, L.O.F.) '
                            "moved the date to January 1, 2026 but 'operate[s] retroactively to "
                            "January 1, 2026' — it does NOT reach TY2025.",
  'summary': 'Florida is a STATIC fixed-date conformity state, re-adopted annually, sitting at '
             'January 1, 2025 for TY2025. It is an ENTITY-ONLY lane: a single corporate '
             'income/franchise tax at 5.5% on federal taxable income with Florida modifications, '
             'apportioned 25 property / 25 payroll / 50 sales, less a $50,000 exemption — no '
             'individual income tax, no PTET, and no fiduciary income tax return. OBBBA is NOT '
             'adopted for TY2025, so a TY2025 Florida return must start from federal taxable '
             'income recomputed under the PRE-OBBBA Code. §168(k) bonus is a 100% add-back '
             'recovered one-seventh per year over seven years; QIP has its own separate add-back '
             'and recovery; and there is NO Florida §179 add-back at all — §179 flows at the '
             'pre-OBBBA TY2025 limit of $1,250,000 / $3,130,000 (SUV sublimit $31,300).',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': 'OBBBA 100% bonus for property acquired and placed in '
                                            'service after 1/19/2025. But for the FLORIDA '
                                            'computation the operative federal Code is the '
                                            '1/1/2025 (pre-OBBBA) Code, whose bonus percentage for '
                                            'calendar-2025 placed-in-service property is 40%.',
                       'state_treatment': '100% ADD-BACK of the amount deducted federally as bonus '
                                          'depreciation under ss. 167 and 168(k), IRC, for assets '
                                          'placed in service AFTER DECEMBER 31, 2007 AND BEFORE '
                                          'JANUARY 1, 2027 (s. 220.13(1)(e), F.S.; F-1120 Schedule '
                                          'I Line 21). RECOVERY: an annual subtraction of '
                                          'ONE-SEVENTH of the addition over a SEVEN-YEAR period '
                                          'beginning with the taxable year of the addition (F-1120 '
                                          'Schedule II Line 9). A supporting schedule showing the '
                                          'year and amount of each original addition and each '
                                          "year's subtraction must be attached.",
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': '§12 CONFIRMED the fraction (one-seventh) and ADDED the opening '
                                'date of the window (after 12/31/2007), which the draft omitted — '
                                'immaterial for TY2025 but load-bearing for prior-year carryover '
                                'schedules. Compounding effect: net TY2025 result is no '
                                'current-year bonus benefit in Florida either way, but the AMOUNT '
                                'of the add-back and of the seven-year subtraction schedule '
                                'differs from the federal 4562 whenever the taxpayer claimed OBBBA '
                                '100% bonus federally. This is a DERIVED conclusion — [UNVERIFIED] '
                                'item 2 remains open: DOR has published no TY2025 line-level '
                                'guidance, and F-1120N R. 01/26 read cover to cover (17 pp.) has '
                                'ZERO occurrences of OBBBA, P.L. 119-21, or any recompute '
                                'instruction.'},
                      {'item': 'Qualified improvement property (QIP), IRC §168(e)(6)',
                       'federal_treatment': 'QIP depreciated under s. 167(a) or bonus-depreciated '
                                            'under s. 167 or s. 168(k), including the retroactive '
                                            'CARES Act change.',
                       'state_treatment': 'SEPARATE, PERMANENT ADD-BACK with its own recovery. '
                                          'Addition equal to the federally deducted depreciation '
                                          'on QIP placed in service on or after January 1, 2018 '
                                          '(F-1120 Sch. I Line 22). Subtraction limited to the '
                                          'depreciation that WOULD have been allowed under the IRC '
                                          'in effect on January 1, 2020, WITHOUT the retroactive '
                                          'CARES Act change and WITHOUT regard to any sale or '
                                          'other disposition of the property (F-1120 Sch. II Line '
                                          '10).',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'Interaction rule printed in the instructions: if QIP bonus was '
                                'already added back on Sch. I Line 21, it is NOT added back again '
                                'on Line 22. The one-seventh recovery in s. 220.13(1)(e) DOES NOT '
                                'apply to QIP add-backs — QIP has its own recovery mechanism. '
                                'Confirmed by §12 at F-1120N Sch. II Lines 9/10.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'NO FLORIDA ADD-BACK. The s. 220.13(1)(e) §179 add-back '
                                          'is expired by its own terms — it applies only to §179 '
                                          'amounts in excess of $128,000 for taxable years '
                                          'beginning after December 31, 2007 and before January 1, '
                                          '2015. The TY2025 F-1120 and F-1120N contain NO §179 '
                                          "line and NO §179 instruction. Florida's TY2025 §179 "
                                          'limit is therefore whatever §179 provides in the IRC as '
                                          'in effect January 1, 2025 — the pre-OBBBA, '
                                          'inflation-indexed limit: $1,250,000 expensing '
                                          'limitation / $3,130,000 phase-out threshold / $31,300 '
                                          'sport utility vehicle sublimit.',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': "⚠ §12 RESOLVED THE FIGURES (was [UNVERIFIED] item 1, 'do not "
                                "guess'). Source: Rev. Proc. 2024-40 §2.25, I.R.B. 2024-45, "
                                'fetched live from irs.gov and read in full on 2026-08-06 — §2.25 '
                                "is intact and unaltered; the prior draft's claim that Rev. Proc. "
                                "2025-32 'removed'/'withdrew' it is NOT accurate as to "
                                'availability. Rev. Proc. 2024-40 §1 states the amounts are for '
                                "the Code 'as in effect on October 22, 2024' — a pre-OBBBA "
                                'snapshot, the same Code Florida adopted as of 1/1/2025. DO NOT '
                                'ENCODE $2,500,000 / $4,000,000 FOR FLORIDA TY2025. Every line of '
                                'F-1120 Sch. I (1–26) and Sch. II (1–13) was read: §179 appears '
                                'nowhere.'},
                      {'item': 'OBBBA (P.L. 119-21) as a whole',
                       'federal_treatment': 'OBBBA enacted 7/4/2025 and effective for TY2025 '
                                            'federally.',
                       'state_treatment': 'NOT ADOPTED for TY2025 — the conformity date (1/1/2025) '
                                          'precedes enactment, and the s. 220.03(3) '
                                          'automatic-adjustment mechanism does not reach it. '
                                          'TY2025 Line 1 must start from federal taxable income '
                                          'recomputed under the pre-OBBBA Code.',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'DOR states it in terms in a boxed notice at the head of TIP '
                                "25C01-01 (12/1/2025): 'The new law discussed below does not "
                                'address the One Big Beautiful Bill Act (Public Law 119-21), which '
                                "was enacted after the 2025 Florida legislative session ended.' "
                                "§12 CLOSED the s. 220.03(3) escape hatch: it operates only 'when "
                                "expressly authorized by law' — not self-executing — and no "
                                'Florida law expressly authorized adoption of OBBBA for TY2025. ⚠ '
                                '[UNVERIFIED] item 2 (still open): DOR has published NO mechanics '
                                'for the TY2025 pre-OBBBA recompute and the TY2025 instructions '
                                'are silent; expect a preparer-facing disclosure and a manual '
                                'override path rather than a fully automated Line 1 (§12 '
                                'confidence: MEDIUM on presentation, HIGH on the substantive '
                                'law).'},
                      {'item': 'Business meals deduction',
                       'federal_treatment': 'Enhanced meals deduction above the pre-P.L. 116-260 '
                                            '50% limit.',
                       'state_treatment': 'ADD-BACK of the excess over the pre-P.L. 116-260 50% '
                                          'limit (F-1120 Sch. I Line 23). Applies to taxable years '
                                          'beginning on or after 1/1/2021 and before 1/1/2026 — IN '
                                          'FORCE FOR TY2025, expiring for TY2026.',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'Window confirmed by §12 against F-1120N R. 01/26.'},
                      {'item': 'IRC §181 film / TV / live theatrical production',
                       'federal_treatment': 's. 181 current deduction for qualified production '
                                            'costs.',
                       'state_treatment': 'ADDITION of the s. 181 deduction (F-1120 Sch. I Line '
                                          '24) and SUBTRACTION of what would have been allowed '
                                          'without s. 181 (Sch. II Line 11). Same window as '
                                          'business meals — IN FORCE FOR TY2025, expiring for '
                                          'TY2026.',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'Window confirmed by §12 against F-1120N R. 01/26.'},
                      {'item': 'IRC §163(j) business interest limitation',
                       'federal_treatment': 'CARES Act raised the ATI limitation from 30% to 50% '
                                            'for TY2019–TY2020.',
                       'state_treatment': 'Computed AT THE FILER LEVEL. Florida did NOT follow the '
                                          'CARES Act 30%→50% increase for TY2019–TY2020; any '
                                          'resulting Florida addition is carried forward as '
                                          'disallowed business interest expense.',
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'F-1120N R. 01/26 pp. 5, 7, 9. Confirmed accurate as drafted by '
                                '§12.'},
                      {'item': 'Legacy 1981/1986 depreciation elections (Election A / Election B)',
                       'federal_treatment': 'Federal depreciation for assets placed in service '
                                            '1981–1986.',
                       'state_treatment': "Taxpayers who made 'Election A' (s. 220.03(5)(b)) or "
                                          "'Election B' (s. 220.03(5)(c)) still owe a depreciation "
                                          'adjustment for assets placed in service '
                                          '1/1/1981–12/31/1981 (A) or 1/1/1981–12/31/1986 (B), '
                                          'measured against the IRC of 1954 as in effect 1/1/1980. '
                                          "Reported under Sch. I Line 25 'Other additions.'",
                       'authority_source_code': 'FL_FS_220_03_CONFORMITY',
                       'notes': 'Vanishingly rare; the brief says do not build for it, but do not '
                                'assert it is gone.'}],
  'notes': "PTET: FLORIDA HAS NONE, and this is 'the rule says no,' not 'no rule found' — ch. 220, "
           'F.S. contains no elective or mandatory entity-level tax on partnerships or S '
           'corporations and no PTE election section; no form exists; owner-side treatment is '
           'none/not applicable (there is no Florida individual income tax against which an owner '
           'credit could apply). Florida must NEVER appear in a PTET election UI, a PTET credit '
           'allocation, or a K-1 PTET line. SCOPE: entity-only lane — no individual income tax, no '
           'fiduciary income tax return (charitable trusts file F-1120 for TY2025 only; excluded '
           "from TY2026). The software's hardest job in Florida is deciding WHETHER A RETURN "
           'EXISTS: an S corporation usually files nothing (F-1120 only if paying federal tax on '
           'Form 1120S Line 23c under §1374/§1375), and a partnership files an F-1065 information '
           'return only if a partner is itself subject to ch. 220 — do not generate a return by '
           'default. Corporate rate 5.5% (the automatic rate-adjustment mechanism was REPEALED for '
           'TYs beginning on/after 1/1/2022 — 4.458% and 3.535% are historical only), $50,000 '
           'exemption, three-factor apportionment 25 property / 25 payroll / 50 sales, NO '
           'throwback. ⚠ MID-CHANGE RISK: ch. 2026-137 (HB 7031, 2026) moves conformity to '
           '1/1/2026 for TY2026 forward, taking ss. 168(k), 174(a), 163(j), 274 and 179 as in '
           'effect 1/1/2025 (pre-OBBBA) and excluding ss. 168(n) and 174A entirely, with a pro '
           'forma federal return required — CONTEXT ONLY, DO NOT ENCODE AS TY2025. ⚠ NEW '
           '[UNVERIFIED] item 9 (opened on verification, BLOCKS FISCAL-YEAR SUPPORT): the ch. '
           '2026-137 retroactivity clause is DATE-based, not tax-year-based, so a FISCAL TY2025 '
           'straddling 1/1/2026 (e.g. FYE 6/30/2026) is not squarely addressed; DOR elsewhere '
           "frames the companion changes as applying 'for tax years beginning on or after January "
           "1, 2026', which if carried across would leave a FYE 6/30/2026 year on the 1/1/2025 "
           'Code. Confirm before building fiscal-year support. Other still-open items: 5 (official '
           'constitution text), 6 (DOR developer calendar / ATS — FTA SES access is the long '
           'pole), 7 (Rule 12C-1.015 throwback-equivalent), 8 (tiered partnership F-1065), 10 '
           '(F-1120 / F-1120A form-face details).'},
 {'jurisdiction_code': 'TX',
  'conformity_type': 'partial',
  'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
  'federal_reference_note': "Tex. Tax Code §171.0001(9) still defines 'Internal Revenue Code' as "
                            'the IRC of 1986 in effect for the federal tax year beginning on '
                            'January 1, 2007, not including any changes made by federal law after '
                            'that date (Acts 2006, 79th Leg., 3rd C.S., Ch. 1 (H.B. 3), §2, eff. '
                            'Jan. 1, 2008). But BEGINNING WITH THE 2026 FRANCHISE TAX REPORT (= '
                            'Delvio TY2025) the Comptroller reinterpreted its scope: a taxable '
                            'entity determines amounts taken from its federal tax return under the '
                            'federal tax law in effect for THAT federal tax year, UNLESS the Texas '
                            'statute or rule specifically references the IRC — where it does, the '
                            '2007 IRC still governs. This applies to all components of the '
                            'franchise tax. Controlling authority: STAR memo 202603002M (March 12, '
                            '2026), which updates and replaces STAR 202512012M (Dec. 19, 2025). '
                            'This was an administrative reinterpretation, NOT a repeal of '
                            '§171.0001(9).',
  'summary': 'TEXAS HAS NO INCOME TAX OF ANY KIND — no individual income tax (constitutionally '
             'prohibited by Tex. Const. art. VIII, §24-a), no corporate income tax, no PTET, no '
             'local income taxes, no composite or nonresident withholding. What it has instead is '
             "the FRANCHISE ('MARGIN') TAX under Tex. Tax Code Chapter 171: an entity-level tax on "
             'MARGIN, a gross-receipts-derived base with no relationship to federal taxable '
             "income. 'Conformity' in the ordinary sense does not exist here — Texas has only a "
             'DEFINITIONAL IRC tie used where Chapter 171 cites the Code, which is why the posture '
             'is recorded as PARTIAL rather than rolling/static/decoupled. TY2025 is the year '
             'Texas MOVED OFF THE 2007 IRC: federal return amounts are now determined under '
             'then-current federal law (so OBBBA bonus depreciation and §179 flow into COGS), '
             'except where the statute or rule expressly cites the IRC. There is also a ONE-TIME, '
             '2026-report-only net depreciation catch-up adjustment with a carryforward. Do not '
             "port last year's Texas logic.",
  'decoupled_items': [{'item': 'IRC conformity scope — the 2007-IRC departure (Tex. Tax Code '
                               '§171.0001(9))',
                       'federal_treatment': 'Current federal law, including OBBBA (P.L. 119-21, '
                                            '7/4/2025).',
                       'state_treatment': 'HYBRID. Beginning with the 2026 report, amounts taken '
                                          'from the federal return are determined under the '
                                          'federal tax law in effect for that federal tax year, '
                                          'UNLESS the Texas statute or rule specifically '
                                          'references the IRC — where it does, the 2007 IRC '
                                          'governs. Applies to all components of the franchise '
                                          'tax, including apportionment gross receipts. OBBBA is '
                                          'therefore adopted only INDIRECTLY, through '
                                          'federal-return line items and COGS depreciation, never '
                                          'as an income-tax conformity election; it has NO effect '
                                          'on rates, the threshold, the margin formula, or '
                                          'apportionment.',
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': '§12 CONFIRMED the departure verbatim from the controlling STAR '
                                'memo and corrected the citation: the draft cited STAR 202512012M, '
                                'which was COMPLETELY SUPERSEDED on 3/12/2026 by 202603002M. Cite '
                                "202603002M. The Comptroller's Dec. 1, 2025 news release states "
                                "the change 'follows a statutory review confirming that Texas "
                                'franchise tax law provides the flexibility to apply the current '
                                "internal revenue code (IRC) for depreciation calculations.'"},
                      {'item': 'IRC §168(k) bonus depreciation (inside COGS)',
                       'federal_treatment': 'OBBBA 100% bonus for qualifying property acquired and '
                                            'placed in service after 1/19/2025.',
                       'state_treatment': 'CONFORMS, MANDATORILY, VIA COGS — but only inside Cost '
                                          'of Goods Sold under Tex. Tax Code §171.1012(c)(6), and '
                                          'only for entities that qualify to use COGS at all. '
                                          'Texas margin has NO depreciation deduction as such. A '
                                          'taxable entity includes the depreciation reported on '
                                          'its federal return for each qualifying asset, and that '
                                          'amount may include federal bonus depreciation. NO '
                                          "OPT-OUT: 'A taxable entity generally must use the same "
                                          'methods it uses on its current federal return. Section '
                                          "171.1012(h).' ⚠ GATED: the controlling STAR memo limits "
                                          "this to assets 'placed in service on or after January "
                                          "19, 2025.'",
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': '⚠⚠ KEN JUDGEMENT CALL / [UNVERIFIED] #9 (NEW, opened by the '
                                'verification pass, LOAD-BEARING, STILL OPEN): THREE OFFICIAL '
                                'SOURCES STATE THREE DIFFERENT SCOPES — the STAR memo (202603002M, '
                                "and identically 202512012M) says 'placed in service on or after "
                                "January 19, 2025'; the Comptroller's Dec. 2025 news release says "
                                "'acquired after Jan. 19, 2025'; and adopted Rule 3.588 states the "
                                "rule with NO date qualifier. The brief's position is that the "
                                'memo governs, but this acquired-vs-placed-in-service ambiguity '
                                'MUST BE SETTLED BEFORE THE DEPRECIATION MODULE IS CODED. Do NOT '
                                "encode 'all federal bonus flows into COGS' without the gate. For "
                                '2025 report years and earlier, federal bonus was NOT allowed for '
                                'Texas COGS at all, because the Economic Stimulus Act of 2008 '
                                'became part of the IRC after Jan. 1, 2007.'},
                      {'item': 'IRC §179 expensing (inside COGS)',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'The FEDERAL §179 AMOUNT AS ACTUALLY CLAIMED flows '
                                          'through into COGS if otherwise qualified under '
                                          '§171.1012(c)(6). NO TEXAS-SPECIFIC §179 DOLLAR LIMIT OR '
                                          'PHASEOUT EXISTS for the 2026 report — the adopted '
                                          'amendment to 34 TAC §3.588 (adopted June 1, 2026, '
                                          'effective June 21, 2026; proposed text 51 TexReg 2237, '
                                          "Apr. 3, 2026) DELETES the rule's reference to 'Internal "
                                          'Revenue Code, §179 (Election to expense certain '
                                          "depreciable assets)', which was the sole source of the "
                                          'old $25,000 / $200,000 Texas cap.',
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': "✅ §12 RESOLVED ([UNVERIFIED] §10.2 closed). ENCODE 'federal "
                                "amount as claimed' — NOT a hardcoded Texas cap and NOT a literal "
                                "'unlimited'; it is constrained by the federal limit and by "
                                '§171.1012(c)(6) qualification. Matters for amended '
                                '2025-and-earlier reports: under the prior regime §179 was capped '
                                'at $25,000 with a $200,000 phase-out threshold under the 2007 '
                                'IRC. Caveat carried from §12: the adopted text of §3.588/§3.587 '
                                'was read only through the Texas Register adoption preamble, not '
                                'section-by-section — sufficient for the §179 conclusion (the '
                                'deletion is stated explicitly), not sufficient to rule out other '
                                'detail changes.'},
                      {'item': 'One-time net depreciation adjustment (2026 report only, with '
                               'carryforward)',
                       'federal_treatment': 'No federal analogue — this is a Texas transition '
                                            'mechanic.',
                       'state_treatment': 'A qualifying asset is one that (a) is associated with '
                                          'and necessary for the production of goods under '
                                          '§171.1012(c)(6), (b) was placed in service PRIOR to the '
                                          'accounting year begin date on the 2026 report, and (c) '
                                          'was NOT disposed of prior to that date. For each such '
                                          'asset, for each tax year it was in service through the '
                                          'accounting year end date on the 2025 report, compute '
                                          'federal depreciation claimed MINUS depreciation claimed '
                                          'for Texas franchise tax COGS; yearly amounts may be '
                                          "negative; sum them. 'The net depreciation adjustment "
                                          "cannot be less than zero.' Include the net amount in "
                                          'COGS on the 2026 report only to the extent it does not '
                                          "take margin below zero; 'Any unused net depreciation "
                                          'adjustment may be carried forward to consecutive '
                                          "reports until exhausted.' It is NOT limited to assets "
                                          'disposed of in the period, and CANNOT be applied by '
                                          "amending prior years ('The net depreciation adjustment "
                                          "is intended to be prospective'). If an ITC reduced the "
                                          "asset's federal basis, the REDUCED basis is used both "
                                          'for TX COGS depreciation and for this adjustment.',
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': 'ENGINEERING CONSEQUENCE (from the brief): a correct TX build '
                                'needs a per-asset, per-year history of (federal depreciation, '
                                "TX-COGS depreciation) going back to the asset's in-service date, "
                                'plus a carryforward balance that survives across report years. '
                                'This is the single largest data requirement in the Texas module '
                                "and it does not exist in any income-tax state's spec. §12 "
                                'confirmed the mechanic word-for-word in both Form 05-915 and the '
                                'memo, and noted that 202603002M added the clarification that the '
                                "adjustment applies 'regardless of whether those assets were "
                                "disposed of' in the accounting period."},
                      {'item': 'IRC §197 amortization',
                       'federal_treatment': 'Current-law §197 15-year amortization of intangibles.',
                       'state_treatment': "STAYS ON THE 2007 IRC — 'any recovery under Section 197 "
                                          "must be computed under the 2007 IRC', and 'A "
                                          'depreciation adjustment is not allowed for recovery '
                                          'claimed under Internal Revenue Code (IRC) Section 197 '
                                          "as those amounts are determined under the 2007 IRC.'",
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': 'IRC Conformity FAQ; Form 05-915 p. 20. Confirmed verbatim by '
                                '§12.'},
                      {'item': 'IRC §174 research & development',
                       'federal_treatment': 'Current-law §174 / §174A treatment of R&E '
                                            'expenditures.',
                       'state_treatment': 'STAYS ON THE 2007 IRC — §171.1012(c)(9) ties the '
                                          'deduction to the 2007 IRC; an entity may use EITHER '
                                          '2007-IRC §174 method for COGS regardless of its current '
                                          'federal method.',
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': 'IRC Conformity FAQ. Confirmed by §12.'},
                      {'item': 'IRC §78 and §§951–964 amounts (GILTI / FDII, OBBBA-renamed NCTI / '
                               'FDDEI)',
                       'federal_treatment': 'GILTI (§951A) inclusion and the §250 FDII deduction '
                                            'under current law.',
                       'state_treatment': 'The §78 and §§951–964 amounts under §171.1011 are tied '
                                          'to the 2007 IRC, which is why GILTI/FDII ARE INCLUDED '
                                          'IN TOTAL REVENUE AND MAY NOT BE SUBTRACTED — not as '
                                          'foreign dividends/royalties, not as §78/§§951-964 '
                                          'amounts, and not as Schedule C deductions.',
                       'authority_source_code': 'TX_STAR_202603002M_IRC_CONFORMITY',
                       'notes': 'This is a real TY2025 software rule for C-corp clients with '
                                'foreign income (four separate Q&As in the IRC Conformity FAQ). '
                                '§12 confirmed verbatim from the STAR memo: amounts under §78 and '
                                "§§951-964 'are determined under the 2007 IRC and do not include "
                                'the current IRC Section 951A global intangible low-taxed income '
                                "(GILTI) as GILTI was added to the IRC after January 1, 2007.'"}],
  'notes': '⚠ REPORT-YEAR MAPPING — READ FIRST. Texas does not label returns by tax year. A report '
           'is labeled by the REPORT YEAR (the calendar year the report is due) and is based on '
           'the accounting period ENDING IN THE PRIOR CALENDAR YEAR. So the Delvio TY2025 entity '
           "return is the TEXAS 2026 ANNUAL FRANCHISE TAX REPORT, DUE MAY 15, 2026. A '2025 Texas "
           "report' is TY2024 and is the WRONG source for this campaign. PTET: NONE, and Texas "
           'structurally cannot have a conventional one — there is no individual income tax to '
           'credit against (Tex. Const. art. VIII, §24-a, added by Prop. 4, approved 11/5/2019: '
           "'The legislature may not impose a tax on the net incomes of individuals, including an "
           "individual's share of partnership and unincorporated association income.'). No "
           'elective PTE tax provision was found in Ch. 171 and no PTET form appears on the '
           "Comptroller's 2026 forms list. Owner-side treatment: none — no credit, deduction, "
           'exclusion, or addback; nothing flows to a K-1 as a state tax credit. ⚠ LEAVE ANY PTET '
           'RATE/BASE/CREDIT FIELD NULL, NOT ZERO. SCOPE: entity-only lane. No individual return, '
           'no starting point, no rate structure, no part-year/nonresident schedule, no local '
           'income tax, no composite return, no nonresident withholding. Inverse of every '
           'income-tax state: a Texas RESIDENT INDIVIDUAL generates no Texas filing, but a Texas '
           'ENTITY generates a filing (or at minimum a PIR/OIR) regardless of whether it owes tax. '
           'For the 2026 report the NO-TAX-DUE THRESHOLD is $2,650,000 of annualized total '
           'revenue; an entity at or below it owes no tax and FILES NO FRANCHISE TAX REPORT AT ALL '
           '— the No Tax Due Report was abolished and does not exist for 2026 — but still owes a '
           'Public Information Report (05-102) or Ownership Information Report (05-167). For a '
           'large share of Texas entity clients the correct product output is AN INFORMATION '
           'REPORT ONLY, not a tax return. ⚠ KEN JUDGEMENT CALL PENDING: [UNVERIFIED] #9 — the '
           'bonus depreciation acquired-vs-placed-in-service gate (memo, news release and adopted '
           'rule state three different scopes) must be settled before the depreciation module is '
           'coded. Other still-open items: #6 developer-program calendar (no published timeline; '
           'Ken-only action — email XMLBusiness@cpa.texas.gov; lead-time-bearing) and #8 Rule '
           '3.581 operative trust mapping (low urgency, fiduciary is on demand).'},
 {'jurisdiction_code': 'TN',
  'conformity_type': 'rolling',
  'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
  'federal_reference_note': 'ROLLING conformity — no conformity date. Tenn. Code Ann. § 67-4-2004 '
                            '(definitions subdivision): "\'Internal Revenue Code\' means title 26 '
                            'of the United States Code as effective during the year in which net '
                            'earnings are determined under this part." The DOR describes this '
                            "repeatedly as 'the state's general rolling conformity with the "
                            "Internal Revenue Code, as amended' (F&E Manual, Dec 2025, OBBBA "
                            'chapter, pp. 268–271). OBBBA (P.L. 119-21, 7/4/2025) is therefore '
                            'PARTIALLY ADOPTED for TY2025: rolling conformity pulls it in by '
                            'default, and Tennessee then overrides it wherever a statutory '
                            'decoupling names a specific pre-OBBBA version of an IRC section.',
  'summary': 'Tennessee is an ENTITY-ONLY state with ROLLING IRC conformity that is nevertheless '
             'STATUTORILY FROZEN AT THE TCJA VERSION OF §168(k). There is no individual income tax '
             '(the Hall income tax was repealed for tax periods beginning on or after 1/1/2021), '
             'no fiduciary income tax, and no PTET. The whole lane is the franchise & excise tax '
             'on Form FAE170 — one return carrying two separately-computed taxes: a 6.5% excise '
             'tax on net earnings and a 0.25% franchise tax on net worth (minimum $100). For '
             'TY2025 the two OBBBA depreciation provisions split in OPPOSITE directions: Tennessee '
             'conforms to OBBBA §179 at the full $2,500,000 / $4,000,000 while allowing only 40% '
             'bonus and ZERO §168(n). Bonus itself runs two regimes split on ACQUISITION date '
             '(on/before 12/31/2022 vs. on/after 1/1/2023).',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': 'OBBBA 100% bonus, permanent, for property acquired '
                                            'and placed in service after 1/19/2025.',
                       'state_treatment': 'DOES NOT CONFORM to OBBBA — Tennessee remains coupled '
                                          'to the TCJA VERSION of §168(k), permanently frozen '
                                          '(Tenn. Code Ann. § 67-4-2006(a)(12); Public Chapter 377 '
                                          '(2023), Tennessee Works Tax Act), so the applicable '
                                          'percentage is 40% for 2025, 20% for 2026, 0% for 2027 '
                                          'and after. TWO REGIMES SPLIT ON ACQUISITION DATE: (1) '
                                          'assets PURCHASED ON OR BEFORE 12/31/2022 — bonus is '
                                          'FULLY DISALLOWED for excise tax purposes; federal bonus '
                                          'is added back on Schedule J Line 3, the TN depreciation '
                                          'actually permitted is deducted on Schedule J Line 16, '
                                          'and the resulting federal/state basis difference '
                                          'produces an excess gain/loss adjustment on disposition '
                                          'on Schedule J Line 17 (this regime does not expire); '
                                          '(2) assets PURCHASED ON OR AFTER 1/1/2023 — TN conforms '
                                          'to the TCJA §168(k) percentages, and where federal '
                                          'bonus under OBBBA exceeds the TCJA-allowable amount '
                                          "'the excess bonus depreciation cannot be deducted for "
                                          "excise tax purposes; this portion of the property's "
                                          'basis must be depreciated for Tennessee excise tax '
                                          'purposes in accordance with the federal MACRS '
                                          "depreciation provisions', with addback and deduction "
                                          'adjustments on Schedule J. A TY2025 asset acquired '
                                          'after 1/19/2025 therefore generates a 60-POINT ADD-BACK '
                                          'plus an ongoing MACRS recovery of the differential — '
                                          'the software must carry a separate TN basis.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': '⚠⚠ KEN JUDGEMENT CALL #1 — THE DOR CONTRADICTS ITSELF ON THE '
                                'KEYING (§10 item 8, opened by the verification pass). F&E Manual '
                                "p. 267 (the OBBBA chapter) says verbatim that 'the 40%, 20%, and "
                                '0% applicable percentages will apply for excise tax purposes to '
                                'qualified property PLACED IN SERVICE in 2025, 2026, and 2027 and '
                                "after', but the phase-down table at manual p. 225 is captioned "
                                "'Asset ACQUIRED Between:' (1/1/2025–12/31/2025 = 40%). The two "
                                'give DIFFERENT ANSWERS for an asset acquired in 2024 and placed '
                                "in service in 2025. The brief's instruction: build to the p. 267 "
                                'placed-in-service statement (later text, OBBBA-specific, and '
                                'consistent with TCJA §168(k)(6)) BUT FLAG FOR KEN AND CONFIRM '
                                'WITH THE DOR BEFORE THE SPEC IS SEALED. Per the '
                                'Authoritative-Source Rule this is a source contradiction, not a '
                                'gap to guess at. ⚠⚠ KEN JUDGEMENT CALL #2 — WHICH SCHEDULE J '
                                'LINES CARRY THE POST-2022 OBBBA DIFFERENTIAL IS A DOR GAP (§10 '
                                'item 6, new). The TY2025 instructions scope Schedule J Lines 3, '
                                "16 and 17 textually to 'assets purchased on or before December "
                                "31, 2022', and manual p. 223 still says taxpayers should NOT make "
                                "Line 3/16/17 adjustments for post-2022 assets 'unless the federal "
                                'bonus depreciation provisions are amended by subsequent enactment '
                                "of federal legislation' — OBBBA IS that subsequent enactment, and "
                                "the OBBBA chapter directs 'appropriate bonus depreciation addback "
                                "and deduction adjustments on Schedule J' without naming a line. "
                                'The DOR did not update the wording on the TY2025 form. WORKING '
                                'ASSUMPTION: Lines 3/16/17 carry BOTH regimes. Confirm with the '
                                'DOR before authoring.'},
                      {'item': 'IRC §168(n) qualified production property',
                       'federal_treatment': 'OBBBA 100% election for qualified production '
                                            'property.',
                       'state_treatment': "DECOUPLED — NO BONUS AT ALL. 'Because IRC § 168(n) does "
                                          'not exist in the TCJA version of IRC § 168, this OBBBA '
                                          'provision is not applicable for Tennessee excise tax '
                                          "purposes' — depreciate as MACRS nonresidential real "
                                          'property.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'Tenn. Code Ann. § 67-4-2006(a)(12); F&E Manual p. 268. Confirmed '
                                'verbatim by §12.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA), both '
                                            'inflation-indexed.',
                       'state_treatment': 'CONFORMS at the full OBBBA figures — $2,500,000 limit / '
                                          '$4,000,000 phaseout, indexed, for tax years beginning '
                                          "after 12/31/2024. 'Tennessee conforms to IRC § 179 via "
                                          "the state's general rolling conformity with the "
                                          "Internal Revenue Code, as amended.' NO state-specific "
                                          '§179 limit and NO add-back.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'F&E Manual p. 270; confirmed verbatim by §12. ⚠ This is the half '
                                'of the OBBBA depreciation split that goes the OTHER way from '
                                'bonus — do not assume a state that freezes §168(k) also freezes '
                                '§179. Two TN-specific §179 mechanics that are easy to miss: (1) '
                                'on Schedules J1 (partnerships) and J3 (S corps), gain or loss on '
                                'disposition of property for which a §179 deduction was previously '
                                'passed through — reported federally on Form 1065 Sch. K box 20 '
                                'code L or Form 1120S Sch. K box 17 code K rather than on Form '
                                '4797 — must be computed PRO FORMA AT THE ENTITY LEVEL, '
                                'disregarding any partner-/shareholder-level §179 limits (Sch. J1 '
                                'lines 2 and 5; Sch. J3 lines 2 and 4); (2) on Schedule J1 Line 6 '
                                '/ J2 Line 8 the self-employment-earnings deduction is taken NET '
                                'of pass-through expenses deducted elsewhere on the return, such '
                                'as IRC §179 expense.'},
                      {'item': 'IRC §163(j) business interest limitation',
                       'federal_treatment': 'TCJA/current-law 30%-of-ATI limitation on business '
                                            'interest.',
                       'state_treatment': 'DECOUPLED — Tennessee conforms to the PRE-TCJA §163(j); '
                                          'most taxpayers fully expense business interest.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'Tenn. Code Ann. § 67-4-2006(a)(10).'},
                      {'item': 'IRC §951A net CFC tested income (ex-GILTI)',
                       'federal_treatment': 'GILTI/NCTI inclusion with the related §250 deduction.',
                       'state_treatment': 'Included in the starting point, then ONLY 5% is taxed; '
                                          'the related §250 deduction is NOT allowed. The OBBBA '
                                          'changes to this provision apply for tax years beginning '
                                          'after 12/31/2025 — i.e. NOT TY2025.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'Tenn. Code Ann. §§ 67-4-2006(b)(1)(P), (b)(2)(T).'},
                      {'item': 'IRC §174 / new §174A research & development',
                       'federal_treatment': 'OBBBA §174 / §174A R&E treatment.',
                       'state_treatment': 'CONFORMS — and Tennessee already allowed full expensing '
                                          'since 1/1/2022. Foreign R&D still requires a Schedule J '
                                          'addback/deduction to reach full expensing.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'Tenn. Code Ann. § 67-4-2006(a)(11).'},
                      {'item': 'IRC §250 FDII / foreign-derived deduction (33.34%)',
                       'federal_treatment': 'OBBBA §250 foreign-derived deduction at 33.34%.',
                       'state_treatment': 'CONFORMS via rolling conformity — but effective for tax '
                                          'years beginning after 12/31/2025, i.e. NOT TY2025.',
                       'authority_source_code': 'TN_TCA_67_4_2004_IRC_DEF',
                       'notes': 'F&E Manual p. 271.'}],
  'notes': "PTET: NONE, and Tennessee structurally cannot use one — 'the rule says no,' not 'found "
           "nothing.' There is no owner-level Tennessee income tax to shift, the 563-page December "
           "2025 F&E Tax Manual contains ZERO occurrences of 'pass-through entity tax' or 'PTET', "
           "and the DOR's complete F&E forms page lists no PTET election form or return. "
           'Owner-side treatment: none — no credit, deduction, exclusion, or K-1 pass-through of '
           'TN tax. Instead Tennessee reaches pass-through income by TAXING THE ENTITY DIRECTLY. ⚠ '
           'THE PORTED-SPEC BREAKER: Tennessee taxes federal pass-throughs at the ENTITY level. '
           'LLCs, LPs, LLPs, S corps, business trusts, and even a single-member LLC owned by an '
           'individual are all FAE170 taxpayers in their own right — the test is whether the '
           'entity confers LIMITED LIABILITY on its owners, not how it is classified federally. '
           'Disregarded entities are NOT disregarded for F&E purposes, with two exceptions: an '
           'SMLLC whose single member is a corporation (Tenn. Code Ann. §§ 67-4-2007(d), '
           '67-4-2106(c)) and (per §12) an SMLLC wholly owned by a pension trust. An SMLLC owned '
           'by an individual computes net earnings on Schedule J2 by pulling Form 1040 Schedules '
           'C, D, E, F and Form 4797 amounts. SCOPE: no individual income tax — the Hall income '
           'tax was repealed for tax periods beginning on or after 1/1/2021 (final applicable tax '
           'year 2020); no Form INC250 for TY2025, no wage withholding, no individual estimated '
           'payments. No fiduciary income tax: estates and trusts filing federal Form 1041 are not '
           'subject to F&E, EXCEPT business trusts, which are. ⚠ TWO KEN JUDGEMENT CALLS ARE '
           "PENDING ON DEPRECIATION (see the §168(k) item): the DOR's own manual contradicts "
           'itself on whether the bonus applicable percentage is keyed to ACQUISITION (p. 225) or '
           'PLACED IN SERVICE (p. 267), and the DOR never said which Schedule J lines carry the '
           'post-2022 OBBBA differential. Both change numbers on returns and must be walked at '
           'Gate 1 rather than resolved by inference. Other open items: the software-developer '
           'certification calendar remains unpublished (lead-time-bearing); short 2025 periods '
           '(apportionment formula and Schedule PL availability turn on period_end < 2025-12-31, '
           'but the TY2025 form supports neither cleanly); and Tenn. Code Ann. § 67-4-2004 is '
           'still reachable only through a secondary reprint (FindLaw) — subdivision numbers '
           '((19), (27), (32), (35), (36)) are read rather than inferred and are corroborated by '
           "the DOR manual's own footnotes, and no figure depends on a subdivision number. The "
           'Schedule G minimum-property-measure OPT-IN SURVIVES (Tenn. Code Ann. § 67-4-2123, PC '
           '950 (2024)) and cannot be dropped from the spec; its line-level guidance depends on '
           'the DECEMBER 2023 manual, because the December 2025 manual deliberately deleted it.'},
 {'jurisdiction_code': 'VA',
  'conformity_type': 'static',
  'authority_source_code': 'VA_CODE_58_1_301',
  'federal_reference_note': 'IRC fixed date of December 31, 2025 — Va. Code § 58.1-301 ("as they '
                            'existed on December 31, 2025"), as amended by the thirteenth '
                            'enactment clause of the 2026 Amendments to the 2025 Appropriation Act '
                            '(HOUSE BILL 29, Chapter 7 of the 2026 Acts of Assembly), effective '
                            'February 20, 2026. Set by the BUDGET bill, not standalone conformity '
                            'legislation. Because the date post-dates OBBBA (P.L. 119-21, signed '
                            '7/4/2025), OBBBA IS IN the Virginia base for TY2025, except for three '
                            'carve-outs. Narrow rolling carve-out: Virginia continues to conform '
                            'automatically to federal amendments that extend the expiration date '
                            'of a provision Virginia conforms to or has conformed to (Tax Bulletin '
                            '26-1).',
  'summary': 'Virginia is a STATIC / fixed-date conformity state for TY2025, at December 31, 2025 '
             '— and it got there late and by an unusual route (the 2026 budget bill, effective '
             '02/20/2026, mid-filing-season and retroactive to TY2025). The fixed date PULLS OBBBA '
             'IN, but Virginia then carved out three new business deconformities — §168(n) '
             'qualified production property, §174A domestic R&E expensing (INCLUDING the '
             'retroactive and catch-up provisions), and the §179 expensing-limit increases — on '
             'top of eight long-standing exceptions, bonus depreciation chief among them. All '
             'three new deconformities resolve as TIMING differences: a fixed date conformity '
             'ADDITION now and a fixed date conformity SUBTRACTION later, which makes a multi-year '
             'Virginia shadow depreciation/amortization book mandatory. Virginia also conforms to '
             'the OBBBA §163(j) change but CUT the Virginia subtraction for federally disallowed '
             'business interest from 50% to 20%, for TY2025 and thereafter.',
  'decoupled_items': [{'item': 'IRC §168(k)/(l)/(m)/(n), 1400L, 1400N bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent); §168(n) '
                                            'immediate expensing of qualified production property.',
                       'state_treatment': 'NOT adopted — Va. Code § 58.1-301 B exception 1. '
                                          'Depreciation must be recomputed for Virginia purposes '
                                          'as if the assets had not received bonus, for any year '
                                          'from 2001 through 2025; where 2025 Virginia '
                                          'depreciation is less than 2025 federal depreciation the '
                                          'difference is an ADDITION (corporate: Schedule 500ADJ '
                                          'Section A Line 1; individual: Schedule ADJ Line 2a A), '
                                          'with corresponding Section B SUBTRACTIONS in later '
                                          'years as Virginia depreciation exceeds federal. A '
                                          'separate conformity adjustment is required on '
                                          'disposition of a bonus asset (Schedule 500ADJ Section A '
                                          "Line 2). Timing difference recovered over the asset's "
                                          'life, not a permanent disallowance.',
                       'authority_source_code': 'VA_CODE_58_1_301',
                       'notes': '§168(n) — new under OBBBA — was folded into the SAME statutory '
                                'exception 1 as §§168(k)/(l)/(m). §12.2 confirmed § 58.1-301 B '
                                'enumerates the other two new carve-outs by OBBBA section number '
                                '(§ 70302 → R&E; § 70306 → expensing limits).'},
                      {'item': 'IRC §179 expensing limits (OBBBA increases)',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'DECONFORMED from the increases — NEW for TY2025, the '
                                          'first time in recent history. TB 26-1: taxpayers "must '
                                          'maintain separate Virginia records and calculate '
                                          'depreciation, amortization, carryforwards, and '
                                          'adjustments as if the 2025 H.R. 1 changes had not been '
                                          'enacted." Recovered as a fixed date conformity ADDITION '
                                          'now / SUBTRACTION later — a timing difference, not a '
                                          'permanent disallowance.',
                       'authority_source_code': 'VA_TB_26_1',
                       'notes': '⚠ [UNVERIFIED — dollar figures; brief §10 item 1, still OPEN '
                                'after the adversarial pass, confirmed open BY EXHAUSTION]. '
                                'VIRGINIA PUBLISHES NO §179 DOLLAR LIMIT OR PHASE-OUT THRESHOLD OF '
                                'ITS OWN. The $1,250,000 limit / $3,130,000 phase-out / $31,300 '
                                'SUV cap are DERIVED from Rev. Proc. 2024-40 § 3.25 (pre-OBBBA '
                                "indexed 2025 federal amounts) by applying the DOR's own 'as if "
                                "H.R. 1 had not been enacted' instruction — the arithmetic is "
                                'verified verbatim but the ATTRIBUTION TO VIRGINIA IS AN '
                                'INFERENCE, not a Virginia-published constant. Encode as a '
                                'configurable/derived value with a Virginia-source TODO. Do NOT '
                                'encode the federal OBBBA $2,500,000 / $4,000,000 figures for '
                                'Virginia.'},
                      {'item': 'IRC §174A domestic research & experimental expensing',
                       'federal_treatment': 'OBBBA immediate expensing of domestic R&E, INCLUDING '
                                            'the retroactive and catch-up provisions.',
                       'state_treatment': 'DECONFORMED, including the retroactive and catch-up '
                                          'provisions. Same recovery mechanic: separate Virginia '
                                          'records computed as if H.R. 1 had not been enacted, '
                                          'fixed date conformity addition now / subtraction later.',
                       'authority_source_code': 'VA_TB_26_1',
                       'notes': 'Brief §9 calls the retroactive/catch-up dimension the nastiest '
                                'piece — federal catch-up deductions have no Virginia counterpart. '
                                'Codified in § 58.1-301 B by OBBBA section number (§ 70302).'},
                      {'item': 'IRC §163(j) business interest limitation — Virginia subtraction '
                               'rate',
                       'federal_treatment': 'OBBBA change to the federal business interest '
                                            'limitation.',
                       'state_treatment': 'Virginia CONFORMS to the OBBBA §163(j) change itself, '
                                          'but the Virginia SUBTRACTION for federally disallowed '
                                          'business interest is REDUCED FROM 50% TO 20% for '
                                          'Taxable Year 2025 and thereafter.',
                       'authority_source_code': 'VA_TB_26_1',
                       'notes': '⚠ Mid-season retroactive rate change — enacted February 2026 but '
                                'effective FOR TY2025. TB 26-1 p.2 and 2025 Form 500 instructions '
                                'p.1; §12.2 re-verified verbatim in two FINAL post-legislation '
                                'sources. Amended-return hazard: TB 26-1 directs taxpayers who '
                                'already filed to consider amending.'},
                      {'item': 'Federal overall limitation on itemized deductions (individual)',
                       'federal_treatment': 'OBBBA replacement of the federal overall limitation '
                                            'on itemized deductions; temporarily higher SALT cap.',
                       'state_treatment': 'NOT adopted — Virginia CONTINUES TO APPLY THE PEASE '
                                          'LIMITATION. Virginia generally applies NO SALT cap when '
                                          'computing Virginia itemized deductions; however a '
                                          "taxpayer subject to Virginia's Pease limitation must "
                                          'apply the SALT cap applicable for the year (including '
                                          "OBBBA's higher temporary cap) WHEN CALCULATING THAT "
                                          'LIMITATION.',
                       'authority_source_code': 'VA_TB_26_1',
                       'notes': 'TB 26-1 p.3; also standing exception 5 of the eight long-standing '
                                'exceptions. Individual lane only.'}],
  'notes': 'PTET: Form 502PTET, 5.75% flat, ELECTIVE and made ANNUALLY (by estimated payment, '
           'extension payment, or filing 502PTET by the extended due date); once filed the '
           'election is binding for the year AND binding on all eligible owners (no opt-out); '
           'owner-side REFUNDABLE CREDIT for individual/estate/trust DIRECT owners only; filed '
           'INSTEAD of Form 502; permanently extended by HB 29 Ch. 7 (2026) — two sunsets repealed '
           '(election/credits 1/1/2027, out-of-state PTET credit 1/1/2026). An electing PTE STILL '
           'WITHHOLDS for nonresident CORPORATE owners on the 502PTET itself (Page 2 Section II '
           'Line 7(b), added to the 5.75% tax) — the PTET module carries a withholding leg. No '
           'retroactive-election window for TY2025. ⚠ MID-CHANGE RISK: the TY2025 conformity '
           'legislation was enacted 02/20/2026, MID-FILING SEASON, retroactively changing the '
           '§163(j) subtraction and adding three deconformities for TY2025 — TY2025 Virginia '
           'support must handle amended returns. ⚠ TWO SPEC-BLOCKING GAPS remain open (brief '
           "§12.5): Virginia's own §179 dollar figure is UNPUBLISHED, and the specific TY2025 form "
           'line/worksheet for the H.R. 1 conformity addition/subtraction is unnamed (existing '
           'Schedule 500ADJ Lines 1–2 and Schedule ADJ Line 2a are written for BONUS DEPRECIATION '
           'ONLY). ⚠ The TY2025 Form 502PTET package on the DOR site is provably PRE-amendment '
           "(ModDate 2025-12-18) and its 'before January 1, 2027' sunset language is DEAD TEXT — "
           'everything else in it is live. Out of scope for this row but noted by the brief: '
           'general corporations use THREE-FACTOR apportionment with a double-weighted sales '
           'factor (÷4) for TY2025 — NOT single sales factor — and non-TPP sales are COST OF '
           'PERFORMANCE, not market-sourced; commentary asserting otherwise is wrong (§12.3, '
           'confirmed three independent ways).'},
 {'jurisdiction_code': 'CO',
  'conformity_type': 'rolling',
  'authority_source_code': 'CO_CRS_39_22_103',
  'federal_reference_note': 'ROLLING conformity — NO conformity date exists to encode. § '
                            '39-22-103(5.3), C.R.S.: "\'Internal revenue code\' means the '
                            "provisions of the federal 'Internal Revenue Code of 1986', as "
                            'amended, and other provisions of the laws of the United States '
                            'relating to federal income taxes, as the same may become effective at '
                            'any time or from time to time, for the taxable year." OBBBA (P.L. '
                            '119-21) therefore flows into Colorado AUTOMATICALLY for TY2025 except '
                            'where the legislature bolted on a specific add-back.',
  'summary': 'Colorado is a ROLLING-conformity, FLAT-RATE, FEDERAL-TAXABLE-INCOME state: every '
             'module (individual, PTE, C-corp, fiduciary) starts at federal TAXABLE income — DR '
             '0104 line 1 takes Form 1040 line 15, not federal AGI — and is taxed at 4.4% for '
             'TY2025. OBBBA is IN. COLORADO HAS NO DEPRECIATION MODIFICATION OF ANY KIND: §168(k) '
             'bonus and §179 both flow straight through at the federal amount, with no add-back, '
             'no state dollar limit, no recovery schedule and no separate state basis. What '
             'Colorado does have instead is an add-back layer on high-income individuals — a full '
             '§199A QBI add-back above AGI $500,000/$1,000,000 and a federal '
             'itemized-OR-standard-deduction add-back capped at $12,000/$16,000 above AGI $300,000 '
             '— plus a SALT Parity Act election that forces a full QBI add-back on EVERY owner '
             'regardless of income.',
  'decoupled_items': [{'item': 'IRC §199A qualified business income deduction',
                       'federal_treatment': '20% QBI deduction, allowed in arriving at federal '
                                            'taxable income.',
                       'state_treatment': 'ADD-BACK on DR 0104 line 3 where federal AGI exceeds '
                                          '$500,000 ($1,000,000 filing jointly) — the ENTIRE '
                                          'deduction, regardless of how far over the threshold. '
                                          'EXCEPTION: does not apply to a taxpayer required to '
                                          'file a federal Schedule F. SEPARATELY: a full add-back '
                                          'is required REGARDLESS OF AGI, and is NOT limited to '
                                          'the QBI attributable to the electing entity, if the '
                                          'taxpayer is a partner or shareholder of an entity that '
                                          'made a SALT Parity Act election.',
                       'authority_source_code': 'CO_2025_INDIV_TAX_GUIDE',
                       'notes': 'Made PERMANENT by HB 25B-1001 (2025 First Extraordinary Session; '
                                'approved and effective 8/28/2025), which "continues indefinitely" '
                                'a requirement that would otherwise have ended for income tax '
                                'years commencing on or after 1/1/2026 — one of the two Colorado '
                                'OBBBA-response bills. Individual lane; thresholds re-verified '
                                'verbatim in §12.'},
                      {'item': 'Federal itemized OR standard deduction (individual)',
                       'federal_treatment': 'Federal itemized deductions, or the federal standard '
                                            'deduction.',
                       'state_treatment': 'ADD-BACK on DR 0104 line 4 where federal AGI exceeds '
                                          '$300,000: add back the excess of the federal deduction '
                                          'over $12,000 (single / MFS / head of household) or '
                                          '$16,000 (MFJ). Applies whether the taxpayer ITEMIZED OR '
                                          'TOOK THE STANDARD DEDUCTION. The add-back is REDUCED BY '
                                          'the state income tax already added back on DR 0104 line '
                                          '2, but is NOT reduced by the portion of that line-2 '
                                          "add-back attributable to the taxpayer's share of state "
                                          'income tax deducted by a partnership or S corporation.',
                       'authority_source_code': 'CO_2025_INDIV_TAX_GUIDE',
                       'notes': '⚠ ONE-YEAR VALUE. The $12,000/$16,000 limit DROPS TO '
                                "$1,000/$2,000 for tax years 2026 and later (guide's own table: "
                                "'2023–2025 $12,000 / $16,000 · 2026 and later $1,000 / $2,000'). "
                                'Must be tax-year-keyed. Individual lane.'},
                      {'item': 'OBBBA overtime compensation deduction',
                       'federal_treatment': 'OBBBA deduction for overtime compensation.',
                       'state_treatment': 'NO ADD-BACK FOR TY2025 — the federal deduction flows '
                                          'through to Colorado taxable income unchanged. CDOR '
                                          'Individual Income Tax Guide (Rev. Jan 2026), Part 3: '
                                          '"For tax years 2026 and later, an individual who claims '
                                          'a deduction for overtime compensation on their federal '
                                          'income tax return must add back the amount of the '
                                          'deduction on their Colorado return."',
                       'authority_source_code': 'CO_2025_INDIV_TAX_GUIDE',
                       'notes': 'Recorded as a TY2026 divergence trigger, NOT a TY2025 '
                                'modification. Companion finding: the OBBBA qualified-TIPS '
                                'deduction gets NO add-back at all — "No addback is required on '
                                "the taxpayer's Colorado return for any deduction claimed on their "
                                'federal return for qualified tips" — a rule-says-no, not a '
                                'not-found.'}],
  'notes': '⚠ THE DEPRECIATION NEGATIVE IS AFFIRMATIVELY VERIFIED, NOT MERELY UNFOUND. '
           '`decoupled_items` contains NO depreciation entry because Colorado HAS no depreciation '
           "modification — this is a 'rule says no'. The §12 adversarial pass attacked it from "
           "five directions and it did not move: CRS 2024 Title 39 full text — 'depreciat*' 21 "
           "hits, ZERO in the Article 22 income-tax modification provisions; 'section 179' EXACTLY "
           "2 hits, both inside credit 'qualifying investment' definitions; '168(k)' / 'section "
           "168' / 'bonus depreciation' ZERO hits; the Corporate Income Tax Guide Part 4 "
           '(additions) and Part 5 (subtractions) and the Individual Income Tax Guide Part 3 read '
           "in full, line by line, with no depreciation item in any of them; 'depreciat*' zero "
           'hits in Book 104, DR 0112 and both guides; and both 2025 extraordinary-session bills '
           '(HB 25B-1001, HB 25B-1002) read, neither touching depreciation. So §168(k) CONFORMS '
           "(100% OBBBA bonus allowed in full — do NOT port Georgia's add-back logic), §179 "
           'CONFORMS at the federal limit with NO Colorado dollar limit or phaseout and no '
           'pre-OBBBA freeze, and there are NO recovery mechanics because there is nothing to '
           'recover. Two qualifications recorded by the brief, neither a modification: DR 0106 '
           'line 2 aggregates gain/loss on disposition of property for which a §179 deduction was '
           'passed through to partners/shareholders (a starting-point rule — a spec omitting it '
           'UNDERSTATES DR 0106 line 2), and a pre-1965 higher-Colorado-basis gain subtraction '
           'exists in Corporate Guide Part 5 (practically dead; encode as an edge case, NOT as '
           'authority for a modern depreciation basis split). PTET: SALT Parity Act (§ 39-22-340 '
           'et seq., C.R.S.), ELECTIVE, ANNUAL but IRREVOCABLE and binding on all owners, 4.4% '
           '(statute cross-references the CORPORATE rate § 39-22-301, not the individual rate — a '
           'trap in any year TABOR moves one and not the other), owner-side REFUNDABLE CREDIT, '
           'elected on DR 0106 box I / DR 1705 / DR 0106EP; guaranteed payments and '
           'negative-income owners excluded from the base; a C-corp partner unitary with the '
           'partnership is excluded entirely; retroactive-election window CLOSED (ran '
           '9/1/2023–6/30/2024 for TY2018–2021); tiered-partner elections are INDEPENDENT — do not '
           'propagate an election up or down the tier chain. The election is statutorily gated on '
           'a federal §164 SALT limitation existing — encode as a live check, not a constant. ⚠ '
           'TY2026 RE-VERIFICATION TRIGGERS: itemized/standard cap collapses to $1,000/$2,000; the '
           'overtime add-back begins; the §250 FDDEI add-back and the HB 25B-1002 tax-haven '
           'expansion both first apply TY2026 (their 8/28/2025 EFFECTIVE DATE is not their first '
           'applicable tax year); and the LCS forecast projects rates of 4.33% (TY2027) / 4.29% '
           '(TY2028), so the rate must be tax-year-keyed. ⚠ STILL OPEN ([UNV-2], MEDIUM '
           'confidence): how rolling conformity treats RETROACTIVELY EFFECTIVE federal amendments. '
           "CDOR's Rule 39-22-103(5.3) now shows as [Repealed]; the CARES-Act guidance is 404; "
           'Anschutz (Colo. App. 2022COA132) is known only from secondary reporting. No CDOR '
           "guidance on OBBBA's retroactive small-business §174A R&D election was found. MUST be "
           'resolved before the C-corp and PTE specs are authored.'},
 {'jurisdiction_code': 'OH',
  'conformity_type': 'static',
  'authority_source_code': 'OH_RC_5701_11',
  'federal_reference_note': 'STATIC (fixed date), refreshed by annual conformity legislation, with '
                            'a taxpayer election covering the gap period — R.C. 5701.11. '
                            'Conformity date for TY2025 is MARCH 5, 2026, set by Am. Sub. S.B. 9 '
                            'of the 136th General Assembly (signed 3/5/2026); the immediately '
                            'prior conformity date was March 7, 2025. Because 3/5/2026 post-dates '
                            'OBBBA (7/4/2025), OBBBA APPLIES for Ohio TY2025 — ODT states this '
                            'directly on its conformity page: "This bill officially puts Ohio into '
                            'conformity for tax year 2025 (filed in 2026). ... This includes '
                            'conformity with the tax changes contained in the One Big Beautiful '
                            'Bill Act (OBBBA) that impact Ohio taxation." R.C. 5701.11(B)(1) lets '
                            'a taxpayer irrevocably elect the prior-IRC version for years ending '
                            'after 3/7/2025 and before the current effective date, but there is no '
                            'divergence to elect away from since OBBBA was already federal law for '
                            'TY2025.',
  'summary': 'Ohio is a STATIC / fixed-date conformity state at March 5, 2026 (S.B. 9), so OBBBA '
             'is IN for TY2025. Ohio does NOT conform to §168(k) bonus depreciation and also claws '
             'back §179 above a 12/31/2002 baseline of $25,000, through an ADD-BACK NOW / RECOVER '
             'IN EQUAL INCREMENTS LATER regime — not a different depreciation table and not a '
             'different §179 dollar limit — requiring multi-year state-basis tracking. Ohio has NO '
             'conventional CORPORATE INCOME TAX: C corporations are subject to the Commercial '
             'Activity Tax, a gross-receipts tax with a $6,000,000 exclusion for TY2025 and no '
             'annual minimum tax since 2024, so conformity is irrelevant to the C-corp lane. Ohio '
             'likewise has no general partnership or S-corp income tax return — the PTE forms (IT '
             '1140 / IT 4708 / IT 4738) are conditional and largely elective.',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent).',
                       'state_treatment': 'NOT adopted — add back a FRACTION of the §168(k) '
                                          'deduction on Ohio Schedule of Adjustments line 9 (R.C. '
                                          '5747.01(A)(17)), then recover it in EQUAL INCREMENTS on '
                                          'Schedule of Adjustments line 27 (R.C. 5747.01(A)(18)). '
                                          'Fractions: 5/6 default, recovered 1/5 per year over 5 '
                                          'succeeding years; 2/3 where the employer increased Ohio '
                                          'income taxes withheld by at least 10% over the prior '
                                          'year, recovered 1/2 per year over 2 years; 6/6 where '
                                          'the taxpayer incurs a federal NOL RESULTING FROM the '
                                          '168(k)/179 expense, recovered 1/6 per year over 6 '
                                          'years. NO add-back is required where the withholding '
                                          'increase equals or exceeds the total 168(k)+179 '
                                          'expense, or for 168(k)/179 depreciation from a '
                                          'pass-through entity in which the taxpayer owns less '
                                          'than 5%. Unused portions cannot be carried forward. In '
                                          'any year with an NOL, NOL carryback or NOL carryforward '
                                          'the deduction is SUSPENDED and must be carried to the '
                                          'next year with none.',
                       'authority_source_code': 'OH_RC_5747_01',
                       'notes': '⚠ MODELLING CORRECTION (§12): THE FRACTION IS CHOSEN PER SOURCE '
                                'OF DEPRECIATION, NOT PER TAXPAYER. ODT FAQ Example 2 — "Mark must '
                                'use a different add-back fraction for each source of '
                                'depreciation" — applies 2/3 to §168(k) from one PTE and 5/6 to '
                                '§179 from a sole proprietorship IN THE SAME TAX YEAR and sums '
                                'them. The engine must track fractions per source and maintain '
                                'PARALLEL RECOVERY SCHEDULES OF DIFFERENT LENGTHS (5-year and '
                                '2-year) running concurrently for one taxpayer. ⚠ The <5% PTE '
                                'exception is a DISCRETIONARY COMMISSIONER WAIVER in R.C. '
                                '5747.01(A)(17)(a)(v) ("may waive"), though ODT administers it as '
                                "automatic in both the booklet and the FAQ — follow ODT's "
                                'administration, but do not state the exception as statutorily '
                                "absolute. OBBBA interaction: because Ohio's conformity date now "
                                "post-dates OBBBA's 100% bonus, Ohio add-backs get MATERIALLY "
                                'LARGER for TY2025 than TY2024 and the recovery tails extend '
                                'correspondingly. Applies on the IT 1041 and flows through the PTE '
                                'returns via the Ohio IT K-1.'},
                      {'item': 'IRC §179 expensing above the 12/31/2002 baseline',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'Ohio imposes NO §179 DOLLAR LIMIT OF ITS OWN. The '
                                          'federal §179 amount flows into the starting point '
                                          '(federal AGI); Ohio then adds back the same fraction '
                                          '(5/6 / 2/3 / 6/6, per source) of the EXCESS OVER the '
                                          '§179 amount that would have been allowed under §179 AS '
                                          'IT EXISTED ON DECEMBER 31, 2002, recovered on the same '
                                          '1/5 / 1/2 / 1/6 schedules. Net effect for TY2025: the '
                                          'OBBBA federal §179 amount flows in, the pre-2003 '
                                          'baseline is permanently allowed, and the fraction of '
                                          'the difference is DEFERRED, not denied.',
                       'authority_source_code': 'OH_FAQ_INCOME_BONUS_DEPR',
                       'notes': '⚠ THE 12/31/2002 §179 BASELINE IS $25,000 — RESOLVED in §12 (item '
                                '2). Neither the IT 1040 booklet nor R.C. 5747.01(A)(17) states a '
                                "figure; ODT's own 'Income – Bonus Depreciation' FAQ does, "
                                'verbatim: "The amount subject to the add-back is the taxpayer\'s '
                                "total §179 expense less $25,000 plus all of the taxpayer's "
                                '§168(k) depreciation expense," with a worked example ($125,000 − '
                                '25,000) + $80,000 = $180,000. Matches IRC §179(b)(1) as it stood '
                                'on 12/31/2002 (pre-JGTRRA). ⚠ THE ODT FORMULA APPLIES A FLAT '
                                '$25,000 SUBTRACTION AND SPECIFIES NO SEPARATE '
                                'INVESTMENT-LIMITATION PHASE-OUT — implement it as written, not as '
                                'a reconstructed 2002 §179 computation.'},
                      {'item': 'IRC §168(n) qualified production property',
                       'federal_treatment': 'OBBBA special depreciation allowance for qualified '
                                            'production property.',
                       'state_treatment': 'CONFORMS — §168(n) is OUTSIDE the R.C. 5747.01(A)(17) '
                                          'add-back. A full-text scan of the post-S.B. 9 R.C. '
                                          "5747.01 (version header 'Effective: March 5, 2026 · "
                                          'Latest Legislation: Senate Bill 9 - 136th General '
                                          "Assembly') finds EVERY reference to section 168 "
                                          "qualified as 'subsection (k) of section 168' or "
                                          "'section 168(k)' — in (A)(17)(a)(i), (a)(iv), (a)(v) "
                                          'and (A)(18)(a)(i), (c) — and NO reference to subsection '
                                          '(n) or to qualified production property anywhere in the '
                                          "section. ODT's FAQ formula is likewise closed-form: "
                                          '(§179 − 25,000) + §168k. S.B. 9 amended R.C. 5747.01 '
                                          'and did NOT extend the add-back to (n).',
                       'authority_source_code': 'OH_RC_5747_01',
                       'notes': 'RULE SAYS NO, on the statutory text — resolved in §12 (item 3). '
                                'RESIDUAL RISK (low but real): ODT has published no '
                                '§168(n)-specific guidance, and at least one practitioner '
                                'commentary describes Ohio as requiring an add-back of 100% QPP '
                                'amounts without distinguishing (k) from (n). Re-check for an ODT '
                                'information release or tax alert before the spec is authored; the '
                                'statute, not the commentary, governs.'}],
  'notes': '⚠ OHIO HAS NO CORPORATE INCOME TAX — R.C. 5733.01(G)(2)(a)(vi): "For tax year 2010 and '
           'each tax year thereafter, no tax." C corporations pay the COMMERCIAL ACTIVITY TAX '
           'instead: a gross-receipts tax at 0.26% (two and six-tenths mills per dollar) on Ohio '
           'taxable gross receipts above a $6,000,000 exclusion for TY2025, annual minimum tax '
           'ELIMINATED beginning 2024, quarterly returns due the 10th day of the 2nd month after '
           'quarter end (Q4 return is the annual return), registration only on EXCEEDING the '
           'exclusion. Conformity is irrelevant to the CAT — it has no federal-taxable-income '
           'starting point. So for most small and mid-market clients there is NO Ohio entity-level '
           'return at all, and a partnership or S corp whose equity investors are all full-year '
           "Ohio residents files NOTHING at the Ohio entity level. PTET: IT 4738 'Electing "
           "Pass-Through Entity Income Tax Return', ELECTIVE, ANNUAL and IRREVOCABLE for the year, "
           '3% (periods beginning on/after 1/1/2023), made by the entity and binding on all '
           "owners, base includes ALL owners' qualifying taxable income (residents AND "
           'nonresidents), disregarded entities may not elect. OWNER SIDE IS TWO-LEGGED and both '
           'legs must be modelled: an ADD-BACK on Ohio Schedule of Adjustments line 2 plus a '
           'REFUNDABLE credit on Ohio Schedule of Credits line 43 (verified structurally — line 43 '
           'sits inside the Refundable Credits block 41–46 → line 47 → IT 1040 line 16). ⚠ THREE '
           'PTE FORMS, THREE DIFFERENT RATES IN THE SAME YEAR: IT 4738 3%, IT 4708 composite '
           '3.125% (2025; tracks the top individual nonbusiness rate, was 3.5% for 2024), IT 1140 '
           'withholding 3%. Once an IT 1140 is filed for a period the PTE may not amend to an IT '
           '4708 or IT 4738 — the mutual exclusivity is one-way-locking. ⚠ TIMING TRAP: the FINAL '
           "TY2025 IT 1040 instruction booklet is stamped 'accurate as of November 27, 2025' "
           '(ModDate 2026-01-23) and WAS NEVER REVISED FOR S.B. 9 — it still reflects the pre-S.B. '
           '9 conformity date of March 7, 2025. ODT posted conformity guidance but did not reissue '
           "the booklet. The mechanical hooks are Schedule of Adjustments line 11 'Federal "
           "Conformity Additions' AND line 31 'Federal Conformity Deductions' — model BOTH. The "
           'R.C. 5701.11(B)(1) election is ALL-OR-NOTHING and RETURN-LEVEL: "A person must elect '
           'one version of the Internal Revenue Code (IRC); the person cannot selectively '
           'incorporate provisions from each version" — enforce as a single return-level flag, not '
           'a per-item choice. ⚠ LOCAL LAYER (out of scope for this row, but it is what breaks a '
           'ported spec): Ohio stacks TWO independent local income taxes on the state return — 210 '
           'taxing school districts (SD 100, two different tax bases, 0.25%–2.00%) and 600+ '
           'municipalities under Chapter 718, administered variously by RITA, CCA or the '
           'municipality. The municipal layer is a separate product. ⚠ Ohio-specific defect to '
           "implement as literal data: the TY2025 IT 1040 bracket table's $2,394.32 base does not "
           'derive arithmetically ($342.00 + 2.75% × $73,950 = $2,375.63, a $18.69 gap) — a '
           'genuine legislative defect in H.B. 96, TY2025-only. And the IT 1041 does NOT use the '
           'IT 1040 bracket schedule: only the upper two rows match; the first $26,050 is taxed at '
           '1.31287% for estates/trusts where the IT 1040 charges 0.000%.'},
 {'jurisdiction_code': 'MA',
  'conformity_type': 'partial',
  'authority_source_code': 'MA_TIR_26_4',
  'federal_reference_note': 'SPLIT BY CHAPTER — no single Massachusetts conformity date exists. '
                            'PERSONAL INCOME TAX (G.L. c. 62): STATIC at January 1, 2024 — G.L. c. '
                            '62, § 1(c): "\'Code\', the Internal Revenue Code of the United '
                            'States, as amended on January 1, 2024 and in effect for the taxable '
                            'year" — with a verbatim list of ROLLING carve-out sections, of which '
                            '§ 62(a)(1) (trade or business expense deductions) is the channel '
                            'through which current-Code business provisions reach the personal '
                            'income tax. CORPORATE EXCISE (G.L. c. 63, § 1; §§ 30.3, 30.4): '
                            'ROLLING — "the Internal Revenue Code of the United States, as amended '
                            'and in effect for the taxable year, unless otherwise provided." The '
                            'two answers point in opposite directions on OBBBA, but BOTH chapters '
                            'were then retroactively decoupled from the OBBBA business provisions '
                            'by the FY2026 mid-year Supplemental Budget, St. 2026, c. 101, signed '
                            'June 12, 2026, back to taxable years beginning on or after January 1, '
                            '2025. Authoritative conformity chart: TIR 26-4 (FINAL, 06/23/2026).',
  'summary': 'Massachusetts is a SPLIT-CONFORMITY state — c. 62 personal income tax static at '
             '1/1/2024 with rolling carve-outs, c. 63 corporate excise fully rolling — so any '
             "single 'MA conformity date' field is wrong by construction. For TY2025 the practical "
             'answer collapses to the same place on both sides, for a reason that POST-DATES THE '
             'TY2025 FILING SEASON: St. 2026, c. 101 (signed 6/12/2026) retroactively delayed '
             'conformity to the OBBBA business provisions — §179 increased limits, §168(n), '
             '§174/§174A, §163(j) ATI and §1400Z-2 — for both chapters, back to tax years '
             'beginning on or after 1/1/2025. §168(k) bonus remains permanently disallowed in both '
             'chapters, as it has been since 2002, with Massachusetts basis determined WITHOUT '
             'regard to §168(k). TY2025 Massachusetts returns filed on the original OBBBA basis '
             'must be amended; St. 2026 c. 101 § 38 gives a 90-day penalty-and-interest safe '
             'harbour that DOR has hardened into a site banner deadline of September 10, 2026. Any '
             'TY2025 MA logic built before June 2026 is stale.',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA § 70301, permanent).',
                       'state_treatment': 'PERMANENTLY NOT ALLOWED, BOTH CHAPTERS — decoupled '
                                          'since 2002 and never re-coupled; TIR 26-4 marks OBBBA § '
                                          "70301 'No' for c. 62 AND 'No' for c. 63. There is NO "
                                          'recovery schedule: the MASSACHUSETTS ADJUSTED BASIS of '
                                          'depreciable property is simply determined WITHOUT '
                                          'REGARD TO §168(k), so the adjustment FLIPS SIGN over '
                                          'the asset\'s life — DOR verbatim, "The adjustment may '
                                          'result in an addition to, or a subtraction from, '
                                          'taxable net income." A per-asset DUAL-BASIS LEDGER is '
                                          "required; a single 'add back bonus in year 1' rule "
                                          'produces wrong numbers from year 2 onward.',
                       'authority_source_code': 'MA_GL_C62_S2',
                       'notes': 'Statutory hooks: G.L. c. 62, § 2(d)(1)(N), verbatim "The '
                                'deduction allowed by section 168(k) of the Internal Revenue Code, '
                                'as amended and in effect for the current tax year" (personal '
                                'income tax); G.L. c. 63, § 30(4) (corporate excise). Historical '
                                'mechanics in TIR 02-11 and TIR 03-25, both still operative. This '
                                'is a FLAT NON-ADOPTION, not a Georgia-style '
                                'add-back-and-recover-over-life mechanism.'},
                      {'item': 'IRC §179 expensing limits (OBBBA increases)',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA § '
                                            '70306).',
                       'state_treatment': 'DELAYED — Massachusetts does not allow the increased '
                                          'dollar limitations for tax years beginning on or after '
                                          '1/1/2025 and before 1/1/2027; TIR 26-4 marks OBBBA § '
                                          "70306 'Yes, effective TYs beginning on or after "
                                          "1/1/2027' for BOTH chapters. Taxpayers must apply the "
                                          'limitations in IRC § 179 AS AMENDED AND IN EFFECT ON '
                                          'JULY 3, 2025, and Massachusetts adjusted basis is '
                                          'likewise determined by applying the §179 deductions as '
                                          'in effect on July 3, 2025. COUPLING RULE: MA §179 is '
                                          'NOT an independent election — the taxpayer MUST HAVE '
                                          'CLAIMED §179 FEDERALLY, and MA then caps the claimed '
                                          'amount at the pre-OBBBA limits (a $2,000,000 federal '
                                          'claim is limited to the MA cap, and MA basis reflects '
                                          'the MA amount).',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': '⚠ PROVENANCE — MASSACHUSETTS PUBLISHES NO §179 DOLLAR FIGURE FOR '
                                "TY2025 (§13.2). MA publishes only the RULE ('as amended and in "
                                "effect on July 3, 2025'). Its one printed figure is STALE AND "
                                'SUPERSEDED: the 2025 Form 1 Instructions (ModDate 2026-04-23, '
                                'still what mass.gov serves) say at Schedule C line 11 '
                                '"Massachusetts adopts the current federal §179 rules… The maximum '
                                '§179 expensing allowance is $2,500,000" — written before the '
                                '6/12/2026 law and never corrected. No phase-out figure is '
                                'published anywhere (zero hits for 4,000,000 / 3,130,000 / '
                                '1,250,000 across the Form 1, 355 and 355S instructions). The '
                                'working amounts of $1,250,000 limit / $3,130,000 phase-out (and '
                                'the § 179(b)(5)(A) SUV cap of $31,300) REST ON REV. PROC. 2024-40 '
                                '§ 3.25, RE-EXTRACTED VERBATIM FROM THE IRS PDF — NOT ON ANY '
                                'MASSACHUSETTS DOCUMENT. The derivation is sound and adopted '
                                '(§12.2/C-6) because Rev. Proc. 2024-40 issued in Oct 2024, '
                                "pre-OBBBA, and therefore IS '§179 as in effect on July 3, 2025' "
                                'for TY2025 — but keep the provenance visible. ⚠ TY2026 '
                                'FORWARD-YEAR TRAP: no federal publication will ever exist for a '
                                "TY2026 'pre-OBBBA' §179 figure (OBBBA rebased the inflation "
                                "adjustment, base year 2016 → 2024), so MA's TY2026 limit must be "
                                'computed by applying pre-OBBBA § 179(b)(6) indexing to the TY2025 '
                                'amounts — an MA-only computation. Gate-1 item; do not let the '
                                'engine reuse the TY2025 constants for TY2026.'},
                      {'item': 'IRC §168(n) qualified production property',
                       'federal_treatment': 'OBBBA § 70307 special depreciation allowance for '
                                            'qualified production property.',
                       'state_treatment': 'NOT ALLOWED for tax years beginning on or after '
                                          '1/1/2025 and before 1/1/2027, BOTH CHAPTERS; TIR 26-4 '
                                          "marks § 70307 'Yes, effective TYs beginning on or after "
                                          "1/1/2027'. Massachusetts basis determined without "
                                          'regard to §168(n).',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': 'Retroactive via St. 2026, c. 101 — see the September 10, 2026 '
                                'amendment window in `notes`.'},
                      {'item': 'IRC §174 / §174A research & experimental expenditures',
                       'federal_treatment': 'OBBBA § 70302 full expensing of domestic R&E, with § '
                                            '70302(f) retroactive transition rules for 2022–2024.',
                       'state_treatment': '§174A first-year expensing NOT allowed for tax years '
                                          'beginning on or after 1/1/2025 and before 1/1/2026 (TIR '
                                          "26-4: 'In part, effective TYs beginning on or after "
                                          "1/1/2026', both chapters), AND Massachusetts DOES NOT "
                                          'FOLLOW the P.L. 119-21 § 70302(f) transition rules for '
                                          '2022–2024. R&E incurred in tax years 2022 through 2025 '
                                          'must continue to be AMORTIZED UNDER §174 AS IN EFFECT '
                                          'ON JULY 3, 2025 — five-year amortization for domestic '
                                          'costs.',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': '⚠ REACHES FURTHER BACK THAN TY2025: recalculation is required for '
                                'taxable years beginning on or after 1/1/2022 and before 1/1/2026, '
                                'because MA also rejects the § 70302(f) transition rules. The '
                                'five-year mechanic no longer depends on the working draft — TIR '
                                '26-4 fn 5 is FINAL.'},
                      {'item': 'IRC §163(j) business interest limitation — adjusted taxable income',
                       'federal_treatment': 'OBBBA § 70303 EBITDA-style adjusted taxable income '
                                            'definition.',
                       'state_treatment': 'MA does NOT follow the OBBBA ATI definition for tax '
                                          'years beginning on or after 1/1/2025 and before '
                                          "1/1/2027 (TIR 26-4: 'Yes, effective 1/1/2027', both "
                                          'chapters). Taxpayers must RECOMPUTE ATI INCLUDING '
                                          'depreciation, amortization and depletion — the '
                                          'EBIT-style pre-OBBBA definition — before applying the '
                                          '30% cap.',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': 'Retroactive via St. 2026, c. 101.'},
                      {'item': 'IRC §1400Z-2 opportunity zones',
                       'federal_treatment': 'OBBBA § 70421 permanent renewal and enhancement of '
                                            'opportunity zones.',
                       'state_treatment': "TIR 26-4: 'No' for c. 62; 'Yes, effective 1/1/2027' for "
                                          'c. 63 — the OBBBA amendments are delayed to tax years '
                                          'beginning on or after 1/1/2027. SEPARATELY, MA '
                                          "redefines a 'Qualified Opportunity Zone' to include "
                                          'ONLY areas located ENTIRELY WITHIN THE COMMONWEALTH.',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': '⚠ OPEN CONFLICT — [UNVERIFIED-11], DOR CONTRADICTS ITSELF on the '
                                'START DATE of the in-Commonwealth-only rule. The Working Draft '
                                'TIR says "For taxable years beginning on or after January 1, '
                                '2026" (citing Supplemental Budget §§ 7, 14, 45); the DOR '
                                "'Differences … Corporate Excise' page (updated 7/29/2026) says "
                                '"For taxable years beginning on or after January 1, 2025". Both '
                                'read verbatim on 2026-08-06. PREFER the TIR (1/1/2026) — it cites '
                                'the enacting sections — BUT DO NOT CODE AN OZ START DATE WITHOUT '
                                'A GATE-1 RULING.'},
                      {'item': 'IRC §199A qualified business income deduction',
                       'federal_treatment': '20% QBI deduction (OBBBA § 70105 made permanent).',
                       'state_treatment': "NOT adopted — TIR 26-4 marks § 70105 'No' for c. 62; "
                                          'N/A for c. 63.',
                       'authority_source_code': 'MA_TIR_26_4',
                       'notes': "Individual lane. Same 'No' answer for the OBBBA increased SALT "
                                'cap (§ 70120), no tax on tips / overtime / car loan interest (§§ '
                                '70201/70202/70203), expanded §1202 QSBS (§ 70431), the excess '
                                'business loss modification (§ 70601), and the 1099-K de minimis '
                                'repeal (§ 70432, both chapters). MA has no standard deduction, no '
                                'itemized deductions and no NOL for personal income tax.'}],
  'notes': '⚠ conformity_type is `partial` BY CONSTRUCTION — the split is c. 62 STATIC 1/1/2024 vs '
           'c. 63 ROLLING, and any single-date field for Massachusetts is wrong. Both dates are '
           'carried in federal_reference_note. ⚠ AMENDMENT WINDOW — SEPTEMBER 10, 2026, and it is '
           'a RELIEF WINDOW, NOT A FILING DEADLINE. St. 2026 c. 101 § 38 provides that where a '
           'taxpayer who filed a TY2025 return applying P.L. 119-21 before enactment files an '
           'amended return WITHIN 90 DAYS OF ENACTMENT, "no interest or penalties shall be imposed '
           'on any underpayment, late payment, or underpaid estimated payment attributable to '
           'changes in law made by the Supplemental Budget." 90 days from 6/12/2026 = 9/10/2026, '
           'which DOR has hardened into a site-wide banner. The DUTY to amend arises from the '
           'substantive decoupling, not from § 38 — after 9/10/2026 the amendment is still '
           'required, it just stops being free. WHO IT BITES: only taxpayers whose TY2025 MA '
           'return took a position under Code §§ 163(j), 168(n), 174, 174A or 179, or an exclusion '
           'under § 1400Z-2 — both chapters. A TY2025 return with none of those six positions is '
           'unaffected. PTET: TWO excises exist as of TY2026, but FOR TY2025 ONLY THE c. 63D '
           'EXCISE APPLIES — 5% of qualified income taxable in Massachusetts, elected on Form '
           '63D-ELT (+ 63D-EXT), owner-side credit of 90% (NOT 100%) and REFUNDABLE against the c. '
           '62 personal income tax. The 10% haircut is the field most likely to be wrongly assumed '
           'to match another state. Elective, annual, made only on a TIMELY FILED ORIGINAL return '
           '(never on an amended return), irrevocable for the year and binding on all qualified '
           'members; qualified member = natural person, estate or trust (corporations and general '
           'partnerships are NOT qualified members and get no credit); a general partnership CAN '
           'be an eligible PTE; a grantor trust cannot (the grantor is the member); the excise '
           'base is Part-A/B/C-CLASS-BLIND at the entity level; PTE-level capital losses cannot be '
           'carried forward; c. 63D is fixed at 5% and CANNOT be raised to absorb the 4% surtax. ⚠ '
           'THE FORM NUMBER CHANGES AT THE TY2025/TY2026 BOUNDARY: TY2025 = Form 63D-ELT; TY2026 '
           'forward = Form 63-ELT (covering both the c. 63D and the new c. 63E 4% excise). Both '
           'excises EXPIRE if the federal SALT deduction limitation expires or is repealed — '
           'encode as a TY-gated feature, not a permanent one. ⚠ NEW STANDING RULE — MA now has an '
           'ANTI-MID-YEAR-CONFORMITY BRAKE (St. 2026 c. 101 §§ 13, 45): new Code amendments do not '
           'apply to the MA income tax or corporate excise for any taxable year beginning in the '
           'calendar year of enactment or any prior taxable year, EXCEPT where the Commissioner '
           'determines the revenue impact is under $20 million (rolling 3-year average, '
           'inflation-adjusted), with a 90-day reporting duty. Campaign-level note, not just an MA '
           'note. ⚠ Initiative Petition 25-18 (5% → 4% rate cut) is DEAD — the SJC held it '
           'ineligible for the 2026 ballot on 6/18/2026 (Finfer v. Attorney General, 2026 Mass. '
           'LEXIS 313), extinguishing every CONDITIONAL alternative effective date in the '
           'Supplemental Budget. Do not encode it; the 5.00% Part B rate stands for TY2026. ⚠ '
           'INDIVIDUAL-RETURN ARCHITECTURE (why nothing ports here): MA does NOT build the '
           'individual return by modifying federal AGI. It starts from FEDERAL GROSS INCOME (G.L. '
           'c. 62 § 2(a)) and splits MA gross income into PART A / PART B / PART C, each with its '
           'own adjustments, deductions and exemptions — and more than one rate INSIDE a single '
           'Part (Part A carries interest/dividends at 5%, short-term capital gains at 8.5% and '
           "long-term collectibles at 12%). There is no single 'taxable income × rate' line. ⚠ NO "
           'TY2025 REPORTING MECHANISM IS PUBLISHED for the §179 / §163(j) / §168(n) / §174 '
           'back-outs (§13.3). NO MA FORMS WERE REISSUED AFTER 6/12/2026 — captured ModDates: Form '
           '1 and 1-NR/PY 2026-01-23, Form 1 instructions 2026-04-23, Sch B 2026-01-23, Sch D '
           '2026-04-10, Sch Y 2026-02-23, Sch 4% Surtax 2026-02-05, Sch S 2026-02-12, 63D-ELT '
           'instructions 2026-04-23, Form 355 instructions 2026-06-01, Form 355S instructions '
           '2026-06-02 — nothing post-dates the law and no new add-back schedule exists. The 355 '
           'and 355S instructions still carry an unfilled placeholder, "See TIR 25-XX for a '
           'discussion of the effect of the federal legislation on the corporate excise." GATE-1 '
           "WALK ITEM; DO NOT GUESS A LINE. ⚠ Also still open: §197 / §195 treatment is 'NO RULE "
           "FOUND', NOT 'the rule says no' ([UNVERIFIED-5]) — neither DOR Differences page "
           'mentions either section, and under c. 63 rolling conformity and the c. 62 § 62(a)(1) '
           'carve-out federal treatment SHOULD carry, but that is an inference. E-FILE: the TY2025 '
           'Letter of Intent deadline (12/1/2025) has PASSED — MA TY2025 is spec-only, with no '
           'filing path.'},
 {'jurisdiction_code': 'NY',
  'conformity_type': 'rolling',
  'authority_source_code': 'NY_DTF_N_26_1',
  'federal_reference_note': "ROLLING IRC conformity — Tax Law §607 for personal income tax ('the "
                            'internal revenue code of nineteen hundred eighty-six … as the same '
                            'may be or become effective at any time or from time to time for the '
                            "taxable year'); Tax Law §208(9) for corporations (entire net income "
                            'presumably the same as federal taxable income). NO static conformity '
                            'date. The §607 freeze clause (post-March 1, 2020 amendments do not '
                            'apply) is expressly limited to tax years beginning before 2022 and is '
                            'EXPIRED for TY2025 — do not carry March 1, 2020 into a TY2025 spec. '
                            'Because NY is rolling, OBBBA (P.L. 119-21, signed 7/4/2025) flowed '
                            'into the NY base automatically; New York then enacted TARGETED '
                            'decouplings retroactive to tax years beginning on or after January 1, '
                            '2025 via S.9009-C (the C-print), signed by Gov. Hochul May 28, 2026. '
                            "Cite P.L. 119-21 (N-26-1 prints the number both ways: fn 1 '119-121' "
                            "is a typo, fn 3 '119-21' is correct).",
  'summary': 'New York STATE is a rolling-conformity state that did NOT freeze for OBBBA. It took '
             'OBBBA by default and then decoupled from EXACTLY TWO provisions — IRC §168(n) '
             'qualified production property and IRC §174/§174A R&E expensing — retroactively to '
             'TY2025, per DTF Notice N-26-1. NY State did NOT decouple from OBBBA §179 (the '
             'federal $2,500,000 / $4,000,000 limits are INHERITED, not restated in any NY form) '
             'and did NOT decouple from §163(j). Layered on top is a decades-old, UNRELATED '
             '§168(k) bonus add-back (Tax Law §612(b)(8), tax years beginning after 12/31/2002) '
             'that has nothing to do with OBBBA. ⚠ NEW YORK CITY has a DIFFERENT posture — NYC '
             'decoupled from §168(n), §174/§174A, §163(j) AND §179 — but this model holds one row '
             'per (jurisdiction_code, tax_year), so the City posture cannot be a second row; it is '
             'recorded in decoupled_items and notes below.',
  'decoupled_items': [{'item': 'IRC §168(n) qualified production property (OBBBA)',
                       'federal_treatment': 'Special depreciation allowance for qualified '
                                            'production property under IRC §168(n), added by OBBBA '
                                            '(P.L. 119-21).',
                       'state_treatment': "NY STATE DECOUPLED — 'The full amount of any federal "
                                          'deduction for accelerated depreciation on qualified '
                                          'production property under IRC § 168(n) must be added '
                                          "back' (N-26-1). Statute as codified: Tax Law "
                                          '§612(b)(44) / §612(c)(48) (PIT, tax years beginning '
                                          '2025+); §208(9)(b)(28) / §208(9)(a)(24) (corporate '
                                          "mirror — 'as if the taxpayer has not made an election "
                                          'pursuant to subsection (n) of section one hundred '
                                          "sixty-eight'). Reporting: "
                                          'individuals/partnerships/estates & trusts on Form '
                                          'IT-398 PART 1 then Form IT-225 codes A-209 / S-213 (DTF '
                                          'reuses the §168(k) form and the §168(k) code pair); '
                                          'partnerships filing Form IT-204.1 use the CORPORATE '
                                          'codes A-507 / S-507; C corporations on Form CT-399 Part '
                                          '1 Section B then CT-225 / CT-225-A codes A-507 / S-507; '
                                          'NY S corporations CT-399 Part 1 Section B reported on '
                                          'CT-34-SH lines 2 and 4; Article 33 insurance '
                                          'corporations CT-399 Part 1 Section B reported on CT-33 '
                                          '/ CT-33-A. Partners, shareholders and beneficiaries '
                                          'must NOT complete IT-398 or CT-399 — they use IT-225 '
                                          'Part 2 of Schedules A and B (or CT-225 / CT-225-A).',
                       'authority_source_code': 'NY_DTF_N_26_1',
                       'notes': '⚠ The decoupling exists in TY2025 ONLY in N-26-1 — every TY2025 '
                                'form predates the 2026-05-28 budget (IT-398 /ModDate 2025-11-04, '
                                'IT-225-I 2026-03-04), and IT-225-I contains NO §168(n) code at '
                                'all. A spec must encode the notice, not the form. N-26-1 also '
                                "imposes a retroactive amended-return duty: 'If a 2025 tax return "
                                'has been filed, an amended return must be filed to report the '
                                "modifications described in this notice,' with "
                                'penalty-and-interest relief available. Open item U-12: no reissue '
                                'confirmed and it is unknown whether the MeF schema accepts the '
                                'new codes for TY2025 — re-check immediately before authoring.'},
                      {'item': 'IRC §174 / §174A research & experimental expenditures (OBBBA)',
                       'federal_treatment': 'Federal deduction for foreign and domestic R&E '
                                            'expenditures under IRC §§174, 174A and P.L. 119-21 '
                                            '§70302(f)(2)(A).',
                       'state_treatment': "NY STATE DECOUPLED — 'The full amount of any federal "
                                          'deduction for foreign and domestic R&E expenditures '
                                          "must be added back' (N-26-1). Subtraction detail: "
                                          "post-1/1/2025 expenditures amortize over 60 MONTHS ('as "
                                          "if the election under IRC § 174A(c) applied'); "
                                          "pre-1/1/2025 expenditures 'must continue to be "
                                          'amortized under the federal rules in effect on January '
                                          "1, 2022' (i.e. under IRC §174). Codes: IT-225 A-225 "
                                          '(addition) with S-221 (post-1/1/2025) or S-222 '
                                          '(pre-1/1/2025); IT-204.1 uses A-225 / S-221 / S-222; C '
                                          'corporations use A-225 / S-221 / S-222 on CT-225 / '
                                          'CT-225-A — NOT A-507 / S-507. Statute as codified: Tax '
                                          'Law §612(b)(45), §612(c)(49), §612(c)(50), beginning '
                                          '2025.',
                       'authority_source_code': 'NY_DTF_N_26_1',
                       'notes': '⟹ CORRECTED by §12 item 4: the draft implied A-507/S-507 covered '
                                'R&E too; they are the §168(n) codes ONLY. IT-225-I (2025) '
                                'contains no A-225 / S-221 / S-222 codes at all — the R&E '
                                'decoupling likewise lives only in N-26-1 for TY2025 (U-12).'},
                      {'item': 'IRC §168(k) bonus depreciation — LEGACY NY add-back, independent '
                               'of OBBBA',
                       'federal_treatment': '100% bonus depreciation (permanent under OBBBA for '
                                            'property acquired and placed in service after '
                                            '1/19/2025).',
                       'state_treatment': 'NOT ADOPTED, and has not been since 2003 — Tax Law '
                                          "§612(b)(8) requires, 'for taxable years beginning after "
                                          'December thirty-first, two thousand two, in the case of '
                                          'qualified property described in paragraph two of '
                                          "subsection k of section 168,' an addition modification "
                                          'for the federal bonus deduction. Recovery is NOT a '
                                          'scheduled unwind: New York recomputes depreciation as '
                                          'if §168(k) had never applied and allows the recomputed '
                                          "amount as a subtraction over the asset's life. Precise "
                                          'anchor (IT-398, verbatim): the NYS deduction is '
                                          "'determined under IRC § 167, as that section would have "
                                          'applied to the property IF IT HAD BEEN ACQUIRED ON '
                                          "SEPTEMBER 10, 2001'; any consistent §167 method is "
                                          'acceptable. THREE codes: A-209 addition (federal '
                                          'deduction, IT-398 col. G), S-213 subtraction (NY '
                                          'deduction, IT-398 col. F), and S-214 '
                                          'year-of-disposition adjustment (IT-398 Part 2) where '
                                          'total federal depreciation exceeded total NY '
                                          'depreciation on the disposed asset. Forms: IT-398 '
                                          '(individuals / partnerships / fiduciaries), CT-399 '
                                          '(corporations). Form IT-399 is a DIFFERENT form '
                                          '(pre-ACRS / other NY differences) — do not collapse '
                                          'IT-398 and IT-399.',
                       'authority_source_code': 'NY_TAX_LAW_612',
                       'notes': '⚠ Do NOT conflate this with the OBBBA decoupling — it predates '
                                "OBBBA by two decades. OBBBA's permanent 100% bonus simply makes "
                                "the NY add-back bigger. Statutory exceptions: 'qualified "
                                "resurgence zone property' and 'qualified New York Liberty Zone "
                                "property' (§208(9)(n-1), §208(9)(q) for corporations; parallel "
                                'PIT provisions) — geographically narrow legacy carve-outs, almost '
                                'certainly out of scope for v1. S-214 and the disposition leg were '
                                'ADDED by the verification pass.'},
                      {'item': 'Depreciation claimed by institutional real estate investors on '
                               'covered residential property (code A-223) — a SECOND, unrelated NY '
                               'depreciation disallowance',
                       'federal_treatment': 'Full federal depreciation deduction on the property.',
                       'state_treatment': 'An institutional real estate investor must add back the '
                                          'ENTIRE federal depreciation deduction on NY residential '
                                          "'covered property' of no more than two dwelling units "
                                          '(Tax Law §208.9(c-4)(2)), via IT-225 code A-223. IT-398 '
                                          "carries an explicit carve-out: 'Do not use Form IT-398 "
                                          'to report depreciation amounts on any covered '
                                          "properties.'",
                       'authority_source_code': 'NY_TAX_LAW_612',
                       'notes': 'ADDED by the 2026-08-06 verification pass from IT-225-I (2025) '
                                'and IT-398 (2025), both read verbatim. Separate from both the '
                                '§168(k) legacy add-back and the OBBBA decouplings.'},
                      {'item': 'IRC §179 expensing limits — NY STATE: NOT decoupled',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'CONFORMS. New York does not legislate its own §179 '
                                          'dollar limit — the federal deduction flows through the '
                                          'federal-taxable-income / FAGI starting point, and NY '
                                          "did not decouple from OBBBA's §179 change. For TY2025 "
                                          'the federal $2,500,000 / $4,000,000 figures apply for '
                                          'NY STATE purposes. The one NY State exception is sport '
                                          'utility vehicles: Tax Law §612(b)(36) requires an '
                                          'add-back of the §179 deduction claimed for an SUV that '
                                          "is not a 'passenger automobile' under IRC §280F(d)(5), "
                                          'for taxpayers who are not eligible farmers — codes '
                                          "A-208 ('Sport utility vehicle expense deduction', SUV "
                                          'weighing MORE THAN 6,000 pounds) and S-212 (recapture).',
                       'authority_source_code': 'NY_TAX_LAW_612',
                       'notes': "'RULE SAYS NO', not 'no rule found' (U-4, upgraded on "
                                'verification): an explicit absence-of-modification sweep of the '
                                'complete IT-225-I (2025) addition/subtraction code index found NO '
                                '§179 modification of any kind other than the SUV pair — no '
                                'dollar-limit adjustment, no OBBBA modification. RSM states '
                                "directly that for §179 'New York State has not decoupled from the "
                                "changes.' ⚠ The $2,500,000 / $4,000,000 figures are INHERITED "
                                'from federal and are NOT restated in any NY DTF form or '
                                'instruction — encode them as federal inheritance with a '
                                'conformity assertion, not as NY-published constants. ⚠ NYC is the '
                                'opposite — see the NYC entry below.'},
                      {'item': 'IRC §163(j) business interest limitation — NY STATE: NOT decoupled',
                       'federal_treatment': 'OBBBA change to the §163(j) ATI computation (EBITDA → '
                                            'EBIT).',
                       'state_treatment': 'NY STATE did NOT decouple. RSM, on the §163(j) change: '
                                          "'Similar changes were not enacted for New York State' — "
                                          'the change was City-only.',
                       'authority_source_code': 'NY_DTF_N_26_1',
                       'notes': "Secondary source (RSM) used only for the negative; N-26-1's "
                                'decoupling scope covers §168(n) and §174/§174A only. ⚠ NYC DID '
                                'decouple (EBIT-only ATI) — see the NYC entry.'},
                      {'item': "⚠ NEW YORK CITY divergence — §179 and §163(j) (and the City's own "
                               '§168(k) rules). JURISDICTION-DIMENSION PROBLEM: this row shape '
                               'cannot express it.',
                       'federal_treatment': 'OBBBA §179 increased limits; OBBBA §163(j) ATI '
                                            'change. Both flow into the NY base by rolling '
                                            'conformity.',
                       'state_treatment': 'NEW YORK CITY DECOUPLED FROM BOTH — NYC uses EBIT-only '
                                          'ATI for §163(j) and the PRE-OBBBA §179 limits — for the '
                                          'Unincorporated Business Tax, General Corporation Tax, '
                                          'Banking Corporation Tax and Business Corporation Tax, '
                                          'for tax years beginning on or after 1/1/2025. NYC also '
                                          'decoupled from §168(n) and §174/§174A (so NYC decoupled '
                                          'from ALL FOUR while the State decoupled from only two). '
                                          'Separately, NYC is decoupled from §168(k) bonus for '
                                          "UBT/GCT/Bank Tax/BCT except 'qualified New York liberty "
                                          "zone property,' 'qualified New York liberty zone "
                                          "leasehold improvements,' and 'qualified property' "
                                          "placed in service in the Resurgence Zone — and NYC's "
                                          "recomputation anchor DIFFERS from the State's: for City "
                                          'purposes depreciation on all other qualified property '
                                          "'must be calculated as if the property was placed in "
                                          "service PRIOR TO SEPTEMBER 11, 2001' (vs the State's "
                                          "'acquired on September 10, 2001'). NYC depreciation "
                                          'adjustment form: NYC-399Z (flows to NYC-204 Schedule B '
                                          'lines 14(c) and 19). NYC SUV rule: the §280F limit '
                                          "applies, other than for eligible farmers, to 'a sport "
                                          'utility vehicle that is NOT a passenger automobile for '
                                          "purposes of section 280F(d)(5)' — i.e. the HEAVY SUVs "
                                          'that escape §280F federally; such SUVs also get no NYC '
                                          'bonus depreciation except qualified Resurgence Zone '
                                          'property, and gain/loss on disposition must be adjusted '
                                          'for the limited City deductions.',
                       'authority_source_code': 'NY_S9009C_PART_G_NYC',
                       'notes': '⚠⚠ MODEL LIMITATION, RECORDED DELIBERATELY: '
                                'JurisdictionConformitySource holds ONE row per '
                                '(jurisdiction_code, tax_year), so New York City CANNOT be '
                                "represented as a second row under 'NY'. The row above carries the "
                                'NY STATE posture only. Any depreciation or interest-limitation '
                                'engine needs a JURISDICTION DIMENSION, not a single state flag '
                                '(§12: different postures, different recomputation anchors, '
                                'different forms IT-398/CT-399 vs NYC-399Z, different SUV rules). '
                                '⚠ SEPARATE AGENCY: NYC business taxes are administered by the NYC '
                                "Department of Finance, not DTF, and DTF's N-26-1 GOVERNS THE "
                                'STATE TAXES ONLY — it does not reach the City taxes. The City '
                                'decouplings were enacted by the STATE budget bill amending the '
                                'NYC Administrative Code (S.9009-C Part G: NYC Admin. Code '
                                '§§11-506(b)&(c) UBT, 11-602.8(a)&(b) GCT, 11-641(b)&(e) Bank Tax, '
                                '11-651(e) and 11-652.8(a)&(b) BCT); there is no NYC DOF '
                                'memorandum implementing them. ⚠ U-5 STILL OPEN AND BLOCKING: the '
                                'specific post-decoupling NYC §179 dollar limit and phaseout for '
                                'TY2025 EXIST IN NO PUBLISHED SOURCE — EY describes the change '
                                "only as reverting 'to the NYC limitations in effect before the "
                                "OBBBA'; Grant Thornton and RSM state no figures; the TY2025 "
                                'NYC-204/NYC-202 instructions (/ModDate 2025-12-18) predate the '
                                "2026-05-28 budget entirely. 'This is now the highest-priority "
                                "open item and it blocks any NYC business-tax module.' Would "
                                'settle it: the amended NYC Admin. Code §11-507 / §11-602.8(a) '
                                'text as enacted in S.9009-C Part G, the first NYC DOF Finance '
                                'Memorandum implementing it, or the TY2026 NYC-204 instructions. '
                                'NYC SUV authority ⟹ CORRECTED: NYC Finance Memorandum 25-1 (not '
                                'the stale FM 13-01); for §163(j) NYC points to FM 18-11, for TCJA '
                                'items FM 18-10.'}],
  'notes': '⚠⚠ ONE STATE, TWO CONFORMITY POSTURES — and this row can only hold one. NY State '
           'decoupled from §168(n) and §174/§174A ONLY; NYC decoupled from those PLUS §163(j) and '
           '§179. The model holds one row per (jurisdiction_code, tax_year), so the NYC posture is '
           'recorded above as a decoupled_items entry rather than as a second row. Treat the '
           'City/State split as a JURISDICTION DIMENSION in the engine, not a boolean — the two '
           "jurisdictions also use different §168(k) recomputation anchors (State 'acquired "
           "9/10/2001' vs City 'placed in service prior to 9/11/2001'), different depreciation "
           'forms (IT-398 / CT-399 vs NYC-399Z) and different SUV rules, and NYC business taxes '
           "are filed with a different agency (NYC Dept. of Finance). ⚠ BLOCKER: NYC's "
           'post-decoupling §179 limits exist in NO published source (U-5 still open) — this '
           'blocks any NYC business-tax module, though not the State modules. ⚠ Do not conflate '
           'the OBBBA decoupling with the SEPARATE, decades-old §168(k) bonus add-back (Tax Law '
           '§612(b)(8), tax years beginning after 12/31/2002) that predates OBBBA entirely — '
           'though note DTF collapses the two onto one form and one code pair for TY2025 (§168(n) '
           'property is reported in Part 1 of the §168(k) form IT-398 using codes A-209 / S-213). '
           '⚠ WATCH ITEM U-12: every TY2025 NY form predates the 2026-05-28 retroactive law; no '
           'reissue confirmed, and it is unknown whether the MeF schema accepts A-225 / S-221 / '
           'S-222 for TY2025. Re-check /ModDate and the DTF corrections page immediately before '
           'authoring. PTET: NY has TWO. NYS PTET (Art. 24-A) is BRACKETED, not flat — 6.85% / '
           '9.65% / 10.30% / 10.90% with base amounts $137,000 / $426,500 / $2,486,500 (Tax Law '
           '§862); partnerships compute TWO POOLS (resident worldwide / nonresident NY-source). '
           'NYC PTET (Art. 24-B) is FLAT 3.876% and its credit is claimed on the STATE return '
           '(IT-653 Schedule A col. D; State PTET is col. C). Owner side is a REFUNDABLE CREDIT '
           'plus a MANDATORY add-back, and there are THREE add-back codes, not two: A-219 (State, '
           'IT-653 line 1), A-222 (NYC, IT-653 line 2), A-220 (other jurisdictions, §612(b)(43)). '
           'A NYS PTET election is a PREREQUISITE for the NYC PTET election. ⚠ NEITHER PTET RETURN '
           'CAN BE E-FILED by third-party software — DTF requires the election, the annual return '
           "and the extension through the entity's Business Online Services 'PTET web file' "
           'application; no PTET form appears in Publication 115 or TR-376-PITMEF. Form CT-6 (the '
           'NY S election) is in the same position. Scope PTET as compute-and-worksheet. '
           "Complexity: the brief rates NY LARGE — 'New York gets its OWN dedicated wave. Do not "
           "batch it.' Do not port a single-base PTET, a single-rate corporate tax, or a "
           'state-flag depreciation engine into NY.'},
 {'jurisdiction_code': 'MD',
  'conformity_type': 'rolling',
  'authority_source_code': 'MD_TG_10_108',
  'federal_reference_note': 'ROLLING conformity with a statutory automatic-decoupling trigger. '
                            "Individual: Maryland AGI 'is the individual's federal adjusted gross "
                            'income for the taxable year as adjusted under this Part II of this '
                            "subtitle' (Md. Code, Tax-General §10-203). Corporate: Maryland "
                            "modified income is 'the corporation's federal taxable income for the "
                            'taxable year as determined under the Internal Revenue Code and as '
                            "adjusted under this Part II' (§10-304). NO fixed conformity date. "
                            '§10-108 acts as a one-year rolling brake: an IRC amendment affecting '
                            "FAGI/FTI 'does not affect the determination of Maryland taxable "
                            "income' for any taxable year beginning in — or preceding — the "
                            'calendar year the amendment was enacted, UNLESS the Comptroller '
                            'determines the revenue impact is LESS THAN $5,000,000 (§10-108(a), '
                            '(c)). [§12 CORRECTION: §10-108(b) assigns the 60-day report to THE '
                            'COMPTROLLER, not to the Bureau of Revenue Estimates — BRE, a unit '
                            "within the Comptroller's office, produced the 9/5/2025 report in "
                            'practice, so the outcome is unchanged, but the statutory actor is the '
                            'Comptroller. The $5,000,000 test is measured against STATE INCOME TAX '
                            'REVENUE FOR A FISCAL YEAR, not against a tax-year impact.] OBBBA '
                            '(P.L. 119-21) is PARTIALLY ADOPTED for TY2025: the §10-108 trigger '
                            'fired for exactly three OBBBA sections, each scored above $5M by BRE.',
  'summary': 'Maryland is a ROLLING-conformity state (Maryland AGI starts at federal AGI) with a '
             'STATUTORY PERMANENT decoupling from §168(k) bonus and from post-2002 §179 increases, '
             'plus a §10-108 AUTOMATIC temporary decoupling that caught three OBBBA business '
             'provisions for TY2025: §70302 (new IRC §174A domestic R&E full expensing), §70303 '
             '(§163(j) ATI modification) and §70307 (new IRC §168(n) qualified production '
             'property). Maryland §179 is FROZEN at $25,000 / $200,000 — these are the Maryland '
             "figures, NOT the federal OBBBA $2,500,000 / $4,000,000 and NOT Georgia's. ⚠ The "
             '§168(k) and §179 add-backs DO NOT APPLY to manufacturing entities (NAICS 31–33) for '
             'property placed in service on or after 1/1/2019. Mechanically the decoupling runs '
             'through PRO FORMA FEDERAL RETURNS reported on Form 500DM — it is not a percentage '
             'add-back.',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': '100% bonus depreciation (restored permanently by '
                                            'OBBBA §70301 for qualifying property).',
                       'state_treatment': 'DECOUPLED — full add-back, no percentage, PERMANENT and '
                                          "statutory. §10-210.1(b)(1)(i): 'an amount is added to "
                                          'or subtracted from federal adjusted gross income to '
                                          'reflect the determination of the depreciation deduction '
                                          'provided under § 167(a) of the Internal Revenue Code '
                                          'and the adjusted basis of property WITHOUT REGARD TO '
                                          'THE ADDITIONAL ALLOWANCE UNDER § 168(k) of the Internal '
                                          "Revenue Code.' Reported on Form 500DM Part A line 1 as "
                                          'the difference between a pro forma federal return and '
                                          'the actual federal return (positive difference = '
                                          'addition modification; negative = subtraction). '
                                          'Recovery: the Maryland adjusted basis stays higher, so '
                                          'later years generate subtraction modifications until '
                                          'the basis difference is exhausted.',
                       'authority_source_code': 'MD_TG_10_210_1',
                       'notes': 'This decoupling is STATUTORY and PRE-DATES OBBBA — which is why '
                                'OBBBA §70301 does not appear on the §10-108 automatic-decoupling '
                                'list; Maryland was already decoupled. ⚠ Subject to the NAICS '
                                '31–33 manufacturing carve-out (separate entry below). Extended to '
                                'corporations by §10-310.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'DECOUPLED — FROZEN at the pre-2003 federal figures. '
                                          '§10-210.1(b)(3)(i): modification to reflect the maximum '
                                          "§179 expense 'without regard to any changes made to "
                                          'that section after December 31, 2002: 1. increasing '
                                          'above $25,000 the dollar limitation set forth in § '
                                          '179(b)(1)…; or 2. increasing above $200,000 the '
                                          "phase-out threshold set forth in § 179(b)(2).' Form "
                                          "500DM restates it: 'a taxpayer only is allowed to "
                                          'expense up to $25,000, reduced dollar-for-dollar by the '
                                          'amount over $200,000, of the cost of Section 179 '
                                          "property.'",
                       'authority_source_code': 'MD_TG_10_210_1',
                       'notes': '⚠ $25,000 / $200,000 ARE THE MARYLAND FIGURES — they are NOT the '
                                "federal OBBBA $2,500,000 / $4,000,000 and they are NOT Georgia's. "
                                'Do not cross-apply. ⚠ Subject to the NAICS 31–33 manufacturing '
                                'carve-out (separate entry below). Extended to corporations by '
                                '§10-310.'},
                      {'item': '⚠ NAICS 31–33 MANUFACTURING-ENTITY CARVE-OUT from the §168(k) and '
                               '§179 add-backs (Maryland-specific — do not port from any other '
                               'state)',
                       'federal_treatment': 'Federal law draws no such distinction — full federal '
                                            'bonus and full federal §179 apply to all taxpayers '
                                            'alike.',
                       'state_treatment': "The §168(k) add-back 'DOES NOT APPLY TO PROPERTY PLACED "
                                          'IN SERVICE BY A MANUFACTURING ENTITY ON OR AFTER '
                                          "JANUARY 1, 2019' (§10-210.1(b)(1)(ii)), with an "
                                          'IDENTICAL carve-out for §179 at §10-210.1(b)(3)(ii). '
                                          "'Manufacturing entity' = a trade or business 'primarily "
                                          'engaged in activities that, in accordance with the '
                                          'North American Industrial Classification System '
                                          '(NAICS), United States Manual, … 2012 EDITION, would be '
                                          "included in SECTOR 31, 32, or 33'; it 'does not include "
                                          'a refiner, as defined in § 10-101 of the Business '
                                          "Regulation Article' (§10-210.1(a)(4)). → A qualifying "
                                          'manufacturer gets FULL FEDERAL BONUS AND FULL FEDERAL '
                                          "§179 on the Maryland return. Via §10-310 ('the federal "
                                          'taxable income of a corporation shall be adjusted as '
                                          "provided for an individual under § 10-210.1') the "
                                          'carve-out reaches CORPORATIONS as well as individuals.',
                       'authority_source_code': 'MD_TG_10_210_1',
                       'notes': '⚠⚠ THE CARVE-OUT APPEARS ON NO TY2025 MARYLAND FORM OR '
                                'INSTRUCTION. The verification pass grepped the FINAL TY2025 Form '
                                '500DM + instructions, the Corporate Booklet and the Resident '
                                'Booklet: ZERO occurrences. It must be implemented FROM THE '
                                'STATUTE ALONE — there is no form line or checkbox that captures '
                                'it and therefore no printed-form cross-check. Treat the NAICS '
                                '31–33 entity attribute as a spec-level input with its own audit '
                                'trail, and FLAG IT FOR KEN before the depreciation engine is '
                                "authored. (The Corporate Booklet's only 'manufacturing' hits are "
                                'the APPORTIONMENT rule — special single sales factor, COMAR '
                                '03.04.03.10 — a different rule entirely; do not conflate.) ⚠ TWO '
                                'LIMITS, easy to overstate: (1) It does NOT reach the '
                                'heavy-duty-SUV decoupling — §10-210.1(b)(5) has no manufacturing '
                                'exception, and Administrative Release 38 states the §280F '
                                "treatment applies to all taxpayers 'including manufacturing "
                                "entities'; 'full federal §179' means the §179 "
                                'dollar-limit/phase-out add-back switches off, not (b)(5). (2) '
                                "Verified verbatim 2026-08-06: both carve-outs read 'ON OR AFTER "
                                "January 1, 2019' — some secondary summaries render it 'after'. "
                                'Independently corroborated by Administrative Release 38, which '
                                'attributes it to the More Jobs For Marylanders Act (SB 317).'},
                      {'item': 'OBBBA §70302 — full expensing of domestic research & experimental '
                               'expenditures (new IRC §174A) [§10-108 automatic decoupling, '
                               'TY2025]',
                       'federal_treatment': 'Full expensing of domestic R&E expenditures under new '
                                            'IRC §174A.',
                       'state_treatment': 'AUTOMATICALLY DECOUPLED for TY2025 (and preceding '
                                          'years) under §10-108 — BRE scored the impact above $5M. '
                                          'Maryland requires 5-YEAR (60-MONTH) '
                                          'capitalization/amortization on the Maryland return. '
                                          'Maryland WILL NOT ACCEPT AMENDED RETURNS for 2022–2024 '
                                          'claiming the §174A Note (f) catch-up.',
                       'authority_source_code': 'MD_COMP_ALERT_OBBBA_2026',
                       'notes': 'Reported through the pro forma / Form 500DM mechanism. Forms '
                                'updated for the decoupling: 500DM, 502SU, 505SU, 510/511 K-1 and '
                                '504 K-1 — the 502SU/505SU SUBTRACTION-modification code lists '
                                'were also revised, so the subtraction side has its own code '
                                'entries to spec, not only the 500DM addition side.'},
                      {'item': 'OBBBA §70303 — modification of the §163(j) business-interest '
                               'limitation (IRC §163(j)(8)(A)(v)) [§10-108 automatic decoupling, '
                               'TY2025]',
                       'federal_treatment': 'OBBBA modification of the §163(j) adjusted taxable '
                                            'income computation.',
                       'state_treatment': 'AUTOMATICALLY DECOUPLED for TY2025 under §10-108. ATI '
                                          'must be recomputed on a Maryland pro forma WITH '
                                          'depreciation / amortization / depletion deducted. '
                                          'ADD-BACK ONLY — never a subtraction.',
                       'authority_source_code': 'MD_COMP_ALERT_OBBBA_2026',
                       'notes': 'Add-back only; there is no subtraction leg for this item.'},
                      {'item': 'OBBBA §70307 — special depreciation allowance for qualified '
                               'production property (new IRC §168(n)) [§10-108 automatic '
                               'decoupling, TY2025]',
                       'federal_treatment': 'Special depreciation allowance for qualified '
                                            'production property under new IRC §168(n).',
                       'state_treatment': 'AUTOMATICALLY DECOUPLED for TY2025 under §10-108. '
                                          'Recompute under IRS Pub. 946 EXCLUDING §168(n); the '
                                          'basis difference recovers as subtraction modifications '
                                          'in later years.',
                       'authority_source_code': 'MD_COMP_ALERT_OBBBA_2026',
                       'notes': 'The Comptroller states the later-year recovery pattern explicitly '
                                'for this §168(n) case in Tax Alert Example 6.'},
                      {'item': 'Heavy-duty SUV depreciation',
                       'federal_treatment': 'Vehicles rated over 6,000 lb GVW escape the IRC §280F '
                                            'luxury-auto limitations federally.',
                       'state_treatment': 'ADDITIONALLY DECOUPLED — §10-210.1(b)(5) requires '
                                          "depreciation computed 'as if the heavy duty SUV were "
                                          'subject to the limitations of § 280F … as it would be '
                                          'if the vehicle were rated at 6,000 pounds gross vehicle '
                                          "weight or less.' 'Heavy duty SUV' = 4-wheeled, more "
                                          'than 6,000 but not more than 14,000 lb GVW '
                                          '(§10-210.1(a)(3)). Form 500DM: applies to vehicles '
                                          'placed in service after 5/31/2004.',
                       'authority_source_code': 'MD_TG_10_210_1',
                       'notes': '⚠ NO manufacturing exception — §10-210.1(b)(5) is not carved out, '
                                "and AR 38 confirms §280F treatment binds all taxpayers 'including "
                                "manufacturing entities'."},
                      {'item': 'Legacy / non-OBBBA items also reported on Form 500DM (CARES Act '
                               'items, §172 farming-loss carryback election, §108(i) deferrals)',
                       'federal_treatment': 'CARES Act business interest, excess business losses, '
                                            'NOLs and QIP bonus; a §172(b)(1)(H) carryback '
                                            'election; §108(i) discharge-of-indebtedness and OID '
                                            'deferral.',
                       'state_treatment': 'Decoupled and reported on Form 500DM alongside the '
                                          'items above, through the same pro forma mechanism.',
                       'authority_source_code': 'MD_2025_FORM_500DM',
                       'notes': "⚠ §12 CORRECTION: Form 500DM cites 'Technical Bulletin No. 38', "
                                "WHICH DOES NOT EXIST — the Comptroller's complete legal library "
                                '(176 documents) holds 52 technical bulletins and none is number '
                                '38. The real document is ADMINISTRATIVE RELEASE NO. 38, '
                                "'Decoupling from Federal Income Tax Laws' (library date 6/9/2022, "
                                'PDF revised 8/11/2025). AR 38 does not itself contain the CARES '
                                'scenarios — it forwards to Tax Alert 07-24 and, for NOLs, to '
                                'Administrative Release 18; pull all three for the 500DM spec. ⚠ '
                                'OPEN ITEM 8 — STATUTE/FORM MISMATCH ON THE NOL CARRYBACK PERIOD: '
                                "§10-210.1(b)(2) decouples from a §172(b)(1)(H) election 'for a "
                                "carryback period of up to 5 YEARS'; the FINAL TY2025 Form 500DM "
                                "describes the same item as 'a carryback period of up to 2 YEARS "
                                "(Farming loss only).' Both read verbatim; the divergence is "
                                'unexplained and MUST BE SETTLED before the 500DM spec is '
                                'written.'}],
  'notes': '⚠ MECHANISM: Maryland decoupling runs through PRO FORMA FEDERAL RETURNS reported on '
           "Form 500DM — 'Separate (pro forma) federal and Maryland returns must be prepared for "
           "use in completing Form 500DM,' and the pro formas 'are not to be filed with the "
           "Comptroller of Maryland or the IRS.' It is NOT a percentage add-back (contrast NC's "
           '85%/20%-over-five-years). ⚠ THE MANUFACTURING CARVE-OUT IS THE HEADLINE TRAP: a '
           'taxpayer-attribute switch on the depreciation engine that no other state in this '
           'campaign has, and it appears on NO Maryland form — implement from the statute alone, '
           'with its own audit trail, and flag to Ken at Gate 1. PTE mechanics: a PTE makes NO '
           'adjustment on its own Form 510/511 but MUST ATTACH Form 500DM and pass each member '
           'their share of every decoupling modification with the code, via Maryland Schedule K-1 '
           '(510/511); each member then files their own 500DM (line 9). EXPLICITLY NOT DECOUPLED '
           'AND NOT FLOWING TO THE MARYLAND RETURN (BRE found no FAGI impact, so §10-108 never '
           'engages): tips (IRC §224 / P.L. 119-21 §70201), overtime pay (IRC §225 / §70202), '
           'auto-loan interest (IRC §163(h)(4) / §70203) and the additional senior deduction (IRC '
           '§151(d)(5)(C) / §70103) — these are federal below-the-line deductions from FAGI; they '
           "'do not impact the calculation of an individual's Maryland tax liability and are not "
           "reported on the Maryland return,' and they also cannot be claimed as Maryland itemized "
           'deductions. PTET: elective with a mandatory nonresident floor; TY2025 rate 8.75% on '
           "individual and fiduciary members' shares / 8.25% on entity members' shares — "
           'STATUTORILY DERIVED (§10-102.1(d)(2)(i) = §10-106.1 lowest county rate 2.25% + '
           '§10-105(a) top individual rate 6.50%), a TY2025 change from 8.00%. Owner side is a '
           'CREDIT (§10-701.1, Form 502CR Part CC Line 9) PLUS A MANDATORY ADD-BACK (Form 502 '
           "Other Additions code 'r'; corporate leg §10-306(b)(6) → §10-205(m)) — getting the "
           'credit without the add-back is the classic Maryland PTET bug. ⚠ OTHER TY2025 CHANGES '
           'that bear on the modules (transcribed for context, not conformity items): two new top '
           'brackets 6.25% / 6.50% (10 brackets total); a NEW 2% surtax on net capital gain for '
           'filers with FAGI over $350,000 (Form 502CG — and Form 504CG for FIDUCIARIES, whose '
           'threshold is FEDERAL TAXABLE INCOME over $350,000 on UNDISTRIBUTED gain, per Technical '
           'Bulletin 58); a new itemized-deduction phase-out (7.5% of FAGI over $200,000 / '
           '$100,000 MFS); and the county income tax is NO LONGER a flat per-county rate — Anne '
           'Arundel and Frederick run PROGRESSIVE LOCAL BRACKETS for TY2025, so a single '
           'local_rate lookup is wrong for 2 of the 24 jurisdictions (the bracket engine is shared '
           'by the 1040 AND 1041 modules). ⚠ OPEN ITEMS to re-pull before form specs: (7) '
           'installment-sale treatment under the 2% capital-gain surtax — TB 58 contains no '
           'installment-sale rule and §10-105(a)(3) does not either; DO NOT FILL BY INFERENCE, '
           "flag to Ken at Gate 1. (8) the NOL carryback period conflict, §10-210.1(b)(2) '5 "
           "years' vs Form 500DM '2 years (Farming loss only)'. (1) the TY2025/TY2026 MeF LOI and "
           "testing calendar is SES-only and remains the campaign's long pole for MD. (3) "
           'throwback/throwout — two independent negatives agree (COMAR 03.04.03.08 has no '
           'throwback/throwout; zero hits in the corporate booklet) but it stays flagged as '
           "'absence of a rule', not 'a rule of absence'."},
 {'jurisdiction_code': 'AZ',
  'conformity_type': 'static',
  'authority_source_code': 'AZ_HB4168_2026_CH140',
  'federal_reference_note': 'FIXED-DATE (static) conformity, re-adopted annually by legislation. '
                            'Arizona does NOT roll. The TY2025 rule is the REDESIGNATED A.R.S. '
                            '§43-105(B) as amended by H.B. 4168 (57th Leg., 2nd Reg. Sess. (2026), '
                            'Chapter 140, signed by Gov. Hobbs June 13, 2026, conformity amendment '
                            "at Sec. 12), verbatim: 'For the purposes of computing income tax "
                            'pursuant to this title, for taxable years beginning from and after '
                            'December 31, 2024 THROUGH DECEMBER 31, 2025, "internal revenue code" '
                            'means the United States internal revenue code of 1986, as amended, in '
                            'effect on January 1, 2025, including those provisions that became '
                            'effective during 2024 with the specific adoption of all retroactive '
                            'effective dates, but excluding any changes to the code enacted after '
                            'January 1, 2025 AND INCLUDING THOSE PROVISIONS OF PUBLIC LAW 119-21 '
                            'THAT ARE RETROACTIVELY EFFECTIVE DURING TAXABLE YEARS BEGINNING FROM '
                            "AND AFTER DECEMBER 31, 2024 THROUGH DECEMBER 31, 2025.' "
                            'Retroactivity, H.B. 4168 Sec. 35(A): §§42-1001, 43-105, 43-1022, '
                            "43-1041, 43-1121 and 43-1122 'apply retroactively to taxable years "
                            "beginning from and after December 31, 2024'; Sec. 35(B): §§43-1021, "
                            '43-1042, 43-1073.01, 43-1074.01 and 43-1168 apply retroactively only '
                            'to taxable years beginning from and after December 31, 2025. ⚠ '
                            "§43-105(A) — IRC in effect JANUARY 1, 2026, 'BUT EXCLUDING ANY "
                            "CHANGES TO THE CODE ENACTED AFTER JANUARY 1, 2026' — is the TY2026 "
                            'definition and MUST NOT be applied to TY2025.',
  'summary': 'Arizona is a STATIC (fixed-date) conformity state that re-adopts the IRC annually. '
             "For TY2025 the answer is NEITHER 'January 1, 2025' NOR 'January 1, 2026' — it is a "
             'HYBRID: the IRC in effect January 1, 2025, excluding changes enacted after that '
             'date, PLUS ONLY those provisions of OBBBA (P.L. 119-21) that are RETROACTIVELY '
             'EFFECTIVE during TY2025 (§43-105(B), as amended by H.B. 4168, Ch. 140, signed '
             '2026-06-13, retroactive to tax years beginning after 12/31/2024). OBBBA is therefore '
             'PARTIALLY ADOPTED, and adopted BY CATEGORY RATHER THAN BY ENUMERATED LIST. ⚠ Arizona '
             'runs OPPOSITE bonus-depreciation regimes in the same tax year: individuals '
             'effectively CONFORM to §168(k) (§43-1021(11) add-back + §43-1022(17)(e) full-§168(k) '
             'subtraction); corporations DECOUPLE (§43-1121(4) add-back + §43-1122(20) subtraction '
             'computed as if the §168(k)(7) election out had been made). §168(n) qualified '
             'production property has NO Arizona add-back for TY2025 for either entity type — the '
             'add-backs begin TY2026. Arizona has NO §179 modification anywhere in its four '
             "modification sections ('rule says no'), so the applied §179 limit follows the "
             'conformity IRC — and THAT NUMBER IS AN OPEN GATE-1 ITEM, deliberately not stated '
             'here.',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation — INDIVIDUALS: conform (net zero, '
                               'two live lines)',
                       'federal_treatment': 'Federal bonus depreciation allowance under IRC '
                                            '§168(k), included in the §167(a) depreciation '
                                            'deduction.',
                       'state_treatment': 'EFFECTIVE FULL CONFORMITY. Addition, A.R.S. '
                                          "§43-1021(11): 'The amount of any depreciation allowance "
                                          'allowed pursuant to section 167(a) of the internal '
                                          "revenue code to the extent not previously added' (i.e. "
                                          'back out the entire federal depreciation deduction). '
                                          'Subtraction, A.R.S. §43-1022(17)(e), for property '
                                          'placed in service in taxable years beginning from and '
                                          "after December 31, 2016: 'an amount equal to the "
                                          'depreciation allowable pursuant to section 167(a) … as '
                                          'computed as if the additional allowance for '
                                          'depreciation had been THE FULL AMOUNT ALLOWED PURSUANT '
                                          "TO SECTION 168(k)'. The add-back and the subtraction "
                                          'are computed on the same figure, so the net effect is '
                                          'conformity — but this is STILL TWO LIVE LINE ITEMS ON '
                                          'THE RETURN, NOT A NO-OP: Form 140 requires the addition '
                                          'and the subtraction to be stated separately (Form 140 '
                                          'line 26 subtraction; AZDOR procedure ITP 16-2).',
                       'authority_source_code': 'AZ_ARS_43_1022',
                       'notes': "UNCHANGED by H.B. 4168 — verified against the enrolled bill's "
                                'Sec. 15 text of §43-1022, where paragraph 17(e) appears without '
                                'strike-through. Disposition true-up for individuals at '
                                "§43-1022(18): Form 140 instructions describe it as allowing 'a "
                                'subtraction for the difference in basis for any asset for which '
                                "bonus depreciation has been claimed on the federal return.'"},
                      {'item': 'IRC §168(k) bonus depreciation — CORPORATIONS: decouple',
                       'federal_treatment': 'Federal bonus depreciation allowance under IRC '
                                            '§168(k), included in the §167(a) depreciation '
                                            'deduction.',
                       'state_treatment': "DECOUPLED. Addition, A.R.S. §43-1121(4): 'The amount of "
                                          'any depreciation allowance allowed pursuant to section '
                                          "167(a) … to the extent not previously added.' "
                                          "Subtraction, A.R.S. §43-1122(20): 'An amount equal to "
                                          'the depreciation allowable pursuant to section 167(a) … '
                                          'for the taxable year computed as if THE ELECTION '
                                          'DESCRIBED IN SECTION 168(k)(7) of the internal revenue '
                                          'code HAD BEEN MADE for each applicable class of '
                                          'property in the year the property was placed in '
                                          "service' — §168(k)(7) is the ELECTION OUT of bonus. Net "
                                          'effect: corporations must maintain a SEPARATE ARIZONA '
                                          'DEPRECIATION SCHEDULE AND A SEPARATE ARIZONA BASIS, '
                                          'computed with bonus elected out. Disposition true-up at '
                                          '§43-1122(5).',
                       'authority_source_code': 'AZ_ARS_43_1122',
                       'notes': '⚠ ANY ENGINE THAT CARRIES ONE §168(k) RULE ACROSS BOTH MODULES '
                                'WILL BE WRONG FOR ONE OF THEM. UNCHANGED by H.B. 4168 — verified '
                                "against the enrolled bill's Sec. 23 text of §43-1122, where "
                                'paragraph 20 appears without strike-through despite the section '
                                'being reopened and applied retroactively to TY2025.'},
                      {'item': 'IRC §168(n) qualified production property (OBBBA) — TY2025: NO '
                               'Arizona add-back',
                       'federal_treatment': 'Special depreciation allowance for qualified '
                                            'production property under new IRC §168(n).',
                       'state_treatment': 'For TY2025 Arizona ALLOWS the §168(n) allowance WITH NO '
                                          'STATE ADD-BACK for either individuals or corporations. '
                                          'The add-backs H.B. 4168 creates are both expressly '
                                          'limited to taxable years beginning FROM AND AFTER '
                                          'DECEMBER 31, 2025: §43-1021(17) (individuals, H.B. 4168 '
                                          "Sec. 14) — 'FOR TAXABLE YEARS BEGINNING FROM AND AFTER "
                                          'DECEMBER 31, 2025, THE AMOUNT OF THE SPECIAL '
                                          'DEPRECIATION ALLOWANCE FOR QUALIFIED PRODUCTION '
                                          'PROPERTY ALLOWED PURSUANT TO SECTION 168(n) … TO THE '
                                          "EXTENT NOT PREVIOUSLY ADDED' — and §43-1121(25) "
                                          '(corporations, Sec. 22), identical language. Reinforced '
                                          'by Sec. 35(B), which gives §43-1021 a TY2026 '
                                          'retroactive date. From TY2026 it is added back for '
                                          'both.',
                       'authority_source_code': 'AZ_HB4168_2026_CH140',
                       'notes': '⚠ DO NOT CODE A SINGLE §168(n) RULE ACROSS BOTH YEARS. '
                                'Belt-and-braces noted on verification: §43-1021 also gets a '
                                'TY2026 retroactive date under Sec. 35(B), while §43-1121 is Sec. '
                                '35(A) (TY2025) but its paragraph 25 is self-limited to TY2026 — '
                                'same outcome, different route.'},
                      {'item': 'IRC §179 expensing — no Arizona modification exists; the TY2025 '
                               'figure was RULED by Ken 2026-08-16 (broad reading of §43-105(B)): '
                               '$2,500,000 / $4,000,000',
                       'federal_treatment': 'OBBBA increased the §179 dollar limitation and '
                                            'phase-out threshold for property placed in service in '
                                            'taxable years beginning after December 31, 2024. '
                                            '(Dollar figures intentionally omitted here — see '
                                            'state_treatment and notes.)',
                       'state_treatment': 'ARIZONA HAS NO §179 MODIFICATION. A full-text search of '
                                          'A.R.S. §§43-1021, 43-1022, 43-1121 and 43-1122 — the '
                                          "four addition/subtraction sections — and of H.B. 4168's "
                                          'amendments to all four returns NO §179 add-back or '
                                          "limit-override of any kind. This is 'RULE SAYS NO', not "
                                          "'no rule found': Arizona enumerates its modifications "
                                          'exhaustively in these sections and §179 is absent. '
                                          "Therefore Arizona's §179 limit and phaseout EQUAL THE "
                                          'FEDERAL FIGURES UNDER WHATEVER IRC VERSION APPLIES FOR '
                                          'THE YEAR, which for TY2025 routes through §43-105(B). ✅ '
                                          'RULED 2026-08-16: under the BROAD reading of §43-105(B) '
                                          "the OBBBA §179 amendments are 'retroactively effective "
                                          "during TY2025', so Arizona applies LIMIT $2,500,000 / "
                                          'PHASEOUT $4,000,000 for TY2025. Arizona is NOT frozen '
                                          'at a pre-OBBBA §179 level by its own statute — any '
                                          'freeze could only come from the conformity date, not '
                                          'from a §179-specific decoupling.',
                       'authority_source_code': 'AZ_HB4168_2026_CH140',
                       'notes': '✅ RULED BY KEN 2026-08-16 at the Tier-1 Gate-1 walk '
                                '(delvio-states/GATE1_WALK.md item 1): the BROAD reading governs → '
                                '$2,500,000 / $4,000,000 for TY2025. ⚠ THIS IS A RULING ON AN '
                                'INTERPRETIVE QUESTION, NOT A PUBLISHED ARIZONA FIGURE. AZDOR has '
                                'never published its provision-by-provision OBBBA retroactivity '
                                'mapping, and [UNVERIFIED] item 2 stands OPEN as a matter of fact. '
                                'The ruling rests on three structural arguments recorded in the '
                                "walk: (i) the legislature used the identical 'retroactively "
                                "effective' formula in §43-105(C)/(D) for TY2023/TY2024, where it "
                                'can only mean provisions reaching back before enactment; (ii) '
                                'H.B. 4168 separately hard-coded the OBBBA items that do NOT flow '
                                'through federal AGI, implying the conformity clause was expected '
                                "to carry the AGI-affecting ones; (iii) AZDOR's own 2026-01-22 "
                                "release says the forms conform 'with parts of H.R. 1 — "
                                "specifically federal adjusted gross income'. The MECHANISM (no "
                                'Arizona §179 modification) was verified independently and is not '
                                'part of the ruling. ⚠ RE-VERIFY if AZDOR ever publishes the '
                                'mapping.'}],
  'notes': "⚠⚠ THE 'ARIZONA CONFORMED TO JANUARY 1, 2026' HEADLINE THAT APPEARS IN EVERY "
           'PRACTITIONER ALERT DESCRIBES TY2026, NOT TY2025. It is §43-105(A). The TY2025 rule is '
           'the REDESIGNATED §43-105(B) hybrid — Jan 1 2025 code PLUS only those OBBBA provisions '
           "retroactively effective in TY2025. Porting that headline into a TY2025 spec is 'the "
           "single most likely way to get Arizona wrong.' ⚠⚠ OPEN [UNVERIFIED] ITEM 2 — THE "
           'HIGHEST-VALUE GAP IN THE BRIEF, AND AN EXPLICIT KEN GATE-1 JUDGEMENT CALL. The statute '
           "adopts a CATEGORY ('THOSE PROVISIONS OF PUBLIC LAW 119-21 THAT ARE RETROACTIVELY "
           "EFFECTIVE DURING [TY2025]'), not a list, so each OBBBA section must be tested against "
           "its own federal effective date. No Arizona source publishes the mapping: AZDOR's "
           "'Conformity to IRC' page's most recent entry is still '2024 Conformity' (re-fetched "
           'live 2026-08-06), the Jan 2026 AZDOR press releases address forms and amendment relief '
           'rather than provision mapping, and the Senate Fact Sheet for H.B. 4168 as enacted '
           'enumerates no OBBBA sections. Interpretive note added by the verification pass, FOR '
           'KEN, not applied here: the structure of amended §43-105 supports the BROAD reading — '
           '(i) the legislature used the identical formula in redesignated subsections (C) and (D) '
           'for TY2023/TY2024, where it can only mean provisions reaching back before enactment; '
           '(ii) H.B. 4168 separately hard-coded the OBBBA items that do NOT flow through FAGI '
           '(§§224 / 225 / 151(d)(5)(C) / 163(h)(4) are below-the-line federally), implying the '
           "conformity clause was expected to handle the FAGI-affecting ones; (iii) AZDOR's "
           "2026-01-22 release says the forms conform 'with parts of H.R. 1 — specifically federal "
           "adjusted gross income'. KEN SHOULD RULE ON BROAD-VS-NARROW AT GATE 1; IT IS A "
           'JUDGEMENT CALL, NOT A FACT THAT CAN BE PULLED. ⚠ OPEN ITEM 4 RIDES ON ITEM 2: the §179 '
           'limit and phaseout Arizona actually applies for TY2025. No figure is recorded in this '
           'row. H.B. 4168 ALSO REACHED BACK PAST TY2025: Sec. 12 amended redesignated §43-105(C) '
           "and (D) — the TY2024 and TY2023 definitions — to insert 'OF PUBLIC LAW 119-21' into "
           "their existing 'including those provisions that are retroactively effective' clauses. "
           'Out of scope for a TY2025 spec, but it is real amended-return exposure. SEQUENCING '
           "(structural, recurring): AZDOR prints each year's forms BEFORE the legislature acts on "
           'conformity and instructs taxpayers to file assuming adoption. TY2025 forms were NOT '
           'substantively reissued after H.B. 4168 (Form 120 and Form 141AZ instructions carry '
           'ModDate 2026-07-13 but a token-level diff against the 2026-06-03 Wayback capture shows '
           'the only change is one comma). §12 CORRECTION C: the individual module IS BUILDABLE — '
           'acting on Executive Order 2025-15 (2025-11-25), AZDOR routed the four Middle Class Tax '
           "Cuts Package items (tips, overtime, senior, vehicle-loan interest) through the 'Other "
           "Adjustments' catch-all on the Other Subtractions schedule (Form 140 page 6 item V — "
           "'See MCTCP worksheet'; 140PY item Y; 140NR item P), computed on a standalone non-filed "
           'MCTCP Worksheet mapping to IRS Schedule 1-A lines 13 / 21 / 30 / 37. The four are '
           'UNAVAILABLE on Forms 140A and 140EZ, and 140PY/140NR filers may subtract only tips and '
           'overtime. Penalty-safe amendment horizon per AZDOR: amend the TY2025 return by OCTOBER '
           "15, 2027. PTET: elective under A.R.S. §43-1014, rate set BY REFERENCE ('the same as "
           "the highest tax rate prescribed by section 43-1011') = 2.50% for TY2025 (Pub 713); "
           'election made annually by filing Form 165 / 120S, and may be made or revoked on an '
           'amended return within the four-year SOL; individuals, estates and trusts only, with a '
           '60-day owner opt-out. Owner side is BOTH a CREDIT (§43-1077, Form 355, NONREFUNDABLE '
           'with a five-consecutive-year carryforward) AND a mandatory ADD-BACK (Form 140 addition '
           "item 'P. Entity-Level Income Tax Payment'). Entity estimated payments required where "
           'prior-year Arizona taxable income was $150,000 OR MORE (§12 correction H: exactly '
           '$150,000 is IN, not out). OTHER RESIDUAL OPEN ITEMS: (6) nonresident '
           "distributive-share withholding — narrowed to 'no rule found', NOT 'rule says no'; (7) "
           'confirmation that no Arizona locality imposes an income tax — low risk, unconfirmed '
           'exhaustively. ⚠ The posted A.R.S. text on azleg.gov is the PRE-H.B. 4168 version (as '
           'of 2026-08-06) — read the chaptered session law, not the ARS page.'},
 {'jurisdiction_code': 'OR',
  'conformity_type': 'partial',
  'authority_source_code': 'OR_ORS_317_010_CONFORMITY',
  'federal_reference_note': 'TWO-PRONGED statutory definition, parallel in the personal and '
                            'corporate chapters (ORS 316.012; ORS 317.010(7)): the IRC as amended '
                            'and in effect "(a) On December 31, 2023; or (b) If related to the '
                            'definition of taxable income, as applicable to the tax year of the '
                            'taxpayer." Prong (b) is the "rolling reconnect" / "permanent '
                            'connection." OBBBA (P.L. 119-21, signed 7/4/2025) therefore FLOWED '
                            'INTO OREGON AUTOMATICALLY for TY2025 for everything that goes to the '
                            'definition of taxable income; provisions OUTSIDE that definition '
                            '(credits, estimated-tax mechanics, NOL rules and similar '
                            'administrative provisions) remain pinned to the 12/31/2023 IRC. HB '
                            '2092 (2025 R1), which would have temporarily disconnected the rolling '
                            "prong for TY2025, DID NOT BECOME LAW — ORS 316.012's amendment credit "
                            'line in the ORS 2025 Edition ends at 2024 c.75 §21, i.e. no '
                            '2025-session amendment to the statute at all.',
  'summary': 'Oregon is a HYBRID/partial-conformity state and the hybrid is the whole story: '
             'rolling for the federal DEFINITION OF TAXABLE INCOME, fixed-date 12/31/2023 for '
             'every other purpose. Because bonus depreciation and §179 go to the definition of '
             "taxable income, OBBBA's 100% bonus and the $2,500,000/$4,000,000 §179 figures "
             'applied in Oregon for TY2025 WITH NO ADD-BACK. ⚠ DO NOT BUILD AN OREGON BONUS '
             'ADD-BACK FOR TY2025 — nearly every peer state that decoupled has one; Oregon does '
             'not. The standing Oregon decouplings are IRC §139A, IRC §529 earnings used for K-12 '
             'tuition, and IRC §199A (structural: Oregon starts the individual return at federal '
             'AGI, above the §199A line). PTE-E (Form OR-21) is elective at 9% of the first '
             '$250,000 of distributive proceeds and 9.9% above.',
  'decoupled_items': [{'item': 'IRC §168(k)/(n) bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent).',
                       'state_treatment': 'CONFORMS at 100% — NO ADD-BACK FOR TY2025. Oregon '
                                          'depreciation = federal depreciation for TY2025 '
                                          'acquisitions; no separate Oregon basis is created. The '
                                          'DOR states it directly: "Federal depreciation '
                                          'disconnect [Addition code 153] ... As of the date this '
                                          'publication was last revised, Oregon had not '
                                          'disconnected from any new federal depreciation expense '
                                          'provisions for this tax year." Addition code 153 EXISTS '
                                          'but has NO TY2025 population.',
                       'authority_source_code': 'OR_2025_PUB_OR17',
                       'notes': 'VERIFIED NEGATIVE — "the rule says no disconnect," not "found '
                                'nothing." Confirmed on all three legs in the brief\'s §12.1: (a) '
                                'Pub. OR-17 (Rev. 01-29-26, ~7 months post-OBBBA) p. 91 verified '
                                "word-for-word; (b) ORS 317.301's disconnect window CLOSED in 2010 "
                                '(applicability note 2011 c.7 §31); (c) SB 1507 §10(2) applies the '
                                'new §168(k) decoupling only to "property that is placed in '
                                'service in tax years beginning on or after January 1, 2026." '
                                'Recorded as an explicit CONFORMS item rather than an omission so '
                                'no downstream author reads silence as an add-back. STALENESS: SB '
                                '1507 (2026 ch.142) creates a full dual-basis regime for TY2026 '
                                '(add-back measured against §168(k) as in effect 12/1/2017); '
                                '§168(n) is NOT decoupled — it appears zero times in the enrolled '
                                'bill.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'CONFORMS at the federal OBBBA figures via the same '
                                          'rolling tie to the definition of taxable income. OREGON '
                                          'HAS NO SEPARATE §179 DOLLAR LIMIT and no §179 add-back.',
                       'authority_source_code': 'OR_2025_PUB_OR17',
                       'notes': 'VERIFIED NEGATIVE, three ways: (a) ORS 317.301 is the only §179 '
                                'modification statute and its window is closed; (b) Pub. OR-17 p. '
                                "90's exhaustive list of situations where Oregon depreciation "
                                'differs contains no §179 cap; (c) the Schedule OR-ASC-CORP code '
                                'list (2025 Form OR-20 Instructions, Appendix A, p. 19) contains '
                                'NO §179 code — only generic Depreciation differences (addition '
                                '174 / subtraction 353) and Gain or loss on disposition of '
                                'depreciable property (addition 158 / subtraction 356).'},
                      {'item': 'IRC §168(k)/§179 deferral for tax years 2009–2010 (LEGACY, closed '
                               'window)',
                       'federal_treatment': 'Bonus depreciation and §179 as applicable to the tax '
                                            'year for assets placed in service in 2009 or 2010.',
                       'state_treatment': 'ADDITION was required for the difference between '
                                          '§168(k)/§179 as applicable to the tax year and the same '
                                          'sections as amended and in effect on December 31, 2008 '
                                          '— but ONLY for tax years beginning on or after 1/1/2009 '
                                          'and before 1/1/2011. The addition left a HIGHER Oregon '
                                          'basis that unwinds as SUBTRACTIONS over the remaining '
                                          'asset life.',
                       'authority_source_code': 'OR_ORS_317_301_DEPR',
                       'notes': 'Window CLOSED — applicability note 2011 c.7 §31: "ORS 316.739 and '
                                '317.301 apply to tax years beginning on or after January 1, 2009, '
                                'and before January 1, 2011." Creates NO current-year TY2025 '
                                'difference. SOFTWARE IMPLICATION: a legacy 2009/2010 asset can '
                                'still throw an Oregon SUBTRACTION in TY2025, so the engine needs '
                                'the per-asset Oregon-basis mechanism even though no new TY2025 '
                                'differences arise. NOL interaction: where a 2009/2010 NOL '
                                'absorbed the disallowed depreciation/expensing, later-year Oregon '
                                'subtractions are reduced by the amount already in the NOL (Pub. '
                                'OR-17 p. 88).'},
                      {'item': 'IRC §139A — federal subsidies for employer prescription drug plans',
                       'federal_treatment': 'Subsidy excluded from federal income under §139A.',
                       'state_treatment': 'NOT adopted — permanent Oregon ADDITION (ORS 317.401 / '
                                          'addition code 123). One of only two items on the '
                                          "corporate instructions' own disconnect list.",
                       'authority_source_code': 'OR_2025_PUB_OR17',
                       'notes': 'Standing Oregon exception, unrelated to OBBBA. Listed at Pub. '
                                'OR-17 p. 7 and in the OR-20 / OR-20-S / OR-20-INC disconnect list '
                                '(p. 2 of each).'},
                      {'item': 'IRC §529 earnings used for K-12 tuition',
                       'federal_treatment': 'Earnings on 529 funds used for K-12 tuition excluded '
                                            'federally.',
                       'state_treatment': 'NOT adopted — Oregon plans are HIGHER EDUCATION ONLY; '
                                          'earnings used for K-12 tuition do not get the Oregon '
                                          'exclusion.',
                       'authority_source_code': 'OR_2025_PUB_OR17',
                       'notes': 'Standing Oregon exception, unrelated to OBBBA. Pub. OR-17 p. 7.'},
                      {'item': 'IRC §199A qualified business income deduction',
                       'federal_treatment': '20% QBI deduction for noncorporate taxpayers.',
                       'state_treatment': 'NOT ALLOWED for Oregon. STRUCTURAL rather than an '
                                          'add-back: Oregon starts the individual return at '
                                          'federal ADJUSTED GROSS INCOME (Form OR-40 line 7), '
                                          'which is ABOVE the §199A line, so the deduction never '
                                          'enters the Oregon base.',
                       'authority_source_code': 'OR_2025_PUB_OR17',
                       'notes': 'Standing Oregon exception, Pub. OR-17 p. 7. Oregon layers on its '
                                'own additions/subtractions, its own Schedule OR-A itemized '
                                'deductions, and its own exemption CREDITS. Oregon has its own '
                                'separate qualified-business-income REDUCED TAX RATE (ORS 316.043; '
                                'Schedule OR-PTE-FY / Pub. OR-PTE) — do not conflate it with '
                                'federal §199A.'}],
  'notes': '⚠ THE CAT RUNS ON A DIFFERENT CLOCK. The Corporate Activity Tax (ORS ch. 317A, Form '
           'OR-CAT) is a gross-receipts tax filed ENTIRELY SEPARATELY from the income/excise '
           'return, and its IRC tie is a PURE FIXED DATE with NO rolling prong: ORS 317A.100(11), '
           'ORS 2025 Edition, reads "...as they are amended and in effect on December 31, 2023" — '
           'a flat clause, structurally unlike ORS 316.012 / 317.010(7) (credit line ends 2024 '
           'c.75 §26, proving no 2025-session change). CONSEQUENCE: CAT "cost inputs" (COGS) run '
           'on the PRE-OBBBA Code for TY2025 while the income/excise tax runs on the POST-OBBBA '
           'Code. DO NOT SHARE THE CONFORMITY FLAG BETWEEN THE TWO REGIMES. || ⚠ SOURCE CONFLICT — '
           'the single most dangerous item in the Oregon brief. The corporate instructions (2025 '
           'Form OR-20 150-102-020-1 p. 2, Form OR-20-INC 150-102-021-1 p. 2, and Form OR-20-S '
           '150-102-025-1 p. 2 — IDENTICAL wording, systemic not a typo) state the conformity rule '
           'BACKWARDS: "Oregon is tied to the federal definition of taxable income as of December '
           '31, 2023," which is precisely what prong (b) carves out. PUB. OR-17 GOVERNS — BUILD '
           'THE ROLLING PRONG (brief §12.3). Grounds: (1) the statute is dispositive and has two '
           "prongs; (2) the corporate instructions' OWN substantive disconnect list that follows "
           'the bad sentence contains exactly two items (§139A and the closed 2009–2011 ORS '
           '317.301 deferral) and NO current-year depreciation disconnect — operative content '
           'beats summary sentence; (3) recency (OR-17 Rev. 01-29-26 vs 10-14-25 / 10-27-25). A '
           'spec author reading only the OR-20 series would encode a static 12/31/2023 engine and '
           'produce a bonus add-back Oregon does not impose. CARRY THIS WARNING INTO THE RS SPEC. '
           '|| PTE-E OWNER SIDE IS A REFUNDABLE CREDIT **PLUS** A MANDATORY ADDBACK — BOTH, and '
           'this is the field most often mis-ported. (1) Individual PTE members are allowed a '
           'REFUNDABLE CREDIT for their distributive share of the tax paid by the PTE (interest '
           'and penalties excluded); (2) members MUST report an ADDITION for any ORS ch. 314 taxes '
           'paid to Oregon that were deducted on a federal return filed by the PTE at the entity '
           'level — because Oregon starts from federal AGI, the entity-level federal deduction '
           'would otherwise reduce Oregon income twice; (3) a later-year SUBTRACTION for a PTE-E '
           'refund included in federal income where the addition was reported in the prior year. '
           'Not a deduction, not an exclusion. PTE-E rate is two-tier: 9% of the first $250,000 of '
           'distributive proceeds, 9.9% above (worksheet shortcut constant $22,500). Elective, '
           'ANNUAL, non-binding, calendar-year only; all members must be individuals (or '
           'upper-tier PTEs whose members are all individuals). Available for tax years beginning '
           'on/after 1/1/2022 and before 1/1/2028 (SB 1510 (2026) extension), with a CONTINGENT '
           'SUNSET if the federal SALT limitation expires or is repealed. || [UNVERIFIED] carried '
           'from brief §10 — 12 of the original 15 items remain open and MUST be re-pulled before '
           'Oregon form specs are authored: (3) 2025 indexed lower bracket boundaries; (4) '
           'throwback/throwout — FOUND NO RULE, not "rule says no"; (5) Form OR-19 de-minimis '
           'withholding thresholds; (6) OREGON DOR LETTER-OF-INTENT DEADLINE AND ATS WINDOW — '
           're-attacked and CONFIRMED UNOBTAINABLE from public sources; email '
           'electronic.filing@dor.oregon.gov is the only route, a KEN-ONLY lead-time-bearing '
           'action, and the Portland calibration datum (LOI sent early July, ATS opened Dec 1) '
           'says the email should go WELL BEFORE JULY; (7) individual preparer e-file mandate — '
           'FOUND NO RULE; (9) CAT 25% deficiency penalty; (10) ORS 317A.128 CAT SOURCING — '
           'deliberate gap, BLOCKS ANY OR-CAT BUILD; (11)–(15) Portland-metro local items. || KEN '
           'JUDGEMENT CALL CARRIED (brief §6a / §12.2 C-3): the CAT FILING gate conflicts — the '
           'instructions say "$1 million or more" (≥) while ORS 317A.137(1) says "in excess of $1 '
           'million" (>), and the instructions contradict themselves (line 16 "below"; the '
           'estimated-payment worksheet "equal to or less than," which matches the statute). BUILD '
           'TO THE STATUTE (>) AND FLAG THE EXACTLY-$1,000,000 BOUNDARY FOR KEN — a $250 delta and '
           'a spurious return at a round number that will occur in a real client base. || '
           'Portland-metro local income taxes (City of Portland Revenue Division) are a SECOND, '
           'INDEPENDENT MeF jurisdiction with its own LOI and ATS, and its mandatory e-file policy '
           'binds PAID PREPARERS on INDIVIDUAL returns, not just businesses (brief §12.2 C-2). '
           'Oregon = two lead-time-bearing developer programs.'},
 {'jurisdiction_code': 'MO',
  'conformity_type': 'rolling',
  'authority_source_code': 'MO_RSMO_143_091',
  'federal_reference_note': 'ROLLING conformity — §143.091 RSMo ("Meaning of terms"): any '
                            'reference to the laws of the United States means the IRC of 1986 and '
                            'amendments thereto "as the same may be or become effective, at any '
                            'time or from time to time, for the taxable year." Effective 1/1/1990, '
                            'UNAMENDED. OBBBA (P.L. 119-21) is therefore IN AUTOMATICALLY for '
                            'TY2025 with no adoption act — none was needed and none was enacted, '
                            "and the DOR's own 2025 Tax Legislative Changes lists no OBBBA "
                            'decoupling. Corroborated on the FINAL forms: MO-A Part 2 Line 9 / '
                            'Part 2 Worksheet keys to federal Schedule A Line 5d exceeding $40,000 '
                            "($20,000 MFS) — the OBBBA SALT cap — so Missouri's FINAL forms are "
                            'built on post-OBBBA federal figures.',
  'summary': 'Missouri is a ROLLING IRC conformity state building the individual return from '
             'FEDERAL AGI. TY2025 top individual rate 4.7%; flat 4% corporate rate; NO franchise '
             'tax (§147.010.1(5), none imposed for tax years beginning on/after 1/1/2016). THERE '
             'IS NO §168(k) ADD-BACK AND NO §179 MODIFICATION — OBBBA 100% bonus and the '
             '$2,500,000/$4,000,000 §179 figures flow straight through. The real TY2025 divergence '
             'is the 100% CAPITAL GAINS DEDUCTION (§143.121.3(14), HB 594/508), which applies to '
             'INDIVIDUALS ONLY for TY2025: corporations are trigger-gated until the top individual '
             'rate is ≤4.5%, and the FINAL TY2025 MO-1041 and MO-PTE carry no such line at all — '
             'FOUR MODULES, THREE ANSWERS. Missouri also keeps a FEDERAL INCOME TAX DEDUCTION for '
             'individuals and a 20% business income deduction (§143.022).',
  'decoupled_items': [{'item': 'IRC §168(k) bonus depreciation',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent).',
                       'state_treatment': 'CONFORMS — NO ADD-BACK for current-law bonus '
                                          'depreciation. The ONLY Missouri bonus provision is a '
                                          'legacy, CLOSED-WINDOW modification tied to the Job '
                                          'Creation and Worker Assistance Act of 2002, limited to '
                                          'property purchased "on or after July 1, 2002, but '
                                          'before July 1, 2003" (§143.121.2(3) addition, '
                                          '§143.121.3(7) and .3(9) subtraction). OBBBA 100% bonus '
                                          'flows straight through for BOTH individuals and '
                                          'corporations.',
                       'authority_source_code': 'MO_RSMO_143_121',
                       'notes': 'VERIFIED NEGATIVE — "rule says no add-back," not "no rule found," '
                                'and it survived a hard adversarial attack: §143.121 RSMo pulled '
                                'in FULL and searched; every §168 reference is tied to the 2002–03 '
                                'JCWAA window. Confirmed on all four FINAL TY2025 forms: MO-A Line '
                                '14; MO-1120 Line 8 (basis adjustment) and Line 10 (recovery on '
                                'sale); MO-1041 Part 1 Line 16. Recorded as an explicit CONFORMS '
                                'item rather than an omission so no downstream author reads '
                                'silence as an add-back. ⚠ DO NOT CARRY THE GEORGIA PATTERN HERE — '
                                'GA requires a §168(k) add-back; Missouri does not. RESIDUAL '
                                'MECHANIC to keep in the spec: the 2002–03 vintage add-back is '
                                'still recoverable on disposition (MO-A Line 14 checkbox; MO-1120 '
                                'Line 10) — dead for new assets but not removed from the forms.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'CONFORMS to the federal limit — NO Missouri-specific '
                                          'limit or phaseout and NO §179 modification of any kind. '
                                          'Both starting points already embed the federal '
                                          'deduction: individuals start from federal AGI, '
                                          'corporations from federal taxable income (MO-1120 Line '
                                          '1). Missouri applies the federal OBBBA figures by '
                                          'default and is NOT frozen at a pre-OBBBA level.',
                       'authority_source_code': 'MO_RSMO_143_121',
                       'notes': 'VERIFIED NEGATIVE — §143.121 RSMo pulled in full: ZERO '
                                'occurrences of the string "179." The depreciation modifications '
                                "address §168 only. Georgia's §179 posture required a separate "
                                "ruling; Missouri's needs none."},
                      {'item': '100% capital gains deduction — §143.121.3(14) RSMo (HB 594 / HB '
                               '508, 2025)',
                       'federal_treatment': 'Capital gains included in federal income '
                                            '(preferential rates only).',
                       'state_treatment': 'MISSOURI SUBTRACTS 100% — BUT FOR INDIVIDUALS ONLY IN '
                                          'TY2025. §143.121.3(14)(a): "For all tax years beginning '
                                          'on or after January 1, 2025, one hundred percent of all '
                                          'income reported as a capital gain for federal income '
                                          'tax purposes BY AN INDIVIDUAL SUBJECT TO TAX PURSUANT '
                                          'TO SECTION 143.011." (b) extends it to entities taxed '
                                          'under §143.071 only "beginning on or after January '
                                          'first of the tax year following the tax year in which '
                                          'the top rate of tax imposed pursuant to section 143.011 '
                                          'is equal to or less than four and one-half percent" — a '
                                          'trigger NOT met for TY2025. FOUR MODULES, THREE ANSWERS '
                                          '(all four legs independently confirmed on the FINAL '
                                          'forms in §12.1): INDIVIDUAL = YES (MO-A Part 1 Line 18 '
                                          '"Capital Gain," 100%, negative → $0, sourced from '
                                          'federal Line 7a); CORPORATE = NO (MO-1120 subtraction '
                                          'lines enumerated end-to-end; the only capital-gain item '
                                          'is Line 6, low-income-housing exclusion); FIDUCIARY = '
                                          'NO (MO-1041 subtractions Lines 2–5; only Line 3, 25% '
                                          'low-income-housing); PTE = NO LINE ON THE FORM (MO-PTE '
                                          'Page 3 Part A Subtractions is a CLOSED enumerated list, '
                                          'Lines 6–11, totalled at Line 12).',
                       'authority_source_code': 'MO_RSMO_143_121',
                       'notes': '§12 CONFIRMED both statutory legs verbatim and confirmed the '
                                'DOR\'s own statement: "This subtraction is effective for '
                                'individuals starting January 1, 2025. This subtraction will be '
                                'effective for corporations starting January 1st of the tax year '
                                'following the reduction of the individual income tax to 4.5%" '
                                '(MO_2025_TAX_LEG_CHANGES). The four-module split is the '
                                'HIGHEST-RISK item in the Missouri spec and it survived '
                                'adversarial checking intact. ⚠ KEN JUDGEMENT CALL / GATE-1 WALK '
                                'ITEM (brief §12.4) — see the row-level notes: statute-vs-form '
                                "conflict on whether an electing MO-PTE's base gets this "
                                'subtraction. MO-A Line 18 reads federal Line 7a (CORRECTED in '
                                '§12.2 from "Line 7" — real spec impact). Related but distinct MO '
                                'capital-gain subtractions that must not be conflated with this '
                                'one: low-income-housing (25% fiduciary / corporate exclusion), '
                                'ESOP 50%, and the §143.121.6(2) beginning-farmer farmland TIERED '
                                'subtraction on MO-A Line 21 (100% of the first $2M, then '
                                '80/60/40/20% per $1M; 21A Sold / 21B Rented-Leased / 21C '
                                'Crop-Shared).'},
                      {'item': 'Federal NOL deduction — excessive carryback / carryforward',
                       'federal_treatment': 'Federal NOL deduction as allowed under the IRC, '
                                            'including carryback and carryforward periods.',
                       'state_treatment': 'DECOUPLED — §143.121.2(4) RSMo requires an ADDITION for '
                                          'any federal NOL deduction "carried back more than two '
                                          'years or carried forward more than twenty years." '
                                          'Implemented on MO-A Part 1 Line 2 ("NOL – Excessive '
                                          'Carryback/Carryforward … enter that NOL deduction '
                                          'amount as a positive number") and reversed later on '
                                          'MO-1120 Line 9.',
                       'authority_source_code': 'MO_RSMO_143_121',
                       'notes': 'Added by the verification pass as a MATERIAL OMISSION from the '
                                'draft (§12.3 item 2). Missouri is NOT fully conformed on business '
                                'deductions — rolling conformity does not mean zero '
                                'modifications.'}],
  'notes': '⚠ KEN JUDGEMENT CALL — GATE-1 WALK ITEM, STILL OPEN, CLIENT-ADVICE-BEARING (brief §10 '
           'item 1, upgraded by §12.4 from "no line found" to a documented STATUTE-vs-FORM '
           'CONFLICT). LEG 1, the FORM SAYS NO: MO-PTE Page 3 Part A Subtractions is a closed '
           'enumerated list (Lines 6–11) with no capital-gain line, in instructions reissued '
           '2026-01-08 — AFTER the 2025 session that created §143.121.3(14); the Department had '
           'every opportunity to add a line and did not. LEG 2, the STATUTE ARGUABLY SAYS YES: '
           '§143.436.3(1) (partnerships) and .4(1) (S corps) define the PTE base as "increased or '
           'decreased by any modification made pursuant to sections 143.121 and 143.141 that '
           "relates to an item of the affected business entity's income, gain, loss, or "
           'deduction" — and the 100% capital gain subtraction IS a §143.121 modification. LEG 3, '
           'the COUNTER-ARGUMENT: §143.121.3(14)(a) is limited by its own terms to gain reported '
           '"by an INDIVIDUAL subject to tax pursuant to section 143.011," and an affected '
           'business entity is not an individual; reinforcing this, §143.436.3(1) lifts exactly '
           'ONE owner-level item to the entity level by name (the §143.022 business income '
           'deduction) and the Department implemented THAT one with a dedicated line and schedule '
           '(MO-PTE Line 6 / Schedule PTE-BD). PRACTICAL CONSEQUENCE, which stands on the form as '
           'issued: an electing MO-PTE pays 4.7% on capital gains that would have been 100% EXEMPT '
           "on the owner's MO-1040, recovered only as a NON-REFUNDABLE credit against a liability "
           'the exemption would have eliminated — SO FOR GAIN-HEAVY MISSOURI OWNERS THE PTET '
           'ELECTION CAN BE AFFIRMATIVELY WORSE THAN NOT ELECTING, the inverse of the usual '
           'planning default. DISPOSITION: build the PTE base TO THE FORM (no subtraction), gate '
           'the planning advice, DO NOT ENCODE EITHER ANSWER AS AN ASSUMPTION. Settled only by a '
           'DOR FAQ/letter ruling on the §143.121.3(14) / §143.436.3(1) interaction or a direct '
           'answer from DOR PTE staff (pteincome@dor.mo.gov, (573) 751-4541). || THE FEDERAL '
           'INCOME TAX DEDUCTION SURVIVES FOR INDIVIDUALS — Missouri is one of the few states with '
           'one, and it is a real computation, not a rounding item. It is a '
           'PERCENTAGE-OF-FEDERAL-TAX deduction keyed to MISSOURI AGI (MO-1040 Line 6), '
           'CLIFF-STYLE, verbatim from the FINAL MO-1040 Line 12 chart: $25,000 or less → 35%; '
           '$25,001–$50,000 → 25%; $50,001–$100,000 → 15%; $100,001–$125,000 → 5%; $125,001 or '
           'more → 0%. HARD CAP $5,000 individual / $10,000 married filing combined (confirmed '
           'twice: form Line 13 and narrative p. 8). Fiduciaries take it via Form 5802 Part 1 Line '
           '8b. || PTET (SALT Parity Act, §143.436) is 4.7% for TY2025 (MO-PTE Line 10), ELECTIVE '
           'and ANNUAL but IRREVOCABLE WITHIN THE YEAR; owner side is a NON-REFUNDABLE CREDIT with '
           'UNLIMITED CARRYFORWARD (Form MO-TC alpha code SPA, supported by federal K-1 or Form '
           '5889) — note §143.436.10 gives corporate and fiduciary members the credit too (applied '
           'AFTER all other credits), while the RECIPROCAL out-of-state credit under §143.436.9(2) '
           'has NO carryforward at all: two credits, two carryforward rules, easy to conflate. '
           'Member OPT-OUT is new for TY2025 (MO-PTENR nonresident / MO-PTE Opt-Out resident), '
           'available where the un-extended deadline is on or after 8/28/2025, and once filed it '
           'applies to ALL SUBSEQUENT YEARS until revoked. MO-PTE apportions on Form MO-MS PTE — a '
           'THIRD apportionment form distinct from MO-MS (C-corp) and MO-MSS (S-corp) (CORRECTED '
           'in §12.2). || §143.022 20% BUSINESS INCOME DEDUCTION — absent from the draft entirely '
           'and it hits TWO modules (§12.3 item 1): individual MO-A Part 1 Line 17 with its own '
           'worksheet (20% of Missouri-source net profit from Sch C + Sch E Part 2 + Sch F + Form '
           '4835, less agricultural disaster relief), and PTE MO-PTE Line 6 computed at entity '
           'level on SCHEDULE PTE-BD, where "the resulting deduction may be more or less than" the '
           'aggregate owner-level amount. || MARRIED FILING COMBINED IS MANDATORY — "Missouri law '
           'requires a combined return for married couples filing together" — with Y/S columns end '
           'to end and tax computed separately at Lines 30Y/30S: TWO PARALLEL TAX COMPUTATIONS ON '
           'ONE RETURN. || APPORTIONMENT CORRECTION (§12.2 item 2): "no throwback/throwout" is '
           'true of the RECEIPTS FACTOR (zero "throwback" hits across all 63 pp. of 12 CSR 10-2) '
           'but FALSE of the ALLOCATION rules — §143.455.7(2)(b) throws capital gains on tangible '
           'personal property back to Missouri where commercial domicile is here and the taxpayer '
           'is not taxable in the situs state, and §143.455.9(1)(b) does the same for '
           'patent/copyright royalties. Real spec impact for the C-corp and PTE modules. || '
           '[UNVERIFIED] still open (brief §12.5) — (1) the MO-PTE capital-gain interaction above; '
           '(3) whether OBBBA BELOW-THE-LINE deductions (qualified tips, qualified overtime, '
           'senior deduction, auto-loan interest) reduce Missouri income: NO published DOR '
           'position, so this remains "NO RULE FOUND," NOT "rule says no" — the structural '
           'derivation (Missouri starts from federal AGI and picks up federal deductions through '
           'exactly two channels, MO-1040 Line 14 and MO-A Part 2 Line 1 from federal Line 12e, '
           'neither of which reaches them) is high-confidence but is a mechanical read of the '
           'return, not a DOR statement, and THE FLAG STAYS; (5) the DOR software-developer '
           'approval calendar — page re-fetched 2026-08-06, publishes NO dates; the e-file LOI, '
           'schemas and test documents sit behind FTA State Exchange System access requiring an '
           'email to elecfile@dor.mo.gov. TWO HUMAN GATES WITH UNKNOWN TURNAROUND, KEN-ONLY, '
           'LEAD-TIME-BEARING — START EARLY. || SCOPE BOUNDARY: the Kansas City and St. Louis 1% '
           'EARNINGS TAXES are city-administered, ride on neither the MO-1040 nor DOR MeF, and '
           'MUST NOT be built into the state modules. || TY2026 STALENESS LANDMINES ALREADY '
           'ENACTED: §143.121.3(15) specie-legal-tender capital gain subtraction (HB 754); and SB '
           '98 / HB 754 change how RESIDENT ESTATES AND TRUSTS compute Missouri taxable income and '
           "the other-state credit (§§143.081, 143.341) — THE FIDUCIARY MODULE'S STARTING POINT "
           'AND OTHER-STATE CREDIT CHANGE FOR TY2026.'},
 {'jurisdiction_code': 'MS',
  'conformity_type': 'partial',
  'authority_source_code': 'MS_CODE_27_7_17',
  'federal_reference_note': 'NO GENERAL IRC CONFORMITY STATUTE AND NO CONFORMITY DATE — confirmed '
                            'by verified absence across five sections (§§27-7-9, 27-7-15, 27-7-17, '
                            '27-7-26, 27-7-27). Miss. Code Ann. §27-7-17 grants deductions from '
                            "Mississippi's OWN list and reaches into the IRC only where the "
                            'Legislature says so, PROVISION BY PROVISION. The hooks are MOSTLY '
                            'ROLLING (undated "Internal Revenue Code of 1986" / "as amended" / "in '
                            'effect for that year" references — §179, entertainment expenses, '
                            'passive activity and rental real estate, employee pension '
                            'contributions, the WHOLE individual itemized-deduction amount, the '
                            '§27-7-15 gross-income exclusions, the §27-7-9 nonrecognition '
                            'provisions, §27-7-27(2) UBTI); only THREE DEFINITIONS ARE FROZEN AT '
                            '1/1/2021 (§168(k) qualified property, §168(e)(6) QIP, §174 specified '
                            'R&E); and a few items are expressly rejected (NOLs, capital-gain '
                            'character, installment sales). OBBBA (P.L. 119-21) therefore applies '
                            'ONLY where a Mississippi provision points at the current federal rule '
                            '— no blanket adoption, no blanket rejection. The four FINAL TY2025 '
                            'DOR booklets contain NO OBBBA conformity notice; their '
                            'legislative-changes pages list only Mississippi bills.',
  'summary': 'Mississippi is NOT a conformity state in the ordinary sense — selective, '
             'provision-by-provision. ⚠ DO NOT CODE A FEDERAL BONUS ADD-BACK: Mississippi runs its '
             'OWN PERMANENT 100% BONUS DEPRECIATION under §27-7-17(1)(f)(ii)2, independent of IRC '
             '§168(k), with "qualified property" and QIP defined as of 1/1/2021, ELECTIVE and '
             'IRREVOCABLE — with ONE exception, AVIATION ASSETS, which DO conform to federal bonus '
             'rates and are the single place OBBBA §168(k) reaches Mississippi cost recovery. §179 '
             'is the one ROLLING cost-recovery item ("in effect for that year"), and Mississippi '
             'PUBLISHES NO §179 DOLLAR FIGURE of its own. Two rate schedules run concurrently: '
             'individuals and fiduciaries at 0% / 4.4% over $10,000; corporations, composite '
             'filers and electing PTEs at the untouched 0% / 4% / 5%. The individual return is '
             'BUILT FROM SCRATCH (Form 80-105 never imports federal AGI), while the fiduciary '
             'return reconciles from federal Form 1041.',
  'decoupled_items': [{'item': "IRC §168(k) bonus depreciation — Mississippi's own parallel 100% "
                               'regime',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent).',
                       'state_treatment': 'DOES NOT CONFORM — Mississippi runs a PARALLEL, '
                                          'PERMANENT, ELECTIVE 100% BONUS OF ITS OWN: "For the '
                                          'purpose of computing income tax for tax years beginning '
                                          'after December 31, 2022, expenditures for business '
                                          'assets that are qualified property or qualified '
                                          'improvement property shall be eligible for one hundred '
                                          'percent (100%) bonus depreciation and may be deducted '
                                          'as an expense incurred by the taxpayer during the tax '
                                          'year during which the property is placed in service, '
                                          'NOTWITHSTANDING ANY CHANGES TO FEDERAL LAW RELATED TO '
                                          'COST RECOVERY beginning on January 1, 2023, or on any '
                                          'other date. A taxpayer may alternatively treat the '
                                          'depreciation of such business assets in accordance with '
                                          'the schedule provided in 26 USCS Section 168." '
                                          'DEFINITIONS FROZEN AT JANUARY 1, 2021: "qualified '
                                          'property" = §168(k) as it existed 1/1/2021; "qualified '
                                          'improvement property" = §168(e)(6) as it existed '
                                          '1/1/2021 (§27-7-17(1)(f)(ii)4.a–b), both for property '
                                          'placed in service after 12/31/2022. ELECTION IS '
                                          'IRREVOCABLE "unless the commissioner specifically '
                                          'allows a change in the method," made by the return due '
                                          'date including extensions. CAP: any method or '
                                          'combination cannot exceed 100% of the cost of the '
                                          'subject property (§27-7-17(1)(f)(ii)6).',
                       'authority_source_code': 'MS_CODE_27_7_17',
                       'notes': '⚠ DO NOT CODE A GA-STYLE FEDERAL BONUS ADD-BACK. §12 verified '
                                'every element against the CURRENT CODIFIED §27-7-17, not just '
                                'enrolled HB 1733 — the 2023 text survives unamended, so the '
                                'regime is LIVE for TY2025. FORM MECHANICS the spec must get right '
                                '(2025 Form 83-100, Form 83-122 line 6 and line 13): FEDERAL FORM '
                                '4562 IS FILED TWICE — "must be completed twice and attached '
                                'immediately after Form 83-122. The first submission reflects the '
                                'deductions taken for federal income tax purposes. The second '
                                "submission should be labeled 'Mississippi' at the top of the "
                                'form." Form 83-122 LINE 6 adds back the federal special '
                                'depreciation allowance; LINE 13 recovers "the additional '
                                'depreciation expense for purposes of this state due to the basis '
                                'adjustment not being made for state purposes" — i.e. MISSISSIPPI '
                                'KEEPS A SEPARATE, UNREDUCED STATE BASIS. Election is signalled by '
                                'checkboxes at the top of Form 83-122. THE PTE ANALOGUE IS FORM '
                                '84-122 LINE 8, NOT LINE 6 — identical structure, different line '
                                'numbers between the 83- and 84- series. DOR confirmation for '
                                'TY2025: "Expenditures for business assets placed in service after '
                                'December 31, 2022, are eligible for 100% bonus depreciation" '
                                '(83-122 line 6 instructions). Enacted by HB 1733 (2023 Reg. '
                                'Sess.), signed 3/27/2023, effective from and after 1/1/2023 (MS '
                                'DOR Depreciation Notice, 10/20/2023).'},
                      {'item': 'IRC §168(k) bonus depreciation — AVIATION ASSETS (the carve-out)',
                       'federal_treatment': '100% bonus for property acquired and placed in '
                                            'service after 1/19/2025 (OBBBA, permanent).',
                       'state_treatment': 'CONFORMS TO THE FEDERAL RATE — "In the case of new or '
                                          'used aircraft, equipment, engines, or other parts and '
                                          'tools used for aviation, allowance for bonus '
                                          'depreciation CONFORMS WITH THE FEDERAL BONUS '
                                          'DEPRECIATION RATES and reasonable allowance for '
                                          'depreciation under this section is no less than one '
                                          'hundred percent (100%)." (§27-7-17(1)(f)(i))',
                       'authority_source_code': 'MS_CODE_27_7_17',
                       'notes': '⚠ QUALIFICATION ADDED BY THE VERIFICATION PASS (§12, structural '
                                'claim 1). THIS IS THE ONE PLACE OBBBA §168(k) REACHES MISSISSIPPI '
                                'COST RECOVERY DIRECTLY. Code the "MS runs its own bonus" rule as '
                                'HAVING AN AVIATION BRANCH, not as absolute — aviation assets '
                                'follow the FEDERAL rate, which under OBBBA is 100% for property '
                                'acquired and placed in service after 1/19/2025.'},
                      {'item': 'IRC §179 expensing limits',
                       'federal_treatment': '$2,500,000 limit / $4,000,000 phaseout (OBBBA).',
                       'state_treatment': 'ROLLING CONFORMITY — the one place Mississippi tracks '
                                          'current federal law on COST RECOVERY: "In any taxable '
                                          'year in which any 26 USCS Section 179 property is '
                                          'placed in service, a taxpayer may elect to treat the '
                                          'cost of such property as an expense which is not '
                                          "chargeable to a capital account... MISSISSIPPI'S "
                                          'TREATMENT OF THE DEDUCTION SHALL CONFORM TO THE '
                                          'PROVISIONS OF 26 USCS SECTION 179 IN EFFECT FOR THAT '
                                          'YEAR." (§27-7-17(1)(f)(ii)3) The OBBBA §179 limit and '
                                          'phaseout therefore apply in Mississippi for TY2025. '
                                          'MISSISSIPPI PUBLISHES NO §179 DOLLAR FIGURE OF ITS OWN '
                                          '— no §179 limit or phaseout amount appears in any of '
                                          'the four FINAL TY2025 booklets.',
                       'authority_source_code': 'MS_CODE_27_7_17',
                       'notes': '⚠ PROVENANCE OF THE APPLIED LIMIT: Mississippi publishes none. '
                                '§12 RESOLVED the applied TY2025 figures to the FEDERAL amounts — '
                                '$2,500,000 limit / $4,000,000 phaseout (SUV sub-limit $31,300) — '
                                'verified against IRS Instructions for Form 4562 (2025), '
                                'https://www.irs.gov/instructions/i4562, corroborated by Rev. '
                                'Proc. 2025-32, https://www.irs.gov/pub/irs-drop/rp-25-32.pdf — '
                                "NOT against another state's brief or firm memory. ENCODE MS §179 "
                                'AS "= FEDERAL FOR THE TAX YEAR," NEVER AS A HARDCODED NUMBER. '
                                "Georgia's figures are irrelevant here: MS reaches the same "
                                'numbers by a rolling statutory adoption, GA by a separate '
                                'conformity bill — DO NOT CROSS-REFERENCE THE TWO. §12 CORRECTION: '
                                'the draft\'s "zero hits for 179 / no §179 line" is FALSE — Form '
                                '84-132 (Mississippi Schedule K-1) BOX 13 reads "Enter the '
                                "owner's share of MISSISSIPPI SECTION 179 DEDUCTION. Attach a copy "
                                'of the federal Form 4562," so Mississippi computes a §179 amount '
                                'DISTINCT from the federal one (MS apportionment and MS basis '
                                'differ) and passes it through on the MS K-1. (No §179 line on '
                                'Form 83-122 or 84-122 itself — that part stands; the individual, '
                                'corporate and fiduciary booklets do return zero hits, the PTE '
                                'booklet does not.) SCOPE CORRECTION: §179 is the one rolling item '
                                'ON COST RECOVERY, not the one rolling item in Mississippi law — '
                                'see federal_reference_note.'},
                      {'item': 'IRC §174 specified research or experimental expenditures',
                       'federal_treatment': 'Federal amortization/capitalization of specified R&E '
                                            'under §174.',
                       'state_treatment': 'DECOUPLED AND PERMANENTLY FAVORABLE — "a taxpayer may '
                                          'treat specified research or experimental expenditures '
                                          '... as expenses that are not chargeable to the capital '
                                          'account. Such expenditures so treated shall be allowed '
                                          'as an immediate deduction. Such expenditures shall '
                                          'remain allowable as a full and immediate expense '
                                          'deduction in the year in which the expenses are '
                                          'incurred NOTWITHSTANDING ANY CHANGES TO THE FEDERAL '
                                          'INTERNAL REVENUE CODE related to the depreciation of '
                                          'such specified research or experimental expenditures." '
                                          'Elective and irrevocable; the alternative is the §174 '
                                          'schedule. "Specified research or experimental '
                                          'expenditures" is defined by §174 AS IT EXISTED JANUARY '
                                          '1, 2021.',
                       'authority_source_code': 'MS_CODE_27_7_17',
                       'notes': '§27-7-17(1)(f)(ii)1 and 4.c (HB 1733, 2023). One of the THREE '
                                'definitions frozen at 1/1/2021 — the freeze reaches only these '
                                'three, nothing else. Elected via the same checkboxes at the top '
                                'of Form 83-122 / 84-122.'},
                      {'item': 'Net operating losses',
                       'federal_treatment': 'Federal NOL rules and carryover periods under the '
                                            'IRC.',
                       'state_treatment': 'EXPRESSLY DOES NOT CONFORM — "Mississippi does not '
                                          'conform to federal net operating loss rules." The '
                                          'Mississippi NOL is 2 YEARS BACK / 20 YEARS FORWARD, not '
                                          'the federal period.',
                       'authority_source_code': 'MS_2025_83_100_INSTR',
                       'notes': 'Identical sentence in the 2025 Form 83-100 (Rev. 01/26) and the '
                                '2025 Form 84-100 (Rev. 01/26); 2 back / 20 forward at 2025 Form '
                                '83-100 p. 9. MS NOL carryover/carryback is deducted at Form '
                                '84-122 line 34 BEFORE the electing-PTE income subject to tax at '
                                'line 35.'},
                      {'item': 'Character of capital gains',
                       'federal_treatment': 'Capital gain character preserved; preferential '
                                            'federal treatment.',
                       'state_treatment': 'DOES NOT CONFORM — "Mississippi Law does not conform to '
                                          'federal with respect to the tax treatment of capital '
                                          'gains; therefore, THE GAIN IS TAXED AS ORDINARY '
                                          'INCOME."',
                       'authority_source_code': 'MS_2025_84_100_INSTR',
                       'notes': '2025 Form 84-100, Form 84-132 Box 9b instructions; same sentence '
                                'at 2025 Form 81-100, Form 81-132 Box 4b.'},
                      {'item': 'Installment sales',
                       'federal_treatment': 'Federal installment-sale reporting under IRC §453.',
                       'state_treatment': 'DOES NOT CONFORM — "Mississippi does not follow federal '
                                          'rules concerning installment sales."',
                       'authority_source_code': 'MS_2025_83_100_INSTR',
                       'notes': '2025 Form 83-100 p. 8. Same page: the extraterritorial income '
                                'exclusion is NOT adopted and must be added back BEFORE '
                                'apportionment.'},
                      {'item': 'Individual nonbusiness itemized deductions (rolling federal hook)',
                       'federal_treatment': 'Federal itemized deductions as amended by OBBBA, '
                                            'including the $40,000 SALT cap ($20,000 MFS).',
                       'state_treatment': 'ADOPTED BY ROLLING REFERENCE, LESS FIVE NAMED MS '
                                          'CARVE-OUTS — §27-7-17(3)(a): "The amount allowable for '
                                          'individual nonbusiness itemized deductions FOR FEDERAL '
                                          'INCOME TAX PURPOSES where the individual is eligible to '
                                          'elect, for the taxable year, to itemize deductions on '
                                          'his federal return except the following: (i) The '
                                          'deduction for state income taxes paid or other taxes '
                                          'allowed for federal purposes in lieu of state income '
                                          'taxes paid; (ii) ... gaming losses; (iii)–(iv) ... '
                                          'taxes collected by gaming establishments; (v) ... '
                                          'gender transition procedures." This is an UNDATED, '
                                          'ROLLING adoption of the WHOLE federal '
                                          'itemized-deduction amount.',
                       'authority_source_code': 'MS_2025_80_100_INSTR',
                       'notes': '⚠ §12 CORRECTION #4 — the draft called the SALT cap "one '
                                'confirmed OBBBA flow-through," implying an isolated hook. IT IS '
                                'NOT ISOLATED: EVERY OBBBA change to federal itemized deductions '
                                'flows into Form 80-108 Schedule A AUTOMATICALLY. IMPLEMENTING '
                                'ONLY THE $40,000 SALT CAP AND TREATING THE REST OF SCHEDULE A AS '
                                'STATIC WOULD BE WRONG. The one flow-through DOR calls out '
                                'explicitly: "Note: Per the One Big Beautiful Bill Act, there is a '
                                '$40,000 limitation ($20,000 if married filing separately) on this '
                                'deduction" — 2025 Form 80-100 (Rev. 12/25), Schedule A '
                                'instructions, Lines 3a–3c (Taxes Paid), citing §27-7-17(3)(a)(i). '
                                'That OBBBA note appears EXACTLY ONCE across all four booklets. '
                                'Statutory hook read from the current codified §27-7-17(3)(a) '
                                '(Findlaw mirror, stamped current as of 1/1/2025) — FLAGGED FOR '
                                'RE-PULL from the official Mississippi Code. MS standard deduction '
                                '(§27-7-17(3)(b)): $4,600 MFJ / $2,300 MFS / $3,400 single — and '
                                'the $12,000 on the Form 80-105 MFS box is the COMBINED couple '
                                'amount ($6,000 + $2,300 each on separate returns).'}],
  'notes': 'TWO RATE SCHEDULES RUN CONCURRENTLY — this will break a ported spec. §27-7-5(1)(a) '
           'levies 0% / 4% / 5% on "every resident individual, corporation, association, trust or '
           'estate"; §27-7-5(1)(b)(i)–(ii) then reduces the rate FOR INDIVIDUALS ONLY. Verified on '
           'both statute and forms: INDIVIDUALS 0% on the first $10,000 and 4.4% above (2025 Form '
           '80-100 Rev. 12/25); FIDUCIARIES 0% / 4.4% (2025 Form 81-100 Schedule of Tax '
           'Computation p. 11 — the statutory bridge is §27-7-27(1) plus §27-7-35(2), "any '
           'fiduciary required to make returns shall be subject to all the provisions of this '
           'article which apply to individuals"); CORPORATIONS 0% on the first $5,000, 4% on the '
           'next $5,000, 5% over $10,000 (2025 Form 83-100); COMPOSITE FILERS AND ELECTING PTEs on '
           'the SAME unreduced 0/4/5 (2025 Form 84-100 p. 7, in two places) — a partnership or S '
           'corp is not an "individual." HB 1 (2025) LEFT TY2025 UNTOUCHED — "For calendar year '
           '2025 ... four and four-tenths percent (4.4%)" carries no strike-through; HB 1\'s cuts '
           'start at CY2027 (3.75%), and 2026 = 4% comes from the pre-existing HB 531 (2022) '
           'schedule. §27-7-5(4) fiscal-year proration applies. || FRANCHISE TAX ON CAPITAL IS '
           'LIVE AND TY-KEYED — REPEALED 1/1/2028, so the rate MUST be TY-keyed, never constant. '
           '§27-13-5(1)(a)(ix): 75¢ per $1,000 of capital over $100,000 for tax years beginning '
           'on/after 1/1/2025 and before 1/1/2026; (x) 50¢ for 2026; (xi) 25¢ for 2027; NOTHING '
           "THEREAFTER. §27-13-5(1)(b): $25 MINIMUM. DOR's printed phase-out table ($2.00 in 2020 "
           '→ $0.25 in 2027 → repealed 2028) matches the statute step for step. §12 CORRECTION: '
           '"no franchise tax on partnerships" is NOT absolute — §27-13-5(1)(a) and §27-13-7(1)(a) '
           'reach a "partnership TREATED AS A CORPORATION under the income tax laws or '
           'regulations"; further exemptions are fee-in-lieu, the Growth & Prosperity Act, and '
           'exempt organizations, and fee-in-lieu projects use a SINGLE SALES FACTOR for franchise '
           'apportionment. || THE PTET ELECTION IS BINDING FOR ALL LATER YEARS, NOT ANNUAL — "The '
           'election shall be binding for the taxable year and all subsequent taxable years unless '
           'the election is revoked by the electing PTE" (confirmed at three levels: HB 1691 '
           '§1(1)(b), the current codified §27-7-26(1)(b), and 2025 Form 84-100 p. 22). It is made '
           'on FORM 84-381 filed on paper or via TAP, NOT by checking a box on the return — "Once '
           'the Pass-Through Entity Return is filed, it cannot be amended to make a pass-through '
           'entity election." Revocation is also on Form 84-381. Requires a VOTE at the entity\'s '
           'own governance threshold (absent one, >50% of voting control AND the governing body). '
           'Window: "at any time during the tax year ... or by the due date of the return for that '
           'tax year, or by the date such return is filed, whichever is latest" (codified '
           '§27-7-26(1)(b); DOR\'s booklet adds "or the extended due date," administratively MORE '
           'generous). FIDUCIARIES MAY NOT ELECT. The return is Form 84-105 with the "Electing '
           'Pass-Through Entity" box checked, Form 84-381 and every MS K-1 (Form 84-132) attached. '
           'OWNER SIDE IS A CREDIT — the owner REPORTS the income AND takes the credit, never '
           'excludes it: §12 CORRECTION #5 found the draft had quoted SUPERSEDED 2022 enrolled '
           'text ("shall not be liable for the tax"), which is GONE from the codified section and '
           'replaced by "such share SHALL BE USED IN COMPUTING THE TAXPAYER\'S GROSS INCOME TAX '
           'LIABILITY," with excess credits "carried forward as an overpayment or refunded AT THE '
           'ELECTION OF SUCH PERSON." The credit sits in the PAYMENTS block, not the credits block '
           '— Form 80-105 line 26, between estimates (25) and total payments (28), fed from Form '
           '80-161 line 3D (businesses use Form 84-161). Owner basis is computed AS IF NO ELECTION '
           'WERE MADE. Tiering works without an upper-tier election. Estimates required if annual '
           'liability > $200. || §12 CORRECTION — MISSISSIPPI HAS A SALES-FACTOR THROWBACK RULE '
           '(highest-impact correction; the draft recorded "no rule found"). It lives in the '
           'ADMINISTRATIVE CODE, not on any form or in any booklet: 35 Miss. Admin. Code Pt. 3, '
           'Subpt. 08, Ch. 06 §402.09(3)(b)(ii) and (vii) — a sale is a Mississippi sale if the '
           'property "is shipped from an office, store, warehouse, factory, or other place of '
           'storage in this state AND THE TAXPAYER IS NOT TAXABLE IN THE STATE OF THE PURCHASER." '
           'Drop-shipment throwback at (viii); primary rule is destination; U.S. Government sales '
           'carved out; "sales" includes business interest and dividends and only the GAIN on '
           'capital-asset sales. || THE INDIVIDUAL RETURN IS BUILT FROM SCRATCH — Form 80-105 has '
           'ZERO references to federal AGI or Federal Form 1040 anywhere on the form (total income '
           'line 49 → Mississippi AGI line 66), while the FIDUCIARY return RECONCILES FROM FEDERAL '
           'FORM 1041. Two different scaffolds. || [UNVERIFIED] / open (brief §12): '
           'COMPOSITE-RETURN RATE — a genuine statute-vs-booklet conflict, not settleable from '
           'public sources; DOR states 0/4/5 in two independent places and the line 6 instructions '
           "do carry a TY2025-keyed rate; RECOMMENDATION RECORDED: follow DOR's 0%/4%/5% AS A "
           'FLAGGED CONSTANT and ask DOR. MeF handbook / LOI / ATS window CONFIRMED UNPUBLISHED — '
           '"letter of intent" appears ZERO times on either current DOR e-file page and the sole '
           'support was a TY2019 handbook on a third-party mirror, so the LOI claim is DOWNGRADED '
           'to unconfirmed; requires an email to efile@dor.ms.gov (Ken-only, lead-time-bearing). '
           'LOCAL INCOME TAXES — no affirmative preemption authority located; the "FOUND NO RULE, '
           'not rule says no" framing is RETAINED DELIBERATELY, do NOT upgrade it. OBBBA '
           'tips/overtime — no DOR guidance exists either way, and this is now HIGHER priority '
           'given the rolling itemized-deduction hook; because MS builds its own gross income, a '
           'federal deduction of that kind would not automatically reach the MS return, but '
           'nothing is published. §27-7-3 still not pulled. || ⚠ MIRROR DEPENDENCY — the franchise '
           "rate ladder, §27-7-26, §27-7-17's current codified status, the fiduciary rate chain "
           'and the throwback rule were all read from FINDLAW / CORNELL LII MIRRORS because '
           'law.justia.com, regulations.justia.com and sos.ms.gov/adminsearch all returned HTTP '
           '403. Both mirrors are stamped current as of 1/1/2025 and the substance is internally '
           'consistent with the official DOR PDFs, but PER CAMPAIGN RULES THESE MUST BE RE-PULLED '
           'FROM THE OFFICIAL MISSISSIPPI CODE AND ADMINISTRATIVE CODE BEFORE SPECS ARE AUTHORED. '
           'Tooling note: www.dor.ms.gov serves an incomplete TLS chain — WebFetch fails; PDFs '
           'need a direct HTTP client (curl -k).'},
 {'jurisdiction_code': 'LA',
 'conformity_type': 'rolling',
 'authority_source_code': 'LA_RS_47_CONFORMITY',
 'federal_reference_note': 'ROLLING, with NO conformity date anywhere in the income-tax chapters. R.S. '
                           "47:287.701(A) defines federal law as the IRC 'as amended'; corporate net income "
                           'starts from FEDERAL TAXABLE INCOME (47:287.65) and individual from FEDERAL AGI '
                           '(47:293(1)). OBBBA (P.L. 119-21, enacted 7/4/2025) is therefore IN for TY2025 by '
                           'flow-through, and no LDR OBBBA pronouncement exists either way (a recorded '
                           'negative, not an assumption). THE ONE DELIBERATE EXCEPTION TO ROLLING: the state '
                           'full-expensing election statutes (R.S. 47:287.744 corporate / 47:297.25 '
                           'individual-fiduciary) freeze THEIR OWN IRC references at 1/1/2024; that freeze '
                           'governs the election definitions only, NOT the federal starting point.',
 'summary': 'Rolling conformity; flat rates across the board for TY2025 (individuals/estates/trusts/electing '
            'PTEs 3%, corporations 5.5%); corporate FRANCHISE tax repealed effective 1/1/2026 (last period '
            '2025, reported on the 2024 CIFT-620 - the TY2025 corporate return is renamed CIT-620 and '
            'carries no franchise schedules). NO federal bonus-depreciation add-back exists. PTE owner-side '
            'relief is an EXCLUSION, not a credit, and reaches individuals/estates/trusts only. TY2026 is a '
            'cliff for S corporations (Act 382).',
 'decoupled_items': [{'item': 'IRC 168(k) bonus depreciation',
                      'federal_treatment': 'IRC 168(k) bonus depreciation flows into federal taxable income '
                                           '/ AGI',
                      'state_treatment': 'CONFORMS - NO add-back. Louisiana has no 168(k) decoupling; OBBBA '
                                         '100% bonus flows through. Established AFFIRMATIVELY: R.S. '
                                         '47:287.71 additions contain no depreciation item and all four '
                                         'TY2025 booklets grep clean. A widely-circulated secondary source '
                                         '(Bloomberg Tax) states the opposite and is WRONG on the primary '
                                         'sources.',
                      'authority_source_code': 'LA_RS_47_CONFORMITY',
                      'notes': 'DO NOT code a Georgia-shaped add-back for Louisiana. This is the single most '
                               'likely wrong port.'},
                     {'item': 'IRC 179 expensing',
                      'federal_treatment': 'IRC 179 expensing at the federal limit for the year',
                      'state_treatment': 'CONFORMS BY SILENCE - zero modification lines across all four '
                                         "TY2025 booklets. Encode as '= federal for the tax year'; no "
                                         'Louisiana figure exists.',
                      'authority_source_code': 'LA_RS_47_CONFORMITY',
                      'notes': 'Never a Louisiana constant, never a frozen number.'},
                     {'item': 'State elective 100% expensing (R.S. 47:287.744 / 47:297.25)',
                      'federal_treatment': 'Federal cost recovery over the asset life',
                      'state_treatment': 'ADDS AN ELECTIVE STATE-ONLY 100% EXPENSING REGIME on top (R.S. '
                                         '47:287.744 / 47:297.25, Acts 5 and 11 of 2024 3ES; IRC definitions '
                                         'frozen 1/1/2024), with a SUBSEQUENT-YEAR add-back of federal '
                                         'depreciation ONLY on property the taxpayer chose to state-expense '
                                         '(47:287.744(C)(3)). Requires Form R-90158.',
                      'authority_source_code': 'LA_RS_47_CONFORMITY',
                      'notes': 'RED-DEFERRED in the specs: Form R-90158 has NO PUBLISHED PDF ANYWHERE as of '
                               '2026-08-22 (both LDR forms indexes, LDR site search and a web-wide sweep '
                               'returned nothing), despite being named as a required attachment in five '
                               'TY2025 booklets and RIB 25-012. Re-check before any app build.'},
                     {'item': 'Net operating loss (IRC 172)',
                      'federal_treatment': 'Federal NOL under IRC 172',
                      'state_treatment': 'LOUISIANA HAS ITS OWN REGIME - federal 172 is INOPERATIVE. '
                                         'Utilization capped at 72% of Louisiana net income; carryforward '
                                         'INDEFINITE (R.S. 47:287.86).',
                      'authority_source_code': 'LA_RS_47_CONFORMITY',
                      'notes': 'CIT-620 line 1C1.'},
                     {'item': 'Federal income tax deduction',
                      'federal_treatment': 'Federal deduction for income taxes paid (historically deductible '
                                           'on the LA return)',
                      'state_treatment': 'REPEALED - the federal income tax deduction is GONE from TY2022 '
                                         'onward (R.S. 47:293(4) repealed by Act 395 of 2021; corporate '
                                         'parallel Act 396). No FIT plumbing exists anywhere on the TY2025 '
                                         'forms.',
                      'authority_source_code': 'LA_RS_47_CONFORMITY',
                      'notes': 'A spec ported from a pre-2022 Louisiana return would look for a line that no '
                               'longer exists.'}],
 'notes': 'TRANSCRIBED from the VERIFIED conformity/la_conformity.md (adversarial pass 2026-08-22; its '
          "Verification section governs). Seeded 2026-08-22 alongside the LA form specs under Ken's direct "
          'seed approval (campaign D-17). || ORDERING NOTE: campaign D-8 requires a state conformity row to '
          'PRECEDE its form specs. For Louisiana that order was INVERTED - the forms seeded first and '
          'exported a NULL state_conformity block until this row landed minutes later. Recorded rather than '
          'tidied away, because the same inversion will recur for any state that was never a Tier-1 '
          'conformity subject. || TY2026 IS A RE-AUTHORING EVENT, NOT A CONSTANT BUMP: four acts pivot at '
          '1/1/2026 - Act 6 (franchise repeal), Act 5 (CIT 5.5%), Act 11 (3%), and ACT 382, which flips S '
          'CORPORATIONS to INFORMATION filers with new Schedules K/L plus a composite, ENDS the S-corp '
          'exclusion, and BARS the PTE election for S-corp composite filers. || VINTAGE TRAP: the CURRENTLY '
          'CODIFIED R.S. 47:287.732 is ALREADY the Act 382 rewrite - the TY2025 S-corp exclusion text is '
          'GONE from current law, so TY2025 authority is the CIT-620i booklet and the pre-Act-382 text, NOT '
          'a fresh statute pull. || OPEN: whether an ELECTING PTE may take the Schedule F line 3f $20,000 '
          'standard deduction (the printed test names corporations subject to R.S. 47:287.11, while '
          '47:287.732.2(B) taxes the electing entity at the INDIVIDUAL rate instead - evidence against '
          'eligibility, but no instruction addresses it either way). Current LDR MeF developer gates also '
          'unresolved (the 2018 handbook is confirmed current).'}]
