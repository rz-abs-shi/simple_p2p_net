import threading
import time


class UserInterface(threading.Thread):

    def __init__(self):
        self._buffer = []

    def run(self):
        """
        Which the user or client sees and works with.
        This method runs every time to see whether there are new messages or not.
        """
        while True:
            message = input("Write your command:\n")
            self._buffer.append(message)

    def read_and_clear_buffer(self):
        buffer = self._buffer
        self._buffer = []
        return buffer
