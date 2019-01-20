from . import UserInterface, Peer, PacketFactory, Packet


class PeerStatus:
    STATUS_INITIAL = 0
    STATUS_REGISTERED = 1
    STATUS_ADVERTISED = 2
    STATUS_JOINED = 3

    def __init__(self):
        self.status = self.STATUS_INITIAL

    @property
    def is_registered(self):
        return self.status >= self.STATUS_REGISTERED

    def set_registered(self):
        if self.status == self.STATUS_INITIAL:
            self.status = self.STATUS_REGISTERED
            return True

    @property
    def is_advertised(self):
        return self.status >= self.STATUS_ADVERTISED

    def set_advertised(self):
        if self.status == self.STATUS_REGISTERED:
            self.status = self.STATUS_ADVERTISED
            return True

    @property
    def is_joined(self):
        return self.status >= self.STATUS_JOINED

    def set_joined(self):
        if self.status == self.STATUS_ADVERTISED:
            self.status = self.STATUS_JOINED
            return True


class PeerClient(Peer):
    def __init__(self, address: tuple, root_address: tuple):
        super(PeerClient, self).__init__(address)

        self.root_address = root_address
        self.parent_address = None
        self.status = PeerStatus()

    def handle_user_interface_command(self, command, *args):
        if super(PeerClient, self).handle_user_interface_command(command, *args):
            return True

        if command == UserInterface.CMD_REGISTER:
            if self.status.is_registered:
                print("Ignoring command because this node is already registered.")
                return True

            packet = PacketFactory.new_register_packet(Packet.REQUEST, self.address, self.root_address)
            self.stream.get_or_create_node_to_server(self.root_address, True).add_message_to_out_buff(packet.get_buf())

            return True

        elif command == UserInterface.CMD_ADVERTISE:
            if self.status.is_joined:
                print("Ignoring command because this node is already joined.")
                return True

            packet = PacketFactory.new_advertise_packet(Packet.REQUEST, self.address)

            self.stream.get_or_create_node_to_server(self.root_address).add_message_to_out_buff(packet.get_buf())

    def __handle_register_packet(self, packet: Packet):
        _type = packet.get_body()[0:3]

        if _type == Packet.REQUEST:
            print("Ignoring register request packet for client")

        elif _type == Packet.RESPONSE:
            if self.status.is_registered:
                print("Ignoring register response packet, because is already registered!")

            else:
                self.status.set_registered()
                print("Successfully registered")

        else:
            print("Ignoring invalid register packet")

    def __handle_advertise_packet(self, packet: Packet):
        _type = packet.get_body()[0:3]

        if _type == Packet.REQUEST:
            print("Ignoring advertise request packet for client")

        elif _type == Packet.RESPONSE:
            if self.status.is_joined:
                print("Ignoring advertise response packet, because is already joined!")

            else:
                parent_ip = packet.get_body()[4:19]
                parent_port = packet.get_body()[20:25]

                if not parent_ip or not parent_port:
                    print("invalid advertise packet")
                    return

                parent_address = (parent_ip, parent_port)

                self.status.set_advertised()

                print("Sending join message")
                packet = PacketFactory.new_join_packet((parent_ip, parent_port))
                self.stream.get_or_create_node_to_server(parent_address).add_message_to_out_buff(packet.get_buf())
        else:
            print("Ignoring invalid advertise packet")

