import asyncio
import sys
import os
import re
import shutil
from time import sleep
from dotenv import load_dotenv
import requests
from pyppeteer import launch
from pyppeteer.errors import PageError
from emailExtractor import EmailExtractor
from pdfScraper import PDFScraper
from logger import Logger

async def get_pdf(email_content: str) -> str:
    """Fetches pdf from secmail email"""
    logger = Logger()

    try:
        target_file = ""
        browser = await launch(executablePath="/usr/bin/chromium")
        page = await browser.newPage()
        await page.setContent(email_content)
        open_email_button = await page.querySelector("button")
        await open_email_button.click()
        await asyncio.sleep(10)
        password_field = await page.querySelector("#loginform > div:nth-child(2) > input")
        await password_field.type(os.getenv("SECPASS"))
        login_submit_button = await page.querySelector("#loginform > div.d-flex.flex-row.justify-content-between > div:nth-child(2) > input")
        await login_submit_button.click()
        await asyncio.sleep(10)
        await page.waitForSelector("#content > div > div > div > ul > li > a")
        download_pdf_link = await page.querySelector("#content > div > div > div > ul > li > a")

        if download_pdf_link:
            try:
                pdf_url = await page.evaluate("(element) => element.href", download_pdf_link)
                response = requests.get(pdf_url, timeout=15)
                headers = response.headers
                if "Content-Disposition" in headers:
                    filename = re.search("filename=([^\s]+)\.", headers["Content-Disposition"]).group(1)
                    target_file = f"{filename}.pdf"

                    with open(target_file, "wb") as f:
                        f.write(response.content)

            except PageError as e:
                logger.write_log(f"Exception occured while accessing pdf link: {e}")

        await browser.close()
        return target_file
    except Exception as e:
        logger.write_log(f"Exception occurred during proccessing website elements: {e}")


def store_file_based_on_keyword(filename: str, words: list[str], base_path: str) -> str | None:
    """Stores file in matching directory"""
    logger = Logger()

    if filename == "":
        logger.write_log("No pdf file provided")
        return
    
    matched_keyword = PDFScraper(filename).search_pdf_for_words(words)

    path = None
    match matched_keyword:
        case "Zeitnachweisliste":
            path = f"{base_path}/Zeitnachweise"
        case "Lohnsteuerbescheinigung":
            path = f"{base_path}/Lohnsteuerbescheinigungen"
        case "Entgeltabrechnung":
            path = f"{base_path}/Gehaltsabrechnungen"

    if path is None:
        logger.write_log("Failed to find keyword in pdf file")
        return None
    
    if not os.path.exists(path):
        os.mkdir(path)
    
    try:
        shutil.move(filename, path)
        return path
    except shutil.Error as e:
        logger.write_log(str(e))

        if os.path.exists(f"{path}/{filename}"):
            os.remove(filename)
    

if __name__ == "__main__":
    load_dotenv()
    BASE_PATH = os.getenv("TARGET_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    GMAIL_SERVER = "imap.gmail.com"
    GMAIL_PORT = 993
    keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]
    logger = Logger(os.curdir + "/logs")
    RUNNING_MODE = os.getenv("RUNNING_MODE")
    SLEEP_TIME = 604800 # Sleep for one week

    if RUNNING_MODE == "pc":
        SLEEP_TIME = 7200

    print("----------------\nStart monitoring\n----------------")

    while True:
        if not os.path.exists(BASE_PATH):
            logger.write_log("Base path does not exist")
            sys.exit(1)

        email_extractor = EmailExtractor(GMAIL_SERVER, GMAIL_PORT, EMAIL, APP_PW, "inbox")
        target_email = email_extractor.extract_and_decode_email_with_matching_keyword("UNSEEN", "secmaildata")
        pdf_file = ""

        if target_email is not None:
            pdf_file = asyncio.get_event_loop().run_until_complete(get_pdf(target_email))
            matching_directory = store_file_based_on_keyword(pdf_file, keywords, BASE_PATH)

            if matching_directory is not None:
                logger.write_log(f'"{pdf_file}" successfully stored in "{matching_directory}"')
        sleep(20)
