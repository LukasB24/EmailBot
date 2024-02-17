import asyncio
import datetime
import imaplib
import sys
import os
from time import sleep
from dotenv import load_dotenv
from accesstimeLogger import AccesstimeLogger
from emailExtractor import EmailExtractor
from logger import Logger
import fileHandler

def mainloop():
    load_dotenv()
    logger = Logger(os.curdir + "/logs")
    access_time_handler = AccesstimeLogger()
    CHROME_PATH = os.getenv("CHROME_PATH")
    BASE_PATH = os.getenv("TARGET_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 0
    sleep_duration = 0
    default_sleep_duration = 0

    try:
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        sleep_duration = int(os.getenv("TIME_UNTIL_NEXT_CHECK")) * 86400
        default_sleep_duration = sleep_duration

    except ValueError as ve:
        logger.write_log(f"Check datatypes of mail related env variables: {ve}")
        sys.exit()

    last_log = access_time_handler.get_last_log_time()

    if last_log != "":
        time_passed_since_last_log = access_time_handler.calculate_time_difference()
        sleep_duration -= time_passed_since_last_log
        sleep_duration = 0 if sleep_duration < 0 else sleep_duration
        print("next check:   " + str(round(sleep_duration / 60 / 60 / 24, 2)) + " days")
        sleep(sleep_duration)

    keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]

    while True:
        if not os.path.exists(BASE_PATH):
            message = "Base path to target directory does not exist"
            logger.write_log(message)
            print(message)
            sys.exit()

        try:
            email_extractor = EmailExtractor(MAIL_SERVER, MAIL_PORT, EMAIL, APP_PW, "inbox")
        except imaplib.IMAP4.error as e:
            message = f"Something went wrong connecting to specified email server: {e}"
            logger.write_log(message)
            print(message)
            sys.exit()
        except TimeoutError as timeout:
            message = f"{timeout}: check port in .env"
            logger.write_log(message)
            print(message)
            sys.exit()

        target_emails = email_extractor.extract_and_decode_email_with_matching_keyword("UNSEEN", "secmaildata")
        pdf_file = None

        if target_emails is not None:
            for email in target_emails:
                try: 
                    pdf_file = asyncio.get_event_loop().run_until_complete(fileHandler.get_pdf(email, CHROME_PATH))
                except os.error as e:
                    logger.write_log(str(e))
                    print(str(e))
                    sys.exit()

                if pdf_file is None:
                    continue

                matching_directory = fileHandler.store_file_based_on_keyword(pdf_file, keywords, BASE_PATH)

                if matching_directory is not None:
                    logger.write_log(f'"{pdf_file}" successfully stored in "{matching_directory}"')
            
        access_time_handler.log_time()
        sleep_duration = default_sleep_duration
        print("next check:   " + str(round(sleep_duration / 60 / 60 / 24, 2)) + " days")
        sleep(sleep_duration)

if __name__ == "__main__":
    print("------------------------\nEmail monitoring\n------------------------")
    print(str(datetime.datetime.now().ctime()) + "\n")
    print("status: " + "\033[32m      active\033[0m")
    mainloop()
