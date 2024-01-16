from __future__ import annotations

from db_init import db

from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, nullable=False)
#     author = db.Column(db.String, nullable=False)
#     type = db.Column(db.String, nullable=False)
#     year = db.Column(db.Integer, nullable=False)


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)


booklist_book_table = db.Table(
    "booklist_book",
    db.metadata,
    Column("booklist_id", ForeignKey("booklists.id"), primary_key=True),
    Column("book_id", ForeignKey("books.id"), primary_key=True)
)


class BookList(db.Model):
    __tablename__ = "booklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    books: Mapped[list[Book]] = relationship(secondary=booklist_book_table)
