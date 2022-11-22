from flask_json import FlaskJSON
from CRUDs import login_module
from Models.tasks import TaskModel, TaskSchema
from flask import request, jsonify
from resp_error import errorss
from marshmallow import ValidationError
from flask import request, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import and_, update


# send func to worker thread
def migrate_tasks(db):
    tasks = db.session.query(TaskModel).filter_by().all()
    for t in tasks:
        t.deadline += timedelta(days=1)
    db.session.commit()


def load_task_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

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
            if json_data['priority'] not in ['High', 'Middle', 'Low']:
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
                if json_data['priority'] not in ['High', 'Middle', 'Low']:
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

    @app.route('/task/date', methods=['GET'])  # Get list of all tasks for user for particular date
    @login_module.login_required
    def GetAllTasksForDate():
        content_type = request.headers.get('Content-Type')
        json_data = request.get_json()

        if content_type != 'application/json':
            return {"Response": "Wrong content type supplied, JSON expected"}, 400

        if 'target_date' not in json_data or not json_data['target_date']:
            return {"Response": "Missing or incorrect information"}, 400
        json_data["target_date"] = str((json_data["target_date"])[2:])
        target_date = datetime.strptime(json_data["target_date"], '%y-%m-%dT%H:%M:%S'),  # request example { "target_date":"2022-11-23T00:00:00"}
        target_date = target_date[0]

        task_lst = db.session.query(TaskModel).filter_by(user_id=login_module.current_user.id) \
            .filter(and_(TaskModel.deadline >= target_date,
                         TaskModel.deadline < (target_date + timedelta(days=1)))
                    ).all()

        if not task_lst:
            return {"Response": "Tasks not found"}, 400
        tasks = []

        for el in task_lst:
            tasks.append(el.info())
        # print(tasks)
        return jsonify(tasks), 200
