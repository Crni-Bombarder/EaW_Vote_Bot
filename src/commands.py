import discord
import re
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

    @classmethod
    def init_commands(cls):
        HelpCommand()
        ManageWatchedGuildCommand()
        ManageAdminCommand()
        ManagePermissionCommand()
        ManageWatchedChannels()
        ManageSeniorVoteForums()
        ManageSeniorVoteReactions()
        ManageSeniorVoterRoles()
        ManageSeniorVoterRolesBlacklist()
        SeniorVoteCommand()

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

class ManageSeniorVoteForums(BotCommand):
    def __init__(self):
        super().__init__("manage-seniorvoteforums",
                         Scope.PRIVATE,
                         "Manage the vote forums watched by the bot",
                         "**manage-seniorvoteforums** add|remove|list\n\
Manage the vote forum watched by the bot. Threads created in them will automaticaly be added as new vote\n\
* **add** *forum_name*\nAdd the forum named *forum_name* to the watched channel list\n\
* **remove** *forum_name*\nRemove the forum named *forum_name* from the watched forum list\n\
* **list**\nShow the list of watched forums")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoteforums"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"All watched Forums")
            for channel in bot.settings["senior_vote_forums"]:
                embed.add_field(name=channel, value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            embed = discord.Embed(title=f'Not enough arguments or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoteforums"])
            return

        if argv[1] == "add":
            if argv[2] not in bot.settings["senior_vote_forums"]:
                bot.settings["senior_vote_forums"].append(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoteforums"].exec(bot, message, ["manage-seniorvoteforums" ,"list"])
            return

        if argv[1] == "remove":
            if argv[2] in bot.settings["senior_vote_forums"]:
                bot.settings["senior_vote_forums"].remove(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoteforums"].exec(bot, message, ["manage-seniorvoteforums" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoteforums"])

class ManageSeniorVoteReactions(BotCommand):
    def __init__(self):
        super().__init__("manage-seniorvotereactions",
                         Scope.PRIVATE,
                         "Manage the reactions used for the senior votes",
                         "**manage-seniorvoteforums** yes|abstaining|against|list\n\
Manage the reactions used for the senior votes\n\
* **yes** *emoji*\nSet the reaction used for a yes as *emoji*\n\
* **abstaining** *emoji*\nSet the reaction used for abstaining as *emoji*\n\
* **against** *emoji*\nSet the reaction used against as *emoji*\n\
* **list**\nShow the current reactions used for the votes")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvotereactions"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"Reactions used for the vote")
            embed.add_field(name="Yes", value=bot.settings["senior_vote_reactions"]["yes"], inline=False)
            embed.add_field(name="Abstaining", value=bot.settings["senior_vote_reactions"]["abstaining"], inline=False)
            embed.add_field(name="Against", value=bot.settings["senior_vote_reactions"]["against"], inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            embed = discord.Embed(title=f'Not enough arguments or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvotereactions"])
            return

        if argv[1] == "yes":
            bot.settings["senior_vote_reactions"]["yes"] = argv[2]
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvotereactions"].exec(bot, message, ["manage-seniorvotereactions" ,"list"])
            return

        if argv[1] == "abstaining":
            bot.settings["senior_vote_reactions"]["abstaining"] = argv[2]
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvotereactions"].exec(bot, message, ["manage-seniorvotereactions" ,"list"])
            return

        if argv[1] == "against":
            bot.settings["senior_vote_reactions"]["against"] = argv[2]
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvotereactions"].exec(bot, message, ["manage-seniorvotereactions" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvotereactions"])

class ManageSeniorVoterRoles(BotCommand):
    def __init__(self):
        super().__init__("manage-seniorvoterroles",
                         Scope.PRIVATE,
                         "Manage who has the right to vote",
                         "**manage-seniorvoterroles** add|remove|list\n\
Manage the roles that can vote.\n\
* **add** *role_name*\nAdd the role named *role_name* to the voter role list\n\
* **remove** *role_name*\nRemove the role named *role_name* from the voter role list\n\
* **list**\nShow the list of the voter roles")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterroles"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"All voter roles")
            for role in bot.settings["senior_vote_voter_roles"]:
                embed.add_field(name=role, value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            embed = discord.Embed(title=f'Not enough arguments or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterroles"])
            return

        if argv[1] == "add":
            if argv[2] not in bot.settings["senior_vote_voter_roles"]:
                bot.settings["senior_vote_voter_roles"].append(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoterroles"].exec(bot, message, ["manage-seniorvoterroles" ,"list"])
            return

        if argv[1] == "remove":
            if argv[2] in bot.settings["senior_vote_voter_roles"]:
                bot.settings["senior_vote_voter_roles"].remove(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoterroles"].exec(bot, message, ["manage-seniorvoterroles" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterroles"])

class ManageSeniorVoterRolesBlacklist(BotCommand):
    def __init__(self):
        super().__init__("manage-seniorvoterrolesblacklist",
                         Scope.PRIVATE,
                         "Manage what role unable the voting right",
                         "**manage-seniorvoterrolesblacklist** add|remove|list\n\
Manage what role unable the voting right.\n\
* **add** *role_name*\nAdd the role named *role_name* to the voter role blacklist\n\
* **remove** *role_name*\nRemove the role named *role_name* from the voter role blacklist\n\
* **list**\nShow the list of the voter blacklistes")

    async def exec(self, bot, message, argv):
        if len(argv) < 2:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterrolesblacklist"])
            return

        if argv[1] == "list":
            embed = discord.Embed(title=f"All blacklisted voter roles")
            for role in bot.settings["senior_vote_blacklisted_voter_roles"]:
                embed.add_field(name=role, value="", inline=False)
            await send_private_message(message, f'', embed=embed)
            return

        if len(argv) < 3:
            embed = discord.Embed(title=f'Not enough arguments or wrong command')
            await send_private_message(message, '', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterrolesblacklist"])
            return

        if argv[1] == "add":
            if argv[2] not in bot.settings["senior_vote_blacklisted_voter_roles"]:
                bot.settings["senior_vote_blacklisted_voter_roles"].append(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoterrolesblacklist"].exec(bot, message, ["manage-seniorvoterrolesblacklist" ,"list"])
            return

        if argv[1] == "remove":
            if argv[2] in bot.settings["senior_vote_blacklisted_voter_roles"]:
                bot.settings["senior_vote_blacklisted_voter_roles"].remove(argv[2])
            bot.settings.save_to_file()
            await BotCommand.list_command["manage-seniorvoterrolesblacklist"].exec(bot, message, ["manage-seniorvoterrolesblacklist" ,"list"])
            return

        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-seniorvoterrolesblacklist"])

class SeniorVoteCommand(BotCommand):
    def __init__(self):
        self.discord_thread_link_parser = re.compile(r"https://discord.com/channels/(\d+)/(\d+)")
        super().__init__("seniorvote",
                         Scope.PUBLIC,
                         "Start, stop, list, manage the senior votes currently running",
                         "**seniorvote** status|configuration\n\
Manage the votes. A vote is running using a thread. THis command need to be run on a server.\n\
* **status** [thread_id]\nDisplay the status of the vote the command is called in. Else try to find the vote corresponding to the thread provided (Through a link or thread ID directly).\
Else will display all the informations of every running vote\n\
* **content**:\n\
 * **add**\nAdd the message replied to as content.\n\
 * **remove**\Remove the message replied to as content.\n\
 * **[list]**\nList all the message that are considered content for the vote. Default if no argument for the content command\n\
* **list** *[command]*\nShow the roles that can call *command* if specified, else the permissions of all the commands")

    async def generate_vote_embed(self, bot, channel):
        embed = discord.Embed(title=f"{channel.name}")
        embed.add_field(name="Content link", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{channel.id}")
        return embed

    async def exec(self, bot, message, argv):
        if len(argv) < 2 or isinstance(message.channel, discord.DMChannel):
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"seniorvote"])
            return

        channel = message.channel
        in_voting_thread = str(channel.id) in bot.settings["senior_vote_list"]

        if argv[1] == "status":
            # If the command is launch in a voting thread, without argument
            if in_voting_thread and len(argv) == 2:
                embed = await self.generate_vote_embed(bot, channel)
                await channel.send("", embed=embed)
                return

            # If the command is launched with an argument
            if len(argv) > 2:
                match = self.discord_thread_link_parser.match(argv[2])
                thread_id = None
                if match:
                    thread_id = match.group(2)
                else:
                    try:
                        thread_id = int(argv[2])
                    except:
                        pass
                if not thread_id:
                    embed = discord.Embed(title=f'Wrong argument thread_id. Should be either a link to a thread or a thread id')
                    await channel.send('', embed=embed)
                    await BotCommand.list_command["help"].exec(bot, message, ["help" ,"seniorvote"])
                    return

                thread = message.guild.get_channel_or_thread(thread_id)
                if not thread:
                    try:
                        thread = await message.guild.fetch_channel(thread_id)
                    except discord.NotFound:
                        embed = discord.Embed(title=f'Could not find the thread with the thread id {thread_id}')
                        await channel.send('', embed=embed)
                        return

                embed = await self.generate_vote_embed(bot, thread)
                await channel.send("", embed=embed)
                return

            await bot.get_sem_vote_list()
            try:
                for vote_id_str in bot.settings["senior_vote_list"]:
                    vote_id = int(vote_id_str)
                    thread = message.guild.get_channel_or_thread(vote_id)
                    if not thread:
                        try:
                            thread = await message.guild.fetch_channel(vote_id)
                        except discord.NotFound:
                            embed = discord.Embed(title=f'Could not find the thread with the thread id {vote_id}')
                            await channel.send(message, '', embed=embed)
                            bot.free_sem_vote_list()
                            return
                    embed = await self.generate_vote_embed(bot, thread)
                    await channel.send("", embed=embed)
            finally:
                bot.free_sem_vote_list()

            bot.free_sem_vote_list()

        if argv[1] == "content":
            if not in_voting_thread:
                embed = discord.Embed(title=f'This command need to be executed inside a currently running vote')
                await channel.send(message, '', embed=embed)
                return

            if len(argv) == 2 or (len(argv) > 2 and argv[2] == "list"):
                embed = discord.Embed(title=f"{channel.name}")
                embed.add_field(name="Content 0", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{channel.id}")
                for i, elmt in enumerate(bot.settings["senior_vote_list"][str(channel.id)]["content"]):
                    embed.add_field(name=f"Content {i}", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{elmt}")
                channel.send('', embed=embed)
                return

            if (not argv[3] == "add") and (not argv[2] == "remove"):
                embed = discord.Embed(title=f'Invalid action for this command')
                await channel.send(message, '', embed=embed)
                return

            if not message.reference or message.reference.channel_id != channel.id:
                embed = discord.Embed(title="This command need to be executed inside a reply to another message in the thread")
                channel.send('', embed=embed)
                return

            print(message.reference)
            if argv[2] == "add":
                pass

            if argv[2] == "remove":
                pass


        if argv[1] == "amendment":
            pass

        if argv[1] == "start":
            pass

        if argv[1] == "close":
            pass