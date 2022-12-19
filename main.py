from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from CRUDs.login_module import load_login_module
from CRUDs.user_crud import load_user_crud
from CRUDs.category_crud import load_category_crud
from CRUDs.event_crud import load_event_crud
from CRUDs.task_crud import load_task_crud
from CRUDs.notifications_module import notifications_func
from flask_cors import CORS

from threading import Thread


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/planex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'test-secret-key'

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '8190f37066adef'
app.config['MAIL_PASSWORD'] = 'ca2237b79a9cc0'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)

CORS(app, supports_credentials=True)

if __name__ == "__main__":
    load_login_module(app, db)
    load_user_crud(app, db)
    load_category_crud(app, db)
    load_event_crud(app, db)
    load_task_crud(app, db)

    notifications_thread = Thread(target=notifications_func, args=(db, app))
    # for better performance do not start thread when notifications are not necessary :)

    # notifications_thread.start()

    app.run(debug=False)

    notifications_thread.join()
