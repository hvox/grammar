ε = ()
τ = None


class Grammar:
    def __init__(self, rules, terminals):
        self.rules = rules
        self.terminals = terminals

    def starts(self):
        rules, terminals = self.rules, self.terminals
        starts = {nt: set() for nt, _ in rules}

        def get_firsts(seq):
            if len(seq) == 0:
                return {ε}
            if seq[0] in terminals:
                return seq[0]
            if ε not in starts[seq[0]]:
                return starts[seq[0]]
            return starts[seq[0]] - {ε} | get_firsts(seq[1:])

        while True:
            anything_has_changed = False
            for nt, seq in rules:
                for first in get_firsts(seq):
                    if first in starts[nt]:
                        continue
                    starts[nt].add(first)
                    anything_has_changed = True
            if not anything_has_changed:
                return starts
