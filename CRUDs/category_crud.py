from flask import request, redirect, url_for

from flask_json import FlaskJSON

from Models.user_event import UserEventModel
from Models.category import CategoryModel, CategorySchema
from CRUDs import login_module


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
            errors = CategorySchema().validate(data=json_data, session=db.session)
            if errors:
                print(errors)
                return {
                           "Response": "Missing or incorrect information"
                       }, 400
            existing_user_category = db.session.query(CategoryModel).filter_by(
                name=json_data['name'],
                description=json_data["description"]).first()
            if existing_user_category:
                return redirect(url_for(f'/category/"{existing_user_category.id}"', method='GET'))
            else:
                new_category = CategorySchema().load(data=json_data, session=db.session)
                db.session.add(new_category)
                db.session.commit()
                return {
                           "Response": "Added successfully"
                       }, 200
        else:
            return {
                       "Response": "Content-Type not supported!"
                   }, 400

    # retrieve all categories for current user
    @app.route('/all_categories', methods=['GET'])  # Retrieve all categories
    @login_module.login_required
    def retrieve_multiple_categories():
        user_events = db.session.query(UserEventModel).filter_by(
            user_id=login_module.current_user.id
        ).all()
        print(user_events)
        if user_events:
            result = {'categories': []}
            for el in user_events:
                if el.category_id:
                    category = db.session.query(CategoryModel).filter_by(
                        id=el.category_id
                    ).first()
                    result['categories'].append(CategoryModel.info(category))
            return result, 200

        else:
            return {
                       "Response": "Categories not found"
                   }, 400

    @app.route('/category/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])  # RUD category
    @login_module.login_required
    def rud_category(category_id):
        request_cat_id = category_id
        category = db.session.query(CategoryModel).filter_by(
            id=request_cat_id).first()
        content_type = request.headers.get('Content-Type')
        if category:
            if request.method == 'GET':
                return CategoryModel.info(category), 200
            elif request.method == 'DELETE':
                db.session.delete(category)
                db.session.commit()
                return {"Response": "Category deleted successfully"}, 200
            elif request.method == 'PUT':
                if content_type == 'application/json':
                    json_data = request.get_json()
                    errors = CategorySchema().validate(data=json_data, session=db)
                    if errors:
                        return {
                                   "Response": "Missing or incorrect information"
                               }, 400

                    db.session.query(CategoryModel).filter_by(
                        id=request_cat_id).update(json_data)

                    db.session.commit()
                    return {"Response": "Category info updated successfully"}, 200
                else:
                    return {"Response": "Wrong content type supplied, JSON expected"}, 400
            else:
                return {"Response": "Bad request"}, 400
        else:
            return {"Response": "Category not found"}, 400
