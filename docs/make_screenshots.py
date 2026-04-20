"""Generate SVG 'screenshots' of qttt's UI from captured terminal output.

Run from the repo root:

    python docs/make_screenshots.py

This produces:
    docs/menu.svg       — main menu
    docs/gameplay.svg   — in-game board
    docs/training.svg   — training progress

The SVGs preserve our ANSI 256-color palette as inline <tspan fill="..."/>
elements, so they render correctly on GitHub without any external tooling.
"""

import io
import os
import re
import sys
from contextlib import redirect_stdout

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

# --- 1. force-enable ANSI colors in the style module, before board imports it
import utils.style as style  # noqa: E402

style._ENABLED = True
style.RESET = "\033[0m"
style.BOLD = "\033[1m"
style.DIM = "\033[2m"
style.GREEN = "\033[38;5;46m"
style.CYAN = "\033[38;5;51m"
style.YELLOW = "\033[38;5;226m"
style.RED = "\033[38;5;196m"
style.MAGENTA = "\033[38;5;201m"
style.GRAY = "\033[38;5;244m"
style.WHITE = "\033[38;5;255m"


def _mk(code):
    return lambda s: f"{code}{s}\033[0m"


style.green = _mk(style.GREEN)
style.cyan = _mk(style.CYAN)
style.yellow = _mk(style.YELLOW)
style.red = _mk(style.RED)
style.magenta = _mk(style.MAGENTA)
style.gray = _mk(style.GRAY)
style.white = _mk(style.WHITE)
style.bold = _mk(style.BOLD)
style.dim = _mk(style.DIM)

from game import board  # noqa: E402

board.clear_screen = lambda: None

# --- 2. ANSI parser -------------------------------------------------------

ANSI_RE = re.compile(r"\033\[([0-9;]*)m")

COLOR_MAP = {
    46: "#5cff5c",
    51: "#5ce7ff",
    226: "#ffee55",
    196: "#ff5c5c",
    201: "#ff5cff",
    244: "#8a8a8a",
    255: "#e8e8e8",
}
DEFAULT_FG = "#c6c6c6"


def parse_ansi_lines(text):
    lines, line = [], []
    fg, bold = DEFAULT_FG, False
    pos = 0

    def flush_chunk(chunk):
        nonlocal line
        parts = chunk.split("\n")
        for i, part in enumerate(parts):
            if part:
                line.append((fg, bold, part))
            if i < len(parts) - 1:
                lines.append(line)
                line = []

    for m in ANSI_RE.finditer(text):
        if m.start() > pos:
            flush_chunk(text[pos : m.start()])
        pos = m.end()
        code = m.group(1)
        if code in ("", "0"):
            fg, bold = DEFAULT_FG, False
        elif code == "1":
            bold = True
        elif code == "2":
            fg = "#8a8a8a"
        elif code.startswith("38;5;"):
            try:
                idx = int(code.split(";")[2])
                fg = COLOR_MAP.get(idx, DEFAULT_FG)
            except (IndexError, ValueError):
                pass

    if pos < len(text):
        flush_chunk(text[pos:])
    if line:
        lines.append(line)
    return lines


# --- 3. SVG renderer ------------------------------------------------------

CHAR_W = 9
LINE_H = 20
PAD = 18
BG = "#0d1117"  # GitHub dark
CHROME_H = 28


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def to_svg(lines, title="qttt"):
    max_cols = max((sum(len(s) for _, _, s in ln) for ln in lines), default=0)
    width = max_cols * CHAR_W + PAD * 2
    height = len(lines) * LINE_H + PAD * 2 + CHROME_H

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace, Menlo, Consolas, monospace" font-size="14">'
    )
    out.append(f'  <rect width="{width}" height="{height}" rx="10" fill="{BG}"/>')
    # window chrome
    out.append(f'  <rect width="{width}" height="{CHROME_H}" rx="10" fill="#161b22"/>')
    out.append(f'  <rect y="{CHROME_H - 10}" width="{width}" height="10" fill="#161b22"/>')
    out.append('  <circle cx="16" cy="14" r="5" fill="#ff5f57"/>')
    out.append('  <circle cx="34" cy="14" r="5" fill="#febc2e"/>')
    out.append('  <circle cx="52" cy="14" r="5" fill="#28c840"/>')
    out.append(
        f'  <text x="{width/2}" y="18" fill="#8a8a8a" font-size="12" '
        f'text-anchor="middle">{_escape(title)}</text>'
    )

    y = CHROME_H + PAD + LINE_H - 6
    for ln in lines:
        out.append(f'  <text x="{PAD}" y="{y}" xml:space="preserve">')
        for fg, bold, s in ln:
            weight = ' font-weight="700"' if bold else ""
            out.append(f'    <tspan fill="{fg}"{weight}>{_escape(s)}</tspan>')
        out.append("  </text>")
        y += LINE_H
    out.append("</svg>")
    return "\n".join(out)


def capture(fn):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()
    return buf.getvalue()


def main():
    out_dir = os.path.join(_ROOT, "docs")

    # Menu screenshot
    b = board.Board()
    text = capture(b.render_main_menu)
    svg = to_svg(parse_ansi_lines(text), title="qttt — main menu")
    with open(os.path.join(out_dir, "menu.svg"), "w") as f:
        f.write(svg)

    # Gameplay screenshot (a realistic mid-game state)
    b = board.Board()
    b.place(0, 0, "X")
    b.place(1, 1, "O")
    b.place(0, 2, "X")
    b.place(2, 0, "O")
    text = capture(lambda: b.render("ai", "X"))
    svg = to_svg(parse_ansi_lines(text), title="qttt — human vs trained AI")
    with open(os.path.join(out_dir, "gameplay.svg"), "w") as f:
        f.write(svg)

    # Training screenshot (simulate a few progress lines)
    def _render_training():
        b2 = board.Board()
        b2.render_training(1, 10000, 0.900, 0, 0, 0)
        b2.render_training(1000, 10000, 0.604, 428, 391, 181)
        b2.render_training(3000, 10000, 0.223, 312, 472, 216)
        b2.render_training(6000, 10000, 0.101, 256, 547, 197)
        b2.render_training(10000, 10000, 0.100, 198, 601, 201)

    text = capture(_render_training)
    svg = to_svg(parse_ansi_lines(text), title="qttt — self-play training")
    with open(os.path.join(out_dir, "training.svg"), "w") as f:
        f.write(svg)

    print("wrote docs/menu.svg, docs/gameplay.svg, docs/training.svg")


if __name__ == "__main__":
    main()
