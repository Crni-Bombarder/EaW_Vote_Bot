# TODO:

# Setup argparser
# Get discord dev token

import discord
import argparse
import sys

def create_arg_parser():
    parser = argparse.ArgumentParser(description="A discord bot used to manage a user unique ID for vote through a google form")
    discord_token = parser.add_mutually_exclusive_group()
    discord_token.add_argument("--discord-token-file",
                               type=str,
                               default="./discord_token.txt",
                               help="Path to a file containing a discord authentification token, default to ./discord_token.txt")
    discord_token.add_argument("--discord-token",
                               type=str,
                               help="Discord authentification token to use")

    parser.add_argument("--google-token-file",
                        type=str,
                        default="./google_token.txt",
                        help="Path to a file containing a google authentification token")

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

    if args.discord_token:
        discord_token = args.discord_token
    else:
        discord_token = get_discord_token_from_file(args.discord_token_file)

