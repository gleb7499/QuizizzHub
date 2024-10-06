import os

from dotenv import load_dotenv

from DoAnswers import doAnswers

if __name__ == '__main__':
    load_dotenv()

    CODE = os.getenv('CODE')
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    SAFE_DATA_IN_ACCOUNT = True

    doAnswers(CODE)
