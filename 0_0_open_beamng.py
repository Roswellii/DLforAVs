from beamngpy import BeamNGpy

# 启动 BeamNG.tech 并加载 Italy 地图
beamng = BeamNGpy('localhost', 25252, home=r'C:\Program Files (x86)\BeamNG.tech.v0.34.2.0')
bng = beamng.open(launch=True)  # 启动 BeamNG 实例（会加载默认地图）

print("BeamNG.tech 已启动，可运行控制脚本连接它。不要关闭此窗口。")

# 保持运行，直到手动停止（或通过 Ctrl+C）
try:
    while True:
        pass
except KeyboardInterrupt:
    print("用户终止 BeamNG 实例，关闭连接。")
    bng.close()
