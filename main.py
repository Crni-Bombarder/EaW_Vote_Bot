import argparse
import sys
import time

from src.database import IDDatabase
from src.discord_bot import DiscordBot

def create_arg_parser():
    parser = argparse.ArgumentParser(description="A discord bot used to manage a user unique ID for vote through a google form")
    discord_token = parser.add_mutually_exclusive_group()
    discord_token.add_argument("--discord-token-file",
                               default="./discord_token.txt",
                               help="Path to a file containing a discord authentification token, default to ./discord_token.txt")
    discord_token.add_argument("--discord-token",
                               help="Discord authentification token to use")

    parser.add_argument("--google-token-file",
                        default="./google_token.txt",
                        help="Path to a file containing a google authentification token")
    parser.add_argument("--database-file",
                        default="./database.txt",
                        help="The path of the database file, default to database.txt")
    parser.add_argument("--reset-database",
                        action="store_true",
                        help="Reset the database at startup, deleting the previous one if it was present")
    parser.add_argument("--display-database",
                        action="store_true",
                        help="Display the database specified and quit")
    parser.add_argument("--bot-command",
                        default="$eaw-vote",
                        help="Prefix for the bot commands, default to $eaw-vote")
    parser.add_argument("--bot-channel",
                        default="general",
                        help="Channel name that the bot will parse, default to general")
    parser.add_argument("admin_name",
                        help="Discord ID of the admin")

    return parser

def get_discord_token_from_file(filepath):
    discord_token = None
    with open(filepath, "r") as fd:
        line = fd.readline().strip()
        while line:
            if line.startswith("#"):
                line = fd.readline().strip()
            else:
                discord_token = line
                break

    if not discord_token:
        print(f"Error, Token not found in {filepath}, exiting ...")
        sys.exit(0)
    return discord_token

if __name__ == "__main__":
    # Parsing arguments
    parser = create_arg_parser()
    args = parser.parse_args()

    # Get the discord token
    if args.discord_token:
        discord_token = args.discord_token
    else:
        discord_token = get_discord_token_from_file(args.discord_token_file)

    database = IDDatabase(args.database_file, args.reset_database)
    if args.display_database:
        print(str(database))
        sys.exit()
    discord_bot = DiscordBot(database, discord_token, args.bot_channel, args.bot_command, args.admin_name)
    discord_bot.run()
