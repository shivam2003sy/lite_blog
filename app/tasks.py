from app import celery , mail , app
from flask_mail import Message


@celery.task
def sayhello(name):
    print("celesy task")
    return ("Hello {}".format(name))



@celery.task
def send_reminder():
    # Implement the logic to send a reminder via webhook, SMS, or email
    # using appropriate libraries or APIs
    pass


#  send email using flask mail
@celery.task
def send_email(subject, sender, recipients, text_body, html_body):
    with app.app_context():
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
    return "Email sent"