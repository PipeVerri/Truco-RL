import asyncio
import websockets
from Agent.truco_agent import TrucoAgent

class PlayerAgent(TrucoAgent):
    def __init__(self):
        super().__init__()
