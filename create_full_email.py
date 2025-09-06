from datetime import datetime
import os
from date_string import get_date_string
from get_events import create_event_email
from get_updates import create_update_email

CHURCH_LOGO_URL = os.environ.get("CHURCH_LOGO_URL")
CHURCH_NAME = os.environ.get("CHURCH_NAME")


def create_email() -> str:
    email = ""
    if CHURCH_LOGO_URL:
        email += f'<center><img style="width: 25rem;" src={CHURCH_LOGO_URL}></img>'
        email += f"<h2>{CHURCH_NAME + ' ' if CHURCH_NAME else ''}Event Update - {get_date_string(datetime.now())}</h2></center>"
    email += create_event_email()
    email += create_update_email()
    return email
