import os

from sqlalchemy.orm import Session

from make_pairs import make_pairs
from models import User, Wish
from db import engine, db_path


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
            for email, name, family, password, _ in users:
                # TODO: depends on correct ordering in input
                user = User(email=email, name=name, family=family)
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
