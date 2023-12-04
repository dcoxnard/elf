import os

from sqlalchemy.orm import Session

from make_pairs import make_pairs
from models import User
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
            for email, name, family in users:
                # TODO: depends on correct ordering in input
                user = User(email=email, name=name, family=family)
                commit_list.append(user)
            session.add_all(commit_list)
            session.commit()

    def make_pairs(self):
        with Session(self.engine) as session:
            users = session.query(User).all()
            partition = [{user.email: user.family} for user in users]
            user_names = list(partition.keys())
            pairs = make_pairs(user_names, partition)
            for left, right in pairs:
                santa = [user for user in user if user.email == left][0]
                recipient = [user for user in user if user.email == right][0]
                santa.recipient = recipient
                session.add(santa)
            session.commit()
