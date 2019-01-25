"""

    This is the format of packets in our network:
    


                                                **  NEW Packet Format  **
     __________________________________________________________________________________________________________________
    |           Version(2 Bytes)         |         Type(2 Bytes)         |           Length(Long int/4 Bytes)          |
    |------------------------------------------------------------------------------------------------------------------|
    |                                            Source Server IP(8 Bytes)                                             |
    |------------------------------------------------------------------------------------------------------------------|
    |                                           Source Server Port(4 Bytes)                                            |
    |------------------------------------------------------------------------------------------------------------------|
    |                                                    ..........                                                    |
    |                                                       BODY                                                       |
    |                                                    ..........                                                    |
    |__________________________________________________________________________________________________________________|

    Version:
        For now version is 1
    
    Type:
        1: Register
        2: Advertise
        3: Join
        4: Message
        5: Reunion
                e.g: type = '2' => Advertise packet.
    Length:
        This field shows the character numbers for Body of the packet.

    Server IP/Port:
        We need this field for response packet in non-blocking mode.



    ***** For example: ******

    version = 1                 b'\x00\x01'
    type = 4                    b'\x00\x04'
    length = 12                 b'\x00\x00\x00\x0c'
    ip = '192.168.001.001'      b'\x00\xc0\x00\xa8\x00\x01\x00\x01'
    port = '65000'              b'\x00\x00\\xfd\xe8'
    Body = 'Hello World!'       b'Hello World!'

    Bytes = b'\x00\x01\x00\x04\x00\x00\x00\x0c\x00\xc0\x00\xa8\x00\x01\x00\x01\x00\x00\xfd\xe8Hello World!'




    Packet descriptions:
    
        Register:
            Request:
        
                                 ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |                  IP (15 Chars)                 |
                |------------------------------------------------|
                |                 Port (5 Chars)                 |
                |________________________________________________|
                
                For sending IP/Port of the current node to the root to ask if it can register to network or not.

            Response:
        
                                 ** Body Format **
                 _________________________________________________
                |                  RES (3 Chars)                  |
                |-------------------------------------------------|
                |                  ACK (3 Chars)                  |
                |_________________________________________________|
                
                For now only should just send an 'ACK' from the root to inform a node that it
                has been registered in the root if the 'Register Request' was successful.
                
        Advertise:
            Request:
            
                                ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |________________________________________________|
                
                Nodes for finding the IP/Port of their neighbour peer must send this packet to the root.

            Response:

                                ** Packet Format **
                 ________________________________________________
                |                RES(3 Chars)                    |
                |------------------------------------------------|
                |              Server IP (15 Chars)              |
                |------------------------------------------------|
                |             Server Port (5 Chars)              |
                |________________________________________________|
                
                Root will response Advertise Request packet with sending IP/Port of the requester peer in this packet.
                
        Join:

                                ** Body Format **
                 ________________________________________________
                |                 JOIN (4 Chars)                 |
                |________________________________________________|
            
            New node after getting Advertise Response from root must send this packet to the specified peer
            to tell him that they should connect together; When receiving this packet we should update our
            Client Dictionary in the Stream object.


            
        Message:
                                ** Body Format **
                 ________________________________________________
                |             Message (#Length Chars)            |
                |________________________________________________|

            The message that want to broadcast to whole network. Right now this type only includes a plain text.
        
        Reunion:
            Hello:
        
                                ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |           Number of Entries (2 Chars)          |
                |------------------------------------------------|
                |                 IP0 (15 Chars)                 |
                |------------------------------------------------|
                |                Port0 (5 Chars)                 |
                |------------------------------------------------|
                |                 IP1 (15 Chars)                 |
                |------------------------------------------------|
                |                Port1 (5 Chars)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IPN (15 Chars)                 |
                |------------------------------------------------|
                |                PortN (5 Chars)                 |
                |________________________________________________|
                
                In every interval (for now 20 seconds) peers must send this message to the root.
                Every other peer that received this packet should append their (IP, port) to
                the packet and update Length.

            Hello Back:
        
                                    ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |           Number of Entries (2 Chars)          |
                |------------------------------------------------|
                |                 IPN (15 Chars)                 |
                |------------------------------------------------|
                |                PortN (5 Chars)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IP1 (15 Chars)                 |
                |------------------------------------------------|
                |                Port1 (5 Chars)                 |
                |------------------------------------------------|
                |                 IP0 (15 Chars)                 |
                |------------------------------------------------|
                |                Port0 (5 Chars)                 |
                |________________________________________________|

                Root in an answer to the Reunion Hello message will send this packet to the target node.
                In this packet, all the nodes (IP, port) exist in order by path traversal to target.
            
    
"""
from struct import *
from tools.Node import Node


