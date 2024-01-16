# app.py
from flask import Flask
from flask_restx import Api, reqparse, Resource
from resources import api as books_api

app = Flask(__name__)
api = Api(app, doc='/swagger/')
api.add_namespace(books_api, path='/books')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)