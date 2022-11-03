from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserEventModel(db.Model, UserMixin):
    __tablename__ = "User_event"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id

    def __repr__(self):
        return '{' + f' "id" : "{self.id}",' \
                     f' "user_id" : "{self.user_id}",' \
                     f' "event_id" : "{self.event_id}",' + '}'
