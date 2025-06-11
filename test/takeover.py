import time
import json
import math
import keyboard  # ⬅️ 新增导入
from beamngpy import BeamNGpy
from beamngpy.sensors import Electrics

# ====================== 参数设置 ===========================
TRAJECTORY_FILE = r'C:\Workspace\beamNG\DL\traj\vehicle_trajectory.json'
VEHICLE_ID = 'etk_car'
LOOKAHEAD_DISTANCE = 5.0
TARGET_SPEED = 15.0
# ===========================================================

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def get_closest_point(current_pos, traj):
    closest = None
    min_dist = float('inf')
    for point in traj:
        pos = point.get("position") or point.get("data", {}).get("position")
        if pos:
            d = distance(current_pos, pos)
            if d < min_dist:
                min_dist = d
                closest = pos
    return closest

def get_next_point(current, traj, offset=5):
    for i in range(len(traj)):
        pos = traj[i].get("position") or traj[i].get("data", {}).get("position")
        if pos == current and i + offset < len(traj):
            return traj[i + offset].get("position") or traj[i + offset].get("data", {}).get("position")
    return current

def compute_lookahead(current_pos, next_pos, dist):
    dx = next_pos[0] - current_pos[0]
    dy = next_pos[1] - current_pos[1]
    total_dist = math.hypot(dx, dy)
    if total_dist == 0:
        return next_pos
    ratio = dist / total_dist
    return [current_pos[0] + dx * ratio, current_pos[1] + dy * ratio]

def compute_steering_angle(current_pos, current_dir, lookahead_pos):
    dx = lookahead_pos[0] - current_pos[0]
    dy = lookahead_pos[1] - current_pos[1]
    target_angle = math.atan2(dy, dx)
    vehicle_yaw = math.atan2(current_dir[1], current_dir[0])
    angle = target_angle - vehicle_yaw
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def main_loop():
    beamng = BeamNGpy('localhost', 25252, home=r'C:\Program Files (x86)\BeamNG.tech.v0.34.2.0')
    bng = beamng.open(launch=False)

    scenario = bng.scenario.get_current(connect=True)
    vehicle = scenario.get_vehicle(VEHICLE_ID)
    if not vehicle:
        print(f"❌ 未找到 ID 为 '{VEHICLE_ID}' 的车辆")
        return

    vehicle.connect(bng)
    vehicle.attach_sensor('electrics', Electrics())
    vehicle.ai.set_mode("manual")


    with open(TRAJECTORY_FILE, 'r') as f:
        trajectory = json.load(f)

    print("🚗 开始自动轨迹跟踪")

    try:
        while True:
            vehicle.sensors.poll()
            pos = vehicle.state["pos"]
            direction = vehicle.state["dir"]
            speed = vehicle.sensors["electrics"]["wheelspeed"]

            current_point = get_closest_point(pos, trajectory)
            next_point = get_next_point(current_point, trajectory, offset=5)
            lookahead = compute_lookahead(pos, next_point, LOOKAHEAD_DISTANCE)
            steering_angle = compute_steering_angle(pos, direction, lookahead)

            steering = max(-1.0, min(1.0, -2 * steering_angle / math.pi))

            speed_error = TARGET_SPEED - speed
            if speed < 0.5 or speed_error > 0:
                throttle = min(0.8, 0.1 * speed_error)
                brake = 0.0
            elif speed_error < 0:
                throttle = max(0.01, 0.1 * speed_error)
                brake = min(0.5, -0.1 * speed_error)
            else:
                throttle = 0.01
                brake = 0.0

            if abs(steering) > 0.5:
                throttle = 0.01
                brake = 0.2

            vehicle.control(steering=steering, throttle=throttle, brake=brake, gear=2)

            print(f"[{time.time():.2f}] pos={pos}, speed={speed:.2f}, steering={steering:.2f}, throttle={throttle:.2f}, brake={brake:.2f}")
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("🛑 跟踪中断")
        bng.close()

if __name__ == '__main__':
    # ✅ 屏蔽方向键输入
    for key in ['up', 'down', 'left', 'right']:
        keyboard.block_key(key)

    try:
        main_loop()
    finally:
        for key in ['up', 'down', 'left', 'right']:
            keyboard.unblock_key(key)
