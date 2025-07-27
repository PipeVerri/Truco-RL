extends Node2D

var socket := WebSocketPeer.new()  # ← instead of WebSocketClient

func _ready():
	var err = socket.connect_to_url("ws://localhost:8080")
	if err != OK:
		push_error("Can't connect: %s" % err)
		return
	set_process(true)

func _process(delta):
	socket.poll()
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count() > 0:
			var msg = socket.get_packet().get_string_from_utf8()
			print("Received:", msg)
