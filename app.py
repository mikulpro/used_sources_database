# app.py
from db.models import db
from resources.resources import api as books_api
from db.models import BookType

from flask import Flask
from flask_restx import Api, reqparse

import logging
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite://books.db")
db.init_app(app)
api = Api(app, doc='/swagger/')
api.add_namespace(books_api, path='/books')

# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)

parser = reqparse.RequestParser()
parser.add_argument('id', type=int, required=True, help="ID cannot be blank and must be an integer.")
parser.add_argument('title', required=True, help="Title cannot be blank.")
parser.add_argument('author', required=True, help="Author cannot be blank.")
parser.add_argument('type', required=True, help="Type must be either 'fiction' or 'non-fiction'.")
parser.add_argument('year', type=int, required=True, help="Year cannot be blank and must be an integer lesser than 10000.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if len(db.session.query(BookType).all()) == 0:
            db.session.add(BookType(name="fiction"))
            db.session.add(BookType(name="non-fiction"))
            db.session.commit()
    app.run(debug=os.getenv("FLASK_DEBUG"), host="0.0.0.0", port=5000)
