import os

from dotenv import load_dotenv

from algorithms.GetAnswers import GetAnswers

if __name__ == '__main__':
    load_dotenv()

    CODE = os.getenv('CODE')
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    SAFE_DATA_IN_ACCOUNT = True

    quizizz = GetAnswers()
    quizizz.doAnswers(CODE=CODE)
