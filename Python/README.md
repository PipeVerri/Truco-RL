# Python — Technical Details

This document covers the agent architecture, input/output encoding, game environment, and training algorithm.

---

## Neural Network Architecture

Each agent is a **multilayer perceptron (MLP)** implemented from scratch using NumPy. No ML framework is used.

![](/docs/nn-architecture.png)

The output is passed through a **validity mask** before taking the argmax — the agent can never choose an action that is illegal given the current game state (e.g., singing retruco before truco has been sung).

---

## Input Encoding (79 neurons)

### Cards (45 neurons)

Three groups of 3 cards each — my hand, my played cards, opponent's played cards — encoded identically. Each card takes **5 neurons**:

| Neuron | Value |
|---|---|
| 1 | Power ranking (integer, 1–14; 0 if slot is empty) |
| 2–5 | Suit one-hot (espadas / bastos / oros / copas; all zeros if slot is empty) |

Cards in hand are sorted by power (ascending) at the start of each round. When a card is played, its slot is zeroed out (power=0, suit all zeros).

The motivation behind the card sorting is so that the order of the cards doesn't matter, playing the first card always means playing the strongest one.

### Hand state (9 neurons)

One 3-element one-hot vector per hand (3 hands total), from this agent's point of view:

`[won, lost, tied]` — all zeros if that hand hasn't been played yet.

### Hand criticality (4 neurons)

Two 2-element vectors — one for this agent, one for the opponent — encoding what outcomes are still mathematically possible for the current hand being played:

`[can_tie_without_losing, can_lose]`

These depend on the hand index and prior outcomes:
- **Hand 0:** both outcomes are always possible → `[1, 1]`
- **Hand 1:** depends on who won hand 0 (e.g. if you lost hand 0, you must win hand 1 to stay alive — tying the hand is no longer safe)
- **Hand 2:** depends on the combination of hand 0 and hand 1 outcomes

This tells the agent whether it is in a must-win, can-afford-to-tie, or already-safe situation without needing to reason over the hand history itself.

### Envido points (1 neuron)

Best envido score the agent can form from its current 3 cards. In Truco, envido is scored by taking two cards of the same suit and summing their envido values plus 20 (or the single best card if no two cards share a suit). The agent gets the computed maximum.

### Falta envido stakes (2 neurons)

Only non-zero when falta envido has actually been sung (`envido_state == 4`):

`[points_I_would_win, points_opponent_would_win]`

Falta envido awards the points needed to reach 30, so its value depends on each player's current score — hence both are provided separately.

### Point insights (3 neurons)

```
[30 - my_points,  30 - opponent_points,  my_points - opponent_points]
```

Points are encoded as *distance to 30* rather than points accumulated, because what matters strategically is how close each player is to winning, not what they've already scored. The third neuron captures the margin between players.

### Truco possibilities (3 neurons)

`[can_sing_truco, can_sing_retruco, can_sing_vale4]`

Each is 1 only if that exact escalation step is available to this agent right now.

### Current truco state (encoded inside canto status, see below)

Even though the truco possibility flags above tell the agent what it *can* sing, they don't fully describe *why* certain options are unavailable. If retruco can't be sung, it could mean (a) truco was never called, or (b) the opponent has already called it. The truco state scalar removes that ambiguity.

### Envido possibilities (4 neurons)

`[can_sing_envido, can_sing_doble, can_sing_real, can_sing_falta]`

Each is 1 if that escalation step is reachable from the current envido state.

### Canto status (2 neurons)

```
[truco_points_at_stake,  envido_points_accumulated]
```

- `truco_points_at_stake` = `truco_state + 1` (so: 1 if no truco, 2 if truco, 3 if retruco, 4 if vale 4)
- `envido_points_accumulated` = total envido points put on the table so far (e.g. envido + envido = 4)

### Envido acceptance vector (4 neurons)

One-hot encoding of how envido resolved, from this agent's perspective. All zeros until envido concludes:

