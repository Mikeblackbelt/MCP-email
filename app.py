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
import sheets

loop = asyncio.get_event_loop()

mcp = FastMCP("EmailWriter")

HOST = 'claude' #claude if claude

def gather_emails(isDraft: bool = False):
    IDS = mail.get_Drafts() if isDraft else mail.email_ids
    return [mail.parse_email(mail.fetch_mail_by_id(email_id)) for email_id in IDS] 


@mcp.tool("getRecentEmails")
def recentEmail(amount: int = 5, filterUnread: bool = False, filterMailingList: bool = True, range: list[int] = None):
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
    
        if filterMailingList:
            email_data = [email for email in email_data if not email['is_mailing_list']]

        for email in email_data:
            email
        return email_data[:amount] if not range else email_data[range[0]:range[1]]
    
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

@mcp.tool('writeDrafts')
def write_Draft(subject: str, content: str, * ,recipent: str = None, BCC: str = None, CC: str = None):
    mail.send_Email(recipent, subject, content,BCC=BCC, CC=CC, isDraft=True)
    return f'Draft to {(recipent if recipent else "no recipent")} with subject {subject} created.'

@mcp.tool('searchByDate')
def search_by_date(*, start_date: datetime.date = None, end_date: datetime.date = None, max_amount: int = None, isDraft: bool = False):
    email_data = gather_emails(isDraft)
    if (start_date is not None): email_data[:] = [email for email in email_data if start_date <= email["date"]]
    if (end_date is not None):  email_data[:] = [email for email in email_data if end_date >= email["date"]]
    if int(start_date is not None) + int(end_date is not None) + int(max_amount is not None) < 2: raise ValueError('Not enough arguments')
    if (max_amount > len(email_data)): max_amount = len(email_data)
    if (max_amount is not None and end_date is not None): return email_data[-max_amount:]
    if (max_amount is not None and start_date is not None): return email_data[:max_amount - 1]
    return email_data
            
@mcp.tool('searchOther')
def searchOther(*, author: str = None,BCC: str = None, CC: str = None, isDraft: bool = False, max_amount: int = None):
    email_data = gather_emails(isDraft)
    if (author is not None): email_data = [email for email in email_data if email["from"] == author]
    if (BCC is not None): email_data = [email for email in email_data if email['BCC'] == BCC]
    if (CC is not None): email_data = [email for email in email_data if email['CC'] == CC]
    if (max_amount > len(email_data)): max_amount = len(email_data)
    return email_data[-max_amount:] if max_amount is not None else email_data

@mcp.tool("GetStudentData")
def getStudentData():
    return sheets.get_StudentData()

@mcp.tool("GetFilteredStudentData")
def getFiteredStudentData(*,includeRACE: list[str] = None, includeGPA_RANGE: list[list[int]] = None, includeGENDER: list[str] = None, include_INCOME_RANGE: list[list[int]] = None,includeGrade: list[int] = None,  excludeRACE: list[str] = None, excludeGPA_RANGE: list[list[int]] = None, excludeGENDER: list[str] = None, exclude_INCOME_RANGE: list[list[int]] = None, excludeGrade: list[int] = None, interest: str = None):
    data = sheets.filter_out(includeRACE=includeRACE,includeGPA_RANGE=includeGPA_RANGE,includeGENDER=includeGENDER,include_INCOME_RANGE=include_INCOME_RANGE,includeGrade=includeGrade,exclude_INCOME_RANGE=exclude_INCOME_RANGE,excludeGENDER=excludeGENDER,excludeRACE=excludeRACE,excludeGPA_RANGE=excludeGPA_RANGE,excludeGrade=excludeGrade)
    return sheets.get_Interest(interest, student_data=data, categories=1) if interest is not None else data
        

@mcp.tool("GetSpecificStudent")
def getSpecificStudent(*, firstName:str =None, lastName: str = None, OSIS: int | str = None):
    if OSIS is not None and type(OSIS) is not int: OSIS = int(OSIS)
    if not any([lastName is None, firstName is None, OSIS is None]): raise ValueError("Atleast one argument is required")
    toReturn = []
    for students in sheets.get_StudentData():
        if not ((OSIS is not None and int(students['OSIS']) == OSIS) or (OSIS is None)):  continue #filter by osis
        elif not ((firstName is not None and firstName == students['First Name']) or firstName is None): continue #filter by first
        elif not ((lastName is not None and lastName == students['Last Name']) or lastName is None): continue
        else: toReturn.append(students)
    return toReturn


    
    
if __name__ == "__main__":
    if HOST == "claude":
        print("Starting EmailWriter server...", file=sys.stderr)
        mcp.run(transport='stdio')
    """elif HOST == 'http':
        print("Starting EmailWriter server on http://localhost:3333", file=sys.stderr)
        mcp.run(transport="http", port=3333)""" #dont
    else:
        raise ValueError("Invalid Host")


