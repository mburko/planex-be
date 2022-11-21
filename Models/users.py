from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class UserModel(db.Model, UserMixin):
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
        return str(CategorySchema().dump(self))

    def info(self):
        return CategorySchema().dump(self)


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        include_fk = True
        load_instance = True
