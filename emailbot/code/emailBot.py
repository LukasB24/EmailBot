import os
from logger import Logger
from dotenv import load_dotenv
from accesstimeLogger import AccesstimeLogger
from time import sleep
import imaplib
import asyncio
from emailExtractor import EmailExtractor
import fileHandler

class EmailBot:
    def __init__(self) -> None:
        load_dotenv()
        self.__logger = Logger()
        self.__CHROMIUM_PATH = os.getenv("CHROMIUM_PATH")
        self.__BASE_PATH = os.getenv("TARGET_PATH")
        self.__APP_PW = os.getenv("APP_PW")
        self.__EMAIL = os.getenv("EMAIL")
        self.__MAIL_SERVER = os.getenv("MAIL_SERVER")
        self.__MAIL_PORT = 0
        self.__SENDER_EMAIL = os.getenv("SENDER_EMAIL")
        self.__SUBJECT = os.getenv("SUBJECT")
        self.__sleep_duration = 0
        self.__access_time_handler = AccesstimeLogger()

    def check_env_variables(self) -> str|None:
        exit_message = None

        if None in (self.__CHROMIUM_PATH, 
                    self.__BASE_PATH, 
                    self.__APP_PW, 
                    self.__EMAIL, 
                    self.__MAIL_SERVER, 
                    self.__MAIL_PORT, 
                    self.__SENDER_EMAIL, 
                    self.__SUBJECT):
            
            exit_message = "You need to initialize all variables in .env"
            return exit_message
            
        
        try:
            self.__MAIL_PORT = int(os.getenv("MAIL_PORT"))
            self.__sleep_duration = int(os.getenv("TIME_UNTIL_NEXT_CHECK")) * 86400
            self.__SENDER_EMAIL = self.__SENDER_EMAIL.lower()
            self.__SUBJECT = self.__SUBJECT.lower()
        except ValueError as ve:
            exit_message = f"Check datatypes of mail related env variables: {ve}"
        
        return exit_message
    
    def calculate_remaining_sleep_duration(self) -> float:
        last_log = self.__access_time_handler.get_last_log_time()
        sleep_duration = self.__sleep_duration

        if last_log is not None:
            time_passed_since_last_log = self.__access_time_handler.calculate_time_difference()
            sleep_duration -= time_passed_since_last_log
            sleep_duration = 0 if sleep_duration < 0 else sleep_duration
        else:
            sleep_duration = 0

        return sleep_duration

    
    def run(self) -> str|None:
        exit_message = self.check_env_variables() 

        if exit_message is not None:
            return exit_message
        
        remaining_sleep_duration = self.calculate_remaining_sleep_duration()

        if remaining_sleep_duration != 0:
            print("next check:   " + str(round(self.__sleep_duration / 60 / 60 / 24, 2)) + " days")
            sleep(remaining_sleep_duration)

        keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]

        while True:
            if not os.path.exists(self.__BASE_PATH):
                exit_message = "Base path to target directory does not exist"
                return exit_message

            try:
                email_extractor = EmailExtractor(self.__MAIL_SERVER, 
                                                 self.__MAIL_PORT, 
                                                 self.__EMAIL, 
                                                 self.__APP_PW, 
                                                 "inbox")
            except imaplib.IMAP4.error as e:
                exit_message = f"Something went wrong connecting to specified email server: {e}"
                return exit_message
            except TimeoutError as timeout:
                exit_message = f"{timeout}: check port in .env"
                return exit_message

            target_payloads = email_extractor.extract_payload_by_keyword(mail_criteria="UNSEEN", 
                                                                         target_subject=self.__SUBJECT, 
                                                                         payload_keyword="<!DOCTYPE html>", 
                                                                         email_sender=self.__SENDER_EMAIL)
            pdf_file = None

            if target_payloads is not None:
                for email in target_payloads:
                    try: 
                        pdf_file = asyncio.get_event_loop().run_until_complete(fileHandler.get_pdf_from_secmail(email, self.__CHROMIUM_PATH))
                    except Exception as e:
                        exit_message = str(e)
                        return exit_message

                    if pdf_file is None:
                        continue

                    matching_directory = fileHandler.store_file_based_on_keyword(pdf_file, keywords, self.__BASE_PATH)

                    if matching_directory is not None:
                        self.__logger.write_log(f'"{pdf_file}" successfully stored in "{matching_directory}"')
                
            self.__access_time_handler.log_time()
            print("next check:   " + str(round(self.__sleep_duration / 60 / 60 / 24, 2)) + " days")
            sleep(self.__sleep_duration)

