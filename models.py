from typing import Optional, List
import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


def make_temp_password():
    pw = str(uuid.uuid4())[:6]
    return pw


# TODO: Might need to live elsewhere
class CommunicationKind(enum.Enum):
    KICKOFF = "kickoff"
    REMINDER = "reminder"
    ACCOUNT_RECOVERY = "account_recovery"


class CommunicationStatus(enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


class Base(DeclarativeBase):
    pass


class User(Base, UserMixin):

    __tablename__ = "user"

    email: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    family: Mapped[str]
    image: Mapped[Optional[str]]
    recipient_email: Mapped[Optional[str]] = mapped_column(ForeignKey("user.email"))
    recipient: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[recipient_email],
        post_update=True,
        lazy="joined",
        join_depth=2,
        remote_side=[email]
    )
    previous_recipient_email: Mapped[Optional[str]] = mapped_column(ForeignKey("user.email"))
    previous_recipient: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[previous_recipient_email],
        lazy="joined",
        join_depth=2,
        remote_side=[email]
    )
    wishes: Mapped[List["Wish"]] = relationship(lazy="joined")
    communications = relationship("Communication")
    password_hash: Mapped[str]
    temporary_password: Mapped[str] = mapped_column(default=make_temp_password())
    user_has_set_own_password: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def recipient_set(self):
        return self.recipient is not None

    def n_wishes(self):
        if self.wishes is None:
            n = 0
        else:
            n = len(self.wishes)
        return n

    def set_password(self, password, user_has_set=True):
        self.password_hash = generate_password_hash(password)
        self.user_has_set_own_password = user_has_set

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.email

    def __repr__(self):
        return f"User(email={self.email}, name={self.name}, family={self.family}, recipient_set={self.recipient_set()}, n_wishes={self.n_wishes()})"


class Wish(Base):

    __tablename__ = "wish"

    wish_id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]
    link: Mapped[Optional[str]]
    user_email: Mapped[str] = mapped_column(ForeignKey("user.email"))

    def __repr__(self):
        return f"Wish(description={self.description}, link={self.link}"


class Communication(Base):

    __tablename__ = "communication"

    communication_id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
    kind: Mapped[CommunicationKind] = mapped_column(nullable=False)
    status: Mapped[CommunicationStatus] = mapped_column(nullable=False)
    detail: Mapped[Optional[str]]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
