from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from login_module import load_login_module

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'test-secret-key'

db = SQLAlchemy(app)

if __name__ == "__main__":
    load_login_module(app, db)
    app.run(debug=True)
