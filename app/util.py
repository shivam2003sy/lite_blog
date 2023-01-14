from flask import current_app
from functools import wraps
import jwt
from flask import request, abort
from flask import current_app
from app import ALLOWED_EXTENSIONS, app
from app.models import *
import os 
def token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
            if current_user.id != data['id']:
                return {
                "message": "Authentication token is Invalid !",
                "data": None,
                "error": "Unauthorized"
            }, 401
            # if not current_user["active"]:
            #     abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        return f(current_user, *args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)
        app.logger.info("------------------------------image ----------------deleete -------------")
        return 'Image deleted successfully'
    else:
        return 'Image not found'