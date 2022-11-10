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
                        actions[i, follower] = ("reduce", Rule(head, tuple(body)))
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
            for terminal, j in ((t, j) for t in self.terminals if (j := gotos.get((i, t)))):
                assert (i, terminal) not in actions, "Conflict!"
                actions[i, terminal] = ("shift", j)
            for item in filter(lambda item: item.dot == len(item.rule.body), item_set):
                if item.rule.head is not None:
                    assert (i, item.follower) not in actions, "Conflict!"
                    actions[i, item.follower] = ("reduce", item.rule)
                elif item.follower is None:
                    assert (i, None) not in actions, "Conflict!"
                    actions[i, None] = ("accept",)
        return actions, {k: v for k, v in gotos.items() if k[1] in self.variables}

    def construct_lalr_parsing_table(self):
        # total_hours_wasted_here = 6
        LR0Item = NamedTuple("LR0Item", dot=int, rule=Rule)
        LR1Item = NamedTuple("LR1Item", dot=int, rule=Rule, follower=str)

        def lr0_closure(core_items: set[LR0Item]) -> set[LR0Item]:
            item_set = set(core_items)  # TODO: use some cool datastructure for queues
            done = False
            while not done:
                done = True  # TODO: optimize by using queue instead of flags
                for i, item_rule in list(item_set):
                    if i == len(item_rule.body) or item_rule.body[i] not in self.variables:
                        continue
                    next_symbol = item_rule.body[i]
                    # TODO: optimize by per-head rules
                    for rule in filter(lambda r: r.head == next_symbol, self.rules):
                        new_item = LR0Item(0, rule)
                        if new_item not in item_set:
                            item_set.add(new_item)
                            done = False
            return item_set

        def lr1_closure(core_items: set[LR1Item]) -> set[LR1Item]:
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
                        for new_item in (LR1Item(0, rule, symbol) for symbol in followers):
                            if new_item not in item_set:
                                item_set.add(new_item)
                                done = False
            return item_set

        gotos, actions = {}, {}
        # TODO: use something more appropriate for queue
        lr0_item_sets = [{LR0Item(0, Rule(None, (self.start,)))}]
        for i, item_set in enumerate(map(lr0_closure, lr0_item_sets)):
            # TODO: use more efficient way to find next sets
            for next_symbol in self.symbols:
                if next_set := {
                    LR0Item(i + 1, rule) for i, rule in item_set
                    if i < len(rule.body) and rule.body[i] == next_symbol
                }:
                    gotos[i, next_symbol] = push_if_not_in(lr0_item_sets, next_set)
        lalr_item_sets = [set() for _ in lr0_item_sets]
        lalr_item_sets[0].add(LR1Item(0, Rule(None, (self.start,)), None))
        done = False
        while not done:
            done = True
            for (i, next_symbol), j in gotos.items():
                if not lalr_item_sets[i]:
                    continue
                item_set = lr1_closure(lalr_item_sets[i])
                next_set = {
                    LR1Item(i + 1, rule, follower) for i, rule, follower in item_set
                    if i < len(rule.body) and rule.body[i] == next_symbol
                }
                for item in next_set:
                    if item in lalr_item_sets[j]:
                        continue
                    lalr_item_sets[j].add(item)
                    done = False
        for i, item_set in enumerate(map(lr1_closure, lalr_item_sets)):
            for terminal, j in ((t, j) for t in self.terminals if (j := gotos.get((i, t)))):
                assert (i, terminal) not in actions, "Conflict!"
                actions[i, terminal] = ("shift", j)
            for item in filter(lambda item: item.dot == len(item.rule.body), item_set):
                if item.rule.head is not None:
                    assert (i, item.follower) not in actions, "Conflict!"
                    actions[i, item.follower] = ("reduce", item.rule)
                elif item.follower is None:
                    assert (i, None) not in actions, "Conflict!"
                    actions[i, None] = ("accept",)
        return actions, {k: v for k, v in gotos.items() if k[1] in self.variables}

    # TODO: IELR: Just like CLR, but with tables almost as small as LALR
    # TODO: GLR: Can parse every CFG in O(n^3), deterministic ones in O(n)
