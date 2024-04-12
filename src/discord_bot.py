import discord

class DiscordBot:
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
            if message.author == self.client.user:
                return

            if message.content.startswith('$hello'):
                await message.channel.send('Hello!')

    def run(self):
        self.client.run(self.discord_token)