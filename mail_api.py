import os
import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]


class MailApi:

    creds = None
    service = None

    def send_test_email(self, from_, to):
        raise NotImplementedError

    def build_creds(self):
        raise NotImplementedError

    def initialize_service(self):
        raise NotImplementedError

    def send_email(self, from_, to_, subject_line, message_body):
        raise NotImplementedError


# https://developers.google.com/gmail/api/guides/sending#sending_messages
def gmail_send_message():
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # creds, _ = google.auth.default()
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        content = """
        This is automated draft mail!
        """
        message.set_content(content)

        message["To"] = ""
        message["From"] = ""
        message["Subject"] = "Test!"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # noinspection PyInterpreter
        send_message = (service.users()
                        .messages()
                        .send(userId="me", body=create_message)
                        .execute())
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


if __name__ == "__main__":
    gmail_send_message()
