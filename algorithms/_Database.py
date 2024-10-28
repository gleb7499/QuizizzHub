import sqlite3 as sq


class _Database:
    _instance: '_Database' = None
    CLEAR: bool = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, CLEAR_IT: bool = False):
        try:
            self._connector = sq.connect("../Data/Questions.db")
            self._cursor = self._connector.cursor()
            if CLEAR_IT:
                self._cursor.execute("DROP TABLE IF EXISTS Questions")
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Questions (
                            QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Question TEXT,
                            Answer TEXT
                            )""")
        except sq.Error:
            if self._connector:
                self._connector.rollback()

    def find_question(self, question: str, answers: str) -> tuple:
        try:
            self._cursor.execute("SELECT * FROM Questions WHERE Question = ? AND Answer = ?", (question, answers))
            return self._cursor.fetchone()
        except sq.Error:
            if self._connector:
                self._connector.rollback()

    def add_question(self, question: str, answers: str) -> None:
        if self.find_question(question, answers):
            return
        try:
            self._cursor.execute("INSERT INTO Questions (Question, Answer) VALUES (?, ?)", (question, answers))
            self._connector.commit()
        except sq.Error:
            if self._connector:
                self._connector.rollback()

    def get_answer(self, question: str) -> str:
        try:
            self._cursor.execute("SELECT Answer FROM Questions WHERE Question = ?", (question,))
            return self._cursor.fetchone()[0]
        except sq.Error:
            if self._connector:
                self._connector.rollback()

    def __del__(self):
        if self._connector:
            self._connector.close()
