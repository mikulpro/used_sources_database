from flask_restx import Resource, fields, reqparse
from . import api
from flask import request
from models import db, Book as Bookdb, BookType as BookTypedb

# defining book_model again cuz i am retarded so this is TODO
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
parser.add_argument('page', type=int, default=1, help='Page number')
parser.add_argument('per_page', type=int, default=10, help='Books per page')
parser.add_argument("title", required=False, help="Search by title")
parser.add_argument("author", required=False, help="search by Author.")
parser.add_argument("type", required=False, help="Search by type, only 'fiction' or 'non-fiction' exists.")
parser.add_argument(
    "year",
    type=int,
    required=False,
    help="Year cannot be blank and must be an integer lesser than 10000.",
)

class BookList(Resource):
    @api.doc(
        description="Retrieve a list of books based on query parameters. Can filter by id, author, title, year, and type."
    )
    @api.expect(parser)
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.response(404, "No Books Found")
    @api.response(500, "Internal Server Error")
    def get(self):
        # Add other filters as needed
        args = parser.parse_args()

        # Base query
        query = Bookdb.query

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

        # Pagination
        page = args['page']
        per_page = args['per_page']
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        books = pagination.items

        # Serialize books
        # TODO there has to be better way to do this right?
        serialized_books = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'type': book.type.name if book.type else None,  # Assuming 'type' is a related object
            'year': book.year
        } for book in books]

        # Return results
        if not serialized_books:
            return {"error": "No books found"}, 404

        return {
            "books": serialized_books,
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page
        }, 200

    @api.doc(description="Add multiple new books to the database.")
    @api.expect(book_list_model, validate=True)
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

