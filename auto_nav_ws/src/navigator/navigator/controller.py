import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf_transformations import euler_from_quaternion

import math

class Controller(Node):
    def __init__(self):
        super().__init__("navigator")

        self.path = None

        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)

        self.subscription = self.create_subscription(
            Path,
            "/path",
            self.get_path,
            10
        )

        self.timer = self.create_timer(0.05, self.control_bot)

    def get_path(self, msg):
        self.path = msg

        self.destroy_subscription(self.subscription)
        self.subscription = None

    def get_pose(self):
        path_frame = self.path.header.frame_id

        try:
            tform = self.buffer.lookup_transform(
                path_frame,
                'base_link',
                rclpy.time.Time()
            )

            x = tform.transform.translation.x
            y = tform.transform.translation.y

            q = tform.transform.rotation
            quaternion = [q.x, q.y, q.z, q.w]

            roll, pitch, yaw = euler_from_quaternion(quaternion)

            return x, y, yaw

        except TransformException as e:
            self.get_logger().warn(f"Error: {e}")
            return None

    def control_bot(self):
        if self.path is None:
            return

        pose = self.get_pose()
        if pose is None:
            return

        x, y, yaw = pose
        yaw_deg = math.degrees(yaw)

        self.get_logger().info(f"{x}, {y}, {yaw_deg}")

def main():
    rclpy.init()
    node = Controller()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()