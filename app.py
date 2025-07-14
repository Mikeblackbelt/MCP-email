import asyncio
import email
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import mcp.types as types
import mail
import sys
import datetime
import json

loop = asyncio.get_event_loop()

mcp = FastMCP("EmailWriter")


def gather_emails():
    return [mail.parse_email(mail.fetch_mail_by_id(email_id)) for email_id in mail.email_ids]


@mcp.tool("getRecentEmails")
def recentEmail(amount: int = 5, filterUnread: bool = False):
    """
    Get recent emails
    Args:
        amount: int -> Amount of emails to read
        filterUnread: bool -> Return only unread emails
    """
    try:
        email_data = gather_emails()
        email_data.sort(key=lambda x: x.get("date", ""), reverse=True)
        if filterUnread:
            email_data = [email for email in email_data if not email.get("seen", False)]
        return email_data[:amount]
    except Exception as e:
        print(f"Error in recentEmail: {e}", file=sys.stderr)
        raise e


@mcp.tool("sendDrafts")
def sendDrafts(
    filter_Subject: str = '',
    filter_DateBefore: datetime.date = None,
    filter_DateAfter: datetime.date = None,
    filter_Recipent: str = None
):
    drafts = mail.get_Drafts()
    draft_data = [mail.fetch_mail_by_id(draftID) for draftID in drafts]
    parsed_data = [mail.parse_email(unparsed) for unparsed in draft_data]
    
    sent = []

    for msg in parsed_data:
        subject = msg.get('subject', '')
        to = msg.get('to', '')
        date_str = msg.get('date', '')
        try:
            msg_date = email.utils.parsedate_to_datetime(date_str).date()
        except:
            msg_date = None

        # Filters
        if filter_Subject and filter_Subject.lower() not in subject.lower():
            continue

        if filter_Recipent:
            to_list = [x.strip().lower() for x in to.split(",")]
            if filter_Recipent.lower() not in to_list:
                continue

        if filter_DateBefore and msg_date and msg_date >= filter_DateBefore:
            continue

        if filter_DateAfter and msg_date and msg_date <= filter_DateAfter:
            continue

        # Send the email
        try:
            result = mail.send_Email(
                adresss=to,
                subject=subject,
                content=msg.get("body", ""),
                BCC=msg.get("BCC"),
                CC=msg.get("CC")
            )
            if result:
                sent.append(subject)
        except Exception as e:
            print(f"Failed to send draft: {e}", file=sys.stderr)

    return sent, "Success"


if __name__ == "__main__":
    print("Starting EmailWriter server...", file=sys.stderr)
    mcp.run(transport='stdio')
