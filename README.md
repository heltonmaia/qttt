# qttt — Q-Learning Tic-Tac-Toe

A Python Tic-Tac-Toe with a **reinforcement-learning** agent. The AI learns by
playing against itself (self-play) and can then face humans, a random bot, or
another AI in spectate mode.

> **About the name:** `qttt` = **Q** (as in *Q-learning*) + **ttt** (as in
> *tic-tac-toe*). Short, pronounceable ("Q-triple-T") and faithful to what the
> project actually does: a tabular Q-learning agent playing tic-tac-toe.

---

## Project Structure

```
qttt/
├── main.py                    # Entry point
├── agent/
│   └── qlearning.py           # Tabular Q-Learning agent
├── game/
│   ├── board.py               # Board state + terminal rendering
│   └── engine.py               # Game engine / control flow
├── models/
│   └── qlearning_model.pkl    # Trained Q-table (generated after training)
├── utils/
│   ├── clear_screen.py        # Cross-platform screen clear
│   └── style.py               # ANSI color helpers
├── about_AI.md                # Q-learning math + agent hyperparameters
└── README.md                  # This file
```

---

## Running

```bash
git clone https://github.com/heltonmaia/qttt.git
cd qttt
python main.py
```

---

## Game Modes

* `1` human vs human
* `2` human vs random bot
* `3` human vs trained AI
* `4` spectate: random bot vs trained AI
* `5` train the AI (self-play)

---

## About the AI

The agent uses **Q-Learning**, a model-free reinforcement learning algorithm:

* Stores state-action values in a **Q-table** (plain dict, pickled to disk)
* Learns by trial and error, playing against itself
* Uses **ε-greedy** exploration with decay
* After training, the model is saved to `models/qlearning_model.pkl`

See `about_AI.md` for the math and hyperparameters.

---

## Requirements

* Python 3.6+
* No external dependencies (standard library only)

---

## License

Distributed under the MIT License. See `LICENSE` for details.
