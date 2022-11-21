from flask import Flask, url_for, redirect
from flask import request

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from Models.users import UserModel

from flask_json import FlaskJSON


def validate_login(login_field):
    existing_user_login = UserModel.query.filter_by(
        login=login_field).first()
    if existing_user_login:
        return False
    return True


def load_login_module(application, database):
    app = application

    bcryptor = Bcrypt(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    FlaskJSON(app)

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    @app.route('/')
    def home():
        return {
                   "Response": "Home page"
               }, 200

    @app.route('/login', methods=['POST'])
    def login():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.get_json()
            print(json_data)
            print(json_data["password"])
            if \
                    not json_data["login"] \
                            or not json_data["password"]:
                return {
                           "Response": "Missing information"
                       }, 400
            else:
                user = UserModel.query.filter_by(login=json_data["login"]).first()
                if user is not None:
                    if bcryptor.check_password_hash(user.password, json_data["password"]):
                        login_user(user)
                        return "Ok", 200
                        # return redirect(url_for('user_page'))
                    else:
                        return {
                                   "Response": "Wrong pass"
                               }, 400
                else:
                    return {
                               "Response": "No user"
                           }, 400
        else:
            return {"Response": "Content-Type not supported!"}, 400

    @app.route('/user_page', methods=['GET'])
    @login_required
    def user_page():

        t = current_user.username
        return {
            "Response": "Welcome to User page, " + t
        }, 200

    @app.route('/logout', methods=['GET'])
    @login_required
    def logout():
        logout_user()
        return {
            "Response": "Log out"
        }, 200


# **********************************************************************************


if __name__ == "__main__":
    app_1 = Flask(__name__)

    from flask_cors import CORS

    CORS(app_1)

    FlaskJSON(app_1)

    app_1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
    app_1.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app_1.config['SECRET_KEY'] = 'test-secret-key'

    db_1 = SQLAlchemy(app_1)

    load_login_module(app_1, db_1)
    app_1.run(debug=True)
