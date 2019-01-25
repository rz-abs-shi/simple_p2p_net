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
        self._nodes = {}

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

        self._server = Server(*address, callback)

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
        pass

    def remove_node(self, node):
        """
        Remove the node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        pass

    def get_node_by_server(self, address: tuple) -> Node:
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param address: input address (IP, Port) tuple

        :return: The node that input address.
        :rtype: Node
        """
        pass

    def get_or_create_node_to_server(self, address: tuple, register_connection=False) -> Node:
        """
        :param address:
        :param register_connection: if set True send via register_connection node
        :return:
        """
        pass

    def add_message_to_out_buff(self, address, message):
        """
        In this function, we will add the message to the output buffer of the node that has the input address.
        Later we should use send_out_buf_messages to send these buffers into their sockets.

        :param address: Node address that we want to send the message
        :param message: Message we want to send

        Warnings:
            1. Check whether the node address is in our nodes or not.

        :return:
        """
        pass

    def read_and_clear_in_buf(self) -> list:
        in_bufs = self._server_in_buf
        self._server_in_buf = []
        return in_bufs
    
    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        Warnings:
            1. Insert an exception handler here; Maybe the node socket you want to send the message has turned off and
            you need to remove this node from stream nodes.

        :param node:
        :type node Node

        :return:
        """
        pass

    def send_out_buf_messages(self):
        """
        In this function, we will send whole out buffers to their own clients.

        :return:
        """
        for node in self._nodes:  # type: Node
            node.send_message()

    def get_nodes(self, ignore_register=False) -> list:
        pass

    def shutdown(self):
        self._server.shutdown = True


class Server(threading.Thread):

    def __init__(self, ip, port, read_callback, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.tcp_server = TCPServer(ip, port, read_callback, maximum_connections=1024)
        self.shutdown = False

    def run(self):
        while not self.shutdown:
            self.tcp_server.run()