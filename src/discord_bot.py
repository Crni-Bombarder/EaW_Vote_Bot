import discord
import string
import random
import re

class DiscordBot:

    VOTE_ID_ELEMENTS = list(string.digits) + list(string.ascii_uppercase)
    VOTE_ID_LENGTH = 6
    STRING_MANUAL = """EaW Voting Bot list of commands:
* **get-vote-id** : Return a unique vote ID to identify you. Don't share it! Recalling this function will resend you the vote ID if you have lose it"""
    STRING_MANUAL_ADMIN = """Admin only:
* **get-database** : Return in DM the whole current database
* **delete-from-database** : Delete a user from the database, forcing to regenerate a different vote ID. For debug"""

    RE_SEND_VOTE_ID_TO_ROLE = re.compile('\\S*\\s+send-vote-id-to-role\\s"(.*)"\\s*')

    def __init__(self, database, discord_token, bot_channel, bot_command, admin_name):
        self.database = database
        self.discord_token = discord_token
        self.bot_channel = bot_channel
        self.bot_command = bot_command
        self.admin_name = admin_name
        self.botname = "EaW VOte ID Bot"

        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True

        self.client = discord.Client(intents=self.intents)

        @self.client.event
        async def on_ready():
            print(f'We have logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user or message.channel.name != self.bot_channel or len(message.content) > 100:
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


    def run(self):
        self.client.run(self.discord_token)