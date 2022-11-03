from flask import request, redirect
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON
from Models.users import UserModel
from CRUDs import login_module


def load_event_crud(application, database):
    app = application
    db = database

    bcryptor = Bcrypt(app)

    FlaskJSON(app)