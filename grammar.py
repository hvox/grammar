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
