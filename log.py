import textwrap
import constants as const

class Msg():
    def __init__(self, string, color_active=const.base2, color_inactive=const.base0):
        self.string = string
        self.color_active = color_active
        self.color_inactive = color_inactive

class Log():
    """
    Log. New messages have a different color
    """
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.reset()

    def reset(self):
        self.messages = []
        self.last = 0 # used to know which messages are bright

    def is_there_new(self):
        return self.last != self.height

    def set_rendered(self):
        self.last = self.height

    def add_log(self, message, color_active=const.base2, color_inactive=const.base0):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message, self.width)
        self.last -= len(new_msg_lines)
        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Msg(line, color_active, color_inactive))
