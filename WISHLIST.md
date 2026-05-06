# WISHLIST

Living, append-only list of **known data sources that look promising but have not yet been captured by this project**. The complement to `briefs/`: this file holds raw "things we know exist" before they become structured opportunity briefs.

## Rules

- Both the operator and `maximizer` may **append** entries. Only the operator may delete; maximizer marks entries `dismissed` instead.
- Maximizer must append a wishlist entry whenever it identifies a candidate source while reading signal digests, even if it doesn't immediately turn it into a brief. The wishlist is the durable surface area of "things we know exist"; the brief corpus is just the subset deemed worth committing to.
- Status values:
  - `backlog` — default for new entries.
  - `promoted-to-candidate` — set when a real brief has been created in `briefs/candidates/`. Set `promoted_to: <brief_id>`.
  - `dismissed` — operator (or maximizer with a clear hard-constraint trigger) determined the source isn't worth pursuing. Set `dismissed_reason` so the same entry isn't re-promoted later.
- Entries `backlog` for >90 days should be surfaced for operator review during a `wishlist hygiene` synthesis pass; do not auto-dismiss.
- Hard constraints from `CONSTRAINTS.md` apply: do not append entries whose capture would require auth-bypass, ToS/robots/rate-limit violations, or DDOS-grade load.
- Lane hints are speculative. They are not authoritative — the brief assigns the real lane during scoring.
- **Promoted entries are stubs.** Once an entry is `promoted-to-candidate`, the canonical detail (`why_interesting`, `known_constraints`, `estimated_size`, `rate_limit_notes`) lives in the brief file. The wishlist retains only metadata + status to keep this file tractable. To recover full pre-promotion context for a promoted entry, see the brief at `briefs/candidates/<promoted_to>.md` or git history of this file.
- **Dismissed entries are stubs too.** The full `dismissed_reason` and revisit triggers live in `docs/wishlist-dismissals.md` (loaded on demand, not via `@`-import). Each dismissed entry here carries `dismissed_reason_ref` (path + anchor) and a one-line `dismissed_summary`. **Read `docs/wishlist-dismissals.md` before re-promoting a dismissed source or evaluating a candidate that overlaps with a dismissed precedent.** When dismissing a new entry, append the full reasoning to `docs/wishlist-dismissals.md` and leave only the stub here.

## Sources

