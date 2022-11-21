from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class EventModel(db.Model, UserMixin):
    __tablename__ = "Event"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    finish = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(100))
    repeat = db.Column(db.String(50))  # types DAILY / WEEKLY / YEARLY
    description = db.Column(db.String(150))

    def __init__(self, start, finish, title, repeat, description):
        self.start = start
        self.finish = finish
        self.title = title
        self.repeat = repeat
        self.description = description

    def __repr__(self):
        return str(CategorySchema().dump(self))

    def info(self):
        return CategorySchema().dump(self)


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventModel
        include_fk = True
        load_instance = True
