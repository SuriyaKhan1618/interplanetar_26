##TASK 3: 6-DOF Robotic Arm Manipulation

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

Run the planning scene in rviz:

```bash
ros2 launch arm_moveit_config demo.launch.py
```
