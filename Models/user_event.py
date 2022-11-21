from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class UserEventModel(db.Model, UserMixin):
    __tablename__ = "User_event"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer)

    def __init__(self, user_id, event_id, category_id):
        self.user_id = user_id
        self.event_id = event_id
        self.category_id = category_id

    # def __repr__(self):
    #     return '{' + f' "id" : "{self.id}",' \
    #                  f' "user_id" : "{self.user_id}",' \
    #                  f' "event_id" : "{self.event_id}",' \
    #                  f' "category_id" : "{self.category_id}",' + '}'

    def __repr__(self):
        return str(CategorySchema().dump(self))

    def info(self):
        return CategorySchema().dump(self)


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserEventModel
        include_fk = True
        load_instance = True
