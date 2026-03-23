import json
import numpy as np
import multiprocessing
from Enviroment.truco_environment import TrucoEnvironment
from Agent.genetic_agent import GeneticAgent
from Utils.truco_utils import NumpyEncoder
from concurrent.futures import ProcessPoolExecutor, as_completed


def _simulate_agent_fitness(i, opponent_indices, agent_weights_list, AgentClass, MatchEnvClass, k):
    """
    Helper function to compute fitness for agent i against its sampled opponents.
    Unpickles weights into agents and runs games.
    """
    # Reconstruct agent objects from weights
    agent_i = AgentClass(predefined_weights=agent_weights_list[i])
    match_env = MatchEnvClass()
    total_score = 0.0
    for j in opponent_indices:
        opponent = AgentClass(predefined_weights=agent_weights_list[j])
        score, _ = match_env.game(agent_i, opponent)
        total_score += score
    return i, total_score / k


class GeneticEnvironment:
    def __init__(
        self,
        AgentClass,
        MatchEnv,
        initial_size=50,
        rank=10,
        mutation_rate=0.1,
        mutation_strength=0.1,
        k=2,
        depth=3,
        width=128,
        processes=None,
    ):
        """
        :param processes: number of parallel processes (defaults to cpu_count)
        """
        self.AgentClass = AgentClass
        self.MatchEnvClass = MatchEnv
        self.rank = rank
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.network_depth = depth
        self.k = k
        self.processes = processes or multiprocessing.cpu_count()

        # Initialize agents and extract weights for fast pickle
        self.agents = [AgentClass(depth=depth, width=width) for _ in range(initial_size)]
        self._update_weights_cache()

    def _update_weights_cache(self):
        # Flatten current populations' weights for parallel simulation
        self.agent_weights = [agent.weights for agent in self.agents]

    def train(self, generations):
        for gen in range(generations):
            self._new_generation()
            print(f"Generation: {gen + 1}/{generations}")
        # Final selection
        fitness = self._eval_fitness()
        top_two = np.argsort(fitness)[::-1][:2]
        return self.agents[top_two[0]], self.agents[top_two[1]]

    def _new_generation(self):
        fitness = self._eval_fitness()
        top_indices = np.argsort(fitness)[::-1][: self.rank]

        # Generate offspring in parallel
        offspring_weights = []
        for i in top_indices:
            for j in top_indices[: i + 1]:
                # average parent weights
                child_weights = [ (w1 + w2) / 2.0 for w1, w2 in zip(self.agent_weights[i], self.agent_weights[j]) ]
                offspring_weights.append(child_weights)

        # Apply mutation
        mutated = self._mutate_population(offspring_weights)
        # Reconstruct agents
        self.agents = [self.AgentClass(predefined_weights=w) for w in mutated]
        self._update_weights_cache()

    def _eval_fitness(self):
        # Sample opponents matrix
        N = len(self.agents)
        opponents = np.random.randint(0, N - 1, size=(N, self.k))
        rows = np.arange(N)[:, None]
        opponents += (opponents >= rows)

        fitness = np.zeros(N)
        # Parallel evaluation
        with ProcessPoolExecutor(max_workers=self.processes) as executor:
            futures = {
                executor.submit(
                    _simulate_agent_fitness,
                    i,
                    opponents[i],
                    self.agent_weights,
                    self.AgentClass,
                    self.MatchEnvClass,
                    self.k,
                ): i
                for i in range(N)
            }
            for future in as_completed(futures):
                idx, fit = future.result()
                fitness[idx] = fit

        return fitness

    def _mutate_population(self, weights_list):
        # Vectorized mutation across the population
        for w in weights_list:
            for i in range(len(w)):
                if np.random.rand() < self.mutation_rate:
                    w[i] += np.random.normal(0, self.mutation_strength, w[i].shape)
        return weights_list

if __name__ == "__main__":
    env = GeneticEnvironment(GeneticAgent, TrucoEnvironment)
    best_agent1, best_agent2 = env.train(100)
    truco_env = TrucoEnvironment()
    debug, p1, p2 = truco_env.match(best_agent1, best_agent2, 0, 0, debug=True)
    with open("../best_agents.json", "w", encoding="utf-8") as f:
        json.dump({"agent1_points": p1, "agent2_points": p2, "debug": debug}, f, cls=NumpyEncoder, ensure_ascii=False)