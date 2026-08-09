FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /ros2_ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-pip \
    python3-pyqt6\
    libsqlite3-dev \
    portaudio19-dev \
    alsa-utils \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-geometry-msgs \
    ros-jazzy-nav-msgs \
    x11-apps \
    mesa-utils \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir vosk sounddevice --break-system-packages

COPY . .

RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
