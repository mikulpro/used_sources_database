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
        id = request.args.get('id')  # Get id from query parameter
        author = request.args.get('author')  # Get author from query parameter
        name = request.args.get('name')
        year = request.args.get('year')

        conn = get_db_connection()
        cursor = conn.cursor()

        if id:
            # Fetch books by the specified author
            cursor.execute('SELECT * FROM books WHERE id = ?', (id,))
        elif author:
            # Fetch books by the specified author
            cursor.execute('SELECT * FROM books WHERE author = ?', (author,))
        elif name:
            # Fetch books by the specified author
            cursor.execute('SELECT * FROM books WHERE name = ?', (name,))
        elif year:
            # Fetch books by the specified author
            cursor.execute('SELECT * FROM books WHERE year = ?', (year,))

        books = cursor.fetchall()
        conn.close()

        # Convert each row to a dictionary
        books_list = [dict(ix) for ix in books]
        
        return jsonify(books_list)

    def put(self):
        data = request.json  # Assuming the data is provided in JSON format in the request body

        # Validate that the required fields are present in the JSON data
        if 'id' not in data:
            return {'error': 'Missing "id" field in JSON data'}, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the book with the provided ID exists
        cursor.execute('SELECT * FROM books WHERE id = ?', (data['id'],))
        existing_book = cursor.fetchone()

        if not existing_book:
            conn.close()
            return {'error': 'Book not found with the provided ID'}, 404

        # Update the book information with the new data
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

api.add_resource(InformationSource, '/books')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")