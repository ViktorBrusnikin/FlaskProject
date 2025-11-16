from app import app, USERS, QUESTIONS, EXPRESSIONS


@app.route("/")
def index():
    response = (
        "<h1>Hello, World!</h1>"
        f"Users: <br>{"<br>".join(user.repr() for user in USERS)}<br>"
        f"Questions: <br>{"<br>".join(question.repr() for question in QUESTIONS)}<br>"
        f"Expressions: <br>{"<br>".join(expression.repr() for expression in EXPRESSIONS)}<br>"
    )
    return response