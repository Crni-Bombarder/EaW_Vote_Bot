class BotCommand:

    list_command = {}

    def __init__(self, name, short_desc, long_desc):
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        BotCommand.list_command[name] = self

    @classmethod
    async def exec_command(cls, message, argv):
        if argv[0] in BotCommand.list_command:
            await BotCommand.list_command[argv[0]].exec(message, argv)
            return False
        return True
    
    @classmethod
    def init_commands(cls):
        HelpCommand()
        ManageAdminCommand()
        ManagePermissionCommand()

class HelpCommand(BotCommand):

    def __init__(self):
        super().__init__("help", "Send help", "Help sends")

    async def exec(self, message, argv):
        await message.author.send(f'Execute command: {argv[0]}')

class ManageAdminCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-admin", "Used to manage the admin accounts for the bot", "Help sends")

    async def exec(self, message, argv):
        await message.author.send(f'Execute command: {argv[0]}')

class ManagePermissionCommand(BotCommand):
    def __init__(self):
        super().__init__("manage-permission", "Used to manage the commands permissions", "Help sends")

    async def exec(self, message, argv):
        await message.author.send(f'Execute command: {argv[0]}')