#initialisation de la database
xterm -e "roslaunch mongodb_store mongodb_store.launch db_path:=/home/isnard/Documents/database" &
sleep 1s

#lancement de la simu morse dans blender
xterm -e "roslaunch multiple_robots_simu 2robots_nav_morse.launch" &
sleep 1s

#lancement du l'interface pour gerer la database : soma
xterm -e "roslaunch soma_manager soma_local.launch map_name:=map" &
sleep 1s

#lancement de l'enregistrement des positions du robot dans la db
xterm -hold -e "roslaunch multiple_robots_simu trajectory_to_db.launch" &
sleep 1s

#chargement des region d'interet roi avec la database
xterm -e "rosrun soma_roi_manager soma_roi_node.py 1" &
sleep 1s

xterm -e "rosrun rviz rviz" 



