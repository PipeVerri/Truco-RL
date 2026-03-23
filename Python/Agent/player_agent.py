import asyncio
import websockets
from Agent.truco_agent import TrucoAgent

# TODO: Allow the player to plain against the agent
class PlayerAgent(TrucoAgent):
    def __init__(self):
        super().__init__()
