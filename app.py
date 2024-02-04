# app.py
from models import db
from resources.resources import api as books_api
from models import Book, BookCollection

from flask import Flask
from flask_restx import Api, reqparse, Resource

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db.init_app(app)
api = Api(app, doc='/swagger/')
api.add_namespace(books_api, path='/books')

parser = reqparse.RequestParser()
parser.add_argument('id', type=int, required=True, help="ID cannot be blank and must be an integer.")
parser.add_argument('title', required=True, help="Title cannot be blank.")
parser.add_argument('author', required=True, help="Author cannot be blank.")
parser.add_argument('type', required=True, help="Type must be either 'fiction' or 'non-fiction'.")
parser.add_argument('year', type=int, required=True, help="Year cannot be blank and must be an integer lesser than 10000.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
