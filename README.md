# Truco-RL

> Two neural network agents learning to play Truco through a genetic algorithm.

**[▶ Watch Demo on YouTube](https://youtu.be/MAPCtqJ6L4A)**

---

## What is this?

Truco is a trick-taking card game where **deception is a core mechanic**. Players can sing challenges (truco, envido) regardless of the strength of their hand — bluffing is not just allowed, it's often the right play. This makes it a richer problem than games like Poker, where bluffing is primarily expressed through betting patterns and tells, not through strategic vocal choices mid-round.

This project trains two MLP agents to play Truco against each other using a **genetic algorithm** rather than traditional reinforcement learning. Agents evolve over generations by competing in tournaments, with the best performers reproducing and mutating.

### Observed behavior

After training, the agents don't play randomly — they develop patterns. One consistent emergent behavior: **agents learn to sing _falta envido_ on the very first hand, regardless of their actual envido points**. This is a high-risk bluff that pressures the opponent into accepting or rejecting a large point wager early. It's a real strategy used by human players, and the agents discovered it on their own.

---

## Architecture

![](/docs/architecture.png)

**Neural network:** 79 input neurons → 3 hidden layers (128 neurons each, ReLU) → 15 output neurons (softmax + action mask)

**Training:** Parallel genetic algorithm — population of 50 agents, tournament selection, weight averaging crossover, Gaussian mutation.

→ See [Python/README.md](Python/README.md) for a full breakdown of the network architecture, input encoding, and training details.

---

## Tech Stack

| Component | Technology |
|---|---|
| Game simulation & training | Python 3, NumPy |
| Agent architecture | Custom MLP (no ML framework) |
| Communication | WebSockets (`websockets` library) |
| Visualization | Godot 4 (GDScript) |

---

## How to Run

### 1. Train agents

Adjust hyperparameters inside the file, then run:

```bash
cd Python
python -m Enviroment.GeneticEnvironment
```

This outputs `best_agent_weights.pkl` and `best_agents.json` (a full debug trace of the best match found).

### 2. Start the visualization server

```bash
cd Python
python -m Interactivity.visualizer
```

The server listens on `ws://localhost:8080` and serves the match trace step by step.

### 3. Open the Godot project

Open `Godot/` in Godot 4, then run the game. Use the **"Siguiente jugada"** (Next play) button to step through each action in the match.

### Dependencies

```bash
pip install -r Python/requirements.txt
```

---

## The game's UI
- The green/red squares below the played cards mean that:
  - If the square is green, the mano has won the hand
  - If the square is red, the pie has won the hand
- The godot logo on each player indicates if it's their turn

---

## Project Status

**Paused WIP.** Training and visualization are functional. Planned next steps:

- [ ] Human vs. agent mode
- [ ] Replace genetic algorithm with actual RL (e.g. PPO or MCTS)