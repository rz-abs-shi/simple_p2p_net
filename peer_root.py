import time

from . import Peer, Packet, PacketFactory, ReunionParser
from tools.NetworkGraph import NetworkGraph


CLIENT_DISCONNECTION_DEADLINE = 30


class PeerRoot(Peer):
    def __init__(self, address: tuple):
        super(PeerRoot, self).__init__(address)

        self.graph = NetworkGraph(address)
        self.run_reunion_daemon()

    @property
    def is_root(self):
        return True

    def __handle_register_packet(self, packet: Packet):
        _type = packet.get_body()[0:3]

        if _type == Packet.REQUEST:
            sender_address = packet.get_source_server_address()
            resp_packet = PacketFactory.new_register_packet(Packet.RESPONSE, self.address)

            self.send_packet(sender_address, resp_packet, register_connection=True)
        else:
            print("Ignoring register response packet for root")

    def __handle_advertise_packet(self, packet: Packet):
        # TODO: don't advertise deleted nodes or its children
        # TODO: check if sender already in graph

        _type = packet.get_body()[0:3]

        if _type == Packet.REQUEST:
            sender_address = packet.get_source_server_address()
            parent_address = self.graph.insert_node(sender_address)
            resp_packet = PacketFactory.new_advertise_packet(Packet.RESPONSE, self.address, parent_address)
            self.send_packet(sender_address, resp_packet)

        else:
            print("Ignoring advertise response packet for root")

    def __handle_reunion_packet(self, packet: Packet):
        # TODO: don't accept reunion from disconnected peers and its children
        parser = ReunionParser(packet)

        if not parser.is_valid():
            print("Ignoring invalid reunion packet")
            return

        neighbor = parser.entries[-1]

        if not self.is_neighbour(neighbor):
            print("Ignoring reunion packet received from non neighbor")
            return

        if parser.request_type == Packet.REQUEST:
            for address in parser.entries:
                node = self.graph.find_node(address)
                if node:
                    node.update_last_seen()

            resp_packet = PacketFactory.new_reunion_packet(Packet.RESPONSE, self.address, list(reversed(parser.entries)))
            self.send_packet(neighbor, resp_packet)

        else:
            print("Ignoring reunion response packet")

    def update_reunion(self):
        active_threshold = time.time() - CLIENT_DISCONNECTION_DEADLINE

        for client in self.graph.get_inactive_nodes(active_threshold):
            self.graph.remove_node(client)
