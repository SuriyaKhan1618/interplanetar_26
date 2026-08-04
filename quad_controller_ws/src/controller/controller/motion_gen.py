import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MotionGenerator(Node):
    def __init__(self):
        super().__init__("motion_generator")

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.callback)

    def callback(self):
        velocity = Twist()
        velocity.linear.x = 0.3
        velocity.linear.y = 0.0
        velocity.linear.z = 0.1
        velocity.angular.x = 0.0
        velocity.angular.y = 0.0
        velocity.angular.z = 0.2
        self.publisher.publish(velocity)

def main():
    rclpy.init()
    node = MotionGenerator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()