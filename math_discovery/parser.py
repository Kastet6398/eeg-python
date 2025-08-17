from __future__ import annotations
from typing import List, Tuple
from .ast import (
    Term, TIntConst, TVar, TAdd, TSub, TMul,
    Fmla, FEq, FLt, FLe, FGt, FGe, FNot, FAnd, FOr, FImpl, FIff, FForall
)

Token = Tuple[str, str]

def tokenize(s: str) -> List[Token]:
    i = 0
    tokens: List[Token] = []
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c in '()':
            tokens.append((c, c))
            i += 1
            continue
        if c == ',':
            tokens.append(('COMMA', ','))
            i += 1
            continue
        if c == ':':
            tokens.append(('COLON', ':'))
            i += 1
            continue
        if c == '.':
            tokens.append(('DOT', '.'))
            i += 1
            continue
        if c == '+':
            tokens.append(('PLUS', '+'))
            i += 1
            continue
        if c == '*':
            tokens.append(('MUL', '*'))
            i += 1
            continue
        if c == '-':
            # could be negative literal, or ->
            if i + 1 < len(s) and s[i+1] == '>':
                tokens.append(('IMPL', '->'))
                i += 2
                continue
            tokens.append(('MINUS', '-'))
            i += 1
            continue
        if c == '=':
            if i + 1 < len(s) and s[i+1] == '=':
                tokens.append(('EQ', '=='))
                i += 2
                continue
            tokens.append(('EQ', '='))
            i += 1
            continue
        if c == '<':
            if s[i:i+2] == '<=':
                tokens.append(('LE', '<='))
                i += 2
                continue
            if s[i:i+3] == '<->':
                tokens.append(('IFF', '<->'))
                i += 3
                continue
            tokens.append(('LT', '<'))
            i += 1
            continue
        if c == '>':
            if s[i:i+2] == '>=':
                tokens.append(('GE', '>='))
                i += 2
                continue
            tokens.append(('GT', '>'))
            i += 1
            continue
        if c == '|':
            tokens.append(('OR', '|'))
            i += 1
            continue
        if c == '&':
            tokens.append(('AND', '&'))
            i += 1
            continue
        if c == '!':
            tokens.append(('NOT', '!'))
            i += 1
            continue
        if c.isdigit():
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            tokens.append(('INT', s[i:j]))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i + 1
            while j < len(s) and (s[j].isalnum() or s[j] == '_'):
                j += 1
            word = s[i:j]
            lw = word.lower()
            if lw == 'forall':
                tokens.append(('FORALL', word))
            elif lw == 'exists':
                tokens.append(('EXISTS', word))
            elif lw == 'and':
                tokens.append(('AND', word))
            elif lw == 'or':
                tokens.append(('OR', word))
            elif lw == 'not':
                tokens.append(('NOT', word))
            else:
                tokens.append(('ID', word))
            i = j
            continue
        raise SyntaxError(f"Unexpected char '{c}' at {i}")
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

    def parse(self) -> Fmla:
        f = self.parse_iff()
        if self.peek()[0] != 'EOF':
            raise SyntaxError('Trailing tokens')
        return f

    # Precedence similar to propositional
    def parse_iff(self) -> Fmla:
        n = self.parse_impl()
        while self.peek()[0] == 'IFF':
            self.eat('IFF')
            r = self.parse_impl()
            n = FIff(n, r)
        return n

    def parse_impl(self) -> Fmla:
        n = self.parse_or()
        while self.peek()[0] == 'IMPL':
            self.eat('IMPL')
            r = self.parse_or()
            n = FImpl(n, r)
        return n

    def parse_or(self) -> Fmla:
        n = self.parse_and()
        while self.peek()[0] == 'OR':
            self.eat('OR')
            r = self.parse_and()
            n = FOr(n, r)
        return n

    def parse_and(self) -> Fmla:
        n = self.parse_not()
        while self.peek()[0] == 'AND':
            self.eat('AND')
            r = self.parse_not()
            n = FAnd(n, r)
        return n

    def parse_not(self) -> Fmla:
        if self.peek()[0] == 'NOT':
            self.eat('NOT')
            return FNot(self.parse_not())
        return self.parse_quant_or_atom()

    def parse_quant_or_atom(self) -> Fmla:
        t = self.peek()
        if t[0] == 'FORALL':
            self.eat('FORALL')
            vars: List[str] = []
            # vars separated by commas, terminated by ':' or '.'
            while True:
                tok = self.peek()
                if tok[0] != 'ID':
                    raise SyntaxError('Expected variable after forall')
                vars.append(self.eat('ID')[1])
                if self.peek()[0] == 'COMMA':
                    self.eat('COMMA')
                    continue
                break
            if self.peek()[0] in ('COLON', 'DOT'):
                self.pos += 1
            body = self.parse_iff()
            return FForall(vars, body)
        if t[0] == '(':  # parenthesized formula
            self.eat('(')
            node = self.parse_iff()
            self.eat(')')
            return node
        # Otherwise, a comparison over terms
        left = self.parse_term()
        op = self.peek()[0]
        if op == 'EQ':
            self.eat('EQ')
            right = self.parse_term()
            return FEq(left, right)
        if op == 'LT':
            self.eat('LT')
            right = self.parse_term()
            return FLt(left, right)
        if op == 'LE':
            self.eat('LE')
            right = self.parse_term()
            return FLe(left, right)
        if op == 'GT':
            self.eat('GT')
            right = self.parse_term()
            return FGt(left, right)
        if op == 'GE':
            self.eat('GE')
            right = self.parse_term()
            return FGe(left, right)
        raise SyntaxError('Expected comparison or forall')

    # Terms: + and - low precedence, * high precedence, unary -
    def parse_term(self) -> Term:
        n = self.parse_factor()
        while self.peek()[0] in ('PLUS', 'MINUS'):
            if self.peek()[0] == 'PLUS':
                self.eat('PLUS')
                n = TAdd(n, self.parse_factor())
            else:
                self.eat('MINUS')
                n = TSub(n, self.parse_factor())
        return n

    def parse_factor(self) -> Term:
        n = self.parse_atom_term()
        while self.peek()[0] == 'MUL':
            self.eat('MUL')
            n = TMul(n, self.parse_atom_term())
        return n

    def parse_atom_term(self) -> Term:
        tok = self.peek()
        if tok[0] == 'INT':
            val = int(self.eat('INT')[1])
            return TIntConst(val)
        if tok[0] == 'ID':
            name = self.eat('ID')[1]
            return TVar(name)
        if tok[0] == 'MINUS':
            self.eat('MINUS')
            # unary minus
            inner = self.parse_atom_term()
            return TSub(TIntConst(0), inner)
        if tok[0] == '(':
            self.eat('(')
            t = self.parse_term()
            self.eat(')')
            return t
        raise SyntaxError('Expected term')


def parse_math_formula(s: str) -> Fmla:
    return Parser(tokenize(s)).parse()