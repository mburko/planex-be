from flask import Flask, request, redirect, abort

from flask_sqlalchemy import SQLAlchemy
from flask_json import FlaskJSON
from Models.users import UserModel
import json


def load_user_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

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
        usr_arr = ""
        for el in users:
            x = str(el)
            usr_arr += x + '\n'

        return usr_arr

    @app.route('/data/<int:id>')  # Retrieve single user
    def RetrieveSingleUser(id):
        user = db.session.query(UserModel).filter_by(id=id).first()
        if user:
            return str(user)
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
                    team_working = json_data['team_working']
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

    app_2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
    app_2.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app_2.config['SECRET_KEY'] = 'test-secret-key'

    FlaskJSON(app_2)

    db_2 = SQLAlchemy(app_2)

    load_user_crud(app_2, db_2)
    app_2.run(debug=True)

