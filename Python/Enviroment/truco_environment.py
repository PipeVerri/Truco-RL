from Utils.truco_utils import *
from Agent.genetic_agent import GeneticAgent
from collections import deque
import copy
import json

CARDS = np.array([
    {"id": 0, "power": 14, "palo": 0, "envido": 1},  # 1 of espadas (macho)
    {"id": 1, "power": 13, "palo": 1, "envido": 1},  # 1 of bastos (hembra)
    {"id": 2, "power": 12, "palo": 0, "envido": 7},  # 7 of espadas
    {"id": 3, "power": 11, "palo": 2, "envido": 7},  # 7 of oros
    # 3s
    {"id": 4, "power": 10, "palo": 0, "envido": 3},
    {"id": 5, "power": 10, "palo": 1, "envido": 3},
    {"id": 6, "power": 10, "palo": 2, "envido": 3},
    {"id": 7, "power": 10, "palo": 3, "envido": 3},
    # 2s
    {"id": 8, "power": 9, "palo": 0, "envido": 2},
    {"id": 9, "power": 9, "palo": 1, "envido": 2},
    {"id": 10, "power": 9, "palo": 2, "envido": 2},
    {"id": 11, "power": 9, "palo": 3, "envido": 2},
    # 1s (oros, copas)
    {"id": 12, "power": 8, "palo": 2, "envido": 1},
    {"id": 13, "power": 8, "palo": 3, "envido": 1},
    # 12s
    {"id": 14, "power": 7, "palo": 0, "envido": 0},
    {"id": 15, "power": 7, "palo": 1, "envido": 0},
    {"id": 16, "power": 7, "palo": 2, "envido": 0},
    {"id": 17, "power": 7, "palo": 3, "envido": 0},
    # 11s
    {"id": 18, "power": 6, "palo": 0, "envido": 0},
    {"id": 19, "power": 6, "palo": 1, "envido": 0},
    {"id": 20, "power": 6, "palo": 2, "envido": 0},
    {"id": 21, "power": 6, "palo": 3, "envido": 0},
    # 10s
    {"id": 22, "power": 5, "palo": 0, "envido": 0},
    {"id": 23, "power": 5, "palo": 1, "envido": 0},
    {"id": 24, "power": 5, "palo": 2, "envido": 0},
    {"id": 25, "power": 5, "palo": 3, "envido": 0},
    # 7s (weak ones: bastos, copas)
    {"id": 26, "power": 4, "palo": 1, "envido": 7},
    {"id": 27, "power": 4, "palo": 3, "envido": 7},
    # 6s
    {"id": 28, "power": 3, "palo": 0, "envido": 6},
    {"id": 29, "power": 3, "palo": 1, "envido": 6},
    {"id": 30, "power": 3, "palo": 2, "envido": 6},
    {"id": 31, "power": 3, "palo": 3, "envido": 6},
    # 5s
    {"id": 32, "power": 2, "palo": 0, "envido": 5},
    {"id": 33, "power": 2, "palo": 1, "envido": 5},
    {"id": 34, "power": 2, "palo": 2, "envido": 5},
    {"id": 35, "power": 2, "palo": 3, "envido": 5},
    # 4s
    {"id": 36, "power": 1, "palo": 0, "envido": 4},
    {"id": 37, "power": 1, "palo": 1, "envido": 4},
    {"id": 38, "power": 1, "palo": 2, "envido": 4},
    {"id": 39, "power": 1, "palo": 3, "envido": 4},
])

ENVIDO_STATE_POINTS = [
    2, # Envido
    2, # Doble envido
    3, # Real envido
]

