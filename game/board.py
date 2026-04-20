"""Board state and terminal rendering (hacker-style UI)."""

from utils.clear_screen import clear_screen
from utils.style import bold, cyan, gray, green, magenta, red, yellow

BANNER_LINES = [
    " ██████╗ ████████╗████████╗████████╗",
    "██╔═══██╗╚══██╔══╝╚══██╔══╝╚══██╔══╝",
    "██║   ██║   ██║      ██║      ██║   ",
    "██║▄▄ ██║   ██║      ██║      ██║   ",
    "╚██████╔╝   ██║      ██║      ██║   ",
    " ╚══▀▀═╝    ╚═╝      ╚═╝      ╚═╝   ",
]

MODE_LABELS = {
    "pvp":    "human vs human",
    "random": "human (X) vs random bot (O)",
    "ai":     "human (X) vs trained AI (O)",
    "watch":  "random bot (X) vs trained AI (O)",
    "train":  "training the AI",
}


def _banner():
    print()
    for line in BANNER_LINES:
        print("  " + green(line))
    print("  " + gray("q-learning · tabular RL · self-play"))
    print()


def _compact_header():
    print()
    print(f"  {green(bold('qttt'))} {gray('::')} {gray('q-learning tic-tac-toe')}")
    print()


def _sep():
    print(gray("  " + "─" * 58))


class Board:
    def __init__(self):
        self.grid = [[" "] * 3 for _ in range(3)]

    def reset(self):
        self.grid = [[" "] * 3 for _ in range(3)]

    def place(self, row, col, player):
        if 0 <= row <= 2 and 0 <= col <= 2 and self.grid[row][col] == " ":
            self.grid[row][col] = player
            return True
        return False

    def is_empty(self, row, col):
        return self.grid[row][col] == " "

    def empty_positions(self):
        return [(i, j) for i in range(3) for j in range(3) if self.grid[i][j] == " "]

    def is_full(self):
        return all(cell != " " for row in self.grid for cell in row)

    def copy_grid(self):
        return [row[:] for row in self.grid]

    def render(self, mode, current_player, message=""):
        clear_screen()
        _compact_header()
        print(f"  {cyan('[ mode ]')} {MODE_LABELS.get(mode, 'unknown')}")
        _sep()
        print()
        print("       " + "   ".join(cyan(str(i)) for i in range(3)))
        print(gray("     ┌───┬───┬───┐"))
        for i in range(3):
            cells = []
            for j in range(3):
                v = self.grid[i][j]
                if v == "X":
                    cells.append(cyan(bold("X")))
                elif v == "O":
                    cells.append(magenta(bold("O")))
                else:
                    cells.append(" ")
            row = (
                f"   {cyan(str(i))} {gray('│')} "
                + f" {gray('│')} ".join(cells)
                + f" {gray('│')}"
            )
            print(row)
            if i < 2:
                print(gray("     ├───┼───┼───┤"))
        print(gray("     └───┴───┴───┘"))
        print()

        if message:
            print(f"  {message}")
            print()

        if mode in ("random", "ai") and current_player == "O":
            who = "trained AI" if mode == "ai" else "random bot"
            print(f"  {magenta('[ turn ]')} {who} (O) thinking...")
        elif mode == "watch":
            who = "random bot" if current_player == "X" else "trained AI"
            print(
                f"  {magenta('[ turn ]')} {who} ({current_player}) thinking...  "
                f"{gray('ctrl+c to quit')}"
            )
        elif mode != "train":
            print(f"  {green('[ turn ]')} player {bold(current_player)}")
            print(
                f"  {gray('root@qttt:~$')} "
                f"{gray('row col (e.g. 1 2) or q to quit')}"
            )

        _sep()

    def render_main_menu(self):
        clear_screen()
        _banner()
        print(f"  {cyan('[ system ]')} tabular q-learning agent  {gray('::')} v1.0")
        _sep()
        print()
        print(f"  {yellow('[ modes ]')} select operation:")
        print()
        print(f"    {green('[1]')} {gray('>')} human vs human")
        print(f"    {green('[2]')} {gray('>')} human vs random bot")
        print(f"    {green('[3]')} {gray('>')} human vs trained AI")
        print(f"    {green('[4]')} {gray('>')} spectate  {gray('::')} random bot vs AI")
        print(f"    {green('[5]')} {gray('>')} train the AI  {gray('(self-play)')}")
        print(f"    {red('[q]')} {gray('>')} quit")
        print()
        _sep()

    def render_training(self, episode, total, epsilon, wins_x, wins_o, draws):
        if episode == 1:
            clear_screen()
            _banner()
            print(f"  {yellow('[ training ]')} starting with {total:,} episodes")
            _sep()
            print()
        if episode % 1000 == 0:
            pct = episode / total * 100
            filled = int(pct / 2)
            bar = green("█" * filled) + gray("░" * (50 - filled))
            print(f"  {gray('ep')} {episode:>7,}/{total:,}  [{bar}] {pct:5.1f}%")
            print(
                f"  {gray('ε')} {epsilon:.3f}   {gray('last 1k →')} "
                f"X:{wins_x:3d}  O:{wins_o:3d}  draw:{draws:3d}"
            )
            _sep()
