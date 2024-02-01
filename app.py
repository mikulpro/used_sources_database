# app.py
from models import db
from resources import api as books_api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db.init_app(app)
api = Api(app, doc="/swagger/")
api.add_namespace(books_api, path="/books")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
