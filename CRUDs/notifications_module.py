from flask_mail import Mail, Message

from Models.users import UserModel
from Models.event import EventModel
from Models.user_event import UserEventModel
from Models.tasks import TaskModel

from CRUDs.task_crud import migrate_tasks, prio_to_int

from datetime import datetime, timedelta
from time import sleep

from threading import Thread


TIME_REVISION = 30  # minutes
MIDNIGHT_MAIL = datetime.strptime('11:50', '%H:%M')


def load_current_events(user_id, db):
    user_event_lst = db.session.query(UserEventModel).filter_by(user_id=user_id).all()
    event_lst = []
    if user_event_lst:
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            if datetime.now() <= temp.start <= datetime.now() + timedelta(minutes=TIME_REVISION):
                event_lst.append(temp)

    event_lst = sorted(event_lst, key=lambda ev: ev.start)
    return event_lst


def load_tomorrow_events(user_id, db):
    user_event_lst = db.session.query(UserEventModel).filter_by(user_id=user_id).all()
    event_lst = []
    if user_event_lst:
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            tomorrow = datetime.now() + timedelta(days=1)
            if temp.start.date == tomorrow.date():
                event_lst.append(temp)

    event_lst = sorted(event_lst, key=EventModel.start)
    return event_lst


def load_tomorrow_tasks(user_id, db):
    all_tasks = db.session.query(TaskModel).filter_by(user_id=user_id).all()
    print(all_tasks)
    task_lst = []
    if all_tasks:
        for el in all_tasks:
            tomorrow = datetime.now() + timedelta(days=1)
            print(tomorrow.date(), el.deadline.date())
            if el.deadline.date() == tomorrow.date():
                task_lst.append(el)

    task_lst = sorted(task_lst, key=lambda cur_el: prio_to_int(cur_el.priority), reverse=True)
    return task_lst


def send_mail(recipient_mail, subject, body, app):
    mail_sender = Mail(app)

    msg = Message(subject=subject,
                    sender='notification_planex@mailtrap.io',
                    recipients=[recipient_mail],
                    body=body)

    mail_sender.send(msg)
    print(msg.sender)
    print(*msg.recipients)
    print(msg.subject)
    print(msg.body)
    return "Message sent!"


def current_notification(user, db, app):
        events = load_current_events(user_id=user.id, db=db)
        if not events:
            return
        mail_body = f"{user.username}, You have {len(events)} events planed for next {TIME_REVISION} minutes:\n"
        i = 1
        for ev in events:
            start_time = ev.start.time()
            # delay = start_time - datetime.now().time()
            mail_body += f"{i}. {ev.title} - begins at {start_time}\n"
            if ev.description:
                mail_body += f"\t{ev.description}\n"
            i += 1
        send_mail(recipient_mail=user.email, subject='Next events', body=mail_body, app=app)


def tomorrow_notifications(user, db, app):
    events = load_tomorrow_events(user_id=user.id, db=db)
    tasks = load_tomorrow_tasks(user_id=user.id, db=db)
    if not events and not tasks:
        mail_body = "Congratulations, your day is free :)"
    else:
        mail_body = f"{user.username}, You have {len(events)} events and {len(tasks)} tasks planed for tomorrow:\n"
        if events:
            i = 1
            events = sorted(events, key=EventModel.start)
            for ev in events:
                start_time = ev.start.time()
                delay = (ev.start - datetime.now()).time()
                mail_body += f"{i}. ({delay} min) {ev.title} - begins at {start_time}\n"
                if ev.description:
                    mail_body += f"\t{ev.description}\n"
                i += 1
        if tasks:
            mail_body += 'To do list:\n'
            i = 1
            for el in tasks:
                mail_body += f"{i}. {el.title} - {el.priority} priority\n"
                if el.description:
                    mail_body += f"\t{el.description}\n"
                i += 1
    send_mail(recipient_mail=user.email,
              subject='Tomorrow routine',
              body=mail_body,
              app=app)


def notifications_func(db, app):
    print('Notifications thread started')
    with app.app_context():
        while True:
            print(datetime.now())
            # next day routine info
            if (datetime.now().hour == MIDNIGHT_MAIL.hour
                    and datetime.now().minute == MIDNIGHT_MAIL.minute):
                # relocate uncompleted tasks
                migrate_tasks(db)
                # send mail
                users = db.session.query(UserModel).filter_by().all()
                for user in users:
                    if user.team_working == 1:
                        tomorrow_notifications(user, db=db, app=app)
                sleep(60)
            # events for next TIME_REVISION minutes
            if datetime.now().minute % TIME_REVISION == 0:
                users = db.session.query(UserModel).filter_by().all()
                for user in users:
                    if user.team_working == 1:
                        current_notification(user, db=db, app=app)
                # sleep((TIME_REVISION-2)*60)
                sleep(60)






if __name__ == '__main__':
    from main import app, db

    notifications_func(db=db, app=app)
    app.run(debug=True)
