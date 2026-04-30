import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Vector3, Twist
import math
from rclpy.duration import Duration
from hri_client.hri_client import HRIClient
from navigation_client.navigation_client import NavigationClient
import time

from simple_hri_interfaces.srv import Speech
from nav2_msgs.action import NavigateToPose

class FinalProjectNode(Node):
    def __init__(self):
        super().__init__('final_project_node')

        self.person_found = False

        self.attractive_sub = self.create_subscription(
            Vector3,
            'attractive_vector',
            self.attractive_callback,
            10
        )

        self.client = self.create_client(Speech, '/tts_service')

        self.state = 'INIT'
        self.current_goal = None
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.timer = self.create_timer(1.0, self.control_cycle)
        self.get_logger().info('fsm_nav_node started')

        self.nav_client_ = NavigationClient(self)
        self.target_pose_ = self.nav_client_.create_pose_stamped(6.0, -2.0, 0.0)
        
        self.hri_client = HRIClient(self)

        self.server_ready_ = False
        self.goal_sent_ = False

        self.points_reached = 0

        self.get_logger().info('Aplicación de navegación iniciada (Python)')
        
        self.timer_ = self.create_timer(0.5, self.control_cycle)

    def control_cycle(self):
        if not self.server_ready_:
            if self.nav_client_.wait_for_action_server(1.0):
                self.get_logger().info('Servidor disponible, preparado para navegar')
                self.server_ready_ = True
            return

        if not self.goal_sent_:
            self.get_logger().info('Enviando objetivo de navegación...')
            self.nav_client_.send_goal(self.target_pose_)
            self.goal_sent_ = True
            return

        if not self.nav_client_.is_goal_done():
            feedback = self.nav_client_.get_feedback()
            if feedback:
                t_sec = feedback.navigation_time.sec + feedback.navigation_time.nanosec / 1e9
                self.get_logger().info(
                    f'\t-Distancia restante: {feedback.distance_remaining:.2f} m | '
                    f'Tiempo: {t_sec:.1f} s'
                )
            return

        if self.nav_client_.was_goal_successful():
            self.get_logger().info('Navegación completada con éxito')
        else:
            self.get_logger().warn('Navegación fallida')

        self.timer_.cancel()
        self.get_logger().info('Aplicación finalizada')

    def attractive_callback(self, msg: Vector3):
        if not self.person_found:
            self.person_found = True
        self.get_logger().debug(f'Received Attractive vector: x={msg.x:.2f}, y={msg.y:.2f}. Magnitude={math.hypot(msg.x, msg.y):.2f}. Angle={math.degrees(math.atan2(msg.y, msg.x)):.2f} deg')

        

    

def main(args=None):
    
    rclpy.init(args=args)
    node = FinalProjectNode()
    rclpy.spin(node)

    
    node.destroy_node()
    rclpy.shutdown()
