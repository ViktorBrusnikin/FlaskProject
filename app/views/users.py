import json
from http import HTTPStatus

from flask import request, Response, url_for

from app import app, USERS, models
from app.models import User

import matplotlib.pyplot as plt


@app.post("/user/create")
def user_create():
    data = request.get_json()
    user_id = len(USERS)
    first_name = data["first_name"]
    last_name = data["last_name"]
    phone = data["phone"]
    email = data["email"]

    if not models.User.is_valid_email(email) or not models.User.is_valid_phone(phone):
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = models.User(user_id, first_name, last_name, phone, email)

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
    if not User.is_valid_id(user_id):
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

@app.get('/users/<int:user_id>/history')
def get_user_history(user_id):
    if len(USERS) == 0:
        return Response(
            "Users database is empty",
            status=HTTPStatus.BAD_REQUEST,
        )

    if not User.is_valid_id(user_id):
        return Response(
            "User with this id is not found",
            status=HTTPStatus.BAD_REQUEST,
        )

    user = USERS[user_id]

    return Response(
        json.dumps(
            {
                "history": user.history
            }
        ),
        status=HTTPStatus.OK,
        mimetype='application/json'
    )

@app.get('/users/leaderboard')
def get_user_leaderboard():
    data = request.get_json()
    leaderboard_type = data['type']
    leaderboard = sorted(USERS, reverse=True)
    if leaderboard_type == 'table':
        return Response(
            json.dumps(
                {
                    "leaderboard": [user.to_dict() for user in leaderboard]
                }
            ),
            status=HTTPStatus.OK,
            mimetype='application/json'
        )
    elif leaderboard_type == 'graph':
        fig, ax = plt.subplots()
        user_names = [f'{user.first_name} {user.last_name} {user.id}' for user in leaderboard]
        user_scores = [user.score for user in leaderboard]

        ax.bar(user_names, user_scores)
        ax.set_ylabel("User score")
        ax.set_title("User leaderboard by score")
        plt.savefig('app/static/users_leaderboard.png')

        return Response(
            f"""<img src="{url_for('static', filename='users_leaderboard.png')}">""",
            status=HTTPStatus.OK,
            mimetype='text/html'
        )

    else:
        return Response(
            "Incorrect leader board type. You can choose \"table\" or \"graph\".",
            status=HTTPStatus.BAD_REQUEST,
        )