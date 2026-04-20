# qttt — Q-Learning Tic-Tac-Toe

A Python Tic-Tac-Toe where the computer player is a **reinforcement-learning
agent**. No neural network, no external dependencies — just a classical
**tabular Q-learning** agent that learns by playing millions of games against
itself and then sits down to play with you.

> **About the name:** `qttt` = **Q** (as in *Q-learning*) + **ttt** (as in
> *tic-tac-toe*). Short, pronounceable ("Q-triple-T") and faithful to what the
> project actually does.

---

## In action

**Main menu**

![main menu](docs/menu.svg)

**Gameplay (human vs trained AI)**

![gameplay](docs/gameplay.svg)

**Self-play training**

![training](docs/training.svg)

---

## A gentle intro to Reinforcement Learning

**Reinforcement learning (RL)** is how you teach a program to make decisions
when nobody hands it a labelled dataset. Instead, the program (the *agent*)
tries things in an environment, observes the outcome, and receives a scalar
**reward**. Its job is to figure out, through trial and error, which sequences
of actions lead to high total reward.

For tic-tac-toe:

| RL concept        | In qttt                                            |
|-------------------|----------------------------------------------------|
| **Environment**   | The 3×3 board + the rules of the game              |
| **Agent**         | The Q-learning player                              |
| **State `s`**     | A snapshot of the board, e.g. `"X OX  O X"`        |
| **Action `a`**    | Picking an empty cell `(row, col)`                 |
| **Reward `r`**    | `+1` for a win, `-1` for a loss, `0` for a draw    |
| **Policy**        | A function `state → action` the agent learns       |

The trick: the reward only arrives at the **end** of the game. Placing a good
move in turn 2 doesn't get an immediate reward — you have to wait nine turns
to find out if it led to a win. RL's whole point is to back-propagate the
final reward through the earlier moves that made it possible.

### Why tic-tac-toe is the "hello world" of RL

1. **Tiny state space.** There are only ~5,000 reachable board positions, so
   we can store a value for *every single state-action pair* in memory — no
   need for a neural network to approximate anything.
2. **Short games.** Each episode ends in at most 9 moves, so the agent gets
   fast feedback and training finishes in seconds.
3. **Perfect-information, deterministic, zero-sum.** The cleanest possible
   RL setting — great for building intuition before moving to chess, Go or
   Atari.

### Q-learning in one paragraph

The agent keeps a **Q-table**: a big dictionary mapping
`(state, action) → expected future reward`. When it makes a move and sees
what happens next, it nudges that Q-value toward the reward it observed plus
the best Q-value available from the new state. Over many games, these nudges
converge to the *optimal* action-value function: `Q*(s, a)`. At play time,
the agent just picks the action with the highest Q-value in the current
state — that's its learned policy.

The update rule (Bellman equation):

```
Q(s, a) ← Q(s, a) + α · [ r + γ · max Q(s', a')  −  Q(s, a) ]
```

- `α` (alpha) — **learning rate**. How much each new experience updates the old estimate. Too high → jittery; too low → slow.
- `γ` (gamma) — **discount factor**. How much the agent values future reward vs. immediate. With γ=0.9, a reward two moves away is worth `0.9² ≈ 0.81` of the same reward right now.
- `max Q(s', a')` — the best the agent *thinks* it can do from the next state. This is what lets reward flow backwards through a game.

### Explore vs. exploit (ε-greedy)

If the agent only ever picks the action it currently thinks is best, it will
never discover that a move it has low confidence in might actually be great.
So during training we use **ε-greedy**: with probability `ε` the agent
picks a random action (**explore**), otherwise it picks the best one it
knows (**exploit**). `ε` starts high (0.9 — mostly exploring) and decays
(`ε ← ε · 0.995`) until it bottoms out at `0.1`. By then the agent has seen
enough of the game tree to lean on what it has learned.

### How qttt actually trains

The training loop uses **self-play**: the same agent plays both X and O. For
each episode we:

1. Play a full game, recording every `(state, action, player)` tuple along
   the way.
2. When the game ends, compute the reward from each player's perspective
   (`+1 / 0 / −1`).
3. Walk the tuples back through the Q-learning update rule, propagating the
   terminal reward into the Q-values of every move that led to it.
4. Decay ε and move on to the next game.

After **10,000 episodes** the Q-table has learned values for ~4,000 states —
enough to play near-optimally. Against a random opponent it wins or draws
almost every game; against a perfect player it forces a draw, which is the
best anyone can do at tic-tac-toe.

See [`about_AI.md`](about_AI.md) for the math details and hyperparameter
choices.

---

## Running

```bash
git clone https://github.com/heltonmaia/qttt.git
cd qttt
python main.py
```

No dependencies to install — uses only the Python standard library.

---

## Game Modes

| # | Mode                                                  |
|---|-------------------------------------------------------|
| 1 | human vs human                                        |
| 2 | human vs random bot                                   |
| 3 | human vs trained AI (requires trained model)          |
| 4 | spectate: random bot vs trained AI                    |
| 5 | train the AI (self-play, ~10s)                        |

---

## Project Structure

```
qttt/
├── main.py                    # Entry point
├── agent/
│   └── qlearning.py           # Tabular Q-learning agent
├── game/
│   ├── board.py               # Board state + terminal rendering
│   └── engine.py              # Game loop / control flow
├── models/
│   └── qlearning_model.pkl    # Trained Q-table (generated after training)
├── utils/
│   ├── clear_screen.py        # Cross-platform screen clear
│   └── style.py               # ANSI color helpers
├── docs/
│   ├── make_screenshots.py    # Regenerate the SVGs below
│   ├── menu.svg
│   ├── gameplay.svg
│   └── training.svg
├── about_AI.md                # Q-learning math + hyperparameters
└── README.md
```

---

## Requirements

* Python 3.6+
* No external dependencies (standard library only)

---

## License

Distributed under the MIT License. See `LICENSE` for details.
