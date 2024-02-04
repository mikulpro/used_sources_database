# resources.py
from flask_restx import Namespace


api = Namespace("books", description="Book related operations")

from .book import Book
api.add_resource(Book, "/books/<int:book_id>")

from .booklist import BookList
from .bookcollection import BookCollectionNonID, BookCollectionID


api.add_resource(BookList, "/books")

api.add_resource(BookCollectionNonID, '/collections')
api.add_resource(BookCollectionID, '/collections/<int:collection_id>')



