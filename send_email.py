from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from create_email import create_email_message
from google_login import google_login


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
