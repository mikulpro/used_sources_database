from flask_restx import Resource, fields, reqparse
from .api import api
from flask import request
from db.models import db
from db.models import Book as Bookdb
from db.models import BookType as BookTypedb
from utils.utils import is_integer

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
        query = db.session.query(Bookdb)

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

        if not books:
            return {"error": "No books found"}, 404

        # Use the api.marshal to serialize the list of books
        data = {
            "books": books,
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page
        }
        # New TODO, rewrite to book_model
        return api.marshal(data, book_list_model), 200

    @api.doc(description="Add a new book to the database.")
    @api.expect(book_model, validate=True)
    @api.marshal_with(book_model)
    @api.response(201, "Book Created")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self):
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
            booktype = db.session.query(BookTypedb).filter(BookTypedb.name == data["type"]).first()
            book = Bookdb(
                title=data["title"],
                author=data["author"],
                type_id=booktype.id,
                year=data["year"]
            )
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            api.logger.error(f'Failed to insert a book! {e}')
            return {"error": "Book wasn't inserted"}, 500
        return book, 201

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
