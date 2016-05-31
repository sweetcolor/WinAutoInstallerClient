import pickle


class CommandFile:
    def __init__(self):
        self.data = b''

    def write(self, part):
        self.data += part

    def pickle_loads_data(self):
        return pickle.loads(self.data)

    def get_text(self):
        return self.data.decode()

    def get_lines(self):
        return self.get_text().splitlines()

    def close(self):
        pass
