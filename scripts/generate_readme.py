import requests
import os
from datetime import date

# =========================
# USER CONFIGURATION
# =========================
GITHUB_USERNAME = "ShavirV"
FULL_NAME = "Shavir Vallabh"
HOST = "University of Pretoria"
BIRTHDATE = date(2005, 2, 4)

# SVG styling
FONT_FAMILY = "monospace"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 20

# Colors
COLOR_LOGO = "#7aa2f7"
COLOR_LABEL = "#9ece6a"
COLOR_USER = "#bb9af7"
COLOR_SEPARATOR = "#565f89"
BG_COLOR = "#1a1b26"

# GitHub API
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

def get_user_data():
    r = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def calculate_age(birthdate: date):
    today = date.today()

    # Start with difference in years, months, days
    years = today.year - birthdate.year
    months = today.month - birthdate.month
    days = today.day - birthdate.day

    # Adjust if days negative
    if days < 0:
        months -= 1
        # Number of days in previous month
        from calendar import monthrange
        days += monthrange(today.year, (today.month - 1) or 12)[1]

    # Adjust if months negative
    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months, {days} days"

def escape_svg_text(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_text(x, y, text, color):
    text = escape_svg_text(text)
    return f'<text x="{x}" y="{y}" fill="{color}">{text}</text>'

def generate_svg(user):
    age = calculate_age(BIRTHDATE)

    left_block = [
"****++=========-----------------====++++++++%",
"**+++=======----------------------===++++++++",
"*++=======--------------------------==+++++++",
"++=======-=--------:-::::::::-:---=*===+*****",
"+=======-----------::::::::::::---****==*****",
"+======-----------:::::::::::::::-=%%#-==****",
"======------=**#*=-:::::::::::::::------=****",
"======------*##=#*-::::::::::::::::-----=****",
"=====--------*##*-:::::::::::-:-:-:-:----+*++",
"=====--------:-::::::::::--=+++=====----=++++",
"=====------:::::::::::--=************=--=++++",
"+=====-----:-::::::-=++***********+***-=+++++",
"*=====------::::---+*************++++--=+++++",
"*+=====-----:-:---==*******++=++++=---======+",
"+++=====-----:-:----==+++++++===-----========",
"+++++====------:::-:-:------:-::-------======",
"===========---------:-:::::-:::-:---------===",
"==============-----:-:::-:-:--:--:----------=",
"==============----------:-:-:-:-:------------",
"==========-=----------------:--:-:-:---------",
"=========--------------------:--:-:-:-:------",
"=======-------------------------:--:-:-:-:---",
"=====-=------------------------:-:-::-:---:--",
"====-=--------------:-:-:-:-:-:-:-::::-:::-:-"
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

def update_readme():
    """Update README.md to reference the hosted neofetch.svg"""
    readme_path = "README.md"
    svg_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/ShavirV/main/neofetch.svg"

    img_block = f'''
<!-- neofetch:start -->
<a href="https://github.com/{GITHUB_USERNAME}/ShavirV">
  <img alt="{FULL_NAME}'s GitHub Profile README" src="{svg_url}" width="700"/>
</a>
<!-- neofetch:end -->
'''.strip()

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

def main():
    print("Generating neofetch.svg...")
    user = get_user_data()
    svg_content = generate_svg(user)

    with open("neofetch.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("Updating README.md to reference hosted SVG...")
    update_readme()
    print("Done!")

if __name__ == "__main__":
    main()
