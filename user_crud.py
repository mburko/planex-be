from flask import Flask, request, redirect, abort
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON
from Models.users import UserModel
import login_module


def load_user_crud(application, database):
    app = application
    db = database

    bcryptor = Bcrypt(app)

    FlaskJSON(app)

    @app.route('/register', methods=['POST'])
    def register():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.get_json()
            print(json_data)
            if \
                    "login" not in json_data \
                            or not json_data["login"] \
                            or "password" not in json_data \
                            or not json_data["password"] \
                            or "email" not in json_data \
                            or not json_data["email"] \
                            or "username" not in json_data \
                            or not json_data["username"]:
                return {
                    "Response": "Missing information"
                }
            if not login_module.validate_login(json_data["login"]):
                return {
                    "Response": "User already exists"
                }
            hashed_password = bcryptor.generate_password_hash(json_data['password'])
            new_user = UserModel(login=json_data["login"],
                                 password=hashed_password,
                                 email=json_data["email"],
                                 username=json_data["username"],
                                 team_working=False)
            db.session.add(new_user)
            db.session.commit()
            return {
                "Response": "Registration successful (maybe redirect to login page)"
            }
            # return redirect(url_for('login'))
        else:
            return 'Content-Type not supported!'

    @app.route('/data/<int:id>')  # Retrieve single user
    @login_module.login_required
    def RetrieveSingleUser(id):
        if login_module.current_user.id != id:
            return "Permission denied"
        user = db.session.query(UserModel).filter_by(id=id).first()
        if user:
            return str(user)
        return f"User with id = {id} doesn't exist"

    @app.route('/data/<int:id>/update', methods=['POST'])  # update user
    @login_module.login_required
    def update(id):
        user = db.session.query(UserModel).filter_by(id=id).first()
        content_type = request.headers.get('Content-Type')
        if request.method == 'POST':
            if content_type == 'application/json':
                if user:
                    json_data = request.get_json()
                    user.login = json_data['login']
                    user.password = json_data['password']
                    user.username = json_data['username']
                    user.email = json_data['email']
                    user.team_working = json_data['team_working']

                    db.session.commit()
                    return redirect(f'/data/{id}')
                return f"User with id = {id} doesn't exist"

    @app.route('/data/<int:id>/delete', methods=['POST'])  # delete user
    @login_module.login_required
    def delete(id):
        if login_module.current_user.id != id:
            return "Permission denied"
        user = db.session.query(UserModel).filter_by(id=id).first()
        if request.method == 'POST':
            if user:
                db.session.delete(user)
                db.session.commit()
                return redirect('/')
            abort(404)
