import sys
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/books/', methods=['GET'])
    def get_books():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = Book.query.all()
        formatted_books = [book.format() for book in books]
        if len(formatted_books) == 0:
          abort(404)

        return jsonify({
            'success': True,
            'books': formatted_books[start:end],
            'total_books': len(formatted_books)
        })

    @app.route('/books/<book_id>', methods=['PATCH'])
    def update_rating(book_id):
        # Obtain book item to be updated.
        book = Book.query.filter_by(id=book_id).one_or_none()
        rating = request.get_json().get('rating', '')

        if book is None:
            abort(404)

        if rating != '':
            try:
                book.rating = rating
                book.update()
            except Exception as e:
                db.session.rollback()
                error_info = sys.exc_info()
                print(error_info)
            finally:
                db.session.close()
        else:
            abort(400, 'Rating Value unacceptable: ' + rating)

        return jsonify({
            'success': True
        })

    @app.route('/books/<book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.filter_by(id=book_id).one_or_none()
            total_books = len(Book.query.all())
            if book is None:
                abort(404)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            formatted_books = [book.format() for book in selection]
            books_left = formatted_books[0:BOOKS_PER_SHELF]

            return jsonify({
                'success': True,
                'deleted': book_id,
                'books': books_left,
                'total_books': total_books
            })
        except:
          abort(422)


    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()

        title = body.get('title', None)
        author = body.get('author', None)
        rating = body.get('rating', None)

        try:
            book = Book(title=title, author=author, rating=rating)
            book.insert()

            selection = Book.query.order_by(Book.id).all()
            formatted_books = [book.format() for book in selection]
            books_left = formatted_books[0:BOOKS_PER_SHELF]

            return jsonify({
              'success': True,
              'created': book.id,
              'books': books_left,
              'total_books': len(Book.query.all())
            })

        except:
          abort(422)

    return app
