import imaplib
import smtplib
import email
from email.header import decode_header
import os
import sys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
load_dotenv("n.env")  
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Email and Password must be set in the environment variables.")

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# IMAP connection
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)
mail.select("inbox")

# Search for all emails
status, messages = mail.search(None, 'ALL')
email_ids = messages[0].split()


def fetch_mail_by_id(email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        print(f"Failed to fetch email with ID {email_id}", file=sys.stderr)
        return None
    return msg_data


def parse_email(msg_data):
    msg = email.message_from_bytes(msg_data[0][1])
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors='ignore')

    from_ = msg.get("From")
    to_ = msg.get("To")
    BCC = msg.get("BCC") or None
    CC = msg.get("CC") or None
    date_ = msg.get("Date")

    body = ""
    html_body = ""

    mailing_list_headers = ["List-ID", "List-Unsubscribe", "Precedence"]
    is_mailing_list = any(header in msg for header in mailing_list_headers) or any(n in from_.lower() for n in ['noreply','alert','no-reply','donotreply'])

    if msg.is_multipart():
        for part in msg.walk():
            if part is None: continue
            content_type = part.get_content_type()
            content_dispo = str(part.get("Content-Disposition"))

            if "attachment" in content_dispo:
                continue

            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                decoded = payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
            except Exception:
                continue

            if content_type == "text/plain":
                body += decoded
            elif content_type == "text/html":
                html_body += decoded
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            decoded = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
            if content_type == "text/plain":
                body = decoded
            elif content_type == "text/html":
                html_body = decoded

    if not body and html_body:
        soup = BeautifulSoup(html_body, "html.parser")
        body = soup.get_text(separator="\n").strip()

    return {
        "subject": subject,
        "from": from_,
        "to": to_,
        "BCC": BCC,
        "CC": CC,
        "date": date_,
        "body": body,
        "is_mailing_list": is_mailing_list
    }


def get_Drafts():
    mail.select('"[Gmail]/Drafts"')
    status, data = mail.search(None, "ALL")
    return data[0].split() if status == "OK" else []


def send_Email(adresss: str, subject: str, content: str, *, BCC: str = None, CC: str = None, msgType: str = 'plain', isDraft: bool = False):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = adresss
        msg['Subject'] = subject
        if BCC:
            msg['BCC'] = BCC
        if CC:
            msg['CC'] = CC

        msg.attach(MIMEText(content, msgType))

        if isDraft:
            msg.add_header('X-Unsent', '1')

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        return msg
    except Exception as e:
        print(f"Email send failed: {e}", file=sys.stderr)
        return None
