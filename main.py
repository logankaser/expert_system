#!/usr/bin/env python3

import re
import sys
import math
from collections import deque
from enum import Enum


class TokenType(Enum):
    LEFT_PAREN = 0
    RIGHT_PAREN = 1
    AND = 2
    XOR = 3
    NOT = 4
    IMPLIES = 5
    IMPLIES_ELSE = 6


class Token:
    def __init__(self, token_type):
        self.type = token_type
    def __str__(self):
        return ""
    def __repr__(self):
        return ""
    def __eq__(self, other):
        return self.d == other.d and self.c == other.c
    def __lt__(self, other):
        return self.d < other.d


def main(args):
    verbose = False
    if "-v" in args or "--verbose" in args[1:]:
        verbose = True
    inputs = []
    if sys.stdin.isatty() and "-" in args[1:]:
        inputs = sys.stdin.readlines()
    inputs += list(filter(
        lambda a: a != "-v" and a != "--verbose" and a != "-", args[1:]))
    for line in inputs:
        print(line)


if __name__ == "__main__":
    main(sys.argv)
