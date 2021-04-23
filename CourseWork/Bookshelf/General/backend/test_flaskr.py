import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookshelfTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgres://{}@{}/{}".format('chancemaston', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_book = {
            'title': 'The Name of the Wind',
            'author': 'Patrick Rothfuss',
            'rating': 5
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_books_pass(self):
        res = self.client().get('/books/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_get_books_fail_404(self):
        # Page out of range test
        res = self.client().get('/books/?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_book_rating_pass(self):
        res = self.client().patch('/books/5', json={'rating': 1})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(book.format()['rating'], 1)

    def test_update_book_rating_fail_400(self):
        # Missing input rating test
        res = self.client().patch('/books/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_create_new_book_pass(self):
        res = self.client().post('/books/', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['books']))

    def test_create_new_book_fail_405(self):
        # Creation method not allowed test
        res = self.client().post('/books/45', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_book_pass(self):
        book_to_delete = Book.query.filter_by(title=self.new_book['title']).first()
        book_delete_id = book_to_delete.id
        res = self.client().delete('/books/'+str(book_delete_id))
        data = json.loads(res.data)

        book = Book.query.filter(Book.id == book_delete_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(int(data['deleted']), int(book_delete_id))
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
        self.assertEqual(book, None)

    def test_delete_bookfail_422(self):
        # Delete book that does not exist test
        res = self.client().delete('/books/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()