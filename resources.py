# resources.py
from flask import request
from flask_restx import Namespace, Resource, fields, reqparse

from utils import get_db_connection, is_integer
from models import db
from models import Book as Bookdb
from models import BookType as Booktypedb
from models import BookList as Booklistdb


api = Namespace("books", description="Book related operations")

# Define individual book model
book_model = api.model(
    "Book",
    {
        "id": fields.Integer,
        "title": fields.String,
        "author": fields.String,
        'type': fields.String(attribute=lambda book: book.type.name if book.type else None),
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
                if is_integer(year) and len(year) <= 4:
                    query = query.filter(Bookdb.year == year)
                if not is_integer(year):
                    return {"error": "Year is not an integer"}, 400
                if len(year) > 4:
                    return {"error": "Year is too long"}, 400

            if "book_type" in request.args:
                book_type = request.args["book_type"]
                if book_type not in ["fiction", "non-fiction"]:
                    return {"error": 'Type must be "fiction" or "non-fiction"'}, 400
                query = query.filter(Bookdb.type.name == book_type)

            result = query.all()

        # Return the result
        if result is None:
            return {"error": "No books found"}, 404
        return result, 200

    @api.doc(description="Add a new book to the database.")
    @api.expect(book_model, validate=True)
    @api.response(201, "Book Created")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self):
        # Get the JSON data from the request
        data = request.json
        if data is None:
            return {"error": "No JSON data provided"}, 400

        # Validate that the required fields are present in the JSON data and that they are correct
        if "id" not in data:
            return {"error": 'Missing "id" field in JSON data'}, 400
        if not is_integer(data["id"]):
            return {"error": "Book id is not an integer"}, 400
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

        # Establish a connection to the database
        conn = get_db_connection()
        if conn is None:
            return {"error": "Could not connect to database"}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {"error": "Could not get cursor from database connection"}, 500

        # Check if the book with the provided ID exists
        try:
            cursor.execute("SELECT * FROM books WHERE id = ?", (data["id"],))
        except:
            return {
                "error": "Could not execute query to check whether provided ID exists in database"
            }, 500
        existing_book = cursor.fetchone()

        if existing_book:
            return {"error": "Book with provided ID already exists"}, 400
        else:
            try:
                cursor.execute(
                    "INSERT INTO books (id, title, author, type, year) VALUES (?, ?, ?, ?, ?)",
                    (
                        data["id"],
                        data["title"],
                        data["author"],
                        data["type"],
                        data["year"],
                    ),
                )
            except:
                return {
                    "error": "Could not execute query to insert new book into database"
                }, 500
            conn.commit()
            conn.close()
            return {"message": "New book inserted successfully"}, 201

    @api.doc(description="Update an existing book.")
    @api.expect(book_model, validate=True)
    @api.response(200, "Book Updated")
    @api.response(400, "Validation Error")
    @api.response(404, "Book not found")
    @api.response(500, "Internal Server Error")
    def put(self):
        # Get the JSON data from the request
        data = request.json
        if data is None:
            return {"error": "No JSON data provided"}, 400

        # Validate that the required fields are present in the JSON data and that they are correct
        if "id" not in data:
            return {"error": 'Missing "id" field in JSON data'}, 400
        if not is_integer(data["id"]):
            return {"error": "Book id is not an integer"}, 400
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

        # Establish a connection to the database
        conn = get_db_connection()
        if conn is None:
            return {"error": "Could not connect to database"}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {"error": "Could not get cursor from database connection"}, 500

        # Check if the book with the provided ID exists
        try:
            cursor.execute("SELECT * FROM books WHERE id = ?", (data["id"],))
        except:
            return {
                "error": "Could not execute query to check whether provided ID exists in database"
            }, 500
        existing_book = cursor.fetchone()

        if existing_book:
            try:
                cursor.execute(
                    "UPDATE books SET author = ?, title = ?, year = ? WHERE id = ?",
                    (
                        data.get("author", existing_book["author"]),
                        data.get("title", existing_book["title"]),
                        data.get("year", existing_book["year"]),
                        data["id"],
                    ),
                )
            except:
                return {
                    "error": "Could not execute query to update book in database"
                }, 500
            conn.commit()
            conn.close()
            return {
                "message": f"Book with id {data['id']} updated successfully",
                "previous_author": f"{existing_book['author']}",
                "previous_title": f"{existing_book['title']}",
                "previous_year": f"{existing_book['year']}",
                "new_author": f"{data['author']}",
                "new_title": f"{data['title']}",
                "new_year": f"{data['year']}",
            }, 200
        else:
            return {"error": "Book with provided ID does not exist"}, 404

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
    def delete(self):
        query_parameters = request.args
        if "id" in query_parameters:
            book_id = query_parameters["id"]
            if not is_integer(book_id):
                return {"error": "Book id is not an integer"}, 400
        else:
            return {"error": "No book id provided"}, 400

        # Establish a connection to the database
        conn = get_db_connection()
        if conn is None:
            return {"error": "Could not connect to database"}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {"error": "Could not get cursor from database connection"}, 500

        # Check if the book with the provided ID exists
        try:
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        except:
            return {
                "error": "Could not execute query to check whether provided ID exists in database"
            }, 500
        existing_book = cursor.fetchone()

        if existing_book:
            try:
                cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            except:
                return {
                    "error": "Could not execute query to delete book from database"
                }, 500
            conn.commit()
            conn.close()
            return {"message": f"Book with id {book_id} deleted successfully"}, 200
        else:
            return {"error": f"Book with id {book_id} does not exist"}, 404


class BookList(Resource):
    @api.doc(
        description="Retrieve a list of books based on query parameters. Can filter by id, author, title, year, and type."
    )
    @api.marshal_with(book_list_model)
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.response(404, "No Books Found")
    @api.response(500, "Internal Server Error")
    def get(self):
        # Get the query parameters from the request
        query_parameters = request.args
        query = "SELECT * FROM books WHERE "
        query_conditions = []
        args = []

        # Check query parameters
        if "id" in query_parameters:
            id = query_parameters["id"]
            if is_integer(id):
                query_conditions.append("id = ?")
                args.append(id)
            else:
                return {"error": "Book id is not an integer"}, 400
        if "author" in query_parameters:
            query_conditions.append("author = ?")
            args.append(query_parameters["author"])
        if "title" in query_parameters:
            query_conditions.append("title = ?")
            args.append(query_parameters["title"])
        if "year" in query_parameters:
            year = query_parameters["year"]
            if is_integer(year) and len(year) <= 4:
                query_conditions.append("year = ?")
                args.append(year)
            if not is_integer(year):
                return {"error": "Year is not an integer"}, 400
            if len(year) > 4:
                return {"error": "Year is too long"}, 400
        if "type" in query_parameters:
            book_type = query_parameters["type"]
            if book_type not in ["fiction", "non-fiction"]:
                return {"error": 'Type must be "fiction" or "non-fiction"'}, 400
            query_conditions.append("type = ?")
            args.append(book_type)

        # Construct the query
        if not query_conditions:
            return {"error": "No query parameters provided"}, 400
        if len(query_conditions) == 1:
            query += query_conditions[0]
        if len(query_conditions) > 1:
            for condition in query_conditions[:-1]:
                query += condition + " AND "
            query += query_conditions[-1]

        # Execute the query
        conn = get_db_connection()
        if conn is None:
            return {"error": "Could not connect to database"}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {"error": "Could not get cursor from database connection"}, 500
        try:
            books = cursor.execute(query, tuple(args)).fetchall()
        except:
            return {"error": "Could not execute query to fetch book from database"}, 500
        conn.close()

        # Return the result
        if books is None:
            return {"error": "No books found"}, 404
        return {"books": books}, 200

    @api.doc(description="Add multiple new books to the database.")
    @api.expect(book_model, validate=True)
    @api.response(201, "Books Created")
    @api.response(207, "Partial Success with Errors")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self):
        # Parse the JSON body of the request
        try:
            book_data = request.get_json()
        except:
            return {"error": "Invalid JSON format"}, 400

        # Validate and insert each book
        inserted_books = []
        errors = []
        conn = get_db_connection()
        if conn is None:
            return {"error": "Could not connect to database"}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {"error": "Could not get cursor from database connection"}, 500

        for book in book_data:
            if all(key in book for key in ["id", "title", "author", "type", "year"]):
                try:
                    cursor.execute(
                        "INSERT INTO books (id, title, author, book_type, year) VALUES (?, ?, ?, ?, ?)",
                        (
                            book["id"],
                            book["title"],
                            book["author"],
                            book["type"],
                            book["year"],
                        ),
                    )
                    inserted_books.append(book)
                except sqlite3.Error as e:
                    errors.append({"book": book, "error": str(e)})
            else:
                errors.append({"book": book, "error": "Missing required fields"})

        conn.commit()
        conn.close()

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
api.add_resource(BookList, "/booklists")
api.add_resource(BookList, "/booklists/<int:booklist_id>")
