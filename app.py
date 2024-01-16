# app.py
from flask import Flask
from flask_restx import Api, reqparse, Resource
from resources import api as books_api

app = Flask(__name__)
api = Api(app, doc='/swagger/')
api.add_namespace(books_api, path='/books')

parser = reqparse.RequestParser()
parser.add_argument('id', type=int, required=True, help="ID cannot be blank and must be an integer.")
parser.add_argument('title', required=True, help="Title cannot be blank.")
parser.add_argument('author', required=True, help="Author cannot be blank.")
parser.add_argument('type', required=True, help="Type must be either 'fiction' or 'non-fiction'.")
parser.add_argument('year', type=int, required=True, help="Year cannot be blank and must be an integer lesser than 10000.")




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)