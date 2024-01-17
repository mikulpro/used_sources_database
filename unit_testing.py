import unittest
from utils import is_integer, get_db_connection
from app import app


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
        response = self.app.get('/books/book?id=99999')
        self.assertEqual(response.status_code, 404)

    def test_post_book(self):
        # Provide a sample book data
        book_data = {'id': 1, 'title': 'Test Book', 'author': 'Author', 'type': 'fiction', 'year': 2021}
        response = self.app.post('/books/book', json=book_data)
        self.assertEqual(response.status_code, 201)

        # Cleanup: remove the inserted book
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = ?', (1,))
        conn.commit()
        conn.close()
    def test_get_book_by_author(self):
        # Insert a mock book
        mock_book_data = {'id': 4, 'title': 'Mock Book', 'author': 'Mock Author', 'type': 'fiction', 'year': 2022}
        self.app.post('/books/book', json=mock_book_data)

        # Test retrieval by author
        response = self.app.get('/books/book?author=Mock Author')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Mock Author', response.data.decode())

        # Cleanup: remove the mock book
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = ?', (4,))
        conn.commit()
        conn.close()

    def test_get_book_invalid_year(self):
        response = self.app.get('/books/book?year=abcd')
        self.assertEqual(response.status_code, 400)

    def test_update_book(self):
        # First, insert a book to update
        book_data = {'id': 2, 'title': 'Old Title', 'author': 'Author', 'type': 'fiction', 'year': 2020}
        self.app.post('/books/book', json=book_data)

        # Update the book
        update_data = {'id': 2, 'title': 'New Title', 'author': 'Author', 'type': 'fiction', 'year': 2021}
        response = self.app.put('/books/book', json=update_data)
        self.assertEqual(response.status_code, 200)

        # Cleanup: remove the book
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = ?', (2,))
        conn.commit()
        conn.close()

    def test_delete_book(self):
        # First, insert a book to delete
        book_data = {'id': 3, 'title': 'Test Book', 'author': 'Author', 'type': 'fiction', 'year': 2021}
        self.app.post('/books/book', json=book_data)

        # Delete the book
        response = self.app.delete('/books/book?id=3')
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_book(self):
        response = self.app.delete('/books/book?id=999')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
    # launched by
    # docker exec used_sources_database-app-1 python unit_testing.py
