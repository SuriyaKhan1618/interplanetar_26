import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

from moveit.planning import MoveItPy


def add_box(scene, object_id, frame_id, x, y, z, sx, sy, sz):
    collision_object = CollisionObject()

    collision_object.id = object_id
    collision_object.header.frame_id = frame_id
    collision_object.operation = CollisionObject.ADD

    primitive = SolidPrimitive()
    primitive.type = SolidPrimitive.BOX
    primitive.dimensions = [sx, sy, sz]

    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.w = 1.0

    collision_object.primitives.append(primitive)
    collision_object.primitive_poses.append(pose)

    scene.apply_collision_object(collision_object)


def main():
    rclpy.init()

    robot = MoveItPy(node_name="planning_scene")
    planning_scene_monitor = robot.get_planning_scene_monitor()
    with planning_scene_monitor.read_write() as scene:
        add_box(
            scene,
            "object",
            "base_link",
            0.30, 0.00, 0.05,
            0.10, 0.10, 0.10
        )

        add_box(
            scene,
            "drop_zone",
            "base_link",
            0.00, 0.40, 0.025,
            0.20, 0.20, 0.05
        )

    rclpy.shutdown()


if __name__ == "__main__":
    main()