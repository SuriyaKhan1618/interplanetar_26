import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class TelemetryPublisher(Node):
    def __init__(self):
        super().__init__("telemetry_publisher")

        self.subscription = self.create_subscription(Odometry, '/odom', self.callback, 10)
        self.publisher = self.create_publisher()
        
    def callback(self, msg):
        self.get_logger().info(f"Drone sends: {msg}")

def main():
    rclpy.init()
    node = TelemetryPublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()