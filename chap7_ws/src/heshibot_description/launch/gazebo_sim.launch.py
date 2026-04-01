import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    urdf_package_path=get_package_share_directory("heshibot_description")
    default_xacro_path=os.path.join(urdf_package_path,"urdf","heshibot/heshibot.urdf.xacro")
    default_gazebo_world_path=os.path.join(urdf_package_path,"world","custom_room.world")

    action_declare_arg_mode_path=launch.actions.DeclareLaunchArgument(
        name="model",default_value=str(default_xacro_path),description="加载的模型文件路径"
    )

    substitution_command_result=launch.substitutions.Command(['xacro ',launch.substitutions.LaunchConfiguration('model')])
    robot_description_value=launch_ros.parameter_descriptions.ParameterValue(substitution_command_result,value_type=str)

    action_robot_state_publisher=launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description":robot_description_value}]
    )

    action_launch_gazebo=launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            [get_package_share_directory('gazebo_ros'),'/launch','/gazebo.launch.py']
        ),
        launch_arguments=[('world',default_gazebo_world_path),('verbose','true')]
    )

    action_spawn_entity=launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic','/robot_description','-entity','heshibot']
    )

    action_load_joint_state_broadcaster=launch_ros.actions.Node(
        package='controller_manager',
        executable='spawner',
        arguments=['heshibot_joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    action_load_effort_controller=launch_ros.actions.Node(
        package='controller_manager',
        executable='spawner',
        arguments=['heshibot_effort_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    action_load_diff_drive_controller=launch_ros.actions.Node(
        package='controller_manager',
        executable='spawner',
        arguments=['heshibot_diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )
    # action_joint_state_publisher=launch_ros.actions.Node(
    #     package="joint_state_publisher",
    #     executable="joint_state_publisher",
    # )

    # action_rviz_node=launch_ros.actions.Node(
    #     package="rviz2",
    #     executable="rviz2",
    #     arguments=['-d',default_rviz_config_path]
    # )

    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_robot_state_publisher,
        action_launch_gazebo,
        action_spawn_entity,
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_spawn_entity,
                on_exit=[action_load_joint_state_broadcaster]
            )
        ),
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_load_joint_state_broadcaster,
                on_exit=[action_load_effort_controller]
            )
        ),
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_load_effort_controller,
                on_exit=[action_load_diff_drive_controller]
            )
        ),
    ])