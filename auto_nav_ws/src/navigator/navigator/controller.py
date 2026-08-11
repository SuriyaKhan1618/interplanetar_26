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
        self.current_index = 0
        self.lookahead = 0.3
        self.goal_tolerance = 0.05

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
        self.current_index = 0

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

    def get_waypoint(self, robot_x, robot_y):
        poses = self.path.poses

        for i in range(self.current_index, len(poses)):
            waypoint_x = poses[i].pose.position.x
            waypoint_y = poses[i].pose.position.y
            distance = math.hypot(waypoint_x - robot_x, waypoint_y - robot_y)

            if distance >= self.lookahead:
                self.current_index = i
                return waypoint_x, waypoint_y, False

        final_waypoint = poses[-1].pose.position
        dist_to_final = math.hypot(final_waypoint.x - robot_x, final_waypoint.y - robot_y)

        if dist_to_final <= self.goal_tolerance:
            return final_waypoint.x, final_waypoint.y, True

        return final_waypoint.x, final_waypoint.y, False

    def control_bot(self):
        if self.path is None:
            return

        robot_pose = self.get_pose()
        if robot_pose is None:
            return

        robot_x, robot_y, robot_yaw = robot_pose
        robot_yaw_deg = math.degrees(robot_yaw)

        target_x, target_y, reached_goal = self.get_waypoint(
            robot_x, robot_y
        )

        if reached_goal:
            self.get_logger().info("Goal reached!")
            self.path = None
            return

        self.get_logger().info(f"Target waypoint: {self.current_index}")

def main():
    rclpy.init()
    node = Controller()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()