from flask import Flask, request, redirect, abort
from flask_cors import CORS

# from users import UserModel
from flask_sqlalchemy import SQLAlchemy
import json


def load_user_crud(application, database):
    app = application
    db = database
    db.init_app(app)

    class UserModel(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.String(20), nullable=False, unique=True)
        password = db.Column(db.String(80), nullable=False)
        username = db.Column(db.String(50))
        email = db.Column(db.String(50))
        team_working = db.Column(db.Boolean, default=False)

        def __init__(self, login, password, username, email, team_working):
            self.login = login
            self.password = password
            self.username = username
            self.email = email
            self.team_working = team_working

        def __repr__(self):
            return '{' + f' "id" : "{self.id}",' \
                         f' "login" : "{self.login}",' \
                         f' "password" : "{self.password}",' \
                         f' "username" : "{self.username}",' \
                         f' "email" : "{self.email}",' \
                         f' "team_working" : {self.team_working}' + '}'

    @app.route('/data/create', methods=['POST'])  # Create user add to db
    def create():
        content_type = request.headers.get('Content-Type')
        if request.method == 'POST':
            if content_type == 'application/json':
                json_data = request.get_json()
                login = json_data['login']
                password = json_data['password']
                username = json_data['username']
                email = json_data['email']
                team_working = json_data['team_working']
                user = UserModel(login=login, password=password, username=username, email=email,
                                 team_working=team_working)
                db.session.add(user)
                db.session.commit()
                return redirect('/data')

    @app.route('/data')  # Retrieve list of users
    def RetrieveDataList():

        users = UserModel.query.all()
        usr_arr = []
        for el in users:
            x = str(el)
            print(x)
            y = json.dumps(x)
            usr_arr.append(y)

        return usr_arr

    @app.route('/data/<int:id>')  # Retrieve single user
    def RetrieveSingleUser(id):
        user = db.session.query(UserModel).filter_by(id=id).first()
        if user:
            return json.dumps(str(user))
        return f"User with id = {id} doesn't exist"

    @app.route('/data/<int:id>/update', methods=['GET', 'POST'])  # update user
    def update(id):
        user = db.session.query(UserModel).filter_by(id=id).first()
        content_type = request.headers.get('Content-Type')
        if request.method == 'POST':
            if content_type == 'application/json':
                if user:
                    db.session.delete(user)
                    db.session.commit()

                    json_data = request.get_json()
                    login = json_data['login']
                    password = json_data['password']
                    username = json_data['username']
                    email = json_data['email']
                    team_working = json_data['teamworking']
                    user = UserModel(login=login, password=password, username=username, email=email,
                                     team_working=team_working)

                    db.session.add(user)
                    db.session.commit()
                    return redirect(f'/data/{id}')
                return f"User with id = {id} doesn't exist"

    @app.route('/data/<int:id>/delete', methods=['GET', 'POST'])  # delete user
    def delete(id):
        user = db.session.query(UserModel).filter_by(id=id).first()
        if request.method == 'POST':
            if user:
                db.session.delete(user)
                db.session.commit()
                return redirect('/data')
            abort(404)


if __name__ == "__main__":
    app_2 = Flask(__name__)

    app_2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////db/planex.db'
    app_2.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app_2.config['SECRET_KEY'] = 'test-secret-key'

    db_2 = SQLAlchemy(app_2)
    db_2.init_app(app_2)

    # engine = create_engine('sqlite:///planex.db', convert_unicode=False, echo=False)
    # Base = declarative_base()
    # Base.metadata.reflect(engine)
    # db_session = scoped_session(sessionmaker(bind=engine))

    load_user_crud(app_2, db_2)

    app_2.run(host='localhost', port=5000)
