from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class CategoryModel(db.Model, UserMixin):
    __tablename__ = "Category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.TEXT, nullable=True)

    def __repr__(self):
        return str(CategorySchema().dump(self))

    def info(self):
        return CategorySchema().dump(self)

class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CategoryModel
        include_fk = True
        load_instance = True
