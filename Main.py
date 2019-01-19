from Peer import Peer
import argparse
from ipaddress import ip_address

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a peer')
    parser.add_argument('ip', help='ip of this peer', type=ip_address)
    parser.add_argument('port', help='port of this peer', type=int)
    
    parser.add_argument('--root', help='this peer is a root', dest='is_root', default=False, type=bool)
    
    parser.add_argument('--root-ip', help='ip of root peer', type=ip_address, dest='root_ip')
    parser.add_argument('--root-port', help='port of root peer', type=int, dest='root_port')
    
    args = parser.parse_args()

    if args.is_root:
        peer = Peer(args.ip, args.port, is_root=True)
    else:
        if args.root_port is None or args.root_ip is None:
            print("Error: you should specify root-ip and root-port")
            exit(1)

        peer = Peer(args.ip, args.port, is_root=None, root_address=(args.root_ip, args.root_port))

    peer.run()
