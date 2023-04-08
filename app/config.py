import os
from   decouple import config
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
class Config():
    CSRF_ENABLED = True
    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')
    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Celery Config
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
    # Flask-Mail settings
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'shivam2003sy@outlook.com'
    MAIL_PASSWORD = 'kstswoogmkexfome'
    # FLASK CACHE
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = '4'
    CACHE_DEFAULT_TIMEOUT = 300

