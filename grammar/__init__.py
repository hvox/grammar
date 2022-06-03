from dataclasses import dataclass
from typing import Any
from functools import cache

ε = object()  # empty sequence of tokens
τ = object()  # end of the input


@dataclass
class Grammar:
    variables: frozenset[str]
    terminals: frozenset[Any]
    rules: tuple[(str, tuple[Any])]
    start: str

    def __init__(self, rules):
        self.rules = tuple(rules)
        self.variables = {nt for nt, _ in rules}
        symbols = {s for _, seq in rules for s in seq}
        self.terminals = {t for t in symbols if t not in self.variables}

    def __repr__(self):
        return f"Grammar({self.rules})"

    @property
    @cache
    def prefixes(self):
        prefixes = {nt: set() for nt in self.variables}

        def get_prefixes(seq):
            if len(seq) == 0:
                return {ε}
            if seq[0] in self.terminals:
                return {seq[0]}
            if ε not in prefixes[seq[0]]:
                return prefixes[seq[0]]
            return prefixes[seq[0]] - {ε} | get_prefixes(seq[1:])

        while True:
            anything_has_changed = False
            for nt, seq in self.rules:
                for first in get_prefixes(seq):
                    if first in prefixes[nt]:
                        continue
                    prefixes[nt].add(first)
                    anything_has_changed = True
            if not anything_has_changed:
                break
        prefixes[()] = {ε}
        for _, seq in self.rules:
            for i in range(len(seq)):
                prefixes[seq[i:]] = get_prefixes(seq[i:])
        return prefixes

    @property
    @cache
    def followers(self):
        prefixes = self.prefixes
        followers = {nt: set() for nt in self.variables}
        followers[next(iter(self.rules))[0]] = {τ}

        while True:
            updates = []
            for nt1, seq in self.rules:
                for i, s in enumerate(seq):
                    if s in self.terminals:
                        continue
                    nt2 = s
                    if i == len(seq) - 1:
                        updates.append((followers[nt1], nt2))
                        continue
                    for s in prefixes[seq[i + 1 :]]:
                        if s == ε:
                            updates.append((followers[nt1], nt2))
                        else:
                            updates.append(({s}, nt2))
            updated = False
            for terms, nt in updates:
                for t in terms:
                    if t not in followers[nt]:
                        updated = True
                        followers[nt].add(t)
            if not updated:
                break
        return followers

    def __eq__(u, v):
        return u.rules == v.rules

    def __hash__(self):
        return hash(self.rules)
