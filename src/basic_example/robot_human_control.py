#!/usr/bin/env python

import pymorse
import rospy
import random
import roslib
roslib.load_manifest('basic_example')
import actionlib
from geometry_msgs.msg import *
from soma_map_manager.srv import MapInfo
from soma_manager.srv import SOMAQueryROIs

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *

def print_pos(pose):
    print("I'm currently at %s" % pose)

def count_regions(roi):
    compt=0
    for region in roi:
        compt+=1
    return compt

def already_connected(line_connexions,num):
    for i in range(0,len(line_connexions)):
        if line_connexions[i]==num:
            return True
    return False

def count_connexions(array_connexions,num_regions):
    num_connexions= [[0]*2]*num_regions
    nb=0
    #for i in range(0,num_regions):
        #if array_connexions[]

def pick_new_region(line_connexions):
    pick=random.randrange(1,len(line_connexions))
    return line_connexions[pick]

def search_index(array_connexions,next_id):
    for i in range(0,len(array_connexions)):
        if array_connexions[i][0]==next_id :
            return i
    return -1

def print_centre_data(centre_data):
    point = rospy.Publisher('centre_zones', PoseArray, queue_size = 10)
    rospy.init_node('calcul_centre',anonymous = True)
    rate = rospy.Rate(10) # 10hz
    centre_ros = PoseArray()
    for i in range(len(centre_data)) :
        centre = Pose()
        centre.position.x = centre_data[i][1]
        centre.position.y = centre_data[i][2]
        centre_ros.poses.append(centre)
    centre_ros.header.frame_id = "map"
   
    while not rospy.is_shutdown():
        #   rospy.loginfo(centre_ros)
        point.publish(centre_ros)
        rate.sleep()

def extract_points(result):
    compt=0
    for region in result.rois:
        if region.config == '1' and region.map_name == soma_map:
            xs = [pose.position.x for pose in region.posearray.poses]
            ys = [pose.position.y for pose in region.posearray.poses]

        #we have to build an array to store the points and ID of each regions
        temp1 = [0]*(len(xs)+1)
        temp2 = [0]*(len(xs)+1)
        temp1[0]=region.id
        temp2[0]=region.id
        for i in range(0,len(xs)):
            temp1[i+1]=xs[i]
            temp2[i+1]=ys[i]
        all_points[compt*2]=temp1
        all_points[compt*2+1]=temp2

        #we want also an array for the centres of each region
        # we assume we have only rectangular polygons and calculate the center of the diagonal
        x_centre=(xs[1]+xs[3])/2
        y_centre=(ys[1]+ys[3])/2
        centre_data[compt]=[region.id,x_centre,y_centre]

        compt+=1

    return all_points, centre_data

def calculate_connexions(all_points,nb_regions):
    for i in range (0,nb_regions):
        # we asign the number of the region we deal with
        temp1 = []
        temp1.append(all_points[i*2][0])
        temp2=[]
        compt=0
        temp2.append(all_points[i*2][0])
        # we make a connexion between region if there is a common point between polygons
        for j in range(1,5):
            for k in range(0,nb_regions):
                for l in range(1,5):
                    if all_points[2*i][0]!=all_points[2*k][0] and abs(all_points[2*i][j]-all_points[2*k][l])<0.2 and abs(all_points[2*i+1][j]-all_points[2*k+1][l])<0.2 :
                        # if common point so we make a connexion between regions
                        if already_connected(temp1,all_points[2*k][0])==False:
                            compt+=1
                            temp1.append(all_points[2*k][0])
        #print('------temp-----')
        #print(temp)
        temp2.append(compt)
        num_connexions[i]=temp2
        array_connexions[i]=temp1
    return array_connexions,num_connexions

