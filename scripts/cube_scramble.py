import random
import hashlib
from datetime import date

SVG_WIDTH   = 1000
SVG_HEIGHT  = 700

CELL        = 58
GAP         = 4

FONT        = "monospace"
BG          = "#262d33"
GRID_STROKE = "#1a2025"

#text colors
COLOR_PROMPT = "#16c60c"
COLOR_PATH   = "#3a96dd"
COLOR_LABEL  = "#6ca0c7"
COLOR_VALUE  = "#d4d4d4"
COLOR_MUTED  = "#7a7a7a"

MOVE_COL    = "#d4d4d4"
PRIME_COL   = "#bb9af7"
DOUBLE_COL  = "#e0af68"

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

#generate scramble
def daily_scramble(seed_date: date):
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

def solved_state():
    return {f: [f] * 9 for f in "UDFBLR"}

def rotate_face_cw(f):
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

def _apply_single(s, face, ccw=False):
    if ccw:
        for _ in range(3):
            _apply_single(s, face, False)
        return

    s[face] = rotate_face_cw(s[face])

    if face == "U":
        tmp = s["F"][0:3]
        s["F"][0:3] = s["R"][0:3]
        s["R"][0:3] = s["B"][0:3]
        s["B"][0:3] = s["L"][0:3]
        s["L"][0:3] = tmp

    elif face == "D":
        tmp = s["F"][6:9]
        s["F"][6:9] = s["L"][6:9]
        s["L"][6:9] = s["B"][6:9]
        s["B"][6:9] = s["R"][6:9]
        s["R"][6:9] = tmp

    elif face == "F":
        u = [s["U"][6], s["U"][7], s["U"][8]]
        s["U"][6], s["U"][7], s["U"][8] = s["L"][8], s["L"][5], s["L"][2]
        s["L"][2], s["L"][5], s["L"][8] = s["D"][0], s["D"][1], s["D"][2]
        s["D"][0], s["D"][1], s["D"][2] = s["R"][6], s["R"][3], s["R"][0]
        s["R"][0], s["R"][3], s["R"][6] = u

    elif face == "B":
        u = [s["U"][0], s["U"][1], s["U"][2]]
        s["U"][0], s["U"][1], s["U"][2] = s["R"][2], s["R"][5], s["R"][8]
        s["R"][2], s["R"][5], s["R"][8] = s["D"][8], s["D"][7], s["D"][6]
        s["D"][6], s["D"][7], s["D"][8] = s["L"][0], s["L"][3], s["L"][6]
        s["L"][0], s["L"][3], s["L"][6] = u[::-1]

    elif face == "L":
        u = [s["U"][0], s["U"][3], s["U"][6]]
        s["U"][0], s["U"][3], s["U"][6] = s["B"][8], s["B"][5], s["B"][2]
        s["B"][2], s["B"][5], s["B"][8] = s["D"][0], s["D"][3], s["D"][6]
        s["D"][0], s["D"][3], s["D"][6] = s["F"][0], s["F"][3], s["F"][6]
        s["F"][0], s["F"][3], s["F"][6] = u

    elif face == "R":
        u = [s["U"][2], s["U"][5], s["U"][8]]
        s["U"][2], s["U"][5], s["U"][8] = s["F"][2], s["F"][5], s["F"][8]
        s["F"][2], s["F"][5], s["F"][8] = s["D"][2], s["D"][5], s["D"][8]
        s["D"][2], s["D"][5], s["D"][8] = s["B"][6], s["B"][3], s["B"][0]
        s["B"][0], s["B"][3], s["B"][6] = u[::-1]

def scramble_state(scramble):
    state = solved_state()
    for m in scramble:
        apply_move(state, m)
    return state

