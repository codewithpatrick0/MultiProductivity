from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Text, ForeignKey, Integer, CheckConstraint, Boolean, Identity

class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")

class Task(Base):
    __tablename__="tasks"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    info: Mapped[str|None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), server_default='pending', nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in progress', 'completed')",
            name="chk_status"
        ),
    )

    user: Mapped["User"] = relationship(back_populates="tasks")