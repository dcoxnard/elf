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

        commit_list = []
        with Session(self.engine) as session:
            for email, name, family, password in users:
                # TODO: depends on correct ordering in input
                user = User(email=email, name=name, family=family)
                user.set_password(password)
                commit_list.append(user)
            session.add_all(commit_list)
            session.commit()

    def make_pairs(self):
        """
        Generate a random pairing and persist it

        :return: None
        """
        with Session(self.engine) as session:
            users = session.query(User).all()
            partition = {user.email: user.family for user in users}
            user_names = list(partition.keys())
            pairs = make_pairs(user_names, partition)
            for left, right in pairs:
                santa = [user for user in users if user.email == left][0]
                recipient = [user for user in users if user.email == right][0]
                santa.recipient = recipient
                session.add(santa)
            session.commit()

    # TODO: Not sure about this function signature...
    def record_wishes(self, user_email, *wishes):
        with Session(self.engine) as session:
            user = (session
                    .query(User)
                    .where(User.email == user_email)
                    .one())
            for wish in wishes:
                new_wish = Wish(description=wish)  # TODO: Also for option Wish.link
                user.wishes.append(new_wish)
            session.add(user)
            session.commit()

    def get_user(self, user_email):
        with Session(self.engine) as session:
            user = (session
                    .query(User)
                    .where(User.email == user_email)
                    .one())
            return user
        #     user_dict = {
        #         "email": user.email,
        #         "name": user.name,
        #         "family": user.family,
        #         "wishes": [(w.description, w.link) for w in user.wishes],
        #     }
        #     if user.recipient is not None:
        #         recipient_details = {
        #             "recipient": user.recipient.name,
        #             "recipient_wishes": [
        #                 (w.description, w.link) for w in user.recipient.wishes
        #             ],
        #         }
        #     else:
        #         recipient_details = {
        #             "recipient": None,
        #             "recipient_wishes": None,
        #         }
        #     user_dict.update(recipient_details)
        # return user_dict
