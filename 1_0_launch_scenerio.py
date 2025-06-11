from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Electrics
import time

# 初始位置与朝向
spawn_pos = (-298.436, 56.521, 111.962)
spawn_rot = (0.0010, 0.1242, 0.9884, -0.0872)

def main():
    set_up_simple_logging()

    # 连接已启动的 BeamNG
    bng = BeamNGpy('localhost', 25252, home=r'C:\Program Files (x86)\BeamNG.tech.v0.34.2.0')
    bng.open(launch=False)

    # 创建场景与车辆
    scenario = Scenario('west_coast_usa', 'relative_camera_view')
    vehicle = Vehicle('etk_car', model='etk800', licence='ZJU')
    vehicle.sensors.attach('electrics', Electrics())


    scenario.add_vehicle(vehicle, pos=spawn_pos, rot_quat=spawn_rot)
    scenario.make(bng)
    bng.scenario.load(scenario)
    bng.scenario.start()

    # 建立连接
    vehicle.connect(bng)


    print("🚗 正在实时输出车辆位姿数据...")

    try:
        while True:
            vehicle.sensors.poll()
            state = vehicle.state

            pos = state['pos']

            dir_vec = state['dir']
            speed = vehicle.sensors['electrics']['wheelspeed']

            print(f"[{time.time():.2f}]")
            print(f"  📍 Position   : x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")
            print(f"  🔄 Direction : dx={dir_vec[0]:.3f}, dy={dir_vec[1]:.3f}, dz={dir_vec[2]:.3f}")

            print(f"  🚀 Speed     : {speed:.2f} m/s")
            print("-" * 50)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("🔚 中断程序，正在关闭连接...")
    finally:
        bng.close()

if __name__ == '__main__':
    main()