class TrucoEnvironment:
    def game(self, agent1, agent2, seed=None):
        agents = [
            {"agent": agent1, "points": 0},
            {"agent": agent2, "points": 0}
        ]
        mano_index = 0
        while agents[0]["points"] < 30 and agents[1]["points"] < 30:
            mano_points, pie_points = self.match(agents[mano_index]["agent"], agents[not mano_index]["agent"], agents[mano_index]["points"], agents[not mano_index]["points"], seed=seed)
            agents[mano_index]["points"] = mano_points
            agents[not mano_index]["points"] = pie_points
            mano_index = not mano_index
        return min(30, agents[0]["points"]), min(30, agents[1]["points"])

    def match(self, agent1, agent2, agent1_points, agent2_points, debug=False, seed=None):
        # Inicializar
        # Parametros agente
        if seed is not None:
            np.random.seed(seed)
        selected = np.random.choice(CARDS, 6, replace=False)
        cards_agent1 = copy.deepcopy(selected[:3])
        cards_agent2 = copy.deepcopy(selected[3:])
        # Inicializar los agentes en si
        agent1.start_round(0, cards_agent1, True, agent1_points, agent2_points)
        agent2.start_round(1, cards_agent2, False, agent2_points, agent1_points)
        agents = [agent1, agent2] # 2 templates para cada agente
        # Parametros globales
        hand_state = [0, 0, 0]
        truco_state = 0 # 0 para nada, 1 para el truco, ...
        actions_queue = deque() # Todas las cosas a procesar
        envido_state = 0 # 1 para envido, 2 para doble envido...
        envido_points = 0 # La suma de los envido_states cantados
        previous_envido_points = 0 # Los puntos que se perderian si rechazara el nuevo envido
        falta_envido = False # Que se haga el handling del falta envido al definir si se quiere o no
        mano = 0 # El index de la mano
        on_truco_chain = False
        on_envido_chain = False

        def process_action(i, action):
            nonlocal hand_state, truco_state, actions_queue, envido_state, envido_points, previous_envido_points, falta_envido, mano, on_envido_chain, on_truco_chain

            if action < 3: # Tira alguna de las primeras 3 cartas
                card = agents[i].cards[action]
                assert card["id"] != -1 and not agents[i].expect_envido_response and not agents[i].expect_truco_response
                agents[i].played_cards[mano] = card.copy()
                opponent_card = agents[not i].played_cards[mano]

                if opponent_card["id"] != -1: # Si el otro ya jugo, actualizar el hand_state y fijarme si se definio la partida
                    if card["power"] > opponent_card["power"]:
                        mano_result = i + 1
                    elif card["power"] < opponent_card["power"]:
                        mano_result = (not i) + 1
                    else:
                        mano_result = 3

                    # Actualizar hand_state
                    hand_state[mano] = mano_result

                    # Fijarme si se definio la partida
                    win = mano_result == i + 1
                    loose = mano_result == (not i) + 1
                    tie = mano_result == 3
                    my_critical_hand_state = build_hand_critical_input(mano, hand_state, i, agents[i].is_mano)
                    if (not my_critical_hand_state[0] and loose) or (not my_critical_hand_state[1] and tie):
                        # Sumarle al oponente el truco + 1(por ganar)
                        agents[not i].points += truco_state + 1
                        return False
                    # Fijarme si la partida la gane
                    opp_critical_hand_state = build_hand_critical_input(mano, hand_state, not i, agents[not i].is_mano)
                    if (not opp_critical_hand_state[0] and win) or (not opp_critical_hand_state[1] and tie):
                        agents[i].points += truco_state + 1
                        return False

                    # Agregar el que siguiente juege al dq
                    if win:
                        actions_queue.append(i)
                    elif loose:
                        actions_queue.append(not i)
                    else:
                        if agents[i].is_mano:
                            actions_queue.append(i)
                        else:
                            actions_queue.append(not i)

                    # Si la mano jugada fue primera, entonces ahora ninguno puede cantar envido
                    if mano == 0:
                        agents[0].can_cantar_envido = False
                        agents[1].can_cantar_envido = False

                    mano += 1 # Irme a la mano siguiente
                else:
                    actions_queue.appendleft(not i)  # Ahora le toca al otro jugar. Esto solo lo hago en el caso donde no se "definio" la mano porque cuando se define depende de quien gano el primero que juega

                agents[i].cards[action]["id"] = -1 # Anular la carta para que no pueda ser jugada
            elif action < 6: # Canto alguno de los trucos
                # Asegurarse que no se haya mandado ninguna
                desired_truco_state = action - 3 + 1
                assert agents[i].can_cantar_truco and desired_truco_state == truco_state + 1 and not agents[i].expect_envido_response # Fijarme que lo tenga y que ese cantando algo correcto

                # Modificar quien tiene el canto
                truco_state += 1
                agents[i].can_cantar_truco = False
                agents[i].expect_truco_response = False # Ya no se espera su respuesta si estaba en la cadena
                agents[not i].can_cantar_truco = True
                agents[not i].expect_truco_response = True

                # Agregarlos al queue
                if not on_truco_chain:
                    actions_queue.appendleft(i)
                actions_queue.appendleft(not i)

                on_truco_chain = True
            elif action < 10: # Canto alguno de los envidos
                # Asegurarse de que pueda cantar ese envido
                desired_envido_state = action - 6 + 1
                assert envido_state < desired_envido_state and agents[i].can_cantar_envido

                if envido_points == 0:
                    previous_envido_points = 1 # Si se rechaza el primer envido, es solo 1 punto
                else:
                    previous_envido_points = envido_points

                # Actualizar las variables globales
                envido_state = desired_envido_state
                if action != 9:
                    envido_points += ENVIDO_STATE_POINTS[desired_envido_state - 1]
                else: # Falta envido
                    falta_envido = True

                # Actualizar los agentes
                agents[i].can_cantar_envido = False
                agents[i].expect_envido_response = False
                agents[not i].can_cantar_envido = True
                agents[not i].expect_envido_response = True

                # Agregarlos al queue
                if agents[i].expect_truco_response:
                    agents[i].expect_truco_response = False
                    truco_state = 0 # Se anula la cadena de truco que habia
                    on_truco_chain = False
                    actions_queue.appendleft(not i)
                else:
                    if not on_envido_chain:
                        actions_queue.appendleft(i)
                    actions_queue.appendleft(not i)

                on_envido_chain = True
            elif action == 10: # Acepto el truco
                assert agents[i].expect_truco_response
                # Actualizar los parametros de los agentes, los globales ya fueron actualizados al hacer el canto
                agents[i].can_cantar_truco = True # Ahora yo tengo el truco
                agents[i].expect_truco_response = False # Ya no espero una respuesta
                agents[i].can_cantar_envido = False
                agents[not i].can_cantar_truco = False
                agents[not i].can_cantar_envido = False
                # No hace falta agregarlos al queue, el queue sigue el orden que tenia antes
                on_truco_chain = False
            elif action == 11: # Rechazo el truco
                assert agents[i].expect_truco_response
                # Perdi la ronda, sumarle los puntos del truco
                agents[i].expect_truco_response = False
                agents[not i].points += truco_state + 1
                on_truco_chain = False
                return False
            elif action == 12: # Acepto el envido
                my_points = agents[i].calculate_envido()
                opp_points = agents[not i].calculate_envido()
                if my_points > opp_points:
                    winner = i
                elif my_points < opp_points:
                    winner = not i
                else:
                    winner = i if agents[i].is_mano else (not i)

                if falta_envido:
                    agents[winner].points += calculate_falta_envido_points(agents[not winner].points)
                else:
                    agents[winner].points += envido_points # Al falta envido no se le suman los puntos de la cadena anterior

                # Informale a los agentes sobre los puntos del enemigo
                agents[i].opponent_envido_points = opp_points
                agents[not i].opponent_envido_points = my_points
                # Y sobre como les salio el envido
                agents[winner].envido_acceptance_status = 1
                agents[not winner].envido_acceptance_status = 2

                agents[i].expect_envido_response = False

                # No hace falta agregarlos al queue otra vez, sigue el protocolo normal de la partida
                on_envido_chain = False
            elif action == 13: # Rechazo el envido
                assert agents[i].expect_envido_response
                agents[i].can_cantar_envido = False
                agents[i].expect_envido_response = False
                agents[not i].points += previous_envido_points
                on_envido_chain = False
            elif action == 14: # Se fue al mazo
                assert (not agents[i].expect_envido_response) and (not agents[i].expect_truco_response)
                agents[not i].points += truco_state + 1
                return False

            if agents[i].points >= 30 or agents[not i].points >= 30: # Termino la partida
                agents[not i].points += 1
                return False

            # Actualizar los parametros globales
            for j in range(2):
                agents[j].hand_state = hand_state
                agents[j].opponent_points = agents[not i].points
                agents[j].truco_state = truco_state
                agents[j].envido_state = envido_state
                agents[j].envido_points = envido_points
                agents[j].reject_envido_points = previous_envido_points

            return True

        # Agregar el mano al actions queue y repetir hasta que la funcion retorne False, indicando que el match termino
        actions_queue.append(0) # Empieza jugando el mano
        debug_output = []
        while True:
            assert len(actions_queue) > 0 # Si se quedo sin jugadas y la partida no se definio, algo anda mal
            agent = actions_queue.popleft()
            action = agents[agent].turn(mano)

            if debug:
                mano_state = copy.deepcopy(agents[0].__dict__)
                pie_state = copy.deepcopy(agents[1].__dict__)
                del mano_state["weights"]
                del pie_state["weights"]

                debug_output.append({
                    "agent_index": int(agent),
                    "action_chosen": action,
                    "mano": mano,
                    "global_state": {
                        "hand_state": hand_state.copy(),
                        "truco_state": truco_state,
                        "envido_state": envido_state,
                        "envido_points": envido_points,
                        "previous_envido_points": previous_envido_points,
                        "falta_envido": falta_envido,
                    },
                    "mano_state": mano_state,
                    "pie_state": pie_state
                })

            keep_playing = process_action(agent, action)
            if not keep_playing:
                break

        if debug:
            return debug_output, agents[0].points, agents[1].points
        else:
            return agents[0].points, agents[1].points

if __name__ == "__main__":
    def seed_match_tester(s):
        test_agent_1 = GeneticAgent(seed=s)
        test_agent_2 = GeneticAgent(seed=s)
        MatchEnvironment = TrucoEnvironment()
        sample_debug, agent1_points, agent2_points = MatchEnvironment.match(test_agent_1, test_agent_2, 0, 0, debug=True, seed=s) # TODO, poner en true
        print(f"Puntos: {agent1_points}, {agent2_points} | {s}")
        #print(sample_debug)
        with open("../debug.json", "w", encoding="utf-8") as f:
            json.dump({"agent1_points": agent1_points, "agent2_points": agent2_points, "debug": sample_debug}, f, cls=NumpyEncoder, ensure_ascii=False)

    def seed_game_tester(s=None):
        test_agent_1 = GeneticAgent(seed=s)
        test_agent_2 = GeneticAgent(seed=s)
        MatchEnvironment = TrucoEnvironment()
        agent1_points, agent2_points = MatchEnvironment.game(test_agent_1, test_agent_2)
        assert agent1_points <= 30 and agent2_points <= 30

    seed_game_tester(0)