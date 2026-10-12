from graderprobe.normalize import normalize_answer


def test_casefold_and_whitespace():
    assert normalize_answer("  Hello   WORLD ")["normalized"] == "hello world"


def test_punctuation_stripped():
    # Em-dash removal leaves the two surrounding spaces (server behavior).
    assert normalize_answer('"Hello," — world!')["normalized"] == "hello  world"


def test_numbers_after_punctuation_strip():
    assert normalize_answer("1,000.50")["normalized"] == "100050"
    assert normalize_answer("42.0")["normalized"] == "420"
    assert normalize_answer("42,5")["normalized"] == "425"
    assert normalize_answer("-0.0")["normalized"] == "00"


def test_steps_match_server_order():
    result = normalize_answer(" Hello,  42.0 ")
    assert result["steps"] == [
        "casefold",
        "whitespace-collapse",
        "punctuation-strip",
        "number-format",
    ]
    assert result["normalized"] == "hello 420"


def test_matches_with_reference():
    assert normalize_answer(" C. ", reference="c")["matches"] is True
    assert normalize_answer(" Hello,  42.0 ", reference="hello 420")["matches"] is True
    assert normalize_answer("hi", reference="bye")["matches"] is False


def test_no_reference_means_matches_none():
    assert normalize_answer("x")["matches"] is None
