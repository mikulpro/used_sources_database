from flask_restx import Resource, fields, reqparse
from . import api
from models import db, BookCollection

# Define the book collection model
book_collection_model = api.model(
    "BookCollection",
    {
        "id": fields.Integer(description="The collection ID"),
        "description": fields.String(required=True, description="Collection description"),
        "book_ids": fields.List(fields.Integer, description="List of book IDs in the collection"),
    },
)

class BookCollection(Resource):
    @api.doc(description="Create a new book collection.")
    @api.expect(book_collection_model, validate=True)
    @api.response(201, "Collection created successfully.")
    @api.response(400, "Validation Error")
    @api.response(500, "Internal Server Error")
    def post(self):
        data = request.json
        # mock success response
        return {"message": "Collection created", "collection": data}, 201

    @api.doc(description="Add books to an existing collection.")
    @api.expect(book_collection_model, validate=True)
    @api.response(200, "Books added successfully.")
    @api.response(400, "Validation Error")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def put(self, collection_id):
        data = request.json
        # mock success response
        return {"message": f"Books added to collection {collection_id}", "updated_collection": data}, 200

    @api.doc(description="Retrieve a book collection.")
    @api.response(200, "Success")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def get(self, collection_id):
        #  mock collection
        mock_collection = {
            "id": collection_id,
            "description": "A mock book collection",
            "book_ids": [1, 2, 3]  # Example book IDs
        }
        return mock_collection, 200

    @api.doc(description="Delete a book collection.")
    @api.response(200, "Collection deleted successfully.")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def delete(self, collection_id):
        
        # mock success response
        return {"message": f"Collection {collection_id} deleted successfully"}, 200