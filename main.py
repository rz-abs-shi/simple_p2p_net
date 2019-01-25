import argparse
from ipaddress import ip_address

from net import PeerRoot, PeerClient
from tools import Node

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a peer')
    parser.add_argument('ip', help='ip of this peer', type=ip_address)
    parser.add_argument('port', help='port of this peer', type=int)
    
    parser.add_argument('--root', help='this peer is a root', dest='is_root', default=False, type=bool)
    
    parser.add_argument('--root-ip', help='ip of root peer', type=ip_address, dest='root_ip')
    parser.add_argument('--root-port', help='port of root peer', type=int, dest='root_port')
    
    args = parser.parse_args()

    address = Node.parse_address((str(args.ip), args.port))

    if args.is_root:
        peer = PeerRoot(address)
    else:
        if args.root_port is None or args.root_ip is None:
            print("Error: you should specify root-ip and root-port")
            exit(1)

        root_address = Node.parse_address((str(args.root_ip), args.root_port))
        peer = PeerClient(address, root_address)

    peer.run()
