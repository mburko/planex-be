import copy

from dateutil.parser import parse
from flask import request, redirect, jsonify

from flask_json import FlaskJSON

from CRUDs import login_module
from Models.category import CategoryModel
from Models.event import EventModel, EventSchema
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
            return {"Response": "Content-Type not supported!"}, 400
        json_data = request.get_json()
        # parsing category id
        category_id_loc = None
        if json_data["category_id"] and int(json_data["category_id"]):
            category = db.session.query(CategoryModel).filter_by(id=int(json_data["category_id"])).first()
            if not category:
                return {"Response: Such category id does not exist"}, 400
            else:
                category_id_loc = category.id
        else:
            return {"Response": "Missing or incorrect information"}, 400
        del json_data["category_id"]

        errors = EventSchema().validate(data=json_data, session=db)
        if errors:
            print("errors", errors)
            return {
                       "Response": "Missing or incorrect information"
                   }, 400
        print(json_data)

        json_data["start"] = str((json_data["start"])[2:])
        print(json_data["start"])
        json_data["finish"] = str((json_data["finish"])[2:])
        print(json_data["finish"])

        if datetime.strptime(json_data["start"], '%y-%m-%dT%H:%M:%S') > \
                datetime.strptime(json_data["finish"], '%y-%m-%dT%H:%M:%S'):
            return {"Response": "Wrong start/finish values"}, 400

        new_event = EventModel(
            start=datetime.strptime(json_data["start"], '%y-%m-%dT%H:%M:%S'),  # example "20/01/01 12:12:12"
            finish=datetime.strptime(json_data["finish"], '%y-%m-%dT%H:%M:%S'),
            title=json_data["title"],
            repeat=json_data["repeat"],
            description=json_data["description"]
        )

        db.session.add(new_event)
        db.session.commit()
        last_event = db.session.query(EventModel).order_by(EventModel.id.desc()).first()

        new_user_event = UserEventModel(
            user_id=login_module.current_user.id,
            event_id=last_event.id,
            category_id=category_id_loc
        )

        db.session.add(new_user_event)
        db.session.commit()

        return {"Response": "Event and UserEvent were successfully added"}, 200

    @app.route('/event', methods=['PUT'])  # update ONLY event (without user_event and category)
    # -> more info in Update below
    @login_module.login_required
    def UpdateEvent():
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return {"Response": "Wrong content type supplied, JSON expected"}, 400
        json_data = request.get_json()

        # category fix
        # parsing category id
        category_id_loc = None
        if json_data["category_id"] and int(json_data["category_id"]):
            category = db.session.query(CategoryModel).filter_by(id=int(json_data["category_id"])).first()
            if not category:
                return {"Response: Such category id does not exist"}, 400
            else:
                category_id_loc = category.id
        else:
            return {"Response": "Missing or incorrect information"}, 400
        del json_data["category_id"]

        errors = EventSchema().validate(data=json_data, session=db)
        if errors:
            print(errors)
            return {
                       "Response": "Missing or incorrect information"
                   }, 400

        # previously commented
        # user_event = db.session.query(UserEventModel).filter_by(id=json_data["user_event_id"]).first()
        user_event = db.session.query(UserEventModel).filter_by(event_id=json_data["id"]).first()
        # potentially change all user_events for all users

        if not user_event:
            return {"Response": "User event not found"},

        event = db.session.query(EventModel).filter_by(id=json_data["id"]).first()
        if not event:
            return {"Response": "Event not found"}, 400

        json_data["start"] = str((json_data["start"])[2:])
        print(json_data["start"])
        json_data["finish"] = str((json_data["finish"])[2:])
        print(json_data["finish"])

        event.start = datetime.strptime(json_data["start"], '%y-%m-%dT%H:%M:%S')
        event.finish = datetime.strptime(json_data["finish"], '%y-%m-%dT%H:%M:%S')
        event.title = json_data["title"]
        event.repeat = json_data["repeat"]
        event.description = json_data["description"]

        # here # previously commented
        # if category_id_loc:
        user_event.category_id = category_id_loc

        # in this update event was connected to user_event, so if necessary
        # properties of user_event can also be modified

        # UPDATE
        # without choosing specific user_event or specific category_id we want to replace it is impossible
        # to change category id, since we need that info to find linker in user_event responsible for our category_id
        db.session.commit()
        return {"Response": "Event was successfully updated"}, 200

    @app.route('/event', methods=['DELETE'])  # delete event and all user_events connected to it
    @login_module.login_required
    def DeleteEvent():
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return {"Response": "Wrong content type supplied, JSON expected"}, 400

        json_data = request.get_json()
        user_event = db.session.query(UserEventModel).filter_by(event_id=json_data["event_id"]).all()
        # look for all user events and delete them sequentially
        if not user_event:
            return {"Response": "User event not found"}, 400

        event = db.session.query(EventModel).filter_by(id=json_data["event_id"]).first()
        if not event:
            return {"Response": "Event not found"}, 400

        for el in user_event:
            db.session.delete(el)

        db.session.delete(event)
        db.session.commit()
        return {"Response": "Event and User_event were successfully deleted"}, 200

    @app.route('/event', methods=['GET'])  # Get list of all events for user
    @login_module.login_required
    def GetAllEvents():
        user_event_lst = db.session.query(UserEventModel).filter_by(user_id=login_module.current_user.id).all()
        if not user_event_lst:
            return {"Response": "User events not found"}, 400
        event_lst = []
        for el in user_event_lst:
            ev = (EventModel.info(db.session.query(EventModel).filter_by(id=el.event_id).first()))
            cat_id = db.session.query(UserEventModel).filter_by(event_id=el.event_id).first()
            ev["category_id"] = cat_id.category_id

            event_lst.append(ev)

        if not event_lst:
            return {"Response": "Events not found"}, 400

        return jsonify(event_lst), 200

    @app.route('/event/period', methods=['POST'])  # Get list of all events for user from particular date to another
    @login_module.login_required
    def GetAllEventsInTimePeriod():
        content_type = request.headers.get('Content-Type')
        json_data = request.get_json()

        if content_type != 'application/json':
            return {"Response": "Wrong content type supplied, JSON expected"}, 400

        user_event_lst = db.session.query(UserEventModel).filter_by(user_id=login_module.current_user.id).all()
        if not user_event_lst:
            return {"Response": "User events not found"}, 400

        event_lst = []
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            if temp.repeat:  # check if event is periodical
                lst_cases = ["YEARLY", "MONTHLY", "WEEKLY", "DAILY"]
                if temp.repeat not in lst_cases:
                    return {"Response": "Wrong repeat value"}, 400
                all_dates = list(
                    rrule(lst_cases.index(temp.repeat), dtstart=temp.start,
                          until=parse(json_data["finish_period"])))
                for el1 in all_dates:
                    if parse(json_data["start_period"]) < el1 < parse(json_data["finish_period"]):
                        temp1 = copy.deepcopy(temp)
                        temp1.start = el1
                        temp1.finish = el1 + (temp1.finish - temp1.start)
                        # event_lst.append(EventModel.info(temp1))

                        ev = EventModel.info(temp1)
                        cat_id = db.session.query(UserEventModel).filter_by(event_id=el.event_id).first()
                        ev["category_id"] = cat_id.category_id
                        event_lst.append(ev)

            else:  # if it's not simply check time period and add it
                if parse(json_data["start_period"]) < temp.start < parse(json_data["finish_period"]):
                    # event_lst.append(EventModel.info(temp))
                    ev = EventModel.info(temp)
                    cat_id = db.session.query(UserEventModel).filter_by(event_id=el.event_id).first()
                    ev["category_id"] = cat_id.category_id
                    event_lst.append(ev)

        if not event_lst:
            return {"Response": "Events in this time period not found"}, 400

        return jsonify(event_lst), 200
