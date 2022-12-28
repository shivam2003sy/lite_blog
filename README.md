# kanban web  app 
# Modern application Development 1 Graded Project

A kanban web app is one of the tools that can be used  to manage work at a personal or organizational level.

Ways to use :  
API for CRUD On List and Cards of tasks 
Web application to manage your daily tasks

### Extension:
- Restful: [Flask-restplus](http://flask-restplus.readthedocs.io/en/stable/)

- SQL ORM: [Flask-SQLalchemy](https://flask-sqlalchemy.palletsprojects.com/en/latest/)

- Token: [PYjwt](https://pyjwt.readthedocs.io/en/stable/)

- OAuth: [Flask-OAuth](https://flask-login.readthedocs.io/en/latest/)

- template :[jinja-template](https://jinja.palletsprojects.com/en/3.1.x/)

- Visualization : [Matplotlib](https://matplotlib.org/)

## Installation
make sure python is installed in  your system.
Install with pip:

```
$ git clone "repo"
$ cd kanban
$ virtualenv venv
$ venv/Scripts/activate
$ pip install -r requirements.txt
$ flask run
```
## Flask Application Structure
```
.
|──────kanban/
| |────.env
| |────.gitignore
| |────requiurements.txt
| |──────run.py
| |───────────app/
| | |────────__init__.py
| | |────────endpoints.py
| | |────────config.py
| | |────────forms.py
| | |────────models.py
| | |────────utils.py
| | |────────views.py
| | |────────────────templates/
| | | |──────────────index.html
| | | |──────────────page-403.html
| | | |──────────────page-404.html
| | | |──────────────page500.html
| | | |──────────────summary/
| | | | |────────────main.py
| | | |─────────────layouts/
| | | | |──────────────base.html
| | | | |──────────────base-home.html
| | | |──────────────includes
| | | | |──────────────footer.html
| | | | |──────────────navigation.html
| | | | |──────────────naviagation-home.html
| | | |──────────────create/
| | | | |──────────────createlist.html
| | | | |──────────────editlist.html
| | | |──────────────card
| | | | |──────────────createcard.hmtl
| | | | |──────────────editcard.html
| | | |──────────────accounts
| | | | |──────────────login
| | | | |──────────────register
| | | |──────────────static/

```


API Documentation link

[API Docs](https://documenter.getpostman.com/view/17092710/2s83KNj76P#b478a8ad-bf79-41a1-a690-87d3cca3ce87)
