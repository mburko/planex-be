from flask_json import FlaskJSON
import login_module
from Models.tasks import TaskModel, TaskSchema
from flask import request, jsonify
from resp_error import errorss
from marshmallow import ValidationError


def load_task_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

    def create_entry(model_class, *, commit=True, **kwargs):
        entry = model_class(**kwargs)
        db.session.add(entry)
        if commit:
            db.session.commit()
        return entry

    def update_entry(entry, *, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(entry, key, value)
        if commit:
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
            try:
                task_data = TaskSchema().load(json_data)
            except ValidationError as err:
                return err.messages, 422
            task = db.session.query(TaskModel).filter_by(id=task_data["id"]).first()
            if task:
                return errorss.exists
            task = create_entry(TaskModel, **task_data)
            return jsonify(TaskSchema().dump(task)), 200
        else:
            return errorss.not_supported

    @app.route('/all_tasks', methods=['GET'])
    @login_module.login_required
    def retrieve_multiple_categories():
        tasks_list = db.session.query(TaskModel).all()
        return TaskSchema().dump(tasks_list, many=True), 200

    @app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
    @login_module.login_required
    def task_id_api(task_id):
        task = db.session.query(TaskModel).filter_by(id=task_id).first()
        if not task:
            return errorss.not_found
        if request.method == 'GET':
            return TaskSchema().dump(task), 200
        if request.method == 'PUT':
            json_data = request.json
            if not json_data:
                return errorss.bad_request
            try:
                data = TaskSchema().load(json_data, partial=True)
            except ValidationError as err:
                return err.messages, 422
            for key, value in data.items():
                if key == "id":
                    us = db.session.query(TaskModel).filter_by(id=data["id"]).first()
                    if us:
                        return errorss.exists
            updated_task = update_entry(task, **data)
            return TaskSchema().dump(updated_task), 200
        if request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()
            return {"message": "Deleted successfully"}, 200