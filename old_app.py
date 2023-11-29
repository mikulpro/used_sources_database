from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3

DATABASE = 'books.sqlite'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_books_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    # This SQL statement creates a table with an image, title, author, type, and year column
    # The data types may need to be adjusted to match your needs
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image TEXT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        type TEXT NOT NULL,
        year INTEGER NOT NULL
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()

    # debug?
    if not books:
        books = []

    return render_template('index.html', books=books)

@app.route('/add', methods=('GET', 'POST'))
def add():
    create_books_table()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book_type = request.form['type']
        year = request.form['year']
        
        # Initialize image_filename as None or as an empty string
        image_filename = ''  # or image_filename = ''
        
        # For the image, you need to save it first
        image = request.files['image']
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
            image_url = url_for('static', filename=f'images/{image_filename}')

        # Now, insert the new book into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO books (image, title, author, type, year) VALUES (?, ?, ?, ?, ?)',
                     (image_filename, title, author, book_type, year))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    # fetch book with the given id and process form data to edit
    # redirect to index page after editing
    return render_template('edit.html', book=book)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")