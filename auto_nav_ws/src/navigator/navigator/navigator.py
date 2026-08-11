import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

import asyncio
import threading
import websockets
import math
import json

def yaw_to_quaternion(yaw):
    return(
        0.0,
        0.0,
        math.sin(yaw/2.0),
        math.cos(yaw/2.0)
    )

class Navigator(Node):
    def __init__(self):
        super().__init__("navigator")

        self.publisher = self.create_publisher(Path, "/path", 10)
        self.url = "ws://localhost:8765"

        self.is_running = True

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_event_loop,
                                       daemon=True)
        self.thread.start()

        asyncio.run_coroutine_threadsafe(self.connect_socket(), self.loop)

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def connect_socket(self):
        while self.is_running and rclpy.ok():
            try:
                async with websockets.connect(self.url) as socket:
                    while self.is_running and rclpy.ok():
                        data = await socket.recv()

                        path_msg = self.parse_json(data)
                        if path_msg:
                            self.publisher.publish(path_msg)

            except(websockets.exceptions.ConnectionClosedError,
                   ConnectionRefusedError) as e:
                self.get_logger().warn(f"Connection lost: {e}")
                await asyncio.sleep(2.0)

            except Exception as e:
                self.get_logger().warn(f"Error: {e}")
                await asyncio.sleep(2.0)

    def parse_json(self, raw_json):
        try:
            raw_data = json.loads(raw_json)
            waypoints = raw_data.get("waypoints", [])

            path_msg = Path()
            path_msg.header.stamp = self.get_clock().now().to_msg()
            path_msg.header.frame_id = 'odom'

            for waypoint in waypoints:
                pose_stamped = PoseStamped()
                pose_stamped.header = path_msg.header

                pose_stamped.pose.position.x = float(waypoint.get("x", 0.0))
                pose_stamped.pose.position.y = float(waypoint.get("y", 0.0))
                pose_stamped.pose.position.z = 0.0

                qx, qy, qz, qw = yaw_to_quaternion(waypoint.get("yaw", 0.0))
                pose_stamped.pose.orientation.x = qx
                pose_stamped.pose.orientation.y = qy
                pose_stamped.pose.orientation.z = qz
                pose_stamped.pose.orientation.w = qw

                path_msg.poses.append(pose_stamped)

            return path_msg

        except json.JSONDecodeError as e:
            self.get_logger().warn(f"Error: {e}")
            return None

    def destroy_node(self):
        self.is_running = False
        if self.loop.is_running:
            self.loop.call_soon_threadsafe(self.loop.stop)
        super.destroy_node()


def main():
    rclpy.init()
    node = Navigator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()