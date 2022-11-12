from itertools import groupby
from re import compile as compile_re
from typing import Any, Callable, NamedTuple
from libs.string_utils import split_str

Rule = NamedTuple("Rule", head=str, body=tuple[str, ...])
Node = NamedTuple("Node", span=str, value=Any)
LR0Item = NamedTuple("LR0Item", dot=int, rule=Rule)
LR1Item = NamedTuple("LR1Item", dot=int, rule=Rule, follower=str)


class Syntax:
    rules: dict[Rule, Callable[..., Any]]  # children nodes -> new node value
    nodes: dict[str, dict[Rule, Callable[..., Any]]]
    tokens: dict[str, Callable[[str, int], int]]

    def __init__(
        self, rules: dict[str | Rule, Callable[..., Any]],
        tokens: dict[str, Callable[[str, int], int]] = {},
    ):
        self.rules = rules = {parse_rule(rule): f for rule, f in rules.items()}
        self.nodes = {n: dict(rs) for n, rs in groupby(rules.items(), lambda r: r[0].head)}
        self.tokens = {
            t: literal_scanner(t) for _, body in self.rules for t in body if t not in self.nodes
        } | {token: f or literal_scanner(token) for token, f in tokens.items()}

    def __str__(self):
        rules = ["rules:"] + [head + " -> " + " ".join(body) for head, body in self.rules]
        return "\n  ".join(rules) + "\ntokens: " + ", ".join(self.tokens)


def parse_rule(source: str | tuple[str, tuple[str, ...]]) -> Rule:
    if isinstance(source, str):
        head, *body = split_str(source, " ")
    else:
        head, body = source
    return Rule(head, tuple(body))


def literal_scanner(literal: str) -> Callable[[str, int], int]:
    if literal == "":
        regex = compile_re(r"\w+")
        return lambda s, i: regex.match(s, i).end - i
    return lambda source, i: len(literal) if source[i:i+len(literal)] == literal else 0
