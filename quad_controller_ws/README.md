##TASK 1: VOICE-CONTROLLED QUADROTOR & TELEMETRY

This uses a basic SDF placeholder that subscribes to /quadrotor/cmd_vel for Twist and publishes Odometry to model/quadrotor/odometry. It can be replaced with any model that uses the same message types. The main.py may be remapped to adjust topic names.

##PREREQUISITE SETUP

A running Docker container as specified in the main directory's README.

Clean previous build artifacts:

```bash
rm -rf build install log
```

##RUN

```bash
colcon build
source install/setup.bash
```

Launch the quadrotor simulation:

```bash
ros2 launch quad_sim sim.launch.py
```

##EXIT

Since Ctrl+C raises Python and PyQt6 conflicts, please instead exit the GUI app with the 'x' button.