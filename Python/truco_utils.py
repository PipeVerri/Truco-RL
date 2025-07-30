def build_hand_critical_input(mano, hand_state, i, is_mano):
        won = i + 1
        lost = (not i) + 1
        # Ver que mano esta siendo jugada ahora
        if mano == 0:
            return [True, True] # Aun no se hizo nada, puedo perderla o empardarla
        elif mano == 1:
            if hand_state[0] == won:
                return [True, True] # Gane primera, sigo pudiendo hacer lo que quiera
            elif hand_state[0] == lost:
                return [False, False] # Perdí primera, tengo que ganar segunda
            else:
                return [False, True] # Emparde primera, no puedo perder segunda pero puedo volver a empardarla
        else:
            if hand_state[0] == won:
                return [False, True] # La unica forma de llegar a tercera habiendo ganado primera es perdiendo segunda, lo cual solo me deja empardar
            elif hand_state[0] == lost:
                return [False, False] # Si perdi primera y llegue a tercera, solo lo pude haber hecho ganando segunda, y no puedo hacer nada
            else:
                return [False, is_mano] # La unica manera de llegar a tercera habiendo empardado primera es si tambien emparde segunda, lo cual me deja la opcion de empardar SOLO si soy mano

def calculate_falta_envido_points(points):
    return 15 - points if points < 15 else 30 - points