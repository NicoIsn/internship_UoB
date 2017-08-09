#! /usr/bin/env morseexec

import sys
import subprocess
import os
import random

from morse.builder import *
from strands_sim.builder.robots import Scitosa5 
from NewScitosA5 import *
"""
robot = Scitosa5(with_cameras = Scitosa5.WITHOUT_CAMERAS)
# Specify the initial position and rotation of the robot
robot.translate(x=4,y=-4, z=0)
robot.rotate(z=-1.57)
"""
# let's create a second robot that represent a human to follow
robot2 = newScitosa5(with_cameras = newScitosa5.WITHOUT_CAMERAS)
#newScitosa5(with_cameras = newScitosa5.WITHOUT_CAMERAS)
robot2.translate(x=5,y=-4, z=0)
robot2.rotate(z=-1.57)
# Keyboard control

robot2.keyboard = Keyboard()
robot2.append(robot2.keyboard)

#for human robot2.use_world_camera()
#robot2.disable_keyboard_control()

# An odometry sensor to get odometry information
odometry = Odometry()
robot2.append(odometry)
odometry.add_interface('ros', topic="/odom")
odometry.add_interface('socket')

# An hokuyo lidar
scan = Hokuyo()
scan.translate(x=0.1094, z=0.3848)
robot2.append(scan)
scan.properties(Visible_arc = True)
scan.properties(laser_range = 30.0)
scan.properties(resolution = 1.0)
scan.properties(scan_window = 180.0)
scan.create_laser_arc()
scan.add_interface('ros', topic='/base_scan')
"""
# define the way to move 
waypoint=Waypoint()
waypoint.add_interface('socket') #doit etre avant append
robot2.append(waypoint)
"""
motion = MotionXYW()
motion.properties(ControlType = 'Position')
robot2.append(motion)
motion.add_interface('ros', topic='/cmd_vel')

# Add default interface for our robot's components
# robot2.add_default_interface('ros')



# Always finish by specifying where the model of the environment is
model_file=os.path.join(os.path.dirname(os.path.abspath( __file__)),'maps/cs_lg.blend')
# Create the environment with the model file, and use fast mode - you can do
# this to speed things up a little when you're using the scitos A5 without
# depthcams.
env = Environment(model_file,fastmode=False)
# Place the camera in the environment
env.set_camera_location([12, -7, 25])
# Aim the camera so that it's looking at the environment
env.set_camera_rotation([0.5, 0.1, 0.43])


