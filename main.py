from email.message import Message
import os
from dotenv import load_dotenv
import imaplib, email
import requests
import asyncio
from pyppeteer import launch

def getMultiPartPayload(msg: Message):
    payloads = []

    for part in msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            payloads.append(payload.decode())

    return payloads

load_dotenv()
APP_PW = os.getenv('APP_PW')
EMAIL = os.getenv('EMAIL')
GMAIL_SERVER = 'imap.gmail.com'
GMAIL_PORT = 993
URL = "https://secmail-api.misoft.de/v2/createsession"
mail = imaplib.IMAP4_SSL(GMAIL_SERVER, GMAIL_PORT)
mail.login(EMAIL, APP_PW)
mail.select('inbox')
payload = ''

status, data = mail.search(None, 'UNSEEN')

if status == 'OK':
    for num in data[0].split():
        status, msg_data = mail.fetch(num, '(RFC822)')
        if status == 'OK':
            raw_email = msg_data[0][1] 
            msg = email.message_from_bytes(raw_email)
            print('Nachricht:', num)
            print('Betreff:', msg['Subject'])
            print('Absender:', msg['From'])

            if msg.is_multipart():
                payloads = getMultiPartPayload(msg)
                for element in payloads:
                    if 'secmaildata' in element:
                        payload = element

            else:
                payload = msg.get_payload(decode=True).decode()
      
else:
    print("Fehler beim Durchsuchen der E-Mails.")

mail.logout()
    
async def main():
    browser = await launch(executablePath='/usr/bin/chromium')
    page = await browser.newPage()
    await page.setContent(payload)
    openEmailButton = await page.querySelector("button")
    await openEmailButton.click()
    await asyncio.sleep(2)
    passwordField = await page.querySelector("#loginform > div:nth-child(2) > input")
    await passwordField.type(os.getenv("SECPASS"))
    loginSumbitButtton = await page.querySelector("#loginform > div.d-flex.flex-row.justify-content-between > div:nth-child(2) > input")
    await loginSumbitButtton.click()
    await asyncio.sleep(2)
    await page.waitForSelector("#content > div > div > div > ul > li > a")
    downloadPdf = await page.querySelector("#content > div > div > div > ul > li > a")

    if downloadPdf:
        try:
            pdf_url = await page.evaluate('(element) => element.href', downloadPdf)
            response = requests.get(pdf_url)

            with open("my-pdf.pdf", "wb") as f:
                f.write(response.content)

        except Exception as e:
            print("Fehler beim klicken", e)

    await asyncio.sleep(3)
    await page.screenshot({"path": "screen.png", "fullPage": True})
    await browser.close()

print("Starting")
asyncio.get_event_loop().run_until_complete(main())
print("Screenshot has been taken")