from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    team_working = db.Column(db.Boolean, default=False)

    def __init__(self, login, password, username, email, team_working):
        self.login = login
        self.password = password
        self.username = username
        self.email = email
        self.team_working = team_working

    def __repr__(self):
        return '{' + f' "id" : "{self.id}",' \
                     f' "login" : "{self.login}",' \
                     f' "password" : "{self.password}",' \
                     f' "username" : "{self.username}",' \
                     f' "email" : "{self.email}",' \
                     f' "team_working" : {self.team_working}' + '}'
