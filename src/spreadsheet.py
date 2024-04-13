import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SpreadsheetHandler:

    TOKEN_FILEPATH = "token.json"
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, credentials_path, spreadsheet_id, sheet_name):
        self.spreadsheet_id = spreadsheet_id

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(SpreadsheetHandler.TOKEN_FILEPATH):
            creds = Credentials.from_authorized_user_file(SpreadsheetHandler.TOKEN_FILEPATH, SpreadsheetHandler.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SpreadsheetHandler.SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(SpreadsheetHandler.TOKEN_FILEPATH, "w") as token:
                    token.write(creds.to_json())
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

        self.sheet_name = sheet_name
        self.current_index = self.get_next_index() + 1

    def get_next_index(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_name}!A:A")
            .execute()
        )
        rows = result.get("values", [])
        return len(rows)

    def write_vote_id(self, vote_id):
        result = (
            self.sheet.values()
            .update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A{self.current_index}",
                valueInputOption="USER_ENTERED",
                body={"values": [[vote_id]]},
            )
            .execute()
        )
        self.current_index += 1
