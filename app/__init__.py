__all__ = ("app",)

from flask import Flask

app = Flask(__name__)

USERS = list()
EXPRESSIONS = list()
QUESTIONS = list()

from app import views_all
from app import models
from app import views