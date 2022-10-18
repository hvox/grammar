from lib.deterministic import DeterministicSet as set
from functools import cached_property, reduce
from typing import Iterable, NamedTuple
from contextlib import suppress

Rule = NamedTuple("Rule", head=str, body=tuple[str])


def push_if_not_in(xs: list, x):
    with suppress(ValueError):
        return xs.index(x)
    xs.append(x)
    return len(xs) - 1


class Grammar:
    rules: set[Rule]
    variables: set[str]
    terminals: set[str]
    symbols: set[str]  # TODO: make symbol property
    start: str

    def __init__(
        self,
        rules: Iterable[tuple[str, tuple[str, ...]]],
        variables: Iterable[str] | None = None,
        terminals: Iterable[str] | None = None,
        start: str | None = None,
    ):
        self.rules = set(Rule(head, body) for head, body in rules)
        self.start = start if start is not None else next(iter(self.rules))[0]
        self.variables = (
            set(variables) if variables is not None else set(head for head, _ in self.rules)
        )
        self.terminals = (
            set(terminals)
            if terminals is not None
            else set(t for _, b in rules for t in b if t not in self.variables)
        )
        self.symbols = self.variables | self.terminals

    @cached_property
    def prefixes(self) -> dict[str, set[str | None]]:
        prefixes = {s: set([s] if s in self.terminals else []) for s in self.symbols}

        def get_prefixes(body: tuple[str, ...]):
            if len(body) == 0:
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
        return prefixes

    @cached_property
    def followers(self) -> dict[str, set[str | None]]:
        followers = {v: set([]) for v in self.symbols}
        followers[self.start].add(None)  # None is input right endmarker.
        done = False
        while not done:
            done = True
            for head, body in self.rules:
                current_followers = followers[head]
                for symbol in reversed(body):
                    for follower in current_followers:
                        if follower not in followers[symbol]:
                            done = False
                            followers[symbol].add(follower)
                    current_followers = (
                        self.prefixes[symbol] - {None} | current_followers
                        if None in self.prefixes[symbol]
                        else self.prefixes[symbol]
                    )
        return followers

    def construct_ll1_parsing_table(self):
        table = {}
        for head, body in self.rules:
            body_prefixes = reduce(
                lambda u, v: u | v - {None} if None in v else v,
                [self.prefixes[s] for s in reversed(body)],
                set([None]),
            )
            for term in body_prefixes & self.terminals:
                assert (head, term) not in table, "Conflict!"
                table[head, term] = (head, body)
            if all(None in self.prefixes[symbol] for symbol in body):
                for term in self.followers[head]:
                    assert (head, term) not in table, "Conflict!"
                    table[head, term] = (head, body)
        return table

    def construct_slr_parsing_table(self):
        # TODO: simplify this method by splitting into functions
        item_sets = [{(None, 0, self.start)}]
        gotos = {}
        for i, item_set in enumerate(map(set, item_sets)):
            done = False
            while not done:
                done = True
                for head, j, *body in list(item_set):
                    if j >= len(body) or body[j] not in self.variables:
                        continue
                    next_symbol = body[j]
                    for head, body in self.rules:  # TODO: optimize by per-head rules
                        if head == next_symbol:
                            item = (head, 0) + tuple(body)
                            if item not in item_set:
                                item_set.add(item)
                                done = False
            # TODO: use more efficient way to find next sets
            for next_symbol in self.symbols:
                next_set = {
                    (head, i + 1) + tuple(body)
                    for head, i, *body in item_set
                    if i < len(body) and body[i] == next_symbol
                }
                if next_set:
                    if next_set not in item_sets:
                        j = len(item_sets)
                        item_sets.append(next_set)
                    else:
                        j = item_sets.index(next_set)
                    gotos[i, next_symbol] = j
        actions = {}
        for i, item_set in enumerate(map(set, item_sets)):
            done = False
            while not done:
                done = True
                for head, j, *body in list(item_set):
                    if j >= len(body) or body[j] not in self.variables:
                        continue
                    next_symbol = body[j]
                    for head, body in self.rules:  # TODO: optimize by per-head rules
                        if head == next_symbol:
                            item = (head, 0) + tuple(body)
                            if item not in item_set:
                                item_set.add(item)
                                done = False
            for terminal in self.terminals:
                if j := gotos.get((i, terminal), 0):
                    assert (i, terminal) not in actions, "Conflict!"
                    actions[i, terminal] = ("shift", j)
            for head, j, *body in item_set:
                if j != len(body):
                    continue
                elif head is None:
                    assert (i, None) not in actions, "Conflict!"
                    actions[i, None] = ("accept",)
                else:
                    for follower in self.followers[head]:
                        assert (i, follower) not in actions, "Conflict!"
                        # TODO: use rule numbers instead of the rules themself
                        actions[i, follower] = ("reduce", head, body)
        gotos = {(i, ch): j for (i, ch), j in gotos.items() if ch in self.variables}
        return actions, gotos

    def construct_clr_parsing_table(self):
        Item = NamedTuple("Item", dot=int, rule=Rule, follower=str)

        def closure(core_items: set[Item]) -> set[Item]:
            # TODO: Is it ok to define functions inside functions?
            # https://stackoverflow.com/a/38937898
            item_set = set(core_items)  # TODO: use some cool datastructure for queues
            done = False
            while not done:
                done = True  # TODO: optimize by using queue instead of flags
                for i, item_rule, follower in list(item_set):
                    if i == len(item_rule.body) or item_rule.body[i] not in self.variables:
                        continue
                    next_symbol = item_rule.body[i]
                    # TODO: optimize by per-head rules
                    for rule in filter(lambda r: r.head == next_symbol, self.rules):
                        followers = reduce(
                            lambda x, y: y - {None} | x if None in y else y,
                            map(self.prefixes.get, reversed(item_rule.body[i+1:])), {follower}
                        )
                        for new_item in (Item(0, rule, symbol) for symbol in followers):
                            if new_item not in item_set:
                                item_set.add(new_item)
                                done = False
            return item_set
        gotos, actions = {}, {}
        # TODO: use something more appropriate for queue
        item_sets = [{Item(0, Rule(None, (self.start,)), None)}]
        for i, item_set in enumerate(map(closure, item_sets)):
            # TODO: use more efficient way to find next sets
            for next_symbol in self.symbols:
                if next_set := {
                    Item(i + 1, rule, follower) for i, rule, follower in item_set
                    if i < len(rule.body) and rule.body[i] == next_symbol
                }:
                    gotos[i, next_symbol] = push_if_not_in(item_sets, next_set)
        for i, item_set in enumerate(map(closure, item_sets)):
            for terminal in self.terminals:
                if j := gotos.get((i, terminal), 0):
                    assert (i, terminal) not in actions, "Conflict!"
                    actions[i, terminal] = ("shift", j)
            for dot, rule, follower in item_set:
                if dot != len(rule.body):
                    continue
                elif rule.head is not None:
                    assert (i, follower) not in actions, "Conflict!"
                    actions[i, follower] = ("reduce", rule)
                elif follower is None:
                    assert (i, None) not in actions, "Conflict!"
                    actions[i, None] = ("accept",)
        gotos = {(i, ch): j for (i, ch), j in gotos.items() if ch in self.variables}
        return actions, gotos
