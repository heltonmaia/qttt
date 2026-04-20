"""ANSI color helpers for the terminal-hacker aesthetic.

Colors are disabled automatically when stdout is not a TTY
or when the NO_COLOR environment variable is set.
"""

import os
import sys

_ENABLED = (
    os.environ.get("FORCE_COLOR") == "1"
    or (sys.stdout.isatty() and os.environ.get("NO_COLOR") is None)
)


def _c(code: str) -> str:
    return code if _ENABLED else ""


RESET = _c("\033[0m")
BOLD = _c("\033[1m")
DIM = _c("\033[2m")

GREEN = _c("\033[38;5;46m")
CYAN = _c("\033[38;5;51m")
YELLOW = _c("\033[38;5;226m")
RED = _c("\033[38;5;196m")
MAGENTA = _c("\033[38;5;201m")
GRAY = _c("\033[38;5;244m")
WHITE = _c("\033[38;5;255m")


def green(s):   return f"{GREEN}{s}{RESET}"
def cyan(s):    return f"{CYAN}{s}{RESET}"
def yellow(s):  return f"{YELLOW}{s}{RESET}"
def red(s):     return f"{RED}{s}{RESET}"
def magenta(s): return f"{MAGENTA}{s}{RESET}"
def gray(s):    return f"{GRAY}{s}{RESET}"
def white(s):   return f"{WHITE}{s}{RESET}"
def bold(s):    return f"{BOLD}{s}{RESET}"
def dim(s):     return f"{DIM}{s}{RESET}"
