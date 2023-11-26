from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask("lorem")

# Database setup
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for the index page
@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

# Route for adding a new book
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author) VALUES (?, ?)',
                     (title, author))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")