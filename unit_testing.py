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

if __name__ == '__main__':
    unittest.main()
    # launched by
    # docker exec used_sources_database-app-1 python unit_testing.py
