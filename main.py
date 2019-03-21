#!/usr/bin/env python3
"""Expert System."""

import sys
from lark import Lark, Transformer, UnexpectedInput
from collections import deque, defaultdict

grammar = r"""
    ?expressions: (rule | fact | query)*

    IMPLIES: "=>"
    IFF: "<=>"
    SYMBOL: "A".."Z"
    _NEWLINE: /\r?\n/+

    value: SYMBOL

    and: statement "+" statement
    or: statement "|" statement
    xor: statement "^" statement
    not: "!" statement

    ?statement: not
              | ("(" statement ")"
              | (value | and | or | xor))

    rule: statement (IMPLIES | IFF) statement _NEWLINE?

    fact: "=" SYMBOL+ _NEWLINE?
    query: "?" SYMBOL+ _NEWLINE?

    %import common.WS_INLINE
    %ignore WS_INLINE
    _COMMENT: /#.+/ _NEWLINE
    %ignore _COMMENT
"""

RULE_GRAPH = defaultdict(lambda: [])
FACTS = {}
QUERY = deque()


class TraverseAST(Transformer):
    """Read inital state and bould graph."""

    def fact(self, items):
        """Record facts."""
        global FACTS
        for fact in items:
            FACTS[fact.value] = True

    def query(self, items):
        """Store queries."""
        global QUERY
        for query in items:
            QUERY.append(query.value)

    def rule(self, items):
        """Build rule graph."""
        global RULE_GRAPH
        if items[1].type == "IMPLIES":
            pass
            RULE_GRAPH[items[2].children[0].value].append(items[0])
        elif items[1].type == "IFF":
            pass


parser = Lark(grammar, start="expressions", parser="lalr")


def eval_node(root):
    """Traverse the AST tree evalulating the truth of the node."""
    if root.data == "value":
        return backwards_chain(root.children[0].value)
    elif root.data == "and":
        fst, snd = root.children
        return eval_node(fst) and eval_node(snd)
    elif root.data == "or":
        fst, snd = root.children
        return eval_node(fst) or eval_node(snd)
    elif root.data == "xor":
        fst, snd = root.children
        return eval_node(fst) != eval_node(snd)
    elif root.data == "not":
        return not eval_node(root.children[0])
    else:
        # Should never happen, means the AST has changed.
        assert(False)


def backwards_chain(goal):
    """Follow goals in consequence -> premise order i.e backwards."""
    # If we already know the value then return it.
    # Also prevents looping logic.
    # Can't detect impossible statements.
    if goal in FACTS:
        return FACTS[goal]

    # If we don't know the value of our goal then try to prove it using rules.
    # value starts at False
    FACTS[goal] = False
    for statement in RULE_GRAPH[goal]:
        if eval_node(statement):
            return True

    return FACTS[goal]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit("u bad")
    with open(sys.argv[1]) as f:
        source = f.read()
        try:
            tree = parser.parse(source)
            print(tree.pretty())
            tree = TraverseAST().transform(tree)
        except UnexpectedInput as e:
            print(f"Syntax error at line {e.line}, column {e.column}")
            print(e.get_context(source, 80))
    while QUERY:
        goal = QUERY.pop()
        res = backwards_chain(goal)
        print(f"{goal}: {res}")
