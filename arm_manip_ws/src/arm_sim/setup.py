from setuptools import find_packages, setup
from glob import glob

package_name = 'arm_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py') + ['launch/view_robot.launch']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf') + glob('urdf/*.xacro')),
        ('share/' + package_name + '/rviz', ['rviz/default_view.rviz']),
        ('share/' + package_name + '/meshes', glob('meshes/*')), #include meshes
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Azwad Wakif',
    maintainer_email='wakifrajin@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
