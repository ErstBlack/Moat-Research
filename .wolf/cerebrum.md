# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-04

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

## Key Learnings

- **Composite score validation:** The somd-cameras rescore against RUBRIC.md produced 7.221, confirming the scoring formula and weights work as intended for a known-good moat. No rubric adjustments needed yet; revisit after ≥3 more lane-1 candidates are scored.
- **Robots.txt ambiguity resolution:** When an API endpoint's robots.txt contains `Disallow: /` (appears to block all programmatic access), prefer bulk-download paths that are explicitly documented and clearly allowed over live API endpoints. Applied to USGS/NWS fusion: selected NCEI bulk CSV over api.weather.gov.

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->

## Decision Log

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