```yaml
sources:
  # ───────── Promoted to candidate (stubs; full detail in briefs/candidates/) ─────────

  - id: njdot_511_cameras
    title: "New Jersey DOT Traffic Camera Images (511NJ)"
    url: https://www.511nj.org
    discovered: 2026-05-04
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.360-20260504-njdot-511-cameras

  - id: usgs_nws_flood_fusion
    title: "USGS Stream Gauge × NWS Storm Events Cross-source Fusion"
    url: https://waterdata.usgs.gov/nwis/iv
    discovered: 2026-05-04
    lane_hint: 4   # re-categorized from 3 on 2026-05-04 under CONSTRAINTS §5
    status: promoted-to-candidate
    promoted_to: 07.695-20260504-usgs-nws-flood-fusion
    promoted_to_history:
      - 07.771-20260504-usgs-nws-flood-fusion (Lane 3 → Lane 4 under CONSTRAINTS §5)

  - id: us_transit_gtfsrt_smaller_agencies
    title: "US Transit GTFS-Realtime Vehicle Positions — Smaller-Agency Aggregation"
    url: https://gtfs.org/realtime/
    discovered: 2026-05-04
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 06.701-20260504-us-transit-gtfsrt-smaller-agencies

  - id: cslb_ca_contractor_disciplinary_corpus
    title: "California CSLB Contractor Disciplinary Actions — Structured Extraction Corpus"
    url: https://www.cslb.ca.gov/About_Us/Library/Disciplinary_Actions/
    discovered: 2026-05-04
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 07.009-20260504-cslb-ca-contractor-disciplinary-corpus

  - id: multi_state_medical_board_enforcement
    title: "Multi-State Medical Board Enforcement Actions — Cross-State Entity-Resolved Corpus"
    url: https://www.fsmb.org/physician-profile/
    discovered: 2026-05-04
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.892-20260504-multi-state-medical-board-enforcement

  - id: usda_aphis_animal_welfare_inspections
    title: "USDA APHIS Animal Welfare Act Inspection Reports"
    url: https://efile.aphis.usda.gov/PublicSearchTool/
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.805-20260505-usda-aphis-animal-welfare-inspections

  - id: ferc_elibrary_regulatory_filings
    title: "FERC eLibrary Energy Regulatory Filings — Structured-Extraction Corpus"
    url: https://elibrary.ferc.gov/eLibrary/search
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 07.006-20260505-ferc-elibrary-regulatory-filings

  - id: faa_notams_aviation_alerts
    title: "FAA NOTAMs (Notice to Air Missions) — Continuous Ephemeral Capture"
    url: https://notams.aim.faa.gov/notamSearch/
    discovered: 2026-05-05
    lane_hint: 1
    status: graduated
    promoted_to: 07.898-20260505-faa-notams-aviation-alerts
    approved: 2026-05-05
    graduated: 2026-05-05
    graduated_to: /home/runner/faa-alerts

  - id: osha_enforcement_inspection_corpus
    title: "DOL/OSHA Enforcement Inspection Records & Violation Data"
    url: https://www.osha.gov/enforcement
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.723-20260505-osha-enforcement-inspection-corpus

  - id: multi_state_insurance_dept_enforcement
    title: "Multi-State Insurance Department Enforcement Orders"
    url: https://www.dfs.ny.gov/industry_guidance/enforcement_actions
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.483-20260505-multi-state-insurance-dept-enforcement

  - id: epa_echo_enforcement_corpus
    title: "EPA ECHO Federal Enforcement & Compliance Corpus"
    url: https://echo.epa.gov/tools/data-downloads
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.608-20260505-epa-echo-enforcement-corpus

  - id: msha_mine_safety_enforcement_corpus
    title: "MSHA Mine Safety Enforcement, Citations & Fatality Reports"
    url: https://www.msha.gov/data-and-reports/statistics
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.470-20260505-msha-mine-safety-enforcement-corpus

  - id: nlrb_unfair_labor_practice_cases
    title: "NLRB Unfair Labor Practice Cases & Board Decisions"
    url: https://www.nlrb.gov/cases-decisions/cases
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.802-20260505-nlrb-unfair-labor-practice-cases

  - id: txdot_drivetexas_cameras
    title: "TxDOT Live Traffic Cameras via DriveTexas.org"
    url: https://drivetexas.org/
    discovered: 2026-05-05
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.216-20260505-txdot-drivetexas-cameras

  - id: uspto_patent_claim_citation_corpus
    title: "USPTO Patent Grant Corpus — Claim Graphs, Inventor ER & Citation Network"
    url: https://data.uspto.gov/
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.911-20260505-uspto-patent-claim-citation-corpus

  - id: cra_exam_narrative_corpus
    title: "CRA Performance Evaluation Exam Reports — Multi-Regulator Narrative Extraction"
    url: https://www.occ.gov/topics/consumers-and-communities/community-development/cra-performance-evaluations/
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 07.274-20260505-cra-exam-narrative-corpus

  - id: bis_export_enforcement_corpus
    title: "BIS/OEE Export Enforcement Orders & Denial Notices"
    url: https://www.bis.gov/enforcement/oee
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 07.315-20260505-bis-oee-export-enforcement-corpus

  - id: ftc_consumer_antitrust_enforcement_corpus
    title: "FTC Consumer Protection & Antitrust Enforcement Cases"
    url: https://www.ftc.gov/legal-library/browse/cases-proceedings
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 07.063-20260505-ftc-consumer-antitrust-enforcement-corpus

  - id: hud_fheo_fair_housing_enforcement
    title: "HUD FHEO Fair Housing Enforcement Cases"
    url: https://www.hud.gov/program_offices/fair_housing_equal_opp
    discovered: 2026-05-05
    lane_hint: 2
    status: promoted-to-candidate
    promoted_to: 06.799-20260505-hud-fheo-fair-housing-enforcement

  - id: caltrans_quickmap_cameras
    title: "Caltrans Traffic Cameras via QuickMap"
    url: https://quickmap.dot.ca.gov/
    discovered: 2026-05-05
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.139-20260505-caltrans-quickmap-cameras

  - id: wsdot_traffic_cameras
    title: "WSDOT Traffic Cameras — Mountain Pass & Puget Sound Corridors"
    url: https://wsdot.wa.gov/travel/real-time/traffic-cameras
    discovered: 2026-05-05
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 06.997-20260505-wsdot-traffic-cameras

  - id: multi_state_attorney_bar_discipline
    title: "Multi-State Attorney Bar Disciplinary Actions"
    url: https://www.calbar.ca.gov/Attorneys/Discipline/Discipline-Charges-Decisions
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.499-20260505-multi-state-attorney-bar-discipline

  - id: odot_tripcheck_cameras
    title: "Oregon DOT Traffic Cameras via TripCheck"
    url: https://www.tripcheck.com/
    discovered: 2026-05-05
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.279-20260505-odot-tripcheck-cameras

  - id: sec_enforcement_structured_corpus
    title: "SEC Enforcement Actions — Structured Litigation Release & AP Corpus"
    url: https://www.sec.gov/litigation/
    discovered: 2026-05-05
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 07.509-20260505-sec-enforcement-structured-corpus

  - id: fdot_fl511_cameras
    title: "Florida DOT Traffic Camera Images (FL511)"
    url: https://fl511.com
    discovered: 2026-05-06
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.283-20260506-fdot-fl511-cameras

  - id: multi_state_pharmacy_board_enforcement
    title: "Multi-State Pharmacy Board Enforcement Actions — Cross-State Entity-Resolved Corpus"
    url: https://www.pharmacy.ca.gov/enforcement/
    discovered: 2026-05-06
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.907-20260506-multi-state-pharmacy-board-enforcement

  # ───────── Dismissed (full reasoning in docs/wishlist-dismissals.md) ─────────
  # Stubs only here — read docs/wishlist-dismissals.md before re-promoting any of these
  # or evaluating a candidate that overlaps with a dismissed precedent.

  - id: ndbc_realtime_buoys
    title: "NOAA NDBC Real-time Buoy Observation Files"
    url: https://www.ndbc.noaa.gov/data/realtime2/
    discovered: 2026-05-04
    lane_hint: 1
    status: dismissed
    promoted_to: briefs/rejected/00.000-20260504-ndbc-realtime-buoys.md
    dismissed_reason_ref: docs/wishlist-dismissals.md#ndbc_realtime_buoys
    dismissed_summary: "NDBC's own /data/swden/ and /data/historical/swden/ preserve the same :10/:40 spectral cadence; CONSTRAINTS §5 → Defensibility=0."

  - id: coops_ais_coastal_fusion
    title: "NOAA CO-OPS Tide Gauge × AIS Vessel Position Coastal Fusion"
    url: https://api.tidesandcurrents.noaa.gov
    discovered: 2026-05-04
    lane_hint: 3
    status: dismissed
    dismissed_reason_ref: docs/wishlist-dismissals.md#coops_ais_coastal_fusion
    dismissed_summary: "Both inputs publicly archived with timestamps (CO-OPS historical API + NOAA MarineCadastre AIS bulk); join reconstructible → §5."

  - id: dc_capital_bikeshare_gbfs
    title: "Capital Bikeshare (DC) GBFS Real-time Bike & Station Status"
    url: https://gbfs.lyft.com/gbfs/1.1/dca-cabi/gbfs.json
    discovered: 2026-05-04
    lane_hint: 1
    status: dismissed
    dismissed_reason_ref: docs/wishlist-dismissals.md#dc_capital_bikeshare_gbfs
    dismissed_summary: "Multi-operator fusion thesis collapsed: 1 of 5 DDOT operators viable; CaBi-only is materially smaller and partly overlaps with CaBi's quarterly trip dumps."

  # ───────── Backlog (new entries pending operator review) ─────────

  - id: gdot_ga511_cameras
    title: "Georgia DOT Traffic Camera Images (511GA)"
    url: https://www.511ga.org/
    discovered: 2026-05-06
    lane_hint: 1
    status: promoted-to-candidate
    promoted_to: 07.141-20260506-gdot-ga511-cameras

  - id: multi_state_real_estate_commission_enforcement
    title: "Multi-State Real Estate Commission Disciplinary Actions — Cross-State Entity-Resolved Corpus"
    url: https://www.dre.ca.gov/Licensees/EnforcementActions.html
    discovered: 2026-05-06
    lane_hint: 4
    status: promoted-to-candidate
    promoted_to: 06.914-20260506-multi-state-real-estate-commission-enforcement

  - id: adot_az511_cameras
    title: "Arizona DOT Traffic Camera Images (AZ511)"
    url: https://az511.gov/list/cameras
    discovered: 2026-05-06
    lane_hint: 1
    why_interesting: |
      Fills the I-10 Tucson–Phoenix–Nogales gap between TxDOT's El Paso coverage and the Pacific
      corridor (Caltrans). Nogales POE is the #2 commercial land border crossing in the US by truck
      volume — cross-border supply chain intelligence is a direct buyer vertical. AZ also covers
      I-19 (Tucson→Nogales), I-17 (Phoenix→Flagstaff), and SR-51/I-10 Phoenix metro freight
      corridors. Camera JPEGs served via CDN; no upstream historical archive found (same archetype
      as NJDOT/TxDOT/Caltrans/WSDOT). Distinct buyer thesis: maquiladora supply chain, produce
      imports (Nogales is #1 US fresh produce POE by value), automotive parts (Sonora/Hermosillo
      plant nexus).
    known_constraints: |
      robots.txt (2026-05-06): Selective Disallow — blocks /list/GetData/ and /list/getdata/
      (AJAX camera-metadata API), /my511/, /map/map*, /bundles/, /eventdetails/, /error/.
      Camera image delivery paths NOT blocked. Brief-stage: confirm image URLs are accessible
      without calling the blocked /list/GetData/ endpoint (camera IDs derivable from HTML or
      alternate public path). No ToS prohibition on archival found. HTTP 200 on az511.gov and
      az511.com (2026-05-06).
    estimated_size: "<1 GB/day (est. ~500–800 cameras, ~1 frame/min, ~20 KB/frame)"
    rate_limit_notes: "No published rate limit found; TTL/refresh cadence ~60s per camera standard for AZ511"
    status: backlog
    promoted_to: null
    dismissed_reason: null

  - id: multi_state_ag_consumer_protection
    title: "Multi-State Attorney General Consumer Protection Enforcement Actions — Cross-State Entity-Resolved Corpus"
    url: https://oag.ca.gov/
    discovered: 2026-05-06
    lane_hint: 4
    why_interesting: |
      50 state AGs independently enforce consumer protection, antitrust, data privacy, and
      environmental law — a corpus structurally parallel to multi-state-medical-board but with
      a broader buyer vertical (corporate compliance, risk, insurance, competitive intelligence).
      Distinct from the FTC brief (federal enforcement only); state AGs file cases the FTC does
      not and vice versa. No free public comprehensive multi-state AG consumer enforcement database
      exists; NAAG publishes press releases, not structured case data. LexisNexis/Westlaw cover
      AG enforcement commercially ($50k+/year) — paid precedent confirming buyer willingness.
      Lane-4 three pillars: (1) OCR + NER + structured extraction across 50 heterogeneous state
      portals; (2) ongoing weekly/monthly compounding as new actions are filed; (3) cross-state
      entity resolution of defendant company and individual names across divergent state naming
      conventions.
    known_constraints: |
      Primary sources: individual state AG websites (oag.ca.gov, texasattorneygeneral.gov,
      ag.ny.gov, etc.) — all HTTP 200 (2026-05-06). CA AG robots.txt: no blocking of enforcement
      pages (2026-05-06). NAAG (naag.org) HTTP 301→200, robots.txt blocks /wp-content/uploads/CPDB/
      (PDF upload dir) only — HTML pages not blocked. Brief-stage: per-state robots.txt audit
      required (same methodology as multi-state-medical-board). Raw enforcement PDFs/HTML are
      publicly posted; §5 applies to raw input, not the derived structured corpus.
    estimated_size: "<5 GB/year (PDFs + structured extraction; ~50 states × ~200 actions/year avg)"
    rate_limit_notes: "No published rate limits; polite crawl (Crawl-delay: 10 where specified) sufficient"
    status: backlog
    promoted_to: null
    dismissed_reason: null
```

