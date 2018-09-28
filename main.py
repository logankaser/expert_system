#!/usr/bin/env python3

import re
import sys
import math
import itertools
from collections import deque
from enum import IntEnum, auto


class TokenType(IntEnum):
    SYMBOL = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    IMPLIES = auto()
    IMPLIES_ELSE = auto()
    INIT = auto()
    QUERY = auto()
    BREAK = auto()


class Token:
    def __init__(self, token_type, symbol=None):
        self.type = token_type
        self.symbol = symbol

    def __str__(self):
        if self.type == TokenType.BREAK:
            return "\n"
        elif self.type == TokenType.SYMBOL:
            return f"{self.type.name}({self.symbol})"
        return self.type.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.type == other.type
    """
    def __lt__(self, other):
        return False
    """


class Expression:
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent


grammar = {
    "(": Token(TokenType.LEFT_PAREN),
    ")": Token(TokenType.RIGHT_PAREN),
    "!": Token(TokenType.NOT),
    "+": Token(TokenType.AND),
    "|": Token(TokenType.OR),
    "^": Token(TokenType.XOR),
    "=>": Token(TokenType.IMPLIES),
    "<=>": Token(TokenType.IMPLIES_ELSE),
    "=": Token(TokenType.INIT),
    "?": Token(TokenType.QUERY),
    ";": Token(TokenType.BREAK)
}


def lex(file):
    tokens = deque()
    for line in file.readlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        line = deque(line.partition("#")[0].strip())
        tmp = ""
        for i in range(len(line)):
            c = line.popleft()
            if c.isspace():
                continue
            tmp += c
            if c == "=" and line and line[0] == ">":
                continue
            elif tmp.isalpha():
                tokens.append(Token(TokenType.SYMBOL, tmp))
                tmp = ""
            elif tmp in grammar:
                tokens.append(grammar[tmp])
                tmp = ""
        tokens.append(grammar[";"])
    return tokens


def to_expressions(tokens):
    exps = deque()
    tmp = []
    while tokens:
        if tokens[0].type == TokenType.BREAK:
            tokens.popleft()
            if len(tmp) > 0:
                exps.append(tmp)
            tmp = []
        else:
            tmp.append(tokens.popleft())
    return exps


def toRPN(tokens):
    exps = []
    ops = []

    while tokens:
        output = []
        while tokens and tokens[0].type != TokenType.BREAK:
            tmp = tokens.popleft()
            if tmp.type == TokenType.SYMBOL:
                output.append(tmp)
            elif tmp.type > TokenType.RIGHT_PAREN:
                ops.append(tmp)
            elif tmp.type == TokenType.LEFT_PAREN:
                ops.append(tmp)
            elif tmp.type == TokenType.RIGHT_PAREN:
                print(ops)
                while ops and ops[-1].type != TokenType.LEFT_PAREN:
                    output.append(ops.pop())
                ops.pop()
        while ops:
            output.append(ops.pop())
        tokens.popleft()
        exps.append(output)
    return exps


def parse(exps):
    errors = []

    # Rules
    rules = list(filter(lambda x: not Token(TokenType.INIT) in x and not Token(TokenType.QUERY) in x, exps))

    # Build state
    state = {}
    symbols = map(lambda l: filter(lambda x: x == Token(TokenType.SYMBOL), l), exps)
    symbols = list(itertools.chain.from_iterable(symbols))
    for x in symbols:
        state[x.symbol] = False

    # Get inital facts
    fact_exps = list(filter(lambda x: Token(TokenType.INIT) in x, exps))
    if len(fact_exps) > 1:
        errors.append("Multiple facts error")
    elif len(fact_exps) == 1:
        for x in fact_exps[0]:
            if x.type == TokenType.SYMBOL:
                state[x.symbol] = True

    # Get inital query
    query = []
    query_exps = list(filter(lambda x: Token(TokenType.QUERY) in x, exps))
    if len(query_exps) > 1:
        errors.append("Multiple query error")
    elif len(query_exps) == 1:
        query = list(filter(lambda x: x == Token(TokenType.SYMBOL), query_exps[0]))

    return (rules, state, query, errors)


def main(args):
    verbose = False
    if "-v" in args or "--verbose" in args[1:]:
        verbose = True
    if sys.stdin.isatty() and "-" in args[1:]:
        source = sys.stdin
    else:
        try:
            source_name = list(filter(
                lambda a: a != "-v" and a != "--verbose" and a != "-", args[1:]
            ))[0]
        except IndexError:
            exit("Usage: ./main.py <source_path>")
        try:
            source = open(source_name)
        except OSError:
            exit("Error opening file.")
    rules, state, query, errors = parse(to_expressions(lex(source)))
    print("Rules:\n" + "\n".join(map(str, rules)), "\n")
    print("Inital Facts:\n" + str(state), "\n")
    print("Query: " + ",".join(map(lambda x: x.symbol, query)))
    if errors:
        print(errors)


if __name__ == "__main__":
    main(sys.argv)
