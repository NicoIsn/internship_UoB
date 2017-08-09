#!/bin/bash

environment_name="multiple_robots_simu"
strands_morse=`rospack find strands_morse`
example=`rospack find multiple_robots_simu`
path="$example"
PYTHONPATH="$path/src:$common/src:$PYTHONPATH"
MORSE_RESOURCE_PATH="$strands_morse:$common/data:$common/robots:$path:$MORSE_RESOURCE_PATH"
export MORSE_RESOURCE_PATH PYTHONPATH
added=`$strands_morse/morse_config.py $environment_name $path`
echo "Running morse on $path with PYTHONPATH=$PYTHONPATH and MORSE_RESOURCE_PATH=$MORSE_RESOURCE_PATH"
PATH=/opt/strands-morse-simulator/bin:$PATH

xterm -hold -e "morse run multiple_robots_simu `rospack find multiple_robots_simu`/construction_map_morse.py" &
sleep 3s
xterm -hold -e "roslaunch morse_basic_example_nav nav.launch" &
sleep 3s
xterm -e "morse run multiple_robots_simu `rospack find multiple_robots_simu`/robot_human_control_morse_new.py"
