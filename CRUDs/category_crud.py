from flask import request, redirect, url_for


from flask_json import FlaskJSON

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
            # print(json_data)
            errors = CategorySchema().validate(data=json_data, session=db.session)
            if errors or json_data["user_id"] != login_module.current_user.id:
                print(errors)
                return {
                    "Response": "Missing or incorrect information"
                }
            existing_user_category = db.session.query(CategoryModel).filter_by(
                    name=json_data['name'],
                    user_id=login_module.current_user.id).first()
            if existing_user_category:
                return redirect(url_for(f'/category/"{existing_user_category.id}"', method='GET'))
            else:
                new_category = CategorySchema().load(data=json_data, session=db.session)
                db.session.add(new_category)
                db.session.commit()
                return {
                    "Response": "Added successfully"
                }
        else:
            return 'Content-Type not supported!'

    # retrieve all categories for current user
    @app.route('/all_categories', methods=['GET'])  # Retrieve all categories
    # for test purposes disabled auth
    @login_module.login_required
    def retrieve_multiple_categories():
        categories = db.session.query(CategoryModel).filter_by(
            user_id=login_module.current_user.id
        ).all()
        print(categories)
        if categories:
            result = {}
            result['categories']=[]
            for cat in categories:
                result['categories'].append(CategoryModel.info(cat))
            print(result)
            return result  # str(categories)
        else:
            return "Category not found", 400

    @app.route('/category/<category_id>', methods=['GET', 'PUT', 'DELETE'])  # RUD category
    @login_module.login_required
    def rud_category(category_id):
        request_cat_id = category_id
        category = db.session.query(CategoryModel).filter_by(
            user_id=login_module.current_user.id,
            id=request_cat_id).first()
        content_type = request.headers.get('Content-Type')

        if category:
            if request.method == 'GET':
                return CategoryModel.info(category), 200
            elif request.method == 'DELETE':
                db.session.delete(category)
                db.session.commit()
                return 'ok', 200
            elif request.method == 'PUT':
                if content_type == 'application/json':
                    json_data = request.get_json()

                    errors = CategorySchema().validate(data=json_data,session= db)
                    if errors:
                        return {
                            "Response": "Missing or incorrect information"
                        }

                    db.session.query(CategoryModel).filter_by(
                        user_id=login_module.current_user.id,
                        id=request_cat_id).update(json_data)

                    db.session.commit()
                    return "Ok", 200
                else:
                    return "Wrong content type supplied, JSON expected", 400
            else:
                return "Bad request", 400
        else:
            return "Category not found", 400
