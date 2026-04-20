"""Clear the terminal screen (cross-platform)."""

import os


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
