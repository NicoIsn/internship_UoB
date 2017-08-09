#! /usr/bin/env morseexec

""" Basic MORSE simulation scene for <nav_tutorial> environment

Feel free to edit this template as you like!
"""
import sys
import subprocess
import os
import random
from morse.builder import *

# A 'naked' PR2 robot to the scene
robot = BasePR2()
robot.translate(x=2.5, y=3.2, z=0.0)
robot.add_interface('ros')

scan = Hokuyo()
scan.translate(x=0.275, z=0.252)
robot.append(scan)
scan.properties(Visible_arc = False)
scan.properties(laser_range = 30.0)
scan.properties(resolution = 1.0)
scan.properties(scan_window = 180.0)
scan.create_laser_arc()

scan.add_interface('ros', topic='/base_scan')


# An odometry sensor to get odometry information
odometry = Odometry()
robot.append(odometry)
odometry.add_interface('ros', topic="/odom")
odometry.add_interface('socket')

# Keyboard control
keyboard = Keyboard()
robot.append(keyboard)

motion = MotionXYW()
motion.properties(ControlType = 'Position')
robot.append(motion)
motion.add_interface('ros', topic='/cmd_vel')

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