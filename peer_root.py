from . import Peer, Packet, PacketFactory
from tools.NetworkGraph import NetworkGraph


class PeerRoot(Peer):

    def __init__(self, address: tuple):
        super(PeerRoot, self).__init__(address)

        self.graph = NetworkGraph(address)

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
