import os

from sqlalchemy.orm import Session

from models import User
from db import engine, db_path


class Round:

    """
    A class to model all of the actions taken in a round, including setup,
    and to capture helpful metadata.
    """

    def __init__(self):
        self.engine = engine

        if not os.path.isfile(db_path):
            from models import Base
            Base.metadata.create_all(engine)

    def register_users(self, users):
        """
        Initialize DB with user information
        :param users: List[Tuple[str, str] of emails and names
        :return: None
        """

        if os.path.isfile(db_path):
            raise RuntimeError(f"DB Already set up at {db_path}")

        commit_list = []
        with Session(self.engine) as session:
            for email, name in users:
                user = User(email=email, name=name)
                commit_list.append(user)
            session.add_all(commit_list)
            session.commit()
