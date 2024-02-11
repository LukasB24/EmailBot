import asyncio
import os
from dotenv import load_dotenv
import requests
from pyppeteer import launch
from pyppeteer.errors import PageError
from emailExtractor import EmailExtractor

async def main():
    """Fetches email from secmail and stores it"""
    load_dotenv()
    APP_PW = os.getenv("APP_PW")
    EMAIL = os.getenv("EMAIL")
    GMAIL_SERVER = "imap.gmail.com"
    GMAIL_PORT = 993

    email_extractor = EmailExtractor(GMAIL_SERVER, GMAIL_PORT, EMAIL, APP_PW, "inbox")
    target_email = email_extractor.extract_and_decode_email_with_matching_keyword("UNSEEN", "secmaildata")

    if target_email is None:
        return

    browser = await launch(executablePath="/usr/bin/chromium")
    page = await browser.newPage()
    await page.setContent(target_email)
    open_email_button = await page.querySelector("button")
    await open_email_button.click()
    await asyncio.sleep(2)
    password_field = await page.querySelector("#loginform > div:nth-child(2) > input")
    await password_field.type(os.getenv("SECPASS"))
    login_submit_button = await page.querySelector("#loginform > div.d-flex.flex-row.justify-content-between > div:nth-child(2) > input")
    await login_submit_button.click()
    await asyncio.sleep(2)
    await page.waitForSelector("#content > div > div > div > ul > li > a")
    download_pdf_link = await page.querySelector("#content > div > div > div > ul > li > a")

    if download_pdf_link:
        try:
            pdf_url = await page.evaluate("(element) => element.href", download_pdf_link)
            response = requests.get(pdf_url, timeout=15)

            with open("my-pdf.pdf", "wb") as f:
                f.write(response.content)

        except PageError as e:
            print("Exception occured while accessing pdfLink", e)

    await asyncio.sleep(3)
    await page.screenshot({"path": "screen.png", "fullPage": True})
    await browser.close()

print("Starting")
asyncio.get_event_loop().run_until_complete(main())
print("Screenshot has been taken")
