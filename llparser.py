from lookaheaditerators import LookAheadIterator
from dataclasses import dataclass
from grammar import Grammar, ε, τ


def construct_table(grm):
    nonterminals, terminals = grm.nonterminals, grm.terminals
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


@dataclass
class Parser:
    grammar: Grammar
    table: {(str, str): int}

    def __init__(self, grammar, table=None):
        self.table = table or construct_table(grammar)
        self.grammar = grammar

    def parse_symbol(self, source, symbol):
        rules, table = self.grammar.rules, self.table
        if symbol in self.grammar.terminals:
            if symbol != source.next:
                raise SyntaxError(f"Expected {symbol}")
            return next(source)
        state = (symbol, source.next)
        if state not in table:
            raise SyntaxError(f"Unexpected token: {source.next}")
        rule = rules[table[state]][1]
        fields = tuple(self.parse_symbol(source, symbol) for symbol in rule)
        return (symbol, fields)

    def parse(self, source, symbol=None):
        symbol = symbol if symbol is not None else self.grammar.rules[0][0]
        if not (isinstance(source, LookAheadIterator)):
            source = LookAheadIterator(source)
        return self.parse_symbol(source, symbol)
