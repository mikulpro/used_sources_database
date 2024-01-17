# import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# old
# connection = sqlite3.connect('books.db')

# with open('schema.sql') as f:
#     connection.executescript(f.read())

# connection.commit()
# connection.close()
