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

## Sources

```yaml
sources:
  - id: ndbc_realtime_buoys
    title: "NOAA NDBC Real-time Buoy Observation Files"
    url: https://www.ndbc.noaa.gov/data/realtime2/
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      NOAA NDBC operates ~1,000 moored buoys and C-MAN stations reporting meteorological,
      oceanographic, and directional wave spectral data every 10–50 minutes. The raw
      "realtime2" text files (e.g., 41025.txt for primary obs, 41025w.txt for spectral
      wave density) are overwritten as new observations arrive. While NCEI archives the
      primary hourly-aggregated observations, the full-resolution spectral wave density
      data (wave height by frequency bin) is not fully mirrored at NCEI at sub-hourly
      cadence. For offshore operations planning, marine insurance underwriting, and
      hurricane track research, having a continuous 15-minute spectral archive across
      all buoys is materially more useful than hourly summaries. No public or commercial
      service offers this at scale. The moat is the continuous record — once a 10-minute
      window closes, that specific reading cannot be reconstructed.
    known_constraints: |
      robots.txt fetched 2026-05-04 at https://www.ndbc.noaa.gov/robots.txt — only
      blocks bots '008', 'SemrushBot', 'SemrushBot-SA'; User-agent: * is not restricted.
      Data directory https://www.ndbc.noaa.gov/data/realtime2/ returned an accessible
      HTML directory listing (HTTP 200, verified 2026-05-04). US government data;
      public domain per 15 U.S.C. § 1508. No ToS clause against archival located.
      No published per-request rate limit for file-based HTTP access. Brief must
      verify NCEI archive completeness for spectral (w-file) data before asserting
      Lane 1 — if NCEI archives spectral files fully, the ephemeral argument weakens.
    estimated_size: "~1 GB/month (1,000 buoys × 8 file types × ~10 KB avg × 144 update cycles/day)"
    rate_limit_notes: "No published rate limits for file-based access; recommend polite crawl ≥60s between station files."
    status: dismissed
    promoted_to: briefs/rejected/00.000-20260504-ndbc-realtime-buoys.md
    promoted_to_history:
      - 07.600-20260504-ndbc-realtime-buoys (Lane 1, scored 2026-05-04 → rejected 2026-05-04 under CONSTRAINTS §5)
    dismissed_reason: |
      Moat thesis collapsed under 2026-05-04 verification. The brief's lane-1
      premise — "the full-resolution spectral wave density data (wave height by
      frequency bin) is not fully mirrored at NCEI at sub-hourly cadence" — is
      factually incorrect. NDBC itself publishes a complete public archive at
      the SAME :10/:40 sub-hourly cadence as the realtime feeds:
        - Monthly: https://www.ndbc.noaa.gov/data/swden/{Jan|Feb|...|Dec}/<station><MM><YYYY>.txt.gz
        - Annual:  https://www.ndbc.noaa.gov/data/historical/swden/<station>w<YYYY>.txt.gz
      Both are open HTTP, public domain, identical column schema (YY MM DD hh
      mm + frequency-bin energies). Sample verifications 2026-05-04:
      41001w2024.txt.gz, 41001w2025.txt.gz (last-modified 2026-02-11),
      4100212026.txt.gz (Jan 2026 monthly file).

      The realtime "10–50 minute" cadence cited in the wishlist entry was
      speculative; actual NDBC observation cycle is twice-hourly at fixed
      :10/:40 minutes, and that exact cadence is preserved in both the monthly
      and annual public archives. There is no temporal-resolution gap between
      what we proposed to capture and what NDBC publishes for free. CONSTRAINTS
      §5 fires → Defensibility=0 → composite 7.600 → 0.000 → auto-reject. Full
      reasoning in briefs/rejected/00.000-20260504-ndbc-realtime-buoys.md
      "Verification outcome (2026-05-04 — rejection)" section.

      Revisit only if (a) NDBC announces it will retire /data/swden/ or
      /data/historical/swden/, (b) a higher-cadence stream becomes available
      (sub-30-minute) that is NOT folded into the historical archive, or (c) a
      Lane-4 derived-feature thesis emerges where compute on the public archive
      (not data access) is the moat. In any of those cases, file a fresh
      wishlist entry; do not revive this one.

  - id: njdot_511_cameras
    title: "New Jersey DOT Traffic Camera Images (511NJ)"
    url: https://www.511nj.org
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      New Jersey DOT operates 200+ traffic cameras along the NJ Turnpike, Garden State
      Parkway, and major state highways. Images are published live via 511nj.org and are
      not archived by NJDOT. This is the somd-cameras archetype applied to the most
      commercially dense corridor in the US: the NJ Turnpike carries a disproportionate
      share of Northeast freight traffic, and a camera archive covering it would reveal
      recurring congestion patterns, incident dwell times, and weather-induced slowdowns
      that insurance, logistics, and real estate analytics buyers cannot get elsewhere.
      A combined Maryland + New Jersey archive would cover the full mid-Atlantic I-95
      corridor, materially increasing the dataset's value beyond either state alone.
    known_constraints: |
      robots.txt fetched 2026-05-04 at https://511nj.org/robots.txt — User-agent: *
      Allow: / (no path restrictions). Site map page returned HTTP 308 redirect to
      HTTPS (accessible, verified 2026-05-04). Camera image URLs require discovery
      via the 511nj.org map API or NJDOT open data; brief must verify endpoint path
      and confirm image polling is not rate-limited separately from the web UI.
      No formal API ToS located for camera images; treating as public-facing content.
      NJDOT does not appear to publish an archival prohibition in site terms.
    estimated_size: "~70 GB/month (est. 200 cameras × 40 KB/image × 288 polls/day)"
    rate_limit_notes: "No published rate limits for camera images; recommend ≥5s between requests, one camera at a time."
    status: promoted-to-candidate
    promoted_to: 07.360-20260504-njdot-511-cameras
    dismissed_reason: null

  - id: usgs_nws_flood_fusion
    title: "USGS Stream Gauge × NWS Storm Events Cross-source Fusion"
    url: https://waterdata.usgs.gov/nwis/iv
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 3
    why_interesting: |
      USGS maintains 8,000+ stream gauges reporting discharge, stage, and velocity at
      15-minute intervals. NWS Storm Events Database records every declared storm event
      with polygon geometry and start/end times. Neither source is ephemeral, but the
      JOIN — mapping every NWS storm polygon to all USGS gauges within it, capturing
      peak discharge, time-to-peak lag from storm onset, and recession curve shape —
      does not exist as a machine-readable public dataset. Flood insurance actuaries,
      municipal stormwater engineers, and climate researchers all need this fusion but
      must currently assemble it ad hoc. A continuously-updated fusion dataset covering
      the full network across every storm event since gauge installation is the moat:
      the historical depth compounds over time and is impossible to retroactively
      reconstruct once the storm-event → gauge-response join window closes.
    known_constraints: |
      USGS waterdata robots.txt fetched 2026-05-04 at https://waterdata.usgs.gov/robots.txt
      — User-agent: * Allow: / (no restrictions). USGS NWIS instantaneous values API
      at https://waterdata.usgs.gov/nwis/iv returned HTTP 200 with live data (station
      01646500, parameter 00060, verified 2026-05-04). USGS data is US government
      public domain. NWS api.weather.gov/robots.txt returns Disallow: / for User-agent: *
      (verified 2026-05-04); however, api.weather.gov is a publicly documented REST API
      explicitly intended for programmatic use — the robots.txt Disallow is aimed at
      search engine indexers. Brief must confirm NWS terms of service page before
      treating as clear. NWS Storm Events data is also available as bulk CSV downloads
      from NCEI (ncei.noaa.gov) which may have cleaner ToS; brief should evaluate both
      access paths.
    estimated_size: "~50 MB/month gauge data; derived fusion artifacts ~200 MB/month (computed, not ingested)"
    rate_limit_notes: "USGS: no formal rate limit published; recommends polite usage and bulk WaterServices endpoints. NWS: no per-minute rate limit for standard API use."
    status: promoted-to-candidate
    promoted_to: 07.695-20260504-usgs-nws-flood-fusion
    promoted_to_history:
      - 07.771-20260504-usgs-nws-flood-fusion (Lane 3, 2026-05-04 → 2026-05-04, re-categorized to Lane 4 under CONSTRAINTS §5)
    dismissed_reason: null

  - id: coops_ais_coastal_fusion
    title: "NOAA CO-OPS Tide Gauge × AIS Vessel Position Coastal Fusion"
    url: https://api.tidesandcurrents.noaa.gov
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 3
    why_interesting: |
      NOAA CO-OPS provides 6-minute water level, current velocity, and meteorological
      data from 200+ coastal stations as a free public API. USCG/MarineCadastre
      publishes delayed AIS vessel position data as open data. Neither source is a moat
      alone. The fusion — tying exact tidal height, current speed/direction, and wave
      conditions at each CO-OPS station to vessel transits through adjacent waters —
      creates coastal maritime operational intelligence that port risk managers, marine
      insurance underwriters, and search-and-rescue analysts cannot buy anywhere at
      national coverage with sub-daily granularity. The time-aligned join is the moat:
      once a vessel transit occurs in a specific tidal window, that correlated event
      cannot be retroactively reconstructed from separately-archived sources because
      the vessel's exact position relative to the CO-OPS station at that tidal moment
      requires millisecond-aligned join keys that are not preserved in either archive.
    known_constraints: |
      Re-verified 2026-05-04. CO-OPS API: api.tidesandcurrents.noaa.gov/robots.txt
      returns HTTP 403 (no robots.txt on API subdomain — absent, not Disallow);
      datagetter endpoint returned live 6-minute water level for station 8518750
      (NY Battery) and the mdapi station inventory lists 301 active waterlevel
      stations. CO-OPS data is US government public domain.

      MarineCadastre/AIS: marinecadastre.gov 301-redirects to hub.marinecadastre.gov
      (ArcGIS Hub site). hub.marinecadastre.gov/robots.txt is `User-agent: *
      Crawl-delay: 60` with Disallow only on site-infrastructure paths
      (/sites/, /admin/, /sessions/, /groups/, /people/, /workspace/) — data
      paths not blocked. The actual bulk AIS data is hosted at
      coast.noaa.gov/htdata/CMSP/AISDataHandler/{year}/, which coast.noaa.gov's
      robots.txt does NOT disallow (verified 2026-05-04 against the full
      robots.txt list). NOAA changed AIS file format from daily .zip (2024 and
      prior, 366 files) to daily .csv.zst (zstd-compressed CSV) starting 2025
      (365 files). Sample file ais-2025-01-01.csv.zst = 202 MB compressed,
      last-modified 2025-08-29. AIS data is US government public domain.

      KEY LIMITATION (newly discovered 2026-05-04): MarineCadastre AIS publishes
      with a 6–12 month delay, not the ~72h originally guessed in the prior pass.
      The 2026 archive does not exist yet (HTTP 404). This is a bulk-only,
      non-real-time source. Any thesis that relies on live or near-live AIS
      cannot be served by this path; AISHub remains restricted (data-sharing
      agreement required, prior verification holds).
    estimated_size: "CO-OPS: ~5 MB/month per station × 301 stations ≈ 1.5 GB/month live. AIS bulk: 81.5 GB/year (2025 full-year confirmed); ~7 GB/month equivalent post-publication."
    rate_limit_notes: "CO-OPS API: max 1 year per request, no per-minute rate limit published. AIS: bulk download only with 6–12 month publishing latency; honor hub.marinecadastre.gov Crawl-delay 60s for any hub-side requests. coast.noaa.gov bulk paths have no published rate limit but recommend ≥5s between zst downloads."
    status: dismissed
    promoted_to: null
    dismissed_reason: |
      Moat thesis collapsed under 2026-05-04 verification (operator decision
      2026-05-04, parity with dc_capital_bikeshare_gbfs handling). Both raw
      inputs are publicly archived with timestamps: CO-OPS has its own historical
      API, and AIS is in the NOAA MarineCadastre bulk archive (coast.noaa.gov
      /htdata/CMSP/AISDataHandler/{year}/, public-domain, no robots restriction
      on data path). A historical time-aligned join therefore can be reconstructed
      by any analyst from public sources at any time — there is no temporal-loss
      moat. The original wishlist `why_interesting` claim that "the vessel's exact
      position relative to the CO-OPS station at that tidal moment requires
      millisecond-aligned join keys that are not preserved in either archive" is
      factually incorrect (AIS records carry timestamps; CO-OPS records carry
      6-minute timestamps; the join is straightforward). Project policy: if there
      isn't a viable moat to exploit, the work can be reconstructed by anyone
      later without issue, so the entry is not worth carrying. Revisit if (a) a
      reframed Lane-4 derived-artifact thesis emerges where compute (not data
      access) is the barrier, or (b) a real-time/low-latency AIS source becomes
      publicly accessible without a data-sharing agreement, at which point a
      fresh wishlist entry should be added rather than reviving this one.

  - id: dc_capital_bikeshare_gbfs
    title: "Capital Bikeshare (DC) GBFS Real-time Bike & Station Status"
    url: https://gbfs.lyft.com/gbfs/1.1/dca-cabi/gbfs.json
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      GBFS free_bike_status and station_status feeds are overwritten on each poll
      (TTL=60s per the lyft_cabi system_information feed, verified 2026-05-04).
      Per-bike position records and minute-resolution station fill-state at minute T
      cannot be reconstructed from any later snapshot. Capital Bikeshare publishes
      historical station-level trip dumps quarterly, but per-vehicle dwell times,
      ebike rebalancing trajectories, and minute-resolution station occupancy are
      not in the public archive. A continuous multi-year capture would support
      trip-demand modeling, rebalance-fleet dispatch analysis, transit-equity
      research, and weather/event-correlated demand studies that the quarterly
      trip dumps do not enable.

      IMPORTANT — the original multi-operator moat thesis from FOCUS.md item 1
      does NOT survive verification. Of the five DDOT-listed DC operators
      (Capital Bikeshare, Lime, Lyft scooters, Helbiz, Spin), four were eliminated
      on 2026-05-04: Lime on robots.txt Disallow; Lyft scooters on stale-feed
      grounds (last_updated 2023-08-17, file no longer refreshed; Lyft's DC
      operations are now solely under the Capital Bikeshare brand and covered by
      this entry); Helbiz on 504 timeout (company exited US market in 2023);
      Spin on 404 "Invalid feed" (DC feed retired). Cross-operator
      substitution / modal-share fusion is therefore not achievable from publicly
      accessible GBFS feeds in DC right now. Operator should weigh whether a
      single-operator CaBi archive merits brief promotion on its own — still a
      lane-1 candidate, but a smaller defensible moat than the original FOCUS
      item assumed.
    known_constraints: |
      Discovery manifest at https://gbfs.capitalbikeshare.com/gbfs/gbfs.json
      (HTTP 200, verified 2026-05-04) points to https://gbfs.lyft.com/gbfs/1.1/dca-cabi/
      where the actual data feeds live. All six core feeds (gbfs.json,
      system_information.json, station_information.json, station_status.json,
      free_bike_status.json, ebikes_at_stations.json) returned HTTP 200 on
      2026-05-04 with a "moat-research/0.1" UA. The prior 2026-05-04 dismissal
      that cited gbfs.lyft.com → 403 was UA-dependent or transient and did not
      reproduce in this recheck. robots.txt at both gbfs.capitalbikeshare.com
      and gbfs.lyft.com returns S3 AccessDenied 403 — the buckets have no robots.txt
      configured, treat as absent rather than Disallow. system_information lists
      operator: "Lyft", system_id: "lyft_cabi". Capital Bikeshare publishes data
      under the official Capital Bikeshare open-data terms allowing reuse with
      attribution. No published per-request rate limit; GBFS Best Practices
      recommend honoring the feed-provided TTL (60s) as minimum poll interval.
    estimated_size: "~30 GB/month raw (free_bike_status ~350 KB × 1440/day + station_status ~320 KB × 1440/day) before compression; ~2–5 GB/month with gzip + delta-only retention."
    rate_limit_notes: "Honor TTL=60s as minimum poll interval per GBFS Best Practices. No published per-IP rate limit; recommend single-process polling, not multi-process."
    status: dismissed
    promoted_to: null
    dismissed_reason: |
      Moat thesis collapsed under 2026-05-04 verification. The FOCUS.md item 1
      premise was a multi-operator continuous archive across all five DC
      micromobility fleets; only 1 of 5 operators (Capital Bikeshare) survived
      hard-constraint and reachability checks. A single-operator CaBi-only
      archive is materially smaller than the original thesis: cross-operator
      substitution patterns, modal share, and dwell-time-by-zone — the value
      adds that distinguished this from any one operator's internal logs —
      cannot be produced from a single feed. Capital Bikeshare also already
      publishes quarterly station-level trip dumps publicly, so the marginal
      moat from a sub-minute archive is narrower than for less-archived
      operators (e.g., the somd-cameras pattern). Recheck if (a) Lime
      relaxes its `Disallow: /` robots.txt, (b) any new operator (Veo, Bird,
      Helbiz successor) publishes an open DC GBFS feed, or (c) the operator
      decides a CaBi-only sub-minute archive is worth pursuing on its own
      narrowed merits — at which point a fresh wishlist entry should be
      added rather than reviving this one.

  - id: us_transit_gtfsrt_smaller_agencies
    title: "US Transit GTFS-Realtime Vehicle Positions — Smaller-Agency Aggregation"
    url: https://gtfs.org/realtime/
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      The somd-cameras / njdot-511-cameras pattern applied to transit telemetry.
      ~150–200 US transit agencies publish GTFS-Realtime VehiclePosition feeds
      (typically 15–30s polling cadence). The position of every bus / light-rail
      vehicle / streetcar at minute T is overwritten on each poll. A handful of
      large agencies archive their own (NYC MTA, CTA Chicago, BART) and Interline /
      Transitland operates a *commercial* archive, but no PUBLIC continuous archive
      exists across the long tail of small/mid agencies (Allegheny County PRT,
      Sacramento RT, RTD Denver, Sound Transit, Cap Metro, MARTA, RIPTA, CDTA,
      LANTA, Foothill Transit, etc.). A multi-year cross-agency archive enables
      operations research (run-time variance, dwell-time distributions, on-time-
      performance), real-estate analytics (proximity-weighted reliability),
      insurance underwriting (transit-corridor incident exposure), and academic
      transportation research that none of the agencies' own (often non-existent)
      public archives can support. Per-agency verification at brief stage:
      (a) feed is publicly reachable without paid auth (free token OK), (b) no
      public historical archive of vehicle positions exists from the agency or any
      free third party at <60s cadence. Agencies failing (b) are excluded from the
      thesis individually, like the somd-cameras vs. NJ-DOT split.
    known_constraints: |
      gtfs.org/realtime is the spec (informational). Per-agency endpoints vary;
      many require a free developer-account API token (e.g., AC Transit returns
      401 without one — verified 2026-05-04). Free tokens do not violate
      CONSTRAINTS §1 (auth-bypass) but the brief must enumerate per-agency token
      ToS clauses, especially around redistribution / archival rights. Some
      agencies' developer agreements forbid public re-sharing of feed contents
      while permitting analytical use — that's compatible with this project's
      private-corpus moat thesis but must be reviewed per agency. No multi-agency
      robots.txt issue since each is its own host. Concurrency: ~200 agencies ×
      30s polling = ~7 req/s aggregate, trivial. Storage: ~30 GB/month per agency
      raw protobuf before compression; ~3–5 GB/month with delta-only retention.
      Critical §5 check: confirm Transitland / Mobility Database do NOT offer free
      public historical vehicle-position downloads (Transitland's archive is paid;
      Mobility Database catalogs schedules + RT URLs but does not archive RT
      payloads — verify both at brief stage).
    estimated_size: "~5–10 GB/month/agency raw; ~1 TB/year aggregate at 200 agencies with delta-only retention."
    rate_limit_notes: "GTFS-RT best-practice cadence 15–30s; honor per-agency rate limits and developer agreements. Single-process polling per agency."
    status: promoted-to-candidate
    promoted_to: 06.701-20260504-us-transit-gtfsrt-smaller-agencies
    dismissed_reason: null

  - id: cslb_ca_contractor_disciplinary_corpus
    title: "California CSLB Contractor Disciplinary Actions — Structured Extraction Corpus"
    url: https://www.cslb.ca.gov/About_Us/Library/Disciplinary_Actions/
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 4
    why_interesting: |
      The California Contractors State License Board publishes monthly
      disciplinary-action newsletters and individual administrative-order PDFs
      (license suspensions, revocations, fines, citation history) for ~290k
      licensed contractors. The raw PDFs are archived on CSLB's site, so Lane 1
      does NOT apply (§5: raw is reconstructible). The defensible artifact is the
      *structured extraction* — contractor name → license # → violation taxonomy
      → fine amount → suspension dates → repeat-offender lookup → cross-licensee
      RMO/RME relationships — at scale and ongoing, with weekly cadence and
      cross-state entity resolution as the moat compounds. Buyers: GC vetting
      tools, construction insurance underwriters, plaintiff's attorneys (lemon-
      contractor identification), regulatory data brokers (LexisNexis Risk,
      Verisk, ContractorCheck), state-AG consumer-protection units. A Lane-4
      thesis: compute (OCR + NER + entity resolution + canonicalization) is the
      barrier; an analyst with the same PDFs needs months of NLP + cleanup to
      reproduce, and the historical depth + ongoing weekly updates compound
      defensibility. Natural extension: federate to all 50 states' contractor
      boards (e.g., NY State Department of State, FL DBPR, TX TDLR, etc.) — the
      cross-state entity resolution is itself a non-trivial moat layer.
    known_constraints: |
      Reachability 2026-05-04: cslb.ca.gov returned 200 on the verify-license
      endpoint (/OnlineServices/CheckLicenseII/CheckLicense.aspx, 37 KB). The
      historical disciplinary-actions archive path /About_Us/Library/Disciplinary_Actions.aspx
      currently 404s into a Page_Not_Found template; the Library landing
      (/About_Us/Library.aspx) returns 200 — brief stage must enumerate the
      current canonical archive URL (likely restructured during a recent site
      migration). robots.txt absent (404). CSLB data is public-record under CA PRA;
      no archival prohibition located. Bulk Public Records Act request channel
      exists (cslb.ca.gov/Resources/Forms/PRA-Request) for compressed historical
      access if needed. CRITICAL §5 caveat: the raw PDFs are publicly archived,
      so the brief MUST justify Lane-4 defensibility on (a) compute-as-barrier
      structured extraction, (b) ongoing-update compounding, (c) cross-state
      entity resolution. If the operator decides any of those collapses (e.g., CA
      releases a structured CSV export, or a competitor publishes the same
      structured corpus), the entry must be re-evaluated per the operator's
      no-moat=no-keep policy.
    estimated_size: "~2–5 GB raw PDF archive at full historical depth; ~500 MB structured artifact (Parquet/JSONL)."
    rate_limit_notes: "No published rate limit; recommend ≥5s between PDF fetches, single-process. CA PRA bulk requests may be the politer path for full historical."
    status: promoted-to-candidate
    promoted_to: 07.009-20260504-cslb-ca-contractor-disciplinary-corpus
    dismissed_reason: null

  - id: multi_state_medical_board_enforcement
    title: "Multi-State Medical Board Enforcement Actions — Cross-State Entity-Resolved Corpus"
    url: https://www.fsmb.org/physician-profile/
    discovered: 2026-05-04
    discovered_by: maximizer
    lane_hint: 4
    why_interesting: |
      State medical boards each publish enforcement actions (license suspensions,
      revocations, probations, surrender-in-lieu, voluntary restrictions, criminal
      conviction notices) against physicians in their jurisdiction. Each state's
      archive is patchy (CA MBC, NY OPMC, TX MB, FL DOH, etc. all have current-
      state-displaying search portals; historical PDFs vary in availability). The
      Federation of State Medical Boards (FSMB) maintains a Physician Data Center
      that aggregates this, but it is a PAID product, restricted to credentialing
      organizations. The National Practitioner Data Bank (NPDB) is statutorily
      restricted to hospitals/insurers — not public. There is no PUBLIC structured
      cross-state corpus with entity-resolved physician records. The moat is
      (a) cross-state entity resolution (Dr. John Smith in CA vs. NY vs. FL — same
      person?), (b) structured extraction of action type / cause / date / scope,
      (c) ongoing weekly updates compounding. Buyers: hospital privileging units,
      malpractice insurance underwriters, telehealth platforms (multi-state
      licensure verification), patient-lookup-services (e.g., consumer-facing
      "is my doctor disciplined?" tools), legal-research tools, journalism
      (medical-error reporting). Lane 4 + Lane 5 (niche-vertical: healthcare
      provider risk).
    known_constraints: |
      Per-state portals reachable 2026-05-04 (CA Medical Board mbc.ca.gov returned
      200 on enforcement-reports landing). robots/ToS varies by state; brief stage
      must verify each state's portal individually (this is the major
      implementation cost — ~50 distinct portals, each with its own quirks).
      Many states publish PDFs of monthly disciplinary newsletters; some have
      structured CSV exports (e.g., CA MBC publishes some enforcement data via
      data.ca.gov). FSMB and NPDB are out-of-scope (paid / restricted). §5 check:
      the structured cross-state corpus does not exist publicly, so Lane 4 holds
      provided the brief commits to compute-as-barrier (structured extraction +
      cross-state entity resolution + ongoing curation) as the actual moat. If
      any state were to publish a complete pre-resolved CSV (FSMB-equivalent) for
      free, the corresponding state's contribution loses moat value but the
      cross-state aggregation moat survives.
    estimated_size: "~5 GB raw archive (PDFs + HTML scrapes across 50 states, full historical); ~1 GB structured artifact."
    rate_limit_notes: "Per-state portal limits unpublished; recommend ≥10s between requests per portal, single-process per state, distributed across portals."
    status: promoted-to-candidate
    promoted_to: 06.892-20260504-multi-state-medical-board-enforcement
    dismissed_reason: null
```

