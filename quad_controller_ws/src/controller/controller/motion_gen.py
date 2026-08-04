import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class MotionGenerator(Node):
    def __init__(self):
        super().__init__("motion_generator")

        self.velocities = {
            "velX": 0.0,
            "velY": 0.0,
            "velZ": 0.0
        }

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(String, 'usr_com', self.calc_vel, 10)
        self.timer = self.create_timer(0.1, self.pub_vel)

    def calc_vel(self, msg):
        if(msg.data == "forward"):
            self.velocities["velX"] = 0.3
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0
        elif(msg.data == "backward"):
            self.velocities["velX"] = -0.3
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0
        elif(msg.data == "up"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.3
        elif(msg.data == "down"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = -0.3
        elif(msg.data == "left"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.3
            self.velocities["velZ"] = 0.0
        elif(msg.data == "right"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = -0.3
            self.velocities["velZ"] = 0.0
        elif(msg.data == "stop"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0
                                                   
    def pub_vel(self):
        velocity = Twist()
        velocity.linear.x = self.velocities["velX"]
        velocity.linear.y = self.velocities["velY"]
        velocity.linear.z = self.velocities["velZ"]
        self.publisher.publish(velocity)

def main():
    rclpy.init()
    node = MotionGenerator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()