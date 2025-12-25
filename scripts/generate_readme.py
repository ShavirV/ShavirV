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
BIRTHDATE = date(2005, 2, 4)

# =========================
# SVG STYLING
# =========================
FONT_FAMILY = "monospace"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 16
SVG_WIDTH = 800

# =========================
# TERMINAL COLOR PALETTE
# =========================
BG_COLOR        = "#0c0c0c"
COLOR_PROMPT    = "#16c60c"
COLOR_PATH      = "#3a96dd"
COLOR_ASCII     = "#e74856"
COLOR_MUTED     = "#7a7a7a"
COLOR_LABEL     = "#9ece6a"
COLOR_VALUE     = "#d4d4d4"
COLOR_USER      = "#bb9af7"
COLOR_SEPARATOR = "#565f89"

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

def calculate_age(birthdate: date):
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

    return f"{years} years, {months} months, {days} days"

def escape_svg_text(text: str):
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

def svg_multicolor_line(x, y, spans):
    """
    spans = [(text, color), (text, color), ...]
    """
    tspan_elements = []
    for text, color in spans:
        text = escape_svg_text(text)
        tspan_elements.append(
            f'<tspan fill="{color}">{text}</tspan>'
        )

    return (
        f'<text x="{x}" y="{y}">'
        + "".join(tspan_elements)
        + "</text>"
    )

# =========================
# SVG GENERATION
# =========================
def generate_svg(user):
    age = calculate_age(BIRTHDATE)

    # LEFT TERMINAL BLOCK (each row = list of spans)
    left_block = [
        [( "shavi@ShavirPC:", COLOR_PROMPT),
         ("/mnt/c/Users/shavi$ neofetch", COLOR_PATH)],

        [],

        [( "    :-::::.........................", COLOR_ASCII)],
        [( "  :--:::.............................", COLOR_ASCII)],
        [( " :-::::................................", COLOR_ASCII)],
        [( " -::::.............................+-..", COLOR_ASCII)],
        [( ".::::.............................==+=..", COLOR_ASCII)],
        [( ".:::...............................*#+..", COLOR_ASCII)],
        [( ".:::.........++*+:.......................", COLOR_ASCII)],
        [( ".::.........=*+.*+.......................", COLOR_ASCII)],
        [( ".::..........=**+........................", COLOR_ASCII)],
        [( ".::........................:----::::.....", COLOR_ASCII)],
        [( ".::.....................:============:..", COLOR_ASCII)],
        [( " ::.................:-================..", COLOR_ASCII)],
        [( " .::...............-=============--=-..", COLOR_ASCII)],
        [( "   .:..............:========------:...", COLOR_ASCII)],
        [( "     ................:--------::........", COLOR_ASCII)],
        [( "       ................................", COLOR_ASCII)],

        [],

        [( "shavi@ShavirPC:/mnt/c/Users/shavi$ sudo rm -rf / --no-preserve-root", COLOR_MUTED)],
    ]

    # RIGHT INFO BLOCK (each row = list of spans)
    right_block = [
        [(f"{GITHUB_USERNAME}@github", COLOR_USER)],
        [("---------------", COLOR_SEPARATOR)],
        [("Name: ", COLOR_LABEL), (FULL_NAME, COLOR_VALUE)],
        [("Host: ", COLOR_LABEL), (HOST, COLOR_VALUE)],
        [("Uptime: ", COLOR_LABEL), (age, COLOR_VALUE)],
        [("Repos: ", COLOR_LABEL), (str(user["public_repos"]), COLOR_VALUE)],
        [("Followers: ", COLOR_LABEL), (str(user["followers"]), COLOR_VALUE)],
        [("Following: ", COLOR_LABEL), (str(user["following"]), COLOR_VALUE)],
    ]

    lines = max(len(left_block), len(right_block))
    height = PADDING * 2 + lines * LINE_HEIGHT

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'''
        <style>
          text {{
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE}px;
            dominant-baseline: text-before-edge;
            white-space: pre;
            letter-spacing: 0.4px;
          }}
        </style>
        '''
    ]

    y = PADDING
    for i in range(lines):
        if i < len(left_block) and left_block[i]:
            svg.append(svg_multicolor_line(PADDING, y, left_block[i]))

        if i < len(right_block) and right_block[i]:
            svg.append(svg_multicolor_line(420, y, right_block[i]))

        y += LINE_HEIGHT

    svg.append("</svg>")
    return "\n".join(svg)

# =========================
# README UPDATE
# =========================
def update_readme():
    readme_path = "README.md"
    svg_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_USERNAME}/main/neofetch.svg"

    img_block = f"""
<!-- neofetch:start -->
<a href="https://github.com/{GITHUB_USERNAME}">
  <img alt="{FULL_NAME}'s GitHub Profile README" src="{svg_url}" width="700"/>
</a>
<!-- neofetch:end -->
""".strip()

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    import re
    new_content = re.sub(
        r"<!-- neofetch:start -->.*?<!-- neofetch:end -->",
        img_block,
        content,
        flags=re.DOTALL
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

# =========================
# MAIN
# =========================
def main():
    print("Generating neofetch.svg...")
    user = get_user_data()

    svg_content = generate_svg(user)
    with open("neofetch.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("Updating README.md...")
    update_readme()
    print("Done!")

if __name__ == "__main__":
    main()
