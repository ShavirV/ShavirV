"""
cube_scramble.py
generate a random valid 3x3 scramble and generate an svg render. to be run daily
"""

import random
import hashlib
from datetime import date

SVG_WIDTH   = 1000
SVG_HEIGHT  = 550
CELL        = 42          #px per sticker (increased from 28)
GAP         = 3           #px between stickers (increased from 2)
FONT        = "monospace"
BG          = "#262d33"
GRID_STROKE = "#1a2025"
LABEL_COL   = "#9a9a9a"
TITLE_COL   = "#16c60c"
MOVE_COL    = "#d4d4d4"
PRIME_COL   = "#ba8ad6"   # moves with '
DOUBLE_COL  = "#6ca0c7"   # moves with 2

# Sticker colours per face (solved state)
FACE_COLORS = {
    "U": "#f0f0f0",   # white
    "D": "#e0ca02",   # yellow
    "F": "#1ebe15",   # green
    "B": "#166daf",   # blue
    "L": "#e87722",   # orange
    "R": "#e30e0e",   # red
}

SCRAMBLE_LEN = 20
MOVES_BASE   = ["U", "D", "F", "B", "L", "R"]
SUFFIXES     = ["", "'", "2"]

#generate scramble
def daily_scramble(seed_date: date) -> list[str]:
    """Deterministic scramble based on date so it's stable all day."""
    seed = int(hashlib.md5(str(seed_date).encode()).hexdigest(), 16)
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
        # CW applied 3 times = CCW
        _apply_single(s, face, False)
        _apply_single(s, face, False)
        _apply_single(s, face, False)
        return

    #rotate the face itself
    s[face] = rotate_face_cw(s[face])

    #cycle adjacent edges
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

    step     = CELL + GAP
    face_w   = 3 * step - GAP   # width of one face block
    face_h   = face_w

    # Net layout:
    #        [U]
    #   [L] [F] [R] [B]
    #        [D]
    # Origin of the net, centred in SVG
    net_total_w = 4 * (face_w + GAP * 2)  # increased spacing between faces
    net_total_h = 3 * (face_h + GAP * 2)
    ox = (SVG_WIDTH - net_total_w) // 2 + GAP * 2
    oy = 60   # leave room for title

    face_spacing_x = face_w + GAP * 3
    face_spacing_y = face_h + GAP * 3

    face_positions = {
        "U": (ox + face_spacing_x,           oy),
        "L": (ox,                            oy + face_spacing_y),
        "F": (ox + face_spacing_x,           oy + face_spacing_y),
        "R": (ox + 2 * face_spacing_x,       oy + face_spacing_y),
        "B": (ox + 3 * face_spacing_x,       oy + face_spacing_y),
        "D": (ox + face_spacing_x,           oy + 2 * face_spacing_y),
    }

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>text {{ font-family: {FONT}; dominant-baseline: text-before-edge; }}</style>',
        # Title
        f'<text x="15" y="15" font-size="14" fill="{TITLE_COL}">shavi@ShavirPC:</text>',
        f'<text x="165" y="15" font-size="14" fill="#3a96dd">~$ cube --daily_scramble --date={today}</text>',
    ]

    # Draw faces
    for face, (fx, fy) in face_positions.items():
        svg_parts.append(draw_face(state[face], fx, fy))
        # Face label
        lx = fx + face_w // 2
        ly = fy - 8
        svg_parts.append(
            f'<text x="{lx}" y="{ly}" font-size="13" fill="{LABEL_COL}" '
            f'text-anchor="middle" font-weight="bold">{face}</text>'
        )

    # Scramble string at bottom — colour-coded
    scramble_y = oy + net_total_h + 20
    move_x = 15
    svg_parts.append(
        f'<text x="{move_x}" y="{scramble_y}" font-size="14" fill="{LABEL_COL}">scramble: </text>'
    )
    move_x += 90
    for move in scramble:
        if "'" in move:
            col = PRIME_COL
        elif "2" in move:
            col = DOUBLE_COL
        else:
            col = MOVE_COL
        svg_parts.append(
            f'<text x="{move_x}" y="{scramble_y}" font-size="14" fill="{col}">{escape(move)} </text>'
        )
        move_x += len(move) * 9 + 6

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