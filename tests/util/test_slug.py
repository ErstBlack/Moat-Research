from mr.util.slug import slugify


def test_basic_lowercase_kebab():
    assert slugify("FAA NOTAMs Aviation Alerts") == "faa-notams-aviation-alerts"


def test_strips_punctuation():
    assert slugify("Real-time! Cameras (SoMD)") == "real-time-cameras-somd"


def test_max_40_chars():
    s = slugify("a" * 100)
    assert len(s) <= 40
    assert s == "a" * 40


def test_truncates_at_word_boundary():
    s = slugify("aaaaa-bbbbb-ccccc-ddddd-eeeee-ffffff-this-is-too-long")
    assert len(s) <= 40
    assert not s.endswith("-")


def test_collapses_whitespace_and_dashes():
    assert slugify("foo   bar---baz") == "foo-bar-baz"


def test_strips_non_ascii():
    assert slugify("Münchéñ café") == "munchen-cafe"


def test_empty_input_returns_fallback():
    assert slugify("") == "untitled"
    assert slugify("!!!") == "untitled"
