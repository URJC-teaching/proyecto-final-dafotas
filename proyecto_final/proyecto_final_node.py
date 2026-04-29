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

        self.client = self.create_client(Speech, '/tts_service')

def main(args=None):
    
    rclpy.init(args=args)
    node = VFFControllerNode()
    rclpy.spin(node)

    
    node.destroy_node()
    rclpy.shutdown()
