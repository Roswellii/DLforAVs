import time
import json
from beamngpy import BeamNGpy, Vehicle
from beamngpy.sensors import Electrics

# 输出轨迹 JSON 文件
output_file = "traj/vehicle_trajectory.json"

def main():
    bng = BeamNGpy('localhost', 25252)
    bng.open(launch=False)

    # 从当前场景中获取所有车辆
    scenario = bng.scenario.get_current(connect=True)
    vehicle= scenario.get_vehicle('etk_car')

    if not vehicle:
        print("❌ 未找到任何车辆，请先加载含有该车辆的场景")
        return

    # 连接你指定的车辆（假设 Vehicle ID 匹配 'etk_car'）
    vehicle.connect(bng)

    # 确保 attach 了 электrics 传感器
    try:
        vehicle.attach_sensor('electrics', Electrics())
    except Exception:
        pass  # 已 attach 忽略错误

    print("✅ 已连接车辆，开始实时记录位姿和速度...")

    trajectory = []
    try:
        while True:
            vehicle.sensors.poll()
            ts = time.time()
            pos = vehicle.state['pos']
            dir_vec = vehicle.state['dir']
            speed = vehicle.sensors['electrics']['wheelspeed']

            data = {
                "timestamp": ts,
                "position": pos,
                "direction": dir_vec,
                "speed": speed
            }
            trajectory.append(data)
            print(f"[{ts:.2f}] pos={pos}, dir={dir_vec}, speed={speed:.2f} m/s")

            with open(output_file, "w") as f:
                json.dump(trajectory, f, indent=2)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"🛑 停止记录，轨迹已保存至：{output_file}")
        bng.close()

if __name__ == "__main__":
    main()
