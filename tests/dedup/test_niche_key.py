from mr.dedup.niche_key import normalize_niche, resolve_niche_key


def test_lowercase():
    assert normalize_niche("Aviation Alerts") == "alerts_aviation"


def test_strips_punctuation_and_collapses_whitespace():
    assert normalize_niche("Aviation, alerts!") == "alerts_aviation"


def test_sorts_tokens_alphabetically():
    assert normalize_niche("Real-Time Cameras") == "cameras_real_time"


def test_unicode_to_ascii():
    assert normalize_niche("Café Münchéñ") == "cafe_munchen"


def test_empty_input_returns_fallback():
    assert normalize_niche("") == "untagged"
    assert normalize_niche("!!!") == "untagged"


def test_alias_resolution_maps_to_canonical():
    aliases = {"alerts_aviation": ["aviation alerts", "FAA aviation", "aviation"]}
    assert resolve_niche_key("aviation alerts", aliases) == "alerts_aviation"
    assert resolve_niche_key("FAA aviation", aliases) == "alerts_aviation"
    assert resolve_niche_key("aviation", aliases) == "alerts_aviation"


def test_alias_resolution_falls_through_when_no_match():
    aliases = {"alerts_aviation": ["aviation alerts"]}
    assert resolve_niche_key("court records", aliases) == "court_records"


def test_alias_resolution_normalizes_alias_input():
    # Aliases are matched against the normalized niche, not the raw string
    aliases = {"alerts_aviation": ["aviation alerts"]}
    assert resolve_niche_key("AVIATION ALERTS!!!", aliases) == "alerts_aviation"
