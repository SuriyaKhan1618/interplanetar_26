##TASK 2: AUTONOMOUS NAVIGATION & VISION

This task utilizes the question world and has a separate package with a launch file for navigation and vision.


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

Run the Turtlebot4 simulation in Gazebo:

```bash
ros2 launch questions main_assignment.launch.py
```

Start all navigation and computer vision nodes:

```bash
ros2 launch navigator navigator.launch.py
```

