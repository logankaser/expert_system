#!/usr/bin/env python3
"""Expert System."""

import sys
from lark import Lark, Visitor, UnexpectedInput
from collections import deque, defaultdict

if "-g" in sys.argv:
    from sys import platform as sys_pf
    if sys_pf == 'darwin':
       import matplotlib
       matplotlib.use("TkAgg")
    import networkx as nx
    import matplotlib.pyplot as plt
    import warnings
    import matplotlib.cbook
    warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

GRAPH_COLORS = []

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
    fact: "=" SYMBOL* _NEWLINE?
    query: "?" SYMBOL+ _NEWLINE?
    %import common.WS_INLINE
    %ignore WS_INLINE
    _COMMENT: /#.+/ _NEWLINE?
    %ignore _COMMENT
"""

RULE_GRAPH = defaultdict(lambda: [])
FACTS = {}
QUERY = deque()


def iter_and(node):
    """Traverse and values of conclusion and return them as a list."""
    bfs = deque([node])
    and_values = []
    while bfs:
        current = bfs.popleft()
        if current.data == "value":
            and_values.append(current.children[0].value)
        elif current.data == "and":
            bfs.append(current.children[0])
            bfs.append(current.children[1])
    return and_values


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
            for v in iter_and(conclusion):
                RULE_GRAPH[v].append(rule[0])
        elif rule[1].type == "IFF":
            statement = rule[0]
            conclusion = rule[2]
            for v in iter_and(conclusion):
                RULE_GRAPH[v].append(statement)
            for v in iter_and(statement):
                RULE_GRAPH[v].append(conclusion)

def draw_graph(rule, graph):
    if rule.data == "value":
        return rule.children[0].value
    elif rule.data == "and":
        a, b = rule.children
        return draw_graph(a, graph) + " + " + draw_graph(b, graph)
    elif rule.data == "or":
        a, b = rule.children
        return draw_graph(a, graph) + " | " + draw_graph(b, graph)
    elif rule.data == "xor":
        a, b = rule.children
        return draw_graph(a, graph) + " ^ " + draw_graph(b, graph)
    elif rule.data == "not":
        return "!" + draw_graph(rule.children[0], graph)

def eval_node(node, graph):
    """Traverse the AST tree evalulating the truth of the node."""
    if node.data == "value":
        return backwards_chain(node.children[0].value, graph)
    elif node.data == "and":
        a, b = node.children
        return eval_node(a, graph) and eval_node(b, graph)
    elif node.data == "or":
        a, b = node.children
        return eval_node(a, graph) or eval_node(b, graph)
    elif node.data == "xor":
        a, b = node.children
        return eval_node(a, graph) != eval_node(b, graph)
    elif node.data == "not":
        return not eval_node(node.children[0], graph)
    else:
        # Should never happen, means the AST has changed.
        assert False


def backwards_chain(goal, graph):
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
        if eval_node(rule, graph):
            if "-g" in sys.argv[2:]:
                graph_result = draw_graph(rule, graph)
                graph.add_edge(graph_result, goal)
                for c in graph_result:
                    if c.isalpha():
                        graph.add_edge(c, graph_result)
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
            if "-p" in sys.argv[2:]:
                print("--- AST ---")
                sys.stdout.write(tree.pretty())
                sys.stdout.flush()
                print("-----------\n")
            TraverseAST().visit(tree)
        except UnexpectedInput as e:
            print(f"Syntax error at line {e.line}, column {e.column}")
            print(e.get_context(source, 80))

    graph = None
    if "-g" in sys.argv[2:]:
        graph = nx.DiGraph()
    if "-i" not in sys.argv[2:]:
        while QUERY:
            goal = QUERY.popleft()
            res = backwards_chain(goal, graph)
            print(f"{goal}: {res}")
        if "-g" in sys.argv[2:]:
            for node in graph:
                if len(node) != 1:
                    GRAPH_COLORS.append("b")
                elif node in FACTS and FACTS[node]:
                    GRAPH_COLORS.append("g")
                else:
                    GRAPH_COLORS.append("r")
            nx.draw(graph, with_labels=True, arrows=True, node_color=GRAPH_COLORS, edge_color="b")
            plt.show()
        exit(0)
    QUERY.clear()
    old_facts = FACTS.copy()
    while True:
        line = input("eps: ").upper()
        if line == "QUIT" or line == "EXIT":
            exit(0)
        if line == "RESET":
            FACTS = old_facts.copy()
            continue
        falses = [key for key, value in FACTS.items() if value is False]
        # Clear False values from cache in case they are now True
        for key in falses:
            del FACTS[key]
        try:
            parser = Lark(GRAMMAR, start="expressions", parser="lalr")
            tree = parser.parse(line)
            TraverseAST().visit(tree)
        except UnexpectedInput as e:
            print(f"Syntax error at line {e.line}, column {e.column}")
            print(e.get_context(line, 80))
        while QUERY:
            goal = QUERY.popleft()
            res = backwards_chain(goal, graph)
            print(f"{goal}: {res}")
