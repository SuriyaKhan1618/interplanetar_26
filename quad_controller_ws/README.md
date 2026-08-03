##TASK 1: VOICE-CONTROLLED QUADROTOR & TELEMETRY

This uses a basic SDF placeholder that subscribes to cmd_vel and publishes /odom. It can be replaced with any model that uses the similar.

##PREREQUISITE SETUP

A running Docker container as specified in the main directory's README.

Clean previous build artifacts:

'''bash
rm -rf build install log
'''

##RUN

'''bash
colcon build
source install/setup.bash
'''

Launch the quadrotor simulation:

'''bash
ros2 launch quad_sim sim.launch.py
'''