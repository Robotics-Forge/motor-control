from setuptools import setup

package_name = 'servo_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='Servo control package for ROS2',
    entry_points={
        'console_scripts': [
            'servo_control_node = servo_control.servo_control_node:main',
        ],
    },
)
