import imaplib
import email
from email.header import decode_header
import os
import json
from dotenv import load_dotenv

load_dotenv("n.env")  
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Email and Password must be set in the environment variables.")

IMAP_SERVER = "imap.gmail.com"

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)

mail.select("inbox")

status, messages = mail.search(None, 'ALL')

email_ids = messages[0].split()

def fetch_mail_by_id(email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        print(f"Failed to fetch email with ID {email_id}")
        return None
    return msg_data

def parse_email(msg_data):
    msg = email.message_from_bytes(msg_data[0][1])
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else 'utf-8')
    
    from_ = msg.get("From")
    date_ = msg.get("Date")
    
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    
    return json.dumps({
        "subject": subject,
        "from": from_,
        "date": date_,
        "body": body
    }, indent=2)

if __name__ == "__main__":
    print([parse_email(fetch_mail_by_id(i)) for i in email_ids])