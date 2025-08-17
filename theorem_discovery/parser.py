from __future__ import annotations
from typing import List, Tuple
from .ast import Var, Not, And, Or, Impl, Iff, Formula


Token = Tuple[str, str]


def tokenize(source: str) -> List[Token]:
    s = source.strip()
    i = 0
    tokens: List[Token] = []

    def is_alpha(c: str) -> bool:
        return c.isalpha() or c == '_'

    def is_alnum(c: str) -> bool:
        return c.isalnum() or c == '_'

    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == '(':
            tokens.append(('LPAREN', c))
            i += 1
            continue
        if c == ')':
            tokens.append(('RPAREN', c))
            i += 1
            continue
        if c in ['~', '!']:
            tokens.append(('NOT', c))
            i += 1
            continue
        if c == '&':
            tokens.append(('AND', c))
            i += 1
            continue
        if c == '|':
            tokens.append(('OR', c))
            i += 1
            continue
        if c == '-':
            # expect ->
            if i + 1 < len(s) and s[i+1] == '>':
                tokens.append(('IMPL', '->'))
                i += 2
                continue
            raise SyntaxError(f"Unexpected '-' at position {i}")
        if c == '<':
            # expect <-> or <=>
            if s[i:i+3] == '<->':
                tokens.append(('IFF', '<->'))
                i += 3
                continue
            if s[i:i+3] == '<=>':
                tokens.append(('IFF', '<=>'))
                i += 3
                continue
            raise SyntaxError(f"Unexpected '<' at position {i}")
        # identifiers or keywords
        if is_alpha(c):
            j = i + 1
            while j < len(s) and is_alnum(s[j]):
                j += 1
            word = s[i:j]
            lw = word.lower()
            if lw == 'and':
                tokens.append(('AND', word))
            elif lw == 'or':
                tokens.append(('OR', word))
            elif lw == 'not':
                tokens.append(('NOT', word))
            else:
                tokens.append(('ID', word))
            i = j
            continue
        raise SyntaxError(f"Unexpected character '{c}' at position {i}")

    tokens.append(('EOF', ''))
    return tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def eat(self, kind: str) -> Token:
        tok = self.peek()
        if tok[0] != kind:
            raise SyntaxError(f"Expected {kind}, got {tok[0]}")
        self.pos += 1
        return tok

    def parse(self) -> Formula:
        node = self.parse_iff()
        if self.peek()[0] != 'EOF':
            raise SyntaxError("Unexpected input after end of formula")
        return node

    # Precedence: NOT > AND > OR > IMPL -> > IFF <->

    def parse_iff(self) -> Formula:
        node = self.parse_impl()
        while self.peek()[0] == 'IFF':
            self.eat('IFF')
            right = self.parse_impl()
            node = Iff(node, right)
        return node

    def parse_impl(self) -> Formula:
        node = self.parse_or()
        while self.peek()[0] == 'IMPL':
            self.eat('IMPL')
            right = self.parse_or()
            node = Impl(node, right)
        return node

    def parse_or(self) -> Formula:
        node = self.parse_and()
        while self.peek()[0] == 'OR':
            self.eat('OR')
            right = self.parse_and()
            node = Or(node, right)
        return node

    def parse_and(self) -> Formula:
        node = self.parse_not()
        while self.peek()[0] == 'AND':
            self.eat('AND')
            right = self.parse_not()
            node = And(node, right)
        return node

    def parse_not(self) -> Formula:
        if self.peek()[0] == 'NOT':
            self.eat('NOT')
            return Not(self.parse_not())
        return self.parse_atom()

    def parse_atom(self) -> Formula:
        tok = self.peek()
        if tok[0] == 'ID':
            name = self.eat('ID')[1]
            return Var(name)
        if tok[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_iff()
            self.eat('RPAREN')
            return node
        raise SyntaxError(f"Expected variable or '(', got {tok[0]}")


def parse_formula(s: str) -> Formula:
    return Parser(tokenize(s)).parse()