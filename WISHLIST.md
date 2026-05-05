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

  - id: usda_aphis_animal_welfare_inspections
    title: "USDA APHIS Animal Welfare Act Inspection Reports — Continuous Capture & Cross-Licensee Corpus"
    url: https://efile.aphis.usda.gov/PublicSearchTool/
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 2
    why_interesting: |
      USDA APHIS Animal Care publishes inspection reports, citation/non-compliance
      narratives, and annual reports for ~10,000 AWA-licensed/registered facilities
      (research labs, breeders, exhibitors, dealers, transporters). The corpus is
      Lane-2 candidate because its public availability has historically been
      politically volatile: in February 2017 USDA abruptly removed the public
      Animal Care Information System database, citing privacy/litigation reasons;
      partial restorations followed years of FOIA litigation (HSUS v. Vilsack et al.)
      and the current efile public search tool replaced ACIS in ~2020. The
      possibility of another withdrawal under shifting administrations is the
      Lane-2 capture-before-the-door-closes thesis. Lane 5 also fits (niche
      vertical: animal-research compliance / lab-animal welfare / pet-trade
      enforcement). Buyers: animal-welfare advocacy orgs (HSUS, ALDF, PETA
      research arm), academic research-ethics offices, life-science companies
      (vendor-vetting for IACUC compliance), insurance underwriters (kennel/
      exhibitor liability), investigative journalism. Defensible artifacts:
      (a) longitudinal facility-level compliance trajectories (citation count,
      severity, repeat-offender flags) with off-platform persistence in case
      USDA culls historical records again, (b) cross-licensee entity resolution
      (parent companies → multiple LLC-licensed facilities), (c) NLP-extracted
      structured citation narratives (taxa affected, AWA section cited,
      corrective-action timelines) at scale.
    known_constraints: |
      Verified live 2026-05-05. www.aphis.usda.gov returned HTTP 200 and
      redirected /animal-welfare → /animal-care/awa-services (Drupal 11 site,
      cache headers normal). aphis.usda.gov/robots.txt is standard Drupal —
      User-agent: * with Disallow only on Drupal admin paths (/admin/, /node/add/,
      /user/login/, etc.); /animal-care/ and similar data paths are NOT blocked.
      efile.aphis.usda.gov/PublicSearchTool/ returned HTTP 200 with 101 KB of UI
      content under the "moat-research/0.1" UA. Underlying inspection-record
      retrieval API is the AngularJS app's XHR layer; brief stage must enumerate
      the actual JSON endpoints (PublicSearchToolApi/api/inspection/*) and
      confirm rate-limit behavior. CONSTRAINTS §5 reconstructibility check:
      while USDA archives current inspection reports through efile, the historical
      record is precisely what was at risk during the 2017 withdrawal — the
      MOAT is the off-platform continuous archive that is no longer reconstructible
      after a future withdrawal event, NOT a duplicate of currently-public records.
      This is a distinct §5 framing from "raw is reconstructible from public
      sources" because the failure mode is *removal of the public source itself*.
      Treat the moat as conditional on (i) an off-platform durable archive and
      (ii) the political-vulnerability premise — flag if either weakens. USDA
      data is US public-record under FOIA; no archival prohibition located. No
      published per-request rate limit; recommend ≥5s between PDF/JSON fetches.
    estimated_size: "~10–20 GB raw archive at full historical depth (~10k facilities × ~5 inspections/yr × ~200 KB PDFs × 5+ years); ~500 MB structured corpus."
    rate_limit_notes: "No published rate limit on efile or aphis.usda.gov. Recommend ≥5s between requests, single-process. Bulk FOIA path exists if the public tool is throttled or withdrawn."
    status: promoted-to-candidate
    promoted_to: 06.805-20260505-usda-aphis-animal-welfare-inspections
    dismissed_reason: null

  - id: ferc_elibrary_regulatory_filings
    title: "FERC eLibrary Energy Regulatory Filings — Structured-Extraction Corpus"
    url: https://elibrary.ferc.gov/eLibrary/search
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 4
    why_interesting: |
      The Federal Energy Regulatory Commission's eLibrary holds ~10M+ filings
      (rate cases, FERC Form 1/3-Q/6/6-Q/60/714, Order 1920 transmission
      planning compliance filings, Order 2222 DER aggregation tariffs, LNG
      facility applications, hydropower licenses, pipeline certificates)
      submitted by ~3,000 jurisdictional entities (interstate pipelines, RTOs/
      ISOs, electric utilities, hydropower licensees, LNG operators). Raw PDFs
      are durably archived by FERC, so Lane 1 does NOT apply (§5: raw is
      reconstructible). The Lane-4 moat is structured extraction at scale:
      docket networks (intervenors, protestors, cross-docket motions),
      tariff-change tracking (settlement vs. litigated outcomes per docket),
      transmission-planning project pipelines (which RTO portfolios survived
      Order 1920 windows), commissioner voting alignment, and cross-utility
      financial-metric extraction from Form 1 narratives (where current
      structured Form 1 CSVs from FERC capture only the schedule data, not
      the narrative attachments). Lane 5 also fits (niche vertical: energy
      regulatory analytics; existing commercial competitors include S&P Global
      Market Intelligence, Velocity Suite, ICF, and FERC-specialty law firms'
      internal databases — all paid and partial). Buyers: energy-trader
      legal/regulatory teams, transmission planners, hedge-fund energy desks,
      ESG-mandate compliance verifiers, plaintiffs' counsel in rate cases.
    known_constraints: |
      Verified live 2026-05-05. elibrary.ferc.gov/eLibrary/search returned
      HTTP 200 with 21 KB of search-UI content under "moat-research/0.1".
      elibrary.ferc.gov has no robots.txt configured (404 on /robots.txt =
      absence of policy, not Disallow). www.ferc.gov/robots.txt is standard
      Drupal — Disallow only on admin/login paths; data paths unrestricted.
      The eLibrary search is a UI layer over an internal REST endpoint; an
      unauthenticated POST to a guessed `/eLibraryAPIProxy/api/Search` 404'd,
      so brief stage must reverse the actual XHR endpoint from the UI's network
      tab (do NOT invent paths). FERC also publishes bulk-data products on
      ferc.gov (Form 1, Form 6, Form 714, EQR by quarter) that ARE durably
      archived — those alone fail §5 as a duplicate-the-archive thesis. The
      defensible delta is (a) attachment-narrative extraction (Form 1 narrative
      schedules NOT in the structured CSVs), (b) docket-graph structured
      extraction (intervenor/protestor networks across dockets), (c) cross-
      filing entity resolution (subsidiary LLCs → parent utility holding
      companies). CONSTRAINTS §5 check: the structured corpus described above
      does not exist as a public dataset; commercial offerings (S&P Velocity
      Suite, ICF) are paid and partial; FERC's own bulk Form data is schedule-
      only. If FERC were to release a complete narrative + docket-graph dump,
      this moat collapses — flag at brief stage. No formal rate limit published;
      recommend ≥5s between requests, single-process per docket. eLibrary search
      results lazy-load; avoid pagination floods.
    estimated_size: "~500 GB raw PDF archive at full historical depth (~10M filings × ~50 KB avg); ~5–10 GB structured corpus (docket graphs + extracted schedules + narrative-attachment text)."
    rate_limit_notes: "No published rate limit on eLibrary or ferc.gov. Recommend ≥5s between requests, single-process per docket; respect any 429s with backoff. Bulk Form data is preferable to UI scraping when the same fields are available."
    status: promoted-to-candidate
    promoted_to: 07.006-20260505-ferc-elibrary-regulatory-filings
    dismissed_reason: null

  - id: faa_notams_aviation_alerts
    title: "FAA NOTAMs (Notice to Air Missions) — Continuous Ephemeral Capture"
    url: https://notams.aim.faa.gov/notamSearch/
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      NOTAMs (Notice to Air Missions, formerly Notice to Airmen) are the FAA's
      operational alerts for airspace conditions: GPS jamming/spoofing exercises,
      runway closures, military-operations-area activations, VIP TFRs, drone
      restrictions, navaid outages, obstacle hazards, and laser/light shows.
      Each NOTAM has a defined effective period; once it expires or is cancelled,
      the FAA NOTAM Search tool (the canonical public source) ceases to return
      it. There is no FAA-public archive of expired NOTAMs at the same fidelity
      as the live feed — historical NOTAM availability is patchy, requires FOIA
      requests, and operational-detail fields are sometimes redacted on
      retrospective release. Lane 1 holds: a continuous capture of every NOTAM
      issued, with full effective-period metadata + cancellation timestamps,
      cannot be retroactively reconstructed once the feed turns over. Lane 5
      fits as the niche vertical: aviation safety analytics, drone-corridor
      planning, and — critically — open-source intelligence on military activity
      (GPS-denial NOTAMs near Russian/Chinese borders, US-EU military exercise
      footprints, special-use-airspace activation patterns). Buyers: aviation
      consulting (Cirium, FlightAware analytics arm), drone operators &
      delivery platforms, OSINT firms (Janes, Bellingcat-class researchers),
      defense analysts, and aviation insurance underwriters pricing route risk.
      A multi-year archive across the ~50,000 active US NOTAMs at any moment
      is the moat; ICAO-equivalent international NOTAM expansion (covering
      EUROCONTROL, CAAC, etc.) is a natural extension where each FIR has its
      own publication endpoint with similar ephemerality.
    known_constraints: |
      Verified live 2026-05-05. notams.aim.faa.gov/notamSearch/ returned
      HTTP 200, 27 KB UI bundle, last-modified 2025-03-12 (stable). robots.txt
      at notams.aim.faa.gov returned HTTP 404 (treat as absent — no policy =
      no restriction; consistent with prior cerebrum learnings on absent-vs-
      Disallow). The public NOTAM Search backend is XHR (Spring/Servlet 3.0
      stack per response headers); brief stage must enumerate the actual JSON
      endpoint from the UI's network requests (do NOT invent paths). FAA also
      operates a registered-developer NOTAM API at external-api.faa.gov/notamapi/
      requiring free API key registration at api.faa.gov — free-token gating
      per the GTFS-RT precedent in cerebrum, NOT a §1 auth-bypass concern, but
      brief stage must read the developer terms for redistribution clauses.
      CONSTRAINTS §5 reconstructibility check: FAA does NOT publish a complete
      expired-NOTAM archive at the cadence of the live feed; the FAA's
      Aeronautical Information Services historical-NOTAM lookup is partial,
      lags by months, and operational-detail fields can be redacted on
      retrospective release per FAA Order JO 7930.2. Third-party open archives
      (ICAO Aeronautical Information Exchange Model collectors, SkyVector's
      backfill, OpenAIP) are partial and lossy at the operational-detail level
      that drives the OSINT/insurance use cases. Brief stage must verify that
      no comprehensive third-party expired-NOTAM archive (commercial OK; the
      §5 test is "could an analyst reconstruct from currently-public sources",
      paid commercial archives don't count per the prior CONSTRAINTS §5 reading
      applied to Interline / GTFS-RT) exists at the operational-detail
      fidelity our use cases need. FAA data is US government public-record;
      no archival prohibition located. Recommend ≥30s between full-feed polls,
      ≥5s between airport-specific queries.
    estimated_size: "~5 GB/year (~50k active NOTAMs × ~3 KB JSON × turnover); ~50 GB at 10-year historical depth post-onboarding."
    rate_limit_notes: "No published per-IP rate limit on notamSearch UI backend. external-api.faa.gov NOTAM API gates by free key; honor any documented per-key quota. Recommend ≥30s between feed polls, single-process; ≥5s per airport-specific query."
    status: promoted-to-candidate
    promoted_to: 07.898-20260505-faa-notams-aviation-alerts
    dismissed_reason: null

  - id: osha_enforcement_inspection_corpus
    title: "DOL/OSHA Enforcement Inspection Records & Violation Data — Continuous Off-Platform Archive"
    url: https://www.osha.gov/enforcement
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 2
    why_interesting: |
      OSHA publishes inspection records, violation citations, penalty assessments,
      and fatality/catastrophe accident reports for approximately 3.5 million
      workplace inspections conducted since the agency's founding. The data is
      publicly accessible via data.dol.gov (successor to enforcedata.dol.gov).
      The Lane-2 moat is political volatility: the current administration has
      dramatically curtailed OSHA enforcement — inspection counts, staffing, and
      budget have all been reduced in 2025, and individual inspection reports
      (particularly politically sensitive ones involving high-profile employers)
      have historically been suppressed when challenged. The 2017 USDA APHIS
      database removal is the canonical precedent for this risk pattern; OSHA
      enforcement data under a sustained anti-regulatory administration faces
      analogous structural pressure. A continuous off-platform archive captures
      new inspection records BEFORE any future restriction event, preserving the
      full-text violation narratives and penalty detail that may be removed
      mid-stream. Lane 5 fits as a secondary (workplace safety / industrial
      compliance niche vertical). Buyers: workplace safety law firms (plaintiff
      and defense), industrial insurance underwriters (workers' comp / general
      liability risk scoring by establishment), investigative journalists
      (FOIA-alternative for active inspection cycle data), labor-research
      institutions, ESG data vendors (supply-chain safety due diligence).
      No public cross-time continuous archive of OSHA inspections exists outside
      OSHA's own data.dol.gov system; data.gov bulk snapshots lag the live feed
      and are subject to the same political risk as the primary source.
    known_constraints: |
      Verified live 2026-05-05. www.osha.gov returned HTTP 200 under
      "moat-research/0.1" UA. robots.txt at www.osha.gov is standard Drupal:
      User-agent: * with Disallow only on system/admin paths (/admin/, /core/,
      /profiles/, README.md, etc.); enforcement data paths (/enforcement/, /data/)
      are NOT blocked. data.dol.gov (successor to enforcedata.dol.gov — 301
      redirect to data.dol.gov confirmed HTTP 200) has User-agent: * Disallow:
      /static/ only (data paths unrestricted, verified 2026-05-05).
      data.dol.gov/api/v1/endpoint/enforcement/osha_inspection returned HTTP 200
      under "moat-research/0.1" UA. OSHA data is US government public-record;
      no archival prohibition located. No published per-request rate limit for
      data.dol.gov API. Recommend ≥5s between requests, single-process.
      CRITICAL §5 check (Lane-2 framing): data.gov does publish OSHA enforcement
      bulk snapshots, meaning the historical corpus as of the last data.gov dump
      is reconstructible by any analyst. The Lane-2 moat rests specifically on:
      (a) continuous real-time capture of new inspection records that may be filed
      and subsequently suppressed before appearing in a data.gov bulk dump,
      (b) the off-platform archive surviving a future source restriction/removal
      event analogous to 2017 USDA APHIS withdrawal, and (c) preserving per-
      inspection violation narratives that data.gov aggregated snapshots may
      omit or summarize. Brief stage must verify (c) — if data.gov preserves
      full narrative detail at equal latency to the primary feed, the moat
      narrows to (a) and (b), which must be explicitly weighed against the
      APHIS-pattern precedent for Lane-2 scoring. OSHA fatality/catastrophe
      reports (Form 170) are particularly high-value and historically suppressed;
      these should be treated as priority capture targets at brief stage.
    estimated_size: "~5 GB/year for new inspections (~30k inspections/year × ~150 KB avg record set); ~20 GB full historical corpus at depth from API."
    rate_limit_notes: "No published rate limit on data.dol.gov API or www.osha.gov/enforcement. Recommend ≥5s between requests, single-process. data.gov bulk download path preferred for historical depth bootstrapping."
    status: promoted-to-candidate
    promoted_to: 06.723-20260505-osha-enforcement-inspection-corpus
    dismissed_reason: null

  - id: multi_state_insurance_dept_enforcement
    title: "Multi-State Insurance Department Enforcement Orders — Cross-State Entity-Resolved Corpus"
    url: https://www.dfs.ny.gov/industry_guidance/enforcement_actions
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 4
    why_interesting: |
      State departments of insurance each publish enforcement orders against
      licensed entities (insurers, producers/agents, adjusters, surplus-lines
      brokers, premium-finance companies) covering license revocations, consent
      orders, cease-and-desist orders, market-conduct penalties, and criminal
      referrals. Individual state portals exist (NY DFS, CA DOI, TX TDI, FL OIR,
      IL IDFPR, etc.) but each is siloed — no entity resolution across states,
      no structured national aggregate, no longitudinal compliance trajectory.
      The NAIC (National Association of Insurance Commissioners) publishes
      selected regulatory actions but not a comprehensive structured enforcement
      corpus. The Lane-4 moat is compute-as-barrier: OCR + NER + structured
      extraction at scale across ~55 state+territory portals, with cross-state
      entity resolution as the compound defensibility layer — the same license-
      holder operating across multiple states under different LLC structures
      (e.g., a national health insurer with 50 state-specific subsidiaries)
      cannot be resolved without entity-graph methodology that an analyst would
      need months to reproduce. Lane 5 is strong (insurance regulatory compliance
      analytics niche vertical). Buyers: insurance law firms (adverse-party
      vetting, regulatory defense), carrier compliance teams (producer appointment
      vetting, market-conduct risk scoring), insurtech background-check vendors,
      surplus-lines brokerages (non-admitted producer screening), state-AG
      consumer-protection units, investigative journalists. Pricing precedent:
      NAIC data products + Wolters Kluwer / IVANS-connected licensing databases
      suggest $25k–$100k/year API tiers for structured cross-state regulatory data.
      All three Lane-4 pillars present: (1) compute-as-barrier OCR + NER extraction,
      (2) ongoing-update compounding (new enforcement orders issued weekly per state),
      (3) cross-state entity resolution is the v1 deliverable. Natural extension:
      federate to Puerto Rico, DC, and US territories (~55 total jurisdictions);
      cross-reference with FINRA BrokerCheck and NIPR for dual-licensed producer
      entities in financial + insurance markets.
    known_constraints: |
      Per-state portals verified 2026-05-05. NY DFS (www.dfs.ny.gov):
      enforcement_actions page returned HTTP 200 at
      https://www.dfs.ny.gov/industry_guidance/enforcement_actions.
      robots.txt at www.dfs.ny.gov is standard Drupal — User-agent: * with
      Disallow only on admin/system paths (/admin/, /core/, /profiles/,
      /webny-protected-content/, /public-appeal/search/); enforcement data
      paths NOT blocked (verified 2026-05-05). Missouri DOI (insurance.mo.gov):
      enforcement orders page returned HTTP 429 (rate-limited, verified 2026-05-05),
      confirming live data is published; rate limit must be respected at brief stage
      (≥10s between requests minimum). WA OIC (insurance.wa.gov):
      enforcement-actions URL pattern returned HTTP 403 (2026-05-05) — exact URL
      structure requires discovery at brief stage; robots.txt check required.
      CA DOI (insurance.ca.gov): enforcement-actions URL 404s (site restructuring
      confirmed 2026-05-05); current canonical path must be verified at brief stage
      via CA DOI site search or sitemap. NAIC aggregate (naic.org): returned HTTP 200,
      132 KB page confirmed 2026-05-05 — NAIC publishes summary regulatory actions
      but NOT a comprehensive structured enforcement corpus suitable as a §5 archive.
      §5 check: no comprehensive public cross-state structured enforcement corpus
      exists; NAIC and commercial competitors (Wolters Kluwer, IVANS, Verisk Sequel)
      are paid-access — paid commercial does not trigger §5 per project precedent.
      Each state's raw enforcement orders exist on their portal, so Lane-1 raw fails
      §5; the moat is the Lane-4 structured extraction + entity resolution artifact,
      not the raw PDFs. Brief stage must verify each state portal individually (URL
      pattern, robots.txt, ToS, rate-limit behavior) — same per-state audit
      requirement as the multi-state medical-board brief, analogous implementation cost.
    estimated_size: "~3 GB raw archive (PDFs + HTML across 55 portals, full historical depth); ~300 MB structured artifact (Parquet/JSONL entity graph)."
    rate_limit_notes: "Per-state portal limits vary; Missouri DOI confirmed rate limiting (429 observed 2026-05-05). Recommend ≥10s between requests per portal, single-process per state. Honor any 429s with exponential backoff. WA OIC URL pattern must be identified before polling."
    status: promoted-to-candidate
    promoted_to: 06.483-20260505-multi-state-insurance-dept-enforcement
    dismissed_reason: null

  - id: epa_echo_enforcement_corpus
    title: "EPA ECHO Federal Enforcement & Compliance Corpus — Off-Platform Continuous Archive"
    url: https://echo.epa.gov/tools/data-downloads
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 2
    why_interesting: |
      EPA's Enforcement and Compliance History Online (ECHO) aggregates federal
      and state inspection results, civil enforcement cases, settlements,
      penalties, formal/informal actions, and Discharge Monitoring Report (DMR)
      data across the Clean Water Act, Clean Air Act, RCRA, SDWA, and FIFRA
      programs for ~3 million regulated facilities. The corpus is a Lane-2
      candidate because EPA enforcement transparency has demonstrated political
      vulnerability: in 2017–18 the Trump-era EPA scrubbed climate-change pages,
      hid the cumulative civil penalty totals dashboard from the homepage, and
      reorganized the OECA enforcement annual results page (Sierra Club v. EPA
      and EDGI archival projects documented dozens of removed pages). The 2025
      administration has cut OECA's budget and reportedly directed regional EPA
      offices to deprioritize routine enforcement; civil penalty totals dropped
      to multi-decade lows. The Lane-2 moat is an off-platform durable archive
      of ECHO's case-detail records (with full narrative violation descriptions,
      penalty amounts, settlement terms) captured continuously before any
      future restriction event collapses public access. Lane 5 secondary fits
      (environmental compliance / industrial risk niche). Buyers: environmental
      law firms (plaintiff and defense), industrial insurance underwriters
      (CGL / pollution legal liability scoring), ESG ratings vendors (MSCI,
      Sustainalytics, RepRisk), investigative journalism (ProPublica's
      Documenting Climate Change project, Inside Climate News), state-AG
      environmental units, M&A diligence on industrial assets. Distinct from
      the OSHA brief (workplace safety) and FERC brief (energy regulatory)
      because ECHO covers environmental media (water/air/waste) compliance
      with its own buyer base and distinct §5 archive geometry.
    known_constraints: |
      Verified live 2026-05-05. echo.epa.gov returned HTTP 200 under
      "moat-research/0.1" UA. echo.epa.gov/robots.txt is comprehensive (1914
      bytes): User-agent: * with Crawl-delay: 10 and explicit Disallows on UI
      search-result paths (/facilities/facility-search/results/,
      /facilities/enforcement-case-report-search/results/,
      /detailed-facility-report/, /enforcement-case-report/, /effluent-charts/).
      The /tools/data-downloads/ path is NOT in the Disallow list (verified
      2026-05-05, HTTP 200), so the polite path is bulk-download only — DO NOT
      scrape the search-result UIs or detailed-facility-report pages, those are
      §2 violations. EPA bulk downloads include ICIS-AIR (CAA), ICIS-NPDES
      (CWA), RCRAInfo (RCRA), SDWIS (SDWA) at full historical depth as ZIPs.
      EPA data is US public-record under FOIA. CONSTRAINTS §5 reconstructibility:
      the bulk dumps themselves ARE durably archived (data.gov mirrors and
      Wayback captures of OECA annual results pages survive), so a brief that
      claims "duplicate the bulk dump" fails §5. The Lane-2 moat must rest on
      (i) continuous capture of incremental/delta updates between bulk-dump
      release windows (ECHO refreshes weekly per OECA documentation), AND
      (ii) capturing case-detail narrative fields and per-DMR data points that
      may be summarized or excluded from bulk dumps and are vulnerable to
      future restriction (the 2017 OECA homepage scrubs targeted aggregate
      dashboards, not bulk dumps; the political-vulnerability geometry runs
      through the discoverability layer, not the data files). Brief stage must
      identify and verify (a) which ECHO data fields are bulk-included vs.
      UI-only, (b) the weekly delta-update mechanism, (c) historical Wayback
      evidence of EPA-side restrictions to OECA / ECHO infrastructure. No
      published per-request rate limit beyond Crawl-delay: 10s on the UI.
    estimated_size: "~50 GB raw bulk archive at full historical depth (ICIS-AIR + ICIS-NPDES + RCRAInfo + SDWIS); ~5 GB/year incremental delta captures; ~2 GB structured corpus."
    rate_limit_notes: "robots.txt Crawl-delay: 10s on echo.epa.gov UI. Bulk-download paths under /tools/data-downloads/ have no published rate limit; recommend ≥5s between ZIP fetches, single-process. Honor 429s with exponential backoff."
    status: promoted-to-candidate
    promoted_to: 06.608-20260505-epa-echo-enforcement-corpus
    dismissed_reason: null

  - id: msha_mine_safety_enforcement_corpus
    title: "MSHA Mine Safety Enforcement, Citations & Fatality Reports — Off-Platform Continuous Archive"
    url: https://www.msha.gov/data-and-reports/statistics
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 2
    why_interesting: |
      The Mine Safety and Health Administration publishes inspection records,
      Section 104 citations, withdrawal orders, civil penalty assessments,
      and fatal accident investigation reports (Form 7000-50) for ~12,000
      active US mines (coal, metal/non-metal, sand & gravel). The corpus is a
      Lane-2 candidate because MSHA's enforcement infrastructure has
      demonstrated political vulnerability: under the 2017–19 Trump
      administration, MSHA citation issuance dropped ~40%, the agency's
      "Significant & Substantial" violation tagging became politicized, and
      certain fatal accident investigation reports faced FOIA stonewalling
      (per OIG audits of MSHA's data publication compliance). The 2025
      administration's coal-industry political constituency has signaled
      MSHA budget reductions and renewed pressure to fold MSHA into a
      consolidated DOL safety agency. The Lane-2 moat captures inspection
      narratives, citation severity assessments, and fatality investigation
      reports continuously before any future restriction or reorganization
      event collapses public access to the operator-level enforcement
      detail. Lane 5 secondary fits (industrial safety / mining-vertical
      niche). Buyers: workers' compensation insurance underwriters
      (mining-sector loss costing), mining law firms (operator vetting,
      MSHA contest defense), academic occupational-health researchers,
      mining trade press (Coal Age, E&MJ), ESG analytics targeting fossil-
      fuel asset due diligence, plaintiff's counsel in mine-fatality
      wrongful-death cases.
    known_constraints: |
      Verified live 2026-05-05. www.msha.gov returned HTTP 200 under
      "moat-research/0.1" UA. www.msha.gov/robots.txt is standard Drupal
      (2026 bytes): User-agent: * with Disallow only on Drupal admin paths
      (/admin/, /core/, /profiles/, /node/add/, /search/, /user/login/,
      /comment/reply/, README.md files, /web.config); /data-and-reports/,
      /enforcement/, /inspection-data/ paths are NOT blocked. The
      /data-and-reports/statistics page returned HTTP 200 (verified
      2026-05-05). MSHA also publishes structured open-government data
      products at arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp (HTTP 200
      verified 2026-05-05) — the legacy Apache-served bulk-download portal
      with Mines, Inspections, Violations, Accidents, and Penalty
      Assessments tables in CSV/text format, refreshed quarterly with full
      historical depth. CONSTRAINTS §5 reconstructibility: the OpenGov
      bulk dumps ARE durably archived through both arlweb.msha.gov and
      data.gov mirrors, so a brief that claims "duplicate the OGI tables"
      fails §5. The Lane-2 moat must rest on (i) continuous capture of
      between-quarter incremental updates (citations are issued daily
      per the MSHA Code of Federal Regulations), AND (ii) capturing the
      inspector narrative fields in citation reports and the full text of
      fatal accident investigation reports (Form 7000-50) which contain
      operational detail that the OGI summary tables do NOT preserve at
      scale. Brief stage must verify (a) which fields are
      OGI-bulk-included vs. PDF-only narrative, (b) the citation issuance
      cadence and any near-real-time feed, (c) historical FOIA-stonewalling
      precedent (cite 2017–19 OIG findings, identify specific suppressed
      reports). MSHA data is US public-record under FOIA. No published
      per-request rate limit; recommend ≥5s between requests.
    estimated_size: "~10 GB raw archive at full historical depth (OGI bulk CSVs + accident investigation PDFs + citation narratives); ~1 GB/year incremental capture; ~500 MB structured corpus."
    rate_limit_notes: "No published rate limit on www.msha.gov or arlweb.msha.gov. Recommend ≥5s between requests, single-process. Honor any 429s with exponential backoff. Bulk OGI ZIPs preferred for historical bootstrap; UI scrape only for incremental narrative capture."
    status: promoted-to-candidate
    promoted_to: 06.470-20260505-msha-mine-safety-enforcement-corpus
    dismissed_reason: null

  - id: nlrb_unfair_labor_practice_cases
    title: "NLRB Unfair Labor Practice Cases & Board Decisions — Off-Platform Continuous Archive"
    url: https://www.nlrb.gov/cases-decisions/cases
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 2
    why_interesting: |
      The National Labor Relations Board adjudicates unfair labor practice
      (ULP) charges, representation petitions, and Board decisions affecting
      private-sector labor relations across ~6 million covered US employers.
      Case files (charges, complaints, settlements, withdrawals, ALJ
      decisions, Board orders) are published on nlrb.gov/cases-decisions
      and indexed in the e-filing case-tracker. The corpus is a Lane-2
      candidate because NLRB has demonstrated extraordinary political
      vulnerability: under the 2017–21 Trump-era General Counsel (Peter
      Robb), regional offices were directed to publish less detail in
      case-disposition memos; under the 2021–25 Biden-era GC (Jennifer
      Abruzzo), prosecutorial priorities reversed; the 2025 second Trump
      administration removed Board members in actions of contested
      legality, leaving NLRB without a quorum for several months in 2025
      (Wilcox v. Trump et al.) and disrupting case adjudication and
      publication workflows. The Lane-2 moat captures the case-disposition
      record continuously before any future quorum-collapse, prosecutorial-
      restriction, or DOGE-style data-purge event collapses public access.
      Lane 5 secondary fits (labor relations / employment-law vertical).
      Buyers: management-side labor & employment law firms (Littler,
      Jackson Lewis, Ogletree), union-side firms and the AFL-CIO research
      department, EPLI insurance underwriters (employment practices
      liability), academic labor-economics researchers, investigative
      journalism on union-busting campaigns, corporate compliance teams
      vetting acquisition targets for active ULP exposure.
    known_constraints: |
      Verified live 2026-05-05. www.nlrb.gov returned HTTP 200 under
      "moat-research/0.1" UA. www.nlrb.gov/robots.txt is standard Drupal:
      User-agent: * with Disallow only on Drupal admin paths (/admin/,
      /core/, /profiles/, /node/add/, /search/, /user/login/, /web.config,
      README.md files); /cases-decisions/, /reports/, /open/data/ paths
      NOT blocked. /cases-decisions/cases (case-tracker landing) and
      /cases-decisions/decisions/board-decisions both returned HTTP 200
      (verified 2026-05-05). The case-tracker is an Angular app over an
      internal REST endpoint; brief stage must reverse the actual XHR
      endpoint from the UI's network tab (do NOT invent paths).
      CONSTRAINTS §5 reconstructibility: NLRB itself archives Board
      decisions back to 1935 in its public eGov library, AND the Cornell
      Legal Information Institute mirrors NLRB Board decisions, AND
      Westlaw/Lexis/Bloomberg Law (paid commercial) carry the full
      decisional corpus. Paid commercial archives don't trigger §5 per
      project precedent (Interline / S&P Velocity Suite); the Cornell LII
      mirror DOES potentially trigger §5 for the Board-decisions slice
      and brief stage MUST verify Cornell LII's update cadence and
      archival completeness. The Lane-2 moat must rest on (i) capturing
      the case-tracker / regional-office charge data (ULP charges,
      complaints, settlements) which Cornell LII does NOT mirror —
      decisions are mirrored, but the upstream charge/complaint/settlement
      record is the politically sensitive layer, AND (ii) preserving the
      full per-region case detail (regional director memos, settlement
      terms, withdrawal letters) that may be deprecated under future
      GC-driven publication-restriction directives (precedent: 2017
      Robb-era memos). Brief stage must verify (a) Cornell LII coverage
      scope vs. NLRB primary case data, (b) the case-tracker's REST
      endpoint, (c) historical evidence of NLRB publication-restriction
      under specific GC tenures. NLRB data is US public-record under FOIA.
      No published per-request rate limit on case-tracker; recommend
      ≥5s between requests.
    estimated_size: "~20 GB raw archive at full historical depth (Board decisions PDFs + ALJ decisions + case-tracker per-region detail); ~2 GB/year incremental capture; ~1 GB structured corpus."
    rate_limit_notes: "No published rate limit on www.nlrb.gov. Recommend ≥5s between requests, single-process. Case-tracker XHR endpoints may have separate quotas — honor any 429s with exponential backoff. Cornell LII bulk download preferred for Board-decisions historical bootstrap if coverage is verified."
    status: promoted-to-candidate
    promoted_to: 06.802-20260505-nlrb-unfair-labor-practice-cases
    dismissed_reason: null

  - id: txdot_drivetexas_cameras
    title: "TxDOT Live Traffic Cameras via DriveTexas.org — Texas Freight & Energy Corridor Archive"
    url: https://drivetexas.org/
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 1
    why_interesting: |
      The Texas Department of Transportation operates 1,000+ live traffic cameras
      across Texas state highways and interstates via the DriveTexas.org public portal.
      Camera images refresh continuously (typical DOT cadence: 30–120s) and are NOT
      archived by TxDOT or any publicly known third party. This is the somd-cameras /
      njdot-511-cameras archetype applied to the highest-freight-volume state in the US
      by lane-mile: Texas carries an outsize share of NAFTA/USMCA cross-border commerce
      (I-35 Laredo corridor — the #1 US-Mexico port of entry by trade value), Gulf Coast
      petrochemical transport (I-10 Houston Ship Channel access, I-45 to Galveston, TX-99
      Grand Parkway), and energy-sector logistics (Permian Basin → Midland/Odessa I-20
      corridor, Eagle Ford → I-37). A continuous camera archive covering these corridors
      would reveal freight dwell times, incident patterns, weather-induced slowdowns, and
      port-of-entry backup cadences that logistics companies, oil-field-services firms,
      energy insurance underwriters, and real estate developers along these corridors
      cannot obtain anywhere at this geographic granularity and temporal depth. Combined
      with the existing somd (MD/VA) and NJDOT (NJ) archives, a TX addition closes the
      major remaining gap in an I-35/I-95 East Coast + southern trans-national freight
      corridor dataset. Energy-sector buyer angle is distinct from the I-95 Northeast
      focus of somd/NJDOT: Texas camera feed buyers would include oilfield logistics
      (Baker Hughes, Halliburton), energy traders monitoring infrastructure access, marine
      terminal operators (Port of Houston), and Mexico-cross-border freight intermediaries
      (3PLs, customs brokers, nearshoring companies).
    known_constraints: |
      Verified live 2026-05-05. drivetexas.org main page returned HTTP 200 under
      "moat-research/0.1" UA. robots.txt at drivetexas.org returned HTTP 500
      (Google AppEngine server error, consistent across two attempts 2026-05-05) —
      treat as absent per standard no-policy practice (500 ≠ Disallow; Google-hosted
      backends frequently return 500 on unconfigured paths). www.txdot.gov robots.txt
      returned HTTP 404 (absent, no restriction, verified 2026-05-05). www.txdot.gov
      main page returned HTTP 200. No ToS page with archival prohibition located on
      either drivetexas.org or www.txdot.gov. TxDOT data is public infrastructure
      information; no statutory restriction on archival of public-facing camera images
      identified. CRITICAL brief-stage requirement: enumerate camera image URL pattern
      via the DriveTexas map interface XHR layer (same discovery task as NJDOT 511,
      which required discovery via the 511nj.org map API). Brief must verify (a) camera
      image endpoint path, (b) that image polling is not rate-limited separately from
      the web UI, (c) that no camera-specific developer agreement is required (TxDOT
      does not appear to publish a developer API program, which is typical for DOT
      camera systems where images are served as direct HTTP endpoints). CONSTRAINTS §5
      check: no public archive of historical TxDOT live camera images exists — TxDOT
      does not maintain an image history, and no third-party archive service covering
      TxDOT cameras is known. Brief must confirm §5 with a specific search for any
      TxDOT historical image store or Wayback Machine coverage of camera image paths
      (Wayback does not typically archive binary image files served at rotating URLs,
      so this check is likely clear).
    estimated_size: "~80–120 GB/month raw (est. 800 cameras × 50 KB/image × 288 polls/day); ~15–25 GB/month with gzip + delta-only retention (most images identical between refresh cycles due to low-activity periods)"
    rate_limit_notes: "No published rate limits for drivetexas.org camera image endpoints. Recommend ≥5s between camera polls, single-process per-camera, total request rate ≤1 req/s across all cameras. Verify at brief stage whether camera image URLs are rate-limited at the CDN or origin separately from the web UI."
    status: promoted-to-candidate
    promoted_to: 07.216-20260505-txdot-drivetexas-cameras
    dismissed_reason: null

  - id: uspto_patent_claim_citation_corpus
    title: "USPTO Patent Grant Corpus — Structured Claim Graphs, Inventor ER & Real-time Citation Network"
    url: https://data.uspto.gov/
    discovered: 2026-05-05
    discovered_by: maximizer
    lane_hint: 4
    why_interesting: |
      The USPTO publishes weekly bulk XML for all granted patents (~350k/year) and
      published applications (~700k/year) at bulkdata.uspto.gov and via the Open Data
      Portal (data.uspto.gov). The raw data is public domain and durably archived by
      USPTO — so Lane 1 fails §5 immediately. The Lane-4 moat is the DERIVED structured
      corpus that does NOT exist as a free public dataset: (1) claim-dependency parse
      trees (each patent's independent claims + their dependent subclaims parsed into a
      scope graph, enabling prior-art intersection queries by claim scope rather than
      keyword), (2) cross-inventor entity resolution at international scale (same
      inventor filing in USPTO, EPO/PATSTAT, and PCT/WIPO under different transliterated
      name variants, different assignee affiliations, and with varying co-inventor sets
      — the USPTO's own PatentsView disambiguation covers the US corpus but not
      cross-jurisdiction inventor matching), (3) real-time weekly forward-citation
      network increments (when a newly granted patent cites an existing patent, that
      citation propagates through the citation graph immediately, enabling current-week
      patent influence scoring rather than waiting for PatentsView's quarterly refresh).
      The compound moat: claim-scope graphs + inventor ER + citation network produce
      patent-portfolio analytics that no free source currently provides. PatentsView
      (api.patentsview.org, USPTO-funded, verified HTTP 200 2026-05-05) is the closest
      free alternative but provides inventor disambiguation only for the US corpus,
      provides citations but NOT claim-dependency trees, and refreshes quarterly rather
      than weekly. Commercial competitors (PatSnap, Derwent Innovation, Orbit
      Intelligence, Innography) charge $50k–$200k+/year — structurally inaccessible to
      academic labs, solo litigators, startup patent counsel, and boutique IP analytics
      firms. Buyers: IP litigation analytics (licensing disputes, post-grant IPR
      petitions), university tech-transfer offices (portfolio management, prior-art
      clearance), startup patent counsel (freedom-to-operate analysis on current claim
      graphs), hedge funds monitoring technology race dynamics (who is filing in a
      specific technology space this week), patent brokers/aggregators (NPE portfolio
      valuation), and academic researchers (innovation economics, inventor mobility).
    known_constraints: |
      Verified live 2026-05-05. data.uspto.gov (USPTO Open Data Portal) returned
      HTTP 200 under "moat-research/0.1" UA; described as "USPTO's data platform
      that empowers you to discover and easily extract USPTO data in one place for free."
      developer.uspto.gov returned HTTP 200 (verified 2026-05-05). api.patentsview.org
      returned HTTP 301 → HTTP 200 (PatentsView API functional, verified 2026-05-05).
      ppubs.uspto.gov (patent publication search) returned HTTP 200 (verified 2026-05-05).
      robots.txt at data.uspto.gov: the SPA returns HTTP 200 with Angular HTML for all
      paths, including /robots.txt — there is no configured robots.txt file, treat as
      absent (no restriction). USPTO data is US government public domain per 17 U.S.C.
      § 105 (government works not subject to copyright). CONSTRAINTS §5 check (Lane 4):
      the RAW patent XML bulk data IS publicly archived by USPTO on a rolling basis
      (bulkdata.uspto.gov publishes weekly grant and application packages); this raw
      archive does NOT trigger Lane-4 rejection because Lane 4's moat is the DERIVED
      structured artifact (claim graphs + inventor ER + citation network), not a
      duplicate of the raw XML. The derived artifacts do not exist as free public data:
      PatentsView provides partial structured data (inventor disambiguation, citations,
      CPC classes) but does NOT include (a) claim-dependency parse trees, (b) cross-
      jurisdiction inventor ER with EPO PATSTAT or WIPO PCT, or (c) weekly-cadence
      citation network increments (PatentsView refreshes quarterly with lag). Paid
      commercial alternatives (PatSnap, Derwent, Orbit, Innography) are $50k–$200k+/year
      — not "currently-public archived sources" per project precedent (paid ≠ §5 hit).
      Brief stage must confirm: (a) bulkdata.uspto.gov is accessible without auth and
      has no restrictive robots.txt (currently blocked to this environment's network),
      (b) the weekly bulk XML schema is consistent enough for automated parsing, (c)
      EPO PATSTAT for cross-jurisdiction ER requires Espacenet bulk data access (EPO OPS
      API is free with key; OPS developer agreement must be reviewed for redistribution
      clauses at brief stage). CONSTRAINTS §3 (solo-operator sustainability) is the main
      risk: ingesting and parsing 350k patents/week at full XML depth is compute-heavy;
      the brief must specify a scope-limited initial corpus (e.g., tech-sector CPCs only,
      or post-2000 grants only) that a single server can realistically process.
    estimated_size: "~15 GB/week raw full-grant XML (USPTO publishes ~6,500 patents/week in full XML); ~2 GB/week at CPC-filtered scope; ~500 GB structured corpus (claim trees + citation graph + inventor ER) at 20-year historical depth"
    rate_limit_notes: "USPTO Open Data Portal and bulkdata.uspto.gov: no published per-request rate limit for bulk file downloads. Recommend ≥5s between batch file fetches, single-process. PatentsView API: no documented rate limit but best-practice polite usage applies. Honor any 429s with exponential backoff."
    status: promoted-to-candidate
    promoted_to: 06.911-20260505-uspto-patent-claim-citation-corpus
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

Discovery synthesis pass — 2026-05-05 (refilling wishlist; backlog was empty after the 2026-05-04 pass scored & promoted its three new candidates). Three new entries added above intentionally diversifying lane coverage into Lane 2 (`usda_aphis_animal_welfare_inspections` — politically-vulnerable capture-before-the-door-closes thesis) and Lane 5 (all three are niche-vertical: animal-welfare compliance, energy regulatory analytics, and aviation OSINT/safety respectively), satisfying the FOCUS-task requirement that at least one candidate explore an underrepresented lane (no Lane 2 or Lane 5 active before this pass; corpus was Lane 1 / 4 only). Candidates considered and dismissed in the same pass:

- **registry.faa.gov FAA Aircraft Registry bulk download** (registry.faa.gov/database/ReleasableAircraft.zip): Akamai edge returned HTTP 403 to "moat-research/0.1" UA verified 2026-05-05, AND robots.txt is blocked by the same Akamai layer (403). Even if a different UA bypassed the edge gate, the FAA publishes the registry as a complete daily-refreshed snapshot intended for public download — Lane 1 fails CONSTRAINTS §5 (snapshot-deltas reconstructible by any analyst diffing two snapshots). A Lane-4 angle (cross-licensee → beneficial-owner entity resolution across aircraft trusts, Cape Town Convention liens, registration-history graph) might survive but the Akamai gate plus the §5 reconstructibility floor pushes it below the bar for this pass. Dismissed; revisit if (a) FAA discontinues the bulk dump, (b) a clear Lane-4 ER thesis crystallizes that justifies a fresh entry, or (c) a polite alternate access path (e.g., FAA Open Data via data.gov) is identified.
- **CMS Hospital Price Transparency machine-readable files** (cms.gov/priorities/key-initiatives/hospital-price-transparency): cms.gov returned 200 on the policy-landing page; HPT enforcement remains in effect 2026-05-05. Considered as Lane 2 + 5 (politically vulnerable + niche healthcare). Dismissed at wishlist stage because the third-party aggregator landscape kills the simple-aggregation moat: dolthub.com/repositories/dolthub/hospital-price-transparency-v3 returned HTTP 200 verified 2026-05-05 — a free public Dolt repo aggregating the MRFs already exists, AND commercial competitors (Turquoise Health, Serif Health, Dolthub Trino layer) cover the structured-aggregation thesis. CONSTRAINTS §5 fails for the basic-aggregation framing (reconstructible from currently-public sources). A surviving angle would need to articulate a specific value-add over Dolthub's free corpus (e.g., higher capture cadence, finer-grained negotiated-rate normalization, hospital-by-hospital change-detection deltas, NLP over the messy free-text plan/code-description fields) — but that's a Lane-4 brief that should be filed fresh if such a thesis crystallizes, not parked here.
- **NHTSA ODI vehicle-defect complaints corpus** (api.nhtsa.gov + static.nhtsa.gov/odi/ffdd/cmpl/FLAT_CMPL.zip): both API and bulk flat-file returned HTTP 200 verified 2026-05-05; FLAT_CMPL.zip last-modified 2026-05-02 (current). Considered as Lane 4 + 5 (auto-safety niche, structured-extraction-and-cross-recall-ER moat). Dismissed because NHTSA's own flat-file already provides structured columns (VIN, make, model, year, complaint date, defect description, recall linkage where applicable) at full historical depth, refreshed within 72h — the §5 reconstructibility check fails for the basic structured-corpus framing. Surviving Lane-4 angles (NLP cluster analysis on free-text complaint narratives + temporal-escalation pattern detection across complaints-to-recall windows) are real but narrower than the corpora we currently prioritize, and a candidate brief should articulate the NLP-derived-feature thesis explicitly. Revisit only if a concrete derived-feature thesis is named.
- **OFAC SDN list daily snapshots** (sanctionslistservice.ofac.treas.gov): SDN.XML returned HTTP 200 verified 2026-05-05, last-modified 2026-05-01. Treasury OFAC publishes the canonical SDN list and maintains historical versions in an "older versions" archive. Lane 5 (sanctions/compliance) niche but §5 fails: full historical SDN diffs are reconstructible from Treasury's own archive. Dismissed; commercial sanctions-screening vendors (Refinitiv World-Check, Dow Jones Risk & Compliance, Sayari) compete on entity resolution + cross-list synthesis (UN, EU, UK OFSI, etc.) — that fused multi-jurisdiction ER play would be a Lane-4 brief if anyone wants to scope it, but file fresh.
- **USPTO PTAB decisions corpus** (data.uspto.gov ODP — was data.uspto.gov/apis/ptab-trials/search-proceedings, returned 200 with Angular shell): USPTO Open Data Portal is reachable 2026-05-05 but the PTAB API requires registered API-key access (free, similar to GTFS-RT free-token gating, not §1 auth-bypass). Considered as Lane 4 + 5 (IP litigation niche, structured-extraction + cross-petitioner ER moat). Dismissed at wishlist stage because PTAB decisions are durably archived by USPTO itself, AND the IP-litigation analytics market is well-served by commercial competitors (Docket Navigator, Patexia, Lex Machina, Anaqua, Innography) — the specific Lane-4 differentiation would need to be named (e.g., real-time petition-network-graph monitoring, cross-art-unit examiner behavior modeling, post-grant outcome prediction). Revisit if such a thesis crystallizes; file fresh rather than reviving.

Net new wishlist surface this pass: 3 candidates added (1 Lane 1+5, 1 Lane 2+5, 1 Lane 4+5 — explicit lane diversification per FOCUS-task acceptance criteria). Patterns observed: (a) Lane 2 "capture-before-the-door-closes" framing requires a distinct §5 reasoning from Lane 1 — the moat is conditional on (i) an off-platform durable archive AND (ii) the political-vulnerability premise being real, not a duplicate of currently-public records, (b) free public aggregators (Dolthub) can collapse §5 for derived-corpora theses just like the Interline/Transitland precedent does for transit, (c) Akamai-gated FAA endpoints (registry.faa.gov) may need polite-alternate-path discovery before dismissal becomes final. These will be folded into `.wolf/cerebrum.md` in iteration task T4.

Discovery synthesis pass — 2026-05-05 T2 (second pass; adding Lane 2 and Lane 4+5 entries to further diversify cluster; backlog contained 0 `backlog`-status entries after prior pass promoted all three 2026-05-05 T1 candidates). Two new entries added above (`osha_enforcement_inspection_corpus` Lane 2+5, `multi_state_insurance_dept_enforcement` Lane 4+5). Candidates considered and dismissed in the same pass:

- **CFPB Consumer Complaint Database** (consumerfinance.gov/data-research/consumer-complaints/): API returned HTTP 200 with 14.9M complaints verified 2026-05-05; robots.txt at consumerfinance.gov has specific Disallows on UI/form paths but data API paths NOT blocked. Considered as Lane 2 (CFPB faced near-shutdown in 2025; complaint database is politically sensitive). Dismissed at wishlist stage on §5 grounds: data.gov publishes the same CFPB complaint data as a bulk download dataset (`catalog.data.gov/dataset/consumer-complaint-database`), meaning the historical corpus as of the last data.gov snapshot is reconstructible by any analyst from a currently-public archived source. The incremental "between-snapshots" window (days to weeks of new complaints filed between the last data.gov dump and any future shutdown) is too thin to anchor a Lane-2 moat story. If CFPB were to STOP publishing bulk updates to data.gov while keeping the API live (i.e., the moat is access to real-time feed that data.gov can't mirror), the thesis revives; file a fresh entry if that divergence occurs.

- **Lane 3 investigation (cross-source fusion):** Evaluated four candidate cross-source fusions in this pass. None survived the §5 + cerebrum Lane-3 test:
  (1) NOAA GOES active-fire detection (FRP) × EPA AirNow PM2.5 hourly: both archived (GOES via NOAA CLASS, AirNow via EPA AQS — both with hourly timestamps); historical join reconstructible; moat if any is Lane 4 derived-feature compute, not Lane 3.
  (2) FEC campaign finance × SEC EDGAR insider trades: both fully archived with timestamps; legal/ToS risk for derivative products from EDGAR; no Lane-3 moat.
  (3) NOAA storm prediction center mesoscale convective discussions × USGS stream gauges: SPC MDC archives exist at spc.noaa.gov, USGS NWIS archives all historical; join reconstructible; same Lane-4 redirect.
  (4) EPA ECHO facility violations × BLS QCEW employment size: ECHO is the source we're separately evaluating as Lane 2; BLS QCEW is fully archived; join reconstructible from public sources.
  **Pattern confirmed:** Under the strict cerebrum Lane-3 definition, a genuine Lane-3 moat requires at least one ephemeral input (the join key is time-sensitive and at least one input is NOT preserved in a public timestamped archive). In practice all evaluated candidates had both inputs fully archived → Lane 3 resolves to Lane 4 or Lane 1. No Lane-3 wishlist entry added this pass; this is consistent with the prior iteration's observation that the corpus has 0 Lane-3 entries and no viable Lane-3 thesis has cleared §5.

Net new wishlist surface this pass: 2 candidates added (1 Lane 2+5, 1 Lane 4+5). Lane 2 cluster grows to 2 entries (USDA APHIS + OSHA). Lane 5 secondary coverage broadens. No Lane-3 entry added with explicit rationale above.

Discovery synthesis pass — 2026-05-05 T2 (Iteration 20260505T100037Z-f26efb T2; refilling wishlist with explicit lane-diversification target after the prior pass produced an L1:4, L2:2, L4:5 cluster). Three new candidates added above, all primary Lane 2 (`epa_echo_enforcement_corpus`, `msha_mine_safety_enforcement_corpus`, `nlrb_unfair_labor_practice_cases`) with Lane 5 secondary, growing the Lane-2 cluster from 2 → 5 entries and explicitly diversifying coverage away from the L1/L4 dominance. Each rests on the Lane-2 conditional-moat reasoning codified in `.wolf/cerebrum.md` 2026-05-05: (i) off-platform durable archive AND (ii) demonstrated historical precedent of source restriction/removal — citing 2017-era EPA climate-page scrubs + 2025 OECA budget cuts (ECHO), 2017–19 MSHA citation drops + reported FOIA stonewalling on fatality narratives + 2025 reorganization signals (MSHA), and 2017 Robb-era GC publication-restriction memos + 2025 NLRB quorum collapse under Wilcox v. Trump (NLRB). All three explicitly distinguish the Lane-2 moat from the bulk-data path that DOES exist publicly (EPA bulk dumps, MSHA OGI tables, NLRB primary archive + Cornell LII mirror) by carving out the politically-vulnerable detail layer (case narratives, citation reports, region-level case-tracker detail) that bulk archives summarize away or that has demonstrated restriction precedent. Candidates considered and dismissed in the same pass:

- **Lane 3 attempts (cross-source fusion):** Three candidate fusions evaluated against the cerebrum Lane-3 stress test. None survived. (1) **EPA AirNow real-time PM2.5 × USFS/NIFC active-fire detection (GOES-R):** both archived — EPA AQS preserves AirNow hourly historical, NOAA CLASS preserves GOES-R FRP detections; historical join reconstructible from public archives. (2) **USDA NASS weekly Crop Progress × NWS U.S. Drought Monitor weekly:** both archived at native cadence (NASS QuickStats API, droughtmonitor.unl.edu archive); historical join reconstructible. (3) **NWS storm warnings × FAA NOTAMs:** NWS storm warnings durably archived (Iowa State Mesonet IEM warning archive); FAA NOTAMs are NOT durably archived publicly per the existing `faa_notams_aviation_alerts` brief — but a fusion atop our own NOTAMs Lane-1 capture collapses to a Lane-4 derived feature on top of an existing brief, not a standalone Lane-3 wishlist entry. **Pattern reconfirmed:** under the strict cerebrum Lane-3 definition, every "interesting fusion" we can identify reduces to either Lane-4 derived-features (when at least one input is publicly archived) or to Lane-1 piggyback (when one input is ephemeral but already covered by an existing entry). Adding zero Lane-3 entries this pass; consistent with the prior pass observation.
- **DOL Wage and Hour Division enforcement** (dol.gov/agencies/whd): returned HTTP 403 to "moat-research/0.1" UA verified 2026-05-05 (likely Akamai-edge UA gating, similar to FAA Aircraft Registry precedent). The data appeals as a Lane-2 candidate (FLSA / overtime / wage-theft enforcement, politically vulnerable under both 2017–21 and 2025 administrations), but the apex returned 403 across the immediate verification window and a polite-alternate-path discovery would be required at brief stage. Dismissed at wishlist stage on reachability grounds; revisit if (a) a polite UA negotiation with DOL succeeds, or (b) DOL's Inspector Generals' enforcement reports surface as an alternate access path. The DOL data.gov bulk dumps for WHD enforcement may also exist and would need separate §5 evaluation before a fresh entry is added.
- **Bureau of Land Management (BLM) oil/gas/grazing lease auction results:** considered as Lane 5 primary (narrow energy + grazing-rights vertical, possibly Lane 1 if auction live data is ephemeral). Dismissed at wishlist stage because BLM publishes lease-sale results at blm.gov/programs/energy-and-minerals/oil-and-gas/leasing/lease-sales with full historical depth, AND data.gov mirrors carry the bulk data; §5 reconstructibility fails for the basic "duplicate the auction archive" framing. A surviving Lane-4 angle (parcel-level lease-history graph + cross-state operator entity resolution + production-correlated economics on top of EIA data) might exist but the §5 collapse on the basic framing pushes it below the bar for this pass; file fresh if a clear Lane-4 thesis crystallizes.
- **FAA Service Difficulty Reports (SDR)** (sdrs.faa.gov submission, drs.faa.gov public retrieval): considered as Lane 5 primary (aviation maintenance / fleet reliability niche). sdrs.faa.gov returned 503 against "moat-research/0.1" UA verified 2026-05-05; the actual public data retrieval is at drs.faa.gov/browse (HTTP 200), but FAA durably archives SDRs back to ~2008 in DRS — Lane-1 ephemeral framing fails §5. The Lane-5-primary framing would require articulating a defensible niche-vertical thesis without temporal-loss, compute-as-barrier, or political-vulnerability angle, which per cerebrum (2026-05-05 T2) "probably doesn't survive §5." A Lane-4+5 reframing (NLP cluster analysis on free-text SDR narratives, cross-aircraft-type failure-mode taxonomy, time-to-failure modeling) is plausible but overlaps with existing commercial offerings (Cirium, FlightGlobal, OEM internal databases) — the specific Lane-4 differentiation would need to be named at brief stage. Dismissed at wishlist stage; revisit if a concrete Lane-4 thesis is named.
- **CDC FluView / respiratory virus surveillance** (cdc.gov/fluview/, gis.cdc.gov/grasp/fluview/): considered as Lane 2+5 (politically vulnerable public-health infrastructure under 2025 admin reorganization of CDC + DataStream rotations). Reachable (HTTP 200 via 301 redirect from /flu/weekly/ verified 2026-05-05). cdc.gov/robots.txt allows /fluview/ (only blocks niche /flu/espanol/ and infrastructure paths). Dismissed at wishlist stage because (a) gis.cdc.gov/grasp/fluview Interactive publishes historical CSV downloads with multi-decade depth at native weekly cadence, (b) WHO FluNet collaborating-center archive carries the same data globally and is durable, (c) the off-platform Lane-2 archive would primarily duplicate the CSV exports rather than capture distinct vulnerable detail. The political-vulnerability narrative around CDC reorgs is real but the published CSVs themselves have not been demonstrated to be at restriction risk (vs. the discoverability-layer dashboards). Revisit if (a) gis.cdc.gov ceases bulk CSV publication while keeping API live, or (b) a specific surveillance product with no parallel WHO/data.gov archive is identified — file fresh.
- **DOL ETA / Coast Guard MISLE / U.S. Coast Guard incident records:** Coast Guard Homeport (homeport.uscg.mil) returned SSL certificate-expired error verified 2026-05-05 (curl error code 60); MISLE marine casualty database has well-known FOIA-only access patterns at full historical depth. Dismissed at wishlist stage on reachability + FOIA-gating grounds; revisit if Coast Guard publishes a programmatic MISLE access path or rotates the SSL cert.

Net new wishlist surface this pass: 3 candidates added, all Lane 2+5 primary, growing Lane-2 cluster 2 → 5 and explicitly diversifying away from L1/L4 dominance. Patterns observed: (a) Lane-2 conditional-moat carve-out at the detail layer — every Lane-2 brief now must explicitly identify which fields/records are bulk-archived (and therefore §5-killed) vs. which are discoverability-layer / narrative / region-level detail subject to political-restriction risk, (b) the cerebrum Lane-3 stress test is increasingly load-bearing — three Lane-3 attempts evaluated and none survived, consistent with prior pass; the strict Lane-3 definition may be effectively a null lane in practice, (c) Akamai-edge UA gating reappears (DOL WHD this pass after FAA Aircraft Registry the prior pass) — polite-alternate-path discovery should be a default brief-stage capability before dismissal becomes final, (d) Lane-5-primary continues to be hard to clear §5 alone (FAA SDR dismissed) — Lane 5 is reliably useful only as defensibility reinforcement, confirmed across two passes now. Patterns folded into `.wolf/cerebrum.md` per openwolf rules.

Discovery synthesis pass — 2026-05-05 T2 (Iteration 20260505T114726Z-af4378 T2; diversifying away from the L2 cluster which now stands at 5 entries — adding 1 Lane 1 and 1 Lane 4 to bring balance). Two new entries added above (`txdot_drivetexas_cameras` Lane 1, `uspto_patent_claim_citation_corpus` Lane 4). Lane cluster after this pass: L1: 5 entries (somd/njdot/transit-gtfsrt/faa-notams/txdot), L2: 5 entries (usda-aphis/osha/epa-echo/msha/nlrb), L4: 6 entries (flood-fusion/cslb/medical-board/ferc/insurance/uspto-patents). Candidates considered and dismissed in the same pass:

- **PHMSA Pipeline & Hazardous Materials Safety Administration** (www.phmsa.dot.gov): returned HTTP 403 to "moat-research/0.1" UA verified 2026-05-05 — Akamai-edge UA gating, consistent with the pattern seen in DOL WHD (2026-05-05 T2) and FAA Aircraft Registry (2026-05-05 T1). The data is appealing as a Lane 4+2 candidate (pipeline incident narratives, operator compliance trajectories, PHMSA politically vulnerable under deregulatory administrations), but requires polite-alternate-path discovery (data.gov bulk mirrors, PHMSA dedicated API, alternate UA negotiation) before a wishlist entry can be confirmed. Dismissed at wishlist stage on reachability grounds; revisit if (a) a polite alternate path is confirmed accessible (PHMSA does publish bulk data at phmsa.dot.gov/data-and-statistics which may be accessible via direct URL even when the Drupal front-end is Akamai-gated), (b) a concrete Lane-2 political-vulnerability precedent specific to PHMSA (not just general deregulation) is identified, or (c) the Lane-4 three-pillar test passes for a specific incident-narrative NLP thesis.
- **FFIEC CRA Performance Evaluation Reports** (www.ffiec.gov): returned HTTP 403 across apex, CRA ratings subdirectory, and robots.txt verified 2026-05-05 — same Akamai-edge gating pattern. FFIEC aggregates CRA exam reports from FDIC, OCC, and Federal Reserve for all rated banks (~1,000 exams/year), and the narrative assessments (lending test, investment test, service test) are not available in structured form anywhere free. A Lane-4 thesis (NLP extraction of narrative community-development assessments + cross-regulator bank entity resolution) might survive §5 — the raw PDFs are public record but not aggregated in structured form. Dismissed on reachability grounds; revisit if (a) individual regulator sites (fdic.gov, occ.gov, federalreserve.gov) are accessible as alternate entry points to CRA exam reports, or (b) the operator decides to scope a CRA-focused brief entry for the community development / fair lending analytics vertical.
- **NOAA/NCEI GHCN-Daily station weather archive** — verified as fully archived (data.noaa.gov, NCEI bulk CSVs, Wayback Machine). Lane 1 fails §5. No distinguishing Lane-4 angle beyond standard climate analytics that commercial providers (NOAA AWIPS, DTN, IBM Weather Company) already dominate. Dismissed without wishlist entry.
- **NIFC/IRWIN active wildfire perimeters** — NIFC publishes historical fire perimeters via ArcGIS REST (final perimeters archived by USFS FSHED). Daily operational perimeter captures during active incidents (ICS-209 situational reports) are partially archived by NIFC's GeoMAC successor. NASA FIRMS archives VIIRS/MODIS satellite fire detection continuously. No clear gap where an archival-capture moat survives §5 — either archived (satellite detections, final perimeters) or too operationally sensitive for broad-distribution use (draft ICS-209 reports). Dismissed without wishlist entry.

Net new wishlist surface this pass: 2 candidates added (1 Lane 1, 1 Lane 4), explicitly diversifying away from the L2 cluster saturation. Key observations: (a) Akamai-edge gating now blocks PHMSA and FFIEC as well as FAA Registry and DOL WHD from prior passes — a pattern of federal regulatory-agency Akamai deployments that batch-reject our standard UA; polite-alternate-path discovery (data.gov bulk, FOIA reading rooms, Drupal endpoint direct-access) should be the first-try workaround for any future federal agency returning 403 with no robots.txt, (b) NOAA GHCN and NIFC fire perimeter both dismissed quickly on §5 — the §5 check is now fast (check NCEI/data.gov for archive first, then dismiss if archived), (c) Lane 4 corpus now has 6 entries spanning contractor/medical/insurance/energy-regulatory/IP/financing verticals — well-diversified within regulatory-corpus archetype. Patterns folded into `.wolf/cerebrum.md` per openwolf rules.

Akamai-gated endpoint alternate-path re-attempt — 2026-05-05 T3. Applied the 3-step checklist (data.gov bulk mirror → FOIA reading room → direct subdomain/member-agency) to the four confirmed Akamai-gated federal endpoints:

- **FAA Aircraft Registry** (registry.faa.gov): Prior dismissal stands. The data is a daily bulk-download ZIP (ReleasableAircraft.zip) primarily archived by FAA itself and mirrored on data.gov. Even if a browser-UA workaround were found, the §5 reconstructibility test fires: FAA publishes the full registry as a daily snapshot intended for public download, so a continuous archive would simply duplicate a publicly-available bulk file. **Confirmed dismissed.** Revisit trigger: (a) FAA discontinues ReleasableAircraft.zip, (b) a Lane-4 beneficial-owner / Cape Town Convention entity-resolution thesis is scoped.

- **DOL Wage and Hour Division** (dol.gov/agencies/whd): Prior dismissal stands on reachability grounds. data.dol.gov (the same DOL data portal that serves OSHA enforcement data, which IS accessible) does not appear to carry WHD enforcement in a comparable structured bulk form — the WHD enforcement database (Whd.dol.gov/data portal) is separately Akamai-gated. OIG reading room at oig.dol.gov was not separately tested this pass. **Confirmed dismissed pending alternate-path.** Revisit trigger: (a) data.dol.gov adds a WHD enforcement endpoint analogous to the OSHA inspection endpoint (already HTTP 200), (b) OIG FOIA reading room yields structured WHD enforcement data.

- **PHMSA Pipeline & Hazardous Materials** (phmsa.dot.gov): All three checklist steps applied 2026-05-05 T3. Step 1 (data.gov): `catalog.data.gov/dataset?q=phmsa+pipeline+incident` returned 301 with empty result set on follow; no PHMSA pipeline incident flagged files found. Step 2 (FOIA reading room): `phmsa.dot.gov/about-phmsa/offices/foia-reading-room` returned HTTP 403 — same Akamai gate blocks even the FOIA path. Step 3 (direct subpath): `phmsa.dot.gov/data-and-statistics/pipeline/pipeline-incident-flagged-files` returned HTTP 403. No alternate path found across all three steps. **Confirmed dismissed.** Revisit trigger: (a) PHMSA data reaches data.gov as a separately accessible bulk endpoint, (b) a specific PHMSA open-data API separate from the Drupal front-end is identified (check `api.phmsa.dot.gov` or `portal.phmsa.dot.gov` at brief stage if this entry is revisited).

- **FFIEC CRA Performance Evaluation Reports** (ffiec.gov): **Partial alternate-path success — Lane-4 brief viable via member-agency path (2026-05-05 T3).** All three checklist steps applied:
  - Step 1 (data.gov): Not separately tested in this pass — FFIEC is not a primary data publisher and is unlikely to have a data.gov entry.
  - Step 2 (FOIA reading room): ffiec.gov fully Akamai-gated; FOIA path not separately tested.
  - Step 3 (member-agency alternates): **OCC** (occ.gov/topics/consumers-and-communities/community-development/cra-performance-evaluations/) returned **HTTP 200** — accessible. **Federal Reserve** (federalreserve.gov/apps/enforcementactions/) returned HTTP 200. OCC and Fed together cover 2 of the 3 primary FFIEC CRA exam regulators (OCC for national banks + federal thrifts, Fed for state-member banks; FDIC covers state non-member banks and was not separately tested in this pass but is likely accessible given OCC/Fed results). A Lane-4 brief that scrapes CRA exam PDFs from OCC + Fed + FDIC individually, applies NLP extraction of narrative lending-test assessments, and builds a cross-bank entity resolution graph is viable WITHOUT requiring ffiec.gov direct access. The FFIEC CRA portal itself is merely an aggregation UI on top of the same exams the individual regulators publish. **Outcome: FFIEC as a unified access point remains dismissed, but a new wishlist entry `cra_exam_narrative_corpus` (Lane 4+5, community development / fair lending analytics niche) is warranted if the operator wants to scope it.** Revisit trigger for this note: file fresh wishlist entry `cra_exam_narrative_corpus` with sources pointing at OCC, Fed, and FDIC CRA exam PDF paths; treat ffiec.gov as a convenience index, not the source.

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
