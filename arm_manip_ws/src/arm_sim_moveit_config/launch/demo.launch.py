import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    pkg_share = get_package_share_directory("arm_sim_moveit_config")

    moveit_config = (
        MoveItConfigsBuilder("arm_sim", package_name="arm_sim_moveit_config")
        .robot_description_semantic(file_path=os.path.join(pkg_share, "config", "arm_sim.srdf"))
        .planning_pipelines(
            pipelines=["ompl"],
        )
        .trajectory_execution(file_path=os.path.join(pkg_share, "config", "moveit_controllers.yaml"))
        .to_moveit_configs()
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    run_move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(pkg_share, "config", "moveit.rviz")],
        parameters=[moveit_config.to_dict()],
    )

    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
    )

    return LaunchDescription([
        static_tf,
        robot_state_publisher,
        run_move_group,
        rviz_node,
    ])