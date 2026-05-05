# Wishlist dismissals — full reasoning

> On-demand reference. Not loaded into maximizer context by default. Read this file only when (a) considering re-promoting a previously dismissed source, (b) evaluating a new candidate that overlaps with a dismissed precedent, or (c) auditing the dismissal track record during calibration.
>
> WISHLIST.md keeps a one-line pointer per dismissed entry; the full `dismissed_reason` and revisit triggers live here.

## Dismissed entries (full reasoning)

### `ndbc_realtime_buoys` — NOAA NDBC Real-time Buoy Observation Files

- **URL:** https://www.ndbc.noaa.gov/data/realtime2/
- **Discovered:** 2026-05-04 | **Lane hint:** 1
- **Promoted-to (rejected):** `briefs/rejected/00.000-20260504-ndbc-realtime-buoys.md`
- **History:** `07.600-20260504-ndbc-realtime-buoys` (Lane 1, scored → rejected under CONSTRAINTS §5)

**Dismissed reason:**

Moat thesis collapsed 2026-05-04. NDBC itself publishes a complete public spectral archive at the SAME :10/:40 sub-hourly cadence as the realtime feeds:

- Monthly: `/data/swden/{Mon}/<station><MM><YYYY>.txt.gz`
- Annual:  `/data/historical/swden/<station>w<YYYY>.txt.gz`

Both open HTTP, public domain, identical column schema. Sample verifications: 41001w2024, 41001w2025 (last-mod 2026-02-11), 4100212026.txt.gz. The realtime "10–50 minute" framing was speculative; actual cadence is twice-hourly at fixed :10/:40 minutes, fully preserved in the public archive. CONSTRAINTS §5 fires → Defensibility=0 → composite 7.600 → 0.000 → auto-reject.

**Revisit only if:**
- (a) NDBC retires `/data/swden/` or `/data/historical/swden/`,
- (b) a higher-cadence stream (sub-30-min) appears that is NOT folded into history, or
- (c) a Lane-4 derived-feature thesis emerges where compute is the moat.

---

### `coops_ais_coastal_fusion` — NOAA CO-OPS Tide Gauge × AIS Vessel Position Coastal Fusion

- **URL:** https://api.tidesandcurrents.noaa.gov
- **Discovered:** 2026-05-04 | **Lane hint:** 3
- **Promoted-to:** null

**Dismissed reason:**

Both raw inputs publicly archived with timestamps. CO-OPS has its own historical API; AIS is in NOAA MarineCadastre bulk archive (`coast.noaa.gov/htdata/CMSP/AISDataHandler/{year}/`, public-domain, no robots restriction on data path). Historical time-aligned join is reconstructible by any analyst from public sources at any time. The original "millisecond-aligned join keys not preserved" claim is factually incorrect — both formats carry timestamps. CONSTRAINTS §5 → no-moat → dismiss.

**AIS bulk properties (cached):** 6–12 month publishing latency; 2025 = 81.5 GB/year daily `.csv.zst` (changed from `.zip` in 2024). AISHub live AIS requires data-sharing agreement.

**Revisit only if:**
- (a) a Lane-4 derived-artifact thesis emerges where compute (not data access) is the barrier, or
- (b) a real-time/low-latency AIS source becomes publicly accessible without a data-sharing agreement.

---

### `dc_capital_bikeshare_gbfs` — Capital Bikeshare (DC) GBFS Real-time Bike & Station Status

- **URL:** https://gbfs.lyft.com/gbfs/1.1/dca-cabi/gbfs.json
- **Discovered:** 2026-05-04 | **Lane hint:** 1
- **Promoted-to:** null

**Dismissed reason:**

Original FOCUS item 1 multi-operator fusion thesis collapsed: only 1 of 5 DDOT operators (Capital Bikeshare) survived hard-constraint + reachability checks. Lime: `robots.txt Disallow:/`. Lyft scooters DCA: stale (last_updated 2023-08-17). Helbiz: 504 (defunct, exited US 2023). Spin: 404 "Invalid feed" (DC feed retired). A single-operator CaBi-only archive is materially smaller than the cross-operator thesis (no substitution, modal share, or dwell-time-by-zone fusion). CaBi also publishes quarterly station-level trip dumps publicly, narrowing the marginal moat from a sub-minute archive.

**Revisit only if:**
- (a) Lime relaxes its `Disallow:/`,
- (b) a new operator (Veo, Bird, Helbiz successor) publishes an open DC GBFS feed, or
- (c) operator decides a CaBi-only archive merits a fresh entry on its own narrowed merits.
