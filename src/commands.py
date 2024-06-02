import discord

class BotCommand:

    list_command = {}

    def __init__(self, name, short_desc, long_desc):
        self.name = name
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
        ManageAdminCommand()
        ManagePermissionCommand()

class HelpCommand(BotCommand):

    def __init__(self):
        super().__init__("help",
                         "Used to display the commands available",
                         "**help** [command]\nDisplay the documentation of a particular command, or the list of command if none are provided")

    async def exec(self, bot, message, argv):
        if len(argv) > 1 and argv[1] in BotCommand.list_command:
            cmd = BotCommand.list_command[argv[1]]
            embed = discord.Embed(title=cmd.name, description=cmd.long_desc)
        else:
            embed = discord.Embed(title="Available command list")
            for cmd in BotCommand.list_command.values():
                embed.add_field(name=cmd.name, value=cmd.short_desc, inline=False)
        await message.author.send(f'', embed=embed)

class ManageAdminCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-admin",
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
            for admin_name in bot.authorization["admin"]:
                embed.add_field(name=admin_name, value="", inline=False)
            await message.author.send(f'', embed=embed)
            return
        
        if len(argv) < 3:
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage_admin"])
            return
        
        if argv[1] == "add":
            if argv[2] not in bot.authorization["admin"]:
                bot.authorization["admin"].append(argv[2])
            bot.authorization.save_to_file()
            embed = discord.Embed(title=f'Adding as admin "{argv[2]}"')
            await message.author.send(f'', embed=embed)
            return

        if argv[1] == "remove":
            if argv[2] in bot.authorization["admin"]:
                bot.authorization["admin"].remove(argv[2])
            bot.authorization.save_to_file()
            embed = discord.Embed(title=f'Removing as admin "{argv[2]}"')
            await message.author.send(f'', embed=embed)
            return
        
        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage_admin"])

class ManagePermissionCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-permission",
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
            if len(argv) > 2 and argv[2] in bot.authorization["commands"]:
                embed = discord.Embed(title=f"**{argv[2]}** permissions")
                roles = bot.authorization["commands"][argv[2]]
                if not roles:
                    roles = ["Admin only"]
                for role in roles:
                    embed.add_field(name=role, value="", inline=False)
            else:
                embed = discord.Embed(title=f"All command permissions")
                for cmd, roles in bot.authorization["commands"].items():
                    if not roles:
                        roles = ["Admin only"]
                    desc = f"* {roles[0]}"
                    for i in range(1, len(roles)):
                        desc += f"\n* {roles[i]}"
                    embed.add_field(name=cmd, value=desc, inline=False)
            await message.author.send(f'', embed=embed)
            return
        
        if len(argv) < 4 or argv[2] not in bot.authorization["commands"]:
            embed = discord.Embed(title=f'Not enough argument or wrong command')
            await message.author.send('', embed=embed)
            await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-permission"])
            return
        
        if argv[1] == "add":
            if argv[3] not in bot.authorization["commands"][argv[2]]:
                bot.authorization["commands"][argv[2]].append(argv[3])
            bot.authorization.save_to_file()
            await BotCommand.list_command["manage-permission"].exec(bot, message, ["manage-permission" ,"list", argv[2]])
            return

        if argv[1] == "remove":
            if argv[3] in bot.authorization["commands"][argv[2]]:
                bot.authorization["commands"][argv[2]].remove(argv[3])
            bot.authorization.save_to_file()
            await BotCommand.list_command["manage-permission"].exec(bot, message, ["manage-permission" ,"list", argv[2]])
            return
        
        await BotCommand.list_command["help"].exec(bot, message, ["help" ,"manage-permission"])
