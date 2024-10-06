import os
import sqlite3 as sq
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from GetTest import get_test

load_dotenv()

CODE = os.getenv('CODE')
SAFE_DATA_IN_ACCOUNT = True
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

browser = webdriver.Chrome()
browser.get('https://quizizz.com/join')
con = None
wait_long = WebDriverWait(browser, 600)
wait_short = WebDriverWait(browser, 15)

try:
    con = sq.connect('questions.db')
    cursor = con.cursor()
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

    generate_name_but = wait_long.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="player-name-generator-icon"]'))
    )
    generate_name_but.click()
    start_game_but = wait_long.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="start-game primary-button"]'))
    )
    start_game_but.click()

    wait_long.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.total-questions'))
    )

    flag_1 = True
    while True:
        try:
            if flag_1:
                WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.total-questions'))
                )
            buff = wait_long.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div.resizeable.gap-x-2.question-text-color.text-light'))
            )
            buff = buff.text
            try:
                image_question = browser.find_element(By.CSS_SELECTOR, '.question-image').get_attribute('src')
                question = [buff, image_question]
            except NoSuchElementException:
                question = buff
        except TimeoutException:
            try:
                qwq = wait_short.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'button.selector.strip-default-btn-style.selector-item'))
                )
                browser.execute_script("arguments[0].click();", qwq)
                flag_1 = False
                continue
            except TimeoutException:
                break
        ans = wait_short.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bpl-container.th-black.option-inner"))
        )
        time.sleep(0.65)
        browser.execute_script("arguments[0].click();", ans)
        try:
            browser.find_element(By.CSS_SELECTOR,
                                 '[class="msq-text flex justify-center items-center w-full font-semibold text-lg text-light-66% mb-2"]')
            next_but = wait_short.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="submit-button exp-subtext"]'))
            )
            next_but.click()
        except NoSuchElementException:
            pass
        answers_obj = wait_short.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.is-correct'))
        )
        if flag_1:
            answers = []
            for ans in answers_obj:
                try:
                    image_answer = ans.find_element(By.CSS_SELECTOR, '.option-image.object-contain').get_attribute('style')
                    buff = [ans.text, image_answer]
                except NoSuchElementException:
                    buff = [ans.text]
                answers.append(str(buff))
            answers = list(dict.fromkeys(answers))
            answers = str(answers).replace("\\'", "'")
            cursor.execute("SELECT Question, Answer FROM Questions WHERE Question = ? AND Answer = ?", (str(question), str(answers)))
            try:
                cursor.fetchone()[0]
            except TypeError:
                cursor.execute("INSERT INTO Questions VALUES(NULL, ?, ?)", (str(question), str(answers)))
                con.commit()
        wait_long.until((EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.transition-timer-container'))))
        flag_1 = True

except sq.Error:
    if con:
        con.rollback()
finally:
    browser.quit()
    if con:
        con.close()

get_test(CODE, SAFE_DATA_IN_ACCOUNT, EMAIL, PASSWORD)
