from flask import request
from flask_restx import Resource, fields
from models import db, BookCollection, Book
from .resources import api

# Define the book collection model
book_collection_model = api.model(
    "BookCollection",
    {
        "name": fields.String(required=True, description="Collection name"),  # Add this line
        "description": fields.String(required=True, description="Collection description"),
        "book_ids": fields.List(fields.Integer, description="List of book IDs in the collection"),
    },
)

class BookCollectionCreate(Resource):
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
            collection = BookCollection(name=data['name'], description=data['description'])
            if 'book_ids' in data:
                books = Book.query.filter(Book.id.in_(data['book_ids'])).all()
                if len(books) != len(data['book_ids']):
                    return {"error": "One or more book IDs are invalid"}, 400
                collection.books = books
            
            db.session.add(collection)
            db.session.commit()
            return {"message": "Collection created", "collection_id": collection.id}, 201
        except Exception as e:
            return {"error": str(e)}, 500
    
class BookCollectionOperations(Resource):
    @api.doc(description="Add books to an existing collection.")
    @api.response(200, "Books added successfully.")
    @api.response(400, "Validation Error")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    @api.expect(book_collection_model, validate=True)
    def put(self, collection_id):
        data = request.json
        collection = BookCollection.query.get(collection_id)
        if not collection:
            return {"error": f"Collection with id {collection_id} not found"}, 404
        
        try:
            collection.name = data.get('name', collection.name)
            collection.description = data.get('description', collection.description)
            
            if 'book_ids' in data:
                books = Book.query.filter(Book.id.in_(data['book_ids'])).all()
                if len(books) != len(data['book_ids']):
                    return {"error": "One or more book IDs are invalid"}, 400
                collection.books = books
            
            db.session.commit()
            return {"message": f"Collection {collection_id} updated successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc(description="Retrieve a book collection.")
    @api.response(200, "Success")
    @api.response(404, "Collection not found")
    @api.response(500, "Internal Server Error")
    def get(self, collection_id):
        collection = BookCollection.query.get(collection_id)
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
        collection = BookCollection.query.get(collection_id)
        if not collection:
            return {"error": f"Collection with id {collection_id} not found"}, 404
        try:
            db.session.delete(collection)
            db.session.commit()
            return {"message": f"Collection {collection_id} deleted successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
