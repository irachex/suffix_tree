# coding: utf-8

class ActivePoint:
    def __init__(self, active_node, active_edge, active_length, text):
        self.node = active_node
        self.edge_pos = active_edge
        self.length = active_length
        self.text = text

    @property
    def edge(self):
        if self.edge_pos is None:
            return None
        return self.node.get_edge(self.text[self.edge_pos])

    @property
    def edge_char(self):
        if self.edge_pos is None:
            return None
        return self.text[self.edge_pos]

    def __repr__(self):
        return 'ActivePoint(%s, %s, %s)' % (self.node.id, self.edge_char,
                                            self.length)


class Edge:
    def __init__(self, start, end, text, node):
        self.start = start
        self.end = end
        self.text = text
        self.node = node

    def split(self, split_length, current_pos, text):
        self.end = self.start + split_length
        self.node.add_edge(Edge(self.end, -1, self.text, Node()))
        self.node.add_edge(Edge(current_pos, -1, text, Node()))
        return self.node

    def length(self):
        return self.end - self.start if self.end != -1 else 999999999

    @property
    def start_char(self):
        return self.text[self.start]

    def __repr__(self):
        return self.text[self.start:self.end]


class Node:

    total = 0

    def __init__(self):
        Node.total += 1
        self.id = self.total
        self.suffix_link = None
        self.edges = {}

    def add_edge(self, e):
        self.edges[e.start_char] = e

    def get_edge(self, start_char):
        return self.edges.get(start_char)


class SuffixTree:

    def __init__(self, canonicize='$'):
        self.root = Node()
        self.canonicize = canonicize

    def build(self, text):
        text += self.canonicize
        self.active_point = ActivePoint(self.root, None, 0, text)
        self.reminder = 0

        for i, c in enumerate(text):
            self.extend(text, i, c)

    def add_suffix_link(self, node):
        if node is self.root:
            return
        if self.pre_node:
            self.pre_node.suffix_link = node
        self.pre_node = node

    def walk_down(self, edge):
        active_point = self.active_point
        if active_point.length >= edge.length():
            active_point.edge_pos += edge.length()
            active_point.length -= edge.length()
            active_point.node = edge.node
            return True
        return False

    def extend(self, text, start, c):
        self.reminder += 1
        self.pre_node = None
        active_point = self.active_point

        while self.reminder:
            if active_point.length == 0:
                active_point.edge_pos = start

            active_edge = active_point.edge
            if active_edge is None:
                active_point.node.add_edge(Edge(start, -1, text, Node()))
                self.add_suffix_link(active_point.node) # Rule 2
            else:
                if self.walk_down(active_edge): # Observation 2
                    continue
                if active_edge.text[active_edge.start + active_point.length] == c:
                    # Observation 1
                    active_point.length += 1
                    self.add_suffix_link(active_point.node)  # Observation 3
                    break

                split_node = active_edge.split(active_point.length, start, text)
                self.add_suffix_link(split_node)  # Rule 2

            self.reminder -= 1

            if active_point.node is self.root and active_point.length > 0:
                # Rule 1
                active_point.length -= 1
                active_point.edge_pos = start - self.reminder + 1
            else:
                # Rule 3
                if active_point.node.suffix_link is not None:
                    active_point.node = active_point.node.suffix_link
                else:
                    active_point.node = self.root


def export_graph(tree, write):

    def export_nodes(node):
        if node != tree.root:
            node_style = ('[label="",style=filled,fillcolor=lightgrey,'
                          'shape=circle,width=.07,height=.07]')
            if not node.edges:  # leaf
                node_style = '[label="",shape=point]'
            write('\tnode%s %s' % (node.id, node_style))
        for e in node.edges.itervalues():
            export_nodes(e.node)

    def export_edges(node):
        if node.suffix_link:
            write('\tnode%s -> node%s [label="",weight=1,style=dotted]' % (
                node.id, node.suffix_link.id))
        for e in node.edges.itervalues():
            write('\tnode%s -> node%s [label="%s",weight=3]' % (
                node.id, e.node.id, e))
            export_edges(e.node)

    write('digraph {')
    write('\trankdir = LR;')
    write('\tedge [arrowsize=0.4, fontsize=10]')
    write('\t//----- nodes -----')
    write('\tnode%s [label="",style=filled,fillcolor=lightgrey,'
          'shape=circle,width=.1,height=.1];' % tree.root.id)
    export_nodes(tree.root)
    write('\t//----- edges -----')
    export_edges(tree.root)
    write('}')


def print_func(s):
        print s


if __name__ == "__main__":
    tree = SuffixTree()
    # tree.build('abcabxabcd')
    tree.build('aab')
    tree.build('aac')
    export_graph(tree, print_func)
