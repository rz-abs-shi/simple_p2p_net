import time

from . import UserInterface, Peer, PacketFactory, Packet, ReunionParser

CLIENT_REUNION_SEND_DELAY = 4
CLIENT_REUNION_CONNECTIVITY_DEADLINE = 45


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

    def disconnect(self):
        if self.status > self.STATUS_REGISTERED:
            self.status = self.STATUS_REGISTERED
            return True


class PeerClient(Peer):
    def __init__(self, address: tuple, root_address: tuple):
        super(PeerClient, self).__init__(address)

        self.root_address = root_address
        self.parent_address = None
        self.status = PeerStatus()
        self.last_reunion_response_received = -1
        self.last_reunion_request_sent = -1
        self.reunion_sent = False

    def handle_user_interface_command(self, command, *args):
        if super(PeerClient, self).handle_user_interface_command(command, *args):
            return True

        if command == UserInterface.CMD_REGISTER:
            if self.status.is_registered:
                print("Ignoring command because this node is already registered.")
                return True

            packet = PacketFactory.new_register_packet(Packet.REQUEST, self.address, self.root_address)
            self.send_packet(self.root_address, packet, register_connection=True)

            return True

        elif command == UserInterface.CMD_ADVERTISE:
            return self.send_advertise_packet()

        elif command == UserInterface.CMD_PARENT:
            print("Parent is " + str(self.parent_address))
            return True

    def send_advertise_packet(self):
        if self.status.is_joined:
            print("Ignoring command because this node is already joined.")
            return True

        packet = PacketFactory.new_advertise_packet(Packet.REQUEST, self.address)
        self.send_packet(self.root_address, packet)

        return True

    def _handle_register_packet(self, packet: Packet):
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

    def _handle_advertise_packet(self, packet: Packet):
        _type = packet.get_body()[0:3]

        print("Requesting for parent")

        if _type == Packet.REQUEST:
            print("Ignoring advertise request packet for client")

        elif _type == Packet.RESPONSE:
            if self.status.is_joined:
                print("Ignoring advertise response packet, because is already joined!")

            else:
                parent_ip = packet.get_body()[3:18]
                parent_port = packet.get_body()[18:23]

                if not parent_ip or not parent_port:
                    print("invalid advertise packet")
                    return

                self.parent_address = (parent_ip, parent_port)

                self.status.set_advertised()

                print("Sending join message")
                packet = PacketFactory.new_join_packet((parent_ip, parent_port))
                self.send_packet(self.parent_address, packet)

                print("Starting reunion daemon")
                self.status.set_joined()
                self.run_reunion_daemon()
        else:
            print("Ignoring invalid advertise packet")

    def is_my_child(self, address):
        """
        :param address: child address
        :return:
        """
        # fixme
        return self.is_neighbour(address)

    def _handle_reunion_packet(self, packet):
        if not (self.status.is_joined and self.reunion_active):
            print("ignoring reunion packet because this peer is not joined or reunion_active")
            return

        parser = ReunionParser(packet)

        if not parser.is_valid():
            print("Ignoring invalid reunion packet")
            return

        sender_address = packet.get_source_server_address()

        if parser.request_type == Packet.REQUEST:
            # send request packet to parent
            if not self.is_my_child(sender_address):
                print("Ignoring non neighbor reunion request packet")
                return

            new_entries = [*parser.entries, self.address]
            new_packet = PacketFactory.new_reunion_packet(Packet.REQUEST, self.address, new_entries)
            self.send_packet(self.parent_address, new_packet)

        else:
            # send response packet to child
            if sender_address != self.parent_address:
                print("Ignoring reunion response packet from non parent peer")
                return

            entries = parser.entries
            if entries[0] != self.address:
                print("Ignoring invalid reunion packet, it does not sent by me")
                return

            print("Hooray... a reunion response received!")
            self.last_reunion_response_received = time.time()
            self.reunion_sent = False

            new_entries = entries[1:]
            if new_entries:
                child_address = new_entries[0]
                if not self.is_my_child(child_address):
                    print("Propagating reunion response packet to bottom failed because the address is not my child")
                    return

                new_packet = PacketFactory.new_reunion_packet(Packet.RESPONSE, child_address, new_entries)
                self.send_packet(child_address, new_packet)

    def run_reunion_daemon(self):
        super(PeerClient, self).run_reunion_daemon()
        self.last_reunion_response_received = time.time()
        self.reunion_sent = False

    def handle_disconnection(self):
        if not self.status.disconnect():
            print("Disconnecting failed!")
            return

        self.reunion_active = False
        self.parent_address = None

        print("Peer disconnected from network")

        print("Sending new advertise packet!")
        self.send_advertise_packet()

    def send_new_reunion_packet(self):
        if not (self.status.is_joined and self.parent_address and self.reunion_active):
            print("Sending reunion packet failed because peer is not active for sending reunion packet")
            print("joined: %s, parent_address: %s, reunion_active: %s" % (
                self.status.is_joined, self.parent_address, self.reunion_active
            ))
            print("disabling reunion sending")
            self.reunion_active = False
            return

        print("Sending new reunion packet")
        packet = PacketFactory.new_reunion_packet(Packet.REQUEST, self.address, [self.address])
        self.send_packet(self.parent_address, packet)
        self.reunion_sent = True

    def update_reunion(self):
        now = time.time()

        if now - self.last_reunion_response_received > CLIENT_REUNION_CONNECTIVITY_DEADLINE:
            self.handle_disconnection()
            return

        if not self.reunion_sent and (
                self.last_reunion_request_sent < 0 or
                (now - self.last_reunion_request_sent) > CLIENT_REUNION_SEND_DELAY
        ):
            self.send_new_reunion_packet()
