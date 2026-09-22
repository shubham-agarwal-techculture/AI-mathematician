import json

import pytest

from aimath.textutil import (
    extract_tactics,
    find_banned,
    is_trivial,
    parse_conjectures,
    parse_json_blob,
)


def test_sorry_and_admit_are_banned():
    assert find_banned("exact sorry") == "sorry"
    assert find_banned("  admit") == "admit"


def test_sorry_inside_comment_or_string_is_allowed():
    assert find_banned("-- sorry\nsimp") is None
    assert find_banned("/- admit -/\nrfl") is None
    assert find_banned('exact "sorry"') is None


def test_trivial_goals():
    assert is_trivial(" True ")
    assert is_trivial("False")
    assert not is_trivial("∀ n : Nat, n = n")


def test_extract_tactics_from_json_and_fences():
    assert extract_tactics('{"tactics": "simp [Nat.add_zero]"}') == "simp [Nat.add_zero]"
    assert extract_tactics("```lean\nrfl\n```") == "rfl"


def test_parse_conjectures():
    raw = json.dumps({"conjectures": ["∀ n : Nat, n = n", "True"]})
    assert parse_conjectures(raw) == ["∀ n : Nat, n = n", "True"]


def test_parse_json_blob_rejects_prose():
    with pytest.raises(json.JSONDecodeError):
        parse_json_blob("no json here")
