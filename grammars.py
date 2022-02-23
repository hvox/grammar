from dataclasses import dataclass

ε = ()
τ = None


@dataclass
class Grammar:
    rules: ((str, (str)),)
    terminals: {str}
    nonterminals: {str}
    cached_prefixes: {str: {str}} = None
    cached_followers: {str: {str}} = None

    def __init__(self, rules):
        self.rules = tuple(rules)
        self.nonterminals = {nt for nt, _ in rules}
        symbols = {s for _, seq in rules for s in seq}
        self.terminals = {t for t in symbols if t not in self.nonterminals}

    def __repr__(self):
        return f"Grammar({self.rules})"

    def prefixes(self, nonterminal=None):
        if self.cached_prefixes is None:
            self.update_prefixes()
        if nonterminal is None:
            return self.cached_prefixes
        return self.cached_prefixes[nonterminal]

    def update_prefixes(self):
        prefixes = {nt: set() for nt in self.nonterminals}

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
                for _, seq in self.rules:
                    prefixes[seq] = get_prefixes(seq)
                self.cached_prefixes = prefixes
                return

    def followers(self, nonterminal=None):
        if self.cached_followers is None:
            self.update_followers()
        if nonterminal is None:
            return self.cached_followers
        return self.cached_followers[nonterminal]

    def update_followers(self):
        prefixes = self.prefixes()
        followers = {nt: set() for nt in self.nonterminals}
        followers[next(iter(self.rules))[0]] = {τ}

        def get_prefixes(seq):
            if len(seq) == 0:
                return {ε}
            if seq[0] in self.terminals:
                return {seq[0]}
            if ε not in prefixes[seq[0]]:
                return prefixes[seq[0]]
            return prefixes[seq[0]] - {ε} | get_prefixes(seq[1:])

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
                    for s in get_prefixes(seq[i + 1 :]):
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

    def __eq__(u, v):
        return u.rules == v.rules

    def __hash__(self):
        return hash(self.rules)
