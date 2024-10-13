import logging
import sqlite3 as sq
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PassTest:
    def __init__(self):
        # Инициализация драйвера
        self._browser = webdriver.Chrome()
        self._browser.get('https://quizizz.com/join')
        self._wait_long = WebDriverWait(self._browser, 600)
        self._wait_short = WebDriverWait(self._browser, 15)
        self._wait_quite_short = WebDriverWait(self._browser, 0.1)
        # Инициализация БД
        self._connector = sq.connect("../Data/Questions.db")
        self._cursor = self._connector.cursor()

    @staticmethod
    def _setup_logging():
        logging.basicConfig(
            filename='../logFile/app.log',
            encoding='utf-8',
            level=logging.INFO,
            format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%M:%S'
        )
        logging.info('\n\t\t\t***Начала логирования PassTest***\n')

    def pass_test(self, CODE, EMAIL=None, PASSWORD=None):
        PassTest._setup_logging()
        try:
            # Вход в аккаунт, если это нужно
            if EMAIL is not None and PASSWORD is not None:
                self._log_in_account(EMAIL, PASSWORD)

            # Ввести код и нажать Join
            input_and_button = self._wait_long.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[id="proceed-game-action-wrapper"]'))
            )
            input_code = input_and_button.find_element(By.CSS_SELECTOR, 'input')
            input_code.send_keys(CODE)
            input_and_button.find_element(By.CSS_SELECTOR, 'button').click()

            # Кнопка генерации имени, если не нужен вход в аккаунт
            if EMAIL is None and PASSWORD is None:
                generate_name_but = self._wait_long.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '[class="player-name-generator-icon hover:cursor-pointer"]'))
                )
                generate_name_but.click()

            # Кнопка начала игры
            start_game_but = self._wait_long.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[class="start-game hover:cursor-pointer primary-button"]'))
            )
            start_game_but.click()

            # Общее количество вопросов
            total_question_number = int(self._wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[role="total-question-number"]'))).text)

            i = 1
            while i <= total_question_number:
                logging.info(f'Итерация -> {i}')
                try:
                    while True:
                        try:
                            logging.info('Поиск и сравнение номера вопроса')
                            self._wait_quite_short.until(
                                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '[role="current-question-number"]'),
                                                                 str(i)))
                            logging.info('***Номер вопроса найден***')
                            break
                        except TimeoutException:
                            logging.info('Продолжается поиск номера вопроса...')
                            pass

                    logging.info('Ожидание объекта с вопросом')
                    question_obj = self._wait_short.until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, '[class="resizeable gap-x-2 question-text-color text-light font-bold"]'))
                    )
                    logging.info('Объект с вопросами получен')
                    question_text = question_obj.text
                    logging.info(f'Вопрос -> {question_text}')
                    try:
                        logging.info('Начало поиска изображения в вопросе')
                        question_image = self._browser.find_element(By.CSS_SELECTOR, '.question-image').get_attribute(
                            'src')
                        logging.info('Фото в вопросе обнаружено')
                        question = [question_text, question_image]
                    except NoSuchElementException:
                        logging.info('Фото в вопросе нет')
                        question = question_text

                    logging.info('Запрос к базе данных')
                    self._cursor.execute("SELECT Answer FROM Questions WHERE Question = ?", (str(question),))
                    answer_db = self._cursor.fetchone()[0]
                    logging.info(f'Ответ от бд получен -> {answer_db}')
                    logging.info('Начало ожидания массива ответов, доступных на странице')
                    choices = self._wait_short.until(
                        EC.visibility_of_all_elements_located(
                            (By.CSS_SELECTOR, '[class="bpl-content-container w-full"]'))
                    )
                    logging.info('Объекты вариантов ответов получены')
                    for choice in choices:
                        # Поиск ответа
                        try:
                            text_choice = choice.find_element(By.CSS_SELECTOR, '.resizeable.gap-x-2').text
                        except NoSuchElementException:
                            text_choice = ''
                        try:
                            image_answer = choice.find_element(By.CSS_SELECTOR,
                                                               '.option-image.object-contain').get_attribute('style')
                            answer = [text_choice, image_answer]
                        except NoSuchElementException:
                            answer = [text_choice]
                        answer = str(answer)
                        logging.info(f'Текущий кандидат на ответ со страницы -> {answer}')
                        if answer in answer_db:
                            logging.info(f'Выбран ответ {answer}')
                            self._browser.execute_script("arguments[0].click();", choice)
                except TimeoutException:
                    break
                try:
                    ok_button = self._browser.find_element(By.CSS_SELECTOR,
                                                           '[class="show-tooltip cursor-pointer default"]')
                    ok_button.find_element(By.CSS_SELECTOR, 'button').click()
                except NoSuchElementException:
                    pass
                i = i + 1

            # Периодически проверять открыт ли браузер во время спячки кода
            check_interval = 3
            while True:
                time.sleep(check_interval)
                try:
                    self._browser.title
                except:
                    logging.info('Браузер закрыт пользователем')
                    break

        except sq.Error:
            if self._connector:
                self._connector.rollback()
        finally:
            self._browser.quit()
            if self._connector:
                self._connector.close()

    def _log_in_account(self, EMAIL, PASSWORD):
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class="min-w-30 w-full"]'))
        )
        self._browser.execute_script("arguments[0].click();", log_in)
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class="login-button"]'))
        )
        self._browser.execute_script("arguments[0].click();", log_in)
        log_in = self._wait_short.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 '[class="text-sm md:text-base rounded w-full flex justify-between items-center py-2 px-4 shadow-sm border border-light-1 hover:shadow-md"]'))
        )
        self._browser.execute_script("arguments[0].click();", log_in[1])
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email-field-input"]'))
        )
        log_in.send_keys(EMAIL)
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '[class="transition-colors duration-200 ease-in-out flex flex items-center justify-center px-4 py-1 text-sm font-semibold h-8 base bg-lilac text-light-3 hover:bg-lilac-light active:bg-lilac-dark rounded primary relative min-w-max w-full w-full"]'))
        )
        self._browser.execute_script("arguments[0].click();", log_in)
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="password-field-input"]'))
        )
        log_in.send_keys(PASSWORD)
        log_in = self._wait_short.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '[class="transition-colors duration-200 ease-in-out flex flex items-center justify-center px-4 py-1 text-sm font-semibold h-8 base bg-lilac text-light-3 hover:bg-lilac-light active:bg-lilac-dark rounded primary relative min-w-max w-full w-full"]'))
        )
        self._browser.execute_script("arguments[0].click();", log_in)
