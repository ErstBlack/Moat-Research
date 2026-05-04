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
    status: backlog
    promoted_to: null
    dismissed_reason: null

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
    status: backlog
    promoted_to: null
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
    status: backlog
    promoted_to: null
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
      https://api.tidesandcurrents.noaa.gov/robots.txt returns HTTP 403 (no robots.txt
      configured on API subdomain, verified 2026-05-04). API returned live 6-minute
      water level data at station 8518750 without authentication (HTTP 200 with JSON,
      verified 2026-05-04). CO-OPS data is US government public domain. AIS data via
      MarineCadastre (marinecadastre.gov) has NOT been verified in this iteration —
      brief must fetch marinecadastre.gov/robots.txt and data license before proceeding.
      AIS from AISHub (aishub.net) also not verified — robots.txt fetch returned HTTP
      error (verified 2026-05-04); AISHub requires data-sharing agreement rather than
      open access. Recommend brief focus on MarineCadastre bulk-download path.
    estimated_size: "~5 MB/month CO-OPS component; AIS component TBD pending MarineCadastre verification"
    rate_limit_notes: "CO-OPS API: max 1 year per request, no per-minute rate limit published. AIS: bulk download only (not streaming), latency ~72h."
    status: backlog
    promoted_to: null
    dismissed_reason: null
```

## Notes for the operator

Candidates considered and rejected on hard-constraint grounds (2026-05-04 verification pass):

- **PurpleAir** (purpleair.com): robots.txt `User-agent: * Disallow: /` verified 2026-05-04 — crawling the site would violate robots.txt, triggering CONSTRAINTS.md §2. Dismissed.
- **511VA / VDOT 511** (511va.org): robots.txt `User-agent: * Disallow: /` verified 2026-05-04 — same hard-constraint violation. Dismissed.
- **Capitol Bikeshare GBFS** (gbfs.lyft.com): API endpoint returned HTTP 403 AccessDenied (verified 2026-05-04) — cannot verify constraints or access, dropped rather than dismissed; revisit if a public endpoint is found.

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
