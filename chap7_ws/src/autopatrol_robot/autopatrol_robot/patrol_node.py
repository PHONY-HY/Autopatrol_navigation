import rclpy
import sys
from pathlib import Path
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy.time
from rclpy.duration import Duration
from tf2_ros import TransformListener, Buffer
from tf_transformations import quaternion_from_euler
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

try:
    from autopatrol_interfaces.srv import SpeechText
except ModuleNotFoundError:
    current_file = Path(__file__).resolve()
    install_root = current_file.parents[5]
    fallback_path = install_root / 'autopatrol_interfaces' / 'local' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'dist-packages'
    if fallback_path.exists():
        sys.path.insert(0, str(fallback_path))
    from autopatrol_interfaces.srv import SpeechText

class PatrolNode(BasicNavigator):
    def __init__(self):
        # 让节点名与参数文件中的顶层 key 保持一致: patrol_node
        super().__init__(node_name='patrol_node')
        self.declare_parameter('initial_point',[0.0, 0.0, 0.0])
        self.declare_parameter('target_points',[0.0, 0.0, 0.0, 1.0, 1.0, 1.57])
        self.declare_parameter('img_save_path','')
        # 兼容用户写法 targetpoints（无下划线）
        self.declare_parameter('targetpoints',[])
        self.initial_point = self.get_parameter('initial_point').value
        self.target_points = self.get_parameter('target_points').value
        target_points = self.get_parameter('targetpoints').value
        self.img_save_path = self.get_parameter('img_save_path').value
        if not self.img_save_path:
            self.img_save_path = str(Path.home() / 'ros2_patrol_images')
        Path(self.img_save_path).mkdir(parents=True, exist_ok=True)
        if target_points:
            self.target_points = target_points
        self.buffer = Buffer()
        self.tf_listener = TransformListener(self.buffer, self)
        self.get_logger().info(f'加载 target_points: {self.target_points}')
        self.cv_bridge = CvBridge()
        self.image_subscriber = self.create_subscription(
            Image,
            '/camera_sensor/image_raw',
            self.image_callback,
            1
        )
        self.latest_img = None

    def image_callback(self, msg):
        self.latest_img=msg

    def record_img(self):
        if self.latest_img is not None:
            pose=self.get_current_pose()
            cv_image = self.cv_bridge.imgmsg_to_cv2(self.latest_img)
            filename = f'{self.img_save_path}/patrol_{pose.translation.x:.2f}_{pose.translation.y:.2f}.jpg'
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f'已保存巡逻图像: {filename}')
        else:
            self.get_logger().warn('尚未收到图像，跳过保存')

    def get_pose_by_xyyaw(self,x,y,yaw):
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = "map"
        pose.pose.position.x = x
        pose.pose.position.y = y
        quat = quaternion_from_euler(0, 0, yaw)
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]
        return pose
    
    def init_robot_pose(self):
        initial_pose = self.get_pose_by_xyyaw(self.initial_point[0], self.initial_point[1], self.initial_point[2])
        self.setInitialPose(initial_pose)
        self.waitUntilNav2Active()

    def get_target_points(self):
        target_poses = []
        for i in range(0, len(self.target_points), 3):
            x = self.target_points[i]
            y = self.target_points[i+1]
            yaw = self.target_points[i+2]
            target_poses.append(self.get_pose_by_xyyaw(x, y, yaw))
            self.get_logger().info(f'目标点{i//3}: x={x}, y={y}, yaw={yaw}')
        return target_poses
    
    def nav_to_pose(self,target_pose):
        self.goToPose(target_pose)
        while not self.isTaskComplete():
            feedback = self.getFeedback()
            if feedback is not None:
                    self.get_logger().info(f'剩余距离: {feedback.distance_remaining:.2f}米')
        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('导航成功！')
        elif result == TaskResult.CANCELED:
            self.get_logger().info('导航被取消！')
        elif result == TaskResult.FAILED:
            self.get_logger().info('导航失败！')

    def get_current_pose(self):
        while rclpy.ok():
            try:
                result=self.buffer.lookup_transform('map', 'base_link', rclpy.time.Time(seconds=0.0), Duration(seconds=1.0))
                transform=result.transform
                self.get_logger().info(f'平移: {transform.translation}')
                return transform
            except Exception as e:
                self.get_logger().error(f'获取当前位姿失败: {e}')

    def speech_text(self,text):
        client = self.create_client(SpeechText, 'speak_text')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待语音服务可用...')
        request = SpeechText.Request()
        request.text = text
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            if future.result().result:
                self.get_logger().info('语音播放成功！')
            else:
                self.get_logger().error('语音播放失败！')
        else:
            self.get_logger().error(f'调用语音服务失败: {future.exception()}')


def main():
    rclpy.init()
    patrol_node = PatrolNode()
    patrol_node.speech_text('巡逻机器人已启动，正在初始化...')
    patrol_node.init_robot_pose()
    patrol_node.speech_text('机器人初始化完成，开始巡逻！')
    while rclpy.ok():
        target_poses = patrol_node.get_target_points()
        for target_pose in target_poses:
            patrol_node.speech_text(f'正在前往下一个目标点: x={target_pose.pose.position.x:.2f}, y={target_pose.pose.position.y:.2f}')
            patrol_node.nav_to_pose(target_pose)
            patrol_node.speech_text('已到达目标点，正在记录图像...')
            patrol_node.record_img()
    patrol_node.speech_text('巡逻结束，机器人即将关闭。')

    patrol_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()