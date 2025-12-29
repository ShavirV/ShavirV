import json
import requests
import os
from datetime import date
from calendar import monthrange

# =========================
# USER CONFIGURATION
# =========================
GITHUB_USERNAME = "ShavirV"
FULL_NAME = "Shavir Vallabh"
HOST = "University of Pretoria"

LANGUAGES = "C++, C#, Java, Python, JavaScript, PHP"
FRAMEWORKS = "NodeJS, Angular, Django"
HOBBIES = "Console Modding, Emulation"

BIRTHDATE = date(2005, 2, 4)

# =========================
# SVG STYLING
# =========================
FONT_FAMILY = "monospace"
FONT_SIZE = 14
LINE_HEIGHT = 18
PADDING = 16
SVG_WIDTH = 1000

# Terminal palette
BG_COLOR        = "#262d33"
COLOR_PROMPT    = "#16c60c"
COLOR_PATH      = "#3a96dd"
COLOR_ASCII     = "#d9c811"
COLOR_MUTED     = "#7a7a7a"
COLOR_LABEL     = "#e74856"
COLOR_VALUE     = "#d4d4d4"
COLOR_USER      = "#bb9af7"

# =========================
# GITHUB API
# =========================
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# =========================
# HELPERS
# =========================
def get_user_data():
    r = requests.get(
        f"https://api.github.com/users/{GITHUB_USERNAME}",
        headers=HEADERS
    )
    r.raise_for_status()
    return r.json()

def calculate_age(birthdate):
    today = date.today()
    years = today.year - birthdate.year
    months = today.month - birthdate.month
    days = today.day - birthdate.day

    if days < 0:
        months -= 1
        days += monthrange(today.year, (today.month - 1) or 12)[1]
    if months < 0:
        years -= 1
        months += 12

    return f"{years}y {months}m {days}d"

def load_metrics():
    with open("metrics.json", "r", encoding="utf-8") as f:
        return json.load(f)

def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_line(x, y, spans):
    t = "".join(
        f'<tspan fill="{c}">{escape(s)}</tspan>'
        for s, c in spans
    )
    return f'<text x="{x}" y="{y}">{t}</text>'

# =========================
# SVG GENERATION
# =========================
def generate_svg(user, metrics):
    age = calculate_age(BIRTHDATE)

    # Extract metrics
    commits = metrics["plugins"]["lines"]["lines"]["commits"]
    added = metrics["plugins"]["lines"]["lines"]["added"]
    removed = metrics["plugins"]["lines"]["lines"]["deleted"]
    stars = metrics["plugins"]["stars"]["stars"]

    left = [
        [("shavi@ShavirPC:", COLOR_PROMPT), ("~$ neofetch", COLOR_PATH)],
        [],
        [("    :-::::.........................", COLOR_ASCII)],
        [("  :--:::.............................", COLOR_ASCII)],
        [(" :-::::................................", COLOR_ASCII)],
        [(" -::::.............................+-..", COLOR_ASCII)],
        [(" .::::.............................==+=..", COLOR_ASCII)],
        [(" .:::...............................*#+..", COLOR_ASCII)],
        [(" .:::.........++*+:.......................", COLOR_ASCII)],
        [],
        [("shavi@ShavirPC:", COLOR_PROMPT), ("~$ sudo rm -rf /", COLOR_PATH)],
    ]

    right = [
        [(f"{GITHUB_USERNAME}@github", COLOR_USER)],
        [],
        [("Kernel", COLOR_LABEL), (" : " + FULL_NAME, COLOR_VALUE)],
        [("Host", COLOR_LABEL), (" : " + HOST, COLOR_VALUE)],
        [("Uptime", COLOR_LABEL), (" : " + age, COLOR_VALUE)],
        [],
        [("Languages", COLOR_LABEL), (" : " + LANGUAGES, COLOR_VALUE)],
        [("Frameworks", COLOR_LABEL), (" : " + FRAMEWORKS, COLOR_VALUE)],
        [("Hobbies", COLOR_LABEL), (" : " + HOBBIES, COLOR_VALUE)],
        [],
        [("Repos", COLOR_LABEL), (" : " + str(user["public_repos"]), COLOR_VALUE)],
        [("Stars", COLOR_LABEL), (" : " + str(stars), COLOR_VALUE)],
        [("Commits", COLOR_LABEL), (" : " + str(commits), COLOR_VALUE)],
        [("LOC +", COLOR_LABEL), (" : " + str(added), COLOR_VALUE)],
        [("LOC -", COLOR_LABEL), (" : " + str(removed), COLOR_VALUE)],
    ]

    lines = max(len(left), len(right))
    height = PADDING * 2 + lines * LINE_HEIGHT

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'<style>text{{font-family:{FONT_FAMILY};font-size:{FONT_SIZE}px;white-space:pre}}</style>'
    ]

    y = PADDING
    for i in range(lines):
        if i < len(left):
            svg.append(svg_line(PADDING, y, left[i]))
        if i < len(right):
            svg.append(svg_line(420, y, right[i]))
        y += LINE_HEIGHT

    svg.append("</svg>")
    return "\n".join(svg)

# =========================
# MAIN
# =========================
def main():
    user = get_user_data()
    metrics = load_metrics()

    svg = generate_svg(user, metrics)
    with open("neofetch.svg", "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    main()
