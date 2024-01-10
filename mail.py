import os
import base64
from email.message import EmailMessage
import logging
import abc

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
ADMIN_ADDR = os.environ["ADMIN_ADDR"]


class EmailSender(abc.ABC):

    def __init__(self):
        self.email = None

    def set_email_message(self, email):
        self.email = email

    @abc.abstractmethod
    def send_email_message(self):
        pass


class GmailSender(EmailSender):

    def send_message(self):
        """Create and send an email message
        Print the returned  message id
        Returns: Message object, including message id

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        if self.email is None:
            raise ValueError("No email message set")

        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        try:
            service = build("gmail", "v1", credentials=creds)

            # encoded message
            encoded_message = base64.urlsafe_b64encode(self.email.as_bytes()).decode()

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


class MockSender(EmailSender):

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    def send_email_message(self):
        msg = f"""
        SENDING EMAIL
FROM: {self.email["From"]}
TO: {self.email["To"]}
SUBJECT: {self.email["Subject"]}
MESSAGE: {self.email.get_payload()}
        """
        self.logger.info(msg.strip())


class ErrorSender(EmailSender):

    def send_email_message(self):
        raise RuntimeError("This is a mock error!")
