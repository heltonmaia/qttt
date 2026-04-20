# qttt — Q-Learning Tic-Tac-Toe

A tabular Q-learning agent that learns Tic-Tac-Toe by playing millions of
games against itself. No neural networks, no dependencies — just classical
reinforcement learning you can read end-to-end in about 300 lines of Python.

qttt ships in **two flavors** — the same game, same pre-trained model, same
Python source:

- a **terminal** version you run locally with `python main.py`, which also
  lets you retrain the agent from scratch;
- a **web** version that runs the exact same Python code in your browser via
  [Pyodide](https://pyodide.org/), with no backend and nothing to install.

Pick whichever is closer to hand — they share the same game loop.

---

## Play

### In your browser
**[Open the web version →](https://heltonmaia.github.io/qttt/web/)**

The Python code is shipped to your browser and run on a WebAssembly Python
runtime (Pyodide). Training is disabled here because it would happen on your
machine; play against the pre-trained model instead.

### In your terminal

```bash
git clone https://github.com/heltonmaia/qttt.git
cd qttt
python main.py
```

Requires Python 3.6+. No dependencies. This is the only version that can
retrain the agent (mode 5).

---

## Modes

| # | Mode                                               |
|---|----------------------------------------------------|
| 1 | human vs human                                     |
| 2 | human vs random bot                                |
| 3 | human vs trained AI                                |
| 4 | spectate: random bot vs trained AI                 |
| 5 | train the AI (self-play, ~10s) *(terminal only)*   |

A pre-trained model ships in `models/qlearning_model.pkl`, so you can jump
straight into modes 3 and 4 without training first. The web version uses
this same pre-trained model.

---

## Screenshots

![main menu](docs/menu.svg)

![gameplay](docs/gameplay.svg)

![training](docs/training.svg)

---

## Want to understand how it works?

See **[LEARN.md](LEARN.md)** — a short, self-contained lecture on
reinforcement learning built around this codebase. Covers states, actions,
rewards, Q-learning, the Bellman equation, ε-greedy, self-play, and where
to go after tabular methods.

---

## License

MIT — see `LICENSE`.
