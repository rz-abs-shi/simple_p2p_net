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

    def set_address(self, new_address: tuple):
        pass

    def __reset(self):
        pass

    def add_child(self, child: 'GraphNode'):
        pass

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

    def find_live_node(self, sender):
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
        pass

    def find_node(self, address: tuple) -> GraphNode:
        pass

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

    def add_node(self, address: tuple, parent_address: tuple):
        """
        Add a new node with node_address if it does not exist in our NetworkGraph and set its father.

        Warnings:
            1. Don't forget to set the new node as one of the father_address children.
            2. Before using this function make sure that there is a node which has father_address.

        :return:
        """
        pass

    def insert_node(self, address: tuple) -> tuple:
        """
        Search for a parent to this new node
        :param address:
        :return: address of parent
        """

    def get_inactive_nodes(self, active_threshold):
        inactive_nodes = []

        for node in self.root.get_subtree_children():
            if node.last_seen < active_threshold:
                inactive_nodes.append(node)

        return inactive_nodes
