from flask import request
from flask_restx import Resource, fields, reqparse
from models import db
from models import BookCollection as BookCollectiondb
from models import Book as Bookdb
from .resources import api
from sqlalchemy import select


# Define the book collection model
book_collection_model = api.model(
    "BookCollection",
    {
        "name": fields.String(required=True, description="Collection name"), 
        "description": fields.String(required=True, description="Collection description"),
        "book_ids": fields.List(fields.Integer, description="List of book IDs in the collection"),
    },
)

collection_filter_parser = reqparse.RequestParser()
collection_filter_parser.add_argument('name', type=str, help='Filter by collection name')
collection_filter_parser.add_argument('description', type=str, help='Filter by collection description')
collection_filter_parser.add_argument('page', type=int, default=1, help='Page number')
collection_filter_parser.add_argument('per_page', type=int, choices=[10, 20, 50], default=10, help='Collections per page')


class BookCollectionNonID(Resource):
    @api.doc(description="Create a new book collection.")
    @api.response(201, "Collection created successfully.")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    @api.expect(book_collection_model, validate=True)
    def post(self):
        data = request.json
        if 'name' not in data or 'description' not in data:
            return {"error": "Name and description are required"}, 400
        
        try:
            collection = BookCollectiondb(name=data['name'], description=data['description'])
            if 'book_ids' in data:
                books = Bookdb.query.filter(Bookdb.id.in_(data['book_ids'])).all()
                if len(books) != len(data['book_ids']):
                    return {"error": "One or more book IDs are invalid"}, 400
                collection.books = books
            
            db.session.add(collection)
            db.session.commit()
            return {"message": "Collection created", "collection_id": collection.id}, 201
        except Exception as e:
            api.logger.error(f'Failed to insert collection! {e}')
            return {"error": "Failed to insert collection"}, 500

    @api.doc(description="Search collections based on filters.")
    @api.response(200, "Success")
    @api.response(500, "Internal Server Error")
    @api.expect(collection_filter_parser)
    def get(self):
        args = collection_filter_parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        base_query = BookCollectiondb.query
        
        if args['name']:
            base_query = base_query.filter(BookCollectiondb.name.like(f"%{args['name']}%"))
        if args['description']:
            base_query = base_query.filter(BookCollectiondb.description.like(f"%{args['description']}%"))
        
        # Apply pagination
        pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
        collections = pagination.items
        
        # Prepare data for response
        data = {
            "collections": [{
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "book_ids": [book.id for book in collection.books]
            } for collection in collections],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page
        }

        return data, 200


class BookCollectionID(Resource):
    @api.doc(description="Add books to an existing collection.")
    @api.response(200, "Books added successfully.")
    @api.response(400, "Validation Error")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    @api.expect(book_collection_model, validate=True)
    def put(self, collection_id):
        data = request.json
        collection = db.session.query(BookCollectiondb).filter(BookCollectiondb.id == collection_id).first()
        if not collection:
            return {"error": f"Collection with id {collection_id} not found"}, 404
        
        try:
            collection.name = data.get('name', collection.name)
            collection.description = data.get('description', collection.description)
            
            if 'book_ids' in data:
                books = Bookdb.query.filter(Bookdb.id.in_(data['book_ids'])).all()
                if len(books) != len(data['book_ids']):
                    return {"error": "One or more book IDs are invalid"}, 400
                collection.books = books
            
            db.session.commit()
            return {"message": f"Collection {collection_id} updated successfully"}, 200
        except Exception as e:
            api.logger.error(f'Failed to modify collection with id {collection_id}! {e}')
            return {"error": "Failed to modify collection"}, 500

    @api.doc(description="Retrieve a book collection.")
    @api.response(200, "Success")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def get(self, collection_id):
        collection = db.session.query(BookCollectiondb).filter(BookCollectiondb.id == collection_id).first()
        if not collection:
            return {"error": "Collection not found"}, 404
        
        book_ids = [book.id for book in collection.books]  

        collection_data = {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "book_ids": book_ids
        }

        return collection_data, 200

    @api.doc(description="Delete a book collection.")
    @api.response(200, "Collection deleted successfully.")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def delete(self, collection_id):
        collection = db.session.query(BookCollectiondb).filter(BookCollectiondb.id == collection_id).first()
        if not collection:
            return {"error": f"Collection with id {collection_id} not found"}, 404
        try:
            db.session.delete(collection)
            db.session.commit()
            return {"message": f"Collection {collection_id} deleted successfully"}, 200
        except Exception as e:
            api.logger.error(f'Failed to delete collection with id {collection_id}! {e}')
            return {"error": "Failed to delete collection"}, 500
