import os

from dotenv import load_dotenv

from algorithms.QuizizzHub import QuizizzHub

if __name__ == '__main__':
    load_dotenv()

    CODE = os.getenv('CODE')
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')

    quizizz = QuizizzHub()

    quizizz.get_answers(CODE=CODE)

    quizizz.pass_test(wrong=QuizizzHub.SPEED_MEDIUM, CODE=CODE)
