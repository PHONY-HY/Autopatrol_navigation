from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active()
    goal_poses=[]
    goal_pose = PoseStamped()
    goal_pose.header.stamp = nav.get_clock().now().to_msg()
    goal_pose.header.frame_id = "map"
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0
    goal_poses.append(goal_pose)
    goal_pose1 = PoseStamped()
    goal_pose1.header.stamp = nav.get_clock().now().to_msg()
    goal_pose1.header.frame_id = "map"
    goal_pose1.pose.position.x = 1.0
    goal_pose1.pose.position.y = 2.0
    goal_pose1.pose.orientation.w = 1.0
    goal_poses.append(goal_pose1)
    goal_pose2 = PoseStamped()
    goal_pose2.header.stamp = nav.get_clock().now().to_msg()
    goal_pose2.header.frame_id = "map"
    goal_pose2.pose.position.x = 3.0
    goal_pose2.pose.position.y = 3.0
    goal_pose2.pose.orientation.w = 1.0
    goal_poses.append(goal_pose2)
    nav.followWaypoints(goal_poses)
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback is not None:
            nav.get_logger().info(f'路点编号:{feedback.current_waypoint}')
    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        nav.get_logger().info('导航成功！')
    elif result == TaskResult.CANCELED:
        nav.get_logger().info('导航被取消！')
    elif result == TaskResult.FAILED:
        nav.get_logger().info('导航失败！')
    nav.destroy_node()
    rclpy.shutdown()