## How to append

```yaml
- id: <short_snake_case_id>            # stable, used for promoted_to refs
  title: "<human title>"
  url: <primary url>
  discovered: YYYY-MM-DD
  discovered_by: operator              # operator | maximizer (optional)
  lane_hint: <1..5 or null>            # speculative
  why_interesting: |
    Why this might be a moat. One paragraph max.
  known_constraints: |
    Auth, rate limits, robots.txt, ToS notes, anything you noticed.
  estimated_size: "<rough storage rate, e.g., 2 GB/day>"
  rate_limit_notes: "<published or inferred>"
  status: backlog                      # backlog | promoted-to-candidate | dismissed
  promoted_to: null
  dismissed_reason: null
```

When an entry is promoted to a candidate brief, compress this file's entry to a stub (id/title/url/discovered/lane_hint/status/promoted_to). The brief file is the canonical home for the rich detail going forward.

## Notes for the operator — dismissal precedents

These are sources considered and dismissed during discovery synthesis, kept here so future passes don't re-evaluate them from scratch. **Iteration narratives** (what was added when, which calibrations fired) live in `FOCUS.md` "Recently completed" and `.wolf/memory.md` — not duplicated here.

### Hard-constraint hits (CONSTRAINTS §1/§2)

- **PurpleAir** (purpleair.com) — robots.txt `Disallow: /` (2026-05-04).
- **511VA / VDOT 511** (511va.org) — robots.txt `Disallow: /` (2026-05-04).
- **Bay Area 511 API** (api.511.org) — robots.txt `Disallow: /` (2026-05-04).
- **Lime DC GBFS** (data.lime.bike) — robots.txt `Disallow: /` (2026-05-04).
- **HHS OIG CMP cases** (oig.hhs.gov) — robots.txt `Disallow: /*.pdf` blocks the PDF narratives that anchor any Lane-4 thesis. LEIE bulk CSV remains accessible but is §5-killed standalone.

