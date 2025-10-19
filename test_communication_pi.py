# Sends held W/A/S/D keys to the Raspberry Pi

import json
import socket
import threading
import time
from pynput import keyboard
from dotenv import load_dotenv
import os

load_dotenv()
PI_IP = os.getenv("PI_IP", "127.0.0.1")  # fallback to localhost if missing
PI_PORT = int(os.getenv("PI_PORT", "50505"))

SEND_HZ = 30
_keys_down = set()
_lock = threading.Lock()

# Allowed keys and a tiny legend for your console
ALLOWED = {"w","a","s","d","r","f","g","h"}
LEGEND = {
    "w":"Torso +", "s":"Torso -",
    "a":"Hips  -", "d":"Hips  +",
    "r":"Neck  +", "f":"Neck  -",
    "g":"Grip  close", "h":"Grip  open"
}

def on_press(key):
    try:
        k = key.char.lower()
        if k in ALLOWED:
            with _lock:
                if k not in _keys_down:
                    print(f"[KEY DOWN] {k.upper():>2}  -> {LEGEND[k]}")
                _keys_down.add(k)
    except AttributeError:
        # ignore non-character keys
        pass

def on_release(key):
    try:
        k = key.char.lower()
        if k in ALLOWED:
            with _lock:
                print(f"[KEY UP]   {k.upper():>2}")
                _keys_down.discard(k)
    except AttributeError:
        pass

def sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    period = 1.0 / SEND_HZ
    print(f"[INFO] Sending to {PI_IP}:{PI_PORT} at {SEND_HZ} Hz...")
    print("[INFO] Controls:", ", ".join(f"{k.upper()}={v}" for k,v in LEGEND.items()))
    while True:
        with _lock:
            payload = {"held": sorted(_keys_down)}
            held_keys = ", ".join(x.upper() for x in payload["held"]) if payload["held"] else "-"
        print(f"[SENT] held={held_keys}")
        sock.sendto(json.dumps(payload).encode("utf-8"), (PI_IP, PI_PORT))
        time.sleep(period)

if __name__ == "__main__":
    t = threading.Thread(target=sender, daemon=True)
    t.start()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()