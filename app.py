from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from resources import Book, BookList
import sqlite3

DATABASE = 'books.sqlite'

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('id', type=int, required=True, help="ID cannot be blank and must be an integer.")
parser.add_argument('title', required=True, help="Title cannot be blank.")
parser.add_argument('author', required=True, help="Author cannot be blank.")
parser.add_argument('type', required=True, help="Type must be either 'fiction' or 'non-fiction'.")
parser.add_argument('year', type=int, required=True, help="Year cannot be blank and must be an integer lesser than 10000.")

# Reserved for case of adding images to the database
# app.config['UPLOAD_FOLDER'] = 'images'

# Debugging purposes
#####################################################
                                                    #
class HelloWorld(Resource):                         #            
    def get(self):                                  #         
        return {'hello': 'world'}                   #          
api.add_resource(HelloWorld, '/')                   #
                                                    #
todos = {}                                          #
class TodoSimple(Resource):                         #
    def get(self, todo_id):                         #
        return {todo_id: todos[todo_id]}            #
                                                    #
    def put(self, todo_id):                         #    
        todos[todo_id] = request.form['data']       #
        return {todo_id: todos[todo_id]}            #
api.add_resource(TodoSimple, '/<string:todo_id>')   #
                                                    #
#####################################################


api.add_resource(Book, '/book')
api.add_resource(BookList, '/booklist')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)