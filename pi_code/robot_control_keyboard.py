# server_pi_controls_neutral.py
# Raspberry Pi: UDP-controlled servo movement with original neutral pose.

from robot_hat import Servo
import socket, json, time

# === Servo setup ===
grip  = Servo("P11")
neck  = Servo("P10")
torso = Servo("P9")
hips  = Servo("P8")

# --- Original neutral pose ---
NEUTRAL = {
    "grip":  0,    # open
    "neck": -90,
    "torso": -90,
    "hips":  0,
}

# Move to neutral on startup
for name, angle in NEUTRAL.items():
    {"grip": grip, "neck": neck, "torso": torso, "hips": hips}[name].angle(angle)
    time.sleep(0.5)
print("[Pi] Arm in ready (neutral) position.")

# === UDP setup ===
UDP_IP, UDP_PORT = "0.0.0.0", 50505
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)
print(f"[Pi] Listening for commands on {UDP_PORT} ...")

# === Motion parameters ===
angle_grip  = float(NEUTRAL["grip"])
angle_neck  = float(NEUTRAL["neck"])
angle_torso = float(NEUTRAL["torso"])
angle_hips  = float(NEUTRAL["hips"])

CLAMP_MIN, CLAMP_MAX = -90.0, 90.0
STEP_ROT  = 2.0   # for torso/neck/hips
STEP_GRIP = 3.0   # for grip

def clamp(x): 
    return max(CLAMP_MIN, min(CLAMP_MAX, x))

held = set()
last_rx = 0.0
tick_hz = 60.0
period = 1.0 / tick_hz
pkt_count = 0

while True:
    # --- drain up to N packets quickly, keep freshest 'held' ---
    drained = 0
    while drained < 20:
        try:
            data, addr = sock.recvfrom(1024)
        except BlockingIOError:
            break
        pkt_count += 1
        drained += 1
        last_rx = time.time()
        try:
            msg = json.loads(data.decode("utf-8"))
            held = set(msg.get("held", []))
        except Exception as e:
            print(f"[Pi] JSON error: {e}")

    # --- apply movement if we heard from the client recently ---
    if (time.time() - last_rx) < 0.5:
        prev_torso, prev_neck, prev_hips, prev_grip = angle_torso, angle_neck, angle_hips, angle_grip

        # W/S -> Torso
        if "w" in held:
            angle_torso = clamp(angle_torso + STEP_ROT)
        if "s" in held:
            angle_torso = clamp(angle_torso - STEP_ROT)

        # A/D -> Hips
        if "a" in held:
            angle_hips = clamp(angle_hips - STEP_ROT)
        if "d" in held:
            angle_hips = clamp(angle_hips + STEP_ROT)

        # R/F -> Neck
        if "r" in held:
            angle_neck = clamp(angle_neck + STEP_ROT)
        if "f" in held:
            angle_neck = clamp(angle_neck - STEP_ROT)

        # G/H -> Grip  (G = close -> negative, H = open -> positive)
        if "g" in held:
            angle_grip = clamp(angle_grip - STEP_GRIP)
        if "h" in held:
            angle_grip = clamp(angle_grip + STEP_GRIP)

        # Apply only if changed
        if angle_torso != prev_torso:
            torso.angle(int(angle_torso))
        if angle_hips != prev_hips:
            hips.angle(int(angle_hips))
        if angle_neck != prev_neck:
            neck.angle(int(angle_neck))
        if angle_grip != prev_grip:
            grip.angle(int(angle_grip))

        # Optional: lightweight status print
        if int(time.time() * 2) % 2 == 0:
            print(f"[Pi] held={sorted(list(held))} | "
                  f"T={angle_torso:.0f} H={angle_hips:.0f} N={angle_neck:.0f} G={angle_grip:.0f}")

    time.sleep(period)

