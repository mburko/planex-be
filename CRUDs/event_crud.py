import copy

from dateutil.parser import parse
from flask import request, redirect

from flask_json import FlaskJSON

from CRUDs import login_module
from Models.event import EventModel
from Models.user_event import UserEventModel

from datetime import datetime
from dateutil.rrule import *

def load_event_crud(application, database):
    app = application
    db = database

    FlaskJSON(app)

    @app.route('/event', methods=['POST'])  # Create single event
    @login_module.login_required
    def CreateEvent():
        content_type = request.headers.get('Content-Type')

        if content_type != 'application/json':
            return 'Content-Type not supported!', 400

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

    @app.route('/event', methods=['PUT'])  # update event
    @login_module.login_required
    def UpdateEvent():
        if request.method != 'PUT':
            return "Wrong request", 400

        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return "Wrong content type supplied, JSON expected", 400

        json_data = request.get_json()
        user_event = db.session.query(UserEventModel).filter_by(id=json_data["user_event_id"]).first()
        if not user_event:
            return "User event not found", 400

        event = db.session.query(EventModel).filter_by(id=user_event.event_id).first()
        if not event:
            return "Event not found", 400

        event.start = datetime.strptime(json_data["start"], '%y/%m/%d %H:%M:%S')
        event.finish = datetime.strptime(json_data["finish"], '%y/%m/%d %H:%M:%S')
        event.title = json_data["title"]
        event.repeat = json_data["repeat"]
        event.description = json_data["description"]
        # in this update event was connected to user_event, so if necessary
        # properties of user_event can also be modified
        db.session.commit()
        return "Event was successfully updated", 200

    @app.route('/event', methods=['DELETE'])  # delete user
    @login_module.login_required
    def DeleteEvent():
        if request.method != 'DELETE':
            return "Wrong request", 400

        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return "Wrong content type supplied, JSON expected", 400

        json_data = request.get_json()
        user_event = db.session.query(UserEventModel).filter_by(id=json_data["user_event_id"]).first()
        if not user_event:
            return "User event not found", 400

        event = db.session.query(EventModel).filter_by(id=user_event.event_id).first()
        if not event:
            return "Event not found", 400

        db.session.delete(user_event)
        db.session.delete(event)
        db.session.commit()

        return "Event and User_event were successfully deleted", 204

    @app.route('/event', methods=['GET'])  # Get list of all events for user
    @login_module.login_required
    def GetAllEvents():
        if request.method != 'GET':
            return "Wrong request", 400

        user_event_lst = db.session.query(UserEventModel).filter_by(user_id=login_module.current_user.id).all()
        if not user_event_lst:
            return "User events not found", 400

        event_lst = []
        for el in user_event_lst:
            event_lst.append(db.session.query(EventModel).filter_by(id=el.event_id).first())
        if not event_lst:
            return "Events not found", 400

        return str(event_lst)

    @app.route('/event/period', methods=['GET'])  # Get list of all events for user from particular date to another
    @login_module.login_required
    def GetAllEventsInTimePeriod():
        if request.method != 'GET':
            return "Wrong request", 400

        content_type = request.headers.get('Content-Type')
        json_data = request.get_json()
        if content_type != 'application/json':
            return "Wrong content type supplied, JSON expected", 400

        user_event_lst = db.session.query(UserEventModel).filter_by(user_id=login_module.current_user.id).all()
        if not user_event_lst:
            return "User events not found", 400

        event_lst = []
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            if temp.repeat:  # check if event is periodicall
                lst_cases = ["YEARLY", "MONTHLY", "WEEKLY"]
                if temp.repeat not in lst_cases:
                    return "Wrong repeat value", 400
                all_dates = list(
                    rrule(lst_cases.index(temp.repeat), dtstart=temp.start,
                          until=parse(json_data["finish_period"])))
                for el1 in all_dates:
                    if parse(json_data["start_period"]) < el1 < parse(json_data["finish_period"]):
                        temp1 = copy.deepcopy(temp)
                        temp1.start = el1
                        temp1.finish = el1 + (temp1.finish - temp1.start)
                        event_lst.append(temp1)
            else:  # if it's not simply check time period and add it
                if parse(json_data["start_period"]) < temp.start < parse(json_data["finish_period"]):
                    event_lst.append(temp)
        if not event_lst:
            return "Events in this time period not found", 400

        return str(event_lst), 200
