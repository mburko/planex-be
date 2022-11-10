from flask import Flask, request, redirect, abort, url_for
from flask_json import FlaskJSON
from Models.tasks import TaskModel, TaskSchema
import login_module


def load_task_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

    @app.route('/task', methods=['POST'])
    @login_module.login_required
    def create_task():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.get_json()
            errors = TaskSchema().validate(data=json_data, session=db.session)
            if errors or json_data["user_id"] != login_module.current_user.id:
                print(errors)
                return {
                    "Response": "Missing or incorrect information"
                }
            existing_user_task = db.session.query(TaskModel).filter_by(
                    name=json_data['name'],
                    user_id=login_module.current_user.id).first()
            if existing_user_task:
                return redirect(url_for(f'/task/"{existing_user_task.id}"', method='GET'))
            else:
                new_task = TaskSchema().load(data=json_data, session=db.session)
                db.session.add(new_task)
                db.session.commit()
                return {
                    "Response": "Added successfully"
                }
        else:
            return 'Content-Type not supported!'

    @app.route('/all_tasks', methods=['GET'])
    @login_module.login_required
    def retrieve_multiple_categories():
        tasks = db.session.query(TaskModel).filter_by(
            user_id=login_module.current_user.id
        ).all()
        print(tasks)
        if tasks:
            result = {}
            result['tasks']=[]
            for t in tasks:
                result['tasks'].append(TaskModel.info(t))
            print(result)
            return result
        else:
            return "Task not found", 400

    @app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
    @login_module.login_required
    def rud_category(task_id):
        request_t_id = task_id
        task = db.session.query(TaskModel).filter_by(
            user_id=login_module.current_user.id,
            id=request_t_id).first()
        content_type = request.headers.get('Content-Type')

        if task:
            if request.method == 'GET':
                return TaskModel.info(task), 200
            elif request.method == 'DELETE':
                db.session.delete(task)
                db.session.commit()
                return 'ok', 200
            elif request.method == 'PUT':
                if content_type == 'application/json':
                    json_data = request.get_json()

                    errors = TaskSchema().validate(data=json_data, session=db)
                    if errors:
                        return {
                            "Response": "Missing or incorrect information"
                        }

                    db.session.query(TaskModel).filter_by(
                        user_id=login_module.current_user.id,
                        id=request_t_id).update(json_data)

                    db.session.commit()
                    return "Ok", 200
                else:
                    return "Wrong content type supplied, JSON expected", 400
            else:
                return "Bad request", 400
        else:
            return "Task not found", 400
