#!/bin/bash
environment_name="basic_example"
strands_morse=`rospack find strands_morse`
example=`rospack find basic_example`
path="$example"
common="$strands_morse/strands_sim"

PYTHONPATH="$path/src:$common/src:$PYTHONPATH"
MORSE_RESOURCE_PATH="$strands_morse:$common/data:$common/robots:$path:$MORSE_RESOURCE_PATH"
export MORSE_RESOURCE_PATH PYTHONPATH
added=`$strands_morse/morse_config.py $environment_name $path`
echo "Running morse on $path with PYTHONPATH=$PYTHONPATH and MORSE_RESOURCE_PATH=$MORSE_RESOURCE_PATH"
PATH=/opt/strands-morse-simulator/bin:$PATH

#xterm -e "rosrun gmapping slam_gmapping scan:=/base_scan _odom_frame:=/odom"  &
#sleep 0.5s
xterm -hold -e "roslaunch basic_example nav.launch" &
sleep 0.5s
xterm -hold -e "morse run basic_example `rospack find basic_example`/nav_tutorial/default.py"  
