from dataclasses import dataclass

ε = ()
τ = None


@dataclass
class Grammar:
    rules: [(str, (str))]
    terminals: {str}

    def prefixes(self):
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
                return prefixes

    def postfixes(self):
        rules, terminals = self.rules, self.terminals
        prefixes = self.prefixes()
        postfixes = {nt: set() for nt, _ in rules}
        postfixes[next(iter(rules))[0]] = {τ}

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
                        updates.append((postfixes[nt1], nt2))
                        continue
                    for s in get_firsts(seq[i + 1 :]):
                        if s == ε:
                            updates.append((postfixes[nt1], nt2))
                        else:
                            updates.append(({s}, nt2))
            updated = False
            for terms, nt in updates:
                for t in terms:
                    if t not in postfixes[nt]:
                        updated = True
                        postfixes[nt].add(t)
            if not updated:
                return postfixes
