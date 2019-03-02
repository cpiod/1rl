import textwrap

class Log():
    """
    Log. New messages have a different color
    """
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.messages = []
        self.last = 0

    def set_rendered(self):
        self.last = self.height

    def add_log(self, message):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message, self.width)
        self.last -= len(new_msg_lines)
        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(line)
