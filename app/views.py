# Python modules
import os
import datetime
import matplotlib.pyplot as plt
plt.switch_backend('agg')
# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory,flash  ,jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
# App modules
from app import app, lm, db, bc, api
from app.models import User ,Userprofile, Post ,Follow ,Postlikes , Comments
from app.forms import LoginForm, RegisterForm 
from app.util import allowed_file  , delete_image
from app.util import token_required


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    # declare the Registration Form
    form = RegisterForm(request.form)
    msg = None
    success = False
    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg)
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)
        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()
        if user or user_by_email:
            msg = 'Error: User already exist exists!'
        else:
            user = User(user=username, email=email,password=password)
            user.save()
            newprofile = Userprofile(user_id =user.id , no_of_posts=0 , no_of_followers=0 , no_of_following=0)
            newprofile.save()
            
            success = True
            return redirect(url_for('login'))
    else:
        msg = 'Input error'
    return render_template('accounts/register.html', form=form, msg=msg, success=success)
# Authenticate user


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Declare the login form
    form = LoginForm(request.form)
    # Flask message injected into the page, in case of any errors
    msg = None
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        # filter User out of database through username
        user = User.query.filter_by(user=username).first()
        if user:
            # if bc.check_password_hash(user.password, password):
            #     login_user(user)
            #     return redirect(url_for('index'))
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "No user registerd with this usename "
    return render_template('accounts/login.html', form=form, msg=msg)



# App main route + generic routing
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        log_id = current_user.get_id()
        user = User.query.filter_by(id=log_id).first_or_404()
        app.logger.info('User %s logged in successfully', user.user)
        followers = Follow.query.filter_by(followed_id=log_id).all()
        users = []
        for i in followers:
            u = User.query.filter_by(id=i.follower_id).first()
            users.append(u)
        users.append(user)
        CurrentDate = datetime.datetime.now()
        all_users = User.query.all()
        display = []
        if len(all_users) <= 5:
            display = all_users
        else:
            display = all_users[:5]
        likes  =  Postlikes.query.filter_by(user_id = user.id).all()
        like_list = []
        for i in likes:
            like_list.append(i.post_id)
        return render_template('index.html',user=current_user,all_users=display,users=users ,like_list=like_list)



