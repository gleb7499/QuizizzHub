import sqlite3 as sq

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# сделать запуск теста после ответов вручную на случай ошибки


def get_test(CODE, SAFE_DATA_IN_ACCOUNT, EMAIL, PASSWORD):
    browser = webdriver.Chrome()
    browser.get('https://quizizz.com/join')
    con = None
    wait_long = WebDriverWait(browser, 600)
    wait_short = WebDriverWait(browser, 15)

    try:
        if SAFE_DATA_IN_ACCOUNT:
            con = sq.connect('questions.db')
            cursor = con.cursor()

            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="min-w-30 w-full"]'))
            )
            browser.execute_script("arguments[0].click();", log_in)
            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="login-button"]'))
            )
            browser.execute_script("arguments[0].click();", log_in)
            log_in = wait_short.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="text-sm md:text-base rounded w-full flex justify-between items-center py-2 px-4 shadow-sm border border-light-1 hover:shadow-md"]'))
            )
            browser.execute_script("arguments[0].click();", log_in[1])
            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[id="email-field-input"]'))
            )
            log_in.send_keys(EMAIL)
            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="transition-colors duration-200 ease-in-out flex flex items-center justify-center px-4 py-1 text-sm font-semibold h-8 base bg-lilac text-light-3 hover:bg-lilac-light active:bg-lilac-dark rounded primary relative min-w-max w-full w-full"]'))
            )
            browser.execute_script("arguments[0].click();", log_in)
            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[id="password-field-input"]'))
            )
            log_in.send_keys(PASSWORD)
            log_in = wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="transition-colors duration-200 ease-in-out flex flex items-center justify-center px-4 py-1 text-sm font-semibold h-8 base bg-lilac text-light-3 hover:bg-lilac-light active:bg-lilac-dark rounded primary relative min-w-max w-full w-full"]'))
            )
            browser.execute_script("arguments[0].click();", log_in)

        input_code = wait_long.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[class="check-room-input rounded-xl border-0 border-box landing"]'))
        )
        input_code.send_keys(CODE)
        browser.find_element(By.CSS_SELECTOR,
                             '[class="box-border text-unselectable font-bold border text-center disabled:text-ds-light-500-30 disabled:bg-ds-light-500-10 text-ds-light-500 bg-ds-lilac-500 border-transparent hover:bg-ds-lilac-400 hover:border-ds-lilac-400 active:bg-ds-lilac-600 active:border-ds-lilac-600 px-4 py-2 text-base xs:text-xl w-fit rounded-lg floatingButton mb-1 relative check-room-button"]').click()
        if SAFE_DATA_IN_ACCOUNT is False:
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

        while True:
            try:
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

                cursor.execute("SELECT Answer FROM Questions WHERE Question = ?", (str(question),))
                answers_db = cursor.fetchone()[0]
                choices = wait_short.until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.bpl-container.th-black.option-inner"))
                )
                for choice in choices:
                    try:
                        image_answer = choice.find_element(By.CSS_SELECTOR,
                                                           '.option-image.object-contain').get_attribute(
                            'style')
                        buff = [choice.text, image_answer]
                    except NoSuchElementException:
                        buff = [choice.text]
                    buff = str(buff)
                    if buff in answers_db:
                        browser.execute_script("arguments[0].click();", choice)
            except TimeoutException:
                break
            try:
                browser.find_element(By.CSS_SELECTOR,
                                     '[class="msq-text flex justify-center items-center w-full font-semibold text-lg text-light-66% mb-2"]')
                next_but = wait_short.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[class="submit-button exp-subtext"]'))
                )
                next_but.click()
            except NoSuchElementException:
                pass
            wait_short.until((EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.transition-timer-container'))))
            wait_long.until((EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.transition-timer-container'))))

    except sq.Error:
        if con:
            con.rollback()
    finally:
        browser.quit()
        if con:
            con.close()
