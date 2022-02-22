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

    def parse_rule(source, rule):
        nt, seq = rule
        fields = []
        for symbol in seq:
            if symbol in terminals:
                if symbol != next(source):
                    raise SyntaxError(f"Expected {symbol}")
                fields.append(symbol)
            else:
                state = (symbol, source.next)
                if state not in table:
                    raise SyntaxError(f"Unexpected token: {source.next}")
                fields.append(parse_rule(source, rules[table[state]]))
        return (nt, tuple(fields))

    def parse_symbol(source, symbol=rules[0][0]):
        source = LookAheadIterator(source)
        for nt, seq in rules:
            if nt != symbol:
                continue
            if source.next in prefixes[seq]:
                return parse_rule(source, (nt, seq))
        raise SyntaxError()

    return parse_symbol
