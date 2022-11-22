from flask_mail import Mail, Message

from Models.users import UserModel
from Models.event import EventModel
from Models.user_event import UserEventModel
from Models.tasks import TaskModel

from datetime import datetime, timedelta


# to do: change this import
from main import db
from main import app

# def load_notification_module(app, db):

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '8190f37066adef'
app.config['MAIL_PASSWORD'] = 'ca2237b79a9cc0'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

TIME_REVISION = 30  # minutes


mail_sender = Mail(app)


def load_current_events(user_id):
    user_event_lst = db.session.query(UserEventModel).filter_by(user_id=user_id).all()
    event_lst = []
    if user_event_lst:
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            if datetime.now() <= temp.start <= datetime.now() + timedelta(minutes=TIME_REVISION):
                event_lst.append(temp)
    return event_lst


def load_tomorrow_events(user_id):
    user_event_lst = db.session.query(UserEventModel).filter_by(user_id=user_id).all()
    event_lst = []
    if user_event_lst:
        for el in user_event_lst:
            temp = db.session.query(EventModel).filter_by(id=el.event_id).first()
            tomorrow = datetime.now() + timedelta(days=1)
            if temp.start.date == tomorrow.date():
                event_lst.append(temp)
    return event_lst


def load_tomorrow_tasks(user_id):
    all_tasks = db.session.query(TaskModel).filter_by(user_id=user_id).all()
    print(all_tasks)
    task_lst = []
    if all_tasks:
        for el in all_tasks:
            tomorrow = datetime.now() + timedelta(days=1)
            print(tomorrow.date(), el.deadline.date())
            if el.deadline.date() == tomorrow.date():
                task_lst.append(el)
    return task_lst


def send_mail(recipient_mail, subject, body):
    msg = Message(subject=subject,
                  sender='notification_planex@mailtrap.io',
                  recipients=[recipient_mail],
                  body=body)

    # mail_sender.send(msg)
    print(msg.sender)
    print(*msg.recipients)
    print(msg.subject)
    print(msg.body)
    return "Message sent!"


def current_notification(user):
    events = load_current_events(user_id=user.id)
    if not events:
        return
    mail_body = f"{user.username}, You have {len(events)} events planed:\n"
    i = 1
    for ev in events:
        start_time = ev.start.time()
        # delay = start_time - datetime.now().time()
        mail_body += f"{i}. {ev.title} - begins at {start_time}\n"
        if ev.description:
            mail_body += f"\t{ev.description}\n"
        i += 1
    send_mail(recipient_mail=user.email, subject='Next events', body=mail_body)


def tomorrow_notifications(user):
    events = load_tomorrow_events(user_id=user.id)
    tasks = load_tomorrow_tasks(user_id=user.id)
    if not events and not tasks:
        mail_body = "Congratulations, your day is free :)"
    else:
        mail_body = f"{user.username}, You have {len(events)} events and {len(tasks)} tasks planed for tomorrow:\n"
        if events:
            i = 1
            events.sort(key=EventModel.start, reversed=False)
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
    send_mail(recipient_mail=user.email, subject='Tomorrow routine', body=mail_body)


if __name__ == '__main__':
    user = db.session.query(UserModel).filter_by(id=14).first()
    current_notification(user)
    tomorrow_notifications(user)
    app.run(debug=True)
