import os
from email.message import EmailMessage

from sqlalchemy.orm import Session

from make_pairs import make_pairs
from models import User, Wish, Communication, CommunicationKind, \
    CommunicationStatus, make_temp_password
from db import engine, db_path
from mail import ADMIN_ADDR, MockSender
import messages
from app_token import generate_token


class Round:

    """
    A class to model all the actions taken in a round, including setup,
    and to capture helpful metadata.
    """

    engine = engine
    mailer = MockSender

    def __init__(self):

        if not os.path.isfile(db_path):
            from models import Base
            Base.metadata.create_all(engine)

    def has_users(self, check_number=3):  # TODO: Debug setting
        with Session(self.engine) as session:
            n = session.query(User).count()
        return n >= check_number

    def register_users(self, users):
        """
        Initialize DB with user information

        :param users: List[Tuple[str, str] of emails and names
        :return: number of users registered
        """

        with Session(self.engine) as session:
            # TODO: depends on correct ordering in input
            for email, name, family, password, is_admin, _ in users:
                email = email.lower()
                user = User(email=email, name=name, family=family,
                            temporary_password=password,
                            is_admin=is_admin)
                user.set_password(password, user_has_set=False)
                session.add(user)
            n_users = len(session.new)
            session.flush()
            for email, _, _, _, previous_recipient_email in users:
                left = (session
                        .query(User)
                        .where(User.email == email)
                        .one())
                right = (session
                         .query(User)
                         .where(User.email == previous_recipient_email)
                         .one())
                left.previous_recipient = right
                session.add(left)
            session.commit()
        return n_users

    def make_pairs(self):
        """
        Generate a random pairing and persist it

        :return: number of pairs persisted
        """
        with Session(self.engine) as session:
            users = session.query(User).all()
            partition = {user.email: user.family for user in users}
            previous_recipients = {user.email: user.previous_recipient.email for user in users}
            user_names = list(partition.keys())
            pairs = make_pairs(user_names, partition, previous_recipients)
            n_pairs = 0
            for left, right in pairs:
                santa = (session
                         .query(User)
                         .where(User.email == left)
                         .one())
                recipient = (session
                             .query(User)
                             .where(User.email == right)
                             .one())
                santa.recipient = recipient
                session.add(santa)
                n_pairs += len(session.dirty)
            session.commit()
        return n_pairs

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
            n_wishes = len(session.new)  # TODO: Test this
            session.add(user)
            session.commit()
        return n_wishes

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

    def send_email(self, user_email, subject_line, message):
        email = EmailMessage()
        email["From"] = ADMIN_ADDR
        email["To"] = user_email
        email["Subject"] = subject_line
        email.set_content(message)

        mailer = self.mailer()
        mailer.set_email_message(email)
        try:
            mailer.send_email_message()
        except Exception as e:
            status = CommunicationStatus.ERROR
            detail = str(e)
        else:
            status = CommunicationStatus.SUCCESS
            detail = None
        return status, detail

    def record_communication(self, user_email, kind, status, detail):
        with Session(self.engine) as session:
            comm = Communication(user_email=user_email,
                                 kind=kind,
                                 status=status,
                                 detail=detail)
            session.add(comm)
            session.commit()

    def send_kickoff_email(self, name, user_email, password):
        url = "localhost:5000"
        kickoff_message = messages.kickoff_message.format(name=name,
                                                          email=user_email,
                                                          password=password,
                                                          url=url)
        status, detail = self.send_email(user_email,
                                         messages.kickoff_subject_line,
                                         kickoff_message)
        self.record_communication(user_email,
                                  CommunicationKind.KICKOFF,
                                  status,
                                  detail)

    def send_all_kickoff_email(self):
        # Credentials only valid as long as nobody has set their PW yet
        sent_emails = []
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            for user in users:
                name = user.name
                email = user.email
                password = user.temporary_password
                self.send_kickoff_email(name, email, password)
                sent_emails.append(email)
        return sent_emails

    def send_reminder_email(self, name, user_email):
        url = "localhost:5000"
        reminder_message = messages.reminder_message.format(url=url, name=name,
                                                            email=user_email)
        status, detail = self.send_email(user_email,
                                         messages.reminder_subject_line,
                                         reminder_message)
        self.record_communication(user_email,
                                  CommunicationKind.REMINDER,
                                  status,
                                  detail)

    def send_all_reminder_email(self):
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            # This could be done in the qry itself, but doesn't make a big diff
            remind_users = [u for u in users if u.n_wishes() == 0]
            for user in remind_users:
                name = user.name
                email = user.email
                self.send_reminder_email(name, email)

    def send_recovery_email(self, user_email):
        url = "localhost:5000"
        with Session(self.engine) as session:
            name = (session
                    .query(User.name)
                    .where(User.email == user_email)
                    .one())[0]
        token = generate_token(user_email)
        recovery_message = messages.account_recovery_message.format(url=url,
                                                                    name=name,
                                                                    token=token)
        status, detail = self.send_email(user_email,
                                         messages.account_recovery_subject_line,
                                         recovery_message)
        self.record_communication(user_email,
                                  CommunicationKind.ACCOUNT_RECOVERY,
                                  status,
                                  detail)

    def status(self):
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            status_data = dict()
            for user in users:
                user_data = dict()
                for attr in [
                    "name",
                    "user_has_set_own_password",
                ]:
                    user_data[attr] = getattr(user, attr)
                for method in [
                    "recipient_set",
                    "n_wishes",
                ]:
                    user_data[method] = getattr(user, method).__call__()

                communications = sorted(user.communications, key=lambda c: c.timestamp)
                communications_data = []
                for comm in communications:
                    data = dict()
                    for attr in [
                        "communication_id",
                        "kind",
                        "status",
                        "detail",
                        "timestamp"
                    ]:
                        data[attr] = getattr(comm, attr)
                    communications_data.append(data)
                user_data["communications"] = communications_data

                status_data[user.email] = user_data
        return status_data

    def export_for_next_round(self):
        header = [
            "email",
            "name",
            "family",
            "image",
            "previous_recipient",
            "is_admin",
            "next_temporary_password"
        ]
        data = [header]
        with Session(self.engine) as session:
            users = (session
                     .query(User)
                     .all())
            for user in users:
                if user.recipient is not None:
                    recipient_email = user.recipient.email
                else:
                    recipient_email = None
                row = [
                    user.email,
                    user.name,
                    user.family,
                    user.image,
                    recipient_email,
                    user.is_admin
                ]
                temp_pw = make_temp_password()
                row.append(temp_pw)
                data.append(row)
        return data

    def import_from_previous_round(self, export_data):
        header = [
            "email",
            "name",
            "family",
            "image",
            "previous_recipient",
            "is_admin",
            "next_temporary_password"
        ]
        assert all([d == h for d, h in zip(export_data[0], header)])

        # Reshape for self.register_users
        # TODO: A lot of this shouldn't be necessary
        user_data = []
        for data in export_data[1:]:
            email, name, family, image, previous_recipient_email, is_admin, \
                password = data
            user_data.append([email, name, family, password, is_admin,
                              previous_recipient_email])
        self.register_users(user_data)


if __name__ == "__main__":
    round = Round()

    # import csv
    #
    # with open("sample_users.csv", "r") as f_obj:
    #     reader = csv.reader(f_obj)
    #     rows = [row for row in reader]
    #
    # header, users = rows[0], rows[1:]
    # round.register_users(users)
    #
    # from pprint import pprint
    # pprint(round.status())

    # round.export_for_next_round()

    round.send_kickoff_email("Alice", "alice@gmail.com", "otbnoirnborin")
    round.send_reminder_email("Alice", "alice@gmail.com")
    round.send_recovery_email("alice@gmail.com")
