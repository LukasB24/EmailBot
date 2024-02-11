import email
import imaplib
from email.message import Message

def get_and_decode_multipart_payload(msg: Message) -> list[str]:
    "Extracts payload from multipart message"
    payloads = []

    for part in msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            payloads.append(payload.decode())

    return payloads

class EmailExtractor:
    """Connects to a specified emailserver and extracts emails based on provided keywords"""
    def __init__(self, email_server: str, email_server_port: str, user_email: str, app_pw: str, mailbox: str) -> None:
        self.__mail = imaplib.IMAP4_SSL(email_server, email_server_port)
        self.__mail.login(user_email, app_pw)
        self.__mail.select(mailbox)

    def extract_and_decode_email_with_matching_keyword(self, mail_criteria: str, keyword: str) -> str|None:
        """Extracts and decodes email that matches keyword"""
        status, data = self.__mail.search(None, mail_criteria)
        target_email = ""

        if status != "OK":
            return None
        
        for num in data[0].split():
            status, msg_data = self.__mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1] 
            msg = email.message_from_bytes(raw_email)

            if msg.is_multipart():
                payloads = get_and_decode_multipart_payload(msg)
                for element in payloads:
                    if keyword in element:
                        target_email = element

            else:
                target_email = msg.get_payload(decode=True).decode()
        
        self.__mail.logout()
        return target_email