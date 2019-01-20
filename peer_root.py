from peer import Peer


class PeerRoot(Peer):

    def __init__(self, address: tuple):
        super(PeerRoot, self).__init__(address)

    @property
    def is_root(self):
        return True
