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

    burger_spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('turtlebot3_gazebo'),
                'launch',
                'spawn_turtlebot3.launch.py'
            )
        ),
        launch_arguments={
            'x_pose':'-2.0',
            'y_pose':'0.0'
        }.items()
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

    quad_tf_broadcaster = Node(
        package='quad_sim',
        executable='quad_tf_bc',
        name='quad_tf_broadcaster',
        output='screen'
    )

    tracker = Node(
        package='quad_sim',
        executable='tracker',
        name='tracker',
        output='screen'
    )

    world_to_quadrotor_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_to_quadrotor_odom',
        arguments=[
            '--x', '0.0', 
            '--y', '0.0', 
            '--z', '0.2', 
            '--frame-id', 'world', 
            '--child-frame-id', 'quadrotor/odom'],
        output='screen'
    )

    world_to_burger_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_to_burger_odom',
        arguments=[
            '--x', '-2.0', 
            '--y', '0.0', 
            '--z', '0.0', 
            '--frame-id', 'world', 
            '--child-frame-id', 'odom'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_sim,
        spawn_quadrotor,
        burger_spawn,
        ros_gz_bridge,
        quad_tf_broadcaster,
        tracker,
        world_to_quadrotor_odom,
        world_to_burger_odom
    ])