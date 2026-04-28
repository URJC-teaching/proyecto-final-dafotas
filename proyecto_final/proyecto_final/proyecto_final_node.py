import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3, Twist
import math
from rclpy.duration import Duration
import time

class FinalProjectNode(Node):
    def __init__(self):
        super().__init__('final_project_node')



def main(args=None):
    
    rclpy.init(args=args)
    node = VFFControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
