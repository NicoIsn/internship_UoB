#! /usr/bin/env morseexec

import sys
import subprocess
import os
import random
import pymorse
import time

from morse.builder import *
from strands_sim.builder.robots import Scitosa5 
from NewScitosA5 import *
from New2ScitosA5 import *
#from robot_human_control_morse import Robot_human_control_morse

#--------------------------------------------------FIRST ROBOT--------------------------------------------#

robot = ATRV()

# Specify the initial position and rotation of the robot
robot.translate(x=3,y=-4, z=0)
robot.rotate(z=-1.57)

#keyboard
robot.keyboard = Keyboard()
robot.append(robot.keyboard)

# An odometry sensor to get odometry information
robot.odometry = Odometry()
robot.append(robot.odometry)
robot.odometry.add_interface('socket')

# define the position
pose = Pose()
robot.append(pose)
pose.add_interface('socket')

#battery
robot.battery = BatteryStateSensor()
robot.battery.translate(x=0.00,y=0.0,z=0.0)
robot.battery.properties(Range = 0.45)
robot.append(robot.battery)
robot.battery.add_interface('socket')
robot.battery.properties(DischargingRate=0.01)

# An hokuyo lidar
robot.scan = Hokuyo()
robot.scan.translate(x=0.275, z=0.252)
robot.append(robot.scan)
robot.scan.properties(Visible_arc = False)
robot.scan.properties(laser_range = 30.0)
robot.scan.properties(resolution = 1.0)
robot.scan.properties(scan_window = 180.0)
robot.scan.create_laser_arc()
robot.scan.add_interface('socket')

# motion
waypoint=Waypoint()
waypoint.add_interface('socket') #doit etre avant append
robot.append(waypoint)

#--------------------------------------------------SECOND ROBOT--------------------------------------------#

# let's create a second robot that represent a human to follow
robot2 = newScitosa5(with_cameras = newScitosa5.WITHOUT_CAMERAS)
robot2.translate(x=5,y=-4, z=0)
robot2.rotate(z=-1.57)

# Keyboard control
robot2.keyboard = Keyboard()
robot2.append(robot2.keyboard)

# An odometry sensor to get odometry information
robot2.odometry = Odometry()
robot2.append(robot2.odometry)
robot2.odometry.add_interface('ros', topic="/odom")
robot2.odometry.add_interface('socket')

# define the position
pose2 = Pose()
pose2.add_interface('ros',topic='/pose')
robot2.append(pose2)
pose2.add_interface('socket')

#battery
robot2.battery = BatteryStateSensor()
robot2.battery.translate(x=0.00,y=0.0,z=0.0)
robot2.battery.properties(Range = 0.45)
robot2.append(robot2.battery)
robot2.battery.add_interface('ros', topic= "/battery_state")
robot2.battery.add_interface('socket')
robot2.battery.properties(DischargingRate=0.01)

# An hokuyo lidar
robot2.scan = Hokuyo()
robot2.scan.translate(x=0.1094, z=0.3848)
robot2.append(robot2.scan)
robot2.scan.properties(Visible_arc = True)
robot2.scan.properties(laser_range = 30.0)
robot2.scan.properties(resolution = 1.0)
robot2.scan.properties(scan_window = 180.0)
robot2.scan.create_laser_arc()
robot2.scan.add_interface('ros', topic='/base_scan')
robot2.scan.add_interface('socket')

#motion
robot2.motion = MotionXYW()
robot2.motion.properties(ControlType = 'Position')
robot2.append(robot2.motion)
robot2.motion.add_interface('ros', topic='/cmd_vel')
robot2.motion.add_interface('socket')

#--------------------------------------------------ENVIRONMENT--------------------------------------------#

# Always finish by specifying where the model of the environment is
model_file=os.path.join(os.path.dirname(os.path.abspath( __file__)),'maps/cs_lg.blend')
# Create the environment with the model file, and use fast mode - you can do
# this to speed things up a little when you're using the scitos A5 without
# depthcams.
env = Environment(model_file,fastmode=False)
# Place the camera in the environment
env.set_camera_location([12, -7, 25])
# Aim the camera so that it's looking at the environment
env.set_camera_rotation([0.5, 0.1, 0.5])
"""
time.sleep(5)

with pymorse.Morse() as simu:
	# We can start the simulation 
	control = Robot_human_control_morse(simu)
	control.simulation()
"""
