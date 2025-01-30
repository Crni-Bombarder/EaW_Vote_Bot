import discord
import re
import time
from enum import Enum
from src.commands import BotCommand, send_private_message, Scope

class ManageApplicationType(BotCommand):
    def __init__(self):
        super().__init__("manage-applicationtype",
                         Scope.PRIVATE,
                         "Set and get the different application type",
                         "**manage-applicationtype** set|delete|list\n\
Manage the different application type accepted by the bot. They correspond to the type field of the google form\n\
* **set** *name*\nAdd *name* as a new application type. The replied message will be the header for the application, and the current channel the channel the bot will post the replies.\n\
* **delete** *name*\nDelete *name* as an application type.\n\
* **list**\nList the current different application type")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"Application types")
            for name, content in bot.settings["application_type"].items():
                channel = await message.guild.fetch_channel(content["channel"])
                embed.add_field(name=f"{name}", value=f"Respond in {channel.jump_url}```{content["header"]}```", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])
            return

        if argv[1] == "set":
            content = ""
            if message.reference and isinstance(message.reference.resolved, discord.DeletedReferencedMessage):
                content = await message.reference.resolved.fetch()
            bot.settings["application_type"][argv[2]] = {"channel": message.channel.id, "header": content}
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-applicationtype"].exec(bot, message, ["manage-applicationtype" ,"list"])
            return

        if argv[1] == "delete":
            if argv[2] in bot.settings["application_type"]:
                bot.settings["application_type"].delete(argv[2])
            else:
                embed = discord.Embed(title=f"Unknown application type {argv[2]}")
            await BotCommand.list_command["manage-applicationtype"].exec(bot, message, ["manage-applicationtype" ,"list"])

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])

class Application(BotCommand):
    def __init__(self):
        super().__init__("application",
                         Scope.PRIVATE,
                         "Manage the application watched by the bot",
                         "**manage-applicationtype** list|close\n\
The application that I watch are managed by this command. You can list them or mark them as resolved. A reminder for all unresolved application will be send at fixed intervals\n\
* **list** *name*\nAdd *name* as a new application type. The replied message will be the header for the application, and the current channel the channel the bot will post the replies.\n\
* **resolve**\nMark the replied-to application as resolved""")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"Applications running")
            for name, content in bot.settings["application_type"].items():
                channel = await message.guild.fetch_channel(content["channel"])
                embed.add_field(name=f"{name}", value=f"Respond in {channel.jump_url}```{content["header"]}```", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])
            return

        if argv[1] == "set":
            content = ""
            if message.reference and isinstance(message.reference.resolved, discord.DeletedReferencedMessage):
                content = await message.reference.resolved.fetch()
            bot.settings["application_type"][argv[2]] = {"channel": message.channel.id, "header": content}
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-applicationtype"].exec(bot, message, ["manage-applicationtype" ,"list"])
            return

        if argv[1] == "delete":
            if argv[2] in bot.settings["application_type"]:
                bot.settings["application_type"].delete(argv[2])
            else:
                embed = discord.Embed(title=f"Unknown application type {argv[2]}")
            await BotCommand.list_command["manage-applicationtype"].exec(bot, message, ["manage-applicationtype" ,"list"])

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationtype"])
