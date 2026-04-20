# Understanding Q-Learning in qttt

This document explains the math and practical logic behind the AI used in this
Q-Learning Tic-Tac-Toe project.

---

## What is Q-Learning?

**Q-Learning** is a reinforcement learning algorithm that lets an agent learn
an optimal action policy through trial, error, and rewards — no model of the
environment required.

---

## The Update Equation

The formula used to update Q-values is:

```
Q(s, a) ← Q(s, a) + α * [ r + γ * max(Q(s', a')) - Q(s, a) ]
```

Where:

- `s` → current state
- `a` → action taken
- `r` → reward received after the action
- `s'` → next state
- `α` (alpha) → learning rate
- `γ` (gamma) → discount factor for future rewards
- `max Q(s', a')` → best estimated value for the next move

---

## How it maps to the game

### States (`s`)
Board representations as a string, e.g. `'XOX O X O'`.

### Actions (`a`)
Coordinates of an empty cell, e.g. `(0, 2)`.

### Rewards (`r`)
- Win: `+1`
- Loss: `-1`
- Draw: `0`

---

## Exploration vs Exploitation

The agent uses **ε-greedy**:

- **Explore** new moves with probability `ε`
- **Exploit** learned moves with probability `1 - ε`

`ε` decays over time:

```python
epsilon *= epsilon_decay  # until epsilon_min
```

---

## Agent hyperparameters

```python
alpha = 0.1          # learning rate
gamma = 0.9          # discount factor
epsilon = 0.9        # initial exploration rate
epsilon_decay = 0.995
epsilon_min = 0.1
```

---

## Why Q-Learning fits Tic-Tac-Toe

- Small state space (~5k reachable states)
- Agent can train by playing against itself
- Fast, unsupervised learning

---

## Result

After training, the AI plays competitively against humans and random bots.
The model is saved to:

```
models/qlearning_model.pkl
```
