# resources.py
from flask import request
from flask_restx import Namespace, Resource, fields, reqparse

from utils import get_db_connection, is_integer
from models import db
from models import Book as Bookdb
from models import BookType as BookTypedb
from models import BookCollection as BookCollectiondb


api = Namespace("books", description="Book related operations")

# Define individual book model
book_model = api.model(
    "Book",
    {
        "id": fields.Integer,
        "title": fields.String,
        "author": fields.String,
        "type": fields.String(attribute=lambda book: book.type.name if type(book) == Bookdb and book.type else None),
        "year": fields.Integer,
    },
)

# Define list of books model
book_list_model = api.model(
    "BookList", {"books": fields.List(fields.Nested(book_model))}
)

parser = reqparse.RequestParser()
parser.add_argument(
    "id", type=int, required=True, help="ID cannot be blank and must be an integer."
)
parser.add_argument("title", required=False, help="Title cannot be blank.")
parser.add_argument("author", required=False, help="Author cannot be blank.")
parser.add_argument(
    "type", required=False, help="Type must be either 'fiction' or 'non-fiction'."
)
parser.add_argument(
    "year",
    type=int,
    required=False,
    help="Year cannot be blank and must be an integer lesser than 10000.",
)


class Book(Resource):
    @api.doc(
        description="Retrieve a book based on query parameters. Can filter by id, author, title, year, and book_type."
    )
    @api.marshal_with(book_model)
    @api.expect(parser)
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def get(self, book_id=None):
        if book_id:
            result = Bookdb.query.get(book_id)
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

    @api.doc(description="Add a new book to the database.")
    @api.expect(book_model, validate=True)
    @api.response(201, "Book Created")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self, booklist_id=None):
        # Get the JSON data from the request
        data = request.json
        if data is None:
            return {"error": "No JSON data provided"}, 400

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

        try:
            booktype = BookTypedb.query.filter_by(name=data["type"]).first()
            book = Bookdb(
                title=data["title"],
                author=data["author"],
                type_id=booktype.id,
                year=data["year"]
            )
            if booklist_id:
                booklist = BookListdb.query.get(booklist_id)
                if not booklist:
                    return {"error": f"Booklist with id {booklist_id} does not exist"}, 404
                booklist.books.append(book)
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            api.logger.error(f'Failed to insert a book! {e}')
            return {"error": "Book wasn't inserted"}, 500
        return {"message": "New book inserted successfully"}, 201

    @api.doc(description="Update an existing book.")
    @api.expect(book_model, validate=True)
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

        book = Bookdb.query.get(book_id)
        if not book:
            return {"error": f"Book with id {book_id} does not exist"}, 404

        try:
            book.title = data.get("title")
            book.author = data.get("author")
            book.year = data.get("year")
            booktype = BookTypedb.query.filter_by(name=data.get("type")).first()
            book.type_id = booktype.id
            db.session.commit()
            return {"message": f"Book with id {book_id} modified successfully"}, 200
        except Exception as e:
            api.logger.error(f'Failed to modify book with id {book_id}! {e}')
            return {"error": "Book wasn't modified"}, 500

    # not sure this is correct
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
    @api.expect(parser)
    @api.response(200, "Book Deleted")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def delete(self, book_id):
        book = Bookdb.query.get(book_id)
        if not book:
            return {"error": f"Book with id {book_id} does not exist"}, 404
        try:
            db.session.delete(book)
            db.session.commit()
            return {"message": f"Book with id {book_id} deleted successfully"}, 200
        except Exception as e:
            api.logger.error(f'Failed to delete book with id {book_id}! {e}')
            return {"error": "Book wasn't deleted"}, 500


class BookList(Resource):
    @api.doc(
        description="Retrieve a list of books based on query parameters. Can filter by id, author, title, year, and type."
    )
    @api.marshal_with(book_list_model)
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.response(404, "No Books Found")
    @api.response(500, "Internal Server Error")
    def get(self, book_id=None):
        if book_id:
            result = Bookdb.query.get(book_id)
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

        return {"books": result}, 200

    @api.doc(description="Add multiple new books to the database.")
    @api.expect(book_model, validate=True)
    @api.response(201, "Books Created")
    @api.response(207, "Partial Success with Errors")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self):
        # Parse the JSON body of the request
        try:
            books_data = request.get_json()
        except:
            return {"error": "Invalid JSON format"}, 400

        # Validate and insert each book
        inserted_books = []
        errors = []

        for book_data in books_data["books"]:
            if all(key in book_data for key in ["title", "author", "type", "year"]):
                try:
                    booktype = BookTypedb.query.filter_by(name=book_data["type"]).first()
                    book = Bookdb(
                        title=book_data["title"],
                        author=book_data["author"],
                        type_id=booktype.id,
                        year=book_data["year"]
                    )
                    db.session.add(book)
                except Exception as e:
                    api.logger.error(f'Failed to insert a book! {e}')
                    errors.append({"book": book})

            else:
                errors.append({"book": book, "error": "Missing required fields"})

        db.session.commit()

        # Return the result
        if errors:
            return {"inserted_books": inserted_books, "errors": errors}, 207
        else:
            return {
                "message": "All books inserted successfully",
                "inserted_books": inserted_books,
            }, 201

    @api.doc(description="TRACE method, disabled for security reasons.")
    @api.response(405, "Method Not Allowed")
    def trace(self):
        return {"message": "Disabled for security reasons."}, 405

    @api.doc(description="HEAD method to retrieve headers for the book list.")
    @api.response(200, "Success")
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


api.add_resource(Book, "/books")
api.add_resource(Book, "/books/<int:book_id>")
api.add_resource(Book, "/booklists/<int:booklist_id>/books")
api.add_resource(BookList, "/booklists")
api.add_resource(BookList, "/booklists/<int:booklist_id>")
