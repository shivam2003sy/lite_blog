from app.models import User  , Follow ,Post ,Comments ,Postlikes
from app import cache

@cache.memoize(10)
def get_user(search_term):
        data = User.query.filter(User.user.ilike("%"+search_term+"%")).all()
        return data

@cache.memoize(timeout=5)
def get_following_posts(current_user):
    following = Follow.query.filter_by(follower_id=current_user.id).all()
    following = [following.followed_id for following in following]
    following.append(current_user.id)
    return following

@cache.memoize(timeout=5)
def get_post_details(post_id):
    post = Post.query.filter_by(id=post_id).first()
    userid = post.user_id
    user = User.query.filter_by(id=userid).first()
    comments = Comments.query.filter_by(post_id=post_id).all()
    likes = Postlikes.query.filter_by(post_id=post_id).all()
    return post, user, comments, likes