### Akamai-edge UA gating (federal regulatory agencies)

These return HTTP 403 to standard UAs. Apply the 3-step polite-alternate-path checklist before final dismissal (CONSTRAINTS Discovery section + cerebrum 2026-05-05). Confirmed gated:

- **FAA Aircraft Registry** (registry.faa.gov) — alternate-path search exhausted; also fails §5 (daily ReleasableAircraft.zip is the bulk archive).
- **DOL Wage and Hour Division** (dol.gov/agencies/whd) — data.dol.gov has no parallel WHD endpoint to the OSHA one. Revisit if added.
- **PHMSA** (phmsa.dot.gov) — all 3 alternate paths returned 403 (data.gov empty, FOIA reading room, direct subpath).
- **FFIEC CRA portal** (ffiec.gov) — **partial alternate-path success**: OCC + Fed member-agency paths return 200, enabling the `cra_exam_narrative_corpus` brief without ffiec.gov direct access.
- **CPSC** (cpsc.gov) — Akamai 403 + data.gov bulk mirror exists (NEISS, recall data) → dual §2/§5 dismissal.
- **DOL WARN** (federal level) — Akamai 403 at federal aggregator; multi-state WARN aggregation is a plausible Lane-4+5 brief but requires a dedicated 50-state per-portal discovery pass; file fresh if scoped.

