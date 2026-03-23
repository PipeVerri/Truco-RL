import asyncio
import websockets
import json

# Carga tu lista de diccionarios UNA VEZ a nivel de módulo
with open("../best_agents.json", "r") as f:
    data = json.load(f)

async def handler(ws):
    print("Cliente conectado")
    idx = 0
    try:
        async for message in ws:
            print(f"Mensaje recibido: {message}")

            # Si aún quedan elementos en data, los enviamos en orden
            if idx < len(data["debug"]):
                data["debug"][idx]["status"] = "continue"
                payload = json.dumps(data["debug"][idx])
                await ws.send(payload)
                print(f"Enviado data[{idx}]")
                idx += 1
            else:
                # Opcional: si ya no hay más, puedes repetir el último, cerrar, o enviar aviso
                await ws.send(json.dumps({"status": "done", "agent1_points": data["agent1_points"], "agent2_points": data["agent2_points"]}))
                print("No quedan más elementos en data")
    except websockets.ConnectionClosed:
        pass
    finally:
        print("Cliente desconectado")

async def main():
    server = await websockets.serve(handler, "localhost", 8080)
    print("Servidor escuchando en ws://localhost:8080/")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())