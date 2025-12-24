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
BIRTHDATE = date(2004, 2, 4)

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

    lines = [
        "```text",
        "      /\\_/\\",
        f"     ( o.o )    {GITHUB_USERNAME}@github",
        "      > ^ <     -----------------------",
        f"                 Name: {FULL_NAME}",
        f"                 Host: {EMPLOYER}",
        f"                 Uptime: {age}",
        f"                 Repos: {user['public_repos']}",
        f"                 Followers: {user['followers']}",
        f"                 Following: {user['following']}",
        "```"
    ]

    return "\n".join(lines)

def update_readme(neofetch_block):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!-- neofetch:start -->.*?<!-- neofetch:end -->",
        f"<!-- neofetch:start -->\n{neofetch_block}\n<!-- neofetch:end -->",
        content,
        flags=re.DOTALL
    )

    if content == new_content:
        print("README unchanged (no diff)")
    else:
        print("README updated")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    print("Running neofetch README generator...")
    user = get_user_data()
    block = build_neofetch_block(user)
    update_readme(block)

if __name__ == "__main__":
    main()
