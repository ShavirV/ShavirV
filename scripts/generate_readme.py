import requests
import os
import re
from datetime import date

# =========================
# USER CONFIGURATION
# =========================
GITHUB_USERNAME = "ShavirV"
FULL_NAME = "Shavir Vallabh"
EMPLOYER = "University of Pretoria"
BIRTHDATE = date(2004, 02, 04)

# =========================
# GITHUB API SETUP
# =========================
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_user_data():
    response = requests.get(
        f"https://api.github.com/users/{GITHUB_USERNAME}",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

def build_neofetch_block(user):
    age = calculate_age(BIRTHDATE)

    return f"""
```text
      /\_/\\
     ( o.o )    {GITHUB_USERNAME}@github
      > ^ <     -----------------------
                 Name: {FULL_NAME}
                 Host: {EMPLOYER}
                 Uptime: {age}
                 Repos: {user['public_repos']}
                 Followers: {user['followers']}
                 Following: {user['following']}

