from app import app, USERS, models
from flask import request, Response
import json
from http import HTTPStatus


@app.route("/")
def index():
    return "<h1>Hello, World!</h1>"


@app.post("/user/create")
def user_create():
    data = request.get_json()
    id = len(USERS)
    first_name = data["first_name"]
    last_name = data["last_name"]
    phone = data["phone"]
    email = data["email"]

    if not models.User.is_valid_email(email) or not models.User.is_valid_phone(phone):
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = models.User(id, first_name, last_name, phone, email)

    USERS.append(user)

    response = Response(
        json.dumps(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "email": user.email,
                "score": user.score,
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )

    return response


@app.get("/user/<int:user_id>")
def get_user(user_id):
    if len(USERS) <= user_id or user_id < 0:
        return Response(status=HTTPStatus.NOT_FOUND)

    response = Response(
        json.dumps(
            {
                "id": USERS[user_id].id,
                "first_name": USERS[user_id].first_name,
                "last_name": USERS[user_id].last_name,
                "phone": USERS[user_id].phone,
                "email": USERS[user_id].email,
                "score": USERS[user_id].score,
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )

    return response
