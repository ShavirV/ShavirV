"""
proc_modules.py
generates a static, fake output of my skills and tech stack
"""

from datetime import date

SVG_WIDTH  = 1000
FONT       = "monospace"
FONT_SIZE  = 13
LH         = 19
PAD        = 14

BG         = "#262d33"
C_PROMPT   = "#16c60c"
C_PATH     = "#3a96dd"
C_MUTED    = "#7a7a7a"
C_LABEL    = "#e74856"
C_VALUE    = "#d4d4d4"
C_LIVE     = "#0ee355"
C_LOADING  = "#d9c811"
C_UNLOADED = "#7a7a7a"

# (module_name, size_kb, status, used_by, description)
# status: Live | Loading | Unloaded
MODULES = [
    #languages
    ("lang_cpp",        2023,  "Live",     "lang_c",           "everything OOP"),
    ("lang_python",     2024,  "Live",     "personal",         "scripting, automation. Used to generate this :)"),
    ("lang_java",       2025,  "Live",     "university",       "data structures & algorithms, artificial intelligence, networking"),
    ("lang_c",          2024,  "Live",     "everything",       "low-level, networking projects"),
    ("lang_javascript", 2023,  "Live",     "pretty_obvious",   "full-stack web, TypeScript superset"),
    ("lang_php",        2025,  "Live",     "web_backend",      "server-side scripting, RESTful APIs"),
    ("lang_csharp",     2023,  "Live",     "first_lang",       "game dev adjacent, .NET ecosystem"),
    #web / Frameworks
    ("mod_react",       2025,  "Live",     "lang_javascript",  "components, mainly charts & data visualisation"),
    ("mod_nodejs",      2025,  "Live",     "lang_javascript",  "server runtime, event-loop model"),
    ("mod_angular",     2025,  "Live",     "lang_javascript",  "PWA, general webapp development"),
    ("mod_django",      2026,  "Live",     "lang_python",      "batteries-included Python web framework"),
    #tools / systems
    ("mod_linux",       2023,   "Live",     "daily_driver",     "just about everything @home and @work"),
    ("mod_bash",        2024,   "Live",     "mod_linux",        "shell scripting, general sysadmin"),
    ("mod_powershell",  2024,   "Live",     "mod_windows",      "because i need to diversify"),
    ("mod_sql",         2025,  "Live",     "mod_postgres",     "prod databases, schema design"),
    ("mod_html_css",    2023,  "Live",     "mod_react",        "markup, layout, responsive design"),
    ("mod_latex",       2023,  "Live",     "mod_docs",        "the lion concerns himself with documentation"),
    #other
    ("skil_hpc",        "1tflop",  "Live",     "mod_linux",    "optimization, compiling from source, devops..."),
    ("skil_homebrew",   "!warranty",  "Live",     "mod_emulation", "the nintendo switch runs both linux and android :)"),
    ("skil_emulation",  "3fps",  "Live",     "mod_retro_hw",     "RetroArch, Dolphin, RPCS3, Yuzu, PCSX2..."),
    ("skil_cubing",     "3x3+", "Live",     "mod_brain",         "3x3 avg: 30s; fav puzzle: 5x5"),
    #currently learning
    ("prog_rust",        2026,  "Loading",  "lang_c",           "memory safety... quite difficult - WIP"),
    ("prog_opengl",      2026,  "Loading",  "lang_cpp",         "graphics pipeline fundamentals - WIP"),
    ("prog_kubernetes",  2026,  "Loading",  "mod_hpc",          "can restart a kubernetes cluster... sometimes - WIP"),
    ("prog_slurm",       2025,  "Loading",  "mod_hpc",          "real deployments on public servers - WIP"),
    ("prog_qiskit",      2025,  "Loading",  "lang_python",      "general quantum circuit design - WIP"),
    ("prog_emulation",   2025,  "Loading",  "mod_emulation",    "Learning how to build an emulator - WIP"),
    ("prog_bsc_comp_sci",     2027,  "Loading",  "mod_the_goal",     "just one more year left - WIP"),

]


STATUS_COLORS = {
    "Live":     C_LIVE,
    "Loading":  C_LOADING,
    "Unloaded": C_UNLOADED,
}

def escape(t: str) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tspan(text, color):
    return f'<tspan fill="{color}">{escape(text)}</tspan>'

def generate_svg() -> str:
    header_lines = [
        [("shavi@ShavirPC:", C_PROMPT), ("/proc$ cat /proc/modules", C_PATH)],
        [("# Module                 Size    Status    Used-by              Description", C_MUTED)],
        [("# ─────────────────────────────────────────────────────────────────────────────────────────────────────", C_MUTED)],
    ]

    rows = []
    for (name, size, status, used_by, desc) in MODULES:
        rows.append([
            (f"  {name:<22}", C_VALUE),
            (f" {str(size):<7}", C_MUTED),
            (f" {status:<9}", STATUS_COLORS.get(status, C_VALUE)),
            (f" {used_by:<20} ", C_MUTED),
            (f" # {desc}", C_MUTED),
        ])

    footer_lines = [
        [],
        [("shavi@ShavirPC:", C_PROMPT), ("/proc$ lsmod | grep -c Live", C_PATH)],
        [("21", C_LIVE)],
        [("shavi@ShavirPC:", C_PROMPT), ("/proc$ lsmod | grep -c Loading", C_PATH)],
        [("7", C_LOADING)],
        [],
        [("shavi@ShavirPC:", C_PROMPT), ("~$ _", C_PATH)],
    ]

    all_lines = header_lines + rows + footer_lines
    height = PAD * 2 + len(all_lines) * LH + 4

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; dominant-baseline: text-before-edge; letter-spacing: 0.2px; }}</style>',
    ]

    y = PAD
    for line in all_lines:
        if not line:
            y += LH
            continue
        tspans = "".join(tspan(text, col) for text, col in line)
        svg.append(f'<text x="{PAD}" y="{y}">{tspans}</text>')
        y += LH

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = generate_svg()
    with open("proc_modules.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("proc_modules.svg generated")


if __name__ == "__main__":
    main()