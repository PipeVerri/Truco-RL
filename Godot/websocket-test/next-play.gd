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
	if res == "done":
		self.text = "Done"
		set_active_agent(2)
		return
	
	var parsed = JSON.parse_string(res)
	# Ahora modificar la escena en base a lo pasado
	set_active_agent(parsed["agent_index"])

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
		mano_activado.visible = true
		pie_activado.visible = true

func _on_press():
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		socket.send_text("Next")
	else:
		print("Socket is not open!")
