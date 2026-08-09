from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'quad_main'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    py_modules=[
        'quad_main.widgets'
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, glob('quad_main/*.qss')),
        ('share/' + package_name, glob('quad_main/*.otf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='suriya',
    maintainer_email='sfkhan1618@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "quad_controller = quad_main.main:main"
        ],
    },
)
