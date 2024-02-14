import asyncio
from socket import gaierror
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
    BASE_PATH = os.getenv("TARGET_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 0
    sleep_duration = 0
    default_sleep_duration = 0

    try:
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        sleep_duration = int(os.getenv("SLEEP_DURATION")) * 86400
        default_sleep_duration = sleep_duration

    except ValueError as ve:
        logger.write_log(f"Check data type of mail related env variables: {ve}")
        sys.exit()

    last_log = access_time_handler.get_last_log_time()

    if last_log != "":
        time_passed_since_last_log = access_time_handler.calculate_time_difference()
        sleep_duration -= time_passed_since_last_log
        sleep_duration = 0 if sleep_duration < 0 else sleep_duration
        sleep(sleep_duration)

    keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]

    while True:
        if not os.path.exists(BASE_PATH):
            logger.write_log("Base path does not exist")
            sys.exit()

        try:
            email_extractor = EmailExtractor(MAIL_SERVER, MAIL_PORT, EMAIL, APP_PW, "inbox")
        except gaierror:
            logger.write_log("Something went wrong connecting to specified email server. Check if values in .env are correct")
            sys.exit()

        target_email = email_extractor.extract_and_decode_email_with_matching_keyword("UNSEEN", "secmaildata")
        pdf_file = ""

        if target_email is not None:
            pdf_file = asyncio.get_event_loop().run_until_complete(fileHandler.get_pdf(target_email))
            matching_directory = fileHandler.store_file_based_on_keyword(pdf_file, keywords, BASE_PATH)

            if matching_directory is not None:
                logger.write_log(f'"{pdf_file}" successfully stored in "{matching_directory}"')
        
        access_time_handler.log_time()
        sleep_duration = default_sleep_duration
        sleep(sleep_duration)

if __name__ == "__main__":
    print("----------------\nStart monitoring\n----------------")
    mainloop()
