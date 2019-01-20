from . import UserInterface, Peer, PacketFactory, Packet


class PeerClient(Peer):
    def __init__(self, address: tuple, root_address: tuple):
        super(PeerClient, self).__init__(address)

        self.root_address = root_address
        self.registered_to_root = False

    def handle_user_interface_command(self, command, *args):
        if super(PeerClient, self).handle_user_interface_command(command, *args):
            return True

        if command == UserInterface.CMD_REGISTER:
            if self.registered_to_root:
                print("Ignoring command because this node is already registered.")
                return True

            packet = PacketFactory.new_register_packet(Packet.REQUEST, self.address, self.root_address)
            node = self.stream.add_node(self.root_address, set_register_connection=True)
            node.add_message_to_out_buff(packet.get_buf())

            return True

        elif command == UserInterface.CMD_ADVERTISE:
            if self.is_joined_to_parent():
                print("Ignoring command because this node is already joined.")
                return True

            packet = PacketFactory.new_advertise_packet(Packet.REQUEST, self.address)

            node = self.stream.get_node_by_server(*self.root_address)
            if not node:
                raise Exception("Failed to send advertise packet because no connection node found to root")
            else:
                node.add_message_to_out_buff(packet.get_buf())

    def __handle_register_packet(self, packet: Packet):
        _type = packet.get_body()[0]

        if _type == Packet.REQUEST:
            print("Ignoring register request packet for client")

        elif _type == Packet.RESPONSE:
            if self.registered_to_root:
                print("Ignoring register request packet, because is already registered!")
                return

            self.registered_to_root = True
            print("Successfully registered")

        else:
            print("Ignoring invalid register packet")

