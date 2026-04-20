"""Async entry point for qttt in the browser.

Reuses the pure parts of the terminal version (Board, QLearningAgent)
and implements a compact async game loop. Input comes from xterm.js via
the ``window.__qttt_read_line`` JS bridge defined in ``app.js``.

The terminal version's ``game/engine.py`` stays fully synchronous — we
duplicate only the ~100 lines of game flow here so the main code path
remains simple.
"""

import asyncio
import random

import js

from agent.qlearning import QLearningAgent
from game.board import Board
import game.board as board_mod

# xterm.js understands the ANSI clear-screen sequence, so we replace the
# terminal-version's `os.system("clear")` with a no-dependency print.
board_mod.clear_screen = lambda: print("\x1b[2J\x1b[H", end="", flush=True)

MODEL_PATH = "models/qlearning_model.pkl"
MODE_KEY = {"1": "pvp", "2": "random", "3": "ai", "4": "watch"}

GREETINGS = {
    "random": "\x1b[38;5;51m[ start ]\x1b[0m you are X, bot is O. you play first.",
    "ai":     "\x1b[38;5;51m[ start ]\x1b[0m you are X, AI is O. you play first.",
    "pvp":    "\x1b[38;5;51m[ start ]\x1b[0m player X plays first.",
    "watch":  "\x1b[38;5;51m[ start ]\x1b[0m spectating: random bot (X) vs trained AI (O).",
}


async def ainput(prompt: str = "") -> str:
    if prompt:
        print(prompt, end="", flush=True)
    result = await js.window.__qttt_read_line()
    return str(result)


def check_winner(grid):
    for row in grid:
        if row[0] == row[1] == row[2] != " ":
            return row[0]
    for c in range(3):
        if grid[0][c] == grid[1][c] == grid[2][c] != " ":
            return grid[0][c]
    if grid[0][0] == grid[1][1] == grid[2][2] != " ":
        return grid[0][0]
    if grid[0][2] == grid[1][1] == grid[2][0] != " ":
        return grid[0][2]
    return None


async def choose_mode(board, loaded):
    while True:
        board.render_main_menu()
        choice = (
            await ainput("  \x1b[38;5;51mroot@qttt:~$\x1b[0m ")
        ).strip().lower()
        if choice in ("1", "2"):
            return MODE_KEY[choice]
        if choice in ("3", "4"):
            if loaded:
                return MODE_KEY[choice]
            print("  \x1b[38;5;196m[ err ]\x1b[0m trained model not available")
            await asyncio.sleep(1)
        elif choice == "5":
            print(
                "  \x1b[38;5;226m[ info ]\x1b[0m "
                "training is disabled in the browser demo."
            )
            print(
                "  \x1b[2m"
                "(a pre-trained model is already loaded — pick option 3)"
                "\x1b[0m"
            )
            await ainput("  \x1b[2mpress enter to return\x1b[0m ")
        elif choice == "q":
            return None
        else:
            print("  \x1b[38;5;196m[ err ]\x1b[0m invalid option")
            await asyncio.sleep(0.7)


async def auto_move(board, agent, mode, current):
    await asyncio.sleep(1.0)
    if mode == "ai" or (mode == "watch" and current == "O"):
        return agent.choose_action(board.grid, training=False)
    return random.choice(board.empty_positions())


async def human_move(board):
    entry = (await ainput()).strip().lower()
    if entry == "q":
        return "quit", None
    try:
        row, col = map(int, entry.split())
    except ValueError:
        return "err", "use 'row col' separated by space (e.g. 1 2)"
    if not (0 <= row <= 2 and 0 <= col <= 2):
        return "err", "coordinates must be in range 0..2"
    if not board.is_empty(row, col):
        return "err", "cell already occupied"
    return "ok", (row, col)


async def ask_play_again():
    answer = (
        await ainput(
            "\n  \x1b[38;5;226mplay again?\x1b[0m \x1b[2m[y/N]\x1b[0m "
        )
    ).strip().lower()
    return answer == "y"


async def play():
    agent = QLearningAgent()
    loaded = agent.load_model(MODEL_PATH)
    board = Board()

    while True:
        mode = await choose_mode(board, loaded)
        if mode is None:
            print("\n  \x1b[2mbye.\x1b[0m")
            return

        board.reset()
        current = "X"
        print(f"  {GREETINGS[mode]}")
        await asyncio.sleep(1.2)

        while True:
            board.render(mode, current)

            if mode == "watch" or (
                mode in ("random", "ai") and current == "O"
            ):
                row, col = await auto_move(board, agent, mode, current)
            else:
                kind, payload = await human_move(board)
                if kind == "quit":
                    print("  \x1b[2mbye.\x1b[0m")
                    return
                if kind == "err":
                    print(f"  \x1b[38;5;196m[ err ]\x1b[0m {payload}")
                    await asyncio.sleep(0.8)
                    continue
                row, col = payload

            board.place(row, col, current)

            winner = check_winner(board.grid)
            if winner or board.is_full():
                final = (
                    f"\x1b[38;5;46m[ win ]\x1b[0m player {winner}"
                    if winner
                    else "\x1b[38;5;226m[ draw ]\x1b[0m no winner"
                )
                board.render(mode, current, final)
                if not await ask_play_again():
                    print("  \x1b[2mbye.\x1b[0m")
                    return
                break

            current = "O" if current == "X" else "X"


await play()
