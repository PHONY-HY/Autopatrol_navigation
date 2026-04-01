import rclpy
import sys
from pathlib import Path
from rclpy.node import Node
import espeakng

try:
    from autopatrol_interfaces.srv import SpeechText
except ModuleNotFoundError:
    current_file = Path(__file__).resolve()
    install_root = current_file.parents[5]
    fallback_path = install_root / 'autopatrol_interfaces' / 'local' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'dist-packages'
    if fallback_path.exists():
        sys.path.insert(0, str(fallback_path))
    from autopatrol_interfaces.srv import SpeechText

class Speaker(Node):
    def __init__(self):
        super().__init__('speaker_node')
        self.speech_service = self.create_service(SpeechText, 'speak_text', self.speak_text_callback)
        self.get_logger().info('SpeakerNode已启动，等待文本输入...')
        self.esng = None
        try:
            self.esng = espeakng.Speaker()
            self.esng.voice = 'zh'  # 设置中文语音
        except Exception as e:
            self.get_logger().error(f'初始化语音引擎失败: {e}')

    def speak_text_callback(self, request, response):
        text_to_speak = request.text
        self.get_logger().info(f'接收到文本: "{text_to_speak}"，正在朗读...')
        if self.esng is None:
            self.get_logger().error('语音引擎不可用，跳过朗读')
            response.result = False
            return response
        try:
            self.esng.say(text_to_speak)
            response.result = True
            self.get_logger().info('朗读完成！')
        except Exception as e:
            self.get_logger().error(f'朗读失败: {e}')
            response.result = False
        return response
    
def main():
    rclpy.init()
    speaker_node = Speaker()
    rclpy.spin(speaker_node)
    speaker_node.destroy_node()
    rclpy.shutdown()