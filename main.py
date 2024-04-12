# TODO:

# Setup argparser
# Get discord dev token

import discord
import argparse

def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="A discord bot used to manage a user unique ID for vote through a google form"
        )
    discord_token = parser.add_mutually_exclusive_group()
    discord_token.add_argument("--discord-token-file", type=str, default="./discord_token.txt", help="Path to a file containing a discord authentification token")
    discord_token.add_argument("--discord-token", type=str, help="Discord authentification token to use")

    parser.add_argument("--google-token-file", type=str, default="./google_token.txt", help="Path to a file containing a google authentification token")

    return parser

if __name__ == "__main__":
    # Parsing arguments
    parser = create_arg_parser()
    parser.parse_args()