from grammar import ε, τ


def construct_table(grm):
    nonterminals, terminals = {nt for nt, _ in grm.rules}, grm.terminals
    followers, prefixes = grm.followers(), grm.prefixes()
    rules = grm.rules
    table = {}
    for i, rule in enumerate(rules):
        nt, seq = rule
        for term in prefixes[seq]:
            if term == ε:
                for term in followers[nt]:
                    table[nt, term] = i
            else:
                table[nt, term] = i
    return table
