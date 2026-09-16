# QuizizzHub

QuizizzHub is a Python application for automating Quizizz test sessions. It collects questions and answers, then completes a test by selecting the corresponding answers.

## Overview

The project consists of modules that:

- collect questions and answers from Quizizz web pages;
- store collected data in a local database;
- join and complete a test by selecting answers automatically;
- log application activity for later analysis and troubleshooting.

## Features

- **Question and answer collection**
  `get_answers(CODE)` collects questions and correct answers from Quizizz using the unique quiz code provided by the instructor, then stores them in a local SQLite database.

- **Automated test completion**
  `pass_test(wrong, CODE, EMAIL, PASSWORD)` joins a quiz, selects answers, optionally allows a specified number of incorrect answers, and completes the session after processing all questions. If necessary, it signs in using the supplied email and password.

- **Logging**
  Application activity is written to a log file to make execution easier to monitor and debug.

## Installation and usage

### 1. Set up the environment

- Install Python (Python 3.12 is recommended) and Google Chrome.
- Install the required dependencies:

  ```bash
  pip install -r requirements.txt
  ```

- If dependency issues occur, try the extended requirements file:

  ```bash
  pip install -r requirements_full.txt
  ```

### 2. Run the application

Run `main.py` or use the class from your Python code:

```python
from algorithms.QuizizzHub import QuizizzHub

if __name__ == "__main__":
    CODE = "010649"  # Unique quiz code provided by the instructor
    EMAIL = "your_email@example.com"  # Optional Quizizz account email
    PASSWORD = "your_password"  # Optional Quizizz account password

    quizizz = QuizizzHub()
    quizizz.get_answers(CODE=CODE)
    quizizz.pass_test(wrong=0, CODE=CODE, EMAIL=EMAIL, PASSWORD=PASSWORD)
```

### 3. Monitor the process

When the application starts, a Chrome browser window opens. The program enters the quiz code, joins the session, waits for the test to begin, selects answers, records the results, and stores the collected information in the local database.

## Requirements

- **Python 3.12**
- **Google Chrome** for Selenium-based browser automation
- Libraries listed in `requirements.txt`, including:
  - `selenium`
  - `sqlite3` (included with Python)
  - `logging` (included with Python)
  - other project dependencies

## Notes and limitations

- The application handles repeated questions, multiple-answer options, and manual input scenarios.
- Quizizz gamification features, such as bonuses, are not supported. If one appears, select the required option manually.
- If the test does not continue, check whether the browser is waiting for input and intervene manually when necessary.

Use this tool only in accordance with the applicable Quizizz rules, course policies, and terms of service.

## License

This project is distributed under the **MIT License**. See [LICENSE.txt](LICENSE.txt) for the full license text.

## Author

Developed by **Gleb Olegovich Loginov**, an IT student and the author of this project.
