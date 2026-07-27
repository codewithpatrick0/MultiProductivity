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
    categories: Mapped[list["Category"]] = relationship(back_populates="user")

class Task(Base):
    __tablename__="tasks"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    id_user: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    info: Mapped[str|None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), server_default='pending', nullable=False)
    id_category: Mapped[int] = mapped_column(BigInteger, ForeignKey('categories.id'), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, server_default='1', nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in progress', 'completed')",
            name="chk_status"
        ),
        CheckConstraint(
            "priority BETWEEN 1 AND 1000" ,
            name = "chk_priority"
            )
    )

    user: Mapped["User"] = relationship(back_populates="tasks")
    category: Mapped["Category"] = relationship(back_populates="tasks")


class Category(Base):
    __tablename__="categories"

    id:Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)

    user: Mapped["User"] = relationship(back_populates="categories")
    tasks: Mapped[list["Task"]] = relationship(back_populates="category")
