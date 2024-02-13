import asyncio
from socket import gaierror
import sys
import os
from time import sleep
from dotenv import load_dotenv
from emailExtractor import EmailExtractor
from logger import Logger
import fileHandler

def mainloop():
    load_dotenv()
    logger = Logger(os.curdir + "/logs")
    BASE_PATH = os.getenv("TARGET_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 0
    SLEEP_DURATION = 0

    try:
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        SLEEP_DURATION = int(os.getenv("SLEEP_DURATION")) * 86400
    except ValueError as ve:
        logger.write_log(f"Check data type of mail related env variables: {ve}")
        sys.exit()

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
        sleep(SLEEP_DURATION)

if __name__ == "__main__":
    print("----------------\nStart monitoring\n----------------")
    mainloop()
