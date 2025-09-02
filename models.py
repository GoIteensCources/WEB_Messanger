from flask_login import UserMixin
from sqlalchemy import ForeignKey, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash

from settings import Base, Session


class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)

    is_admin: Mapped[bool] = mapped_column(default=False)

    sent_requests: Mapped[list["Friends"]] = relationship(
        "Friends",
        foreign_keys="Friends.sender",
        back_populates="sender_user",
        cascade="all, delete-orphan",
    )
    received_requests: Mapped[list["Friends"]] = relationship(
        "Friends",
        foreign_keys="Friends.recipient",
        back_populates="recipient_user",
        cascade="all, delete-orphan",
    )

    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender",
        back_populates="sender_user",
        cascade="all, delete-orphan",
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.recipient",
        back_populates="recipient_user",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return f"User: {self.username}"

    @staticmethod
    def get(user_id: int):
        with Session() as conn:
            stmt = select(User).where(User.id == user_id)
            user = conn.scalar(stmt)
            if user:
                return user

    @staticmethod
    def get_by_username(username):

        with Session() as conn:
            stmt = select(User).where(User.username == username)
            user = conn.scalar(stmt)
            return user if user else None


class Friends(Base):
    __tablename__ = "friends"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient: Mapped[int] = mapped_column(ForeignKey("users.id"))

    status: Mapped[bool] = mapped_column(
        default=False
    )  # False - очікує підтвердження, True - підтверджено

    sender_user: Mapped["User"] = relationship(
        "User", foreign_keys="Friends.sender", back_populates="sent_requests"
    )
    recipient_user: Mapped["User"] = relationship(
        "User", foreign_keys="Friends.recipient", back_populates="received_requests"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient: Mapped[int] = mapped_column(ForeignKey("users.id"))

    message_text: Mapped[str] = mapped_column(Text)
    status_check: Mapped[bool] = mapped_column(default=False)

    sender_user: Mapped["User"] = relationship(
        "User", foreign_keys="Message.sender", back_populates="sent_messages"
    )
    recipient_user: Mapped["User"] = relationship(
        "User", foreign_keys="Message.recipient", back_populates="received_messages"
    )


# Ініціалізація бази даних і додавання товарів
def init_db():
    base = Base()
    base.drop_db()
    base.create_db()  # Створюємо таблиці

    user_admin = User(
        username="admin", email="ax@gmail.com", password=generate_password_hash("admin")
    )
    user = User(
        username="user", email="user@gmail.com", password=generate_password_hash("user")
    )
    with Session() as conn:
        conn.add_all([user_admin, user])
        conn.flush()
        conn.commit()


if __name__ == "__main__":
    init_db()
