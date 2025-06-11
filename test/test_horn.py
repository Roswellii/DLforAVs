from beamngpy import BeamNGpy
import time

# 启动连接 BeamNG
bng = BeamNGpy('localhost', 25252)
bng.open(launch=False)

scenario = bng.scenario.get_current(connect=True)
vehicle = scenario.get_vehicle('etk_car')
vehicle.connect(bng)

print("🔊 测试喇叭响 0.5 秒")
vehicle.queue_lua_command('input.setValue("horn", 1)\n')
time.sleep(0.5)
vehicle.queue_lua_command('input.setValue("horn", 0)\n')
print("✅ 喇叭测试结束")

bng.close()
