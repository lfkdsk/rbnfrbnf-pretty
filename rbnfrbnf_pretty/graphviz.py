from rbnfrbnf.core.syntax_graph import *
from rbnfrbnf.core.utils import IdAllocator
from typing import Callable, Tuple, Optional, Iterable
from graphviz import Digraph


class GraphvizStyle:

    def __init__(self):
        self.dispatchers = {
            NamedTerminal: lambda node: (None, repr(node), 4),
            NonTerminalEnd: lambda node: ('ellipse', repr(node), 4),
            UnnamedTerminal: lambda node: (None, repr(node), 3),
            Identified: lambda node: ('circle', repr(node), 6),
            SubRoutine: lambda node: ('doublecircle', repr(node), 5),
            TerminalEnd: lambda node: ('ellipse', repr(node), 3),
            Dispatcher: lambda node: ('square', repr(node), 7)
        }

    def set(self,
            typ: type,
            apply: Callable[[Node], Tuple[Optional[str], str, int]] = None):
        """
        :param typ: type of rbnf.core.syntax_graph.Node
        :param apply: (Node) -> (shape: str, label: str, size: int)
        """
        self.dispatchers[typ] = apply


def plot_graph(nodes: Iterable[Node],
               graphviz_style: GraphvizStyle = None,
               view=False,
               filename=None,
               directory=None):
    nodes = list(nodes)

    graphviz_style = graphviz_style or GraphvizStyle()
    id_allocator = IdAllocator()
    g = Digraph()
    for each in nodes:
        id_allocator.add(each)
    id_of = id_allocator.get_identifier
    dispatchers = graphviz_style.dispatchers

    def attrs(node: Node):
        return id_of(node), dispatchers[type(node)](node)

    for number, (shape, label, _) in map(attrs, nodes):
        attrs = {'name': str(number), 'label': label}
        if shape:
            attrs['shape'] = shape
        g.node(**attrs)

    for node in nodes:
        for parent in node.parents:
            g.edge(str(id_of(node)), str(id_of(parent)))

    g.render(filename=filename, directory=directory, view=view)
    return g
