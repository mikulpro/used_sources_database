# models.py

from __future__ import annotations
from typing import List

from .db_init import db

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class BookType(db.Model):
    __tablename__ = "booktypes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    books: Mapped[List["Book"]] = relationship(back_populates="type")

    def __str__(self):
        return self.name


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("booktypes.id"))
    type: Mapped["BookType"] = relationship(back_populates="books")
    year: Mapped[int] = mapped_column(nullable=False)


bookcollection_book_table = db.Table(
    "bookcollection_book",
    db.metadata,
    Column("booklist_id", ForeignKey("bookcollections.id"), primary_key=True),
    Column("book_id", ForeignKey("books.id"), primary_key=True),
)


class BookCollection(db.Model):
    __tablename__ = "bookcollections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    books: Mapped[list["Book"]] = relationship(secondary=bookcollection_book_table)
