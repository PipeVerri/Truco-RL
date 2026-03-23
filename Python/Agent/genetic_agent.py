import numpy as np
from Agent.truco_agent import TrucoAgent

class GeneticAgent(TrucoAgent):
    def __init__(self, depth=3, width=128, seed=None, predefined_weights=None):
        super().__init__()
        # Init weights randomly. 76 inputs, 13 outputs

        if predefined_weights is not None:
            weights = predefined_weights
        else:
            if seed is not None:
                np.random.seed(seed)
            weights = [np.random.uniform(-1, 1, (width, 79 + 1))]  # +1 for bias
            if depth > 1:
                for _ in range(depth - 1):
                    weights.append(np.random.uniform(-1, 1, (width, width + 1)))  # +1 for bias
            weights.append(np.random.uniform(-1, 1, (15, width + 1)))  # Output layer

        self.weights = weights

    def turn(self, mano):
        output = np.append(self._build_input(mano), 1) # Bias
        for i in range(len(self.weights) - 1):
            z = self.weights[i] @ output
            a = np.maximum(0, z) # ReLU
            output = np.append(a, 1) # Bias
        # Output layer transform
        output = self.weights[len(self.weights) - 1] @ output
        output_masked = np.where(self._output_mask(), output, -np.inf)
        return np.argmax(output_masked)