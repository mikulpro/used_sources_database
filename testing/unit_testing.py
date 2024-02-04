import unittest

from app import app
from utils.utils import get_db_connection, is_integer


class TestUtils(unittest.TestCase):
    def test_is_integer_positive(self):
        self.assertTrue(is_integer("123"))

    def test_is_integer_negative(self):
        self.assertFalse(is_integer("-123"))

    def test_is_integer_invalid(self):
        self.assertFalse(is_integer("abc"))


class BookApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_book_not_found(self):
        response = self.app.get("/books/books/99999")
        self.assertEqual(response.status_code, 404)

    def test_post_book(self):
        # Provide a sample book data
        book_data = {
            "title": "Test Book",
            "author": "Author",
            "type": "fiction",
            "year": 2021
        }
        response = self.app.post("/books/books", json=book_data)
        self.assertEqual(response.status_code, 201)
        self.app.delete(f"/books/books/{response.json['id']}")

    def test_get_book_by_author(self):
        # Insert a mock book
        mock_book_data = {
            "title": "Mock Book",
            "author": "Mock Author",
            "type": "fiction",
            "year": 2022
        }
        post_response = self.app.post("/books/books", json=mock_book_data)

        # Test retrieval by author
        response = self.app.get("/books/books?author=Mock Author")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mock Author", response.data.decode())
        self.app.delete(f"/books/books/{post_response.json['id']}")

    def test_get_book_invalid_year(self):
        response = self.app.get("/books/books?year=abcd")
        self.assertEqual(response.status_code, 400)

    def test_update_book(self):
        # First, insert a book to update
        book_data = {
            "title": "Old Title",
            "author": "Author",
            "type": "fiction",
            "year": 2020
        }
        post_response = self.app.post("/books/books", json=book_data)

        # Update the book
        update_data = {
            "title": "New Title",
            "author": "Author",
            "type": "fiction",
            "year": 2021
        }
        response = self.app.put(f"/books/books/{post_response.json['id']}", json=update_data)
        self.assertEqual(response.status_code, 200)
        self.app.delete(f"/books/books/{post_response.json['id']}")

    def test_delete_book(self):
        # First, insert a book to delete
        book_data = {
            "title": "Test Book",
            "author": "Author",
            "type": "fiction",
            "year": 2021
        }
        post_response = self.app.post("/books/books", json=book_data)

        # Delete the book
        response = self.app.delete(f"/books/books/{post_response.json['id']}")
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_book(self):
        response = self.app.delete("/books/books/999")
        self.assertEqual(response.status_code, 404)

class BookCollectionApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_collection(self):
        collection_data = {
            "name": "Sample Collection",
            "description": "A sample book collection",
            "book_ids": []  # Assuming book IDs are optional for creation
        }
        response = self.app.post("/books/collections", json=collection_data)
        self.assertEqual(response.status_code, 201)
        # Clean up by deleting the created collection
        self.app.delete(f"/books/collections/{response.json['collection_id']}")

    def test_get_all_collections(self):
        response = self.app.get("/books/collections")
        self.assertEqual(response.status_code, 200)
        self.assertIn("collections", response.json)

    def test_get_collection_with_filters(self):
        collection_data = {
            "name": "Sample Collection",
            "description": "A sample book collection",
            "book_ids": []  # Assuming book IDs are optional for creation
        }
        response = self.app.post("/books/collections", json=collection_data)
        self.assertEqual(response.status_code, 201)
        

        response1 = self.app.get("/books/collections?name=Sample Collection")
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(any("Sample Collection" in collection["name"] for collection in response1.json["collections"]))

        # Clean up by deleting the created collection
        self.app.delete(f"/books/collections/{response.json['collection_id']}")

    def test_update_collection(self):
        # First, create a collection to update
        collection_data = {
            "name": "Old Collection Name",
            "description": "A collection before update",
            "book_ids": []
        }
        post_response = self.app.post("/books/collections", json=collection_data)
        collection_id = post_response.json['collection_id']

        # Update the collection
        update_data = {
            "name": "New Collection Name",
            "description": "A collection after update",
            "book_ids": []
        }
        response = self.app.put(f"/books/collections/{collection_id}", json=update_data)
        self.assertEqual(response.status_code, 200)

        # Clean up by deleting the updated collection
        self.app.delete(f"/books/collections/{collection_id}")

    def test_delete_collection(self):
        # First, create a collection to delete
        collection_data = {
            "name": "Collection to Delete",
            "description": "This collection will be deleted",
            "book_ids": []
        }
        post_response = self.app.post("/books/collections", json=collection_data)

        # Delete the collection
        collection_id = post_response.json['collection_id']
        response = self.app.delete(f"/books/collections/{collection_id}")
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_collection(self):
        response = self.app.delete("/books/collections/99999")
        self.assertEqual(response.status_code, 404)



if __name__ == "__main__":
    unittest.main()
    # launched by
    # docker exec used_sources_database-app-1 python -m testing.unit_testing
