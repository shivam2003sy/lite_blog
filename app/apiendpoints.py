from logging import Logger
from app import app , api ,db
from app.models import Follow, User
from flask import request, jsonify
import jwt
from datetime import datetime 
from app.util import  token_required
from flask_restful import Resource
from werkzeug.utils import secure_filename
from app.util import allowed_file
from app.models import User , Userprofile , Post , Postlikes , Comments
import os
from io import BytesIO
from PIL import Image

# Set the maximum image size
MAX_IMAGE_SIZE = (500, 500)


#  new user created  sucess
@app.route("/api/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data["username"] or not data["email"] or not data["password"]:
        return {
            "message": "Please provide username, email and password!",
            "data": None,
            "error": "Bad Request"
        }, 400
    if User().get_by_username(data["username"]):
        return {
            "message": "User already exists!",
            "data": None,
            "error": "Bad Request"
        }, 400
    new_user = User(
        user=data["username"],
        email=data["email"],
        password=data["password"]
    )
    new_user.save()
    user = User().get_by_username(data["username"])
    newprofile = Userprofile(user_id =user.id , no_of_posts=0 , no_of_followers=0 , no_of_following=0)
    newprofile.save()
    return {
        "message": "User created successfully! name  :" + str(new_user.user)+"id :"+str(new_user.id)+"email :  "+str(new_user.email),
        "data": new_user.to_json(),
        "error": None
    }, 201 


# login user  sucess
@app.route("/api/users/login", methods=["POST"])
def login_api():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        user = User().login(
            data["username"],
            data["password"]
        )
        if user:
            try:
                # token should expire after 24 hrs
                user["id"] = jwt.encode(
                    {"id": user["id"]},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                return {
                    "message": "Successfully fetched auth token",
                    "data": user
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
                "message": "Something went wrong!",
                "error": str(e),
                "data": None
        }, 500


# get all users
@app.route("/api/all", methods=["GET"], endpoint="get_all_users")
@token_required
def get_all_users(current_user):
    try:
        users = User.query.all()
        if users:
            users = [user.to_json() for user in users]
            return {
                "message": "Users fetched successfully!",
                "data": users,
                "error": None
            }, 200
        return {
            "message": "No users found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500




#  delete User  sucess
@app.route("/api/users", methods=["DELETE"])
@token_required
def delete_user(current_user):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            user.delete()
            return {
                "message": "User deleted successfully!"+str(user.user),
                "data": None,
                "error": None
            }, 200
        return {
            "message": "User not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500





#  read user and userProfile sucess
@app.route("/api/user", methods=["GET"] , endpoint="get_user")
@token_required
def get_user(current_user):
    user  = User.query.filter_by(id=current_user.id).first()
    if user:
        userprofile  = Userprofile.query.filter_by(user_id=current_user.id).first()
        if userprofile:
            return {
                    "message": "User fetched successfully!",
                    "data": {
                        "user": user.to_json(),
                        "userprofile": userprofile.to_json()
                    },
                    "error": None
                }, 200
    return {
        "message": "User not found!",
        "data": None,
        "error": "Not Found"
    }, 404


#   get  user by username
@app.route('/api/users/<string:username>', methods=['GET'] , endpoint="get_user_by_username")
@token_required
def get_user_by_username(current_user,username):
    user = User.query.filter_by(user=username).first()
    if user:
        userprofile  = Userprofile.query.filter_by(user_id=user.id).first()
        if userprofile:
            return {
                    "message": "User fetched successfully!",
                    "data": {
                        "user": user.to_json(),
                        "userprofile": userprofile.to_json()
                    },
                    "error": None
                }, 200
    return {
        "message": "User not found!",
        "data": None,
        "error": "Not Found"
    }, 404

@app.route("/api/user", methods=["PUT"], endpoint="update_user")
@token_required
def update_user(current_user):
    userprofile = Userprofile.query.filter_by(user_id=current_user.id).first()
    user = User.query.filter_by(id=current_user.id).first()
    if request.form:
        if "email" in request.form:
            user.email = request.form['email']
        if "image" in request.files:
            file = request.files["image"]
            # Check if the file has an allowed extension
            if file and allowed_file(file.filename):
                # Open and resize the image
                image = Image.open(file)
                image.thumbnail(MAX_IMAGE_SIZE)
                # Convert the image to a bytes object
                with BytesIO() as output:
                    image.save(output, format="JPEG")
                    blob_data = output.getvalue()
                # Set the user profile image to the bytes object
                userprofile.image = blob_data
            else:
                return {"error": "Invalid file type, allowed file types are jpg, jpeg, png, and gif."}, 400
        userprofile.save()
        user.save()
        return {
            "message": "User profile updated successfully!",
            "data": {
                "user": user.to_json(),
                "userprofile": userprofile.to_json()
            },
            "error": None
        }, 200
    else:
        return {"error": "User not found."}, 404






# read Posts sucess
@app.route("/api/posts", methods=["GET"] , endpoint="get_posts")
@token_required
def get_posts(current_user):
    user  =     User.query.filter_by(id=current_user.id).first()
    if user:
        posts  = Post.query.filter_by(user_id=current_user.id).all()
        if posts:
            return {
                    "message": "Posts fetched successfully!",
                    "data": {
                        "posts": [post.to_json() for post in posts]
                    },
                    "error": None
                }, 200
    return {
        "message": "Posts not found!",
        "data": None,
        "error": "Not Found"
    }, 404

# get all  post of username 
@app.route('/api/users/<string:username>/posts', methods=['GET'] , endpoint="get_posts_by_username")
@token_required
def get_posts_by_username(current_user,username):
    user = User.query.filter_by(user=username).first()
    if user:
        posts  = Post.query.filter_by(user_id=user.id).all()
        if posts:
            return {
                    "message": "Posts fetched successfully!",
                    "data": {
                        "posts": [post.to_json() for post in posts]
                    },
                    "error": None
                }, 200
    return {
        "message": "Posts not found!",
        "data": None,
        "error": "Not Found"
    }, 404
 
#single post  sucess
@app.route("/api/posts/<int:post_id>", methods=["GET"] , endpoint="get_post")
@token_required
def get_post(current_user , post_id):
    post  = Post.query.filter_by(id=post_id).first()
    if post:
        postcomment = Comments.query.filter_by(post_id=post_id).all()
        postliked = Postlikes.query.filter_by(post_id=post_id).all()
        user  = User.query.filter_by(id=post.user_id).first()
        return {
                    "message": "Post fetched successfully!",
                    "data": {
                        "user": user.to_json(),
                        "post": post.to_json(),
                        "postlikedby": [postlike.to_json() for postlike in postliked],
                        "postcommentedby": [postcomment.to_json() for postcomment in postcomment]
                    },
                    "error": None
                }, 200
    return{
                "message": "Post not found!",
                "data": None,
                "error": "Not Found"

            }

# # create post sucess
@app.route("/api/posts", methods=["POST"] , endpoint="create_post")
@token_required
def create_post(current_user):
    app.logger.info("create post")
    title = request.form['title']
    description = request.form['description']
    app.logger.info(title)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        app.logger.info("-----------------" + filename)
    if not title:
        return {
            "message": "Please provide post details",
            "data": None,
            "error": "Bad request"
        }, 400
    user = User().get_by_id(current_user.id)
    if user:
        post = Post(
            user_id = user.id,
            title = title,
            caption = description,
            imgpath= filename,
            timestamp= datetime.now()
        )
        user = Userprofile().query.filter_by(user_id=current_user.id).first()

        user.no_of_posts = user.no_of_posts + 1
        user.save()
        post.save()
        return {
            "message": "Post created successfully!",
            "data": post.to_json(),
            "error": None
        }, 201

# update post  sucess
@app.route("/api/posts/<int:post_id>", methods=["PUT"] , endpoint="update_post")
@token_required
def update_post(current_user , post_id):
    post  = Post.query.filter_by(id = post_id).first()
    app.logger.info("update post")
    if request.form['title']:
        title = request.form['title']
        post.title = title
    if request.form['description']:
        description = request.form['description']
        post.caption = description
    post.timestamp = datetime.now()
    user = User().get_by_id(current_user.id)
    if user:
        post.save()
        user = Userprofile().get_by_id(current_user.id)
        user.no_of_posts = user.no_of_posts + 1
        user.save()
        return {
            "message": "Post updated successfully!",
            "data": post.to_json(),
            "error": None
        }, 201

# delete post sucess
@app.route("/api/posts/<int:post_id>", methods=["DELETE"] , endpoint="delete_post")
@token_required
def delete_post(current_user , post_id):
    try:
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
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


# like post
@app.route("/api/posts/<int:post_id>/like", methods=["POST"] , endpoint="like_post")
@token_required
def like_post(current_user , post_id):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                postlike = Postlikes(
                    user_id = user.id,
                    post_id = post.id,
                )
            duplicate  = Postlikes.query.filter_by(user_id=user.id , post_id=post.id).first()
            if duplicate:
                return {
                    "message": "Post already liked!",
                    "data": None,
                    "error": "Bad request"
                }, 400
            else:
                postlike.save()
                post.no_of_likes = Postlikes.query.filter_by(post_id=post_id).count()
                post.save()
                return {
                    "message": "Post liked successfully!",
                    "data": postlike.to_json(),
                    "error": None
                }, 201
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

# unlike post sucessa
@app.route("/api/posts/<int:post_id>/unlike", methods=["POST"] , endpoint="unlike_post")
@token_required
def unlike_post(current_user , post_id):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                postlike = Postlikes.query.filter_by(user_id=user.id , post_id=post.id).first()
                if postlike:
                    postlike.delete()
                    post.no_of_likes = Postlikes.query.filter_by(post_id=post_id).count()
                    post.save()

                    return {
                        "message": "Post unliked successfully!",
                        "data": None,
                        "error": None
                    }, 200
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

# comment on post sucess
@app.route("/api/posts/<int:post_id>/comment", methods=["POST"] , endpoint="comment_post")
@token_required
def comment_post(current_user , post_id):
    try:
        data = request.get_json()
        if not data:
            return {
                "message": "Please provide comment details",
                "data": None,
                "error": "Bad request"
            }, 400
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                comment = Comments(
                    user_id = user.id,
                    post_id = post.id,
                    comment = data.get("comment"),
                    timestamp = datetime.now()
                )
                comment.save()
                
                #   all comment on post with username
                comments = Comments.query.filter_by(post_id=post_id).all()
                comments = [comment.to_json() for comment in comments]
                for comment in comments:
                    user  = User().get_by_id(comment['user_id'])
                    comment['user'] = user.to_json()
                return {
                    "message": "Comment added successfully!",
                    "data": comments,
                    "error": None
                }, 201
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

# delete comment sucess
@app.route("/api/posts/<int:post_id>/comment/<int:comment_id>", methods=["DELETE"] , endpoint="delete_comment")
@token_required
def delete_comment(current_user , post_id , comment_id):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                comment = Comments.query.filter_by(id=comment_id , user_id=user.id , post_id=post.id).first()
                if comment:
                    comment.delete()
                    return {
                        "message": "Comment deleted successfully!",
                        "data": None,
                        "error": None
                    }, 200
        return {
            "message": "Comment not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

# get all comments sucess
@app.route("/api/posts/<int:post_id>/comments", methods=["GET"] , endpoint="get_comments")
@token_required
def get_comments(current_user , post_id):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                comments = Comments.query.filter_by(post_id=post.id).all()
                if comments:
                    return {
                        "message": "Comments fetched successfully!",
                        "data": [comment.to_json() for comment in comments],
                        "error": None
                    }, 200
                return {
                    "message": "No comments found!",
                    "data": None,
                    "error": "Not Found"
                }, 404
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


# get all likes  sucess
@app.route("/api/posts/<int:post_id>/likes", methods=["GET"] , endpoint="get_likes")
@token_required
def get_likes(current_user , post_id):
    try:
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                likes = Postlikes.query.filter_by(post_id=post.id).all()
                if likes:
                    return {
                        "message": "Likes fetched successfully!",
                        "data": [like.to_json() for like in likes],
                        "error": None
                    }, 200
                return {
                    "message": "No likes found!",
                    "data": None,
                    "error": "Not Found"
                }, 404
        return {
            "message": "Post not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500



# update comment sucess
@app.route("/api/posts/<int:post_id>/comment/<int:comment_id>", methods=["PUT"] , endpoint="update_comment")
@token_required
def update_comment(current_user , post_id , comment_id):
    try:
        data = request.get_json()
        if not data:
            return {
                "message": "Please provide comment details",
                "data": None,
                "error": "Bad request"
            }, 400
        user = User().get_by_id(current_user.id)
        if user:
            post = Post().get_by_id(post_id)
            if post:
                comment = Comments.query.filter_by(id=comment_id , user_id=user.id , post_id=post.id).first()
                if comment:
                    comment.comment = data.get("comment")
                    comment.save()
                    return {
                        "message": "Comment updated successfully!",
                        "data": comment.to_json(),
                        "error": None
                    }, 200
        return {
            "message": "Comment not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500



# search users with string 
@app.route("/api/users/search/<string:search_string>", methods=["GET"] , endpoint="search_users")
def search_users(search_string):
    try:
        users = User.query.filter(User.user.ilike("%"+search_string+"%")).all()
        if users:
            return {
                    "message": "Users fetched successfully!",
                    "data": [user.to_json() for user in users],
                    "error": None
                }, 200
        return {
                "message": "No users found!",
                "data": None,
                "error": "Not Found"
            }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500



#  get  followers of user form table Follow
@app.route("/api/users/<string:user>/followers", methods=["GET"] , endpoint="get_followers")
@token_required
def get_followers(current_user , user):
    try:
        user = User.query.filter_by(user=user).first()
        if user:
            followers = Follow.query.filter_by(followed_id=user.id).all()
            if followers:
                # get user names of followers
                followers = [User.query.filter_by(id=follower.follower_id).first() for follower in followers]
                return {
                    "message": "Followers fetched successfully!",
                    "data": [follower.to_json() for follower in followers],
                    "error": None
                }, 200
            return {
                "message": "No followers found!",
                "data": None,
                "error": "Not Found"
            }, 404
        return {
            "message": "User not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

#  get  followings of user form table Follow
@app.route("/api/users/<string:user>/followings", methods=["GET"] , endpoint="get_followings")
@token_required
def get_followings(current_user , user):
    try:
        user = User.query.filter_by(user=user).first()
        if user:
            followings = Follow.query.filter_by(follower_id=user.id).all() # kis kis ko follow krta h user
            if followings:
                # get user names of folowings
                followings = [User.query.filter_by(id=following.followed_id).first() for following in followings]
                return {
                    "message": "Followings fetched successfully!",
                    "data": [following.to_json() for following in followings],
                    "error": None
                }, 200
            return {
                "message": "No followings found!",
                "data": None,
                "error": "Not Found"
            }, 404
        return {
            "message": "User not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

#  follow  or unfollow user 
@app.route("/api/users/<string:user>/follow", methods=["POST"] , endpoint="follow_user")
@token_required
def follow_user(current_user , user):
    try:
        user = User.query.filter_by(user=user).first()
        if user:
            if user.id == current_user.id:
                return {
                    "message": "You can't follow yourself!",
                    "data": None,
                    "error": "Bad request"
                }, 400
            follow = Follow.query.filter_by(follower_id=current_user.id , followed_id=user.id).first()
            if not follow:
                follow = Follow(follower_id=current_user.id , followed_id=user.id)
                follow.save()
                followed = Userprofile.query.filter_by(user_id=user.id).first()
                followed.no_of_followers += 1
                followed.save()
                follower = Userprofile.query.filter_by(user_id=current_user.id).first()
                follower.no_of_following += 1
                follower.save()
                return {
                    "message": "User followed successfully!",
                    "data": follow.to_json(),
                    "error": None
                }, 200
            return {
                "message": "User already followed!",
                "data": follow.to_json(),
                "error": None
            }, 200
        
        return {
            "message": "User not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500

#  unfollow user
@app.route("/api/users/<string:user>/unfollow", methods=["POST"] , endpoint="unfollow_user")
@token_required
def unfollow_user(current_user , user):
    try:
        user = User.query.filter_by(user=user).first()
        if user:
            follow = Follow.query.filter_by(follower_id=current_user.id , followed_id=user.id).first()
            if follow:
                follow.delete()
                followed = Userprofile.query.filter_by(user_id=user.id).first()
                followed.no_of_followers -= 1
                followed.save()
                follower = Userprofile.query.filter_by(user_id=current_user.id).first()
                follower.no_of_following -= 1
                follower.save()
                return {
                    "message": "User unfollowed successfully!",
                    "data": follow.to_json(),
                    "error": None
                }, 200
            return {
                "message": "You don't follow this user!",
                "data": None,
                "error": "Bad request"
            }, 400
        return {
            "message": "User not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500
    
@app.route("/api/feeds", methods=["GET"] , endpoint="get_feeds")
@token_required
def get_feeds(current_user):
    following = Follow.query.filter_by(follower_id=current_user.id).all()
    following = [following.followed_id for following in following]
    following.append(current_user.id)
    posts = Post.query.filter(Post.user_id.in_(following)).order_by(Post.timestamp.desc()).all()
    if posts:
        posts = [post.to_json() for post in posts]
        for post in posts:
            userid  = Post.query.filter_by(id=post['id']).first().user_id
            user = User.query.filter_by(id=userid).first()
            post["user"] = user.to_json()
            post["comments"] = Comments.query.filter_by(post_id=post["id"]).all()
            post["comments"] = [comment.to_json() for comment in post["comments"]]
            for comment in post["comments"]:
                comment["user"] = User.query.filter_by(id=comment["user_id"]).first().to_json()

            #  names of users who liked the post
            likes = Postlikes.query.filter_by(post_id=post["id"]).all()
            likes = [like.to_json() for like in likes]
            post["likes"] = [User.query.filter_by(id=like["user_id"]).first().to_json() for like in likes]
        return {
            "message": "Posts fetched successfully!",
            "data": posts,
            "error": None
        }, 200
    return {
        "message": "No posts found!",
        "data": None,
        "error": "Not Found"
    }, 404
            




#  celery tasks
from app import tasks
@app.route("/api/tasks/<string:name>", methods=["GET"] , endpoint="get_tasks")
def get_tasks(name):
    jobs = tasks.sayhello.apply_async(args=[name])
    result = jobs.wait()
    return {
        "message": "Task added to queue!",
        "data":str(jobs) ,
        "result" : result,
        "error": None
    }, 200

# run task print date
@app.route("/api/tasks", methods=["GET"] , endpoint="get_date")
def get_date():
    jobs = tasks.print_current_time.apply_async()
    result = jobs.wait()
    return {
        "message": "Task added to queue!",
        "data":str(jobs) ,
        "result" : result,
        "error": None
    }, 200

#  send mail using celery send_mail task
@app.route('/send_email', methods=['POST'])
def trigger_send_email():
    subject = 'testing'
    sender = 'shivam2003sy@outlook.com'
    recipients = ['shivam2003sy@gmail.com', 'ankitayadav80048@gmail.com']
    text_body = 'Plain text'
    html_body = '<h1>I lOVE YOU ANKITA</h1> <h3> will you mary me <h3><img src="https://images.unsplash.com/photo-1606041008023-472dfb5e530f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=388&q=80" alt="flower">'
    
    # Trigger the Celery task asynchronously
    tasks.send_email.apply_async(args=[subject, sender, recipients, text_body, html_body])
    return 'Email task scheduled'