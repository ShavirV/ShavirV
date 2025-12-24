import requests
import os
from datetime import date

# =========================
# USER CONFIGURATION
# =========================
GITHUB_USERNAME = "ShavirV"
FULL_NAME = "Shavir Vallabh"
HOST = "University of Pretoria"
BIRTHDATE = date(2004, 2, 4)

# SVG styling
FONT_FAMILY = "monospace"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 20

# Tokyo Night–ish palette
COLOR_LOGO = "#7aa2f7"
COLOR_LABEL = "#9ece6a"
COLOR_VALUE = "#c0caf5"
COLOR_USER = "#bb9af7"
COLOR_SEPARATOR = "#565f89"
BG_COLOR = "#1a1b26"

# =========================
# GITHUB API
# =========================
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_user_data():
    r = requests.get(
        f"https://api.github.com/users/{GITHUB_USERNAME}",
        headers=HEADERS
    )
    r.raise_for_status()
    return r.json()

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

def svg_text(x, y, text, color):
    return f'<text x="{x}" y="{y}" fill="{color}">{text}</text>'

def generate_svg(user):
    age = calculate_age(BIRTHDATE)

    left_block = [
        r"      /\_/\",
        r"     ( o.o )",
        r"      > ^ <"
    ]

    right_block = [
        (f"{GITHUB_USERNAME}@github", COLOR_USER),
        ("-----------------------", COLOR_SEPARATOR),
        (f"Name: {FULL_NAME}", COLOR_LABEL),
        (f"Host: {HOST}", COLOR_LABEL),
        (f"Uptime: {age}", COLOR_LABEL),
        (f"Repos: {user['public_repos']}", COLOR_LABEL),
        (f"Followers: {user['followers']}", COLOR_LABEL),
        (f"Following: {user['following']}", COLOR_LABEL),
    ]

    lines = max(len(left_block), len(right_block))
    height = PADDING * 2 + lines * LINE_HEIGHT
    width = 700

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'<style>text {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}px; }}</style>'
    ]

    y = PADDING + LINE_HEIGHT

    for i in range(lines):
        if i < len(left_block):
            svg.append(svg_text(PADDING, y, left_block[i], COLOR_LOGO))

        if i < len(right_block):
            text, color = right_block[i]
            svg.append(svg_text(260, y, text, color))

        y += LINE_HEIGHT

    svg.append("</svg>")
    return "\n".join(svg)

def main():
    print("Generating neofetch SVG...")
    user = get_user_data()
    svg = generate_svg(user)

    with open("neofetch.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    print("neofetch.svg written")

if __name__ == "__main__":
    main()
