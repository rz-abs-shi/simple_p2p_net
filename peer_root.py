from . import Peer, Packet, PacketFactory


class PeerRoot(Peer):

    def __init__(self, address: tuple):
        super(PeerRoot, self).__init__(address)

    @property
    def is_root(self):
        return True

    def __handle_register_packet(self, packet: Packet):
        _type = packet.get_body()[0]

        if _type == Packet.REQUEST:
            sender_address = packet.get_source_server_address()
            node = self.__check_source_registered(sender_address)

            if not node:
                node = self.stream.add_node(sender_address, set_register_connection=True)

            packet = PacketFactory.new_register_packet(Packet.RESPONSE, self.address)
            node.add_message_to_out_buff(packet.get_buf())

        elif _type == Packet.RESPONSE:
            if self.is_root:
                print("Ignoring register response packet for root")
                return

        else:
            print("Ignoring invalid register packet")
