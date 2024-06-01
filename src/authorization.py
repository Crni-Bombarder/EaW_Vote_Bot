import os
import json

class Authorization:

    def __init__(self, filepath):
        self.filepath = filepath
        self.database = {"admin": [], "commands": {}}
        if os.path.isfile(self.filepath):
            self.load_from_file()

    def load_from_file(self):
        with open(self.filepath, "r") as fd:
            self.database = json.load(fd)

    def save_to_file(self):
        with open(self.filepath, "w") as fd:
            json.dump(self.database, fd)

    def __getitem__(self, key):
        return self.database[key]
