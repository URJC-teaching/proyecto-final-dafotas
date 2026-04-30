import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3, Twist
import math
from rclpy.duration import Duration
import time

from simple_hri_interfaces.srv import Speech

class FinalProjectNode(Node):
    def __init__(self):
        super().__init__('final_project_node')


        self.person_found = false

        self.attractive_sub = self.create_subscription(
            Vector3,
            'attractive_vector',
            self.attractive_callback,
            10
        )

        self.client = self.create_client(Speech, '/tts_service')
        

        self.state = 'INIT'
        # Declarar parámetros para cada waypoint
        self.declare_parameter('nav1.x', 0.0)
        self.declare_parameter('nav1.y', 0.0)
        self.declare_parameter('nav2.x', 0.0)
        self.declare_parameter('nav2.y', 0.0)
        # Leer los waypoints desde los parámetros
        self.waypoints = [
            {
                'x': self.get_parameter('nav1.x').get_parameter_value().double_value,
                'y': self.get_parameter('nav1.y').get_parameter_value().double_value
            },
            {
                'x': self.get_parameter('nav2.x').get_parameter_value().double_value,
                'y': self.get_parameter('nav2.y').get_parameter_value().double_value
            }
        ]
        self.current_goal = None
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.timer = self.create_timer(1.0, self.state_machine)
        self.get_logger().info('fsm_nav_node started')

    def state_machine(self):
        if self.state == 'INIT':
            self.get_logger().info('State: INIT -> NAV1')
            self.state = 'NAV1'
            self.current_index = 0
            self.send_goal(self.current_index)
        # Las transiciones NAV1->NAV2 y NAV2->DONE se manejan en goal_response_callback

    def send_goal(self, index):
        self.nav_action_client.wait_for_server()
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = self.waypoints[index]['x']
        goal_msg.pose.pose.position.y = self.waypoints[index]['y']
        goal_msg.pose.pose.orientation.w = 1.0
        
        self.get_logger().info(f'Sending goal: {self.waypoints[index]}')
        send_goal_future = self.nav_action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return
        
        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        result = future.result().result
        if self.state == 'NAV1':
            self.get_logger().info('State: NAV1 -> NAV2')
            self.state = 'NAV2'
            self.current_index = 1
            self.send_goal(self.current_index)
        elif self.state == 'NAV2':
            self.get_logger().info('State: NAV2 -> DONE')
            self.state = 'DONE'

        def attractive_callback(self, msg: Vector3):
            self.attractive_vec = msg
            if not self.person_found:
                self.person_found = true
            self.get_logger().debug(f'Received Attractive vector: x={msg.x:.2f}, y={msg.y:.2f}. Magnitude={math.hypot(msg.x, msg.y):.2f}. Angle={math.degrees(math.atan2(msg.y, msg.x)):.2f} deg')

        

    

def main(args=None):
    
    rclpy.init(args=args)
    node = VFFControllerNode()
    rclpy.spin(node)

    
    node.destroy_node()
    rclpy.shutdown()
