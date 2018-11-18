from rbnfrbnf.core.syntax_graph import *
from rbnfrbnf.utils import IdAllocator
from rbnfrbnf_pretty.d3.schema import *
from typing import Iterable, Callable, Tuple, Optional
from subprocess import check_call
import os

Identifier = object


class D3Style:

    def __init__(self):
        self.dispatchers = {
            NamedTerminal: lambda node: ('orange', repr(node), 6),
            NonTerminalEnd: lambda node: ('blue', repr(node), 6),
            UnnamedTerminal: lambda node: ('pink', repr(node), 7),
            SubRoutine: lambda node: ('teal', repr(node), 5),
            Identified: lambda node: ('red', repr(node), 6),
            TerminalEnd: lambda node: ('yellow', repr(node), 4),
            Dispatcher: lambda node: ('green', repr(node), 6)
        }

    def set(self,
            typ: type,
            apply: Callable[[Node], Tuple[Optional[str], str, int]] = None):
        """
        :param typ: type of rbnf.core.syntax_graph.Node
        :param apply: (Node) -> (color: str?, label: str, size: int)
        """
        self.dispatchers[typ] = apply


def plot_graph(nodes: Iterable[Node],
               d3_style: D3Style = None,
               width=1200,
               height=1000,
               view=False,
               port=8080):
    nodes = list(nodes)
    id_allocator = IdAllocator()
    for each in nodes:
        id_allocator.add(each)
    id = id_allocator.get_identifier
    d3_style = d3_style or D3Style()
    dispatchers = d3_style.dispatchers

    def attrs(node: Node):
        number, (color, label, size) = id(node), dispatchers[type(node)](node)
        return make_node(
            id=number, text=label, title=label, color=color, size=size)

    json_nodes = list(map(attrs, nodes))

    json_links = []
    for each in nodes:
        for parent in each.parents:
            json_links.append(
                make_link(start=id(each), end=id(parent), value=3))

    g = {
        'width': width,
        'height': height,
        'data': {
            'links': json_links,
            'nodes': json_nodes
        }
    }
    if view:
        from flask import Flask, jsonify
        app = Flask(__name__)

        filename = os.path.join(os.path.split(__file__)[0], 'index.html')
        with open(filename, 'r') as f:
            html = f.read()

        @app.route('/graph.json')
        def data():
            return jsonify(**g)

        @app.route('/')
        def index():
            return html

        app.debug = True
        check_call(fr'python -m webbrowser -t "http://127.0.0.1:{port}"')
        app.run(port=port)
