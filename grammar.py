from lib.deterministic import DeterministicSet as set
from functools import cached_property, reduce
from typing import Iterable


class Grammar:
    rules: set[tuple[str, tuple[str, ...]]]
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
        self.rules = set(rules)
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
                if (head, term) in table:
                    raise Exception("Conflict!")
                table[head, term] = (head, body)
            if all(None in self.prefixes[symbol] for symbol in body):
                for term in self.followers[head]:
                    if (head, term) in table:
                        raise Exception("Conflict!")
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
                    if (i, terminal) in actions:
                        raise Exception("Conflict!")
                    actions[i, terminal] = ("shift", j)
            for head, j, *body in item_set:
                if j != len(body):
                    continue
                elif head is None:
                    if (i, None) in actions:
                        raise Exception("Conflict!")
                    actions[i, None] = ("accept",)
                else:
                    for follower in self.followers[head]:
                        if (i, follower) in actions:
                            raise Exception("Conflict!")
                        # TODO: use rule numbers instead of the rules themself
                        actions[i, follower] = ("reduce", head, body)
        return actions


# TODO: use pytest for tests
rules_for_ll1 = set(
    [
        ("E", ("T", "E'")),
        ("E'", ("+", "T", "E'")),
        ("E'", ()),
        ("T", ("F", "T'")),
        ("T'", ("*", "F", "T'")),
        ("T'", ()),
        ("F", ("(", "E", ")")),
        ("F", ("id",)),
    ]
)

rules_for_slr = [
    ("E", ("E", "+", "T")),
    ("E", ("T",)),
    ("T", ("T", "*", "F")),
    ("T", ("F",)),
    ("F", ("(", "E", ")")),
    ("F", ("id",)),
]

rules = rules_for_slr

g = Grammar(rules)
print(" -- prefixes --")
for symbol, prefexes in g.prefixes.items():
    print(symbol, " ::: ", " ".join(map(str, prefexes)))

print(" -- followers --")
for symbol, followers in g.followers.items():
    print(symbol, " ::: ", " ".join(map(str, followers)))

print(" -- LL(1) table --")
try:
    for state, nexts in g.construct_ll1_parsing_table().items():
        print(*state, " ::: ", *nexts)
except Exception as e:
    print(e)

print(" -- SLR table --")
for state, nexts in g.construct_slr_parsing_table().items():
    print(*state, " ::: ", *nexts)
