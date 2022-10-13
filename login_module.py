from flask import Flask, url_for, redirect
from flask import request

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON


def load_login_module(application, database):
    app = application
    db = database

    bcryptor = Bcrypt(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    FlaskJSON(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.String(20), nullable=False, unique=True)
        password = db.Column(db.String(80), nullable=False)
        username = db.Column(db.String(50))
        email = db.Column(db.String(50))
        teamworking = db.Column(db.Boolean, default=False)

    def validate_login(login_field):
        existing_user_login = User.query.filter_by(
            login=login_field).first()
        if existing_user_login:
            return False
        return True

    @app.route('/')
    def home():
        return {
            "Response": "Home page"
        }

    @app.route('/123', methods=['GET', 'POST'])
    def test_request():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json = request.get_json()
            print(json)
            return {"current": "test_request",
                    "json": {json}
                    }
        else:
            return 'Content-Type not supported!'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.get_json()
            print(json_data)
            if not json_data["login"] or not json_data["password"]:
                return {
                    "Response": "Missing information"
                }
            else:
                user = User.query.filter_by(login=json_data["login"]).first()
                print(user.password, )
                if user:
                    if bcryptor.check_password_hash(user.password, json_data["password"]):
                        login_user(user)
                        return redirect(url_for('user_page'))
                    else:
                        return {
                            "Response": "Wrong pass"
                        }
                else:
                    return {
                        "Response": "No user"
                    }
        else:
            return 'Content-Type not supported!'

    @app.route('/user_page', methods=['GET', 'POST'])
    @login_required
    def user_page():
        return {
            "Response": "Welcome to User page"
        }

    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return {
            "Response": "Log out"
        }

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # ******************************************************************************************************
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
            if not validate_login(json_data["login"]):
                return {
                    "Response": "User already exists"
                }
            hashed_password = bcryptor.generate_password_hash(json_data['password'])
            new_user = User(login=json_data["login"],
                            password=hashed_password,
                            email=json_data["email"],
                            username=json_data["username"])
            db.session.add(new_user)
            db.session.commit()
            return {
                "Response": "Registration successful (maybe redirect to login page)"
            }
            # ???????
            # return redirect(url_for('login'))
        else:
            return 'Content-Type not supported!'


# ******************************************************************************************************

if __name__ == "__main__":
    app_1 = Flask(__name__)

    FlaskJSON(app_1)

    app_1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
    app_1.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app_1.config['SECRET_KEY'] = 'test-secret-key'

    db_1 = SQLAlchemy(app_1)

    load_login_module(app_1, db_1)
    app_1.run(debug=True)
