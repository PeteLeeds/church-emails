from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from create_email import create_email_message

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def google_login() -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def main() -> None:
    creds = google_login()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        gmail_send_message(service)

    except HttpError as error:
        print(f"An error occurred: {error}")


def gmail_send_message(service: any) -> None:
    try:
        message = MIMEMultipart("alternative")

        email_message = create_email_message()

        message.attach(MIMEText("Here are this week's church events", "plain"))
        message.attach(MIMEText(email_message, "html"))

        message["To"] = os.environ.get("EMAIL_TO")
        message["From"] = os.environ.get("EMAIL_FROM")
        message["Subject"] = "Upcoming Events"
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
