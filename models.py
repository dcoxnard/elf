from typing import Optional, List

# Going to try the new-style SQLAlchemy ORM API
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "user"

    email: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    family: Mapped[str]
    image: Mapped[Optional[str]]
    recipient_email: Mapped[Optional[str]] = mapped_column(ForeignKey("user.email"))
    recipient: Mapped[Optional["User"]] = relationship("User", post_update=True)
    wishes: Mapped[List["Wish"]] = relationship()

    def recipient_set(self):
        return self.recipient is not None

    def n_wishes(self):
        if self.wishes is None:
            n = 0
        else:
            n = len(self.wishes)
        return n

    def __repr__(self):
        return f"User(email={self.email}, name={self.name}, family={self.family}, recipient_set={self.recipient_set()}, n_wishes={self.n_wishes()})"


class Wish(Base):

    __tablename__ = "wish"

    wish_id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]
    link: Mapped[Optional[str]]
    user_email = mapped_column(ForeignKey("user.email"))

    # TODO: def __repr__
