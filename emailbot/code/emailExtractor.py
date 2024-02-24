import email
import imaplib
from email.message import Message

def get_and_decode_multipart_payload(msg: Message) -> list[str]:
    payloads = []

    for part in msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            payloads.append(payload.decode())

    return payloads

class EmailExtractor:
    """Connects to a specified emailserver and extracts emails based on provided keywords"""
    def __init__(self, email_server: str, email_server_port: str, 
                 user_email: str, app_pw: str, mailbox: str) -> None:

        self.__mail = imaplib.IMAP4_SSL(email_server, email_server_port, timeout=10)
        self.__mail.login(user_email, app_pw)
        self.__mail.select(mailbox)
    


    def extract_payload_by_keyword(self, mail_criteria: str, payload_keyword: str, subject_keyword: str) -> list[str] | None:
        status, data = self.__mail.search(None, mail_criteria)
        target_payloads = []

        if status != "OK" or data[0] == b'':
            return None
        
        for num in data[0].split():
            status, msg_data = self.__mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1] 
            msg = email.message_from_bytes(raw_email)
            
            if not subject_keyword is None and not subject_keyword in msg.as_string().lower():
                continue

            if msg.is_multipart():
                payloads = get_and_decode_multipart_payload(msg)
                for element in payloads:
                    if payload_keyword in element:
                        target_payloads.append(element)

            else:
                target_payloads.append(msg.get_payload(decode=True).decode())
        
        return target_payloads
    
    def __del__(self):
        if hasattr(self, "__mail"):
            self.__mail.logout()
        