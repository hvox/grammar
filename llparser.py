from lookaheaditerators import LookAheadIterator
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


def parser(grm):
    terminals = grm.terminals
    table = construct_table(grm)
    rules = grm.rules
    prefixes = grm.prefixes()

    def parse_symbol(source, symbol):
        if symbol in terminals:
            if symbol != source.next:
                raise SyntaxError(f"Expected {symbol}")
            return next(source)
        state = (symbol, source.next)
        if state not in table:
            raise SyntaxError(f"Unexpected token: {source.next}")
        fields = tuple(parse_symbol(source, s) for s in rules[table[state]][1])
        return (symbol, fields)

    return lambda src, sm=rules[0][0]: parse_symbol(LookAheadIterator(src), sm)
