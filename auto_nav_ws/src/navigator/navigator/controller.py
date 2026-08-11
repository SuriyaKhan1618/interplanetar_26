import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import Image
from rclpy.qos import (
    QoSProfile,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSReliabilityPolicy,
)

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf_transformations import euler_from_quaternion

import math

import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np

class Controller(Node):
    def __init__(self):
        super().__init__("navigator")

        self.path = None
        self.current_index = 0
        self.lookahead = 0.5
        self.goal_tolerance = 0.05

        self.linear_speed = 0.4
        self.kp_angular = 1.5
        self.max_angular_speed = 1.5

        path_qos = QoSProfile(
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        reliability=QoSReliabilityPolicy.RELIABLE,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=1,
    )
        cmd_qos = QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.VOLATILE,
        depth=10,
    )

        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)

        self.subscription = self.create_subscription(
            Path,
            "/path",
            self.get_path,
            path_qos
        )
        self.publisher = self.create_publisher(TwistStamped, "/cmd_vel", cmd_qos)
        self.image_subscription = None
        self.bridge = CvBridge()

        self.timer = self.create_timer(0.05, self.control_bot)

    def get_path(self, msg):
        self.path = msg
        self.current_index = 0

        self.destroy_subscription(self.subscription)
        self.subscription = None

    def get_pose(self):
        path_frame = self.path.header.frame_id or 'odom'

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

        target_x, target_y, reached_goal = self.get_waypoint(
            robot_x, robot_y
        )

        if reached_goal:
            self.get_logger().info("Goal reached!")

            cmd = TwistStamped()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.header.frame_id = "base_link"

            self.publisher.publish(cmd)
            self.path = None

            self.create_image_subscription()

            return

        dx = target_x - robot_x
        dy = target_y - robot_y

        x_local = dx * math.cos(-robot_yaw) - dy * math.sin(-robot_yaw)
        y_local = dx * math.sin(-robot_yaw) + dy * math.cos(-robot_yaw)

        target_angle = math.atan2(y_local, x_local)

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = "base_link"

        if abs(target_angle) > math.pi / 2:
            cmd.twist.linear.x = 0.0

            angular_velocity = self.kp_angular * target_angle
            angular_velocity = max(
                -self.max_angular_speed,
                min(self.max_angular_speed, angular_velocity)
            )
            cmd.twist.angular.z = angular_velocity
        else:
            L_sq = x_local**2 + y_local**2
            if L_sq > 0.0:
                curvature = (2.0*y_local)/L_sq
            else:
                curvature = 0.0

            cmd.twist.linear.x = self.linear_speed

            angular_velocity = (
                curvature
                * self.linear_speed
                * self.kp_angular
            )
            angular_velocity = max(
                -self.max_angular_speed,
                min(self.max_angular_speed, angular_velocity)
            )

            cmd.twist.angular.z = angular_velocity

        self.publisher.publish(cmd)

        self.get_logger().info(
        f"Target waypoint: {self.current_index} | "
        f"Target local: ({x_local:.2f}, {y_local:.2f}) | "
        f"Angle: {math.degrees(target_angle):.1f}°"
    )

    def create_image_subscription(self):
        self.image_subscription = self.create_subscription(
            Image,
            '/oakd/rgb/preview/image_raw',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        try:
            try:
                image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            except CvBridgeError as e:
                self.get_logger().warn(f"Error: {e}")
                return

            gray, hsv = self.preprocess_image(image)
            spheres = self.find_sphere(gray)

            if spheres:
                color = self.get_largest_sphere_color(hsv, spheres)
                self.get_logger().info(f"Color of the largest sphere: {color}")
            else:
                self.get_logger().info("No sphere color detected")
            
        finally:
            if self.image_subscription is not None:
                self.destroy_subscription(self.image_subscription)
                self.image_subscription = None

    def preprocess_image(self, image):
        blurred = cv2.GaussianBlur(image, (9, 9), 2)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        return gray, hsv

    def find_sphere(self, gray_image):
        circles = cv2.HoughCircles(
            gray_image,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=40,
            param1=50,
            param2=30,
            minRadius=15,
            maxRadius=200
        )

        if circles is None:
            return

        circles = np.uint16(np.around(circles))
        detected_circles = circles[0, :]
        sorted_spheres = sorted(
            detected_circles,
            key=lambda c: c[2],
            reverse=True
        )

        return sorted_spheres[:3]

    def get_largest_sphere_color(self, hsv_image, sorted_spheres):
        if not sorted_spheres:
            return None

        largest_sphere = sorted_spheres[0]
        x, y, r = largest_sphere

        height, width, _ = hsv_image.shape
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))

        hsv_pixels = hsv_image[
            max(0, y-r//3):min(height, y+r//3),
            max(0, x-r//3):min(width, x+r//3)
        ]

        h, s, v = np.mean(hsv_pixels.reshape(-1, 3), axis=0)

        if s < 50 or v < 50:
            color_name = "White/Grey/Black"
        elif (h >= 0 and h <= 10) or (h >= 170 and h <= 180):
            color_name = "Red"
        elif 11 <= h <= 25:
            color_name = "Orange"
        elif 26 <= h <= 35:
            color_name = "Yellow"
        elif 36 <= h <= 85:
            color_name = "Green"
        elif 86 <= h <= 125:
            color_name = "Blue"
        elif 126 <= h <= 169:
            color_name = "Purple"
        else:
            color_name = "Unknown"

        return color_name

def main():
    rclpy.init()
    node = Controller()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()