from algorithms._PassTest import _PassTest
from algorithms._GetAnswers import _GetAnswers
from algorithms._Database import _Database


class QuizizzHub:
    def __init__(self, CLEAR_DB: bool = False):
        database = _Database(CLEAR_DB)
        self._get_answers = _GetAnswers(database=database)
        self._pass_test = _PassTest(database=database)

    def get_answers(self, CODE: str = None) -> None:
        self._get_answers.get_answers(CODE=CODE)

    def pass_test(self, wrong: int, CODE: int, EMAIL: str = None, PASSWORD: str = None) -> None:
        try:
            self._pass_test.pass_test(wrong=wrong, CODE=CODE, EMAIL=EMAIL, PASSWORD=PASSWORD)
        except ValueError as e:
            raise e
