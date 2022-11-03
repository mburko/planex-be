from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class EventModel(db.Model, UserMixin):
    __tablename__ = "Event"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    finish = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(100))
    repeat = db.Column(db.String(50)) #types DAILY / WEEKLY / YEARLY
    # add validation later!!!
    description = db.Column(db.String(150))

    def __init__(self, start, finish, title, repeat, description):
        self.start = start
        self.finish = finish
        self.title = title
        self.repeat = repeat
        self.description = description

    def __repr__(self):
        return '{' + f' "id" : "{self.id}",' \
                     f' "start" : "{self.start}",' \
                     f' "finish" : "{self.finish}",' \
                     f' "title" : "{self.title}",' \
                     f' "repeat" : "{self.repeat}",' \
                     f' "description" : {self.description}' + '}'
