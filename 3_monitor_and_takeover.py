import time
import json
import math
import keyboard
from beamngpy import BeamNGpy
from beamngpy.sensors import Electrics

# -------- Configuration --------
TRAJECTORY_FILE = r'C:\Workspace\beamNG\DL\traj\vehicle_trajectory.json'
VEHICLE_ID = 'etk_car'
LOOKAHEAD_DISTANCE = 5.0
TARGET_SPEED = 15.0
BLOCKED_KEYS = ['up', 'down', 'left', 'right']
# -------------------------------

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def is_near_target(curr, tgt, threshold=2.0):
    return distance(curr[:2], tgt[:2]) <= threshold

def get_closest_index(curr, traj):
    min_idx, min_dist = 0, float('inf')
    for i, point in enumerate(traj):
        pos = point.get("position") or point.get("data", {}).get("position")
        d = distance(curr, pos)
        if d < min_dist:
            min_dist, min_idx = d, i
    return min_idx

def compute_lookahead(curr, nxt, dist):
    dx, dy = nxt[0]-curr[0], nxt[1]-curr[1]
    total = math.hypot(dx, dy)
    if total == 0: return nxt
    ratio = dist / total
    return [curr[0]+dx*ratio, curr[1]+dy*ratio]

def compute_steering_angle(curr, dirvec, lookahead):
    dx, dy = lookahead[0]-curr[0], lookahead[1]-curr[1]
    tgt = math.atan2(dy, dx)
    yaw = math.atan2(dirvec[1], dirvec[0])
    ang = tgt - yaw
    while ang > math.pi: ang -= 2*math.pi
    while ang < -math.pi: ang += 2*math.pi
    return ang

def main_loop():
    beamng = BeamNGpy('localhost', 25252,
                      home=r'C:\Program Files (x86)\BeamNG.tech.v0.34.2.0')
    bng = beamng.open(launch=False)
    scenario = bng.scenario.get_current(connect=True)
    vehicle = scenario.get_vehicle(VEHICLE_ID)
    if not vehicle:
        print(f"❌ Vehicle '{VEHICLE_ID}' not found in current scenario.")
        return

    vehicle.connect(bng)
    vehicle.attach_sensor('electrics', Electrics())
    vehicle.ai.set_mode("manual")

    traj = json.load(open(TRAJECTORY_FILE, 'r'))
    N = len(traj)
    if N < 15:
        print("⚠️ Not enough trajectory points. Control aborted.")
        return

    start_pt = traj[0].get("position") or traj[0]["data"]["position"]
    end_pt = traj[-1].get("position") or traj[-1]["data"]["position"]

    started = ended = False

    print("⏳ Waiting to reach the starting area...")

    try:
        while True:
            vehicle.sensors.poll()
            pos = vehicle.state["pos"]
            dirvec = vehicle.state["dir"]
            speed = vehicle.sensors["electrics"]["wheelspeed"]

            if not started and is_near_target(pos, start_pt):
                print("🚗 Auto-control engaged. Please keep your hands off the wheel.")
                for k in BLOCKED_KEYS: keyboard.block_key(k)
                started = True

            if started and not ended and is_near_target(pos, end_pt):
                print("🛑 Auto-control ending. Prepare to take over manual control.")
                for k in BLOCKED_KEYS: keyboard.unblock_key(k)
                vehicle.set_lights(left_signal=False, right_signal=False)
                ended = True

            if started and not ended:
                idx = get_closest_index(pos, traj)

                if idx < 50:
                    vehicle.set_lights(left_signal=True, right_signal=False)
                    print("📢 Approaching start of autonomous driving. Do not steer.")

                elif idx >= N - 150:
                    vehicle.set_lights(left_signal=False, right_signal=True)
                    print("📢 Approaching end of autonomous driving. Be ready to steer.")

                else:
                    vehicle.set_lights(left_signal=False, right_signal=False)
                    print("✅ Autonomous driving active. Monitoring surroundings...")

                curr = traj[idx].get("position") or traj[idx]["data"]["position"]
                nxt = traj[min(idx+5, N-1)].get("position") or traj[min(idx+5, N-1)]["data"]["position"]
                lookahead = compute_lookahead(pos, nxt, LOOKAHEAD_DISTANCE)
                angle = compute_steering_angle(pos, dirvec, lookahead)
                steer = max(-1.0, min(1.0, -2 * angle / math.pi))

                err = TARGET_SPEED - speed
                if speed < 0.5 or err > 0:
                    throttle = min(0.8, 0.1 * err); brake = 0.0
                else:
                    throttle = max(0.01, 0.1 * err); brake = min(0.5, -0.1 * err)
                if abs(steer) > 0.5:
                    throttle = 0.01; brake = 0.2

                vehicle.control(steering=steer, throttle=throttle, brake=brake, gear=2)

            else:
                if not started:
                    print(f"[{time.time():.2f}] 🚫 Waiting to engage... Distance to start: {distance(pos, start_pt):.2f} m")
                else:
                    print(f"[{time.time():.2f}] ✅ Control finished. Final idx={idx}")

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("🛑 Manual interrupt detected. Shutting down.")
    finally:
        for k in BLOCKED_KEYS: keyboard.unblock_key(k)
        vehicle.set_lights(left_signal=False, right_signal=False)
        bng.close()
        print("✅ Cleanup complete. Manual control restored.")

if __name__ == '__main__':
    main_loop()