#3d render
def shade(color, factor):
    c = int(color[1:], 16)
    r = int(((c >> 16) & 255) * factor)
    g = int(((c >> 8) & 255) * factor)
    b = int((c & 255) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'

def draw_cube_3d(state, ox, oy):
    out = []
    size = 30
    dx = size
    dy = size // 2

    def poly(points, color):
        pts = " ".join(f"{x},{y}" for x, y in points)
        return f'<polygon points="{pts}" fill="{color}" stroke="{GRID_STROKE}" stroke-width="1.5"/>'

    #faces
    U, F, R = state["U"], state["F"], state["R"]

    #TOP (lighter)
    for r in range(3):
        for c in range(3):
            x = ox + (c-r)*dx
            y = oy + (c+r)*dy
            out.append(poly([
                (x, y),
                (x+dx, y-dy),
                (x+2*dx, y),
                (x+dx, y+dy),
            ], FACE_COLORS[U[r*3+c]]))

    #FRONT
    base_y = oy + 3*dy

    for r in range(3):
        for c in range(3):
            x = ox + c*dx
            y = base_y + r*size
            out.append(poly([
                (x, y),
                (x+dx, y-dy),
                (x+dx, y-dy+size),
                (x, y+size),
            ], FACE_COLORS[F[r*3+c]]))

    #RIGHT (darker)
    for r in range(3):
        for c in range(3):
            x = ox + 3*dx + c*dx
            y = base_y + r*size - c*dy
            out.append(poly([
                (x, y-dy),
                (x+dx, y),
                (x+dx, y+size),
                (x, y-dy+size),
            ], FACE_COLORS[R[r*3+c]]))

    return "\n".join(out)


def generate_svg(today):
    scramble = daily_scramble(today)
    state    = scramble_state(scramble)

    step = CELL + GAP
    face_w = 3 * step - GAP

    ox, oy = 60, 90

    positions = {
        "U": (ox + face_w, oy),
        "L": (ox, oy + face_w),
        "F": (ox + face_w, oy + face_w),
        "R": (ox + 2*face_w, oy + face_w),
        "B": (ox + 3*face_w, oy + face_w),
        "D": (ox + face_w, oy + 2*face_w),
    }

    def draw_face(face, x, y):
        out = []
        for i, s in enumerate(face):
            r, c = divmod(i, 3)
            out.append(
                f'<rect x="{x+c*step}" y="{y+r*step}" width="{CELL}" height="{CELL}" '
                f'rx="6" fill="{FACE_COLORS[s]}" stroke="{GRID_STROKE}" stroke-width="2"/>'
            )
        return "\n".join(out)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'''
        <style>
            text {{
                font-family: {FONT};
                font-size: 14px;
                dominant-baseline: text-before-edge;
                white-space: pre;
                letter-spacing: 0.2px;
            }}
        </style>
        ''',
        f'<text x="15" y="15" fill="{COLOR_PROMPT}" font-weight="bold">shavi@ShavirPC:</text>',
        f'<text x="165" y="15" fill="{COLOR_PATH}">~$ cube --daily --date={today}</text>',
    ]

    #net
    for f, (x,y) in positions.items():
        svg.append(draw_face(state[f], x, y))

    svg.append(draw_cube_3d(state, 760, 220))

    meta_y = 380
    lines = [
        ("cube.session", f"daily #{today.toordinal()}"),
        ("cube.metric", f"HTM {len(scramble)}"),
        ("cube.state", "scrambled"),
        ("cube.generated", str(today))
    ]

    for i, (label, value) in enumerate(lines):
        y = meta_y + i * 24
        svg.append(
            f'<text x="700" y="{y}">'
            f'<tspan fill="{COLOR_LABEL}">{label:<18}</tspan>'
            f'<tspan fill="{COLOR_VALUE}">: {value}</tspan>'
            f'</text>'
        )

    scramble_label_y = 575
    svg.append(
        f'<text x="15" y="{scramble_label_y}" fill="{COLOR_LABEL}">scramble:</text>'
    )

    start_x = 120
    row_y = 605

    for i, move in enumerate(scramble):
        if i > 0 and i % 8 == 0:
            row_y += 24
            start_x = 120

        col = MOVE_COL
        if "'" in move:
            col = PRIME_COL
        elif "2" in move:
            col = DOUBLE_COL

        svg.append(
            f'<text x="{start_x}" y="{row_y}" fill="{col}">{move}</text>'
        )
        start_x += 38

    svg.append(
        f'<text x="15" y="{SVG_HEIGHT-28}" fill="{COLOR_PROMPT}" font-weight="bold">shavi@ShavirPC:~$</text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)

def main():
    today = date.today()
    with open("cube_scramble.svg", "w", encoding="utf-8") as f:
        f.write(generate_svg(today))

if __name__ == "__main__":
    main()