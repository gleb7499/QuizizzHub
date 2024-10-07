import logging
import sqlite3 as sq

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class GetAnswers:
    def __init__(self):
        # Инициализация драйвера
        self._browser = webdriver.Chrome()
        self._browser.get('https://quizizz.com/join')
        self._wait_long = WebDriverWait(self._browser, 600)
        self._wait_short = WebDriverWait(self._browser, 15)
        self._wait_quite_short = WebDriverWait(self._browser, 0.1)
        # Инициализация БД
        self._connector = sq.connect("Data/Questions.db")
        self._cursor = self._connector.cursor()
        self._cursor.execute("DROP TABLE IF EXISTS Questions")
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS Questions (
                        QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Question TEXT,
                        Answer TEXT
                        )""")

    @staticmethod
    def _setup_logging():
        # Очищаем файл перед началом логирования
        with open('../app.log', 'w'):
            pass

        logging.basicConfig(
            filename='../app.log',
            level=logging.INFO,
            format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%M:%S'
        )

    def doAnswers(self, CODE):
        GetAnswers._setup_logging()
        try:
            # Ввести код и нажать Join
            input_and_button = self._wait_long.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[id="proceed-game-action-wrapper"]'))
            )
            input_code = input_and_button.find_element(By.CSS_SELECTOR, 'input')
            input_code.send_keys(CODE)
            input_and_button.find_element(By.CSS_SELECTOR, 'button').click()
            logging.info('input_and_button завершено')

            # Кнопка генерации имени
            generate_name_but = self._wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="player-name-generator-icon hover:cursor-pointer"]'))
            )
            generate_name_but.click()
            logging.info('Кнопка генерации имени нажата')

            # Кнопка начала игры
            start_game_but = self._wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="start-game hover:cursor-pointer primary-button"]'))
            )
            start_game_but.click()
            logging.info('Кнопка начала игры нажата')

            # Общее количество вопросов
            total_question_number = int(self._wait_long.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[role="total-question-number"]'))).text)
            logging.info(f'Всего вопросов -> {total_question_number}')

            flag = True
            i = 1
            while i <= total_question_number:
                logging.info(f'Начало цикла -> {i}')
                while True:
                    try:
                        logging.info("\t\tПоиск текущего вопроса")
                        self._wait_quite_short.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '[role="current-question-number"]'), str(i)))
                        logging.info("\t\t***Обнаружен новый вопрос***")
                        question = self._new_question()
                        break
                    except TimeoutException:
                        try:
                            self._wait_quite_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.selector.strip-default-btn-style.selector-item")))
                            logging.info("\t\t\tОбнаружен повторный вопрос")
                            self._repeat_question()
                            flag = False
                            break
                        except TimeoutException:
                            pass
                # Первая кнопка с ответом
                logging.info('Начало ожидания первой кнопки с ответом')
                ans_butt = self._wait_short.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bpl-container.th-black.option-inner"))
                )
                logging.info('Первая кнопка с ответом обнаружена')
                self._browser.execute_script("arguments[0].click();", ans_butt)
                logging.info('Первая кнопка с ответом нажата')
                # Поиск кнопки при выборе нескольких вариантов ответа
                try:
                    ok_button = self._browser.find_element(By.CSS_SELECTOR, '[class="show-tooltip cursor-pointer default"]')
                    logging.info('Кнопка при выборе нескольких вариантов ответа обнаружена')
                    ok_button.find_element(By.CSS_SELECTOR, 'button').click()
                    logging.info('Кнопка при выборе нескольких вариантов ответа нажата')
                except NoSuchElementException:
                    logging.info('Только один вариант ответа')
                    pass
                if flag:
                    logging.info('Начало ожидания объектов с ответами')
                    answers_obj = self._wait_short.until(
                        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.is-correct'))
                    )
                    logging.info('Объекты с ответами обнаружены')
                    answers = []
                    for ans in answers_obj:
                        # Изображения в ответах
                        try:
                            image_answer = ans.find_element(By.CSS_SELECTOR, '.option-image.object-contain').get_attribute('style')
                            logging.info('Изображение в ответе обнаружено')
                            answer = [ans.text, image_answer]
                        except NoSuchElementException:
                            logging.info('Изображений в ответе нет')
                            answer = [ans.text]
                        answers.append(str(answer))
                    answers = list(dict.fromkeys(answers))
                    answers = str(answers).replace("\\'", "'")
                    question = str(question)
                    logging.info(f'Вопрос -> {question}, Ответ -> {answers}')
                    # Поиск повторений в базе данных
                    self._cursor.execute("SELECT Question, Answer FROM Questions WHERE Question = ? AND Answer = ?", (question, answers))
                    try:
                        self._cursor.fetchone()[0]
                        logging.info('Обнаружена повторка')
                    except TypeError:
                        self._cursor.execute("INSERT INTO Questions VALUES(NULL, ?, ?)", (question, answers))
                        self._connector.commit()
                        logging.info('Вопрос и ответ внесены в БД')
                    i = i + 1
                flag = True

            logging.info('Тест закончен')

        except sq.Error:
            if self._connector:
                self._connector.rollback()
        finally:
            self._browser.quit()
            if self._connector:
                self._connector.close()

    def _new_question(self):
        # Ожидание появление вопроса
        logging.info('Начало ожидания вопроса')
        question_obj = self._wait_short.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[class="resizeable gap-x-2 question-text-color text-light font-bold"]')))
        logging.info('Вопрос появился')
        question_text = question_obj.text
        logging.info(f'Текст вопроса получен -> {question_text}')
        try:
            question_image = self._browser.find_element(By.CSS_SELECTOR, '.question-image').get_attribute('src')
            logging.info('Изображение в вопросе есть')
            question = [question_text, question_image]
        except NoSuchElementException:
            question = question_text
            logging.info('Изображения в вопросе отсутствует')
        return question

    def _repeat_question(self):
        logging.info('Обнаружена страница с повторным вопросом')
        # Значит это страница с повторным вопросом
        logging.info('Начало ожидания кнопки выбора номера повторения вопроса')
        repeat_question_button = self._wait_short.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'button.selector.strip-default-btn-style.selector-item'))
        )
        logging.info('Кнопка выбора номера повторения вопроса обнаружена')
        self._browser.execute_script("arguments[0].click();", repeat_question_button)
        logging.info('Кнопка выбора номера повторения вопроса нажата')
