import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

class QuadTFBroadcaster(Node):
    def __init__(self):
        super().__init__("quad_tf_broadcaster")

        self.broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Odometry,
            '/model/quadrotor/odometry',
            self.callback,
            10
        )

    def callback(self, msg):
        transform = TransformStamped()

        transform.header.stamp = msg.header.stamp
        transform.header.frame_id = msg.header.frame_id
        transform.child_frame_id = msg.child_frame_id

        transform.transform.translation.x = msg.pose.pose.position.x
        transform.transform.translation.y = msg.pose.pose.position.y
        transform.transform.translation.z = msg.pose.pose.position.z

        transform.transform.rotation = msg.pose.pose.orientation

        self.broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = QuadTFBroadcaster()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()