from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    wayfinder = Node(
        package='navigator',
        executable='wayfinder',
        name='wayfinder',
        output='screen'
    )

    navigator = Node(
        package='navigator',
        executable='navigator',
        name='navigator',
        output='screen'
    )

    return LaunchDescription([
        wayfinder,
        navigator
    ])