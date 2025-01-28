import discord
import re
import time
from enum import Enum
from src.commands import BotCommand, send_private_message, Scope

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
        self.discord_thread_link_parser  = re.compile(r"https://discord.com/channels/(\d+)/(\d+)")
        self.discord_message_link_parser = re.compile(r"https://discord.com/channels/(\d+)/(\d+)/(\d+)")
        self.list_status = ["Running", "Accepted", "Refused", "Cancelled"]
        super().__init__("seniorvote",
                         Scope.PUBLIC,
                         "Start, stop, list, manage the senior votes currently running",
                         "**seniorvote** status|configuration\n\
Manage the votes. A vote is running using a thread. THis command need to be run on a server.\n\
* **status** [thread_id]\nDisplay the status of the vote the command is called in. Else try to find the vote corresponding to the thread provided (Through a link or thread ID directly).\
Else will display all the informations of every running vote\n\
* **content**:\n\
 * **add**: Add the message replied to as content.\n\
 * **remove**: Remove the message replied to as content.\n\
 * **[list]**: List all the message that are considered content for the vote. Default if no argument for the content command\n\
* **amendment**:\n\
 * **add** [*message_link*]: Add the message replied to or linked as an amendment.\n\
 * **close** [*cancelled*] [*message_link*]: Close the amendment voting. Canel it if _cancelled_ is added to the command. Target either the message that is replied to or the message linked with message_link\n\
 * **[list]**: List all the amendment and their status for the current vote.\n\
* **list** *[command]*\nShow the roles that can call *command* if specified, else the permissions of all the commands")

    async def generate_vote_embed(self, bot, channel):
        embed = discord.Embed(title=f"{channel.name}")
        embed.add_field(name="Content link", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{channel.id}")
        return embed

    def generate_amendment_embed(self, bot, channel, amendment_id):
        amendment = bot.settings["senior_vote_list"][str(channel.id)]["amendments"][amendment_id]
        embed = discord.Embed(title=f"Amendment {amendment["id"]}  https://discord.com/channels/{channel.guild.id}/{channel.id}/{amendment_id}")
        embed.add_field(name="Status", value=self.list_status[amendment["status"]])
        if not amendment["status"]:
            embed.add_field(name="Started", value=f'<t:{amendment["started"]}:R>')
        else:
            embed.add_field(name="Started", value=f'<t:{amendment["started"]}:f>')
            embed.add_field(name="Finished", value=f'<t:{amendment["closed"]}:f>')
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
                await channel.send('', embed=embed)
                return

            if len(argv) == 2 or (len(argv) > 2 and argv[2] == "list"):
                embed = discord.Embed(title=f"{channel.name}")
                embed.add_field(name="Root message", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{channel.id}")
                for i, elmt in enumerate(bot.settings["senior_vote_list"][str(channel.id)]["content"]):
                    embed.add_field(name=f"Content {i}", value=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{elmt}")
                await channel.send('', embed=embed)
                return

            if (argv[2] != "add") and (argv[2] != "remove"):
                embed = discord.Embed(title=f'Invalid action for this command')
                await channel.send('', embed=embed)
                return

            if not message.reference or message.reference.channel_id != channel.id:
                embed = discord.Embed(title="This command need to be executed inside a reply to another message in the thread")
                await channel.send('', embed=embed)
                return

            message_replied = await channel.fetch_message(message.reference.message_id)

            if argv[2] == "add":
                if str(message_replied.id) not in bot.settings["senior_vote_list"][str(channel.id)]["content"]:
                    bot.settings["senior_vote_list"][str(channel.id)]["content"].append(str(message_replied.id))
                    bot.settings.save_to_file()
                    embed = discord.Embed(title=f"Add https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_replied.id} to the vote content")
                    await channel.send('', embed=embed)
                else:
                    embed = discord.Embed(title=f"Message https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_replied.id} is already a content in the vote")
                    await channel.send('', embed=embed)
                await BotCommand.list_command["seniorvote"].exec(bot, message, ["seniorvote" ,"content"])
                return

            if argv[2] == "remove":
                if str(message_replied.id) in bot.settings["senior_vote_list"][str(channel.id)]["content"]:
                    bot.settings["senior_vote_list"][str(channel.id)]["content"].remove(str(message_replied.id))
                    bot.settings.save_to_file()
                    embed = discord.Embed(title=f"Remove https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_replied.id} from the vote content")
                    await channel.send('', embed=embed)
                else:
                    embed = discord.Embed(title=f"Message https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_replied.id} is not a contnet of the vote")
                    await channel.send('', embed=embed)
                await BotCommand.list_command["seniorvote"].exec(bot, message, ["seniorvote" ,"content"])
                return
            return


        if argv[1] == "amendment":
            if len(argv) == 2 or (len(argv) > 2 and argv[2] == "list"):
                if not in_voting_thread:
                    embed = discord.Embed(title=f'This command need to be executed inside a currently running vote')
                    await channel.send('', embed=embed)
                    return
                amendments = bot.settings["senior_vote_list"][str(channel.id)]["amendments"]
                embed = discord.Embed(title=f'"{channel.name}" Amendmends')
                if len(amendments) == 0:
                    embed.add_field(name=f'This vote has no amendment', value='')
                else:
                    for amendment_id, amendment in amendments.items():
                        embed.add_field(name=f'Amendment {amendment["id"]}',
                                        value=f'Link: https://discord.com/channels/{channel.guild.id}/{channel.id}/{amendment_id}, Status: {self.list_status[amendment["status"]]}')
                await channel.send('', embed=embed)
                return

            if (argv[2] != "add") and (argv[2] != "close"):
                    embed = discord.Embed(title=f'Invalid action for this command')
                    await channel.send('', embed=embed)
                    return

            # Catch the target amendment
            target_message_id = None
            target_message = None
            match = self.discord_message_link_parser.match(argv[-1])
            if match:
                target_message_id = int(match.group(3))
                target_channel_id = match.group(2)
            elif message.reference and message.reference.channel_id == channel.id:
                target_message_id = message.reference.message_id
                target_channel_id = message.reference.channel_id

            # If no amendment is found
            if not target_message_id:
                embed = discord.Embed(title="This command need to be executed inside a reply to another message in the thread, or with a link to a message in a voting thread")
                await channel.send('', embed=embed)
                return

            # Fetch the channel
            vote_channel = channel
            if target_channel_id != channel.id:
                vote_channel = channel.guild.get_channel_or_thread(target_channel_id)

            if not vote_channel:
                try:
                    vote_channel = await channel.guild.fetch_channel(target_channel_id)
                except discord.NotFound:
                    # TODO check if vote exist, and if it does cancel it
                    embed = discord.Embed(title="The channel specified does not exist")
                    await channel.send('', embed=embed)
                    return
            amendments = bot.settings["senior_vote_list"][str(vote_channel.id)]["amendments"]

            # Fetch the message targetted
            try:
                target_message = await channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                target_message = None

            # If the message is not found
            if not target_message:
                if str(target_message_id) in amendments:
                    amendment = amendments[str(target_message_id)]
                    amendment["status"] = 3 # Cancel the amendment
                    amendment["closed"] = int(time.time())
                    bot.settings.save_to_file()
                    embed = discord.Embed(title="Could not find the amendment message, but it is still exists in the data base", description="The amendment has been cancelled")
                else:
                    embed = discord.Embed(title="Could not find the amendment message", description="The message may have been deleted")
                await channel.send('', embed=embed)
                return

            if argv[2] == "add":
                if str(target_message.id) in amendments:
                    embed = discord.Embed(title=f"Message https://discord.com/channels/{channel.guild.id}/{vote_channel.id}/{target_message.id} is already an amendments")
                    await channel.send('', embed=embed)
                    return

                await bot.get_sem_vote_list()
                val_time = int(time.time())
                amendments[str(target_message.id)] = {
                    "id": len(amendments),
                    "status": 0, # 0 running, 1 accepted, 2 refused, 3 cancelled
                    "started": val_time,
                    "closed": 0,
                    "last_checked": val_time,
                    "results": [0, 0, 0, 0]
                }
                bot.settings.save_to_file()
                bot.free_sem_vote_list()

                embed = self.generate_amendment_embed(bot, channel, str(target_message.id))
                await channel.send('', embed=embed)
                return

            if argv[2] == "close":
                # Check the vote is not already closed
                if amendments[str(target_message.id)]["status"]:
                    embed = discord.Embed(title=f"Amendment https://discord.com/channels/{channel.guild.id}/{vote_channel.id}/{target_message.id} is already closed")
                    await channel.send('', embed=embed)
                    return

                if len(argv) > 3 and argv[3] == "cancelled":
                    amendments[str(target_message.id)]["status"] = 3
                return
            return

        if argv[1] == "start":
            pass

        if argv[1] == "close":
            pass