import pickle
from truco_environment import TrucoEnvironment
from Agent.genetic_agent import GeneticAgent
import json
from truco_utils import NumpyEncoder

with open("../best_agent_weights.pkl", "rb") as f:
    best_weights = pickle.load(f)

agent1 = GeneticAgent(predefined_weights=best_weights)
agent2 = GeneticAgent(predefined_weights=best_weights)

truco_env = TrucoEnvironment()
debug, p1, p2 = truco_env.match(agent1, agent2, 0, 0, debug=True)

with open("../best_match.json", "w", encoding="utf-8") as f:
    json.dump({"agent1_points": p1, "agent2_points": p2, "debug": debug}, f, cls=NumpyEncoder, ensure_ascii=False)
