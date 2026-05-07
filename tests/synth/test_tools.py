from mr.synth.tools import (
    CUSTOM_TOOL_DEFS,
    NATIVE_TOOL_DEFS,
    tools_for_command,
)


def test_native_tools_have_anthropic_types():
    assert NATIVE_TOOL_DEFS["web_search"]["type"] == "web_search_20260209"
    assert NATIVE_TOOL_DEFS["web_fetch"]["type"] == "web_fetch_20260209"
    assert NATIVE_TOOL_DEFS["code_execution"]["type"] == "code_execution_20260209"


def test_custom_seen_lookup_schema():
    seen_lookup = CUSTOM_TOOL_DEFS["seen_lookup"]
    assert seen_lookup["name"] == "seen_lookup"
    schema = seen_lookup["input_schema"]
    assert schema["type"] == "object"
    assert "slug" in schema["properties"]
    assert "source_set" in schema["properties"]
    assert "lane_niche" in schema["properties"]


def test_tools_for_discover_has_seen_lookup_search_fetch_code_wayback():
    tools = tools_for_command("discover", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "web_search_20260209" in names
    assert "web_fetch_20260209" in names
    assert "code_execution_20260209" in names
    assert "seen_lookup" in names
    assert "wayback_check" in names
    assert "firecrawl_scrape" not in names


def test_tools_for_score_excludes_web_search():
    tools = tools_for_command("score", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "web_search_20260209" not in names
    assert "web_fetch_20260209" in names
    assert "wayback_check" in names
    assert "robots_check" in names
    assert "head_check" in names


def test_tools_for_wishlist_expand_includes_seen_lookup():
    tools = tools_for_command("wishlist_expand", firecrawl_available=False)
    names = {t.get("name", t.get("type")) for t in tools}
    assert "seen_lookup" in names
    assert "web_search_20260209" in names


def test_firecrawl_only_when_available():
    tools_with = tools_for_command("discover", firecrawl_available=True)
    names_with = {t.get("name", t.get("type")) for t in tools_with}
    assert "firecrawl_scrape" in names_with
