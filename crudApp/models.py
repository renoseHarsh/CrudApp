from typing import List

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL, Enum

from .sqlalchemy import db


class Employee(db.Model):
    EmployeeID: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(50))
    Email: Mapped[str] = mapped_column(String(50), unique=True)
    Department: Mapped[Enum] = mapped_column(
        Enum("HR", "IT", "Finance", "Sales"), nullable=True
    )
    Salary: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=True)
    JoiningDate: Mapped[Date] = mapped_column(Date, nullable=True)
    UserID: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="employees")


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    employees: Mapped[List["Employee"]] = relationship(back_populates="user")
