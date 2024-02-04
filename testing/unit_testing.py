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

        # Cleanup: remove the inserted book
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("DELETE FROM books WHERE id = ?", (1,))
        # conn.commit()
        # conn.close()

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

        # Cleanup: remove the mock book
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("DELETE FROM books WHERE id = ?", (4,))
        # conn.commit()
        # conn.close()

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
        response = self.app.put("/books/books/2", json=update_data)
        self.assertEqual(response.status_code, 200)

        # Cleanup: remove the book
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("DELETE FROM books WHERE id = ?", (2,))
        # conn.commit()
        # conn.close()

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

        with open("new_unit_testing_log.txt", "w") as f:
            f.writelines(f"post_response: {post_response}")

        # Delete the book
        response = self.app.delete(f"/books/books/{post_response.json['id']}")
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_book(self):
        response = self.app.delete("/books/books/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
    # launched by
    # docker exec used_sources_database-app-1 python -m testing.unit_testing
