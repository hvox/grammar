import context
import pytest
from grammar import Grammar, ε, τ
import frozendict


@pytest.fixture
def grammar():
    return Grammar(
        {"S", "F"},
        {"OPEN", "PLUS", "CLOSE", "a"},
        {"S": {("F",), ("OPEN", "S", "PLUS", "F", "CLOSE")}, "F": {("a",)}},
        "S",
    )


def test_followers(grammar):
    assert grammar.followers == {"S": {"PLUS", τ}, "F": {"CLOSE", "PLUS", τ}}


def test_equality(grammar):
    grm1 = Grammar({"S"}, {"f"}, {"S": {("f", "f")}}, "S")
    grm2 = grammar
    grm3 = eval(repr(grm2))
    assert grm1 != grm2
    assert grm2 == grm3


def test_serialization(grammar):
    grm1 = grammar
    grm2 = eval(repr(grm1))
    assert grm1 == grm2


def test_prefixes(grammar):
    assert grammar.prefixes == {
        "S": {"a", "OPEN"},
        "F": {"a"},
        (): {ε},
        ("F",): {"a"},
        ("OPEN", "S", "PLUS", "F", "CLOSE"): {"OPEN"},
        ("S", "PLUS", "F", "CLOSE"): {"OPEN", "a"},
        ("PLUS", "F", "CLOSE"): {"PLUS"},
        ("F", "CLOSE"): {"a"},
        ("CLOSE",): {"CLOSE"},
        ("a",): {"a"},
    }
