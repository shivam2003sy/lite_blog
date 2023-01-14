# this is the entry point of the file
# this file is to be run to start the application 
from app import app # import app full app

if __name__ == '__main__':
    app.run(debug=True)