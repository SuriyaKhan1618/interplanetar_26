import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from shape_msgs.msg import SolidPrimitive

from moveit.planning import PlanningSceneInterface


class PlanningScene(Node):
    def __init__(self):
        super().__init__('planning_scene')

        self.scene = PlanningSceneInterface()

        self.add_object()
        self.add_drop_zone()

    def add_object(self):
        object_pose = Pose()

        object_pose.position.x = 0.30
        object_pose.position.y = 0.00
        object_pose.position.z = 0.05
        object_pose.orientation.w = 1.0

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.10, 0.10, 0.10]

        self.scene.add_collision_object(
            'object',
            primitive,
            object_pose
        )

    def add_drop_zone(self):
        drop_pose = Pose()

        drop_pose.position.x = 0.00
        drop_pose.position.y = 0.40
        drop_pose.position.z = 0.025
        drop_pose.orientation.w = 1.0

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.20, 0.20, 0.05]

        self.scene.add_collision_object(
            'drop_zone',
            primitive,
            drop_pose
        )

def main():
    rclpy.init()
    node = PlanningScene()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__=='__main__':
    main()