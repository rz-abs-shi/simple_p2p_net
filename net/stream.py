from tools.simpletcp.tcpserver import TCPServer

from tools.Node import Node
import threading


class Stream:

    def __init__(self, address: tuple):
        """
        The Stream object constructor.

        Code design suggestion:
            1. Make a separate Thread for your TCPServer and start immediately.

        :param address: (ip, port) 15 characters for ip + 5 characters for port
        """

        self.address = address

        self._server_in_buf = []
        self._nodes = {}  # key: (server_address, registered), value: Node

        def callback(address, queue, data):
            """
            The callback function will run when a new data received from server_buffer.

            :param address: Source address.
            :param queue: Response queue.
            :param data: The data received from the socket.
            :return:
            """
            queue.put(bytes('ACK', 'utf8'))
            self._server_in_buf.append(data)

        real_address = Node.real_address(address)
        self._server = Server(*real_address, callback)
        self._server.start()

    def get_server_address(self):
        """

        :return: Our TCPServer address
        :rtype: tuple
        """
        return self.address

    def add_node(self, server_address, set_register_connection=False) -> Node:
        """
        Will add new a node to our Stream.

        :param server_address: New node TCPServer address.
        :param set_register_connection: Shows that is this connection a register_connection or not.

        :type server_address: tuple
        :type set_register_connection: bool

        :return:
        """

        node = Node(server_address, set_register=set_register_connection)
        self._nodes[server_address, set_register_connection] = node

        return node

    def remove_node(self, node):
        """
        Remove the node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        key = None
        for _key, value in self._nodes.items():
            if value == node:
                key = _key
                break

        if key:
            del self._nodes[key]
            node.close()

    def get_node_by_server(self, address: tuple, register_connection=False) -> Node:
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param address: input address (IP, Port) tuple
        :param register_connection:

        :return: The node that input address.
        :rtype: Node
        """
        return self._nodes.get(address, register_connection)

    def get_or_create_node_to_server(self, address: tuple, register_connection=False) -> Node:
        """
        :param address:
        :param register_connection: if set True send via register_connection node
        :return:
        """
        node = self.get_node_by_server(address, register_connection)

        if not node:
            node = self.add_node(address, register_connection)

        return node

    def read_and_clear_in_buf(self) -> list:
        in_bufs = self._server_in_buf
        self._server_in_buf = []
        return in_bufs

    def send_out_buf_messages(self):
        """
        In this function, we will send whole out buffers to their own clients.

        :return:
        """
        for node in self._nodes.values():  # type: Node
            node.send_message()

    def get_nodes(self, ignore_register=False) -> list:
        if not ignore_register:
            raise NotImplementedError

        nodes = []

        for (_, registered), node in self._nodes.items():
            if not registered:
                nodes.append(node)

        return nodes

    def shutdown(self):
        self._server.close()
        self._server.join(1)
        self._server = None

        for c in self._nodes.values():  # type: Node
            c.close()


class Server(threading.Thread):

    def __init__(self, ip, port, read_callback, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.tcp_server = TCPServer(ip, port, read_callback, maximum_connections=1024)
        self.shutdown = False

    def run(self):
        while not self.shutdown:
            self.tcp_server.run()

    def close(self):
        self.shutdown = True
