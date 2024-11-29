class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_names = []

    def add_node(self, node):
        self.nodes.append(node)
        self.node_names.append(node.name)

    def add_edge(self, node_a, node_b):
        edge = Edge(node_a, node_b)
        self.edges.append(edge)

    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
    def get_node_names(self):
        return self.node_names


class Node:

    def __init__(self, x, y, content):
        self.name = f'{x},{y}'
        self.content = content
        self.neighbors = []

    def get_content(self):
        return self.content

class Edge:
    def __init__(self, node_a, node_b):
        self.start = node_a
        self.end = node_b
        self.name = f'{node_a.name}:{node_b.name}'