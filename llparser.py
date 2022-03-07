from lookaheaditerators import LookAheadIterator
from dataclasses import dataclass, field
from grammars import Grammar, ε, τ
from typing import Any


def construct_table(grammar):
    nonterminals, terminals = grammar.nonterminals, grammar.terminals
    followers, prefixes = grammar.followers(), grammar.prefixes()
    rules = grammar.rules
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
        return self.actions.get(symbol, lambda *f: f)(symbol, *fields)

    def parse(self, source, symbol=None):
        symbol = symbol if symbol is not None else self.grammar.rules[0][0]
        if not (isinstance(source, LookAheadIterator)):
            source = LookAheadIterator(source)
        return self.parse_symbol(source, symbol)
