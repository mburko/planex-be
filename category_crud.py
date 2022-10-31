from flask import request, redirect, url_for


from flask_json import FlaskJSON
from Models.category import CategoryModel
import login_module


def load_category_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

    @app.route('/category', methods=['POST'])  # Add category
    @login_module.login_required
    def create_category():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.get_json()
            # print(json_data)
            if \
                    "name" not in json_data \
                            or not json_data["name"] \
                            or "description" not in json_data \
                            or not json_data["description"] \
                            or "user_id" not in json_data \
                            or not json_data["user_id"]:
                return {
                    "Response": "Missing information"
                }
            existing_user_category = db.session.query.filter_by(
                    name=json_data['name'],
                    user_id=login_module.current_user.id).first()
            if existing_user_category:
                return redirect(url_for(f'/category/"{existing_user_category.id}"', method='GET'))
            else:
                new_category = CategoryModel(
                    name=json_data["name"],
                    description=json_data["description"],
                    user_id=json_data["user_id"])
                db.session.add(new_category)
                db.session.commit()
            return {
                "Response": "Added successfully"
            }
        else:
            return 'Content-Type not supported!'

    # retrieve all categories for current user
    @app.route('/all_categories', methods='GET')  # Retrieve all categories
    # for test purposes disabled auth
    # @login_module.login_required
    def retrieve_multiple_categories():
        category_id = request.args.get('id', type=int)
        categories = db.session.query(CategoryModel).filter_by(
            user_id=login_module.current_user.id,
            id=category_id).all()
        if categories:
            return str(categories)
        else:
            return "Category not found", 400

    @app.route('/category/<id:int>', methods=['GET', 'PUT', 'DELETE'])  # RUD category
    @login_module.login_required
    def rud_category():
        request_cat_id = request.args.get('id', type=int)
        category = db.session.query(CategoryModel).filter_by(
            user_id=login_module.current_user.id,
            id=request_cat_id).first()
        content_type = request.headers.get('Content-Type')

        if category:
            if request.method == 'GET':
                return str(category), 200
            elif request.method == 'DELETE':
                db.session.delete(category)
                return 200
            elif request.method == 'PUT':
                if content_type == 'application/json':
                    json_data = request.get_json()
                    category.name = json_data['name']
                    category.description = json_data['description']
                    db.session.commit()
                    return "Ok", 200
                else:
                    return "Wrong content type supplied, JSON expected", 400
            else:
                return "Bad request", 400
        else:
            return "Category not found", 400
