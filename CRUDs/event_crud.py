from flask import request, redirect
from flask_bcrypt import Bcrypt

from flask_json import FlaskJSON

from CRUDs import login_module
from Models.event import EventModel
from Models.user_event import UserEventModel

from datetime import datetime

'''
to do:
1) System creates unique event with param repeat. Get events from date1 to date2 will
create using rrule lib list of actual dates and compare it to inputted dates ans show them.
List will be created using interval in rrule for next year(maybe more) Optionally after date
of original event was reached we can update starting date of original event so that we won't
generate dates that are already passed.

'''


def load_event_crud(application, database):
    app = application
    db = database

    bcryptor = Bcrypt(app)

    FlaskJSON(app)

    @app.route('/event', methods=['POST'])  # Create single event
    @login_module.login_required
    def CreateEvent():
        content_type = request.headers.get('Content-Type')

        if content_type == 'application/json':
            json_data = request.get_json()

            new_event = EventModel(
                start=datetime.strptime(json_data["start"], '%y/%m/%d %H:%M:%S'),  # example "20/01/01 12:12:12"
                finish=datetime.strptime(json_data["finish"], '%y/%m/%d %H:%M:%S'),
                title=json_data["title"],
                repeat=json_data["repeat"],
                description=json_data["description"]
            )

            db.session.add(new_event)
            db.session.commit()
            last_event = db.session.query(EventModel).order_by(EventModel.id.desc()).first()

            new_user_event = UserEventModel(
                user_id=login_module.current_user.id,
                event_id=last_event.id
            )

            db.session.add(new_user_event)
            db.session.commit()

            return "Event and UserEvent were successfully added", 200

        else:
            return 'Content-Type not supported!', 400
