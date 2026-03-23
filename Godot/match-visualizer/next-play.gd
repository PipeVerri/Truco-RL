extends Button

var socket := WebSocketPeer.new()

func _ready():
	var err = socket.connect_to_url("ws://localhost:8080")
	if err != OK:
		push_error("Can't connect: %s" % err)
		return

	set_process(true)
	connect("pressed", Callable(self, "_on_press"))

func _process(delta):
	socket.poll()
	
	while socket.get_available_packet_count() > 0:
		var packet = socket.get_packet().get_string_from_utf8()
		_process_response(packet)

func _process_response(res):
	var parsed = JSON.parse_string(res)
	if parsed["status"] == "done":
		self.text = "Done"
		set_active_agent(2)
		var points_labels = [get_parent().get_node("mano_puntos"), get_parent().get_node("pie_puntos")]
		points_labels[0].clear()
		points_labels[1].clear()
		points_labels[0].append_text(str(int(parsed["agent1_points"])))
		points_labels[1].append_text(str(int(parsed["agent2_points"])))
		return
	
	# Ahora modificar la escena en base a lo pasado
	set_active_agent(parsed["agent_index"])
	set_current_play(parsed["agent_index"], parsed["action_chosen"])
	set_global_params(parsed["mano"], parsed["global_state"]["truco_state"], parsed["global_state"]["envido_state"], parsed["global_state"]["envido_points"], parsed["global_state"]["previous_envido_points"])
	set_mano_status(parsed["global_state"]["hand_state"])
	# Modificar la escena de los agentes
	set_agent_params(int(0), parsed["mano_state"])
	set_agent_params(int(1), parsed["pie_state"])

func set_mano_status(hand_status):
	var hand_status_rects = [get_parent().get_node("mano1_status"), get_parent().get_node("mano2_status"), get_parent().get_node("mano3_status")]
	
	for i in range(3):
		var color
		if int(hand_status[i]) == 0:
			color = Color(0, 0, 0, 0)
		elif int(hand_status[i]) == 1:
			color = Color(0, 1, 0, 1)
		elif int(hand_status[i]) == 2:
			color = Color(1, 0, 0, 1)
		else:
			color = Color(1, 1, 0, 1)
		
		hand_status_rects[i].color = color

func set_agent_params(index, agent):
	# Setear los puntos
	var points_labels = [get_parent().get_node("mano_puntos"), get_parent().get_node("pie_puntos")]
	points_labels[index].clear()
	points_labels[index].append_text(str(int(agent["points"])))
	# Setear las tarjetas(que tengo)
	var my_cards = [
		[get_node("/root/Node/Viewer/mano_1"), get_node("/root/Node/Viewer/mano_2"), get_node("/root/Node/Viewer/mano_3")],
		[get_node("/root/Node/Viewer/pie_1"), get_node("/root/Node/Viewer/pie_2"), get_node("/root/Node/Viewer/pie_3")]
	]
	my_cards[index][0].texture = load("res://imagenes/cartas/" + str(int(agent["cards"][0]["id"])) + ".png")
	my_cards[index][1].texture = load("res://imagenes/cartas/" + str(int(agent["cards"][1]["id"])) + ".png")
	my_cards[index][2].texture = load("res://imagenes/cartas/" + str(int(agent["cards"][2]["id"])) + ".png")
	# Setear las tarjetas(que jugue)
	var played_cards = [
		[get_node("/root/Node/Viewer/mano_jugada_1"), get_node("/root/Node/Viewer/mano_jugada_2"), get_node("/root/Node/Viewer/mano_jugada_3")],
		[get_node("/root/Node/Viewer/pie_jugada_1"), get_node("/root/Node/Viewer/pie_jugada_2"), get_node("/root/Node/Viewer/pie_jugada_3")]
	]
	played_cards[index][0].texture = load("res://imagenes/cartas/" + str(int(agent["played_cards"][0]["id"])) + ".png")
	played_cards[index][1].texture = load("res://imagenes/cartas/" + str(int(agent["played_cards"][1]["id"])) + ".png")
	played_cards[index][2].texture = load("res://imagenes/cartas/" + str(int(agent["played_cards"][2]["id"])) + ".png")

func set_global_params(mano, truco_state, envido_state, envido_points, previous_envido_points):
	const truco_states = ["Sin truco", "Truco", "Retruco", "Vale 4"]
	const envido_states = ["Sin envido", "Envido", "Envido(2)", "Real envido", "Falta envido"]
	var to_modify = get_parent().get_node("global_params") 
	to_modify.clear()
	to_modify.append_text("Mano: " + str(int(mano)) + "\n")
	to_modify.append_text("Estado truco: " + truco_states[truco_state] + "\n")
	to_modify.append_text("Estado envido: " + envido_states[envido_state] + "\n")
	to_modify.append_text("Si se gana: " + str(int(envido_points)) + " | Si se pierde: " + str(int(previous_envido_points)))

func set_current_play(agent_id, action):
	const actions = ["Jugar primera carta", "Jugar segunda carta", "Jugar tercera carta", "Cantar truco", "Cantar retruco", "Cantar vale 4", "Cantar envido", "Cantar doble envido", "Cantar real envido", "Cantar falta envido", "Acepto(truco)", "Rechazo(truco)", "Acepto(envido)", "Rechazo(envido)", "Me voy al mazo"]
	
	var to_modify
	if agent_id == 0:
		to_modify = get_parent().get_node("mano_play")
	else:
		to_modify = get_parent().get_node("pie_play")
	
	to_modify.clear()
	to_modify.append_text(actions[action])

func set_active_agent(agent_id):
	var mano_activado = get_node("/root/Node/Viewer/mano_activado")
	var pie_activado = get_node("/root/Node/Viewer/pie_activado")
	if agent_id == 0:
		mano_activado.visible = true
		pie_activado.visible = false
	elif agent_id == 1:
		mano_activado.visible = false
		pie_activado.visible = true
	else: # Para mostrar el done
		mano_activado.visible = false
		pie_activado.visible = false

func _on_press():
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		socket.send_text("Next")
	else:
		print("Socket is not open!")
