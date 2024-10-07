import os

from dotenv import load_dotenv

from GetAnswers import GetAnswers
from PassTest import PassTest

if __name__ == '__main__':
    load_dotenv()

    CODE = os.getenv('CODE')
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    SAFE_DATA_IN_ACCOUNT = True

    answers = GetAnswers()
    answers.get_answers(CODE=CODE)

    test = PassTest()
    test.pass_test(CODE)
