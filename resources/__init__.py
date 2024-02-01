# resources.py
from flask_restx import Namespace

from models import db
from models import Book as Bookdb
from models import BookType as BookTypedb
from models import BookList as BookListdb

api = Namespace("books", description="Book related operations")

from .book import Book
api.add_resource(Book, "/books")

from .booklist import BookList
from .bookcollection import BookCollection


api.add_resource(BookList, "/booklists")
api.add_resource(BookCollection, "/collections")

