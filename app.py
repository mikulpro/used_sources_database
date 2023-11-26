from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask("lorem")

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        # process form data to add a new book
        # redirect to index page after adding
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    # fetch book with the given id and process form data to edit
    # redirect to index page after editing
    return render_template('edit.html', book=book)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    # delete the book with the given id
    # redirect to index page after deleting
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")