### §5 reconstructibility kills (data is publicly archived elsewhere)

- **regulations.gov** — durably archived by regulations.gov + National Archives.
- **NJ Judiciary public-access portal** — court-records retention law preserves every filing.
- **NYC Council Legistar** — Legistar IS the system of record (preservation is the platform's purpose).
- **City of Chicago Open Data 311** — Socrata-backed full historical archive.
- **AC Transit live GTFS-RT** — folded into the surviving `us_transit_gtfsrt_smaller_agencies` entry.
- **CSLB live license-status snapshot (Lane-1 reframe)** — folded into the surviving `cslb_ca_contractor_disciplinary_corpus` Lane-4 entry.
- **CMS Hospital Price Transparency MRFs** — Dolthub free public aggregator + commercial competitors (Turquoise, Serif). Revisit if a specific value-add over Dolthub is named.
- **NHTSA ODI vehicle-defect complaints (FLAT_CMPL.zip)** — full historical depth, refreshed within 72h. Revisit if NLP-derived-feature thesis is named.
- **OFAC SDN list** — Treasury maintains historical-versions archive. Cross-jurisdiction ER (UN+EU+UK OFSI) might be a Lane-4 brief; file fresh.
- **CDC FluView** — gis.cdc.gov publishes historical CSVs at native cadence; WHO FluNet mirrors globally.
- **NOAA GHCN-Daily** — fully archived (NCEI, data.gov, Wayback).
- **NIFC/IRWIN active wildfire perimeters** — final perimeters archived (USFS FSHED), satellite detections (NASA FIRMS) continuous.
- **BLM oil/gas/grazing lease auction results** — full historical depth on blm.gov + data.gov.
- **CFPB Consumer Complaint Database** — data.gov bulk dataset reconstructible. Revisit if CFPB stops publishing bulk to data.gov while keeping API live.
- **USPTO PTAB decisions** — durably archived; commercial market well-served.
- **SEC EDGAR risk-factor extraction** — multiple free academic analogs (Stanford OpenEDGAR, ND Risk Factor DB).
- **FMCSA SAFER/SMS** — data.gov bulk available. Surviving angle: chameleon-carrier ER; file fresh if scoped.
- **NOAA SDR** (sdrs.faa.gov / drs.faa.gov) — Lane-1 fails; archived by FAA back to ~2008.

### Reachability/format issues (dismissed pending environment changes)

- **Helbiz, Spin DC GBFS** — operator/feed retired (504, 404).
- **Lyft scooters DCA S3** — stale since 2023-08-17.
- **FCC ULS** — UA-block timeouts + weekly bulk dumps already archived.
- **Coast Guard MISLE** (homeport.uscg.mil) — SSL cert expired (2026-05-05); FOIA-only at full historical depth.
- **NRC Event Notifications** (nrc.gov) — environment-level connection refused (2026-05-05); revisit from a different network.
- **USACE LPMS lock passage** (ndc.ops.usace.army.mil) — connection refused; revisit to confirm ephemerality.
- **Illinois DOT cameras** (gettingaroundillinois.com) — camera page URL 404 after site restructuring; revisit when canonical path identified.
- **Colorado DOT COTRIP, Nevada DOT** — overlap with existing TX/CA/UT coverage; deferred unless a specific buyer thesis surfaces.

### Lane-3 dismissal track record

7 candidate fusions evaluated across 4 discovery passes; **0 survived** the §5 reconstructibility test. Common pattern: both inputs publicly archived with timestamps → join reconstructible → moat is Lane-4 (compute) or Lane-1 (capture the ephemeral input directly). Full list and reasoning in `LANES.md` "Lane-3 discovery track record" section. Operative rule: when contemplating a Lane-3 brief, first verify at least one input is genuinely ephemeral and not already covered by an existing Lane-1 ingestor.
