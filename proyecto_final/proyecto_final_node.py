import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Vector3, Twist
import math
from rclpy.duration import Duration
from hri_client.hri_client import HRIClient
from navigation_client.navigation_client import NavigationClient
import time
from std_msgs.msg import Bool

class FinalProjectNode(Node):
    def __init__(self):
        super().__init__('final_project_node')


        self.person_sub = self.create_subscription(
            Bool,
            'person_detected',
            self.person_callback,
            10
        )

        #Parametros de YOLO
        self.person_found = False
        self.wait_until = 0.0

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
        
        
        self.state = 'init'

    def control_cycle(self):

        if time.time() < self.wait_until:
            return

        if self.state == 'init':
            if self.nav_client_.wait_for_action_server(1.0):
                self.get_logger().info('Servidor disponible, preparado para navegar')
                self.server_ready_ = True
                self.state = 'navigate'
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
            

            # Comprueba si hay persona
            if self.person_found == True:
                self.get_logger().info(f'Persona detectada.') 
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
            
            self.state = 'goal_reached'
            return

        if self.state == 'goal_reached':
            # Si el objetivo se ha alcanzado, pasa a espera para hablar
            if self.nav_client_.was_goal_successful():
                self.get_logger().info(
                    f'Objetivo {self.current_goal_index + 1} completado con éxito'
                )

                # Habla diciendo personas encontradas en este tramo
                num_wp = self.current_goal_index + 1
                mensaje = "He llegado al waypoint. "
                if self.person_found:
                    mensaje += "He visto persona."
                # if num_wp == 1:
                    # mensaje = f"He llegado al waypoint {wp_letras}. He visto {p_letras} personas"
                else:
                    mensaje += "No he detectado personas."
                self.hri_client.start_speaking(mensaje)
                self.wait_until = time.time() + 8.0

                self.get_logger().info(f'Robot dice: {mensaje}')

                self.state = 'waiting_after_goal'
            else:
                self.get_logger().warn(f'Objetivo {self.current_goal_index + 1} fallido')
                self.goal_sent_ = False
                self.state = 'navigate'
            return

        if self.state == 'waiting_after_goal':
            # Para time.time() >= self.wait_until (tiempo cumplido para que hable)
            self.current_goal_index += 1

            if self.current_goal_index < len(self.target_poses_):
                self.person_found = False
                self.goal_sent_ = False
                self.state = 'navigate'
                self.get_logger().info(f'Preparando siguiente objetivo: {self.current_goal_index + 1}')
            else:
                self.state = 'finished'
                self.wait_until = time.time() + 5.0
            return

        if self.state == 'finished':
            return
            # self.get_logger().info('Misión finalizada')
            # self.timer.cancel()
            # self.get_logger().info(f'Total de personas detectadas durante la navegación            # self.get_logger().info('Aplicación finalizada')

    def person_callback(self, msg: Bool):
        if not self.person_found:
            self.person_found = True
            
            self.get_logger().debug(f'Received Person Detected message: {msg}')

    # Si n > 9, se intenta como string por lo menos, no se omite el número
    def numero_a_texto(self, n):
        numeros_letras = {
            0: "cero", 1: "una", 2: "dos", 3: "tres", 4: "cuatro", 
            5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve"
        }
        return numeros_letras.get(n, str(n)) 


def main(args=None):
    
    rclpy.init(args=args)
    node = FinalProjectNode()
    rclpy.spin(node)

    
    node.destroy_node()
    rclpy.shutdown()
