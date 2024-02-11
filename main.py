import asyncio
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

async def main(email_content: str, words: list[str], base_path: str):
    """Fetches pdf from secmail email"""
    try:
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
                    final_filename = f"{filename}.pdf"

                    with open(final_filename, "wb") as f:
                        f.write(response.content)

                    matched_keyword = PDFScraper(final_filename).search_pdf_for_words(words)
                    
                    match matched_keyword:
                        case "Zeitnachweisliste":
                            shutil.move(final_filename, f"{base_path}/Zeitnachweise")
                        case "Lohnsteuerbescheinigung":
                            shutil.move(final_filename, f"{base_path}/Lohnsteuerbescheinigungen")
                        case "Entgeltabrechnung":
                            shutil.move(final_filename, f"{base_path}/Gehaltsabrechnungen")
                            

            except PageError as e:
                print("Exception occured while accessing pdfLink", e)

        await asyncio.sleep(3)
        await browser.close()
    except Exception as e:
        print("Exception occurred during proccessing website elements: ", e)

if __name__ == "__main__":
    load_dotenv()
    BASE_PATH = os.getenv("BASE_PATH")
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    GMAIL_SERVER = "imap.gmail.com"
    GMAIL_PORT = 993
    running = True
    keywords = ["Zeitnachweisliste", "Lohnsteuerbescheinigung", "Entgeltabrechnung"]

    print("----------------\nStart monitoring\n----------------")

    while running:
        email_extractor = EmailExtractor(GMAIL_SERVER, GMAIL_PORT, EMAIL, APP_PW, "inbox")
        target_email = email_extractor.extract_and_decode_email_with_matching_keyword("UNSEEN", "secmaildata")
        if target_email is not None:
            asyncio.get_event_loop().run_until_complete(main(target_email, keywords, BASE_PATH))
        sleep(20)
