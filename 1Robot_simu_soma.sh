#initialisation de la database
xterm -e "roslaunch mongodb_store mongodb_store.launch db_path:=/home/isnard/Documents/database" &
sleep 1s

#lancement de la simu morse dans blender
xterm -e "roslaunch basic_example 1robot_nav.launch" &
sleep 1s

#lancement de la navigation/repérage du robot scitos
#xterm -e "roslaunch strands_morse bham_cs_nav2d.launch" &
#sleep 1s

#lancement du l'interface pour gerer la database : soma
xterm -e "roslaunch soma_manager soma_local.launch map_name:=map" &
sleep 1s

#chargement des region d'interet roi avec la database
xterm -e "rosrun soma_roi_manager soma_roi_node.py 1" &
sleep 1s

#lancement de rviz
xterm -e "rosrun rviz rviz" 


