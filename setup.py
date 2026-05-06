from setuptools import find_packages, setup

package_name = 'proyecto_final'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
		('share/' + package_name + '/launch', ['launch/proyecto_final.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pablogg',
    maintainer_email='paablogg18@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'proyecto_final_node = proyecto_final.proyecto_final_node:main',
			'pf_class_detector_node = proyecto_final.pf_class_detector_node:main',
        ],
    },
)
