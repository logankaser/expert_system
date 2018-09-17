#!/usr/bin/env python3

import re
import sys
import math
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
    """
    def __eq__(self, other):
        return False
    def __lt__(self, other):
        return False
    """

grammar = {
    "A": Token(TokenType.SYMBOL, "A"),
    "B": Token(TokenType.SYMBOL, "B"),
    "C": Token(TokenType.SYMBOL, "C"),
    "D": Token(TokenType.SYMBOL, "D"),
    "E": Token(TokenType.SYMBOL, "E"),
    "F": Token(TokenType.SYMBOL, "F"),
    "G": Token(TokenType.SYMBOL, "G"),
    "H": Token(TokenType.SYMBOL, "H"),
    "I": Token(TokenType.SYMBOL, "I"),
    "J": Token(TokenType.SYMBOL, "J"),
    "K": Token(TokenType.SYMBOL, "K"),
    "L": Token(TokenType.SYMBOL, "L"),
    "M": Token(TokenType.SYMBOL, "M"),
    "N": Token(TokenType.SYMBOL, "N"),
    "O": Token(TokenType.SYMBOL, "O"),
    "P": Token(TokenType.SYMBOL, "P"),
    "Q": Token(TokenType.SYMBOL, "Q"),
    "R": Token(TokenType.SYMBOL, "R"),
    "S": Token(TokenType.SYMBOL, "S"),
    "T": Token(TokenType.SYMBOL, "T"),
    "U": Token(TokenType.SYMBOL, "U"),
    "V": Token(TokenType.SYMBOL, "V"),
    "W": Token(TokenType.SYMBOL, "W"),
    "X": Token(TokenType.SYMBOL, "X"),
    "Y": Token(TokenType.SYMBOL, "Y"),
    "Z": Token(TokenType.SYMBOL, "Z"),
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
    tokens = deque([])
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
            elif tmp in grammar:
                tokens.append(grammar[tmp])
                tmp = ""
        tokens.append(grammar[";"])
    return tokens


def Expressify(tokens):
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
                while ops and ops[0].type != TokenType.LEFT_PAREN:
                    output.append(ops.pop())
                ops.pop()
        while ops:
            output.append(ops.pop())
        tokens.popleft()
        exps.append(output)
    return exps


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
    tokens = lex(source)
    print(" " + " ".join(map(str, tokens)))
    exps = Expressify(tokens)
    print("\n".join(map(str, exps)))


if __name__ == "__main__":
    main(sys.argv)
