import os 
# for api call from postman
from flask_cors import CORS 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api


#file directory
basedir = os.path.abspath(os.path.dirname(__file__))
#images will be uploaded here
UPLOAD_FOLDER = 'app/static/path/to/the/uploads'
#allowed file types
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
CORS(app) # for api call from postman
app.config.from_object('app.config.Config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app) # flask-sqlalchemy
bc = Bcrypt(app) # flask-bcrypt
lm = LoginManager() # flask-loginmanager
lm.init_app(app)   # init the login manager
# flask restfull api
api = Api(app)
# jwt tocken
jwt = JWTManager(app)
# Setup database
@app.before_first_request
def initialize_database():
    db.create_all()

# Import routing, models and Start the App
from app import views, models , apiendpoints
