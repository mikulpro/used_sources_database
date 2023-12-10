from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, fields
import sqlite3

DATABASE = 'books.sqlite'

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()

# Reserved for case of adding images to the database
# app.config['UPLOAD_FOLDER'] = 'images'

@staticmethod
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@staticmethod
def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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

book_resource_fields = {
    'id':       fields.Integer,
    'title':    fields.String,
    'author':   fields.String,
    'type':     fields.String,
    'year':     fields.Integer
}

class Book(Resource):
    def get(self):

        # Get the query parameters from the request
        query_parameters = request.args
        query = 'SELECT * FROM books WHERE '
        query_conditions = []
        args = []

        # Check query parameters
        if 'id' in query_parameters:
            id = query_parameters['id']
            if is_integer(id):
                query_conditions.append('id = ?')
                args.append(id)
            else:
                return {'error': 'Book id is not an integer'}, 400
        if 'author' in query_parameters:
            query_conditions.append('author = ?')
            args.append(query_parameters['author'])
        if 'title' in query_parameters:
            query_conditions.append('title = ?')
            args.append(query_parameters['title'])
        if 'year' in query_parameters:
            year = query_parameters['year']
            if is_integer(year) and len(year) <= 4:
                query_conditions.append('year = ?')
                args.append(year)
            if not is_integer(year):
                return {'error': 'Year is not an integer'}, 400
            if len(year) > 4:
                return {'error': 'Year is too long'}, 400
        if 'type' in query_parameters:
            type = query_parameters['type']
            if type not in ['fiction', 'non-fiction']:
                return {'error': 'Type must be "fiction" or "non-fiction"'}, 400
            query_conditions.append('type = ?')
            args.append(type)
        
        # Construct the query
        if not query_conditions:
            return {'error': 'No query parameters provided'}, 400
        if len(query_conditions) == 1:
            query += query_conditions[0]      
        if len(query_conditions) > 1:
            for condition in query_conditions[:-1]:
                query += condition + ' AND '
            query += query_conditions[-1]

        # Execute the query
        conn = get_db_connection()
        if conn is None:
            return {'error': 'Could not connect to database'}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {'error': 'Could not get cursor from database connection'}, 500
        try:
            books = cursor.execute(query, tuple(args)).fetchall()
        except:
            return {'error': 'Could not execute query'}, 500
        conn.close()

        # Return the results
        books_list = [dict(ix) for ix in books]
        if not books_list:
            return {'error': 'No books found'}, 404
        return jsonify(books_list), 200

    def put(self):

        # Get the JSON data from the request
        data = request.json

        # Validate that the required fields are present in the JSON data and that they are correct
        if 'id' not in data:
            return {'error': 'Missing "id" field in JSON data'}, 400
        if not is_integer(data['id']):
            return {'error': 'Book id is not an integer'}, 400
        if 'title' not in data:
            return {'error': 'Missing "title" field in JSON data'}, 400
        if 'author' not in data:
            return {'error': 'Missing "author" field in JSON data'}, 400
        if 'type' not in data:
            return {'error': 'Missing "type" field in JSON data'}, 400
        if data['type'] not in ['fiction', 'non-fiction']:
            return {'error': 'Type must be "fiction" or "non-fiction"'}, 400
        if 'year' not in data:
            return {'error': 'Missing "year" field in JSON data'}, 400
        if not is_integer(data['year']):
            return {'error': 'Year is not an integer'}, 400
        if len(data['year']) > 4:
            return {'error': 'Year is too long'}, 400

        # Establish a connection to the database
        conn = get_db_connection()
        if conn is None:
            return {'error': 'Could not connect to database'}, 500
        cursor = conn.cursor()
        if cursor is None:
            return {'error': 'Could not get cursor from database connection'}, 500

        # Check if the book with the provided ID exists
        try:
            cursor.execute('SELECT * FROM books WHERE id = ?', (data['id'],))
        except:
            return {'error': 'Could not execute query to check whether provided ID exists in database'}, 500
        existing_book = cursor.fetchone()

        if existing_book:
            try:
                cursor.execute(
                'UPDATE books SET author = ?, name = ?, year = ? WHERE id = ?',
                (data.get('author', existing_book['author']),
                data.get('title', existing_book['title']),
                data.get('year', existing_book['year']),
                data['id'])
                )
            except:
                return {'error': 'Could not execute query to update book in database'}, 500
            conn.commit()
            conn.close()
            return {'message': f'Book with id {data[id]} updated successfully',
                    'previous_author': f'{existing_book['author']}',
                    'previous_title': f'{existing_book['title']}',
                    'previous_year': f'{existing_book['year']}',
                    'new_author': f'{data['author']}',
                    'new_title': f'{data['title']}',
                    'new_year': f'{data['year']}'
                    }, 200
        else:
            try:
                cursor.execute(
                'INSERT INTO books (id, title, author, type, year) VALUES (?, ?, ?, ?, ?)',
                (data['id'],
                data['title'],
                data['author'],
                data['type'],
                data['year'])
                )
            except:
                return {'error': 'Could not execute query to insert new book into database'}, 500
            conn.commit()
            conn.close()    
            return {'message': 'New book inserted successfully'}, 201
        
    # not sure this is correct
    def head(self):
        return {'headers': {
            'header0': 'id',
            'header1': 'title',
            'header2': 'author',
            'header3': 'type',
            'header4': 'year'
        } }, 200

    def trace(self):
        return {'message': 'Disabled for security reasons.'}, 405

    def delete(self, book_id):
        #TODO:
        ...


class BookList(Resource):
    def get(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        books = cursor.execute('SELECT * FROM books').fetchall()
        conn.close()

        books_list = [dict(ix) for ix in books]
        if not books_list:
            return {'error': 'No books found'}, 404

        return jsonify(books_list)
    
    def post(self):
        ...

api.add_resource(Book, '/book')
api.add_resource(BookList, '/booklist')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")