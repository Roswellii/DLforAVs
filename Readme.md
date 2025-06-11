Here is the English version of the `README.md` for your BeamNG vehicle control and monitoring project:

---

# BeamNG Autonomous Vehicle Control and Monitoring System

This project is built on [BeamNG.tech](https://beamng.tech/) and the [beamngpy](https://github.com/BeamNG/BeamNGpy) Python API. It provides a complete pipeline from launching the simulator and loading a scenario, to collecting trajectory data and controlling a vehicle to follow that trajectory with monitoring and takeover capabilities.

## 📁 Project Structure

```
.
├── 0_0_open_beamng.py         # Launch BeamNG instance (Italy map)
├── 1_0_launch_scenerio.py     # Load scenario and vehicle, stream vehicle state
├── 1_1_collect_traj_live.py   # Live trajectory recording to JSON
├── 3_monitor_and_takeover.py  # Autonomous control and manual takeover
└── traj/
    └── vehicle_trajectory.json  # Auto-generated trajectory file
```

## 🚗 Features

### 1. Launch BeamNG Instance

```bash
python 0_0_open_beamng.py
```

* Starts the BeamNG.tech instance.
* Keeps running and waits for other control scripts to connect.

---

### 2. Load Scenario and Stream Vehicle Pose

```bash
python 1_0_launch_scenerio.py
```

* Loads the `west_coast_usa` map and places an `etk800` vehicle at a fixed location.
* Continuously outputs position, direction vector, and speed of the vehicle.

---

### 3. Record Trajectory Live

```bash
python 1_1_collect_traj_live.py
```

* Connects to the vehicle in the current scenario.
* Records position, direction, and speed at 10 Hz.
* Writes data to `traj/vehicle_trajectory.json`.

---

### 4. Autonomous Driving and Takeover Monitoring

```bash
python 3_monitor_and_takeover.py
```

* Reads the recorded trajectory file and finds start/end points.
* Engages autonomous control once the vehicle is near the start point.
* Blocks keyboard arrow keys (↑↓←→) to simulate control takeover.
* Ends control and releases keys when reaching the destination.
* Uses turn signals as visual cues for start/end zones.

---

## ⚙️ Requirements

* Python 3.7+
* BeamNG.tech v0.34.2.0
* `beamngpy`
* `keyboard` (for input blocking)

Install dependencies:

```bash
pip install beamngpy keyboard
```

## ⚠️ Notes

* You **must launch BeamNG** using `0_0_open_beamng.py` before running any other scripts.
* Update the file paths in scripts to match your BeamNG.tech installation and workspace.
* Make sure the simulation is stable (no crashes) during autonomous control.
