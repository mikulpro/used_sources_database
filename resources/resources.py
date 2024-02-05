# resources.py
from .api import api
from .book import Book
from .booklist import BookList
from .bookcollection import BookCollectionNonID, BookCollectionID


api.add_resource(Book, "/books/<int:book_id>")
api.add_resource(BookList, "/books")
api.add_resource(BookCollectionNonID, "/collections")
api.add_resource(BookCollectionID, "/collections/<int:collection_id>")
