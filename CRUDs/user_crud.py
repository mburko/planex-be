from flask import request, redirect
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON
from Models.users import UserModel
from CRUDs import login_module


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
            return 'Content-Type not supported!', 400

    @app.route('/info')  # Retrieve single user
    @login_module.login_required
    def RetrieveSingleUser():
        user = db.session.query(UserModel).filter_by(id=login_module.current_user.id).first()
        if user:
            return str(user)
        else:
            return "User not found", 400

    @app.route('/info/update', methods=['POST'])  # update user
    @login_module.login_required
    def update():
        user = db.session.query(UserModel).filter_by(id=login_module.current_user.id).first()
        content_type = request.headers.get('Content-Type')

        if content_type == 'application/json':
            if user:
                json_data = request.get_json()
                user.login = json_data['login']
                user.password = json_data['password']
                user.username = json_data['username']
                user.email = json_data['email']
                user.team_working = json_data['team_working']

                db.session.commit()
                return redirect(f'/info')
            else:
                return "User not found", 400
        else:
            return "Wrong content type supplied, JSON expected", 400


@app.route('/delete', methods=['DELETE'])  # delete user
@login_module.login_required
def delete():
    user = db.session.query(UserModel).filter_by(id=login_module.current_user.id).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    else:
        return "User not found", 400
