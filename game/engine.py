"""Game engine — control flow for qttt."""

import os
import random
import time

from agent.qlearning import QLearningAgent
from game.board import Board
from utils.clear_screen import clear_screen
from utils.style import cyan, gray, green, magenta, red, yellow


class TicTacToe:
    MODEL_PATH = "models/qlearning_model.pkl"

    def __init__(self):
        self.board = Board()
        self.current_player = "X"
        self.mode = None
        self.agent = QLearningAgent()
        os.makedirs("models", exist_ok=True)

    def check_winner(self):
        g = self.board.grid
        for row in g:
            if row[0] == row[1] == row[2] != " ":
                return row[0]
        for c in range(3):
            if g[0][c] == g[1][c] == g[2][c] != " ":
                return g[0][c]
        if g[0][0] == g[1][1] == g[2][2] != " ":
            return g[0][0]
        if g[0][2] == g[1][1] == g[2][0] != " ":
            return g[0][2]
        return None

    def swap_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def reset_game(self):
        self.board.reset()
        self.current_player = "X"

    def random_move(self):
        empties = self.board.empty_positions()
        return random.choice(empties) if empties else (None, None)

    def ai_move(self):
        action = self.agent.choose_action(self.board.grid, training=False)
        return action if action else (None, None)

    @staticmethod
    def reward_for(winner, player):
        if winner == player:
            return 1
        if winner is None:
            return 0
        return -1

    def train(self, episodes=10000):
        wins_x = wins_o = draws = 0
        for ep in range(1, episodes + 1):
            self.reset_game()
            history = []

            while True:
                state = self.board.copy_grid()
                action = self.agent.choose_action(self.board.grid, training=True)
                if action is None:
                    break
                history.append((state, action, self.current_player))
                self.board.place(action[0], action[1], self.current_player)

                winner = self.check_winner()
                if winner or self.board.is_full():
                    if winner == "X":
                        wins_x += 1
                    elif winner == "O":
                        wins_o += 1
                    else:
                        draws += 1

                    next_state = self.board.copy_grid()
                    for s, a, p in history:
                        reward = self.reward_for(winner, p)
                        self.agent.update_q_value(s, a, reward, next_state)
                    break
                self.swap_player()

            self.agent.decay_epsilon()
            self.board.render_training(
                ep, episodes, self.agent.epsilon, wins_x, wins_o, draws
            )
            if ep % 1000 == 0:
                wins_x = wins_o = draws = 0

        self.agent.save_model(self.MODEL_PATH)
        print()
        print(f"  {green('[ done ]')} training complete")
        print(f"  {gray('[ save ]')} model → {self.MODEL_PATH}")
        print(f"  {gray('[ info ]')} q-table size: {len(self.agent.q_table):,} states")
        print()
        input(f"  {cyan('press enter to return to menu')} ")

    def choose_mode(self):
        while True:
            self.board.render_main_menu()
            try:
                choice = input(f"  {cyan('root@qttt:~$')} ").strip().lower()

                if choice == "1":
                    self.mode = "pvp"
                    return
                if choice == "2":
                    self.mode = "random"
                    return
                if choice == "3":
                    if self.agent.load_model(self.MODEL_PATH):
                        print(f"  {green('[ ok ]')} model loaded from {self.MODEL_PATH}")
                        time.sleep(0.8)
                        self.mode = "ai"
                        return
                    print(
                        f"  {red('[ err ]')} model not found — "
                        "train the AI first (option 5)"
                    )
                    input(f"  {gray('press enter to continue')} ")
                    continue
                if choice == "4":
                    if self.agent.load_model(self.MODEL_PATH):
                        print(f"  {green('[ ok ]')} AI loaded for spectate mode")
                        time.sleep(0.8)
                        self.mode = "watch"
                        return
                    print(
                        f"  {red('[ err ]')} AI not trained — "
                        "train first (option 5)"
                    )
                    input(f"  {gray('press enter to continue')} ")
                    continue
                if choice == "5":
                    self.train()
                    answer = input(
                        f"  {yellow('play against the trained AI now?')} "
                        f"{gray('[y/N]')} "
                    ).strip().lower()
                    if answer == "y":
                        self.reset_game()
                        self.mode = "ai"
                        return
                    continue
                if choice == "q":
                    print(f"\n  {gray('bye.')}")
                    raise SystemExit(0)

                print(f"  {red('[ err ]')} invalid option")
                time.sleep(0.8)

            except KeyboardInterrupt:
                print(f"\n  {gray('bye.')}")
                raise SystemExit(0)

    def read_human_move(self):
        try:
            entry = input().strip().lower()
            if entry == "q":
                return False, None, None, "quit"
            if " " not in entry:
                return False, None, None, "use 'row col' separated by space (e.g. 1 2)"
            row, col = map(int, entry.split())
            if not (0 <= row <= 2 and 0 <= col <= 2):
                return False, None, None, "coordinates must be in range 0..2"
            if not self.board.is_empty(row, col):
                return False, None, None, "cell already occupied"
            return True, row, col, ""
        except ValueError:
            return False, None, None, "numbers only, separated by space"
        except KeyboardInterrupt:
            return False, None, None, "interrupt"

    def auto_move(self):
        time.sleep(1.2)
        if self.mode == "ai":
            return self.ai_move()
        if self.mode == "watch":
            if self.current_player == "X":
                return self.random_move()
            return self.ai_move()
        return self.random_move()

    def ask_play_again(self):
        while True:
            answer = input(
                f"\n  {yellow('play again?')} {gray('[y/N]')} "
            ).strip().lower()
            if answer == "y":
                return True
            if answer in ("n", ""):
                clear_screen()
                print(f"  {gray('bye.')}")
                return False
            print(f"  {red('[ err ]')} answer with y or n")

    def run(self):
        self.choose_mode()

        greetings = {
            "random": "you are X, bot is O. you play first.",
            "ai":     "you are X, AI is O. you play first.",
            "pvp":    "player X plays first.",
            "watch":  "spectating: random bot (X) vs trained AI (O).",
        }
        if self.mode in greetings:
            print(f"  {cyan('[ start ]')} {greetings[self.mode]}")
            time.sleep(1.5)

        while True:
            self.board.render(self.mode, self.current_player)

            if self.mode == "watch" or (
                self.mode in ("random", "ai") and self.current_player == "O"
            ):
                row, col = self.auto_move()
            else:
                ok, row, col, msg = self.read_human_move()
                if not ok and msg == "quit":
                    print(f"  {gray('bye.')}")
                    break
                if not ok and msg == "interrupt":
                    print(f"  {gray('interrupted.')}")
                    break
                if not ok:
                    print(f"  {red('[ err ]')} {msg}")
                    time.sleep(1)
                    continue

            if row is not None and col is not None:
                self.board.place(row, col, self.current_player)

            winner = self.check_winner()
            if winner or self.board.is_full():
                final = (
                    f"{green('[ win ]')} player {winner}"
                    if winner
                    else f"{yellow('[ draw ]')} no winner"
                )
                self.board.render(self.mode, self.current_player, final)
                if not self.ask_play_again():
                    break
                self.reset_game()
                continue

            self.swap_player()
