import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('quad_sim')
    sdf_file_path = os.path.join(pkg_share, 'urdf', 'quadrotor.sdf')

    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args':'-r empty.sdf'}.items()
    )

    spawn_quadrotor = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', sdf_file_path,
            '-name', 'quadrotor',
            '-z', '0.2'
        ],
        output='screen'
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/quadrotor/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            'model/quadrotor/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_sim,
        spawn_quadrotor,
        ros_gz_bridge
    ])