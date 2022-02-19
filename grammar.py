from dataclasses import dataclass

ε = ()
τ = None


@dataclass
class Grammar:
    rules: ((str, (str)),)
    terminals: {str}
    cached_prefixes: {str: {str}} = None
    cached_followers: {str: {str}} = None

    def __init__(self, rules, terminals):
        self.rules = tuple(rules)
        self.terminals = frozenset(terminals)

    def prefixes(self, nonterminal=None):
        if self.cached_prefixes is None:
            self.update_prefixes()
        if nonterminal is None:
            return self.cached_prefixes
        return self.cached_prefixes[nonterminal]

    def update_prefixes(self):
        rules, terminals = self.rules, self.terminals
        prefixes = {nt: set() for nt, _ in rules}

        def get_firsts(seq):
            if len(seq) == 0:
                return {ε}
            if seq[0] in terminals:
                return {seq[0]}
            if ε not in prefixes[seq[0]]:
                return prefixes[seq[0]]
            return prefixes[seq[0]] - {ε} | get_firsts(seq[1:])

        while True:
            anything_has_changed = False
            for nt, seq in rules:
                for first in get_firsts(seq):
                    if first in prefixes[nt]:
                        continue
                    prefixes[nt].add(first)
                    anything_has_changed = True
            if not anything_has_changed:
                self.cached_prefixes = prefixes
                return

    def followers(self, nonterminal=None):
        if self.cached_followers is None:
            self.update_followers()
        if nonterminal is None:
            return self.cached_followers
        return self.cached_followers[nonterminal]

    def update_followers(self):
        rules, terminals = self.rules, self.terminals
        prefixes = self.prefixes()
        followers = {nt: set() for nt, _ in rules}
        followers[next(iter(rules))[0]] = {τ}

        def get_firsts(seq):
            if len(seq) == 0:
                return {ε}
            if seq[0] in terminals:
                return {seq[0]}
            if ε not in prefixes[seq[0]]:
                return prefixes[seq[0]]
            return prefixes[seq[0]] - {ε} | get_firsts(seq[1:])

        while True:
            updates = []
            for nt1, seq in rules:
                for i, s in enumerate(seq):
                    if s in terminals:
                        continue
                    nt2 = s
                    if i == len(seq) - 1:
                        updates.append((followers[nt1], nt2))
                        continue
                    for s in get_firsts(seq[i + 1 :]):
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
                self.cached_followers = followers
                return

    def __hash__(self):
        return hash((self.rules, self.terminals))
