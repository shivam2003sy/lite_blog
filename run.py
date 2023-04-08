# this is the entry point of the file
# this file is to be run to start the application 
from app import app# import app full app
from app import celery ,cache
if __name__ == '__main__':
    app.run(debug=True)