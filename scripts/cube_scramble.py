"""
cube_scramble.py
generate a random valid 3x3 scramble and generate an svg render. to be run daily
"""

import random
import hashlib
from datetime import date

SVG_WIDTH   = 1000
SVG_HEIGHT  = 620
CELL        = 42
GAP         = 3
FONT        = "monospace"
FONT_SIZE   = 14
LINE_HEIGHT = 20
PADDING     = 16

BG          = "#262d33"
GRID_STROKE = "#1a2025"

# Text colors
COLOR_PROMPT = "#16c60c"
COLOR_PATH   = "#3a96dd"
COLOR_LABEL  = "#e74856"
COLOR_VALUE  = "#d4d4d4"
COLOR_MUTED  = "#7a7a7a"
COLOR_USER   = "#bb9af7"

MOVE_COL    = "#d4d4d4"
PRIME_COL   = "#bb9af7"
DOUBLE_COL  = "#e0af68"

# Sticker colours per face (solved state)
FACE_COLORS = {
    "U": "#f0f0f0",
    "D": "#e0ca02",
    "F": "#1ebe15",
    "B": "#166daf",
    "L": "#e87722",
    "R": "#e30e0e",
}

SCRAMBLE_LEN = 20
MOVES_BASE   = ["U", "D", "F", "B", "L", "R"]
SUFFIXES     = ["", "'", "2"]
SEED = ""

#generate scramble
def daily_scramble(seed_date: date) -> list[str]:
    """Deterministic scramble based on date so it's stable all day."""
    seed = int(hashlib.md5(str(seed_date).encode()).hexdigest(), 16)
    SEED = seed
    rng  = random.Random(seed)
    moves = []
    last  = ""
    for _ in range(SCRAMBLE_LEN):
        face = last
        while face == last:
            face = rng.choice(MOVES_BASE)
        last = face
        moves.append(face + rng.choice(SUFFIXES))
    return moves


#cube state sim
#represent each face as a 3x3 list (row-major, 0=top-left)
def solved_state():
    return {f: [f] * 9 for f in "UDFBLR"}


def rotate_face_cw(face_grid):
    """Rotate a 3x3 face grid 90° clockwise."""
    f = face_grid
    return [f[6], f[3], f[0],
            f[7], f[4], f[1],
            f[8], f[5], f[2]]


def apply_move(state, move):
    face = move[0]
    suffix = move[1:]

    times = 2 if suffix == "2" else 1
    ccw   = suffix == "'"

    for _ in range(times):
        _apply_single(state, face, ccw)


def _apply_single(state, face, ccw=False):
    """Apply one quarter-turn. ccw=True for counter-clockwise."""
    s = state

    if ccw:
        _apply_single(s, face, False)
        _apply_single(s, face, False)
        _apply_single(s, face, False)
        return

    s[face] = rotate_face_cw(s[face])

    if face == "U":
        tmp = [s["B"][0], s["B"][1], s["B"][2]]
        s["B"][0], s["B"][1], s["B"][2] = s["R"][0], s["R"][1], s["R"][2]
        s["R"][0], s["R"][1], s["R"][2] = s["F"][0], s["F"][1], s["F"][2]
        s["F"][0], s["F"][1], s["F"][2] = s["L"][0], s["L"][1], s["L"][2]
        s["L"][0], s["L"][1], s["L"][2] = tmp
    elif face == "D":
        tmp = [s["F"][6], s["F"][7], s["F"][8]]
        s["F"][6], s["F"][7], s["F"][8] = s["R"][6], s["R"][7], s["R"][8]
        s["R"][6], s["R"][7], s["R"][8] = s["B"][6], s["B"][7], s["B"][8]
        s["B"][6], s["B"][7], s["B"][8] = s["L"][6], s["L"][7], s["L"][8]
        s["L"][6], s["L"][7], s["L"][8] = tmp
    elif face == "F":
        tmp = [s["U"][6], s["U"][7], s["U"][8]]
        s["U"][6], s["U"][7], s["U"][8] = s["L"][8], s["L"][5], s["L"][2]
        s["L"][2], s["L"][5], s["L"][8] = s["D"][0], s["D"][1], s["D"][2]
        s["D"][0], s["D"][1], s["D"][2] = s["R"][6], s["R"][3], s["R"][0]
        s["R"][0], s["R"][3], s["R"][6] = tmp[0], tmp[1], tmp[2]
    elif face == "B":
        tmp = [s["U"][0], s["U"][1], s["U"][2]]
        s["U"][0], s["U"][1], s["U"][2] = s["R"][2], s["R"][5], s["R"][8]
        s["R"][2], s["R"][5], s["R"][8] = s["D"][8], s["D"][7], s["D"][6]
        s["D"][6], s["D"][7], s["D"][8] = s["L"][0], s["L"][3], s["L"][6]
        s["L"][0], s["L"][3], s["L"][6] = tmp[2], tmp[1], tmp[0]
    elif face == "L":
        tmp = [s["U"][0], s["U"][3], s["U"][6]]
        s["U"][0], s["U"][3], s["U"][6] = s["B"][8], s["B"][5], s["B"][2]
        s["B"][2], s["B"][5], s["B"][8] = s["D"][0], s["D"][3], s["D"][6]
        s["D"][0], s["D"][3], s["D"][6] = s["F"][0], s["F"][3], s["F"][6]
        s["F"][0], s["F"][3], s["F"][6] = tmp[0], tmp[1], tmp[2]
    elif face == "R":
        tmp = [s["U"][2], s["U"][5], s["U"][8]]
        s["U"][2], s["U"][5], s["U"][8] = s["F"][2], s["F"][5], s["F"][8]
        s["F"][2], s["F"][5], s["F"][8] = s["D"][2], s["D"][5], s["D"][8]
        s["D"][2], s["D"][5], s["D"][8] = s["B"][6], s["B"][3], s["B"][0]
        s["B"][0], s["B"][3], s["B"][6] = tmp[2], tmp[1], tmp[0]


