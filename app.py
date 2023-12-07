from flask import Flask, request, jsonify
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
    def get(self):
        query_string = request.args.get() # Get query - hopefully
        conn = get_db_connection()
        cursor = conn.cursor()
        books = cursor.execute('SELECT * FROM books WHERE id = ?', (query_string,))
        books.append(cursor.execute('SELECT * FROM books WHERE author = ?', (query_string,)))
        books.append(cursor.execute('SELECT * FROM books WHERE title = ?', (query_string,)))
        books.append(cursor.execute('SELECT * FROM books WHERE year = ?', (query_string,)))
        books.append(cursor.execute('SELECT * FROM books WHERE type = ?', (query_string,)))
        conn.close()

        # Convert each row to a dictionary
        books_list = [dict(ix) for ix in books]
        
        return jsonify(books_list)

    def put(self):
        data = request.json  # Assuming the data is provided in JSON format in the request body

        # Validate that the required fields are present in the JSON data
        if 'id' not in data:
            return {'error': 'Missing "id" field in JSON data'}, 400
        if 'title' not in data:
            return {'error': 'Missing "title" field in JSON data'}, 400
        if 'author' not in data:
            return {'error': 'Missing "author" field in JSON data'}, 400
        if 'type' not in data:
            return {'error': 'Missing "type" field in JSON data'}, 400
        if 'year' not in data:
            return {'error': 'Missing "year" field in JSON data'}, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the book with the provided ID exists
        cursor.execute('SELECT * FROM books WHERE id = ?', (data['id'],))
        existing_book = cursor.fetchone()

        if existing_book:
            cursor.execute(
            'UPDATE books SET author = ?, name = ?, year = ? WHERE id = ?',
            (data.get('author', existing_book['author']),
             data.get('name', existing_book['name']),
             data.get('year', existing_book['year']),
             data['id'])
            )
            conn.commit()
            conn.close()
            return {'message': 'Book updated successfully'}, 200
        else:
            cursor.execute(
            'INSERT INTO books (id, title, author, type, year) VALUES (?, ?, ?, ?, ?)',
            (data['id'],
             data['title'],
             data['author'],
             data['type'],
             data['year'])
            )
            conn.commit()
            conn.close()    
            return {'message': 'New book inserted successfully'}, 201
        
        def head(self):
            #TODO:
            ...

        def trace(self):
            #TODO:
            ...

api.add_resource(InformationSource, '/books')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")