import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from tf2_ros import Buffer, TransformListener, TransformException

def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

class BurgerTracker(Node):
    def __init__(self):
        super().__init__("burger_tracker")

        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def control_loop(self):
        try:
            transform = self.buffer.lookup_transform(
                'base_footprint',
                'quadrotor/base_footprint',
                rclpy.time.Time ()
            )

            rel_x = transform.transform.translation.x
            rel_y = transform.transform.translation.y

            distance = math.hypot(rel_x, rel_y)
            angle_target = normalize_angle(math.atan2(rel_y, rel_x))

            command = TwistStamped()
            command.header.stamp = self.get_clock().now().to_msg()
            command.header.frame_id = "base_footprint"

            min_distance = 0.5

            if distance > min_distance:
                command.twist.angular.z = max(-1.0, min(1.8, 2.0*angle_target))
                if abs(angle_target) < math.radians(45):
                    command.twist.linear.x = max(0.0, min(0.40, 1.0*(distance - min_distance)))
                else:
                    command.twist.linear.x = 0.0
            else:
                command.twist.angular.z = 0.0
                command.twist.linear.x = 0.0

            self.publisher.publish(command)
        except TransformException as e:
            self.get_logger().warn(f"Failed to fetch transform: {e}")

def main():
    rclpy.init()
    node = BurgerTracker()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()