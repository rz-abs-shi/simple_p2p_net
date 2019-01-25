from net import PacketFactory, Packet

sender = ("127.000.000.001", 31315)
root = ("127.000.000.001", 5356)
child = ("127.000.000.001", 31318)

if __name__ == '__main__':
    packet = PacketFactory.new_register_packet(Packet.REQUEST, sender, sender)
    assert packet.get_buf() == b'\x00\x01\x00\x01\x00\x00\x00\x17\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSREQ127.000.000.00131315'

    packet = PacketFactory.new_register_packet(Packet.RESPONSE, root)
    assert packet.get_buf() == b'\x00\x01\x00\x01\x00\x00\x00\x06\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00\x14\xecRESACK'

    packet = PacketFactory.new_advertise_packet(Packet.REQUEST, sender)
    assert packet.get_buf() == b'\x00\x01\x00\x02\x00\x00\x00\x03\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSREQ'

    packet = PacketFactory.new_advertise_packet(Packet.RESPONSE, root, root)
    assert packet.get_buf() == b'\x00\x01\x00\x02\x00\x00\x00\x17\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00\x14\xecRES127.000.000.00105356'

    packet = PacketFactory.new_join_packet(sender)
    assert packet.get_buf() == b'\x00\x01\x00\x03\x00\x00\x00\x04\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSJOIN'

    packet = PacketFactory.new_reunion_packet(Packet.REQUEST, sender, [sender])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00\x19\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSREQ01127.000.000.00131315'

    packet = PacketFactory.new_reunion_packet(Packet.RESPONSE, root, [sender])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00\x19\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00\x14\xecRES01127.000.000.00131315'

    packet = PacketFactory.new_message_packet("Hi", sender)
    assert packet.get_buf() == b'\x00\x01\x00\x04\x00\x00\x00\x02\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSHi'

    # Reunion Hello with 3 peers:
    packet = PacketFactory.new_reunion_packet(Packet.REQUEST, child, [child])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00\x19\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zVREQ01127.000.000.00131318'

    packet = PacketFactory.new_reunion_packet(Packet.REQUEST, sender, [child, sender])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00-\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSREQ02127.000.000.00131318127.000.000.00131315'

    # Reunion Hello Back with 3 peers:
    packet = PacketFactory.new_reunion_packet(Packet.RESPONSE, root, [sender, child])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00-\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00\x14\xecRES02127.000.000.00131315127.000.000.00131318'

    packet = PacketFactory.new_reunion_packet(Packet.RESPONSE, sender, [child])
    assert packet.get_buf() == b'\x00\x01\x00\x05\x00\x00\x00\x19\x00\x7f\x00\x00\x00\x00\x00\x01\x00\x00zSRES01127.000.000.00131318'





