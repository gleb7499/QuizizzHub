from algorithms._PassTest import _PassTest
from algorithms._GetAnswers import _GetAnswers
from algorithms._Database import _Database


class QuizizzHub:
    SPEED_INSTANTLY = 0
    SPEED_FAST = 1
    SPEED_MEDIUM = 2
    SPEED_SLOW = 3

    def __init__(self):
        database = _Database()
        self._get_answers = _GetAnswers(database=database)
        self._pass_test = _PassTest(database=database)

    def get_answers(self, CODE: str = None) -> None:
        self._get_answers.get_answers(CODE=CODE)

    def pass_test(self, ratio: int, CODE: int, EMAIL: str = None, PASSWORD: str = None) -> None:
        try:
            self._pass_test.pass_test(ratio=ratio, CODE=CODE, EMAIL=EMAIL, PASSWORD=PASSWORD)
        except ValueError as e:
            raise e
