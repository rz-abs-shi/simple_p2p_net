from stream import Stream
from packet import Packet, PacketFactory
from user_interface import UserInterface
from tools.Node import Node
from tools.SemiNode import SemiNode
from tools.NetworkGraph import NetworkGraph, GraphNode
import time
import threading

"""
    Peer is our main object in this project.
    In this network Peers will connect together to make a tree graph.
    This network is not completely decentralised but will show you some real-world challenges in Peer to Peer networks.
    
"""

TIME_STEP = 2


class Peer:
    def __init__(self, address: tuple):
        """
        The Peer object constructor.

        Code design suggestions:
            1. Initialise a Stream object for our Peer.
            2. Initialise a PacketFactory object.
            3. Initialise our UserInterface for interaction with user commandline.
            4. Initialise a Thread for handling reunion daemon.

        Warnings:
            1. For root Peer, we need a NetworkGraph object.
            2. In root Peer, start reunion daemon as soon as possible.
            3. In client Peer, we need to connect to the root of the network, Don't forget to set this connection
               as a register_connection.
        """

        self.address = address
        self._alive = False

        self.stream = Stream(*self.address)
        self._last_update = time.time()

        self.user_interface = UserInterface(self.address)
        self.user_interface.start()

    @property
    def is_root(self):
        return False

    def handle_user_interface_command(self, command, *args) -> bool:
        """
        :param command:
        :param args:
        :return: if handled or not
        """

        if command == UserInterface.CMD_EXIT:
            self.shutdown()
            return True

        elif command == UserInterface.CMD_MESSAGE:
            packet = PacketFactory.new_message_packet(args[0], self.address)
            self.send_broadcast_packet(packet)
            return True

    def run(self):
        """
        update loop handler
        * sleep for at most 2 seconds
        """

        while self._alive:
            now_time = time.time()
            delta = now_time - self._last_update
            self._last_update = now_time

            self.update(delta)

            sleep_time = TIME_STEP - (time.time() - now_time)
            if sleep_time > 0.0001:
                time.sleep(sleep_time)

    def update(self, delta: float):
        """
        The main loop of the program.

        Code design suggestions:
            1. Parse server in_buf of the stream.
            2. Handle all packets were received from our Stream server.
            3. Parse user_interface_buffer to make message packets.
            4. Send packets stored in nodes buffer of our Stream object.

        Warnings:
            1. At first check reunion daemon condition; Maybe we have a problem in this time
               and so we should hold any actions until Reunion acceptance.
            2. In every situation checkout Advertise Response packets; even is Reunion in failure mode or not

        :return:
        """
        
        # Handling in buffer
        for buf in self.stream.read_and_clear_in_buf():
            packet = PacketFactory.parse_buffer(buf)
            self.handle_packet(packet)

        # Handling user interface
        for buf in self.user_interface.read_and_clear_buffer():
            self.handle_user_interface_command(*buf)

        self.stream.send_out_buf_messages()

    def run_reunion_daemon(self):
        """

        In this function, we will handle all Reunion actions.

        Code design suggestions:
            1. Check if we are the network root or not; The actions are identical.
            2. If it's the root Peer, in every interval check the latest Reunion packet arrival time from every node;
               If time is over for the node turn it off (Maybe you need to remove it from our NetworkGraph).
            3. If it's a non-root peer split the actions by considering whether we are waiting for Reunion Hello Back
               Packet or it's the time to send new Reunion Hello packet.

        Warnings:
            1. If we are the root of the network in the situation that we want to turn a node off, make sure that you will not
               advertise the nodes sub-tree in our GraphNode.
            2. If we are a non-root Peer, save the time when you have sent your last Reunion Hello packet; You need this
               time for checking whether the Reunion was failed or not.
            3. For choosing time intervals you should wait until Reunion Hello or Reunion Hello Back arrival,
               pay attention that our NetworkGraph depth will not be bigger than 8. (Do not forget main loop sleep time)
            4. Suppose that you are a non-root Peer and Reunion was failed, In this time you should make a new Advertise
               Request packet and send it through your register_connection to the root; Don't forget to send this packet
               here, because in the Reunion Failure mode our main loop will not work properly and everything will be got stock!

        :return:
        """
        pass

    def send_broadcast_packet(self, broadcast_packet):
        """

        For setting broadcast packets buffer into Nodes out_buff.

        Warnings:
            1. Don't send Message packets through register_connections.

        :param broadcast_packet: The packet that should be broadcast through the network.
        :type broadcast_packet: Packet

        :return:
        """
        pass

    def handle_packet(self, packet: Packet):
        """

        This function act as a wrapper for other handle_###_packet methods to handle the packet.

        Code design suggestion:
            1. It's better to check packet validation right now; For example Validation of the packet length.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """

        _type = packet.get_type()

        if _type == packet.TYPE_REGISTER:
            self.__handle_register_packet(packet)

        elif _type == packet.TYPE_ADVERTISE:
            self.__handle_advertise_packet(packet)

        elif _type == packet.TYPE_JOIN:
            self.__handle_join_packet(packet)

        elif _type == packet.TYPE_MESSAGE:
            self.__handle_message_packet(packet)

        elif _type == packet.TYPE_REUNION:
            self.__handle_reunion_packet(packet)

        else:
            print("Ignoring invalid packet of type: %s" % _type)

    def get_register_node(self) -> Node:
        return

    def is_joined_to_parent(self):
        # TODO: check if has parent
        return self.is_root

    def __check_source_registered(self, source_address) -> Node:
        """
        If the Peer is the root of the network we need to find that is a node registered or not.

        :param source_address: Unknown IP/Port address.
        :type source_address: tuple

        :return: Node
        """
        return Node()

    def __handle_advertise_packet(self, packet):
        """
        For advertising peers in the network, It is peer discovery message.

        Request:
            We should act as the root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When an Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        Code design suggestion:
            1. Start the Reunion daemon thread when the first Advertise Response packet received.
            2. When an Advertise Response message arrived, make a new Join packet immediately for the advertised address.

        Warnings:
            1. Don't forget to ignore Advertise Request packets when you are a non-root peer.
            2. The addresses which still haven't registered to the network can not request any peer discovery message.
            3. Maybe it's not the first time that the source of the packet sends Advertise Request message. This will happen
               in rare situations like Reunion Failure. Pay attention, don't advertise the address to the packet sender
               sub-tree.
            4. When an Advertise Response packet arrived update our Peer parent for sending Reunion Packets.

        :param packet: Arrived register packet
        :type packet Packet

        :return:
        """

        _type = packet.get_body()[0]

        if _type == Packet.REQUEST:
            if not self.is_root:
                print("Ignoring advertise request packet for client")
                return

    def __handle_register_packet(self, packet: Packet):
        """
        For registration a new node to the network at first we should make a Node with stream.add_node for'sender' and
        save it.

        Code design suggestion:
            1.For checking whether an address is registered since now or not you can use SemiNode object except Node.

        Warnings:
            1. Don't forget to ignore Register Request packets when you are a non-root peer.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        raise NotImplementedError

    def __handle_join_packet(self, packet: Packet):
        """
        When a Join packet received we should add a new node to our nodes array.
        In reality, there is a security level that forbids joining every node to our network.

        :param packet: Arrived register packet.


        :type packet Packet

        :return:
        """
        pass

    def __handle_reunion_packet(self, packet):
        """
        In this function we should handle Reunion packet was just arrived.

        Reunion Hello:
            If you are root Peer you should answer with a new Reunion Hello Back packet.
            At first extract all addresses in the packet body and append them in descending order to the new packet.
            You should send the new packet to the first address in the arrived packet.
            If you are a non-root Peer append your IP/Port address to the end of the packet and send it to your parent.

        Reunion Hello Back:
            Check that you are the end node or not; If not only remove your IP/Port address and send the packet to the next
            address, otherwise you received your response from the root and everything is fine.

        Warnings:
            1. Every time adding or removing an address from packet don't forget to update Entity Number field.
            2. If you are the root, update last Reunion Hello arrival packet from the sender node and turn it on.
            3. If you are the end node, update your Reunion mode from pending to acceptance.


        :param packet: Arrived reunion packet
        :return:
        """
        pass

    def __handle_message_packet(self, packet):
        """
        Only broadcast message to the other nodes.

        Warnings:
            1. Do not forget to ignore messages from unknown sources.
            2. Make sure that you are not sending a message to a register_connection.

        :param packet: Arrived message packet

        :type packet Packet

        :return:
        """
        pass

    def __check_neighbour(self, address):
        """
        It checks is the address in our neighbours array or not.

        :param address: Unknown address

        :type address: tuple

        :return: Whether is address in our neighbours or not.
        :rtype: bool
        """
        pass

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from the network_nodes array.
        This function only will call when you are a root peer.

        Code design suggestion:
            1. Use your NetworkGraph find_live_node to find the best neighbour.

        :param sender: Sender of the packet
        :return: The specified neighbour for the sender; The format is like ('192.168.001.001', '05335').
        """
        pass

    def shutdown(self):
        self._alive = False
