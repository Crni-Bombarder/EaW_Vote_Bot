import discord
from discord.ext import tasks
import string
import random
import re
import shlex
import time
from asyncio import Future

from src.settings import Settings
from src.commands import BotCommand

class DiscordBot:

    VOTE_ID_ELEMENTS = list(string.digits) + list(string.ascii_uppercase)
    VOTE_ID_LENGTH = 6
    STRING_MANUAL = """EaW Voting Bot list of commands:
* **get-vote-id** : Return a unique vote ID to identify you. Don't share it! Recalling this function will resend you the vote ID if you have lose it"""
    STRING_MANUAL_ADMIN = """Admin only:
* **get-database** : Return in DM the whole current database
* **delete-from-database** : Delete a user from the database, forcing to regenerate a different vote ID. For debug"""

    RE_SEND_VOTE_ID_TO_ROLE = re.compile('\\S*\\s+send-vote-id-to-role\\s"(.*)"\\s*')

    def __init__(self, database, discord_token, bot_command, settings_file):
        self.database = database
        self.discord_token = discord_token
        self.bot_command = bot_command
        self.settings = Settings(settings_file)
        self.botname = "EaW Vote ID Bot"

        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.intents.guilds = True

        self.client = discord.Client(intents=self.intents)

        self.ready = False
        self.vote_list_sem = None

        @self.client.event
        async def on_ready():
            print(f'We have logged in as {self.client.user}')
            self.settings.load_from_file() # Reloading the setting in case of disconnection
            if not self.bot_command:
                self.bot_command = f"<@{self.client.user.id}>"
            self.ready = True
            if not self.vote_parsing.is_running():
                self.vote_list_sem = [False, None]
                self.vote_parsing.start()

        @self.client.event
        async def on_thread_create(thread):
            if thread.guild.id != self.settings["watched_guild_id"]:
                return

            channel = thread.guild.get_channel(thread.parent_id)
            if channel.name not in self.settings["senior_vote_forums"]:
                return

            if self.vote_list_sem[0]:
                await self.vote_list_sem[1]
            self.vote_list_sem[1] = Future()
            self.vote_list_sem[0] = True
            val_time = int(time.time())
            self.settings["senior_vote_list"][str(thread.id)] = {
                "content": [],
                "time_started": val_time,
                "last_time_checked": val_time,
                "amendments": []
            }
            self.settings.save_to_file()

            self.vote_list_sem[1].set_result(True)
            self.vote_list_sem[0] = False

            # Add voting reaction
            msg = await thread.fetch_message(thread.id)
            await msg.add_reaction(self.settings["senior_vote_reactions"]["yes"])
            await msg.add_reaction(self.settings["senior_vote_reactions"]["abstaining"])
            await msg.add_reaction(self.settings["senior_vote_reactions"]["against"])

            embed = discord.Embed(title=thread.name, description="Vote started")
            await thread.send("", embed=embed)

        @self.client.event
        async def on_message(message):
            channel = message.channel
            if isinstance(channel, discord.Thread):
                channel = channel.parent
            if not self.ready or\
                message.author == self.client.user or\
                (message.author.name not in self.settings["admin"] and isinstance(channel, discord.DMChannel)) or\
                (not isinstance(channel, discord.DMChannel) and channel.name not in self.settings["watched_channels"] and channel.name not in self.settings["senior_vote_forums"]):
                return

            if message.content.startswith(self.bot_command):
                tokens = shlex.split(message.content.strip())

                if len(tokens) < 2:
                    return

                if self.check_authorization(message, tokens[1]):
                    await BotCommand.exec_command(self, message, tokens[1:])
                else:
                    try:
                        await message.author.send(f'Unknown command: {tokens[1]}')
                    except:
                        await message.channel.send(f'Unknown command: {tokens[1]}')

            return

            if message.content.startswith(self.bot_command):
                tokens = message.content.strip().split(" ")
                if len(tokens) == 1:
                    await self.send_manual(message.author)
                    return
                match tokens[1]:
                    case "get-vote-id":
                        await self.get_vote_id_cmd(message.author)

                    case "get-database":
                        if message.author.name == self.admin_name:
                            await message.author.send(str(self.database))
                        else:
                            await self.send_manual(message.author)

                    case "send-vote-id-to-role":
                        if message.author.name == self.admin_name:
                            match = DiscordBot.RE_SEND_VOTE_ID_TO_ROLE.match(message.content.strip())
                            if match:
                                for role in await message.guild.fetch_roles():
                                    if role.name == match.group(1):
                                        for member in role.members:
                                            await self.get_vote_id_cmd(member)
                                        return
                                await message.author.send(f"Cannot find the role {match.group(1)}")
                                await self.send_manual(message.author)
                                return
                        await self.send_manual(message.author)

                    case "delete-from-database":
                        if message.author.name == self.admin_name and len(tokens) > 2:
                            if self.database.check_discord_name(tokens[2]):
                                await message.author.send(f"_{message.content}_: Deleting from database {tokens[2]} that had {self.database.get_vote_id_from_name(message.author.name)}")
                                self.database.delete_entry_from_name(tokens[2])
                            else:
                               await message.author.send(f"_{message.content}_: {tokens[2]} is not in the database")
                        else:
                            await self.send_manual(message.author)
                    case _:
                        await self.send_manual(message.author)

    async def get_sem_vote_list(self):
        if self.vote_list_sem[0]:
            await self.vote_list_sem[1]
        self.vote_list_sem[1] = Future()
        self.vote_list_sem[0] = True

    def free_sem_vote_list(self):
        self.vote_list_sem[1].set_result(True)
        self.vote_list_sem[0] = False

    @tasks.loop(minutes=5)
    async def vote_parsing(self):
        if self.client.is_closed():
            return

        # Get the guild
        guild = self.client.get_guild(self.settings["watched_guild_id"])
        if not guild: return

        # Get the number of voters
        voters = await self.get_all_voters(guild)

        await self.get_sem_vote_list()

        # For each running vote, check the number of votes
        for thread_id, content in self.settings["senior_vote_list"].items():
            thread = await guild.fetch_channel(thread_id)
            root_message = await thread.fetch_message(thread_id)
            results = await self.get_all_votes(root_message, voters)

        self.free_sem_vote_list()

    async def get_all_voters(self, guild):
        voters = set()
        roles = await guild.fetch_roles()
        for role in roles:
            if role.name in self.settings["senior_vote_voter_roles"]:
                voters.update(set([member.id for member in role.members]))

        for role in roles:
            if role.name in self.settings["senior_vote_blacklisted_voter_roles"]:
                voters.difference_update(set([member.id for member in role.members]))

        return voters

    # Get the reaction from a message, and translate them into votes
    # Return:
    # * a list with the of votes [yes, abstaining, against, void]
    # * a dictionary with each voter id and their votes
    # * and finally a set of voter that didn't vote
    async def get_all_votes(self, message, voters_set):
        list_vote = [0, 0, 0, 0]
        dict_index = {self.settings["senior_vote_reactions"]["yes"]: 0,
                      self.settings["senior_vote_reactions"]["abstaining"]: 1,
                      self.settings["senior_vote_reactions"]["against"]: 2}
        already_voted = set()
        not_voted = voters_set.copy()
        voter_value = {}

        for reaction in message.reactions:
            if reaction.emoji not in dict_index:
                continue
            vote_value = dict_index[reaction.emoji]
            async for user in reaction.users():
                if user.id in voters_set:
                    if user.id in already_voted:
                        list_vote[voter_value[user.id]] -= 1
                        list_vote[3] += 1
                        voter_value[user.id] = 4
                    else:
                        voter_value[user.id] = vote_value
                        list_vote[vote_value] += 1
                        not_voted.remove(user.id)
                        already_voted.add(user.id)

        return list_vote, voter_value, not_voted

    async def send_manual(self, user):
        await user.send(DiscordBot.STRING_MANUAL)
        if user.name == self.admin_name:
            await user.send(DiscordBot.STRING_MANUAL_ADMIN)

    def generate_new_vote_id(self):
        vote_id = self.generate_vote_id()
        i = 0
        while self.database.check_vote_id(vote_id):
            vote_id = self.generate_vote_id()
            i += 1
            if i > 50:
                print("Error generating a Vote ID, critical")
                return None
        return vote_id

    async def get_vote_id_cmd(self, member):
        if not self.database.check_discord_name(member.name):
            vote_id = self.generate_new_vote_id()
            if not vote_id:
                await member.send(f"_{self.botname}_: Something went wrong, call the admin !")
            self.database.add_to_file_database(member.name, vote_id)
            #await member.send(f"_{self.botname}_: Associated {member.name} with {vote_id}")
        await member.send(f"_{self.botname}_: Your Vote ID is {self.database.get_vote_id_from_name(member.name)}")

    def generate_vote_id(self):
        return "".join(random.choices(DiscordBot.VOTE_ID_ELEMENTS, k=DiscordBot.VOTE_ID_LENGTH))

    def check_authorization(self, message, command):
        if command not in self.settings["commands"]:
            if command in BotCommand.list_command:
                self.settings["commands"][command] = []
                self.settings.save_to_file()
            else:
                return

        roles = []
        if not isinstance(message.channel, discord.DMChannel):
            roles = [x.name for x in message.author.roles]
        return (message.author.name in self.settings["admin"]) or (any(x in roles for x in self.authorization["commands"][command]))

    def run(self):
        self.client.run(self.discord_token)

def create_cmd(name, desc, authorization, func):
    pass

