import asyncio
import re
import os
import shutil
from pyppeteer import errors
import requests
from pyppeteer import launch
from pyppeteer.errors import PageError
from pdfScraper import PDFScraper
from logger import Logger

async def get_pdf_from_secmail(email_content: str, chrome_path: str) -> str | None:
    """Fetches pdf from secmail email"""
    logger = Logger()

    try:
        target_file = ""

        if not os.path.exists(chrome_path):
            raise os.error(f"'{chrome_path}' does not exist")
        
        browser = await launch(executablePath=chrome_path)
        page = await browser.newPage()
        await page.setContent(email_content)
        open_email_button = await page.querySelector("button")
        await open_email_button.click()
        await asyncio.sleep(10)
        password_field = await page.querySelector("#loginform > div:nth-child(2) > input")
        await password_field.type(os.getenv("PASSWORD"))
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
    except errors.PyppeteerError as e:
        logger.write_log(f"Exception occurred during proccessing website elements: {e}")
        return None


def store_file_based_on_keyword(filename: str, words: list[str], base_path: str) -> str | None:
    """Stores file in matching directory"""
    logger = Logger()

    if filename == "" or None:
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
