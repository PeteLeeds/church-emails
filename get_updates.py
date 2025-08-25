from datetime import datetime
import os
from typing import List
from google_login import google_login
from googleapiclient.discovery import build

UPDATES_SPREADSHEET_ID = os.environ.get("UPDATES_SPREADSHEET_ID")


class Update:
    def __init__(self, row) -> None:
        self.title = row[1]
        self.description = row[2]
        self.displayUntil = datetime.strptime(row[3], "%m/%d/%Y")

    def in_date_range(self) -> bool:
        now = datetime.now()
        return self.displayUntil > now

    def format_for_email(self) -> str:
        formatted_event = f"<h3>{self.title}</h3>"
        formatted_event += f"<p>{self.description}<p>"
        return formatted_event


def get_update_objects() -> List[Update]:
    creds = google_login()
    service = build("sheets", "v4", credentials=creds)
    sheet_info = (
        service.spreadsheets().get(spreadsheetId=UPDATES_SPREADSHEET_ID).execute()
    )
    sheet_length = sheet_info["sheets"][0]["tables"][0]["range"]["endRowIndex"]
    sheet_data = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=UPDATES_SPREADSHEET_ID,
            range=f"Form Responses 1!A2:D{sheet_length}",
        )
        .execute()
    )
    updates = [Update(row) for row in sheet_data["values"]]
    return updates


def create_update_email() -> str:
    update_email = "<h2>Updates</h2>"
    updates = get_update_objects()
    for update in updates:
        if update.in_date_range():
            update_email += update.format_for_email()
    return update_email


print(create_update_email())
