#! /usr/bin/env morseexec

"""
Brings in the CS building simulation environment from bham and uses ScitosA5.
"""
import sys
import subprocess 
import os
from morse.builder import *

# Add a robot with a position sensor and a motion controller
atrv = ATRV()
pose = Pose()
pose.add_interface('socket')
atrv.append(pose)

motion = Waypoint()
motion.add_interface('socket')
atrv.append(motion)


# Environment
env = Environment('land-1/trees')
