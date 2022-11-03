from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserModel(db.Model, UserMixin):
    __tablename__ = "Event"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String(20), nullable=False, unique=True)
    finish = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(50))
    repeat = db.Column(db.String(50))
    description = db.Column(db.Boolean, default=False)

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
