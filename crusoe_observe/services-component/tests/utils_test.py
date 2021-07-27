import pytest
import re
from services_component.utils import any_match, compile_regexes, parse_range

### any_match function
def test_any_match_empty():
    pattern_empty = []
    assert not any_match("", pattern_empty)
    assert not any_match("abc", pattern_empty)
    assert not any_match("123", pattern_empty)

def test_any_match_simple():
    pattern_simple = [re.compile(r"abc")]
    assert any_match("abc", pattern_simple)
    assert not any_match("def", pattern_simple)
    assert any_match("123abc456", pattern_simple)

def test_any_match_complex():
    pattern_complex = [re.compile(r"Abc.efG"), re.compile(r"[0-9]+")]
    assert any_match("1Abcdefg", pattern_complex)
    assert not any_match("Abcdefg", pattern_complex)
    assert any_match("xxAbcxefGyy", pattern_complex)

### compile_regexes function
def test_compile_regexes_str():
    assert compile_regexes(r"abc") == [re.compile(r"abc")]

def test_compile_regexes_list():
    assert compile_regexes([r"a", r"b", r"c"]) == [re.compile(r"a"), re.compile(r"b"), re.compile(r"c")]

### parse_range function
def test_parse_range_number():
    assert parse_range("123") == range(123, 124)
    with pytest.raises(TypeError):
        parse_range(123)

def test_parse_range_simple():
    assert parse_range("0..123") == range(0, 123)

def test_parse_range_step():
    assert parse_range("10,20..50") == range(10, 50, 10)

def test_parse_range_invalid():
    with pytest.raises(ValueError):
        parse_range("abc")
