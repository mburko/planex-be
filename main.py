from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from CRUDs.login_module import load_login_module
from CRUDs.user_crud import load_user_crud
from CRUDs.category_crud import load_category_crud
from CRUDs.event_crud import load_event_crud
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'test-secret-key'

db = SQLAlchemy(app)

CORS(app)

if __name__ == "__main__":
    load_login_module(app, db)
    load_user_crud(app, db)
    load_category_crud(app, db)
    load_event_crud(app, db)
    app.run(debug=True)
