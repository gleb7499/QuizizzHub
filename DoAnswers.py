import logging
import sqlite3 as sq
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_logging():
    # Очищаем файл перед началом логирования
    with open('app.log', 'w'):
        pass

    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%M:%S'
    )


def doAnswers(CODE):

    setup_logging()

    browser = webdriver.Chrome()
    browser.get('https://quizizz.com/join')
    con = None
    wait_long = WebDriverWait(browser, 600)
    wait_short = WebDriverWait(browser, 15)

    try:
        con = sq.connect('questions.db')
        cursor = con.cursor()
        cursor.execute("DROP TABLE IF EXISTS Questions")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Questions (
            QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
            Question TEXT,
            Answer TEXT
            )""")

        # Ввести код и нажать Join
        input_and_button = wait_long.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[id="proceed-game-action-wrapper"]'))
        )
        input_code = input_and_button.find_element(By.CSS_SELECTOR, 'input')
        input_code.send_keys(CODE)
        input_and_button.find_element(By.CSS_SELECTOR, 'button').click()
        logging.info('input_and_button завершено')

        # Кнопка генерации имени
        generate_name_but = wait_long.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="player-name-generator-icon hover:cursor-pointer"]'))
        )
        generate_name_but.click()
        logging.info('Кнопка генерации имени нажата')

        # Кнопка начала игры
        start_game_but = wait_long.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="start-game hover:cursor-pointer primary-button"]'))
        )
        start_game_but.click()
        logging.info('Кнопка начала игры нажата')

        # Ожидание появления верхнего левого объекта
        wait_long.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="absolute h-4 w-auto left-1 right-1 border-t-[0.5px] rounded-md top-1 border-ds-light-500-50 border-gradient-to-b"]'))
        )
        logging.info('Верхний левый объект появился\n')

        flag = True
        while True:
            logging.info('Начало цикла')
            try:
                if flag:
                    # Ожидание появление вопроса
                    logging.info('Начало ожидания вопроса')
                    question_text = WebDriverWait(browser, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="resizeable gap-x-2 question-text-color text-light font-bold"]'))
                    )
                    logging.info('Вопрос появился')
                    question_text = question_text.text
                    logging.info(f'Текст вопроса получен -> {question_text}')
                    try:
                        question_image = browser.find_element(By.CSS_SELECTOR, '.question-image').get_attribute('src')
                        logging.info('Изображение в вопросе есть')
                        question = [question_text, question_image]
                    except NoSuchElementException:
                        question = question_text
                        logging.info('Изображения в вопросе отсутствует')
            except TimeoutException:
                logging.info('Обнаружена страница с повторным вопросом')
                # Значит это страница с повторным вопросом
                try:
                    logging.info('Начало ожидания кнопки выбора номера повторения вопроса')
                    repeat_question_button = wait_short.until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, 'button.selector.strip-default-btn-style.selector-item'))
                    )
                    logging.info('Кнопка выбора номера повторения вопроса обнаружена')
                    browser.execute_script("arguments[0].click();", repeat_question_button)
                    logging.info('Кнопка выбора номера повторения вопроса нажата')
                    flag = False
                    continue
                except TimeoutException:
                    logging.info('Тест закончен')
                    # Значит тест окончен
                    break
            # Первая кнопка с ответом
            logging.info('Начало ожидания первой кнопки с ответом')
            ans_butt = wait_short.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bpl-container.th-black.option-inner"))
            )
            logging.info('Первая кнопка с ответом обнаружена')
            time.sleep(0.65)
            browser.execute_script("arguments[0].click();", ans_butt)
            logging.info('Первая кнопка с ответом нажата')
            # Поиск кнопки при выборе нескольких вариантов ответа
            try:
                next_but = browser.find_element(By.CSS_SELECTOR, '[class="show-tooltip cursor-pointer default"]')
                logging.info('Кнопка при выборе нескольких вариантов ответа обнаружена')
                next_but.find_element(By.CSS_SELECTOR, 'button').click()
                logging.info('Кнопка при выборе нескольких вариантов ответа нажата')
            except NoSuchElementException:
                logging.info('Только один вариант ответа')
                pass
            if flag:
                logging.info('Начало ожидания объектов с ответами')
                answers_obj = wait_short.until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.is-correct'))
                )
                logging.info('Объекты с ответами обнаружены')
                answers = []
                for ans in answers_obj:
                    # Изображения в ответах
                    try:
                        image_answer = ans.find_element(By.CSS_SELECTOR, '.option-image.object-contain').get_attribute('style')
                        logging.info('Изображение в ответе обнаружено')
                        question_text = [ans.text, image_answer]
                    except NoSuchElementException:
                        logging.info('Изображений в ответе нет')
                        question_text = [ans.text]
                    answers.append(str(question_text))
                answers = list(dict.fromkeys(answers))
                answers = str(answers).replace("\\'", "'")
                question = str(question)
                logging.info(f'Вопрос -> {question}, Ответ -> {answers}')
                # Поиск повторений в базе данных
                cursor.execute("SELECT Question, Answer FROM Questions WHERE Question = ? AND Answer = ?", (question, answers))
                try:
                    cursor.fetchone()[0]
                    logging.info('Обнаружена повторка')
                except TypeError:
                    cursor.execute("INSERT INTO Questions VALUES(NULL, ?, ?)", (question, answers))
                    con.commit()
                    logging.info('Вопрос и ответ внесены в БД')
            # Ожидание ухода объекта, после которого можно продолжать цикл
            logging.info('Начало ожидания исчезновения объекта div.transition-timer-container')
            wait_long.until((EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.transition-timer-container'))))
            logging.info('Объект div.transition-timer-container исчез')
            flag = True

    except sq.Error:
        if con:
            con.rollback()
    finally:
        browser.quit()
        if con:
            con.close()
