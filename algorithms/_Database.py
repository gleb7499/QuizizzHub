import logging
import sqlite3 as sq
import os


class _Database:
    _instance: '_Database' = None
    CLEAR: bool = True

    def __new__(cls, CLEAR_IT: bool = False):
        if cls._instance is None:
            cls._instance = super(_Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, CLEAR_IT: bool = False):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Questions.db")
            self._connector = sq.connect(db_path)
            self._cursor = self._connector.cursor()
            if CLEAR_IT:
                self._cursor.execute("DROP TABLE IF EXISTS Questions")
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Questions (
                            QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Question TEXT,
                            Answer TEXT
                            )""")
            self._setup_logging()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            logging.error(f"Ошибка при инициализации базы данных - {e}")

    def find_question(self, question: str, answers: str) -> tuple:
        try:
            self._cursor.execute("SELECT * FROM Questions WHERE Question = ? AND Answer = ?", (question, answers))
            return self._cursor.fetchone()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            logging.error(f"Ошибка при поиске вопроса - {e}")

    def add_question(self, question: str, answers: str) -> None:
        if self.find_question(question, answers) is not None:
            return
        try:
            self._cursor.execute("INSERT INTO Questions (Question, Answer) VALUES (?, ?)", (question, answers))
            self._connector.commit()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            logging.error(f"Ошибка при добавлении вопроса - {e}")

    def get_answer(self, question: str) -> str:
        try:
            self._cursor.execute("SELECT Answer FROM Questions WHERE Question = ?", (question,))
            return self._cursor.fetchone()[0]
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            logging.error(f"Ошибка при получении ответа - {e}")

    def __del__(self):
        if self._connector:
            self._connector.close()

    @staticmethod
    def _setup_logging() -> None:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logFile", "app.log")
        logging.basicConfig(
            filename=log_path,
            encoding='utf-8',
            level=logging.INFO,
            format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%M:%S'
        )
