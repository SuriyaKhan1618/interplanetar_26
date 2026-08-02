FROM osrf/ros:jazzy-desktop
WORKDIR /ros2_ws
COPY . .

RUN apt update && apt install -y python3-colcon-common-extensions
RUN echo "source /opt/ros/jazzy/setup.bash"

CMD ["bash"]