class Packet:
    TYPE_REGISTER = 1
    TYPE_ADVERTISE = 2
    TYPE_JOIN = 3
    TYPE_MESSAGE = 4
    TYPE_REUNION = 5

    RESPONSE = 'RES'
    REQUEST = 'REQ'
    ACK = 'ACK'

    def __init__(self, version: int, _type: int, source_server_ip: str, source_server_port: str, body: str):
        self.version = version
        self._type = _type
        self.source_server_ip = source_server_ip
        self.source_server_port = source_server_port
        self.body = body
        self._ip_parts = list(map(int, source_server_ip.split('.')))

        if len(self._ip_parts) != 4:
            raise ValueError("invalid ip")

    def get_type(self):
        """en(body)
        :return: Packet type
        :rtype: int
        """
        return self._type

    def get_length(self):
        """

        :return: Packet length
        :rtype: int
        """
        return len(self.body)

    def get_body(self):
        """
        :return: Packet body
        :rtype: str
        """
        return self.body

    def get_buf(self):
        """
        In this function, we will make our final buffer that represents the Packet with the Struct class methods.

        :return The parsed packet to the network format.
        :rtype: bytearray
        """
        return pack(
            "!HHIHHHHI",
            self.version,
            self._type,
            self.get_length(),
            *self._ip_parts,
            int(self.source_server_port),
        ) + self.body.encode()

    def get_source_server_ip(self):
        """

        :return: Server IP address for the sender of the packet.
        :rtype: str
        """
        return Node.parse_ip(self.source_server_ip)

    def get_source_server_port(self):
        """
        :return: Server Port address for the sender of the packet.
        :rtype: str
        """
        return Node.parse_port(self.source_server_port)

    def get_source_server_address(self):
        """
        :return: Server address; The format is like ('192.168.001.001', '05335').
        :rtype: tuple
        """
        return self.get_source_server_ip(), self.get_source_server_port()

    @classmethod
    def new_packet(cls, buf: bytes):
        if len(buf) < 20:
            raise ValueError("invalid buf")

        header_buf = buf[:20]
        body_buf = buf[20:]

        header = unpack("!HHIHHHHI", header_buf)

        if header[2] != len(body_buf):
            raise ValueError("invalid packet length")

        ip = "%d.%d.%d.%d" % header[3:7]
        port = header[7]

        return Packet(header[0], header[1], ip, port, body_buf.decode())


class PacketFactory:
    """
    This class is only for making Packet objects.
    """

    @staticmethod
    def parse_buffer(buffer):
        """
        In this function we will make a new Packet from input buffer with struct class methods.

        :param buffer: The buffer that should be parse to a validate packet format

        :return new packet
        :rtype: Packet

        """
        return Packet.new_packet(buffer)

    @staticmethod
    def new_reunion_packet(type, source_address, nodes_array: list):
        """
        :param type: Reunion Hello (REQ) or Reunion Hello Back (RES)
        :param source_address: IP/Port address of the packet sender.
        :param nodes_array: [(ip0, port0), (ip1, port1), ...] It is the path to the 'destination'.

        :type type: str
        :type source_address: tuple
        :type nodes_array: list

        :return New reunion packet.
        :rtype Packet
        """

        if type not in (Packet.REQUEST, Packet.RESPONSE):
            raise ValueError("invalid type")

        if len(nodes_array) > 99:
            raise ValueError("too long nodes_array")

        entities = []

        for ip, port in nodes_array:
            entities.append(Node.parse_ip(ip))
            entities.append(Node.parse_port(port))

        body = type + str(len(nodes_array)).zfill(2) + ''.join(entities)

        return Packet(1, 5, *source_address, body)

    @staticmethod
    def new_advertise_packet(type, source_server_address, neighbour: tuple=None):
        """
        :param type: Type of Advertise packet
        :param source_server_address Server address of the packet sender.
        :param neighbour: The neighbour for advertise response packet; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type neighbour: tuple

        :return New advertise packet.
        :rtype Packet

        """
        if type not in (Packet.REQUEST, Packet.RESPONSE):
            raise ValueError("invalid type")

        if type == Packet.REQUEST:
            body = Packet.REQUEST
        else:
            if not neighbour:
                raise ValueError("neighbour should provided for response")

            body = Packet.RESPONSE + Node.parse_ip(neighbour[0]) + Node.parse_port(neighbour[1])

        return Packet(1, 2, *source_server_address, body)

    @staticmethod
    def new_join_packet(source_server_address) -> Packet:
        """
        :param source_server_address: Server address of the packet sender.

        :type source_server_address: tuple

        :return New join packet.
        :rtype Packet

        """
        return Packet(1, 3, *source_server_address, 'JOIN')

    @staticmethod
    def new_register_packet(type, source_server_address, address=(None, None)) -> Packet:
        """
        :param type: Type of Register packet
        :param source_server_address: Server address of the packet sender.
        :param address: If 'type' is 'request' we need an address; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type address: tuple

        :return New Register packet.
        :rtype Packet
        """
        if type not in (Packet.REQUEST, Packet.RESPONSE):
            raise ValueError("invalid type")

        if type == Packet.REQUEST:
            if not address:
                raise ValueError("address must be set in request")

            body = Packet.REQUEST + Node.parse_ip(address[0]) + Node.parse_port(address[1])

        else:
            body = Packet.RESPONSE + Packet.ACK

        return Packet(1, 1, *source_server_address, body)

    @staticmethod
    def new_message_packet(message, source_server_address):
        """
        Packet for sending a broadcast message to the whole network.

        :param message: Our message
        :param source_server_address: Server address of the packet sender.

        :type message: str
        :type source_server_address: tuple

        :return: New Message packet.
        :rtype: Packet
        """

        return Packet(1, 4, *source_server_address, message)


class Parser:
    def __init__(self, packet):
        self._packet = packet


class ReunionParser(Parser):

    def __init__(self, packet):
        super(ReunionParser, self).__init__(packet)

        self.request_type = None
        self.entries = None

    def is_valid(self):
        body = self._packet.get_body()

        self.request_type = body[:3]

        if len(body) <= 5 or (len(body) - 5) % 20 != 0:
            return False

        try:
            number_of_entries = int(body[3:5])
        except ValueError:
            return False

        if len(body) != 5 + 20 * number_of_entries:
            return False

        self.entries = []

        for i in range(number_of_entries):
            address = parse_address(body[5 + 20 * i: 5 + 20 * (i + 1)])
            if address is None:
                return False

            self.entries.append(address)


def parse_address(address: str) -> tuple:
    return Node.parse_ip(address[:15]), Node.parse_port(address[15:])
