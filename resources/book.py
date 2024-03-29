# book.py

from flask_restx import Resource, fields
from flask import request

from .api import api
from db.models import db
from db.models import Book as Bookdb
from db.models import BookType as BookTypedb
from utils.utils import is_integer


# Define individual book model
book_model = api.model(
    "Book",
    {
        "id": fields.Integer,
        "title": fields.String,
        "author": fields.String,
        "type": fields.String(
            attribute=lambda book: book.type.name
            if type(book) == Bookdb and book.type
            else None
        ),
        "year": fields.Integer,
    },
)


# TODO get fix
class Book(Resource):
    @api.doc(
        description="Retrieve a book based on query parameters. Can filter by id, author, title, year, and book_type."
    )
    @api.marshal_with(book_model)
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def get(self, book_id=None):
        if book_id:
            result = db.session.query(Bookdb).filter(Bookdb.id == book_id).first()
        else:
            # Start with a base query
            query = db.session.query(Bookdb)

            # Check query parameters
            if "id" in request.args:
                id = request.args["id"]
                if is_integer(id):
                    query = query.filter(Bookdb.id == id)
                else:
                    return {"error": "Book id is not an integer"}, 400

            if "author" in request.args:
                query = query.filter(Bookdb.author == request.args["author"])

            if "title" in request.args:
                query = query.filter(Bookdb.title == request.args["title"])

            if "year" in request.args:
                year = request.args["year"]
                if len(year) > 4:
                    return {"error": "Year is too long"}, 400
                if not is_integer(year):
                    return {"error": "Year is not an integer"}, 400
                query = query.filter(db.Book.year == year)

            if "book_type" in request.args:
                book_type = request.args["book_type"]
                if book_type not in ["fiction", "non-fiction"]:
                    return {"error": 'Type must be "fiction" or "non-fiction"'}, 400
                query = query.filter(Bookdb.type.has(name=book_type))

            result = query.all()

        # Return the result
        if not result:
            return {"error": "No books found"}, 404

        return result, 200

    @api.doc(description="Update an existing book.")
    @api.expect(book_model, validate=True)
    @api.marshal_with(book_model)
    @api.response(200, "Book Updated")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def put(self, book_id):
        # Get the JSON data from the request
        data = request.json
        if data is None:
            return {"error": "No JSON data provided"}, 400

        # Validate that the required fields are present in the JSON data and that they are correct
        if "title" not in data:
            return {"error": 'Missing "title" field in JSON data'}, 400
        if "author" not in data:
            return {"error": 'Missing "author" field in JSON data'}, 400
        if "type" not in data:
            return {"error": 'Missing "type" field in JSON data'}, 400
        if data["type"] not in ["fiction", "non-fiction"]:
            return {"error": 'Type must be "fiction" or "non-fiction"'}, 400
        if "year" not in data:
            return {"error": 'Missing "year" field in JSON data'}, 400
        if not is_integer(data["year"]):
            return {"error": "Year is not an integer"}, 400
        if len(str(data["year"])) > 4:
            return {"error": "Year is too long"}, 400

        book = db.session.query(Bookdb).filter(Bookdb.id == book_id).first()
        if not book:
            return {"error": f"Book with id {book_id} does not exist"}, 404

        put_id = None
        try:
            book.title = data.get("title")
            book.author = data.get("author")
            book.year = data.get("year")
            booktype = (
                db.session.query(BookTypedb)
                .filter(BookTypedb.name == data.get("type"))
                .first()
            )
            book.type_id = booktype.id
            db.session.commit()
            put_id = book.id
            return book, 200
        except Exception as e:
            api.logger.error(f"Failed to modify book with id {book_id}! {e}")
            return {"error": "Failed to modify book", "id": put_id}, 500

    def head(self):
        return {
            "headers": {
                "header0": "id",
                "header1": "title",
                "header2": "author",
                "header3": "type",
                "header4": "year",
            }
        }, 200

    def trace(self):
        return {"message": "Disabled for security reasons."}, 405

    @api.doc(description="Delete a book based on its ID.")
    @api.response(200, "Book Deleted")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def delete(self, book_id):
        book = db.session.query(Bookdb).filter(Bookdb.id == book_id).first()
        if not book:
            return {"error": f"Book with id {book_id} does not exist"}, 404
        try:
            db.session.delete(book)
            db.session.commit()
            return {"message": f"Book with id {book_id} deleted successfully"}, 200
        except Exception as e:
            api.logger.error(f"Failed to delete book with id {book_id}! {e}")
            return {"error": "Book wasn't deleted"}, 500
