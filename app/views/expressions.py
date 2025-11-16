import json
import random
from http import HTTPStatus

from flask import request, Response

from app import app, EXPRESSIONS, models, USERS
from app.models import Expression, User


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

    user.solve(expression, user_answer)
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