def scramble_state(scramble: list[str]):
    state = solved_state()
    for move in scramble:
        apply_move(state, move)
    return state


#helpers for svg generation
def escape(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_line(x: int, y: int, spans: list) -> str:
    tspans = "".join(
        f'<tspan fill="{color}">{escape(text)}</tspan>'
        for text, color in spans
    )
    return f'<text x="{x}" y="{y}">{tspans}</text>'


def draw_face(face_stickers, ox, oy):
    """Return SVG rects for a 3x3 face at offset (ox, oy)."""
    out = []
    step = CELL + GAP
    for i, sticker in enumerate(face_stickers):
        row, col = divmod(i, 3)
        x = ox + col * step
        y = oy + row * step
        color = FACE_COLORS[sticker]
        out.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="4" fill="{color}" stroke="{GRID_STROKE}" stroke-width="2"/>'
        )
    return "\n".join(out)


#main svg builder
def generate_svg(today: date) -> str:
    scramble = daily_scramble(today)
    state    = scramble_state(scramble)

    step   = CELL + GAP
    face_w = 3 * step - GAP
    face_h = face_w

    left_x = PADDING
    right_x = 430

    face_spacing_x = face_w + GAP * 3
    face_spacing_y = face_h + GAP * 3

    ox = right_x + 10
    oy = 70

    face_positions = {
        "U": (ox + face_spacing_x,           oy),
        "L": (ox,                            oy + face_spacing_y),
        "F": (ox + face_spacing_x,           oy + face_spacing_y),
        "R": (ox + 2 * face_spacing_x,       oy + face_spacing_y),
        "B": (ox + 3 * face_spacing_x,       oy + face_spacing_y),
        "D": (ox + face_spacing_x,           oy + 2 * face_spacing_y),
    }

    left_block = [
        [("shavi@ShavirPC:", COLOR_PROMPT),
         ("/mnt/c/Users/shavi:~$ cube --daily --date=", COLOR_PATH),
         (str(today), COLOR_VALUE)],

        [],
        [("cube.session", COLOR_USER),
         ("──────────────────────────────", COLOR_MUTED)],

        [("cube.mode", COLOR_LABEL), (" : random daily", COLOR_VALUE)],
        [("cube.metric", COLOR_LABEL), (" : HTM " + str(len(scramble)), COLOR_VALUE)],
        [("cube.state", COLOR_LABEL), (" : scrambled", COLOR_VALUE)],
        [("cube.seed", COLOR_LABEL), (" : md5(date)", COLOR_VALUE)],

        [],
        [("solver.log", COLOR_USER),
         ("──────────────────────────────", COLOR_MUTED)],

        [("> loading cube state...", COLOR_MUTED)],
        [("> applying scramble sequence...", COLOR_MUTED)],
        [("> validating permutation validity...", COLOR_MUTED)],
        [("> render target: cube_scramble.svg", COLOR_MUTED)],
        [("> status: OK", COLOR_VALUE)],

        [],
        [("scramble.sequence", COLOR_USER),
         ("──────────────────────────────", COLOR_MUTED)],
    ]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'''
        <style>
            text {{
                font-family: {FONT};
                font-size: {FONT_SIZE}px;
                white-space: pre;
                dominant-baseline: text-before-edge;
                letter-spacing: 0.3px;
            }}
        </style>
        '''
    ]

    y = PADDING
    for row in left_block:
        if row:
            svg_parts.append(svg_line(left_x, y, row))
        y += LINE_HEIGHT

    preview_y = y + 10
    px = left_x
    py = preview_y

    for i, move in enumerate(scramble):
        if i > 0 and i % 6 == 0:
            py += 22
            px = left_x

        if "'" in move:
            col = PRIME_COL
        elif "2" in move:
            col = DOUBLE_COL
        else:
            col = MOVE_COL

        svg_parts.append(
            f'<text x="{px}" y="{py}" fill="{col}">{escape(move)}</text>'
        )
        px += 42

    for face, (fx, fy) in face_positions.items():
        svg_parts.append(draw_face(state[face], fx, fy))

    meta_y = 470
    lines = [
        ("cube.session", f"daily #{today.toordinal()}"),
        ("cube.generated", str(today)),
        ("cube.output", "cube_scramble.svg"),
    ]

    for i, (label, value) in enumerate(lines):
        yy = meta_y + i * 22
        svg_parts.append(
            svg_line(PADDING, yy, [
                (f"{label:<18}", COLOR_LABEL),
                (" : " + value, COLOR_VALUE)
            ])
        )

    svg_parts.append(
        f'<text x="{PADDING}" y="{SVG_HEIGHT-28}" fill="{COLOR_PROMPT}" font-weight="bold">shavi@ShavirPC:~$</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    today = date.today()
    svg   = generate_svg(today)
    with open("cube_scramble.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"cube_scramble.svg generated for {today}")


if __name__ == "__main__":
    main()