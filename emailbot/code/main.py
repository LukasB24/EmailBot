import asyncio
import imaplib
import os
import platform
from time import sleep
from dotenv import load_dotenv
from accesstimeLogger import AccesstimeLogger
from emailExtractor import EmailExtractor
from logger import Logger
import fileHandler
import ui


def mainloop():
    load_dotenv()
    logger = Logger()
    CHROME_PATH = os.getenv("CHROME_PATH")
    BASE_PATH = os.getenv("TARGET_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 0
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SUBJECT = os.getenv("SUBJECT")

    sleep_duration = 0
    default_sleep_duration = 0
    exit_message = ""

    if None in (CHROME_PATH, BASE_PATH, APP_PW, EMAIL, MAIL_SERVER, MAIL_PORT, SENDER_EMAIL, SUBJECT):
        exit_message = "You need to initialize all variables in .env"
        return exit_message

    try:
        MAIL_PORT = int(os.getenv("MAIL_PORT"))
        sleep_duration = int(os.getenv("TIME_UNTIL_NEXT_CHECK")) * 86400
        SENDER_EMAIL = SENDER_EMAIL.lower()
        SUBJECT = SUBJECT.lower()
        default_sleep_duration = sleep_duration

    except ValueError as ve:
        exit_message = f"Check datatypes of mail related env variables: {ve}"
        return exit_message

    access_time_handler = AccesstimeLogger()
    last_log = access_time_handler.get_last_log_time()

    if last_log != None:
        time_passed_since_last_log = access_time_handler.calculate_time_difference()
        sleep_duration -= time_passed_since_last_log
        sleep_duration = 0 if sleep_duration < 0 else sleep_duration
        
        if sleep_duration != 0:
            print("next check:   " + str(round(sleep_duration / 60 / 60 / 24, 2)) + " days")
            sleep(sleep_duration)

    keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]

    while True:
        if not os.path.exists(BASE_PATH):
            exit_message = "Base path to target directory does not exist"
            return exit_message

        try:
            email_extractor = EmailExtractor(MAIL_SERVER, MAIL_PORT, EMAIL, APP_PW, "inbox")
        except imaplib.IMAP4.error as e:
            exit_message = f"Something went wrong connecting to specified email server: {e}"
            return exit_message
        except TimeoutError as timeout:
            exit_message = f"{timeout}: check port in .env"
            return exit_message

        target_payloads = email_extractor.extract_payload_by_keyword(mail_criteria="UNSEEN", 
                                                                   target_subject=SUBJECT, 
                                                                   payload_keyword="<!DOCTYPE html>", 
                                                                   email_sender=SENDER_EMAIL)
        pdf_file = None

        if target_payloads is not None:
            for email in target_payloads:
                try: 
                    pdf_file = asyncio.get_event_loop().run_until_complete(fileHandler.get_pdf_from_secmail(email, CHROME_PATH))
                except Exception as e:
                    exit_message = str(e)
                    return exit_message

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
    logger = Logger(os.curdir + "/logs")
    ui.display("initialize", ui.StateType.INFO)
    sleep(30)

    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')

    try:
        ui.display("active", ui.StateType.POSITIV)
        error_message = mainloop()

        if error_message != "":
            ui.displayExitScreenAndExit(error_message)
            logger.write_log(error_message)
    except Exception as e:
        logger.write_log("Unhandled exception occured: " + str(e))

