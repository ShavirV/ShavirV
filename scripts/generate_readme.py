import json
from datetime import date
from calendar import monthrange

# =========================
# USER CONFIGURATION
# =========================
GITHUB_USERNAME = "ShavirV"
FULL_NAME = "Shavir Vallabh"
HOST = "University of Pretoria"

LANGUAGES = "C++, C#, Java, Python, JavaScript, PHP"
OTHER_LANGS = "HTML/CSS, Bash, Powershell, SQL"
FRAMEWORKS = "NodeJS, Angular, Django"
HOBBIES = "Console Modding, Homebrew, Emulation"

EMAIL_PERSONAL = "shavirvallabh05@gmail.com"
EMAIL_ACADEMIC = "u23718146@tuks.co.za"
LINKEDIN = "Shavir Vallabh"
DISCORD = "shavirrrr"
INSTAGRAM = "@shavir.v"

BIRTHDATE = date(2005, 2, 4)

# =========================
# SVG STYLING
# =========================
FONT_FAMILY = "monospace"
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 16
SVG_WIDTH = 1000
RIGHT_X = 420

# Terminal palette
BG_COLOR        = "#262d33"
COLOR_PROMPT    = "#16c60c"
COLOR_PATH      = "#3a96dd"
COLOR_ASCII     = "#d9c811"
COLOR_MUTED     = "#7a7a7a"
COLOR_LABEL     = "#e74856"
COLOR_VALUE     = "#d4d4d4"
COLOR_USER      = "#bb9af7"
COLOR_REDDISH   = "#e30e0e"
COLOR_GREENISH  = "#0ee355"

# =========================
# HELPERS
# =========================
def calculate_age(birthdate: date) -> str:
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


