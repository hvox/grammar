from dataclasses import dataclass
from typing import Any
from functools import cache
from frozendict import frozendict

ε = object()  # empty sequence of tokens
τ = object()  # end of the input


@dataclass(unsafe_hash=True)
class Grammar:
    variables: frozenset[str]
    terminals: frozenset[Any]
    rules: frozendict[str, frozenset[tuple[Any]]]
    start: str

    def __init__(self, variables, terminals, rules, start):
        self.variables = frozenset(variables)
        self.terminals = frozenset(terminals)
        self.rules = frozendict({v: frozenset(seq) for v, seq in rules.items()})
        self.start = start

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
            for nt, seq in ((v, s) for v, seqs in self.rules.items() for s in seqs):
                for first in get_prefixes(seq):
                    if first in prefixes[nt]:
                        continue
                    prefixes[nt].add(first)
                    anything_has_changed = True
            if not anything_has_changed:
                break
        prefixes[()] = {ε}
        for seq in (s for _, seqs in self.rules.items() for s in seqs):
            for i in range(len(seq)):
                prefixes[seq[i:]] = get_prefixes(seq[i:])
        return prefixes

    @property
    @cache
    def followers(self):
        prefixes = self.prefixes
        followers = {nt: set() for nt in self.variables}
        followers[self.start] = {τ}

        while True:
            updates = []
            for nt1, seq in ((v, s) for v, seqs in self.rules.items() for s in seqs):
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
