from functools import cached_property
from itertools import chain, groupby
from re import compile as compile_re
from typing import Any, Callable, NamedTuple
from libs.list_utils import push_if_not_in
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

    @cached_property
    def get_prefixes(self) -> Callable[[str | tuple[str, ...]], set[str | None]]:
        # TODO: speed up the thing
        prefixes = {tok: {tok} for tok in self.tokens}
        prefixes |= {node: set() for node in self.nodes}

        def get_prefixes(body: str | tuple[str, ...]) -> set[str | None]:
            if isinstance(body, str):
                return prefixes[body]
            if len(body) == 0 or body[0] is None:
                return set([None])
            if None not in prefixes[body[0]]:
                return prefixes[body[0]]
            return prefixes[body[0]] - {None} | get_prefixes(body[1:])

        done = False
        while not done:
            done = True
            for head, body in self.rules:
                firsts = get_prefixes(body)
                for first in filter(lambda f: f not in prefixes[head], firsts):
                    prefixes[head].add(first)
                    done = False
        return get_prefixes

    def lr1_closure(self, core_items: set[LR1Item]) -> set[LR1Item]:
        # TODO speed up the thing by not using "while not done"
        item_set = set(core_items)  # TODO: use some cool datastructure for queues
        done = False
        while not done:
            done = True  # TODO: optimize by using queue instead of flags
            for i, item_rule, follower in list(item_set):
                # TODO: define function for tuple.get instead of this mess
                for rule in self.nodes.get((item_rule.body + (None,))[i], []):
                    for follower in self.get_prefixes(item_rule.body[i+1:] + (follower,)):
                        new_item = LR1Item(0, rule, follower)
                        if new_item not in item_set:
                            item_set.add(new_item)
                            done = False
        return item_set

    def get_clr_parsing_table(self, root_node: str):
        gotos, actions = {}, {}
        # TODO: use something more appropriate for queue
        item_sets = [{LR1Item(dot=0, rule=Rule(head=None, body=(root_node,)), follower=None)}]
        for i, item_set in enumerate(map(self.lr1_closure, item_sets)):
            # TODO: use more efficient way to find next sets
            for next_symbol in chain(self.nodes, self.tokens):
                if next_set := {
                    LR1Item(i + 1, rule, follower)
                    for i, rule, follower in item_set
                    if i < len(rule.body) and rule.body[i] == next_symbol
                }:
                    gotos[i, next_symbol] = push_if_not_in(item_sets, next_set)
        # gotos are deterministic, actions are not
        for i, item_set in enumerate(map(self.lr1_closure, item_sets)):
            for terminal, j in ((t, j) for t in self.tokens if (j := gotos.get((i, t)))):
                assert (i, terminal) not in actions, "Conflict!"
                actions[i, terminal] = ("shift", j)
            # TODO: make table generation deterministic by using something instead of set
            for item in filter(lambda item: item.dot == len(item.rule.body), item_set):
                if item.rule.head is not None:
                    assert (i, item.follower) not in actions, "Conflict!"
                    actions[i, item.follower] = ("reduce", item.rule)
                elif item.follower is None:
                    assert (i, None) not in actions, "Conflict!"
                    actions[i, None] = ("accept",)
        return actions, {k: v for k, v in gotos.items() if k[1] in self.nodes}


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
