from logging import Logger
from app import app
from app.models import User , Card ,List
from flask import request, jsonify
import jwt
from datetime import datetime 
from app.util import  token_required
import csv
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
    return {
        "message": "User created successfully!",
        "data": new_user.to_json(),
        "error": None
    }, 201


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
                user["public_id"] = jwt.encode(
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

@app.route("/api/lists", methods=["GET"])
@token_required
def all_lists(current_user):
    card_dict ={}
    for l in current_user.list:
        card_dict[l.id] = [c.to_json() for c in l.card]     
    return {"LIST ID " :card_dict}



#CRUD on list models
@app.route("/api/lists/<list_id>", methods=["GET"] ,endpoint="get_list")
@token_required
def get_list(current_user, list_id):
    list = List.query.filter_by(id=list_id).first()
    if not list:
        return {
            "message": "List not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    return {
        "message": "List fetched successfully!",
        "data": list.to_json(),
        "error": None
    }, 200

@app.route("/api/lists/<list_id>", methods=["PUT"] ,endpoint="update_list")
@token_required
def update_list(current_user, list_id):
    list = List.query.filter_by(id=list_id).first()
    if not list:
        return {
            "message": "List not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    data = request.get_json()
    if not data:
        return {
            "message": "Please provide list details",
            "data": None,
            "error": "Bad request"
        }, 400
    if "name" in data:
        list.name = data["name"]
    if "description" in data:
        list.description = data["description"]
    list.save()
    return {
        "message": "List updated successfully!",
        "data": list.to_json(),
        "error": None
    }, 200

@app.route("/api/lists/<list_id>", methods=["DELETE"] ,endpoint="delete_list")
@token_required
def delete_list(current_user, list_id):
    list = List.query.filter_by(id=list_id).first()
    if not list:
        return {
            "message": "List not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    list.delete()
    return {
        "message": "List deleted successfully!",
        "data": None,
        "error": None
    }, 200

@app.route("/api/lists/create", methods=["POST"] ,endpoint="create_list")
@token_required
def create_list(current_user):
    data = request.get_json()
    if not data or not data["name"]:
        return {
            "message": "Please provide list name!",
            "data": None,
            "error": "Bad Request"
        }, 400
    new_list = List(
        name=data["name"],
        description=data["description"],
        user_id=current_user.id
    )
    new_list.save()
    return {
        "message": "List created successfully!",
        "data": new_list.to_json(),
        "error": None
    }, 201


##CRUD on list models
@app.route("/api/cards/<card_id>", methods=["GET"] ,endpoint="get_card")
@token_required
def get_card(current_user, card_id):
    card = Card.query.filter_by(id=card_id).first()
    if not card:
        return {
            "message": "Card not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    return {
        "message": "Card fetched successfully!",
        "data": card.to_json(),
        "error": None
    }, 200


@app.route("/api/cards/<card_id>", methods=["PUT"] ,endpoint="update_card")
@token_required
def update_card(current_user, card_id):
    card = Card.query.filter_by(id=card_id).first()
    if not card:
        return {
            "message": "Card not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    data = request.get_json()
    if not data:
        return {
            "message": "Please provide card details",
            "data": None,
            "error": "Bad request"
        }, 400
    if "name" in data:
        card.Title = data["name"]
    if "description" in data:
        card.Content = data["description"]
    if "list_id" in data:
        card.list_id = data["list_id"]
    if "due_date" in data:
        card.deadline = data["due_date"]
    if "status" in data:
        card.Completed = data["status"]
    card.save()
    return {
        "message": "Card updated successfully!",
        "data": card.to_json(),
        "error": None
    }, 200


@app.route("/api/cards/<card_id>", methods=["DELETE"] ,endpoint="delete_card")
@token_required
def delete_card(current_user, card_id):
    card = Card.query.filter_by(id=card_id).first()
    if not card:
        return {
            "message": "Card not found!",
            "data": None,
            "error": "Not Found"
        }, 404
    card.delete()
    return {
        "message": "Card deleted successfully!",
        "data": None,
        "error": None
    }, 200


@app.route("/api/cards/create/<list_id>", methods=["POST"] ,endpoint="create_card")
@token_required
def create_card(current_user , list_id):
    data = request.get_json()
    if not data or not data["name"]:
        return {
            "message": "Please provide card name!",
            "data": None,
            "error": "Bad Request"
        }, 400
    date_string_due = data["due_date"]
    date_input_due = datetime.strptime(date_string_due,'%Y-%m-%d')
    date_input_current = datetime.now()
    new_card = Card(
        Title=data["name"],
        Content=data["description"],
        deadline=date_input_due,
        Completed=data["status"],
        list_id=list_id  ,
        create_time = date_input_current
    )
    new_card.save()
    return {
        "message": "Card created successfully!",
        "data": new_card.to_json(),
        "error": None
    }, 201



# Statistics API
@app.route("/api/statistics/", methods=["GET"] ,endpoint="get_statistics_list")
@token_required
def get_statistics_list(current_user):
    list = List.query.filter_by(user_id=current_user.id).all()
    list_json=[]
    for i in list:
        card_json = []
        for j in i.card:
            card_json.append(j.to_json())
        list_json.append(card_json)
    return {
            "message": "Card fetched successfully!",
            "data": list_json,
            "error": None
        }, 200

