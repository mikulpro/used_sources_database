from flask import Flask, request
from flask_restful import Api, Resource
import sqlite3

DATABASE = 'books.sqlite'

app = Flask(__name__)
api = Api(app)
# app.config['UPLOAD_FOLDER'] = 'images'

@staticmethod
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
api.add_resource(HelloWorld, '/')

todos = {}
class TodoSimple(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}
api.add_resource(TodoSimple, '/<string:todo_id>')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")