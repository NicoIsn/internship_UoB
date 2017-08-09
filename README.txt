						 _______________________________________________________________________
						|					Author : 	Nicolas ISNARD 							|		
						|					From: 		Polytech Paris UPMC						|
						|					Date : 		11/06/17 to 11/08/17					|
						|					Statut : 	intern									|
						|					At : 		University of Birmingham				|							
						|_______________________________________________________________________|
I. Introduction:
	After learning ROS, Morse, MongoDB and all applications required for this internship, I started by making tutorial simulations and adding my own manipulation with my own code. That led me to make 2 main simulations at the end of my internship that I will present now. Those 2 simulations are in the multiple_robots_simu package because the interest here was to have 2 robots. I have made a script for each simulation so that every command is automaticaly launched with a right delay to let the simulation be stable.

II. General 

	Those 2 simulations have a same idea: Simulate a human behaviour of mouvement on a map with a robot that try to follow him. To do that we use a Markov chain that define regions of interest (roi) and probabilised connexions between them. I made the choice to make a dynamic generation of the Markov chain because, if we have to change the map or simply modify the regions, it's much faster than to define each connexions ourselves manually. 
	The only thing we have to do here is to choose our map and define the regions in Rviz with InteractiveMarkers. Those markers will be saved and the code will automatically generate the Markov chain and all de probabilities. It will store it in the database MongoDB.

	a/ Construction of the simulation
		The first thing we have to keep in mind when we define the roi on Rviz is that the code needs to have the information of a connexion between two roi. In order to give him this info, we have to place at least one common point amoung the points of the two roi that we want to connect (We just have to superpose the best we can the point). 
		The second thing we have to keep in mind is that the code needs also some information to define the probabilities of each connexions between roi. In order to that, we have based the decision on the logic that says "In a building, a person is less likely to stay in very connected area like hallways than few connected area like offices". So the code generate probabilities to go to a region that depends directly on the number of connexions that have this region. Thus, it will be more likely to want to go to an office and to stay here for a moment (we defined 10sec the time to stay in the room but it's renewable). Nevertheless, it's very usual to go in hallways because of the high number of connexions.

	b/ Storage in the MondoDB
		The purpose of those simulations is to track the position of one robot and when we have the total trajectory, we can compare with the part that succeeded the robot to catch using a tracker. 
		In this simulation there is no tracker working yet because it works only in real environment. So we only store the total trajectory of one robot and the other one doesn't do nothing. We store the traj_msgs in MongoDB in message_store and it's possible to visualise them with the command : 'rosrun human_trajectory traj_visualisation.py all'

III. 2Robots_simu_soma.sh

	The first simulation is composed with 2 robots Scitos A5. We launch it with the script './2Robots_simu_soma.sh'. Those 2 robots are supposed to follow the Markov chain and be slightly aside. The big problem here is that in this simulation, I tried to use move_base for both of the 2 robots. It seems to have a problem with tf because I have to launch myself a necessary static_transform and Rviz is unable to find the whole urdf of the robot. Probably because of that, the 2 move_base node are not launched properly and the actionServer of move_base doesn't come up.

IV. morse_2Robots_simu.sh

	The second simulation is composed with 2 robots too. We launch it with the script './morse_2Robots_simu.sh. In this simulation, only one robot uses move_base so that there is no problem with the group name like previously or whatever. The other robot uses the waypoint movement available in Morse to move in the map. 

For any further technical informations, please refers to my internship report in multiple_robots_simu pkg