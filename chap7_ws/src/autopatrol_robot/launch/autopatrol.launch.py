import os
import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.actions import SetEnvironmentVariable
from launch.substitutions import EnvironmentVariable
import sys


def generate_launch_description():
    # 获取与拼接默认路径
    autopatrol_robot_dir = get_package_share_directory(
        'autopatrol_robot')
    autopatrol_robot_prefix = os.path.dirname(os.path.dirname(autopatrol_robot_dir))
    install_root = os.path.dirname(autopatrol_robot_prefix)
    autopatrol_interfaces_prefix = os.path.join(install_root, 'autopatrol_interfaces')
    autopatrol_interfaces_py = os.path.join(
        autopatrol_interfaces_prefix,
        'local',
        'lib',
        f'python{sys.version_info.major}.{sys.version_info.minor}',
        'dist-packages'
    )
    autopatrol_interfaces_lib = os.path.join(autopatrol_interfaces_prefix, 'lib')

    patrol_config_path = os.path.join(
        autopatrol_robot_dir, 'config', 'patrol_config.yaml')

    action_set_pythonpath = SetEnvironmentVariable(
        name='PYTHONPATH',
        value=[
            autopatrol_interfaces_py,
            ':',
            EnvironmentVariable('PYTHONPATH', default_value='')
        ]
    )
    action_set_ld_library_path = SetEnvironmentVariable(
        name='LD_LIBRARY_PATH',
        value=[
            autopatrol_interfaces_lib,
            ':',
            EnvironmentVariable('LD_LIBRARY_PATH', default_value='')
        ]
    )
    
    action_node_turtle_control = launch_ros.actions.Node(
        package='autopatrol_robot',
        executable='patrol_node',
        parameters=[patrol_config_path]
    )
    action_node_patrol_client = launch_ros.actions.Node(
        package='autopatrol_robot',
        executable='speaker_node',
    )

    return launch.LaunchDescription([
        action_set_pythonpath,
        action_set_ld_library_path,
        action_node_turtle_control,
        action_node_patrol_client,
    ])