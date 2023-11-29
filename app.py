from flask import Flask, request
from flask_restful import Api, Resource, reqparse
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

class InformationSource(Resource):

    def get(self, id=None, name=None, author=None, year=None):
        conn = self.get_db_connection()
        query = "SELECT * FROM books"
        all_books = conn.execute(query, (id,)).fetchall()
        result = []
        for book in all_books:
            if book["id"] == id:
                result.append(book)
            elif book["name"] == name:
                result.append(book)
            elif book["author"] == author:
                result.append(book)
            elif book["year"] == year:
                result.append(book)
        if result == []:
            result = "No books found", 204        
        return result, 200
api.add_resource(InformationSource, '/bookid/<int:id>', '/bookname/<string:name>', '/bookauth/<string:author>', '/bookyear/<int:year>')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")