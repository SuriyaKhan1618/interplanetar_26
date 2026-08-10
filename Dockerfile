FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV GZ_SIM_RESOURCE_PATH=/opt/ros/jazzy/share
ENV TURTLEBOT3_MODEL=burger

WORKDIR /ros2_ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-pip \
    python3-pyqt6 \
    python3-transforms3d \
    libsqlite3-dev \
    portaudio19-dev \
    libasound2-dev \
    alsa-utils \
    pulseaudio-utils \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-geometry-msgs \
    ros-jazzy-nav-msgs \
    ros-jazzy-tf-transformations \
    ros-jazzy-turtlebot3-gazebo \
    ros-jazzy-turtlebot3 \
    ros-jazzy-turtlebot3-description \
    ros-jazzy-turtlebot3-msgs \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-tf2-ros \
    x11-apps \
    mesa-utils \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libgl1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir vosk sounddevice --break-system-packages

COPY . .

WORKDIR /ros2_ws/quad_controller_ws
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

WORKDIR /ros2_ws/auto_nav_ws
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

WORKDIR /ros2_ws/arm_manip_ws
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/quad_controller_ws/install/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/auto_nav_ws/install/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/arm_manip_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
