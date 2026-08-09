import sys
import os
import zipfile
import urllib.request
from ament_index_python.packages import get_package_share_directory
import math

from PyQt6.QtCore import (
    Qt,
    QSize,
    QThread,
    pyqtSignal
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QStyle
)
from PyQt6.QtGui import QFont, QFontDatabase
from .widgets import CircularButton, OvalButton, ModeSelector

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from rclpy.executors import ExternalShutdownException

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import tf_transformations

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer


def load_stylesheet(filename):
    try:
        pkg_share = get_package_share_directory('quad_main')
        qss_path = os.path.join(pkg_share, filename)
        
        with open(qss_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not load stylesheet '{filename}': {e}")
        return ""


class ROSNode(QThread):
    telemetry_data = pyqtSignal(
        float, float, float,
        float, float, float,
        float, float, float,
        float, float, float
    )

    def __init__(self):
        super().__init__()
        self.node = None

    def run(self):
        rclpy.init()
        self.node = Node("quad_connector")

        self.velocities = {
            "velX": 0.0,
            "velY": 0.0,
            "velZ": 0.0
        }

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.node.create_subscription(
            Odometry,
            "model/quadrotor/odometry",
            self.emit_telemetry,
            qos_profile
        )

        self.node.publisher = self.node.create_publisher(
            Twist,
            "/quadrotor/cmd_vel",
            10
        )

        self.node.create_timer(0.1, self.publish_command)

        try:
            rclpy.spin(self.node)
        except (KeyboardInterrupt, ExternalShutdownException):
            pass
        finally:
            self.node.destroy_node()
            try:
                if rclpy.ok():
                    rclpy.shutdown()
            except Exception as e:
                pass

    def emit_telemetry(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z

        quaternion = [
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        ]

        x_rad, y_rad, z_rad = tf_transformations.euler_from_quaternion(quaternion)

        x_rot = math.degrees(x_rad)
        y_rot = math.degrees(y_rad)
        z_rot = math.degrees(z_rad)

        x_vel = msg.twist.twist.linear.x
        y_vel = msg.twist.twist.linear.y
        z_vel = msg.twist.twist.linear.z

        x_ang_vel = msg.twist.twist.angular.x
        y_ang_vel = msg.twist.twist.angular.y
        z_ang_vel = msg.twist.twist.angular.z

        self.telemetry_data.emit(
            x, y, z,
            x_rot, y_rot, z_rot,
            x_vel, y_vel, z_vel,
            x_ang_vel, y_ang_vel, z_ang_vel
        )

    def calc_velocity(self, command):
        if(command == "forward"):
            self.velocities["velX"] = 0.3
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0
        elif(command == "backward"):
            self.velocities["velX"] = -0.3
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0
        elif(command == "up"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.3
        elif(command == "down"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = -0.3
        elif(command == "left"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.3
            self.velocities["velZ"] = 0.0
        elif(command == "right"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = -0.3
            self.velocities["velZ"] = 0.0
        elif(command == "stop"):
            self.velocities["velX"] = 0.0
            self.velocities["velY"] = 0.0
            self.velocities["velZ"] = 0.0

    def publish_command(self):
        velocity = Twist()
        velocity.linear.x = self.velocities["velX"]
        velocity.linear.y = self.velocities["velY"]
        velocity.linear.z = self.velocities["velZ"]
        self.node.publisher.publish(velocity)

    def stop(self):
        if self.node:
            self.node.executor.wake()
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception as e:
            pass
        self.quit()
        self.wait()


class VoiceProcessor(QThread):
    command_published = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.q = queue.Queue()

        self.commands = [
            "forward",
            "backward",
            "up",
            "down",
            "left",
            "right",
            "stop"
        ]

    def audio_callback(self,indata, frames, time, status):
        if self.is_running:
            self.q.put(bytes(indata))

    def get_model(self):
        cache_dir = os.path.expanduser("~/.cache/vosk")
        model_dir = os.path.join(cache_dir, "vosk-model-small-en-us-0.15")

        if not os.path.exists(model_dir):
            os.makedirs(cache_dir, exist_ok=True)
            zip_path = os.path.join(cache_dir, "vosk-model-small-en-us-0.15.zip")
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

            print(f"Vosk model missing. Downloading from {model_url}...")
            urllib.request.urlretrieve(model_url, zip_path)

            print("Extracting Vosk model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(cache_dir)

            os.remove(zip_path)
            print("Model download and setup complete.")

        return model_dir
    
    def run(self):
        model_path = self.get_model()
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000, json.dumps(self.commands + ["[unk]"]))

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self.audio_callback
        ):
            while self.is_running:
                try:
                    data = self.q.get(timeout=0.5   )
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())

                    recognized_text = result.get("text", "").strip()
                    if recognized_text in self.commands:
                        self.command_published.emit(recognized_text)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()


class TelemetryDashboard(QWidget):
    command_publish = pyqtSignal(str)
    voice_command = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Quadrotor Control Station")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("mainwindow")

        self.screen = QApplication.primaryScreen().availableGeometry()
        self.width = self.screen.width()
        self.height = self.screen.height()

        self.resize(int(self.width/2), int(self.height/2))

        self.satoshi_black = self.external_font("Satoshi-Black.otf", 25)
        self.satoshi_medium = self.external_font("Satoshi-Medium.otf", 15)
        self.satoshi_black_large = self.external_font("Satoshi-Black.otf", 40)

        self.mode = "voice"

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        self.system_panel = QFrame()
        self.system_panel.setObjectName("invisiblepanel")
        self.system_panel_layout = QHBoxLayout(self.system_panel)
        self.system_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.system_panel_layout.setSpacing(0)

        self.status_panel = QFrame()
        self.status_panel.setObjectName("highlightedcontainer")
        self.status_panel.setFrameShadow(QFrame.Shadow.Raised)
        self.status_panel_layout = QVBoxLayout(self.status_panel)

        self.status_label = QLabel("System Online")
        self.status_label.setFont(self.satoshi_black)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setObjectName("blacklabel")
        self.status_panel_layout.addWidget(self.status_label, 1)

        self.status_sublabel = QLabel("All telemetry data is updated.")
        self.status_sublabel.setFont(self.satoshi_medium)
        self.status_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_sublabel.setObjectName("blacklabel")
        self.status_panel_layout.addWidget(self.status_sublabel, 1)

        self.motion_panel = QFrame()
        self.motion_panel.setObjectName("transcontainer")
        self.motion_panel.setFrameShadow(QFrame.Shadow.Sunken)
        self.motion_panel_layout = QVBoxLayout(self.motion_panel)

        self.motion_label = QLabel("Hovering")
        self.motion_label.setFont(self.satoshi_black)
        self.motion_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.motion_label.setObjectName("whitelabel")
        self.motion_panel_layout.addWidget(self.motion_label, 1)

        self.motion_sublabel = QLabel("At (x, y, z)")
        self.motion_sublabel.setFont(self.satoshi_medium)
        self.motion_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.motion_sublabel.setObjectName("whitelabel")
        self.motion_panel_layout.addWidget(self.motion_sublabel, 1)

        self.z_panel = QFrame()
        self.z_panel.setObjectName("transcontainer")
        self.z_panel.setFrameShadow(QFrame.Shadow.Sunken)
        self.z_panel_layout = QVBoxLayout(self.z_panel)

        self.z_label = QLabel("Level flight")
        self.z_label.setFont(self.satoshi_black)
        self.z_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.z_label.setObjectName("whitelabel")
        self.z_panel_layout.addWidget(self.z_label, 1)

        self.z_sublabel = QLabel("At z")
        self.z_sublabel.setFont(self.satoshi_medium)
        self.z_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.z_sublabel.setObjectName("whitelabel")
        self.z_panel_layout.addWidget(self.z_sublabel, 1)

        self.system_panel_layout.addWidget(self.status_panel, 1)
        self.system_panel_layout.addWidget(self.motion_panel, 1)
        self.system_panel_layout.addWidget(self.z_panel, 1)

        self.control_panel = QFrame()
        self.control_panel.setObjectName("panel")
        self.control_panel.setFrameShadow(QFrame.Shadow.Raised)
        self.control_panel_layout = QGridLayout(self.control_panel)
        self.control_panel_layout.setSpacing(5)
        self.control_panel_layout.setContentsMargins(8, 8, 8, 8)

        self.stop = CircularButton("", 150, 75, "stop")
        self.forward = CircularButton("\u2B06", 120, 55, "forward")
        self.backward = CircularButton("\u2B07", 120, 55, "backward")
        self.left = CircularButton("\u2B05", 120, 55, "left")
        self.right = CircularButton("\u27A1", 120, 55, "right")
        self.up = OvalButton("\u2B06\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.", 60, 300, 17, "up")
        self.down = OvalButton(".\n.\n.\n.\n.\n.\n.\n.\n.\n.\n\u2B07", 60, 300, 17, "down")

        self.pause_icon = self.stop.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        self.stop.setIcon(self.pause_icon)
        self.stop.setIconSize(QSize(150, 150))

        self.stop.clicked.connect(lambda: self.command_gen(self.stop.flag))
        self.forward.clicked.connect(lambda: self.command_gen(self.forward.flag))
        self.backward.clicked.connect(lambda: self.command_gen(self.backward.flag))
        self.left.clicked.connect(lambda: self.command_gen(self.left.flag))
        self.right.clicked.connect(lambda: self.command_gen(self.right.flag))
        self.up.clicked.connect(lambda: self.command_gen(self.up.flag))
        self.down.clicked.connect(lambda: self.command_gen(self.down.flag))

        self.control_panel_layout.addWidget(self.up, 0, 0, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.control_panel_layout.addWidget(self.stop, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.control_panel_layout.addWidget(self.forward, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.control_panel_layout.addWidget(self.backward, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.control_panel_layout.addWidget(self.left, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.control_panel_layout.addWidget(self.right, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        self.control_panel_layout.addWidget(self.down, 0, 4, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)        

        self.control_panel_layout.setRowStretch(0, 3)
        self.control_panel_layout.setRowStretch(1, 4)
        self.control_panel_layout.setRowStretch(2, 3)
        self.control_panel_layout.setColumnStretch(0, 1)
        self.control_panel_layout.setColumnStretch(1, 2)
        self.control_panel_layout.setColumnStretch(2, 4)
        self.control_panel_layout.setColumnStretch(3, 2)
        self.control_panel_layout.setColumnStretch(4, 1)

        self.bottom_panel = QFrame()
        self.bottom_panel.setObjectName("invisiblepanel")
        self.bottom_panel_layout = QHBoxLayout(self.bottom_panel)

        self.mode_manager = ModeSelector()
        self.bottom_panel_layout.addWidget(self.mode_manager, 1)

        self.mode_manager.mode.connect(self.on_mode_changed)

        self.right_panel = QFrame()
        self.right_panel.setObjectName("panel")
        self.right_panel.setFrameShadow(QFrame.Shadow.Raised)
        self.right_panel_layout = QGridLayout(self.right_panel)

        self.motion_x_sublabel = QLabel("Angular velocity about x: 0 rad/s")
        self.motion_x_sublabel.setFont(self.satoshi_medium)
        self.motion_x_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motion_x_sublabel.setObjectName("whitelabel")

        self.motion_y_sublabel = QLabel("Angular velocity about y: 0 rad/s")
        self.motion_y_sublabel.setFont(self.satoshi_medium)
        self.motion_y_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motion_y_sublabel.setObjectName("whitelabel")

        self.motion_z_sublabel = QLabel("Angular velocity about z: 0 rad/s")
        self.motion_z_sublabel.setFont(self.satoshi_medium)
        self.motion_z_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motion_z_sublabel.setObjectName("whitelabel")

        self.x_ang_vel_panel = QFrame()
        self.x_ang_vel_panel.setObjectName("transcontainer")
        self.x_ang_vel_panel_layout = QVBoxLayout(self.x_ang_vel_panel)

        self.x_ang_vel_label = QLabel("0°")
        self.x_ang_vel_label.setFont(self.satoshi_black_large)
        self.x_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_ang_vel_label.setObjectName("yellowlabel")
        self.x_ang_vel_panel_layout.addWidget(self.x_ang_vel_label, 1)

        self.x_ang_vel_sublabel = QLabel("About x axis")
        self.x_ang_vel_sublabel.setFont(self.satoshi_medium)
        self.x_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_ang_vel_sublabel.setObjectName("yellowlabel")
        self.x_ang_vel_panel_layout.addWidget(self.x_ang_vel_sublabel, 1)

        self.y_ang_vel_panel = QFrame()
        self.y_ang_vel_panel.setObjectName("transcontainer")
        self.y_ang_vel_panel_layout = QVBoxLayout(self.y_ang_vel_panel)

        self.y_ang_vel_label = QLabel("0°")
        self.y_ang_vel_label.setFont(self.satoshi_black_large)
        self.y_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.y_ang_vel_label.setObjectName("yellowlabel")
        self.y_ang_vel_panel_layout.addWidget(self.y_ang_vel_label, 1)

        self.y_ang_vel_sublabel = QLabel("About y axis")
        self.y_ang_vel_sublabel.setFont(self.satoshi_medium)
        self.y_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.y_ang_vel_sublabel.setObjectName("yellowlabel")
        self.y_ang_vel_panel_layout.addWidget(self.y_ang_vel_sublabel, 1)

        self.z_ang_vel_panel = QFrame()
        self.z_ang_vel_panel.setObjectName("transcontainer")
        self.z_ang_vel_panel_layout = QVBoxLayout(self.z_ang_vel_panel)

        self.z_ang_vel_label = QLabel("0°")
        self.z_ang_vel_label.setFont(self.satoshi_black_large)
        self.z_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.z_ang_vel_label.setObjectName("yellowlabel")
        self.z_ang_vel_panel_layout.addWidget(self.z_ang_vel_label, 1)

        self.z_ang_vel_sublabel = QLabel("About z axis")
        self.z_ang_vel_sublabel.setFont(self.satoshi_medium)
        self.z_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.z_ang_vel_sublabel.setObjectName("yellowlabel")
        self.z_ang_vel_panel_layout.addWidget(self.z_ang_vel_sublabel, 1)

        self.right_panel_layout.addWidget(self.motion_x_sublabel, 1, 0)
        self.right_panel_layout.addWidget(self.motion_y_sublabel, 3, 0)
        self.right_panel_layout.addWidget(self.motion_z_sublabel, 5, 0)
        self.right_panel_layout.addWidget(self.x_ang_vel_panel, 0, 0)
        self.right_panel_layout.addWidget(self.y_ang_vel_panel, 2, 0)
        self.right_panel_layout.addWidget(self.z_ang_vel_panel, 4, 0)

        self.right_panel_layout.setRowStretch(0, 27)
        self.right_panel_layout.setRowStretch(1, 6)
        self.right_panel_layout.setRowStretch(2, 27)
        self.right_panel_layout.setRowStretch(3, 6)
        self.right_panel_layout.setRowStretch(4, 27)
        self.right_panel_layout.setRowStretch(5, 6)

        self.left_panel = QFrame()
        self.left_panel.setObjectName("panel")
        self.left_panel.setFrameShadow(QFrame.Shadow.Raised)
        self.left_panel_layout = QGridLayout(self.left_panel)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_layout.setSpacing(0)

        self.position_panel = QFrame()
        self.position_panel.setObjectName("highlightedcontainer")
        self.position_panel_layout = QVBoxLayout(self.position_panel)

        self.position_prelabel = QLabel("Position")
        self.position_prelabel.setFont(self.satoshi_black)
        self.position_prelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_prelabel.setObjectName("blacklabel")
        self.position_panel_layout.addWidget(self.position_prelabel, 1)

        self.position_label = QLabel("(0, 0, 0)")
        self.position_label.setFont(self.satoshi_black_large)
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setObjectName("blacklabel")
        self.position_panel_layout.addWidget(self.position_label, 1)

        self.position_sublabel = QLabel("In the Cartesian coordinate system")
        self.position_sublabel.setFont(self.satoshi_medium)
        self.position_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_sublabel.setObjectName("blacklabel")
        self.position_panel_layout.addWidget(self.position_sublabel, 1)

        self.x_vel_panel = QFrame()
        self.x_vel_panel.setObjectName("semihighlightedcontainer")
        self.x_vel_panel_layout = QVBoxLayout(self.x_vel_panel)

        self.x_vel_label = QLabel("0 m/s")
        self.x_vel_label.setFont(self.satoshi_black)
        self.x_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_vel_label.setObjectName("blacklabel")
        self.x_vel_panel_layout.addWidget(self.x_vel_label, 1)

        self.x_vel_sublabel = QLabel("In +x direction")
        self.x_vel_sublabel.setFont(self.satoshi_medium)
        self.x_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_vel_sublabel.setObjectName("blacklabel")
        self.x_vel_panel_layout.addWidget(self.x_vel_sublabel, 1)

        self.y_vel_panel = QFrame()
        self.y_vel_panel.setObjectName("semihighlightedcontainer")
        self.y_vel_panel_layout = QVBoxLayout(self.y_vel_panel)

        self.y_vel_label = QLabel("0 m/s")
        self.y_vel_label.setFont(self.satoshi_black)
        self.y_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.y_vel_label.setObjectName("blacklabel")
        self.y_vel_panel_layout.addWidget(self.y_vel_label, 1)

        self.y_vel_sublabel = QLabel("In +y direction")
        self.y_vel_sublabel.setFont(self.satoshi_medium)
        self.y_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.y_vel_sublabel.setObjectName("blacklabel")
        self.y_vel_panel_layout.addWidget(self.y_vel_sublabel, 1)

        self.z_vel_panel = QFrame()
        self.z_vel_panel.setObjectName("semihighlightedcontainer")
        self.z_vel_panel_layout = QVBoxLayout(self.z_vel_panel)

        self.z_vel_label = QLabel("0 m/s")
        self.z_vel_label.setFont(self.satoshi_black)
        self.z_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.z_vel_label.setObjectName("blacklabel")
        self.z_vel_panel_layout.addWidget(self.z_vel_label, 1)

        self.z_vel_sublabel = QLabel("In +z direction")
        self.z_vel_sublabel.setFont(self.satoshi_medium)
        self.z_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.z_vel_sublabel.setObjectName("blacklabel")
        self.z_vel_panel_layout.addWidget(self.z_vel_sublabel, 1)

        self.left_panel_layout.addWidget(self.position_panel, 0, 0)
        self.left_panel_layout.addWidget(self.x_vel_panel, 1, 0)
        self.left_panel_layout.addWidget(self.y_vel_panel, 2, 0)
        self.left_panel_layout.addWidget(self.z_vel_panel, 3, 0)

        self.left_panel_layout.setRowStretch(0, 4)
        self.left_panel_layout.setRowStretch(1, 2)
        self.left_panel_layout.setRowStretch(2, 2)
        self.left_panel_layout.setRowStretch(3, 2)
        
        self.grid_layout.addWidget(self.right_panel, 0, 0, 3, 1)
        self.grid_layout.addWidget(self.system_panel, 0, 1)
        self.grid_layout.addWidget(self.control_panel, 1, 1)
        self.grid_layout.addWidget(self.bottom_panel, 2, 1)
        self.grid_layout.addWidget(self.left_panel, 0, 2, 3, 1)

        self.grid_layout.setRowStretch(0, 2)
        self.grid_layout.setRowStretch(1, 7)
        self.grid_layout.setRowStretch(2, 1)
        self.grid_layout.setColumnStretch(0, 2)
        self.grid_layout.setColumnStretch(1, 6)
        self.grid_layout.setColumnStretch(2, 2)

        self.ros_thread = ROSNode()
        self.voice_thread = VoiceProcessor()

        self.ros_thread.telemetry_data.connect(self.update_telemetry)
        self.voice_thread.command_published.connect(self.voice_command_gen)
        self.command_publish.connect(self.ros_thread.calc_velocity)

        self.ros_thread.start()
        self.voice_thread.start()

    def external_font(self, font_path, font_size):
        try:
            pkg_share = get_package_share_directory("quad_main")
            font_path = os.path.join(pkg_share, font_path)
            font_id = QFontDatabase.addApplicationFont(font_path)
        except Exception as e:
            font_id = -1

        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font_family = font_families[0]
            custom_font = QFont(font_family, font_size, QFont.Weight.Bold)
        else:
            custom_font = QFont("Sans-Serif", font_size)

        return custom_font

    def isHovering(self, x_velocity, y_velocity):
        return math.isclose(x_velocity, 0.0, abs_tol=1e-2) and math.isclose(y_velocity, 0.0, abs_tol=1e-2)

    def isLevelFlight(self, z_velocity):
        if math.isclose(z_velocity, 0.0, abs_tol=1e-2):
            return "level"
        return "asc" if z_velocity > 0 else "desc"

    def update_telemetry(
            self,
            x, y, z,
            x_rot, y_rot, z_rot,
            x_vel, y_vel, z_vel,
            x_ang_vel, y_ang_vel, z_ang_vel
    ):        
        self.position_label.setText(f"({x:.2f}, {y:.2f}, {z:.2f})")

        self.x_vel_label.setText(f"{x_vel:.2f} m/s")
        self.y_vel_label.setText(f"{y_vel:.2f} m/s")
        self.z_vel_label.setText(f"{z_vel:.2f} m/s")

        self.x_ang_vel_label.setText(f"{x_rot:.1f}°")
        self.y_ang_vel_label.setText(f"{y_rot:.1f}°")
        self.z_ang_vel_label.setText(f"{z_rot:.1f}°")

        self.motion_x_sublabel.setText(f"Angular velocity about x: {x_ang_vel:.2f} rad/s")
        self.motion_y_sublabel.setText(f"Angular velocity about y: {y_ang_vel:.2f} rad/s")
        self.motion_z_sublabel.setText(f"Angular velocity about z: {z_ang_vel:.2f} rad/s")

        if self.isHovering(x_vel, y_vel):
            self.motion_label.setText("Hovering")
            self.motion_sublabel.setText(f"At ({x:.2f}, {y:.2f}, {z:.2f})")
        else:
            self.motion_label.setText("Cruising")
            self.motion_sublabel.setText(f"At ({x:.2f}, {y:.2f}, {z:.2f}) now")

        if self.isLevelFlight(z_vel) == "level":
            self.z_label.setText("Level Flight")
            self.z_sublabel.setText(f"At {z:.2f} m")
        elif self.isLevelFlight(z_vel) == "asc":
            self.z_label.setText("Ascending")
            self.z_sublabel.setText(f"At {z:.2f} m now")
        else:
            self.z_label.setText("Descending")
            self.z_sublabel.setText(f"At {z:.2f} m now")

    def command_gen(self, flag):
        self.com_publish("manual", flag)

    def voice_command_gen(self, com):
        self.com_publish("voice", com)

    def com_publish(self, source, com):
        if self.mode != source:
            return
        self.command_publish.emit(com)

    def on_mode_changed(self, mode):
        self.mode = mode

    def closeEvent(self, event):
        self.ros_thread.stop()
        self.voice_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)

    style = load_stylesheet("style.qss")
    app.setStyleSheet(style)

    window = TelemetryDashboard()
    window.show()

    sys.exit(app.exec())

if __name__=="__main__":
    main()