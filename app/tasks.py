from app import celery , mail , app , db
from flask_mail import Message
from app.models import Post , User , Postlikes , Comments , User ,Follow
from celery.schedules import crontab

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
    # Executes every day at 10:55 AM
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/2'),
        monthly_reminder.s(),
    )
    sender.add_periodic_task(
        crontab(minute='*/5'),
        daily_reminder.s(),
    )

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


@celery.task
def daily_reminder():
    with app.app_context():
        users = User.query.all()
        for user in users:
            # check if user has posted any blog today using timestamp
            posts = Post.query.filter_by(user_id=user.id).all()
            for post in posts:
                if post.timestamp.date() == datetime.date.today():
                    break
            else:
                msg = Message(subject='Not posted today',sender=app.config['MAIL_USERNAME'],recipients=[user.email])
                msg.html = """
                <h1>Hi {}, you have not posted any blog today</h1>
                <p>While you are away, here are some blogs you might like</p>
                """.format(user.user)
                #  get 3 random blogs
                posts = Post.query.all()
                import random
                if len(posts) >  3:
                    random_posts = random.sample(posts, 3)
                    for post in random_posts:
                        msg.html += """
                        <h3>{}</h3>
                        <p>{}</p>
                        <img src="http://localhost:5000/static/path/to/the/uploads/{}" alt="{}" width="200" height="200">
                        <p>posted on {}</p>
                        <p>likes: {}</p>
                        <a href="http://locahost:8080/post/{}">Read more</a>
                        """.format(post.title, post.caption, post.imgpath, post.title, post.timestamp, post.no_of_likes , post.id)
                    mail.send(msg)
                    print('daily reminder sent to {}'.format(user.user))
    return {
        'status': 'success',
        'message': 'Email has been sent to all users',
    }

@celery.task
def monthly_reminder():
    with app.app_context():
        users = User.query.all()
        for user in users:
            msg = Message(subject='Monthly report',sender=app.config['MAIL_USERNAME'],recipients=[user.email])
            #  create a report of all ingagements of the user
            posts = Post.query.filter_by(user_id=user.id).all()
            #  POST CREATED THIS MONTHS
            post_created_this_month = 0
            posts_stats = []
            for post in posts:
                # check if post is created this month
                if post.timestamp.month == datetime.date.today().month and post.timestamp.year == datetime.date.today().year:
                    post_created_this_month += 1
                    post_stats = {
                        'post_id': post.id,
                        'post_title': post.title,
                        'post_caption': post.caption,
                        'post_imgpath': post.imgpath,
                        'post_timestamp': post.timestamp,
                        'post_no_of_likes': post.no_of_likes,
                    }
                    comment = Comments.query.filter_by(post_id=post.id).all()
                    post_stats['no_of_comments'] = len(comment)
                    for c in comment:
                        comments = {
                            'comment_id': c.id,
                            'comment': c.comment,
                            'comment_timestamp': c.timestamp,
                        }

                        for u in users:
                            if u.id == c.user_id:
                                comments['comment_user'] = u.user
                        post_stats['comments'] = (comments)
                    likes = Postlikes.query.filter_by(post_id=post.id).all()
                    for l in likes:
                        for u in users:
                            if u.id == l.user_id:
                                post_stats['likes'] = u.user
                    posts_stats.append(post_stats)

            #  POST LIKED THIS MONTHS
            post_liked_this_month = 0
            post_you_liked  ={
                'post_id': [],
                'post_title': [],
                'post_caption': [],
            }
            for post in posts:
                likes = Postlikes.query.filter_by(post_id=post.id).all()
                for like in likes:
                    if like.timestamp.month == datetime.date.today().month and like.timestamp.year == datetime.date.today().year:
                        if like.user_id == user.id:
                            post_liked_this_month += 1
                            post_you_liked['post_id'].append(post.id)
                            post_you_liked['post_title'].append(post.title)
                            post_you_liked['post_caption'].append(post.caption)
                            break

            #  POST COMMENTED THIS MONTHS
            post_commented_this_month = 0
            post_you_commented = {
                'post_id': [],
                'post_title': [],
                'post_caption': [],
            }
            for post in posts:
                comments = Comments.query.filter_by(post_id=post.id).all()
                for comment in comments:
                    if comment.timestamp.month == datetime.date.today().month and comment.timestamp.year == datetime.date.today().year:
                        if comment.user_id == user.id:
                            post_commented_this_month += 1
                            post_you_commented['post_id'].append(post.id)
                            post_you_commented['post_title'].append(post.title)
                            post_you_commented['post_caption'].append(post.caption)
                            break

            # USER FOLLOWED THIS MONTHS
            user_followed_this_month = 0
            user_you_followed = {
                'user_id': [],
                'user': [],
            }
            for u in users:
                if u.id != user.id:
                    followers = Follow.query.filter_by(follower_id=u.id).all()
                    for follower in followers:
                        if follower.timestamp.month == datetime.date.today().month and follower.timestamp.year == datetime.date.today().year:
                            if follower.follower_id == user.id:
                                user_followed_this_month += 1
                                user_you_followed['user_id'].append(u.id)
                                user_you_followed['user'].append(u.user)
                                break

            # YOU followed THIS MONTHS
            following_this_month = 0
            followings ={
                'user_id': [],
                'user': [],

            }
            for u in users:
                if u.id != user.id:
                    followers = Follow.query.filter_by(followed_id=u.id).all()
                    for follower in followers:
                        if follower.timestamp.month == datetime.date.today().month and follower.timestamp.year == datetime.date.today().year:
                            if follower.follower_id == user.id:
                                following_this_month += 1
                                followings['user_id'].append(u.id)
                                followings['user'].append(u.user)
                                break
        print('monthly reminder sent to {}'.format(user.user))
        msg.html = """
        <h1 style="color: #007BFF;">Monthly Report</h1>
        <p>Here is your monthly report:</p>
        <p><strong>Posts created this month:</strong> {}</p>
        <p><strong>Posts liked this month:</strong> {}</p>
        <p><strong>Posts commented this month:</strong> {}</p>
        <p><strong>Users followed this month:</strong> {}</p>
        <p><strong>You followed this month:</strong> {}</p>
        <p><strong>Posts JSON data:</strong> {}</p>
        <p><strong>Users you followed JSON data:</strong> {}</p>
        <p><strong>Followings JSON data:</strong> {}</p>
        <p><strong>Posts you liked JSON data:</strong> {}</p>
        <p><strong>Posts you commented on JSON data:</strong> {}</p>
        """.format(post_created_this_month, post_liked_this_month, post_commented_this_month, user_followed_this_month, following_this_month ,posts_stats ,user_you_followed, followings, post_you_liked, post_you_commented)
        mail.send(msg)
# verify email
@celery.task
def verify_email(email):
    # msg = Message(subject='Verify your email',sender=app.config['MAIL_USERNAME'],recipients=[email])
    #     msg.html = """
    #     <h1>Verify your email</h1>
    #     <p>Click on the link below to verify your email</p>
    #     <a href="http://localhost:8080/verify/{}">Verify</a>
    #     """.format(email)
    #     mail.send(msg)
    #     print('email sent to {}'.format(email))
    send_email.delay(
        subject='Verify your email',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email],
        text_body='Verify your email',
        html_body="""
        <h1>Verify your email</h1>
        <p>Click on the link below to verify your email</p>
        <a href="http://localhost:5000/api/verify/{}">Verify</a>
        """.format(email)
    )
    return {
        'status': 'success',
        'message': 'Email has been sent to {}'.format(email),
    }