def moveToGoal(xGoal,yGoal):

      #define a client for to send goal requests to the move_base server through a SimpleActionClient
      ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)

      #wait for the action server to come up
      while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
              rospy.loginfo("Waiting for the move_base action server to come up")


      goal = MoveBaseGoal()

      #set up the frame parameters
      goal.target_pose.header.frame_id = "map"
      goal.target_pose.header.stamp = rospy.Time.now()

      # moving towards the goal*/

      goal.target_pose.pose.position =  Point(xGoal,yGoal,0)
      goal.target_pose.pose.orientation.x = 0.0
      goal.target_pose.pose.orientation.y = 0.0
      goal.target_pose.pose.orientation.z = 0.0
      goal.target_pose.pose.orientation.w = 1.0

      rospy.loginfo("Sending goal location ...")
      ac.send_goal(goal)

      ac.wait_for_result(rospy.Duration(60))

      if(ac.get_state() ==  GoalStatus.SUCCEEDED):
              rospy.loginfo("You have reached the destination")
              return True

      else:
              rospy.loginfo("The robot failed to reach the destination")
              return False

#---------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------Beginning of the script--------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------#


# recuperation of the region of interest in the map in the database
soma_service = rospy.ServiceProxy("/soma/map_info", MapInfo)
soma_service.wait_for_service()
soma_map = soma_service(1).map_name
rospy.loginfo("Got soma map name %s..." % soma_map)
# get region information from soma2
soma_service = rospy.ServiceProxy("/soma/query_rois", SOMAQueryROIs)
soma_service.wait_for_service()
result = soma_service(
    query_type=0, roiconfigs=['1'], returnmostrecent=True
)

# we count the number of regions on the map in the database
regions = dict()
nb_regions=count_regions(result.rois)
print(nb_regions)

# create an empty list to store the regions centers and points
centre_data = [[0]*3]*nb_regions
all_points = [[0]*10]*2*nb_regions
all_points,centre_data=extract_points(result)

"""
#il ya trop de cases dans le tableau il faut compter les regions et en mettre autant dans le tableau
print('-----------------------all_points---------------------')
print(all_points)
print('-----------------------centre_data---------------------')
print(centre_data)
"""

# loop for detection of common points between regions to make connexions and we count the connexions of every regions
array_connexions = [[]*10]*nb_regions
num_connexions= [[0]*2]*nb_regions
array_connexions,num_connexions=calculate_connexions(all_points,nb_regions)


print('-----------------------array_connexion---------------------')
print(array_connexions)
print('-----------------------num_connexion---------------------')
print(num_connexions)


#print(centre_data[choice][0])
# We assume that there is equi-probability for a region to go to each region connected
# so the probability is 1/num_connexions for each
# We want know to pick a region randomly and make the robot go there
# when he's arrived he picks randomly in the connected regions 


with pymorse.Morse() as simu:
    # subscribes to updates from the Pose sensor by passing a callback
    #simu.robot2.pose.subscribe(print_pos)
    next_id='1'
    choice=search_index(array_connexions,'13')
    simu.sleep(3)
    """
    #avec le publish de morse
    while True : 
        print('-----------------------choice---------------------')
        print(choice)
        
        # landmark change between Blender and RVIZ x_blender=y_rviz+3.8 y_blender=-xrviz-3.8
        print(centre_data[choice][2]+3.8)
        print(-centre_data[choice][1]-3.8)
        # sends a destination by publish
        simu.robot2.waypoint.publish({'x': centre_data[choice][2]+3.8, 'y': -centre_data[choice][1]-3.8, 'z': 0.0,'tolerance': 0.5,'speed': 1.0})
        while simu.robot2.waypoint.get_status() != "Arrived":
            simu.sleep(0.5)
        print("Here we are!")
        next_id=pick_new_region(array_connexions[choice])
        choice=search_index(array_connexions,next_id)
    """
    
    
    rospy.init_node('map_navigation', anonymous=False)
    goalReached = False
    while True : 
        print('-----------------------choice---------------------')
        print(next_id)
        
        # landmark change between Blender and RVIZ x_blender=y_rviz+3.8 y_blender=-xrviz-3.8
        print(centre_data[choice][1])
        print(centre_data[choice][2])

        try:
            goalReached = moveToGoal(centre_data[choice][1],centre_data[choice][2])
            if (goalReached):
                rospy.loginfo("Congratulations!")
                next_id=pick_new_region(array_connexions[choice])
                choice=search_index(array_connexions,next_id)
                goalReached=False
            else:
                rospy.loginfo("Hard Luck!")
                

        except rospy.ROSInterruptException:
            rospy.loginfo("map_navigation node terminated.")


