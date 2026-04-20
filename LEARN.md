# Learning Reinforcement Learning with qttt

A short, hands-on lecture. Read top to bottom — it builds step by step.
The code references in each section point to the exact file and line where
that idea lives in this repo.

> **Who this is for:** someone who knows basic Python and has heard the term
> "reinforcement learning" but never written an RL agent. We start from the
> very beginning and end at the point where you could meaningfully extend
> qttt or move on to harder RL problems.

---

## Contents

- [Why tic-tac-toe?](#why-tic-tac-toe)
- [The reinforcement learning setup](#the-reinforcement-learning-setup)
- [States, actions, rewards](#states-actions-rewards)
- [Policies and value functions](#policies-and-value-functions)
- [The Q-function](#the-q-function)
- [The Bellman equation, intuitively](#the-bellman-equation-intuitively)
- [Q-learning, step by step](#q-learning-step-by-step)
- [Exploration vs. exploitation (ε-greedy)](#exploration-vs-exploitation-ε-greedy)
- [Self-play: two agents, one brain](#self-play-two-agents-one-brain)
- [Reading the training output](#reading-the-training-output)
- [What tabular methods cannot do](#what-tabular-methods-cannot-do)
- [Where to go next](#where-to-go-next)

---

## Why tic-tac-toe?

Tic-tac-toe is the "hello world" of RL for three specific reasons:

1. **Tiny state space.** Every possible board can be reached by one of only
   ~5,000 positions. That means we can literally store a value for *every
   single (state, action) pair* as a Python dictionary. No neural networks
   needed. This is called the **tabular** setting — "table" because the
   learned values fit in a table.

2. **Very short episodes.** A game ends after at most 9 moves, so the agent
   gets fast feedback. Training 10,000 full games takes about 10 seconds on
   a laptop. Compare that to Atari games, where episodes can last minutes
   and training takes GPU-days.

3. **Deterministic, perfect-information, zero-sum.** The cleanest possible
   RL setting — no randomness in the environment, both players see
   everything, and one player's win is the other's loss. Great for
   building intuition before moving to harder problems.

In return for this simplicity, tic-tac-toe teaches most of the *essential*
RL ideas. The same algorithm you see here generalizes, with tweaks, all the
way to chess, Go, and Atari games.

---

## The reinforcement learning setup

Reinforcement learning studies how an **agent** should act inside an
**environment** to maximize a **reward** signal over time.

```
         ┌──────────────────┐
         │                  │      action
         │     AGENT        │ ─────────────►
         │  (the learner)   │
         │                  │ ◄─────────────
         └──────────────────┘   state, reward
                                (+rules of the world)
                         from the
                                     ▼
                          ┌──────────────────┐
                          │   ENVIRONMENT    │
                          │  (the board, the │
                          │   rules, the     │
                          │   opponent…)     │
                          └──────────────────┘
```

At every step the agent:

1. observes the current **state** of the world,
2. picks an **action**,
3. the environment transitions to a new state and returns a scalar
   **reward**.

The agent's *only* feedback is that scalar reward. There's no labelled
dataset telling it what the right answer was — it has to figure out, by
itself, which sequences of decisions lead to high cumulative reward.

This is fundamentally different from supervised learning. In supervised
learning you already know the right label for every input. In RL you only
find out if a decision was good after playing it all the way to the end.

---

## States, actions, rewards

Let's make all three concrete for qttt.

### State `s`

A **state** is "everything the agent needs to know right now to make a
decision." In qttt, that's the 3×3 board.

We represent it as a string of 9 characters:
- `'X'` or `'O'` for played cells
- `' '` (space) for empty cells

Example: a board with `X` in the top-left and `O` in the center is stored as
the string `'X   O    '`.

The string form is convenient because strings are hashable → we can use
them as dictionary keys.

> **In code:** [`agent/qlearning.py::state_key`](agent/qlearning.py) turns
> a 3×3 grid into this string.

### Action `a`

An **action** is a choice the agent can make in a given state. In qttt, an
action is a `(row, col)` tuple pointing to any empty cell.

The set of valid actions is different in every state — early in the game
there are 9 choices, by the last move there's often only 1.

> **In code:** [`agent/qlearning.py::valid_actions`](agent/qlearning.py)
> returns the empty cells in the current board.

### Reward `r`

A **reward** is a scalar the environment gives back after the agent acts.
In qttt we only hand out reward at the **end** of a game:

| Outcome | Reward |
|---------|--------|
| Win     | +1     |
| Draw    |  0     |
| Loss    | −1     |

Notice what's missing: we don't reward "blocking the opponent's three-in-a-row"
or "taking the center on move 1". Those are human heuristics, and the whole
point of RL is that the agent discovers them on its own, by tracing the final
reward back through the moves that earned it.

This property — reward arriving only at the end, not after every move — is
called **sparse reward**, and it's one of the defining challenges of RL.

> **In code:** [`game/engine.py::reward_for`](game/engine.py) — the
> terminal reward function.

---

## Policies and value functions

RL has three important quantities that build on each other:

### Policy `π`

A **policy** is a strategy: a function that tells the agent what to do.

```
π : state → action
```

A good policy picks actions that lead to high long-term reward. The whole
point of training is to find the best policy `π*`.

### State value `V(s)`

The **value of a state** is the total reward the agent *expects* to collect
from state `s`, if it follows policy `π` from now until the game ends.

```
V^π(s) = expected sum of future rewards starting from s under policy π
```

Intuitively: a board where the agent is about to win has high value; a
board where the agent is about to lose has low value.

### Action value `Q(s, a)`

The **value of an action in a state** is the expected total future reward
if the agent takes action `a` in state `s`, and then follows policy `π`.

```
Q^π(s, a) = expected sum of future rewards after doing a in s, then π
```

`Q` is more useful than `V` because it tells you *which action* to pick.
If you know `Q(s, a)` for every action, the optimal move is simply
`argmax_a Q(s, a)` — "pick the action with the biggest expected reward."

qttt learns the **Q-function** directly. That's what gives Q-learning its
name.

---

## The Q-function

In the tabular setting, `Q` is literally a dictionary:

```python
Q = {
    ('X    O   ', (0, 0)): 0.42,
    ('X    O   ', (0, 1)): 0.11,
    ('X    O   ', (0, 2)): 0.78,
    …
}
```

Each key is `(state_string, (row, col))` and each value is the agent's best
current estimate of the expected future reward for that move.

At the start of training every entry is `0.0` (we use a `defaultdict`).
Over many games, the values drift toward the true `Q*` — the action-values
the agent would have under *optimal* play.

At play time the agent just looks up every empty cell in the current state,
picks the `(row, col)` with the highest Q-value, and plays it. That's the
whole policy.

> **In code:** [`agent/qlearning.py::choose_action`](agent/qlearning.py) —
> the `argmax` over valid actions is the agent's greedy policy.

---

## The Bellman equation, intuitively

The central equation in RL is the **Bellman equation**. For the optimal
action-value function `Q*`, it says:

```
Q*(s, a)  =  r  +  γ · max_{a'} Q*(s', a')
```

Translating to English:

> The value of doing action `a` in state `s` equals the reward you get
> *right now*, **plus** (discounted by γ) the best value you could get
> starting from whatever state `s'` you end up in.

This is just "future planning by one step." You don't need to look to the
end of the game. If you know what the best you could do from the *next*
state is, that's enough — the equation says the current value is just one
step of reward plus the next state's value.

### The discount factor `γ`

`γ` (gamma) is a number between 0 and 1 that says *how much the agent
cares about future reward vs. immediate reward*.

- `γ = 0` → agent is completely short-sighted; only cares about the next
  reward.
- `γ = 1` → agent weighs a reward in 10 moves just as highly as one now.
- `γ = 0.9` (our choice) → a reward 2 moves away is worth `0.9² = 0.81` of
  the same reward right now; 5 moves away, `0.9⁵ ≈ 0.59`.

In tic-tac-toe, where games end quickly, `γ = 0.9` is a gentle preference
for faster wins. With a smaller `γ` the agent would be willing to trade
future reward for a quicker payoff; with `γ = 1` it would just care about
winning, regardless of in how many moves.

---

## Q-learning, step by step

We don't start out knowing `Q*`. We start with a completely empty
(all-zero) Q-table, and we *update* it every time the agent plays a move
and sees what happens.

The Q-learning update rule is:

```
Q(s, a)  ←  Q(s, a)  +  α · [ r + γ · max_{a'} Q(s', a')  −  Q(s, a) ]
```

Look at it as three pieces:

| Piece | Meaning |
|-------|---------|
| `Q(s, a)` on the right | our **current guess** |
| `r + γ · max Q(s', a')` | a **better guess** (Bellman's right-hand side using one real step of experience) |
| `[better − current]` | the **error** — how wrong our current guess was |
| `α · error` | a **small correction** toward the better guess |

The **learning rate `α`** controls how big a step we take each update:

- `α = 1` → replace old value entirely with the new estimate. Jittery.
- `α = 0` → never update. Dead.
- `α = 0.1` (our choice) → nudge 10% of the way from old to new. Stable.

Over many updates the Q-table converges to `Q*`. This is proven to work
under mild assumptions — every (state, action) pair must be visited
infinitely often, and `α` should decay to zero (for us `α = 0.1` is
constant, which works fine in practice for a finite problem like this).

> **In code:** [`agent/qlearning.py::update_q_value`](agent/qlearning.py) —
> a one-liner implementing exactly this formula.

---

## Exploration vs. exploitation (ε-greedy)

Here's the catch. The update rule only improves Q-values for states and
actions the agent actually tries. If the agent always picks its current
best action, it will never discover that a move it thinks is mediocre is
actually great once you explore it further.

This is the **exploration vs. exploitation dilemma**:

- **Exploit** → pick the action you currently think is best (use what you
  know).
- **Explore** → pick a random action (find out more about the world).

Neither extreme works. Pure exploitation → agent gets stuck with whatever
it happened to learn first. Pure exploration → agent never commits to
winning strategies.

The simplest balance is **ε-greedy**:

```
with probability ε  : explore (pick a random valid action)
with probability 1-ε : exploit (pick argmax Q(s, a))
```

We start with `ε = 0.9` (mostly explore — we don't know anything yet), and
decay it each episode by multiplying `ε ← ε · 0.995`, clamped to a floor
of `ε_min = 0.1`. After ~460 episodes `ε` has decayed to 0.1, so for the
remaining 9,540 episodes the agent exploits 90% of the time and still
explores 10% — enough to keep discovering rare states.

> **In code:**
> [`agent/qlearning.py::choose_action`](agent/qlearning.py) implements the
> ε-greedy branch; `decay_epsilon` applies the multiplicative decay each
> episode.

---

## Self-play: two agents, one brain

Tic-tac-toe is a two-player game. Who plays the opponent during training?

The clever answer is: **the same agent plays both sides**. That's called
**self-play**, and it's the same trick that powers AlphaZero.

### How qttt trains

For each of 10,000 episodes:

1. **Reset** the board to empty; start with `X` to move.
2. **Play a full game**:
   - At each turn, the current player (X or O) uses ε-greedy on the
     shared Q-table to pick an action.
   - Record every `(state, action, player_whose_turn_it_was)` tuple in a
     history list.
   - Swap the current player and repeat until someone wins or the board
     fills up.
3. **Compute the terminal reward** from each player's perspective:
   `+1` if they won, `-1` if they lost, `0` if draw.
4. **Backpropagate the reward** to every move in the history, applying the
   Q-learning update with that player's signed reward.
5. **Decay ε** and move on to the next episode.

> **In code:** [`game/engine.py::train`](game/engine.py) is the full
> training loop in ~30 lines.

### Why self-play works

At first the agent is terrible on both sides, so X beats O as often as it
loses. But any lucky win by one side gets reinforced in the Q-table, which
makes *both* sides slightly better next time (they share a brain). Over
10,000 episodes the two sides ratchet each other up toward optimal play.

Interesting consequence: since tic-tac-toe with optimal play always ends in
a draw, a fully-converged self-play agent will draw itself every single
game. You can watch this happen in the training log — the share of draws
climbs toward 100% as training goes on.

---

## Reading the training output

When you run option 5, qttt prints progress every 1,000 episodes:

```
  ep  10,000/10,000 [█████████████████████████████████████████████████] 100.0%
  ε 0.100   last 1k → X: 198  O: 601  draw: 201
```

Line 1 is a progress bar.

Line 2 has three things:
- **`ε`** — current exploration rate. Starts at 0.900, decays toward 0.100.
- **`last 1k → X/O/draw`** — how the previous 1,000 episodes went.

You'll typically see:

- Early episodes: lots of wins for whoever-moves-first (`X`) because O is
  still exploring randomly.
- Middle episodes: O catches up; draws start climbing.
- Later episodes: draws dominate (300–500 of the last 1,000 episodes) and
  the rest are roughly balanced between X and O wins.

If you ever see one side winning almost 100% of games late in training,
something is broken — that would mean the agent found a policy the other
side can't counter, which is impossible in solved tic-tac-toe.

---

## What tabular methods cannot do

qttt works because tic-tac-toe has ~5,000 reachable states. We can store
every one.

That trick breaks the moment the state space gets bigger:

- **Chess** has ~10⁴⁰ legal positions. Even if each entry is 1 byte, the
  table wouldn't fit on Earth.
- **Go** has ~10¹⁷⁰.
- **Atari games** have state spaces defined by pixel values — effectively
  continuous.

For those, we can't enumerate states. We need to **approximate** `Q(s, a)`
with a function whose parameters we can fit from data — typically a neural
network. That's what turns "Q-learning" into **Deep Q-Learning (DQN)**,
the algorithm DeepMind used to master Atari in 2015.

The core ideas you learned here — states, actions, rewards, discount
factor, exploration, the Bellman equation, the Q-learning update — all
carry over to DQN and further to modern methods like PPO and AlphaZero.
The only thing that changes is *how* we represent `Q`.

---

## Where to go next

If you want to extend qttt:

- **Add a tougher opponent.** Train two separate Q-tables, one for X and
  one for O, and let them play each other. Compare to the shared-brain
  self-play.
- **Minimax baseline.** Implement a perfect tic-tac-toe player using
  minimax and measure how often the trained agent beats it. (Answer:
  never; a good trained agent should draw every game, which is what
  minimax would force.)
- **Sarsa instead of Q-learning.** Sarsa uses the *actually chosen* next
  action instead of `max`. Compare stability and final quality.
- **Eligibility traces.** Propagate reward backward with a decay factor
  `λ` instead of a single-step update. This is TD(λ).

If you want to leave the tabular setting:

- **Connect Four.** ~10¹³ positions — still enumerable with effort, but
  worth trying Deep Q-Learning.
- **Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed).**
  The standard textbook, free online, and hugely readable.
- **Spinning Up in Deep RL** (OpenAI). A practical intro to policy
  gradients, PPO, and friends — after you're comfortable with the ideas
  above.

Happy hacking.
