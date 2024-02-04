# resources.py
from flask_restx import Namespace

from models import db
from models import Book as Bookdb
from models import BookType as BookTypedb
from models import BookCollection

api = Namespace("books", description="Book related operations")

from .book import Book
api.add_resource(Book, "/books/<int:book_id>")

from .booklist import BookList
from .bookcollection import BookCollectionCreate, BookCollectionOperations


api.add_resource(BookList, "/books")

api.add_resource(BookCollectionCreate, '/collections')
api.add_resource(BookCollectionOperations, '/collections/<int:collection_id>')


