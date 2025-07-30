import numpy as np
from truco_utils import *

class GeneticAgent:
    def __init__(self, depth=3, width=128, seed=None):
        # Init weights randomly. 76 inputs, 13 outputs
        if seed is not None:
            np.random.seed(seed)
        weights = [np.random.uniform(-1, 1, (width, 79 + 1))] # +1 for bias
        if depth > 1:
            for _ in range(depth - 1):
                weights.append(np.random.uniform(-1, 1, (width, width + 1))) # +1 for bias

        weights.append(np.random.uniform(-1, 1, (15, width + 1))) # Output layer

        # Param initialization
        self.weights = weights
        self.cards = []
        self.played_cards = []
        self.opponent_played_cards = []
        self.hand_state = [0, 0, 0]
        self.is_mano = False
        self.points = 0
        self.opponent_points = 0
        self.truco_state = 0
        self.can_cantar_truco = True
        self.envido_state = 0
        self.can_cantar_envido = True
        self.envido_points = 0 # envido_state es la posicion en la escalera de cantos, envido_points es la cantidad de puntos que se ponen en juego
        self.envido_acceptance_status = 0 # 0 si no paso nada, 1 si lo gane yo, 2 si lo gano el otro, 3 si lo rechaze, 4 si lo rechazo el otro
        self.opponent_envido_points = 0 # Si acepto los puntos con los que lo hizo
        self.expect_truco_response = False # Si tiene que decir que si, que no o subirle al truco
        self.expect_envido_response = False # Si tiene que decir que si, que no o subirle al envido
        self.id = 0,
        self.reject_envido_points = 0 # Lo que perderia si se rechaza el envido

    def start_round(self, agent_id, selected, is_mano, points, opponent_points):
        self.cards = sorted(selected, key=lambda card: card["power"])
        self.id = agent_id

        start_state = [{"id": -1, "power": 0, "palo": 0, "envido": 0}] * 3
        self.played_cards = start_state
        self.opponent_played_cards = start_state

        self.hand_state = [0, 0, 0]
        self.is_mano = is_mano
        self.points = points
        self.opponent_points = opponent_points
        self.truco_state = 0
        self.can_cantar_truco = True
        self.envido_state = 0
        self.can_cantar_envido = True
        self.envido_acceptance_status = 0
        self.opponent_envido_points = 0
        self.expect_truco_response = False
        self.expect_envido_response = False
        self.reject_envido_points = 0

    def turn(self, mano):
        output = np.append(self._build_input(mano), 1) # Bias
        for i in range(len(self.weights) - 1):
            z = self.weights[i] @ output
            a = np.maximum(0, z) # ReLU
            output = np.append(a, 1) # Bias
        # Output layer transform
        output = self.weights[len(self.weights) - 1] @ output
        output_masked = output * self._output_mask()
        return np.argmax(output_masked)

    def _output_mask(self):
        expecting = self.expect_envido_response or self.expect_truco_response
        return np.array([
            # Que cartas puedo jugar
            self.cards[0]["id"] != -1 and not expecting,
            self.cards[1]["id"] != -1 and not expecting,
            self.cards[2]["id"] != -1 and not expecting,
            # Que cantos del truco puedo hacer
            self.truco_state == 0 and self.can_cantar_truco and not self.expect_envido_response,
            self.truco_state == 1 and self.can_cantar_truco and not self.expect_envido_response,
            self.truco_state == 2 and self.can_cantar_truco and not self.expect_envido_response,
            # Que cantos del envido puedo hacer
            self.envido_state == 0 and self.can_cantar_envido,
            self.envido_state == 1 and self.can_cantar_envido, # Solo doble envido si se canto el envido justo antes
            self.envido_state <= 2 and self.can_cantar_envido,
            self.envido_state <= 3 and self.can_cantar_envido,
            # Si se acepta o rechaza el truco, el envido toma prioridad
            self.expect_truco_response and not self.expect_envido_response,
            self.expect_truco_response and not self.expect_envido_response,
            # Si se acepta o rechaza el envido
            self.expect_envido_response,
            self.expect_envido_response,
            # Solo me puedo ir al mazo si no están esperando respuesta, asi no se me complica
            not expecting
        ])

    # TODO: fix
    def _predict_best_play(self):
        input_layer = self._build_input()
        output = np.append(input_layer, 1) # Bias
        for i in range(len(self.weights)):
            output = np.append(self.weights[i] @ output, 1) # Bias

        # Ahora pasarlo por la mascara y retornar la mejor jugada
        masked = np.where(self._output_mask(), output, -np.inf)
        return np.argmax(masked)

    def _build_input(self, mano):
        # Construir el input para alimentarselo al MLP
        return np.concatenate([
            self._build_cards_input(),
            self._build_hand_state_input(),
            self._build_hand_critical_input(mano),
            [self.calculate_envido()],
            self._falta_envido_possible_points(),
            self._points_insights(),
            self._truco_possibilities(),
            self._envido_possibilities(),
            self._cantos_status(),
            self._envido_acceptance_vector(),
            [self.opponent_points],
            [mano]
        ])

    def _envido_acceptance_vector(self):
        to_return = [0, 0, 0, 0]
        if self.envido_acceptance_status > 0:
            to_return[self.envido_acceptance_status - 1] = 1

        return to_return

    def _cantos_status(self):
        return [
            self.truco_state + 1, # Cuantos puntos se ganarian en esta ronda con el truco
            self.envido_points
        ]

    def _envido_possibilities(self):
        to_return = [0, 0, 0, 0]
        if self.can_cantar_envido:
            for i in range(self.envido_state, 4):
                to_return[i] = 1

        return to_return

    def _truco_possibilities(self):
        to_return = [0, 0, 0]
        if self.can_cantar_truco:
            to_return[self.truco_state]  = 1

        return to_return

    def _points_insights(self):
        return [
            30 - self.points, # Cuanto me falta para ganar
            30 - self.opponent_points, # Cuanto le falta al otro para ganar
            self.points - self.opponent_points # Cuanto me esta sacando
        ]

    def _falta_envido_possible_points(self):
        return [
            calculate_falta_envido_points(self.points) if self.envido_state == 4 else 0,
            calculate_falta_envido_points(self.opponent_points) if self.envido_state == 4 else 0
        ]

    def calculate_envido(self):
        c = self.cards
        # Empezar viendo el mejor puntaje posible combinando la primera carta con la segunda o la tercera
        best_envido = max(c[0]["envido"], c[1]["envido"], c[2]["envido"]) # La mejor entre las 3 solas
        if c[0]["palo"] == c[1]["palo"]:
            best_envido = max(best_envido, 20 + c[0]["envido"] + c[1]["envido"]) # Primera y segunda cartas juntas
        if c[0]["palo"] == c[2]["palo"]:
            best_envido = max(best_envido, 20 + c[0]["envido"] + c[2]["envido"]) # Primera y tercera cartas juntas
        if c[1]["palo"] == c[2]["palo"]:
            best_envido = max(best_envido, 20 + c[1]["envido"] + c[2]["envido"]) # Segunda y tercera cartas juntas
        return best_envido

    def _build_hand_critical_input(self, mano):
        my_state = build_hand_critical_input(mano, self.hand_state, self.id, self.is_mano)
        opp_state = build_hand_critical_input(mano, self.hand_state, not self.id, not self.is_mano)
        return my_state + opp_state

    def _build_hand_state_input(self):
        to_return = []
        for i in range(3):
            hand_state = [0, 0, 0] # One hot vector para ganada, perdida o empardada, (o todo 0 si no fue jugada aun)
            if self.hand_state[i] == 2: # Emapte
                hand_state[2] = 1
            elif self.hand_state[i] == self.id + 1: # Gane
                hand_state[0] = 1
            else: # Perdi
                hand_state[1] = 1
            to_return += hand_state
        return to_return

    def _build_cards_input(self):
        to_return = []
        for to_fetch_from in [self.cards, self.played_cards, self.opponent_played_cards]:
            for i in range(3):
                to_return.append(to_fetch_from[i]["power"])
                to_return += self._palo_one_hot(to_fetch_from[i])
        return to_return

    def _palo_one_hot(self, card):
        one_hot = [0, 0, 0, 0]
        if card["id"] != -1:
            one_hot[card["palo"]] = 1
        return one_hot