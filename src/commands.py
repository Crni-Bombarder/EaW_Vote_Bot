import discord
import re
import time
from enum import Enum

class Scope(Enum):
    PRIVATE = 0
    PUBLIC = 1
    ANY = 2

async def send_private_message(message, content, embed=None):
    try:
        await message.author.send(content, embed=embed)
    except:
        await message.channel.send(content, embed=embed)

class BotCommand:

    list_command = {}

    def __init__(self, name, scope, short_desc, long_desc):
        self.name = name
        self.scope = scope
        self.short_desc = short_desc
        self.long_desc = long_desc
        BotCommand.list_command[name] = self

    @classmethod
    async def exec_command(cls, bot, message, argv):
        if argv[0] in BotCommand.list_command:
            await BotCommand.list_command[argv[0]].exec(bot, message, argv)
            return False
        return True

class HelpCommand(BotCommand):

    def __init__(self):
        super().__init__("help",
                         Scope.ANY,
                         "Used to display the commands available",
                         "**help** [command]\nDisplay the documentation of a particular command, or the list of command if none are provided")

    async def exec(self, bot, message, argv):
        if len(argv) > 1 and argv[1] in BotCommand.list_command:
            cmd = BotCommand.list_command[argv[1]]
            embed = discord.Embed(title=cmd.name, description=cmd.long_desc)
            await message.channel.send('', embed=embed)
        else:
            embed = discord.Embed(title="Available command list")
            for cmd in BotCommand.list_command.values():
                embed.add_field(name=cmd.name, value=cmd.short_desc, inline=False)
            await send_private_message(message, '', embed=embed)


class ManageAdminCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-admin",
                         Scope.PRIVATE,
                         "Manage the admin accounts for the bot",
                         "**manage-admin** add|remove|list\n\
Manage the admin accounts for the bot\n\
* **add** *name*\nAdd the discord ID *name* to the bot admin list\n\
* **remove** *name*\nRemove the discord ID *name* from the bot admin list\n\
* **list**\nList the current bot admins")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-admin"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title="Admin list")
            for admin_name in bot.settings["admin"]:
                embed.add_field(name=admin_name, value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-admin"])
            return

        if argv[1] == "add":
            if argv[2] not in bot.settings["admin"]:
                bot.settings["admin"].append(argv[2])
            bot.settings.save_to_file()
            embed = discord.Embed(title=f'Adding as admin "{argv[2]}"')
            await send_private_message(message, f'', embed=embed)
            return

        if argv[1] == "remove":
            if argv[2] in bot.settings["admin"]:
                bot.settings["admin"].remove(argv[2])
            bot.settings.save_to_file()
            embed = discord.Embed(title=f'Removing as admin "{argv[2]}"')
            await send_private_message(message, f'', embed=embed)
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-admin"])


class ManageWatchedGuildCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-watchedguild",
                         Scope.PRIVATE,
                         "Manage the admin accounts for the bot",
                         "**manage-admin** set|show\n\
Manage the watched guild, the server used for all the automated task and commands\n\
* **set** *guild_name*\nSet the name of the watched guild as *guild_name*\n\
* **show**\nShow the name of the watched server")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedguild"])
            return

        if argv[1] == "show":
            embed = discord.Embed(title="Watched Guild Name")
            embed.add_field(name=bot.settings["watched_guild_name"], value=str(bot.settings["watched_guild_id"]), inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedguild"])
            return

        if argv[1] == "set":
            name = argv[2]
            id = None
            for guild in bot.client.guilds:
                if guild.name == name:
                    id = int(guild.id)
                    break
            if not id:
                embed = discord.Embed(title=f'Cannot find the guild "{name}"')
                await send_private_message(message, f'', embed=embed)
                return
            bot.settings["watched_guild_name"] = name
            bot.settings["watched_guild_id"]   = id
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-watchedguild"].exec(bot, message, ["manage-watchedguild" ,"show"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedguild"])


class ManagePermissionCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-permission",
                         Scope.PRIVATE,
                         "Manage the command permissions",
                         "**manage-permission** add|remove|list\n\
Manage the command permissions. List the user roles that can call the command. No roles means it is admin only.\n\
* **add** *command* *role*\nAllow users with *role* to call *command*\n\
* **remove** *command* *role*\nNo longer allow users with *role* to call *command*\n\
* **list** *[command]*\nShow the roles that can call *command* if specified, else the permissions of all the commands")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-permission"])
            return

        if argv[1] == "list":
            if len(argv) > 2 and argv[2] in bot.settings["commands"]:
                embed = discord.Embed(title=f"**{argv[2]}** permissions")
                roles = bot.settings["commands"][argv[2]]
                if not roles:
                    roles = ["Admin only"]
                for role in roles:
                    embed.add_field(name=role, value="", inline=False)
            else:
                embed = discord.Embed(title=f"All command permissions")
                for cmd, roles in bot.settings["commands"].items():
                    if not roles:
                        roles = ["Admin only"]
                    desc = f"* {roles[0]}"
                    for i in range(1, len(roles)):
                        desc += f"\n* {roles[i]}"
                    embed.add_field(name=cmd, value=desc, inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 4 or argv[2] not in bot.settings["commands"]:
            embed = discord.Embed(title=f'Not enough argument or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-permission"])
            return

        if argv[1] == "add":
            if argv[3] not in bot.settings["commands"][argv[2]]:
                bot.settings["commands"][argv[2]].append(argv[3])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-permission"].exec(bot, message, ["manage-permission" ,"list", argv[2]])
            return

        if argv[1] == "remove":
            if argv[3] in bot.settings["commands"][argv[2]]:
                bot.settings["commands"][argv[2]].remove(argv[3])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-permission"].exec(bot, message, ["manage-permission" ,"list", argv[2]])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-permission"])


class ManageWatchedChannels(BotCommand):
    def __init__(self):
        super().__init__("manage-watchedchannels",
                         Scope.PRIVATE,
                         "Manage the channels watched by the bot in order to execute commands",
                         "**manage-watchedchannel** add|remove|list\n\
Manage the channels watched by the bot. A watched channel allow users to execute commands in them\n\
* **add** *channel_name*\nAdd the channel named *channel_name* to the watched channel list\n\
* **remove** *channel_name*\nRemove the channel named *channel_name* from the watched channel list\n\
* **list**\nShow the roles that can call *command* if specified, else the permissions of all the commands")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedchannels"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"All watched channels")
            for channel in bot.settings["watched_channels"]:
                embed.add_field(name=channel, value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            embed = discord.Embed(title=f'Not enough arguments or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedchannels"])
            return

        if argv[1] == "add":
            if argv[2] not in bot.settings["watched_channels"]:
                bot.settings["watched_channels"].append(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-watchedchannels"].exec(bot, message, ["manage-watchedchannels" ,"list"])
            return

        if argv[1] == "remove":
            if argv[2] in bot.settings["watched_channels"]:
                bot.settings["watched_channels"].remove(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-watchedchannels"].exec(bot, message, ["manage-watchedchannels" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-watchedchannels"])
