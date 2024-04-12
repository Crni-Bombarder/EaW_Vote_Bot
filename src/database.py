import os
import re
from threading import Thread
from queue import Queue

class IDDatabase:

    DATABASE_RE = re.compile("(.*),(.*)")

    def __init__(self, filepath, clear_file=False):
        self.filepath = filepath
        if clear_file:
            self.fd = open(filepath, "w", encoding="utf-8")
            self.init_blank_database()
        else:
            if os.path.isfile(filepath):
                self.init_database_from_file(filepath)
            else:
                self.init_blank_database()
            self.fd = open(filepath, "a", encoding="utf-8")

        self.write_queue = Queue()
        self.write_thread = Thread(target=self.write_routine, daemon=True).start()

    def write_routine(self):
        while True:
            discord_name, vote_id = self.write_queue.get()
            self.fd.write(f"{discord_name},{vote_id}\n")
            self.fd.flush()
            self.write_queue.task_done()

    def init_blank_database(self):
        self.couple_dict = {}
        self.vote_id_set = set()
        self.discord_name_set = set()

    def add_to_file_database(self, discord_name, vote_id):
        self.add_to_local_database_entry(discord_name, vote_id)
        self.write_queue.put((discord_name, vote_id))

    def add_to_local_database_entry(self, discord_name, vote_id):
        self.couple_dict[discord_name] = vote_id
        self.vote_id_set.add(vote_id)
        self.discord_name_set.add(discord_name)

    def check_vote_id(self, vote_id):
        return vote_id in self.vote_id_set

    def check_discord_name(self, discord_name):
        return discord_name in self.discord_name_set

    def init_database_from_file(self, filepath):
        self.init_blank_database()
        with open(filepath, "r") as fd:
            line = fd.readline().strip()
            while line:
                results = IDDatabase.DATABASE_RE.match(line)
                if results:
                    discord_name = results[1]
                    vote_id = results[2]
                    if (not self.check_discord_name(discord_name)) and (not self.check_vote_id(vote_id)):
                        self.add_to_local_database_entry(discord_name, vote_id)
                line = fd.readline().strip()

    def __str__(self):
        return str(self.couple_dict)

    def __del__(self):
        try:
            self.write_thread.join()
            self.fd.flush()
            self.fd.close()
        except:
            pass