from flask_restx import Resource, fields, reqparse
from . import api

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

