# Blog Lite web  app 
# Modern application Development 1 Graded Project



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
|──────LITE_BLOG/
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
| | | |──────────────post/
| | | | |────────────editpost.html
| | | | |────────────post.html
| | | |─────────────layouts/
| | | | |──────────────base-all.html
| | | | |──────────────base-home.html
| | | |──────────────includes
| | | | |──────────────footer.html
| | | | |──────────────navigation-all.html
| | | | |──────────────naviagation-home.html
| | | |──────────────accounts
| | | | |──────────────login
| | | | |──────────────register
| | |────────────────profile/
| | | |──────────────edit_profile.html
| | | |──────────────followers.html
| | | |──────────────following.html
| | | |──────────────profile.html
| | |────────────────search/
| | | |──────────────search.html
| | | |──────────────static/
| | | | |──────────────css/
| | | | |──────────────img/
| | | | |   |──────────────path/
| | | | | |  |   |──────────────to/
| | | | |           |──────────────the/
| | | | |               |──────────────uplaod/






```


API Documentation link

[API Docs](https://documenter.getpostman.com/view/17092710/2s83KNj76P#b478a8ad-bf79-41a1-a690-87d3cca3ce87)
