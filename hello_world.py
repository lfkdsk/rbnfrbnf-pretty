from rbnfrbnf.core.tokenizer import Token, lexing
from rbnfrbnf.graph_runners.cfg.no_exc_handling import run_graph
from rbnfrbnf.bootstrap.cfg import parse
from rbnfrbnf.pgen import generate_parsing_graph_for_cfg
from rbnfrbnf.syntax_graph import get_connected_nodes
from pprint import pprint
from typing import List

from rbnfrbnf_pretty.graphviz.plot import plot_graph as plot_graphviz
from rbnfrbnf_pretty.d3.plot import plot_graph as plot_d3
grammar = """
Number  := R'\d+'
Numeric ::= Number | Number '.' Number | '-' Numeric
Add  ::= Atom ('+' Add) | Atom
Atom ::= Numeric | '(' Add ')'
"""

grammar_ast = parse(grammar).result

lexer_table, identified_nodes, all_nodes = generate_parsing_graph_for_cfg(
    grammar_ast)

tokens: List[Token] = list(
    lexing(
        filename='<test>', text='(1+1)', lexer_table=lexer_table, cast_map={}))

pprint(tokens)
pprint(run_graph(tokens, identified_nodes['Atom']))

# use graphviz
# plot_graphviz(get_connected_nodes(identified_nodes['Atom']), view=True)
plot_d3(get_connected_nodes(identified_nodes['Atom']), view=True)
