import discord
import re
import time
from enum import Enum
from src.commands import BotCommand, send_private_message, Scope

class ManageApplicationChannel(BotCommand):
    def __init__(self):
        super().__init__("manage-applicationchannel",
                         Scope.PRIVATE,
                         "Set and get the channel used by the bot to report the application",
                         "**manage-applicationchannel** set|list\n\
Manage application channel for the bot. New application and reminder will be posted here\n\
* **set**\nSet the current channel / thread as the application channel\n\
* **list**\nHow what is the current application channel")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-applicationchannel"])
            return

        if argv[1] == "list":
            # Fetch the channel or the thread
            try:
                application_channel = await message.guild.fetch_channel(bot.settings["application_channel"])
            except:
                await send_private_message(message, f'Application channel not set or not found')
                return
            embed = discord.Embed(title=f"Application channel")
            embed.add_field(name=f"{application_channel.jump_url}", value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if argv[1] == "set":
            bot.settings["application_channel"] = message.channel.id
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-application_channel"].exec(bot, message, ["manage-application_channel" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-application_channel"])
