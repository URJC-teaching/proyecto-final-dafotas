from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    #Argumentos globales para poder cambiarlo desde linea de comandos facilmente y pasarselo a otros launchers
    
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='yolov8m.pt',
        description='Modelo YOLO a usar'
    )
    
    model_type_arg = DeclareLaunchArgument(
        'model_type',
        default_value='YOLO',
        choices=['YOLO', 'World', 'YOLOE'],
        description='Tipo de modelo Ultralytics'
    )
    
    device_arg = DeclareLaunchArgument(
        'device',
        default_value='cpu',
        choices=['cpu', 'cuda'],
        description='Dispositivo para inferencia'
    )
    
    threshold_arg = DeclareLaunchArgument(
        'threshold',
        default_value='0.5',
        description='Umbral de confianza mínimo'
    )
    
    imgsz_height_arg = DeclareLaunchArgument(
        'imgsz_height',
        default_value='480',    
        description='Altura de imagen para inferencia'
    )
    
    imgsz_width_arg = DeclareLaunchArgument(
        'imgsz_width',
        default_value='640',
        description='Ancho de imagen para inferencia'
    )
    
    input_image_topic_arg = DeclareLaunchArgument(
        'input_image_topic',
        default_value='/rgbd_camera/image',
        description='Topic de imagen de entrada'
    )
    
    input_depth_topic_arg = DeclareLaunchArgument(
        'input_depth_topic',
        default_value='/rgbd_camera/depth_image',
        description='Topic de profundidad de entrada'
    )
    
    input_depth_info_topic_arg = DeclareLaunchArgument(
        'input_depth_info_topic',
        default_value='/rgbd_camera/camera_info',
        description='Topic de info de cámara de profundidad'
    )
    
    use_tracking_arg = DeclareLaunchArgument(
        'use_tracking',
        default_value='True',
        description='Activar seguimiento de objetos'
    )
    
    use_3d_arg = DeclareLaunchArgument(
        'use_3d',
        default_value='True',
        description='Activar detección 3D'
    )
    
    use_debug_arg = DeclareLaunchArgument(
        'use_debug',
        default_value='True',
        description='Activar nodo de debug'
    )
    
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='yolo',
        description='Namespace para los nodos YOLO'
    )

    target_class = DeclareLaunchArgument(
        'target_class',
        default_value='person'
    )
    
    base_frame = DeclareLaunchArgument(
        'base_frame',
        default_value='base_footprint'
    )

    optical_frame = DeclareLaunchArgument(
        'optical_frame',
        default_value='camera_rgb_optical_frame'
    )

    #include_yolo = IncludeLaunchDescription(
    #    PythonLaunchDescriptionSource(
    #        PathJoinSubstitution([
    #            FindPackageShare('yolo_bringup'),
    #            'launch',
    #            'yolo.launch.py'
    #        ])
    #    ),
    #    launch_arguments={
    #        # Modelo
    #        'model': LaunchConfiguration('model'),
    #        'model_type': LaunchConfiguration('model_type'),
    #        'device': LaunchConfiguration('device'),
    #        'threshold': LaunchConfiguration('threshold'),
    #        
    #        # Imagen
    #        'imgsz_height': LaunchConfiguration('imgsz_height'),
    #        'imgsz_width': LaunchConfiguration('imgsz_width'),
    #        
    #        # Topics (los más importantes para cambiar según cámara)
    #        'input_image_topic': LaunchConfiguration('input_image_topic'),
    #        'input_depth_topic': LaunchConfiguration('input_depth_topic'),
    #        'input_depth_info_topic': LaunchConfiguration('input_depth_info_topic'),
    #        
    #        # Funcionalidades
    #        'use_tracking': LaunchConfiguration('use_tracking'),
    #        'use_3d': 'True',
    #        'use_debug': LaunchConfiguration('use_debug'),
    #        
    #        # Namespace
    #        'namespace': LaunchConfiguration('namespace'),
    #    }.items()
    # )
    #
    #include_yolo_3d = IncludeLaunchDescription(
    #    PythonLaunchDescriptionSource(
    #        PathJoinSubstitution([
    #            FindPackageShare('camera'),
    #            'launch',
    #            'yolo_detection3d.launch.py'
    #        ])
    #    )
    # )
    #
    proyecto_final_node = Node(
		package='proyecto_final',
		executable='proyecto_final_node',
		name='proyecto_final_node',
		parameters=[{}],
		remappings=[]
	 )
    
    #pf_class_detector_node = Node(
	#	package='proyecto_final',
	#	executable='pf_class_detector_node',
	#	name='pf_class_detector_node',
	#	parameters=[{
	#		'target_class': LaunchConfiguration('target_class'),
	#		'base_frame': LaunchConfiguration('base_frame')
	#	}],
	#	remappings=[
	#		('/input_detection_3d', '/yolo/detections_3d')
	#	]
	# )
    
    return LaunchDescription([
        #Argumentos globales
        model_arg,
        model_type_arg,
        device_arg,
        threshold_arg,
        imgsz_height_arg,
        imgsz_width_arg,
        input_image_topic_arg,
        input_depth_topic_arg,
        input_depth_info_topic_arg,
        use_tracking_arg,
        use_3d_arg,
        use_debug_arg,
        namespace_arg,
        target_class,
        base_frame,
        optical_frame,
        
        #Launchers
        #include_yolo,
        #include_yolo_3d,
        
		#Nodos
		proyecto_final_node,
		#pf_class_detector_node
    ])