from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active()
    goal_pose = PoseStamped()
    goal_pose.header.stamp = nav.get_clock().now().to_msg()
    goal_pose.header.frame_id = "map"
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0
    nav.goToPose(goal_pose)
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback is not None:
            nav.get_logger().info(f'剩余距离: {feedback.distance_remaining:.2f}米')
    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        nav.get_logger().info('导航成功！')
    elif result == TaskResult.CANCELED:
        nav.get_logger().info('导航被取消！')
    elif result == TaskResult.FAILED:
        nav.get_logger().info('导航失败！')
    nav.destroy_node()
    rclpy.shutdown()