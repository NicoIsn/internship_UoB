#! /usr/bin/env morseexec

import sys
import subprocess
import os
import random

from morse.builder import *
from strands_sim.builder.robots import Scitosa5

robot = Scitosa5(with_cameras = Scitosa5.WITHOUT_CAMERAS)
# Specify the initial position and rotation of the robot
robot.translate(x=2,y=2, z=0)
robot.rotate(z=-1.57)

# Specify where the model of the environment is
model_file=os.path.join(os.path.dirname(os.path.abspath( __file__)),'maps/basic_map.blend')
# Create the environment with the model file, and use fast mode - you can do
# this to speed things up a little when you're using the scitos A5 without
# depthcams.
env = Environment(model_file,fastmode=True)
# Place the camera in the environment
env.set_camera_location([0, 0, 10])
# Aim the camera so that it's looking at the environment
env.set_camera_rotation([0.5, 0, -0.5])

