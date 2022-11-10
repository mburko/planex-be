from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class TaskModel(db.Model):
    __tablename__ = "Task"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DATETIME)
    time_to_do = db.Column(db.DATETIME)
    repeat = db.Column(db.DATETIME)
    event_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, id, title, description, deadline, time_to_do, repeat, event_id, user_id):
        self.id = id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.time_to_do = time_to_do
        self.repeat = repeat
        self.event_id = event_id
        self.user_id = user_id

    def __repr__(self):
        return '{' + f' "id" : "{self.id}",' \
                     f' "title" : "{self.title}",' \
                     f' "description" : "{self.description}",' \
                     f' "deadline" : "{self.deadline}",' \
                     f' "time_to_do" : "{self.time_to_do}",' \
                     f' "repeat" : "{self.repeat}",' \
                     f' "event_id" : "{self.event_id}",' \
                     f' "user_id" : "{self.user_id}' + '}'


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TaskModel
        include_relationships = True
        include_fk = True
        load_instance = True
