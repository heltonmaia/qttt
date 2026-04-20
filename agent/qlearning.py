"""Tabular Q-Learning agent for Tic-Tac-Toe."""

import pickle
import random
from collections import defaultdict


class QLearningAgent:
    def __init__(
        self,
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.9,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.1,
    ):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def state_key(self, grid):
        return "".join("".join(row) for row in grid)

    def valid_actions(self, grid):
        return [(i, j) for i in range(3) for j in range(3) if grid[i][j] == " "]

    def choose_action(self, grid, training=True):
        actions = self.valid_actions(grid)
        if not actions:
            return None

        if training and random.random() < self.epsilon:
            return random.choice(actions)

        key = self.state_key(grid)
        best_action, best_value = None, float("-inf")
        for a in actions:
            q = self.q_table[key][a]
            if q > best_value:
                best_value, best_action = q, a
        return best_action if best_action is not None else random.choice(actions)

    def update_q_value(self, state, action, reward, next_state):
        key = self.state_key(state)
        next_key = self.state_key(next_state)
        next_actions = self.valid_actions(next_state)
        max_next_q = max((self.q_table[next_key][a] for a in next_actions), default=0)
        current = self.q_table[key][action]
        self.q_table[key][action] = current + self.alpha * (
            reward + self.gamma * max_next_q - current
        )

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(dict(self.q_table), f)

    def load_model(self, filename):
        try:
            with open(filename, "rb") as f:
                loaded = pickle.load(f)
                self.q_table = defaultdict(lambda: defaultdict(float), loaded)
            return True
        except FileNotFoundError:
            return False

    def stats(self):
        return {
            "num_states": len(self.q_table),
            "epsilon": self.epsilon,
            "alpha": self.alpha,
            "gamma": self.gamma,
        }
