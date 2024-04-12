import discord
import string
import random

class DiscordBot:

    VOTE_ID_ELEMENTS = list(string.digits) + list(string.ascii_uppercase)
    VOTE_ID_LENGTH = 6
    STRING_MANUAL = """EaW Voting Bot list of commands:
* **get-vote-id** : Return a unique vote ID to identify you. Don't share it! Recalling this function will resend you the vote ID if you have lose it"""

    def __init__(self, database, discord_token, bot_channel, bot_command, admin_name):
        self.database = database
        self.discord_token = discord_token
        self.bot_channel = bot_channel
        self.bot_command = bot_command
        self.admin_name = admin_name

        self.intents = discord.Intents.default()
        self.intents.message_content = True

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
                        if self.database.check_discord_name(message.author.name):
                            print(self.database.get_vote_id_from_name(message.author.name))
                            return
                        vote_id = self.generate_new_vote_id()
                        self.database.add_to_file_database(message.author.name, vote_id)
                        print(f"Associated {message.author.name} with {vote_id}")

                    case _:
                        await self.send_manual(message.author)

    async def send_manual(self, user):
        await user.send(DiscordBot.STRING_MANUAL)

    def generate_new_vote_id(self):
        vote_id = self.generate_vote_id()
        i = 0
        while self.database.check_vote_id(vote_id):
            vote_id = self.generate_vote_id()
            i += 1
            if i > 50:
                print("Error generating a Vote ID, critical")
        return vote_id

    def generate_vote_id(self):
        return "".join(random.choices(DiscordBot.VOTE_ID_ELEMENTS, k=DiscordBot.VOTE_ID_LENGTH))


    def run(self):
        self.client.run(self.discord_token)