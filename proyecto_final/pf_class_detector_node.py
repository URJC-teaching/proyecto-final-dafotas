# Copyright 2025 Rodrigo Pérez-Rodríguez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection3DArray
from tf2_ros import Buffer, TransformListener
from std_msgs.msg import Bool


class PFClassDetectorNode(Node):
    def __init__(self):
        super().__init__('pf_class_detector_node')

        # Parameter: target YOLO class
        self.declare_parameter('target_class', 'person')
        self.target_class = self.get_parameter('target_class').value
        self.declare_parameter('base_frame', 'base_footprint')
        self.base_frame = self.get_parameter('base_frame').value

        # TF2 buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Subscriber to Detection3DArray
        self.sub = self.create_subscription(
            Detection3DArray,
            'input_detection_3d',
            self.detection_callback,
            rclpy.qos.qos_profile_sensor_data
        )

        self.person_pub = self.create_publisher(Bool, 'person_detected', 10)

    def detection_callback(self, msg: Detection3DArray):
        self.get_logger().info("AAAAAAAAAAAAAAAAAAAAAAAA")
        if not msg.detections:
            return

        # Find first detection of the target class
        for detection in msg.detections:
            if detection.results and detection.results[0].hypothesis.class_id == self.target_class:
                self.person_pub.publish(Bool(data=True))
                break

        


def main(args=None):
    rclpy.init(args=args)
    node = PFClassDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