@app.route('/create', methods=['GET', 'POST'])
def create():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            title = request.form.get('title', '', type=str)
            content = request.form.get('description', '', type=str)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                app.logger.info('Post %s created successfully', filename )
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # post = Post(title=title, content=content, user_id=current_user.id)
            # post.save()
            app.logger.info('Post %s created successfully', title )
            app.logger.info('Post %s created successfully', content )
            
            app.logger.info("-----------------------------------------------------" )
            post = Post(title=title, caption=content, user_id=current_user.id, imgpath=filename , timestamp= datetime.datetime.now())
            user = Userprofile.query.filter_by(user_id=current_user.id).first()
            user.no_of_posts = user.no_of_posts + 1
            user.save()
            post.save()
            return redirect(url_for('index'))
        else:
            return render_template('page-403.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def editpost(post_id):
    if not current_user.is_authenticated:
            return redirect(url_for('login'))
    else:
            oldpost  = Post.query.filter_by(id=post_id).first()
            if request.method == 'POST':
                oldpost  = Post.query.filter_by(id=post_id).first()
                title = request.form.get('title', '', type=str)
                content = request.form.get('description', '', type=str)               
                if title:
                    oldpost.title = title
                if content:
                    oldpost.caption = content
                oldpost.timestamp= datetime.datetime.now()
                oldpost.save()
                return redirect(url_for('index'))
            else:
                return render_template('post/editpost.html', post = oldpost)





@app.route('/profile/<username>')
def profile(username):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(user=username).first_or_404()
        posts = Post.query.filter_by(user_id=user.id).all()
        follower = Follow.query.filter_by(followed_id=current_user.id).all()
        following = Follow.query.filter_by(follower_id=current_user.id).all() # unfollow
        follow_back=[]
        #follow back them with the id
        for i in range(len(follower)):
            x=follower[i].follower_id
            follow_back.append(x)
        unfollow = []
        #unfollow them with the id
        for i in range(len(following)):
            y =following[i].followed_id
            unfollow.append(y)
        return render_template('profile/profile.html', user=user, posts=posts , unfollow=unfollow , follow_back=follow_back )

@app.route('/profile/<username>/edit', methods=['GET', 'POST'])
def edit_profile(username):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(user=username).first_or_404()
        if request.method == 'POST':
            name  = request.form.get('username', '', type=str)
            email = request.form.get('email', '', type=str)
            if name:
                user.user = name
            if email:
                user.email = email 
            user.save()
            return redirect(url_for('index'))
        else:
            return render_template('profile/edit_profile.html', user=user)


@app.route('/myprofile')
def myprofile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(id=current_user.id).first_or_404()
        posts = Post.query.filter_by(user_id=user.id).all()
        return render_template('profile/myprofile.html', user=user, posts=posts)


# delete user

@app.route("/user", methods=["DELETE"] , endpoint="deleteuser")
def deleteuser():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User().get_by_id(current_user.id)
        userdetails= Userprofile.get_by_id(current_user.id)
        if userdetails:
            userdetails.delete()
        user.delete()
        # post  =  post.query.filter_by(user_id =current_user.id ).all()
        # for i in post:
        #     i.delete()
        return {
                    "message": "User  deleted successfully!",
                    "data": None,
                    "error": None
                }, 200











@app.route('/follow'  ,methods= ["POST"])
def follow():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        current_user_id = current_user.get_id()
        data = request.get_json()
        id  = int(data["id"])
        app.logger.info('User you unfollowed', id)
        followed_id = User.query.filter_by(id=id).first_or_404()
        follower_id = User.query.filter_by(id = current_user_id).first_or_404()
        follow = Follow(follower_id =follower_id.id , followed_id = followed_id.id)
        db.session.add(follow)
        db.session.commit()
        followed_user = User.query.filter_by(id=followed_id.id).first_or_404()
        followed_user.userprofile.no_of_followers +=1
        db.session.add(followed_user)
        follower_user = User.query.filter_by(id = current_user_id).first_or_404()
        follower_user.userprofile.no_of_following +=1
        db.session.add(follower_user)
        db.session.commit()
        return {"message": "followed sucessfully "}



@app.route("/unfollow" ,methods= ["POST"])
def unfollow():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        current_user_id = current_user.get_id()
        data = request.get_json()
        id  = int(data["id"])
        app.logger.info('User you unfollowed', id)
        followed_id = User.query.filter_by(id=id).first_or_404()
        follower_id = User.query.filter_by(id = current_user_id).first_or_404()
        follow = Follow.query.filter_by(follower_id =follower_id.id , followed_id = followed_id.id).first_or_404()
        db.session.delete(follow)
        db.session.commit()
        followed_user = User.query.filter_by(id=followed_id.id).first_or_404()
        followed_user.userprofile.no_of_followers -=1
        db.session.add(followed_user)
        follower_user = User.query.filter_by(id = current_user_id).first_or_404()
        follower_user.userprofile.no_of_following -=1
        db.session.add(follower_user)
        db.session.commit()
        return {"message": "unfollowed sucessfully "}



@app.route('/followings' , methods = ['get'])
def followings():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        current_user_id = current_user.get_id()
        following = Follow.query.filter_by(follower_id = current_user_id).all()
        following_list = []
        for i in following:
            user  = User.query.filter_by(id = i.followed_id).first_or_404()
            following_list.append(user)
        return render_template('profile/followings.html' , following_list = following_list , user = current_user)



@app.route('/followers' , methods = ['get'])
def followers():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        current_user_id = current_user.get_id()
        followers = Follow.query.filter_by(followed_id = current_user_id).all()
        followers_list = []
        for i in followers:
            user  = User.query.filter_by(id = i.follower_id).first_or_404()
            followers_list.append(user)
        followings = Follow.query.filter_by(follower_id = current_user_id).all()
        following_list = []
        for i in followings:
            user  = User.query.filter_by(id = i.followed_id).first_or_404()
            following_list.append(user)
        unfollow = []
        for i in following_list:
            if i in followers_list:
                unfollow.append(i.user)
        return render_template("/profile/followers.html", followers_list = followers_list , user = current_user , unfollow = unfollow)



@app.route('/post/<user>/<id>')
def post(user,id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'],"plot"+id+".png")
        if os.path.exists(image_path):
            os.remove(image_path)
            app.logger.info("------------------------------image ----------------deleete -------------")
        app.logger.warning(os.path.join(app.config['UPLOAD_FOLDER'],"plot"+id+".png"))
        user = User.query.filter_by(user=user).first_or_404()
        post = Post.query.filter_by(id=id).first_or_404()
        likes  =  Postlikes.query.filter_by(user_id = user.id).all()
        comment  = Comments.query.filter_by(post_id= post.id).all()
        like_list = []
        for i in likes:
            like_list.append(i.post_id)
        no_of_comment = len(comment)
        no_of_likes = post.no_of_likes
        plt.bar(1, no_of_comment, label='Comments')
        plt.bar(2, no_of_likes, label='Likes')

# Add labels and a legend
        plt.ylabel('Count')
        plt.xticks([], [])
        # plt.legend()
# Show the chart
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'],"plot"+id+".png"))
        image_path = 'plot{}.png'.format(id)
        return render_template('post/post.html', post=post , user=user , like_list = like_list , image_path= image_path  ,current_user = current_user , comment = comment)



@app.route("/like" , methods = ["POST"])
def like():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        data = request.get_json()
        current_user_id = current_user.get_id()
        post_id = int(data["id"])
        app.logger.info(str(post_id)+" liked by "+ str(current_user_id))
        alredylike = Postlikes.query.filter_by(user_id = current_user_id , post_id = post_id).first()
        if alredylike:
            return {"message": "already liked"}
        else:
            like = Postlikes(user_id = current_user_id , post_id = post_id)
            post  = Post.query.filter_by(id = post_id).first_or_404()
            post.no_of_likes +=1
            db.session.add(post)
            db.session.add(like)
            db.session.commit()
        return {"message": "liked sucessfully "}




@app.route("/unlike" , methods = ["POST"])
def unlike():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        data = request.get_json()
        current_user_id = current_user.get_id()
        post_id = data['id']
        like = Postlikes.query.filter_by(user_id = current_user_id , post_id = post_id).first_or_404()
        post  = Post.query.filter_by(id = post_id).first_or_404()
        post.no_of_likes -=1
        db.session.delete(like)
        db.session.commit()
        return {"message": "unliked sucessfully "}


@app.route('/comment' , methods = ["POST"])
def comment():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        data = request.get_json()
        current_user_id = current_user.get_id()
        post_id = data['id']
        comment = Comments(user_id = current_user_id , post_id = post_id , comment = data["comment"])
        db.session.add(comment)
        db.session.commit()
        return {"message": "commented sucessfully "}





@app.route('/deletecomment' , methods = ["GET"])
def deletecomment():
    return {"message": "comment deleted sucessfully "}







# delete post
@app.route("/posts/<int:post_id>", methods=["DELETE"] , endpoint="deletepost")
def deletepost(post_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                postlikes = Postlikes.query.filter_by(post_id=post_id).all()
                if postlikes:
                    for postlike in postlikes:
                        postlike.delete()
                comments = Comments.query.filter_by(post_id=post_id).all()
                if comments:
                    for comment in comments:
                        comment.delete() 
                post.delete()
                userprofile = Userprofile.query.filter_by(id = user.id)
                userprofile.no_of_posts -=1
                userprofile.save()
                return {
                    "message": "Post deleted successfully!",
                    "data": None,
                    "error": None
                }, 200
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    


@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    users = User.query.filter(User.user.contains(query)).all()
    return jsonify([user.user for user in users])





