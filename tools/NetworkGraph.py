import time
import copy


class GraphNode:
    def __init__(self, address: tuple, parent: 'GraphNode'=None):
        """
        :param address: (ip, port)
        :type address: tuple
        :param parent: parent node
        """
        self.address = address
        self.last_seen = time.time()
        self.children = []
        self.parent = parent

    def add_child(self, child: 'GraphNode'):
        self.children.append(child)

    def update_last_seen(self):
        self.last_seen = time.time()

    def get_subtree_children(self) -> list:
        if not self.children:
            return []
        else:
            _nodes = copy.copy(self.children)
            for child in self.children:  # type: GraphNode
                _nodes += child.get_subtree_children()

            return _nodes


class NetworkGraph:
    def __init__(self, root_address: tuple):
        self.root = GraphNode(root_address)
        self.root.alive = True
        self.address_to_node_map = {}

    def find_parent_for_new_node(self, sender):
        """
        Here we should find a neighbour for the sender.
        Best neighbour is the node who is nearest the root and has not more than one child.

        Code design suggestion:
            1. Do a BFS algorithm to find the target.

        Warnings:
            1. Check whether there is sender node in our NetworkGraph or not; if exist do not return sender node or
               any other nodes in it's sub-tree.

        :param sender: The node address we want to find best neighbour for it.
        :type sender: tuple

        :return: Best neighbour for sender.
        :rtype: GraphNode
        """

        to_visit_nodes = [self.root]

        while to_visit_nodes:
            node = to_visit_nodes[0]  # type: GraphNode
            to_visit_nodes = to_visit_nodes[1:]

            if len(node.children) < 2:
                return node
            else:
                for c in node.children:
                    to_visit_nodes.append(c)

    def find_node(self, address: tuple) -> GraphNode:
        return self.address_to_node_map.get(address)

    def remove_node(self, node: GraphNode):
        """
        We remove the node and its children from graph. Because parent is more updated than its children
        :param node: The node should be deleted with its subtree
        :return:
        """

        if node.parent:
            if node in node.parent.children:
                node.parent.children.remove(node)

            node.parent = None

        if node.address in self.address_to_node_map:
            del self.address_to_node_map[node.address]

    def insert_node(self, address: tuple) -> tuple:
        """
        Search for a parent to this new node
        :param address:
        :return: address of parent
        """
        parent = self.find_parent_for_new_node(address)
        node = GraphNode(address, parent)
        parent.add_child(node)

        return parent.address

    def get_inactive_nodes(self, active_threshold):
        inactive_nodes = []

        for node in self.root.get_subtree_children():
            if node.last_seen < active_threshold:
                inactive_nodes.append(node)

        return inactive_nodes
