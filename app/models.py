import re

from app import USERS, EXPRESSIONS

from abc import ABC, abstractmethod

class User:

    def __init__(self, id, first_name, last_name, phone, email, score=0):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.score = score

    @staticmethod
    def is_valid_email(email):
        if re.match(r"[^@]+@+[^@]+\.+[^@]+", email):
            return True
        return False

    @staticmethod
    def is_valid_phone(phone):
        if re.match(r"^\+?[1-9][0-9]{7,14}$", phone):
            return True
        return False

    @staticmethod
    def is_valid_id(number):
        return number >= 0 and number < len(USERS)

    def increase_score(self, amount=1):
        self.score += amount


class Expression:

    def __init__(self, id, operation, *values, reward=None):
        self.id = id
        self.operation = operation
        self.values = values
        self.answer = self.__evaluate()
        if reward is None:
            reward = len(values) - 1
        self.reward = reward

    def __evaluate(self):
        return eval(self.to_string())

    @staticmethod
    def is_valid_id(number):
        return number >= 0 and number < len(EXPRESSIONS)

    def to_string(self):
        expr_str = "".join([(str(self.values[i]) + ' ' + self.operation + ' ') for i in range(len(self.values))])[:-3]
        return expr_str


class Question(ABC):

    def __init__(self, id, title, description, reward=None):
        self.id = id
        self.title = title
        self.description = description
        if reward is None:
            reward = 1
        self.reward = reward

    @property
    @abstractmethod
    def answer(self):
        pass

class OneAnswer(Question):

    def __init__(self, id, title, description, answer, reward=None):
        super().__init__(id, title, description, reward)
        if not self.is_valid(answer):
            answer = None
        self._answer = answer

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value: str):
        if not self.is_valid(value):
            self._answer = value

    @staticmethod
    def is_valid(answer):
        return isinstance(answer, str)

class MultipleChoice(Question):

    def __init__(self, id, title, description, answer: int, choices: list, reward=None):
        super().__init__(id, title, description, reward)
        if not self.is_valid(answer, choices):
            answer = None
            choices = None
        self._answer = answer
        self.choices = choices

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value: int):
        if self.is_valid(value, self.choices):
            self._answer = value

    @staticmethod
    def is_valid(answer, choices):
        if not isinstance(answer, int) or not isinstance(choices, list):
            return False
        return answer >= 0 and answer < len(choices)