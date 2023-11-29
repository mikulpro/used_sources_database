from flask import Flask
from flask_restful import Api, Resource
import sqlite3

DATABASE = 'books.sqlite'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'
api = Api(app)

@staticmethod
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")