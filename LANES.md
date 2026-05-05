# LANES

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §4. If you change this file, also update the spec.

Each brief declares exactly one primary lane (and may list secondaries):

1. **Ephemeral public data** — published openly now, not archived by the publisher (the cameras pattern).
2. **Soon-to-be-restricted data** — currently open, visibly trending toward paywall/API-shutdown/regulatory closure; capture before the door closes.
3. **Cross-source fusion moats** — at least one input stream is ephemeral (not archived at the required cadence by any party), and the time-aligned join with a second source produces a fused artifact that cannot be reconstructed from either stream alone after the ephemeral window closes. **Survival condition (2026-05-05):** both inputs being publicly archived renders the historical join reconstructible by any analyst (CONSTRAINTS §5 → Defensibility=0 → auto-reject); the brief must then be re-categorized as Lane 4 (compute-as-barrier on a reconstructible join) or dismissed. In practice a surviving Lane-3 brief requires at least one ephemeral input already captured by an active Lane-1 ingestor, with the cross-source fusion as an add-on that amplifies that project's value. **Concrete hypothetical:** A Lane-1 ingestor captures DOT traffic camera frames (ephemeral, not archived). NOAA ASOS/AWOS weather station observations are durably archived by NCEI with hourly timestamps. The historical join "what did camera X look like during precipitation event Y at ASOS station Z" cannot be reconstructed after the camera frame is overwritten — the weather archive timestamp survives, but the camera frame it paired with is gone. This is a genuine Lane-3 fusion: the ephemeral component creates an irreversible join window that no analyst can close retroactively.
4. **Derived-artifact moats** — public raw exists, but the processed artifact (embeddings, OCR, transcription, structured extraction at scale) is the moat; compute is the barrier.
5. **Niche-vertical intelligence** — pick an underserved vertical and become the only entity with a clean longitudinal dataset on it.

Lane 6 (model-training corpora) is intentionally out of scope: the buyer market is concentrated and harder for a solo operator to reach.

## Lane-3 discovery track record (2026-05-05)

Seven candidate Lane-3 fusions were evaluated across four discovery passes; zero survived the §5 reconstructibility test. All failures shared the same root cause: both inputs were publicly archived with timestamps, making the historical join reconstructible by any analyst and the moat therefore Lane-4 (compute-as-barrier) or Lane-1 (capture the ephemeral input directly):

- USGS stream gauges × NWS Storm Events — both archived; re-categorized Lane 4 (flood-fusion brief 07.695)
- CO-OPS tide gauges × NOAA MarineCadastre AIS — both archived; dismissed
- NOAA GOES active-fire × EPA AirNow PM2.5 — both archived; dismissed
- FEC campaign finance × SEC EDGAR insider trades — both archived; dismissed
- NOAA SPC mesoscale discussions × USGS stream gauges — both archived; dismissed
- USDA NASS Crop Progress × NWS Drought Monitor — both archived; dismissed
- NWS storm warnings × FAA NOTAMs — NWS archived; NOTAMs already Lane-1; dismissed as Lane-4 stack, not standalone Lane-3

**Pattern:** "interesting fusion" is near-always a sign that BOTH inputs are worth tracking independently, not that the join is the moat. If the ephemeral input doesn't already have a Lane-1 ingestor, start there first — then the cross-source fusion follows naturally as a derived layer on top.
