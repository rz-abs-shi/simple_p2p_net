from . import Peer, Packet, PacketFactory, ReunionParser
from tools.NetworkGraph import NetworkGraph


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
        _type = packet.get_body()[0:3]

        if _type == Packet.REQUEST:
            sender_address = packet.get_source_server_address()
            parent_address = self.graph.insert_node(sender_address)
            resp_packet = PacketFactory.new_advertise_packet(Packet.RESPONSE, self.address, parent_address)
            self.send_packet(sender_address, resp_packet)

        else:
            print("Ignoring advertise response packet for root")

    def __handle_reunion_packet(self, packet: Packet):
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
