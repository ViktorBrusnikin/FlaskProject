import json
import random
from http import HTTPStatus

from flask import request, Response, url_for

from app import app, QUESTIONS, models, USERS


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
            return Response(
                "answer must be str",
                status=HTTPStatus.BAD_REQUEST
                            )
        question = models.OneAnswer(question_id, title, description, answer, reward=1)
    elif question_type == "MULTIPLE-CHOICE":
        choices = data["choices"]
        answer = data["answer"]
        if not models.MultipleChoice.is_valid(answer, choices):
            return Response(
                "answer must be int and choices must be list, 0 <= answer <= len(choices))",
                status=HTTPStatus.BAD_REQUEST
            )
        question = models.MultipleChoice(
            question_id, title, description, answer, choices, reward=1
        )

    if question is None:
        return Response(
            'Question must be of ONE-ANSWER type or MULTIPLE-CHOICE type',
            status=HTTPStatus.BAD_REQUEST
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
        status=HTTPStatus.CREATED,
    )


@app.get('/question/random')
def get_random_question():
    if len(QUESTIONS) == 0:
        return Response(
            f'No questions in database. Please, <a href="{url_for('create_question')}">create question</a>',
            status=HTTPStatus.NOT_FOUND
        )
    question_id = random.randint(0, len(QUESTIONS)-1)
    question = QUESTIONS[question_id]
    return Response(
        json.dumps(
            {
                "question_id": question.id,
                "reward": question.reward
            }
        ),
        status=HTTPStatus.OK,
        mimetype='application/json'
    )


@app.post('/questions/<int:question_id>/solve')
def solve_question(question_id):
    if question_id < 0 or question_id >= len(QUESTIONS):
        return Response(
            f'Not found this questions in database.',
            status=HTTPStatus.NOT_FOUND
        )

    question = QUESTIONS[question_id]

    data = request.get_json()

    user_id = data['user_id']
    if not isinstance(user_id, int) or user_id < 0 or user_id >= len(USERS):
        return Response(
            f'Not found this user in database or incorrect type of answer.',
            status=HTTPStatus.NOT_FOUND
        )

    user = USERS[user_id]

    user_answer = data['user_answer']
    if isinstance(question, models.OneAnswer) and not isinstance(user_answer, str):
        return Response(
            f'Incorrect type of answer.',
            status=HTTPStatus.NOT_FOUND
        )
    if isinstance(question, models.MultipleChoice) and not isinstance(user_answer, int):
        return Response(
            f'Incorrect type of answer.',
            status=HTTPStatus.NOT_FOUND
        )

    user.solve(question, user_answer)
    if user_answer == question.answer:
        user.increase_score(question.reward)
        return Response(
            json.dumps(
                {
                    "question_id": question_id,
                    "result": "Correct",
                    "reward": question.reward
                }
            ),
            status=HTTPStatus.OK
        )

    user.increase_score(0)
    return Response(
        json.dumps(
            {
                "question_id": question_id,
                "result": "Incorrect",
                "reward": 0
            }
        ),
        status=HTTPStatus.OK
    )