def load_metrics(path="metrics.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def svg_line(x: int, y: int, spans: list) -> str:
    tspans = "".join(
        f'<tspan fill="{color}">{escape(text)}</tspan>'
        for text, color in spans
    )
    return f'<text x="{x}" y="{y}">{tspans}</text>'


def safe_get(obj, *keys, default=0):
    for key in keys:
        obj = obj.get(key, {})
    return obj if obj else default

# =========================
# SVG GENERATION
# =========================
def generate_svg(metrics: dict) -> str:
    age = calculate_age(BIRTHDATE)

    # ---- Extract metrics safely ----
    commits = metrics.get("commits", 0)
    added   = metrics.get("loc_added", 0)
    removed = metrics.get("loc_removed", 0)
    stars   = metrics.get("stars", 0)
    repos   = metrics.get("repos", 0)


    # =========================
    # LEFT TERMINAL BLOCK
    # =========================
    left = [
        [( "shavi@ShavirPC:", COLOR_PROMPT),
         ("/mnt/c/Users/shavi:~$ neofetch", COLOR_PATH)],

        [],

        [("    :-::::.........................          ", COLOR_ASCII)],
        [("  :--:::.............................        ", COLOR_ASCII)],
        [(" :-::::................................      ", COLOR_ASCII)],
        [(" -::::.............................+-..      ", COLOR_ASCII)],
        [(".::::.............................==+=..     ", COLOR_ASCII)],
        [(".:::...............................*#+..     ", COLOR_ASCII)],
        [(".:::.........++*+:.......................    ", COLOR_ASCII)],
        [(".::.........=*+.*+.......................    ", COLOR_ASCII)],
        [(".::..........=**+........................    ", COLOR_ASCII)],
        [(".::........................:----::::.....    ", COLOR_ASCII)],
        [(".::.....................:============:..     ", COLOR_ASCII)],
        [(" ::.................:-================..     ", COLOR_ASCII)],
        [(" .::...............-=============--=-..:----:", COLOR_ASCII)],
        [("   .:..............:========------:...::::::-", COLOR_ASCII)],
        [("     ................:--------::........:::::", COLOR_ASCII)],
        [("       .....................................:", COLOR_ASCII)],
        [("        :....................................", COLOR_ASCII)],
        [("      .:::.................................. ", COLOR_ASCII)],
        [("    .:...................................    ", COLOR_ASCII)],
        [("           .......................           ", COLOR_ASCII)],

        [],

        [("\n\n\nshavi@ShavirPC:", COLOR_PROMPT),
         ("/mnt/c/Users/shavi$ sudo rm -rf / --no-preserve-root", COLOR_PATH)],
    ]

    # =========================
    # RIGHT INFO BLOCK
    # =========================
    right = [
        [("\n", COLOR_MUTED)],
        [("\n", COLOR_MUTED)],

        [(f"{GITHUB_USERNAME}@github", COLOR_USER),
         ("―――――――――――――――――――――――――――――――――――――――", COLOR_MUTED)],

        [("Kernel", COLOR_LABEL), (" : " + FULL_NAME, COLOR_VALUE)],
        [("Host", COLOR_LABEL), (" : " + HOST, COLOR_VALUE)],
        [("Uptime", COLOR_LABEL), (" : " + age, COLOR_VALUE)],

        [("\n", COLOR_MUTED)],

        [("Packages.Programming", COLOR_LABEL), (" : " + LANGUAGES, COLOR_VALUE)],
        [("Packages.Computer", COLOR_LABEL), (" : " + OTHER_LANGS, COLOR_VALUE)],
        [("Packages.Frameworks", COLOR_LABEL), (" : " + FRAMEWORKS, COLOR_VALUE)],
        [("Hobbies", COLOR_LABEL), (" : " + HOBBIES, COLOR_VALUE)],

        [("\n", COLOR_MUTED)],

        [(f"Contact Me:", COLOR_USER), ("――――――――――――――――――――――――――――――――――――――――――", COLOR_MUTED)],
        [("Email.personal", COLOR_LABEL), (" : " + EMAIL_PERSONAL, COLOR_VALUE)],
        [("Email.academic", COLOR_LABEL), (" : " + EMAIL_ACADEMIC, COLOR_VALUE)],
        [("Socials.LinkedIn", COLOR_LABEL), (" : " + LINKEDIN, COLOR_VALUE)],
        [("Socials.Instagram", COLOR_LABEL), (" : " + INSTAGRAM, COLOR_VALUE)],
        [("Socials.Discord", COLOR_LABEL), (" : " + DISCORD, COLOR_VALUE)],

        [("\n", COLOR_MUTED)],

        [("Profile Stats", COLOR_USER),
         ("―――――――――――――――――――――――――――――――――――――――", COLOR_MUTED)],

        [("Repos", COLOR_LABEL),   (" : " + str(repos), COLOR_VALUE)],
        [("Stars", COLOR_LABEL),   (" : " + str(stars), COLOR_VALUE)],
        [("Commits", COLOR_LABEL), (" : " + str(commits), COLOR_VALUE)],
        [("Lines of Code: ", COLOR_LABEL),   ("+" + str(added), COLOR_GREENISH), ("  |  ", COLOR_LABEL),   ("-" + str(removed), COLOR_REDDISH)],
    ]

    # =========================
    # SVG BUILD
    # =========================
    lines = max(len(left), len(right))
    height = PADDING * 2 + lines * LINE_HEIGHT

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'''
        <style>
            text {{
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE}px;
                white-space: pre;
                dominant-baseline: text-before-edge;
                letter-spacing: 0.3px;
            }}
        </style>
        '''
    ]

    y = PADDING
    for i in range(lines):
        if i < len(left) and left[i]:
            svg.append(svg_line(PADDING, y, left[i]))
        if i < len(right) and right[i]:
            svg.append(svg_line(RIGHT_X, y, right[i]))
        y += LINE_HEIGHT

    svg.append("</svg>")
    return "\n".join(svg)

# =========================
# MAIN
# =========================
def main():
    metrics = load_metrics()
    svg = generate_svg(metrics)

    with open("neofetch.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    print("neofetch.svg generated successfully")

if __name__ == "__main__":
    main()