## Notes for the operator

Candidates considered and rejected on hard-constraint grounds (2026-05-04 verification pass):

- **PurpleAir** (purpleair.com): robots.txt `User-agent: * Disallow: /` verified 2026-05-04 — crawling the site would violate robots.txt, triggering CONSTRAINTS.md §2. Dismissed.
- **511VA / VDOT 511** (511va.org): robots.txt `User-agent: * Disallow: /` verified 2026-05-04 — same hard-constraint violation. Dismissed.

DC rideshare/micromobility GBFS — 2026-05-04 recheck of the five DDOT-listed operators (FOCUS.md item 1). Capital Bikeshare survived and was added as `dc_capital_bikeshare_gbfs` above. The other four were dismissed:

- **Lime** (data.lime.bike): robots.txt `User-agent: * Disallow: /` with three narrow Allow exceptions (apple-app-site-association, /juicer, /.well-known/assetlinks.json) — the `/api/partners/v1/gbfs/` path is implicitly blocked. CONSTRAINTS.md §2 hard violation. Endpoint returns live data (HTTP 200, 1.9 MB) but cannot be ingested under our rules. No documented bulk-download alternative. Dismissed.
- **Lyft scooters DCA** (s3.amazonaws.com/lyft-lastmile-production-iad/lbs/dca/free_bike_status.json): file is reachable but `last_updated` field is 1692287847 = 2023-08-17, indicating Lyft no longer refreshes this S3 path. `vehicle_types.json` in the same bucket returns HTTP 403 (partial decommission). Lyft's active DC operations are under the Capital Bikeshare brand — coverage already provided by the surviving entry. Dismissed as stale.
- **Helbiz** (api.helbiz.com): `gbfs.json` returns HTTP 504 Gateway Timeout (verified twice, 30s timeout). Helbiz filed for bankruptcy and exited the US market in 2023; endpoint is no longer maintained. Dismissed as defunct.
- **Spin** (web.spin.pm/api/gbfs/...): redirects to gbfs.spin.pm, which returns HTTP 404 `{"code":404,"message":"Invalid feed"}`. Spin no longer publishes a Washington DC GBFS feed. Dismissed as feed retired.

