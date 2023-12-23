import os

from sqlalchemy.orm import Session

from make_pairs import make_pairs
from models import User, Wish
from db import engine, db_path
from mail_api import MailApi, ADMIN_ADDR
import messages
from app_token import generate_token


class Round:

    """
    A class to model all the actions taken in a round, including setup,
    and to capture helpful metadata.
    """

    engine = engine

    def __init__(self):

        if not os.path.isfile(db_path):
            from models import Base
            Base.metadata.create_all(engine)

    def register_users(self, users):
        """
        Initialize DB with user information

        :param users: List[Tuple[str, str] of emails and names
        :return: None
        """

        with Session(self.engine) as session:
            # TODO: depends on correct ordering in input
            for email, name, family, password, _ in users:
                email = email.lower()
                if email == ADMIN_ADDR:
                    user = User(email=email, name=name, family=family,
                                temporary_password=password,
                                is_admin=True)
                else:
                    user = User(email=email, name=name, family=family,
                                temporary_password=password)
                user.set_password(password, user_has_set=False)
                session.add(user)
            session.flush()
            for email, _, _, _, previous_recipient_email in users:
                left = session.query(User).where(User.email == email).one()
                right = session.query(User).where(User.email == previous_recipient_email).one()
                left.previous_recipient = right
                session.add(left)
            session.commit()

    def make_pairs(self):
        """
        Generate a random pairing and persist it

        :return: None
        """
        with Session(self.engine) as session:
            users = session.query(User).all()
            partition = {user.email: user.family for user in users}
            previous_recipients = {user.email: user.previous_recipient.email for user in users}
            user_names = list(partition.keys())
            pairs = make_pairs(user_names, partition, previous_recipients)
            for left, right in pairs:
                santa = session.query(User).where(User.email == left).one()
                recipient = session.query(User).where(User.email == right).one()
                santa.recipient = recipient
                session.add(santa)
            session.commit()

    # TODO: Not sure about this function signature...
    def record_wishes(self, user_email, wishes, links):
        with Session(self.engine) as session:
            user = (session
                    .query(User)
                    .where(User.email == user_email)
                    .one())
            for wish, link in zip(wishes, links):
                if wish or link:
                    new_wish = Wish(description=wish, link=link)
                    user.wishes.append(new_wish)
            session.add(user)
            session.commit()

    # Eager load for flask-login
    def get_user(self, user_email):
        with Session(self.engine) as session:
            user = (session
                    .query(User)
                    .where(User.email == user_email)
                    .one())
            return user

    def set_user_password(self, user_email, password):
        with Session(self.engine) as session:
            user = (session
                    .query(User)
                    .where(User.email == user_email)
                    .one())
            user.set_password(password)
            session.add(user)
            session.commit()

    @staticmethod
    def send_email(user_email, subject_line, message):
        mailer = MailApi()
        from_ = ADMIN_ADDR
        mailer.send_email(from_=from_, to_=user_email,
                          subject_line=subject_line, message_body=message)

    def send_kickoff_email(self, name, user_email, password):
        url = "localhost:5000/"
        kickoff_message = messages.kickoff_message.format(name=name,
                                                          email=user_email,
                                                          password=password,
                                                          url=url)
        self.send_email(user_email, messages.kickoff_subject_line,
                        kickoff_message)

    def send_all_kickoff_email(self):
        # Credentials only valid as long as nobody has set their PW yet
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            for user in users:
                name = user.name
                email = user.email
                password = user.temporary_password
                self.send_kickoff_email(name, email, password)

    def send_reminder_email(self, user_email):
        self.send_email(user_email, messages.reminder_subject_line,
                        messages.reminder_message)

    def send_all_reminder_email(self):
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            # This could be done in the qry itself, but doesn't make a big diff
            remind_users = [u for u in users if u.n_wishes() == 0]
            for user in remind_users:
                email = user.email
                self.send_reminder_email(email)

    def send_recovery_email(self, user_email):
        token = generate_token(user_email)
        recovery_message = messages.account_recovery_message.format(token=token)
        self.send_email(user_email, messages.account_recovery_subject_line,
                        recovery_message)


if __name__ == "__main__":
    round = Round()

    # import csv

    # with open("sample_users.csv", "r") as f_obj:
    #     reader = csv.reader(f_obj)
    #     rows = [row for row in reader]
    #
    # header, users = rows[0], rows[1:]
    # round.register_users(users)

    round.send_all_kickoff_email()
