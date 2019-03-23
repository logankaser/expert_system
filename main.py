#!/usr/bin/env python3
"""Expert System."""

import sys
from lark import Lark, Visitor, UnexpectedInput
from collections import deque, defaultdict

GRAMMAR = r"""
    IMPLIES: "=>"
    IFF: "<=>"
    SYMBOL: "A".."Z"
    _NEWLINE: /\r?\n/+

    ?expressions: (rule | fact | query)*

    and: statement "+" statement
    or: statement "|" statement
    xor: statement "^" statement
    not: "!" statement
    value: SYMBOL

    ?statement: not
              | "(" statement ")"
              | value
              | and
              | or
              | xor

    rule: statement (IMPLIES | IFF) statement _NEWLINE?

    fact: "=" SYMBOL+ _NEWLINE?
    query: "?" SYMBOL+ _NEWLINE?

    %import common.WS_INLINE
    %ignore WS_INLINE
    _COMMENT: /#.+/ _NEWLINE?
    %ignore _COMMENT
"""

RULE_GRAPH = defaultdict(lambda: [])
FACTS = {}
QUERY = deque()


class TraverseAST(Visitor):
    """Read inital state and build rule graph."""

    def fact(self, fact_node):
        """Record facts."""
        global FACTS
        for fact in fact_node.children:
            FACTS[fact.value] = True

    def query(self, query_node):
        """Store queries."""
        global QUERY
        for query in query_node.children:
            QUERY.append(query.value)

    def rule(self, rule_node):
        """Build rule graph."""
        rule = rule_node.children
        global RULE_GRAPH
        if rule[1].type == "IMPLIES":
            conclusion = rule[2]
            if conclusion.data == "value":
                RULE_GRAPH[conclusion.children[0].value].append(rule[0])
            elif conclusion.data == "and":
               RULE_GRAPH[conclusion.children[0].children[0].value].append(rule[0])
               RULE_GRAPH[conclusion.children[1].children[0].value].append(rule[0])
        elif rule[1].type == "IFF":
            pass


def eval_node(node):
    """Traverse the AST tree evalulating the truth of the node."""
    if node.data == "value":
        return backwards_chain(node.children[0].value)
    elif node.data == "and":
        a, b = node.children
        return eval_node(a) and eval_node(b)
    elif node.data == "or":
        a, b = node.children
        return eval_node(a) or eval_node(b)
    elif node.data == "xor":
        a, b = node.children
        return eval_node(a) != eval_node(b)
    elif node.data == "not":
        return not eval_node(node.children[0])
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
    for rule in RULE_GRAPH[goal]:
        if eval_node(rule):
            FACTS[goal] = True
            break

    return FACTS[goal]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("u bad")
    with open(sys.argv[1]) as f:
        source = f.read()
        try:
            parser = Lark(GRAMMAR, start="expressions", parser="lalr")
            tree = parser.parse(source)
            #print(tree.pretty())
            TraverseAST().visit(tree)
        except UnexpectedInput as e:
            print(f"Syntax error at line {e.line}, column {e.column}")
            print(e.get_context(source, 80))

    if not "-i" in sys.argv[2:]:
        while QUERY:
            goal = QUERY.popleft()
            res = backwards_chain(goal)
            print(f"{goal}: {res}")
    else:
        while True:
            goal = input("Query: ").upper()
            if len(goal) != 1 or not goal.isalpha():
                continue
            falses = [key for key, value in FACTS.items() if value is False]
            for key in falses:
                del FACTS[key]
            res = backwards_chain(goal)
            print(f"{goal}: {res}")
