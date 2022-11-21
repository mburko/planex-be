from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
db = SQLAlchemy()


class TaskModel(db.Model):
    __tablename__ = "Task"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DATETIME)
    time_to_do = db.Column(db.DATETIME)
    repeat = db.Column(db.DATETIME)
    priority = db.Column(db.Text)
    event_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, id, title, description, deadline, time_to_do, repeat, priority, event_id, user_id):
        self.id = id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.time_to_do = time_to_do
        self.repeat = repeat
        self.priority = priority
        self.event_id = event_id
        self.user_id = user_id

    def __repr__(self):
        return '{' + f' "id" : "{self.id}",' \
                     f' "title" : "{self.title}",' \
                     f' "description" : "{self.description}",' \
                     f' "deadline" : "{self.deadline}",' \
                     f' "time_to_do" : "{self.time_to_do}",' \
                     f' "repeat" : "{self.repeat}",' \
                     f' "priority" : "{self.priority}",' \
                     f' "event_id" : "{self.event_id}",' \
                     f' "user_id" : "{self.user_id}' + '}'


class TaskSchema(Schema):
    title = fields.String()
    description = fields.String()
    deadline = fields.DateTime()
    time_to_do = fields.DateTime()
    repeat = fields.DateTime()
    priority = fields.String()
    event_id = fields.Integer()
    user_id = fields.Integer()