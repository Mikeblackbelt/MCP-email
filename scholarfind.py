"""import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; ScholarshipBot/1.0)",
})

def fastweb_login(email: str, password: str) -> bool:
    login_page = session.get("https://www.fastweb.com/login")
    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.select_one("input[name=csrf_token]")["value"]  # hypothetical CSRF
    payload = {"email": email, "password": password, "csrf_token": token}
    resp = session.post("https://www.fastweb.com/login", data=payload)
    return resp.url != login_page.url  # quick check if redirected

def filter_by_interests(scholarships, interests):
    return [
        s for s in scholarships
        if any(kw.lower() in s["name"].lower() for kw in interests)
    ]
"""
