from typing import Optional, List

# Going to try the new-style SQLAlchemy ORM API
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, \
    relationship, validates, Session


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "user"

    email: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    image: Mapped[Optional[str]]
    recipient_email: Mapped[Optional[str]] = mapped_column(ForeignKey("user.email"))
    recipient: Mapped[Optional["User"]] = relationship("User")
    wishes: Mapped[Optional[List["Wish"]]] = relationship()

    @validates("recipient", include_backrefs=False)
    def validate_one_recipient(self, key, recipient):
        if recipient is not None and len(recipient) > 1:
            raise ValueError("Failed validation of exactly one recipient")
        return recipient

    def recipient_set(self):
        return self.recipient is not None

    def n_wishes(self):
        if self.wishes is None:
            n = 0
        else:
            n = len(self.wishes)
        return n

    def __repr__(self):
        return f"User(email={self.email}, name={self.name}, recipient_set={self.recipient_set()}, n_wishes={self.n_wishes()})"


class Wish(Base):

    __tablename__ = "wish"

    wish_id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]
    link: Mapped[Optional[str]]
    user_email = mapped_column(ForeignKey("user.email"))


# Quick test script
# Insert 1x user with 1x wish
# Script doesn't delete any existing DB automatically
if __name__ == "__main__":
    from db import engine
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(email="my_email", name="my_name")
        user.wishes.append(Wish(description="my_wish", link="www.mylink.com"))
        session.add(user)
        session.commit()
