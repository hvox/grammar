from .lookaheaditerators import LookAheadIterator
from dataclasses import dataclass, field
from grammar import Grammar, ε, τ
from typing import Any


def construct_table(grammar):
    nonterminals, terminals = grammar.variables, grammar.terminals
    followers, prefixes = grammar.followers, grammar.prefixes
    rules = tuple(((nt, seq) for (nt, seqs) in grammar.rules.items() for seq in seqs))
    table = {}
    for i, rule in enumerate(rules):
        nonterminal, body = rule
        for terminal in prefixes[body]:
            if terminal == ε:
                for terminal in followers[nonterminal]:
                    table[nonterminal, terminal] = i
            else:
                table[nonterminal, terminal] = i
    return table


@dataclass
class Parser:
    grammar: Grammar
    table: {(str, Any): int} = None
    actions: {str: callable} = None

    def __init__(self, grammar, table=None, actions={}):
        self.table = table or construct_table(grammar)
        self.grammar = grammar
        self.actions = actions

    def parse_symbol(self, source, symbol):
        table = self.table
        rules = tuple(((nt, seq) for (nt, seqs) in self.grammar.rules.items() for seq in seqs))
        if symbol in self.grammar.terminals:
            if symbol != source.next:
                raise SyntaxError(f"Expected {symbol}")
            return next(source)
        state = (symbol, source.next)
        print(state)
        if state not in table:
            raise SyntaxError(f"Unexpected token: {source.next}")
        rule = rules[table[state]][1]
        fields = tuple(self.parse_symbol(source, symbol) for symbol in rule)
        return self.actions.get(symbol, lambda *f: (symbol, f))(*fields)

    def parse(self, source, symbol=None):
        symbol = symbol if symbol is not None else self.grammar.start
        if not (isinstance(source, LookAheadIterator)):
            source = LookAheadIterator(source, end=τ)
        return self.parse_symbol(source, symbol)
