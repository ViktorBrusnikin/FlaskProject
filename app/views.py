from app import app, USERS, models, EXPRESSIONS, QUESTIONS
from flask import request, Response
import json
from http import HTTPStatus
import random

from app.models import User, Expression


@app.route("/")
def index():
    return "<h1>Hello, World!</h1>"


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


@app.post("/math/expression")
def generate_expr():
    data = request.get_json()
    expr_id = len(EXPRESSIONS)
    count_nums = data["count_nums"]
    operation = data["operation"]
    if operation == "random":
        operation = random.choice(["+", "*", "-", "//", "**"])
    min_num = data["min"]
    max_num = data["max"]

    if count_nums <= 1 or (count_nums > 2 and operation not in {"+", "*"}):
        return Response(status=HTTPStatus.BAD_REQUEST)

    values = [random.randint(min_num, max_num) for _ in range(count_nums)]
    expression = models.Expression(expr_id, operation, *values)

    EXPRESSIONS.append(expression)

    response = Response(
        json.dumps(
            {
                "id": expression.id,
                "operation": expression.operation,
                "values": expression.values,
                "expression": expression.to_string(),
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )

    return response


@app.get("/math/<int:expr_id>")
def get_expr(expr_id):
    if not Expression.is_valid_id(expr_id):
        return Response(status=HTTPStatus.BAD_REQUEST)

    expression = EXPRESSIONS[expr_id]

    response = Response(
        json.dumps(
            {
                "id": expression.id,
                "operation": expression.operation,
                "values": expression.values,
                "expression": expression.to_string(),
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )

    return response


@app.post("/math/<int:expression_id>/solve")
def expression_solve(expression_id):
    if not Expression.is_valid_id(expression_id):
        return Response(status=HTTPStatus.BAD_REQUEST)

    data = request.get_json()

    user_id = data["user_id"]

    if not User.is_valid_id(user_id):
        return Response(status=HTTPStatus.BAD_REQUEST)

    user = USERS[user_id]

    user_answer = data["user_answer"]

    expression = EXPRESSIONS[expression_id]

    if user_answer == expression.answer:
        user.increase_score(expression.reward)
        return Response(
            json.dumps(
                {
                    "expression_id": expression_id,
                    "result": "correct",
                    "reward": expression.reward,
                }
            ),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    user.increase_score(-1)

    return Response(
        json.dumps(
            {"expression_id": expression_id, "result": "incorrect", "reward": -1}
        ),
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@app.post("/questions/create")
def create_question():
    data = request.get_json()
    title = data["title"]
    description = data["description"]
    question_type = data["type"]
    question_id = len(QUESTIONS)
    question = None
    if question_type == "ONE-ANSWER":
        answer = data["answer"]
        if not models.OneAnswer.is_valid(answer):
            return Response(status=HTTPStatus.BAD_REQUEST)
        question = models.OneAnswer(question_id, title, description, answer, reward=1)
    elif question_type == "MULTIPLE-CHOICE":
        choices = data["choices"]
        answer = data["answer"]
        if not models.MultipleChoice.is_valid(answer, choices):
            return Response(status=HTTPStatus.BAD_REQUEST)
        question = models.MultipleChoice(
            question_id, title, description, answer, choices, reward=1
        )

    QUESTIONS.append(question)

    return Response(
        json.dumps(
            {
                "id": question.id,
                "title": question.title,
                "description": question.description,
                "type": question_type,
                "answer": question.answer,
            }
        ),
        status=HTTPStatus.OK,
    )