`[won_by_me, won_by_opponent, rejected_by_me, rejected_by_opponent]`

### Opponent's points (1 neuron)

Raw score of the opponent (0–30). Used alongside the point insights above.

### Current hand index — mano (1 neuron)

Which of the 3 hands within the round is being played (0, 1, or 2).

---

## Output Encoding (15 neurons)

| Neurons | Action |
|---|---|
| 0–2 | Play card 1 / 2 / 3 |
| 3–5 | Sing truco / retruco / vale 4 |
| 6–9 | Sing envido / doble envido / real envido / falta envido |
| 10–11 | Accept / reject truco |
| 12–13 | Accept / reject envido |
| 14 | Fold (ir al mazo) |

---

## Game Environment

The Truco simulator (`Enviroment/truco_environment.py`) implements the full game:

- **Deck:** 40 cards (Spanish deck), with power rankings matching Argentine Truco rules
  - Strongest: 1 of swords (14), 1 of clubs (13), 7 of swords (12), 3s (10), 2s (9)...
- **Match:** first to 30 points wins
- **Hand:** 3 tricks per hand; each trick's winner is tracked
- **Cantos:** truco escalation (truco → retruco → vale 4) and envido escalation (envido → doble → real → falta envido)
- **Action queue:** a deque manages whose turn it is and which responses are pending (e.g., after truco is sung, the opponent must respond before play continues)
- **Debug output:** every action is serialized to JSON with the full game state snapshot, which is what the Godot visualizer consumes

---

## Genetic Algorithm

Training is implemented in `Enviroment/GeneticEnvironment.py` using `ProcessPoolExecutor` for parallel evaluation.

### Hyperparameters (defaults)

| Parameter | Default | Description |
|---|---|---|
| `initial_size` | 50 | Population size |
| `rank` | 10 | Top agents selected per generation |
| `mutation_rate` | 0.1 | Fraction of weights mutated |
| `mutation_strength` | 0.1 | Std dev of Gaussian noise applied |
| `k` | 2 | Opponents per agent in tournament |
| `depth` | 3 | Hidden layer count |
| `width` | 128 | Hidden layer width |

### Algorithm per generation

1. **Evaluate** — each agent plays against `k` random opponents; fitness = total points won
2. **Select** — keep top `rank` agents
3. **Crossover** — generate offspring by averaging weight matrices of all rank² parent pairs
4. **Mutate** — apply Gaussian noise to each weight with probability `mutation_rate`
5. **Replace** — new population is entirely composed of mutated offspring

After `N` generations, the two best agents by fitness score are returned.

### Training example

```python
env = GeneticEnvironment(
    GeneticAgent, TrucoEnvironment,
    initial_size=50, rank=10,
    mutation_rate=0.2, mutation_strength=0.05,
    k=2
)
best_agent1, best_agent2 = env.train(200)
```

---

## Observed Behaviors

After 200 generations, agents are not random — they converge on consistent strategies. The most notable:

**Emergent bluffing:** agents learn to sing *falta envido* on the very first hand regardless of their actual envido score. Falta envido wagers a large variable number of points (enough to potentially end the game), so singing it early — even with a weak hand — puts maximum pressure on the opponent. This is a legitimate aggressive strategy in human play, and the agents discovered it without it being encoded anywhere.

---

## Project Structure

```
Python/
├── Agent/
│   ├── truco_agent.py          # Base agent class (input building, output masking)
│   └── genetic_agent.py        # MLP agent with NumPy forward pass
├── Enviroment/
│   ├── truco_environment.py    # Full Truco game simulator
│   └── GeneticEnvironment.py   # Parallel genetic training loop
├── Interactivity/
│   └── visualizer.py           # WebSocket server for Godot visualization
├── Utils/
│   └── truco_utils.py          # Hand criticality, falta envido calculation
├── best_agents.json            # Debug trace of best trained match
├── best_agent_weights.pkl      # Serialized weights of best agents
└── requirements.txt
```
