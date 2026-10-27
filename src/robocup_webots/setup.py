from glob import glob                                     
from setuptools import find_packages, setup

package_name = 'robocup_webots'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),         
        ('share/' + package_name + '/worlds', glob('worlds/*.wbt')),        
        ('share/' + package_name + '/resource', ['resource/nao.urdf']),     
        ('share/' + package_name + '/motions', glob('motions/*.motion')),   
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sirawich-anantapong',
    maintainer_email='sw.anantapong@gmail.com',
    description='robocup project university of glasgow',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ball_detector = robocup_webots.ball_detector:main',
            'striker = robocup_webots.striker:main',
            'defender = robocup_webots.defender:main',
            'goalkeeper = robocup_webots.goalkeeper:main',
        ],
    },
)