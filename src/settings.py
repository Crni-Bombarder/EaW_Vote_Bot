import os
import json

class Settings:

    def __init__(self, filepath):
        self.filepath = filepath
        self.default_database = {
            "admin": [],
            "watched_guild_name": "",
            "watched_guild_id": 0,
            "watched_channels": [],
            "senior_vote_forums": [],
            "senior_vote_list": {},
            "senior_vote_voter_roles": [],
            "senior_vote_blacklisted_voter_roles": [],
            "senior_vote_reactions": {
                "yes": "\ud83d\udc4d",
                "abstaining": "\ud83d\ude36",
                "against": "\ud83d\udc4e"},
            "commands": {}
            }
        self.database = self.default_database
        if os.path.isfile(self.filepath):
            self.load_from_file()

    def load_from_file(self):
        with open(self.filepath, "r") as fd:
            self.database = json.load(fd)

    def save_to_file(self):
        with open(self.filepath, "w") as fd:
            json.dump(self.database, fd, indent=4)

    def __getitem__(self, key):
        if key not in self.database:
            self.database[key] = self.default_database[key]
        return self.database[key]

    def __setitem__(self, key, value):
        self.database[key] = value
