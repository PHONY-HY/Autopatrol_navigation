# 基于 ROS 2 + Navigation2 的自动巡检机器人项目

## 1. 项目简介

本项目实现了一个自动巡检机器人仿真系统，基于 ROS 2 Humble、Gazebo 和 Navigation2。

机器人可按预设巡逻点循环导航，并在每个目标点执行以下动作：
- 语音播报当前状态；
- 采集相机图像并保存到本地。

## 2. 工作空间结构

主要功能包说明：

- `heshibot_description`：机器人模型、传感器、Gazebo 仿真配置
- `heshibot_navigation2`：Navigation2 启动与参数配置
- `heshibot_application`：Python 导航示例节点
- `heshibot_application_cpp`：C++ 导航示例节点
- `autopatrol_interfaces`：自动巡检服务接口（`SpeechText.srv`）
- `autopatrol_robot`：自动巡检核心逻辑（巡逻、语音服务端/客户端、图像保存）

## 3. 环境要求

- Ubuntu 22.04
- ROS 2 Humble

## 4. 依赖安装

### 4.1 导航与建图相关

```bash
sudo apt update
sudo apt install -y \
	ros-$ROS_DISTRO-nav2-bringup \
	ros-$ROS_DISTRO-slam-toolbox
```

### 4.2 仿真与机器人描述相关

```bash
sudo apt install -y \
	ros-$ROS_DISTRO-robot-state-publisher \
	ros-$ROS_DISTRO-joint-state-publisher \
	ros-$ROS_DISTRO-gazebo-ros-pkgs \
	ros-$ROS_DISTRO-ros2-controllers \
	ros-$ROS_DISTRO-xacro
```

### 4.3 语音与视觉相关

```bash
sudo apt install -y python3-pip espeak-ng ros-$ROS_DISTRO-tf-transformations
pip3 install --user espeakng transforms3d
```

## 5. 构建与运行

在工作空间根目录（`chap7_ws`）执行：

### 5.1 构建

```bash
colcon build
```

### 5.2 启动仿真环境

```bash
source install/setup.bash
ros2 launch heshibot_description gazebo_sim.launch.py
```

### 5.3 启动导航

```bash
source install/setup.bash
ros2 launch heshibot_navigation2 navigation2.launch.py
```

### 5.4 启动自动巡检

```bash
source install/setup.bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

## 6. 巡检参数配置

巡检参数文件：`autopatrol_robot/config/patrol_config.yaml`

可配置项：
- `initial_point`：初始位姿 `[x, y, yaw]`
- `target_points`：巡逻点序列（每 3 个值为一组 `x, y, yaw`）
- `img_save_path`：图片保存目录（建议显式配置）
- `use_sim_time`：是否启用仿真时间

示例图片目录：

```yaml
img_save_path: /home/heshi/ros2learning/extra_storage/chap7/chap7_ws/images
```

## 7. 常见问题

- 若节点找不到接口或动态库，请确认已执行：
	`source install/setup.bash`
- 若语音服务一直等待，请先确认 `speaker_node` 是否正常启动。

## 8. 作者

- Heshi