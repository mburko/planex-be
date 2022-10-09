from flask import Flask, render_template, url_for, redirect
from flask import request

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

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
        teamworking = db.Column(db.Boolean)

    class RegisterForm(FlaskForm):
        login = StringField(
            validators=[
                InputRequired(),
                Length(min=4, max=20)
            ],
            render_kw={"placeholder": "login"})

        password = PasswordField(
            validators=[
                InputRequired(),
                Length(min=8, max=20)
            ],
            render_kw={"placeholder": "Password"})

        submit = SubmitField('Register')

        def validate_username(self, login):
            existing_user_username = User.query.filter_by(
                login=login.data).first()
            if existing_user_username:
                raise ValidationError(
                    'That username already exists. Please choose a different one.')

    class LoginForm(FlaskForm):
        login = StringField(validators=[
            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "login"})

        password = PasswordField(validators=[
            InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

        submit = SubmitField('Login')

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/123', methods=['GET', 'POST'])
    def test_request():
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.get_json()
            print(json)
            return json["test"]
        else:
            return 'Content-Type not supported!'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(login=form.login.data).first()
            if user:
                if bcryptor.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('welcome'))
        return render_template('login.html', form=form)

    @app.route('/welcome', methods=['GET', 'POST'])
    @login_required
    def welcome():
        return render_template('welcome.html')

    @app.route('/user_page', methods=['GET', 'POST'])
    @login_required
    def user_page():
        return render_template('user_page.html')

    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            hashed_password = bcryptor.generate_password_hash(form.password.data)
            # create new user ------------------------------------------------------------
            new_user = User(login=form.login.data, password=hashed_password)
            # ----------------------------------------------------------------------------
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

        return render_template('register.html', form=form)


if __name__ == "__main__":
    app_1 = Flask(__name__)

    FlaskJSON(app_1)

    app_1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
    app_1.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app_1.config['SECRET_KEY'] = 'test-secret-key'

    db_1 = SQLAlchemy(app_1)

    load_login_module(app_1, db_1)
    app_1.run(debug=True)
