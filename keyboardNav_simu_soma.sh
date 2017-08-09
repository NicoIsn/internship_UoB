xterm -e "roslaunch mongodb_store mongodb_store.launch db_path:=/home/isnard/Documents/database" &

sleep 1s

xterm -e "roslaunch strands_morse bham_cs_morse.launch" &

sleep 1s

xterm -e "roslaunch strands_morse bham_cs_nav2d.launch" &

sleep 1s

xterm -e "roslaunch soma_manager soma_local.launch map_name:=map" &

sleep 1s

xterm -e "rosrun soma_roi_manager soma_roi_node.py 1" &

sleep 1s

xterm -e "rosrun rviz rviz"