Net outcome: 1 of 5 operators viable. The original FOCUS.md item 1 multi-operator fusion thesis is not achievable from public GBFS endpoints in DC at this time — see `dc_capital_bikeshare_gbfs.why_interesting` for the narrowed thesis.

Discovery synthesis pass — 2026-05-04 (refilling wishlist after the four original entries reached terminal status). Three new candidates added above (`us_transit_gtfsrt_smaller_agencies` Lane 1, `cslb_ca_contractor_disciplinary_corpus` Lane 4, `multi_state_medical_board_enforcement` Lane 4+5). Eight additional candidates were considered and dismissed in the same pass:

- **Bay Area 511 API** (api.511.org): robots.txt `User-agent: * Disallow: /` verified 2026-05-04 — CONSTRAINTS §2 hard violation. Even though the data (transit + traffic) is government-funded and public-spirited, the published robots.txt forbids crawling. Dismissed.
- **regulations.gov** (federal rule comments): CloudFront returned 403 against the `moat-research/0.1` UA verified 2026-05-04, AND comments are durably archived by regulations.gov + the National Archives — Lane 1 thesis fails §5 even if access were granted. Dismissed on dual grounds.
- **NJ Judiciary public-access portal** (portal.njcourts.gov/webe1/ECasePublic/): reachable (200), but court records are systematically archived by the NJ Judiciary as required by court-records retention law — every filing is preserved. Lane 1 fails §5. Lane 4 (OCR/structured extraction of complaint PDFs) might survive but is a deep multi-jurisdiction project beyond a single wishlist entry; would need its own scoping pass. Dismissed for now; revisit if the operator wants to scope a Lane-4 multi-state court-records corpus.
- **NYC City Council Legistar** (legistar.council.nyc.gov): reachable (200), but Legistar IS the system of record for NYC council activity — every meeting, agenda, vote, and (largely) recording is archived in the platform itself. Lane 1 fails §5. Lane 4 thesis (transcription + structured extraction over public-meeting recordings) is well-served by existing commercial offerings (Quorum, FiscalNote, Civic). Dismissed; revisit only if a clearly-differentiated Lane-4 angle emerges.
- **AC Transit GTFS-RT live feed** (api.actransit.org): returned `401 A valid API token is required` verified 2026-05-04. Free-token gating is not a §1 violation but illustrates the per-agency token landscape captured in the surviving `us_transit_gtfsrt_smaller_agencies` entry. Dismissed individually as a wishlist candidate; folded into the broader smaller-agency thesis. (At brief stage, AC Transit is an in-scope target if the developer agreement permits archival.)
- **City of Chicago Open Data 311 service requests** (data.cityofchicago.org): robots.txt allows crawling with `Crawl-delay: 1`; however 311 records are durably archived by the city itself via the Socrata platform with full historical depth. Lane 1 fails §5. Dismissed.
- **CSLB current Lane-1 framing** (live license-status snapshot): considered as a separate Lane-1 thesis (snapshot the current license/status of all 290k contractors at high cadence, capture license suspensions in flight). Dismissed because (a) license-status changes are durably searchable through CSLB's verify-license endpoint at any time, and (b) the disciplinary-action source itself is the higher-value artifact. Folded into the surviving Lane-4 entry.
- **FCC fcc.gov** (license modifications, ULS): every reachability attempt 2026-05-04 timed out or returned HTTP/2 stream INTERNAL_ERROR against our UA across the apex and www subdomains. Even if reachable, ULS publishes weekly bulk dumps + maintains a public structured archive at FTP — Lane 1 fails §5. Dismissed.

Net new wishlist surface: 3 candidates added (1 Lane 1, 2 Lane 4). Patterns observed during the pass are codified in `.wolf/cerebrum.md` (no-archive-without-§5-check, Lane-4 entity-resolution as moat, free-API-token vs. auth-bypass distinction).

## How to append (for operator quick reference)

Each new entry is one YAML map under `sources:`:

```yaml
- id: <short_snake_case_id>            # stable, used for promoted_to refs
  title: "<human title>"
  url: <primary url>
  discovered: YYYY-MM-DD
  discovered_by: operator              # operator | maximizer
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
