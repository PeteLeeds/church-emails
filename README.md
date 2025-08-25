# Church Emails Function

This repository contains a function that fetches events from a church's [A Church Near You](https://www.achurchnearyou.com/) page, formats them and sends them as an email.

## How to use

### Setup Gmail API

If you do not already have a Google Cloud project set up, first use [these instructions](https://developers.google.com/workspace/guides/create-project) to create one.

Then you will need to enable the Gmail API using the instructions on [this page](https://developers.google.com/workspace/gmail/api/quickstart/python). Once you have a `credentials.json` file, copy this into this repository.

### Environment setup

In order to run this project, you will need to set the following environment variables:
```
EMAIL_FROM = <Gmail address to send emails from - this should be the same account you are authenticating the project with>
EMAIL_TO = <The address to send emails to>
CONTACT_EMAIL = <A contact email to include in your email for people to get in touch>
CHURCH_ID = <The ID of your church on A Church Near You>
CHURCH_LOGO_URL = <A link to your church logo to display on the email (leave blank if not wanted)>
CHURCH_NAME = <The name of your church to display on the email header (leave blank if not wanted)>
UPDATES_SPREADSHEET_ID = <The ID of the Google sheet your forms are sending information to (leave blank if not wanted)>
```

For re-usability, you may want to save these in an `.env` file.

### Run the function

To run the code to send an email, run `python send_email.py`.