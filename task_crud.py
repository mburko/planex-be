from flask_json import FlaskJSON
import login_module
from Models.tasks import TaskModel, TaskSchema
from flask import request, jsonify
from resp_error import errorss
from marshmallow import ValidationError
from flask import request, redirect, url_for


def load_task_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

    def create_entry(model_class, *, commit=True, **kwargs):
        entry = model_class(**kwargs)
        db.session.add(entry)
        db.session.commit()
        return entry

    def update_entry(entry, *, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(entry, key, value)
        db.session.commit()
        return entry

    @app.route('/task', methods=['POST'])
    @login_module.login_required
    def create_task():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.json
            if not json_data:
                return errorss.bad_request
            json_data["user_id"] = login_module.current_user.id
            errors = TaskSchema().validate(data=json_data, session=db.session)
            if errors:
                print(errors)
                return {
                    "Response": "Missing or incorrect information"
                }
            task = TaskSchema().load(data=json_data, session=db.session)
            db.session.add(task)
            db.session.commit()
            return jsonify(TaskSchema().dump(task)), 200
        else:
            return errorss.not_supported

    @app.route('/all_tasks', methods=['GET'])
    @login_module.login_required
    def retrieve_multiple_tasks():
        tasks_list = db.session.query(TaskModel).filter_by(user_id=login_module.current_user.id).all()
        if not tasks_list:
            return errorss.not_found
        else:
            return TaskSchema().dump(tasks_list, many=True), 200

    @app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
    @login_module.login_required
    def task_id_api(task_id):
        task = db.session.query(TaskModel).filter_by(id=task_id, user_id=login_module.current_user.id).first()
        if not task:
            return errorss.not_found
        if request.method == 'GET':
            return TaskSchema().dump(task), 200
        if request.method == 'PUT':
            content_type = request.headers.get('Content-Type')
            if content_type == 'application/json':
                json_data = request.json
                if not json_data:
                    return errorss.bad_request
                errors = TaskSchema().validate(data=json_data, session=db)
                if errors:
                    return {
                        "Response": "Missing or incorrect information"
                    }
                updated_task = db.session.query(TaskModel).filter_by(
                    user_id=login_module.current_user.id).update(json_data)
                return TaskSchema().dump(updated_task), 200
            else:
                return errorss.bad_request
        if request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()
            return {"message": "Deleted successfully"}, 200