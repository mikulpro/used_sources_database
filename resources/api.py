# api.py
from flask_restx import Namespace


api = Namespace("books", description="Book related operations")
