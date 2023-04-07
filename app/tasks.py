from app import celery , mail , app , db
from flask_mail import Message
from app.models import Post , User
from celery.schedules import crontab

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1000.0, send_hourly_reminder.s(), name='send hourly reminder')


@celery.task
def sayhello(name):
    print("celesy task")
    return ("Hello {}".format(name))

#  send email using flask mail
@celery.task
def send_email(subject, sender, recipients, text_body, html_body):
    with app.app_context():
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
    return "Email sent"
# blog to csv 
@celery.task
def blog_to_csv(username):
    with app.app_context():
        user  = User.query.filter_by(user=username).first()
        posts = Post.query.filter_by(user_id=user.id).all()
        with open('{}_blogs.csv'.format(username), 'w') as f:
            # write the header
            f.write('id,title,caption,imgpath,timestamp,no_of_likes\n')
            # write the data
            for post in posts:
                f.write('{},{},{},{},{},{}\n'.format(post.id, post.title, post.caption, post.imgpath, post.timestamp, post.no_of_likes))
        # send email to user
        msg = Message(subject='Blog to CSV file',sender=app.config['MAIL_USERNAME'],recipients=[user.email])
        msg.body = 'Hi {}, your blog has been converted to a CSV file'.format(user.user)
        msg.html = 'Hi {}, your blog has been converted to a CSV file'.format(user.user)
        msg.attach('{}_blogs.csv'.format(username), 'text/csv', open('{}_blogs.csv'.format(username), 'rb').read())
        mail.send(msg)
    return {
        'status': 'success',
        'message': 'CSV file has been sent to your email'
    }


# import job  csv_to_blog task
import csv
import os
import datetime
@celery.task
def csv_to_blog(filename,user_id):
    print(filename)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            #  uniques id
            total_post = Post.query.all()
            row[0] = len(total_post) + 1
            row[4] = datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f')
            post = Post(id=row[0],title=row[1], caption=row[2], imgpath=row[3], timestamp=row[4], no_of_likes=row[5], user_id=user_id)
            db.session.add(post)
            db.session.commit()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return {
            'status': 'success',
            'message': 'CSV file has been uploaded'
        }



# Celery task to send reminder email
@celery.task
def send_hourly_reminder():
    print('Sending hourly reminder')
    # Get current time
    now = datetime.datetime.now()
    print(now)
    # Create reminder message
    subject = 'Monthly Engagement Report'
    recipients = ['shivam2003sy@gmail.com']
    subject = 'Monthly Engagement Report'
    recipients = ['21f1006233@ds.study.iitm.ac.in']
    text_body = 'this this body by this'  # Replace with actual email body template
    html_body = '<h1> hi this is a testing server and testing celery jobs  </h1>' # Replace with actual email body template
    send_email.delay(subject = subject, 
                    sender=app.config['MAIL_USERNAME'], 
                    recipients=recipients,
                    text_body = text_body,
                    html_body=html_body)