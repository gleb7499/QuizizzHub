import sqlite3 as sq


class Database:
    _instance: 'Database' = None
    CLEAR: bool = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, CLEAR_IT: bool = False):
        self._connector = sq.connect("../Data/Questions.db")
        self._cursor = self._connector.cursor()
        if CLEAR_IT:
            self._cursor.execute("DROP TABLE IF EXISTS Questions")
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS Questions (
                        QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Question TEXT,
                        Answer TEXT
                        )""")

    def find_question(self, question: str, answers: str) -> tuple:
        self._cursor.execute("SELECT * FROM Questions WHERE Question = ? AND Answer = ?", (question, answers))
        return self._cursor.fetchone()

    def add_question(self, question: str, answers: str) -> None:
        if self.find_question(question, answers):
            return
        self._cursor.execute("INSERT INTO Questions (Question, Answer) VALUES (?, ?)", (question, answers))
        self._connector.commit()

    def get_answer(self, question: str) -> str:
        self._cursor.execute("SELECT Answer FROM Questions WHERE Question = ?", (question,))
        return self._cursor.fetchone()[0]

    def __del__(self):
        if self._connector:
            self._connector.close()
