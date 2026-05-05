import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Vector3, Twist
import math
from rclpy.duration import Duration
from hri_client.hri_client import HRIClient
from navigation_client.navigation_client import NavigationClient
import time

class FinalProjectNode(Node):
    def __init__(self):
        super().__init__('final_project_node')


        self.attractive_sub = self.create_subscription(
            Vector3,
            'attractive_vector',
            self.attractive_callback,
            10
        )

        #Parametros de YOLO
        self.person_found = False
        self.person_count = 0
        self.person_already_counted = False

        #Parametros de HRI
        self.hri_client = HRIClient(self)

        # Declarar parámetros para cada waypoint
        self.declare_parameter('nav1.x', 0.0)
        self.declare_parameter('nav1.y', 0.0)
        self.declare_parameter('nav2.x', 0.0)
        self.declare_parameter('nav2.y', 0.0)
        
        self.x1 = self.get_parameter('nav1.x').get_parameter_value().double_value
        self.y1 = self.get_parameter('nav1.y').get_parameter_value().double_value
        self.x2 = self.get_parameter('nav2.x').get_parameter_value().double_value
        self.y2 = self.get_parameter('nav2.y').get_parameter_value().double_value
        
        #Parametros de navegación
        self.timer = self.create_timer(1.0, self.control_cycle)

        self.nav_client_ = NavigationClient(self)
        self.target_poses_ = [
            self.nav_client_.create_pose_stamped(self.x1, self.y1, 0.0),
            self.nav_client_.create_pose_stamped(self.x2, self.y2, 0.0),
        ]

        self.current_goal_index = 0
        self.server_ready_ = False
        self.goal_sent_ = False

        self.get_logger().info('Aplicación de navegación iniciada (Python)')
        
        self.timer_ = self.create_timer(0.5, self.control_cycle)
        
        
        self.state = 'init'

    def control_cycle(self):
        if self.state == 'init':
            if self.nav_client_.wait_for_action_server(1.0):
                self.get_logger().info('Servidor disponible, preparado para navegar')
                self.server_ready_ = True
                self.state = 'navigate' #Pasa a navegación
            return
        
        if self.state == 'navigate':
            # Si no se ha enviado el objetivo, lo envía
            if not self.goal_sent_:
                target_pose = self.target_poses_[self.current_goal_index]
                self.get_logger().info(
                    f'Enviando objetivo {self.current_goal_index + 1} de {len(self.target_poses_)}...'
                )
                self.nav_client_.send_goal(target_pose)
                self.goal_sent_ = True
                return
            
            #Comprueba si el objetivo se ha alcanzado o no
            if not self.nav_client_.is_goal_done():
                feedback = self.nav_client_.get_feedback()
                if feedback:
                    t_sec = feedback.navigation_time.sec + feedback.navigation_time.nanosec / 1e9
                    self.get_logger().info(
                        f'\t-Distancia restante: {feedback.distance_remaining:.2f} m | '
                        f'Tiempo: {t_sec:.1f} s'
                    )
                return
            
            # Comprueba si hay persona
            if self.person_found == True and self.person_already_counted == False:
                self.person_count += 1
                self.get_logger().info(f'Persona detectada. Total en este tramo: {self.person_count}')
                self.person_already_counted = True
                return


            self.state = 'goal_reached'
            return

        if self.state == 'goal_reached':
            # Si el objetivo se ha alcanzado, pasa al siguiente o finaliza
            if self.nav_client_.was_goal_successful():
                self.get_logger().info(
                    f'Objetivo {self.current_goal_index + 1} completado con éxito'
                )

                # Habla diciendo personas encontradas en este tramo
                mensaje = f"He llegado al waypoint {self.current_goal_index + 1}. " \
                          f"He encontrado {self.person_count} personas"
                self.hri_client.start_speaking(mensaje)
                self.get_logger().info(f'Robot dice: {mensaje}')
                
                # Resetea contador para el siguiente waypoint
                self.person_count = 0
                self.person_already_counted = False

                self.current_goal_index += 1
                if self.current_goal_index < len(self.target_poses_):
                    self.goal_sent_ = False
                    self.state = 'navigate'
                    self.get_logger().info(
                        f'Preparado para enviar objetivo {self.current_goal_index + 1}'
                    )
                    return

                self.get_logger().info('Todas las metas completadas con éxito')
            else:
                self.get_logger().warn(
                    f'Objetivo {self.current_goal_index + 1} fallido'
                )
            self.get_logger().info(f'Total de personas detectadas durante la navegación: {self.person_count}')
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
