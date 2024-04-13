# EaW_Vote_Bot
A custom Discord bot to allow the EaW team to run seemlessly an internal election process

## Setting up
### Python environment
You need Python 3.XX or later installed

Create a virtual environment and run it

```
python -m venv env
& ./env/Scripts/Activate.ps1 # For exemple for windows and in a PowerShell
```

Then install the requirement

```
pip install -r requirements.txt
```

### Generate the discord bot token
You need to generate a bot token in order to use this bot.
* Go to https://discord.com/developers/applications
* Create a new application
* In the Bot tab, activate the Presence, Server Members and Message Content Intents
* In the OAuth2 tab, click on "Reset Secret" and copy the given token into the discord_token.txt file
* You can then generate an invitation link for the bot in the same tab, using a **bot** URL with "Read Messages/View Channels" permission
### Generate Google Credentials
In order for the bot to access a spreadsheet, you need to generate a credential for the Google API
* Go to https://console.cloud.google.com/apis/dashboard, and click at the top of the page on the "Enable APIS and Services" button. Search for Google Sheets API and activate it
* Return to your dashboard, and in the left panel select the OAuth consent screen
  * You need to create a new App, use the External if you cannot put it as Internal
  * Add your google account as test user
  * Fill the rest as you see fit, it doesn't matter
* Once it is done, go to the Credentials tab and create a new credentials for OAuth client ID
* Select a Desktop App and give it a name
* Once it is done, download the JSON, and put it in the bot root folder as **google_credentials.json** (Default name)

You are all set up to start up the bot

## How to use
```
usage: main.py [-h] [--discord-token-file DISCORD_TOKEN_FILE | --discord-token DISCORD_TOKEN] [--google-token-file GOOGLE_TOKEN_FILE] [--database-file DATABASE_FILE] [--reset-database] [--display-database]
               [--bot-command BOT_COMMAND] [--bot-channel BOT_CHANNEL]
               admin_name [spreadsheet_id]

A discord bot used to manage a user unique ID for vote through a google form

positional arguments:
  admin_name            Discord ID of the admin
  spreadsheet_id        ID of the Google Sheet, included in the URL (Example: https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0)

options:
  -h, --help            show this help message and exit
  --discord-token-file DISCORD_TOKEN_FILE
                        Path to a file containing a discord authentification token. Default to ./discord_token.txt
  --discord-token DISCORD_TOKEN
                        Discord authentification token to use
  --google-token-file GOOGLE_TOKEN_FILE
                        Path to a file containing a google authentification token. Default to google_credentials.json
  --database-file DATABASE_FILE
                        The path of the database file, default to database.txt
  --reset-database      Reset the database at startup, deleting the previous one if it was present
  --display-database    Display the database specified and quit
  --bot-command BOT_COMMAND
                        Prefix for the bot commands, default to $eaw-vote
  --bot-channel BOT_CHANNEL
                        Channel name that the bot will parse, default to general
```
### Exemples
```
# Start the bot, reset the database with the admin being crnibombarder
python main.py --reset-database crnibombarder
```

```
# Start the bot with a token from the command line, and a specific spreadsheet
python main.py --discord-token <TOKEN> -- crnibombarder <SPREADSHEETID>
```

```
# Start the bot with custom command prefix and
python main.py --discord-token <TOKEN> -- crnibombarder <SPREADSHEETID>
```
## Generating a release
The packet pyinstaller is used to generate a release package:
```
pyinstaller main.py -F
```