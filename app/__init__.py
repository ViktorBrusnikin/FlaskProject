__all__ = ("app",)

from flask import Flask

app = Flask(__name__)

USERS = list()
EXPRESSIONS = list()


from app import views
from app import models