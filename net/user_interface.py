import threading
import shlex


class UserInterface(threading.Thread):

    CMD_EXIT = 'exit'
    CMD_REGISTER = 'register'
    CMD_ADVERTISE = 'advertiser'
    CMD_MESSAGE = 'message'

    VALID_COMMANDS = (CMD_EXIT, CMD_REGISTER, CMD_ADVERTISE, CMD_MESSAGE)

    def __init__(self, address, is_root=False, *args, **kwargs):
        super(UserInterface, self).__init__(*args, **kwargs)
        self._buffer = []
        self._address = address
        self._is_root = is_root

    def run(self):
        """
        Which the user or client sees and works with.
        This method runs every time to see whether there are new messages or not.
        """

        if self._is_root:
            _input_prefix = "[%s:%s]> " % self._address
        else:
            _input_prefix = "%s:%s> " % self._address

        print("Welcome here")

        while True:
            command = input(_input_prefix)
            command_parts = shlex.split(command)

            if not command_parts:
                continue

            cmd = command_parts[0]

            if cmd == self.CMD_MESSAGE and len(command_parts) != 2:
                print("'message' command takes only 1 argument")
                continue

            elif cmd != self.CMD_MESSAGE and len(command_parts) != 1:
                print("'%s' command takes no argument" % cmd)
                continue

            if cmd in self.VALID_COMMANDS:
                self._buffer.append(command_parts)

                if cmd == self.CMD_EXIT:
                    break

        print("Goodbye")

    def read_and_clear_buffer(self):
        buffer = self._buffer
        self._buffer = []
        return buffer
