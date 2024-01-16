# For marshalling
from flask_restful import fields

book_resource_fields = {
    'id':       fields.Integer,
    'title':    fields.String,
    'author':   fields.String,
    'type':     fields.String,
    'year':     fields.Integer
}
book_list_fields = {
    'books': fields.List(fields.Nested(book_resource_fields))
}