#!/usr/bin/env python

import math
import pymorse
import rospy
import random
import roslib
roslib.load_manifest('multiple_robots_simu')
import actionlib
import multiple_robots_simu.msg
from std_msgs.msg import Header
from geometry_msgs.msg import *
from soma_map_manager.srv import MapInfo
from soma_manager.srv import SOMAQueryROIs
from mongodb_store.message_store import MessageStoreProxy

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *

class Robot_human_control_morse(object):
    def __init__(self, simu):
        self.simu = simu
        # recuperation of the region of interest in the map in the database
        self.soma_service = rospy.ServiceProxy("/soma/map_info", MapInfo)
        self.soma_service.wait_for_service()
        self.soma_map = self.soma_service(1).map_name
        rospy.loginfo("Got soma map name %s..." % self.soma_map)
        # get region information from soma2
        self.soma_service = rospy.ServiceProxy("/soma/query_rois", SOMAQueryROIs)
        self.soma_service.wait_for_service()
        self.result = self.soma_service(query_type=0, roiconfigs=['1'], returnmostrecent=True)
        self._store_client = MessageStoreProxy(collection="markov_chain")

        # we count the number of regions on the map in the database
        self.regions = dict()
        self.nb_regions=self.count_regions(self.result.rois)
        print(self.nb_regions)

        # create an empty list to store the regions centers and points
        self.centre_data = [[0]*3]*self.nb_regions
        self.all_points = [[0]*10]*2*self.nb_regions
        self.all_points,self.centre_data=self.extract_points(self.result)
        #print_centre_data(self.centre_data) #Blocking 
        """
        print('-----------------------self.all_points---------------------')
        print(self.all_points)
        print('-----------------------self.centre_data---------------------')
        print(self.centre_data)
        """

        # loop for detection of common points between regions to make connexions and we count the connexions of every regions
        self.array_connexions = [[]*10]*self.nb_regions
        self.num_connexions= [[0]*2]*self.nb_regions
        self.array_connexions,self.num_connexions=self.calculate_connexions()

        """
        print('-----------------------array_connexion---------------------')
        print(self.array_connexions)
        print('-----------------------num_connexion---------------------')
        print(self.num_connexions)
        """
        #print(self.centre_data[choice][0])

        # We have to build the Markov chains and store it in the database
        self.markov = self.build_Markov_database()
        
        print("-----------------------markov chain ------------------------------------")
        print(self.markov)

        self._publish_online_markov()
        

    def simulation(self):
        
        # subscribes to updates from the Pose sensor by passing a callback
        #simu.robot2.pose.subscribe(print_pos)
        next_id='13'
        choice=self.search_index('13')
        self.simu.sleep(3)
           
        goalReached = False
        while not rospy.is_shutdown() : 
            print('-----------------------choice---------------------')
            print(next_id)
            try:
                # landmark change between Blender and RVIZ x_blender=y_rviz+3.8 y_blender=-xrviz-3.8
                # sends a destination by publish
                #self.simu.robot.waypoint.publish({'x': self.centre_data[choice][2]+3.2, 'y': -self.centre_data[choice][1]-3.2, 'z': 0.0,'tolerance': 0.5,'speed': 1.0})
                goalReached = self.moveToGoal(self.centre_data[choice][1],self.centre_data[choice][2])
                if (goalReached) : #and (self.simu.robot.waypoint.get_status() == "Arrived")
                    rospy.loginfo("Congratulations!")
                    next_id,useless=self.pick_new_region(self.array_connexions[choice])
                    choicePrevious=choice
                    choice=self.search_index(next_id)
                    if choicePrevious == choice:
                        rospy.loginfo("I want to stay here for a while ")
                        self.simu.sleep(10)
                        goalReached=True
                    else :
                        goalReached=False
                else:
                    rospy.loginfo("Hard Luck!")
                      
            except rospy.ROSInterruptException:
                rospy.loginfo("map_navigation node terminated.")


    def print_pos(self,pose):
        print("I'm currently at %s" % pose)

    def count_regions(self,roi):
        compt=0
        for region in roi:
            compt+=1
        return compt

    def already_connected(self,line_connexions,num):
        for i in range(0,len(line_connexions)):
            if line_connexions[i]==num:
                return True
        return False

    def pick_new_region_equiproba(self,line_connexions):
        pick=random.randrange(1,len(line_connexions))
        return line_connexions[pick]

    def pick_new_region(self,line_connexions):
        # we build an array with the ID and a coef proportionnal to the number of connexions of the region
        tab=[[]*2]*len(line_connexions)
        sumTotal=0
        for i in range(0,len(line_connexions)):
            temp=[]
            temp.append(line_connexions[i]) # we add the region ID 
            index=self.search_index(line_connexions[i]) # we search for the index in the array 
            temp.append(self.num_connexions[index][1])  # we add the coef proportional to the number of connexions corresponding
            sumTotal+=self.num_connexions[index][1]     # we make a sum to now the number of connexions of every connected roi
            tab[i]=temp

        tab.sort(key=lambda colonnes: colonnes[1])
        #print("--------------------------------numbers of connexions----------------------")
        #print(tab)

        add=0
        #we use the array to give the biggest importance (proba to stay) to the room with less connection
        #the logic is that there is less chance to stay in an area with a lot of connexions (like hallways...)
        #the regions with less connexions are more likely to be the destination the human is seeking 
        for i in range(0,len(line_connexions)):
            tab[i][1]= 1-tab[i][1]/sumTotal
            add+=tab[i][1]

        count=0
        for i in range(0,len(line_connexions)):
            tab[i][1]= 100*tab[i][1]/add

        import copy
        tab2 = copy.deepcopy(tab)
        #print("--------------------------------Probability corresponding---------------------")
        #print(tab)

        for i in range(0,len(line_connexions)):
            count+=tab[i][1]
            tab[i][1]= count
        tab.sort(key=lambda colonnes: colonnes[1])

        #print("-------------------------------- Cumulated Probability---------------------")
        #print(tab)

        pick=random.uniform(0,100)
        i=0
        test = pick > tab[i][1]
        while test and i+1 < len(line_connexions):
            i+=1
            test = pick > tab[i][1] 

        return tab[i][0], tab2

    def search_index(self,next_id):
        for i in range(0,len(self.array_connexions)):
            if self.array_connexions[i][0]==next_id :
                return i
        return -1

    # careful this fonction is blocking 
    def print_centre_data(self):
        point = rospy.Publisher('centre_zones', PoseArray, queue_size = 10)
        rospy.init_node('calcul_centre',anonymous = True)
        rate = rospy.Rate(10) # 10hz
        centre_ros = PoseArray()
        for i in range(len(self.centre_data)) :
            centre = Pose()
            centre.position.x = self.centre_data[i][1]
            centre.position.y = self.centre_data[i][2]
            centre_ros.poses.append(centre)
        centre_ros.header.frame_id = "map"
       
        while not rospy.is_shutdown():
            #   rospy.loginfo(centre_ros)
            point.publish(centre_ros)
            rate.sleep()

    def moy(self,pos,nb_pos):
        count=0
        for i in range(0,nb_pos):
            count+=pos[i]

        return count/nb_pos

    # fonction that extracts the position of the region stocked in the database
    def extract_points(self,result):
        compt=0
        for region in result.rois:
            if region.config == '1' and region.map_name == self.soma_map:
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
            self.all_points[compt*2]=temp1
            self.all_points[compt*2+1]=temp2

            #we also want an array for the centres of each region
            # we assume we have only rectangular polygons and calculate the center of the diagonal
            x_centre= self.moy(xs,len(xs))
            y_centre= self.moy(ys,len(ys))
            self.centre_data[compt]=[region.id,x_centre,y_centre]

            compt+=1

        return self.all_points, self.centre_data

    # Function that searches the common points between regions and define a connexion if there is one.
    def calculate_connexions(self):
        for i in range (0,self.nb_regions):
            # we asign the number of the region we deal with
            temp1 = []
            temp1.append(self.all_points[i*2][0])
            temp2=[]
            compt=0
            temp2.append(self.all_points[i*2][0])
            # we make a connexion between region if there is a common point between polygons
            for j in range(1,5):
                for k in range(0,self.nb_regions):
                    for l in range(1,5):
                        if self.all_points[2*i][0]!=self.all_points[2*k][0] and abs(self.all_points[2*i][j]-self.all_points[2*k][l])<0.2 and abs(self.all_points[2*i+1][j]-self.all_points[2*k+1][l])<0.2 :
                            # if common point so we make a connexion between regions
                            if self.already_connected(temp1,self.all_points[2*k][0])==False:
                                compt+=1
                                temp1.append(self.all_points[2*k][0])
            #print('------temp-----')
            #print(temp)
            temp2.append(compt)
            self.num_connexions[i]=temp2
            self.array_connexions[i]=temp1
        return self.array_connexions,self.num_connexions

    def toQuaternion(self,pitch, roll,yaw):
        q = Pose()
        t0 = math.cos(yaw * 0.5);
        t1 = math.sin(yaw * 0.5);
        t2 = math.cos(roll * 0.5);
        t3 = math.sin(roll * 0.5);
        t4 = math.cos(pitch * 0.5);
        t5 = math.sin(pitch * 0.5);

        q.orientation.w = t0 * t2 * t4 + t1 * t3 * t5;
        q.orientation.x = t0 * t3 * t4 - t1 * t2 * t5;
        q.orientation.y = t0 * t2 * t5 + t1 * t3 * t4;
        q.orientation.z = t1 * t2 * t4 - t0 * t3 * t5;
        return q;

    # Function that give the request to go to a goal position to the movebase module 
    def moveToGoal(self,xGoal,yGoal):
          #define a client for to send goal requests to the move_base server through a SimpleActionClient
          ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)

          #wait for the action server to come up
          while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
                  rospy.loginfo("Waiting for the move_base action server to come up")

          goal = MoveBaseGoal()

          #set up the frame parameters
          goal.target_pose.header.frame_id = "map"
          goal.target_pose.header.stamp = rospy.Time.now()

          # moving towards the goal

          goal.target_pose.pose.position =  Point(xGoal,yGoal,0)
          # we give the current orientation as target so that the orientation doesn't matter
          pose=self.simu.robot2.pose2.get()
          pose2 = Pose()
          pose2= self.toQuaternion(pose['pitch'],pose['roll'],pose['yaw'])
          #pose2.orientation = geometry_msgs.msg.Quaternion(*tf_conversions.transformations.quaternion_from_euler(pose['roll'],pose['pitch'],pose['yaw']))
          goal.target_pose.pose.orientation = pose2.orientation
          print(goal.target_pose.pose)

          rospy.loginfo("Sending goal location ...")
          ac.send_goal(goal)

          ac.wait_for_result(rospy.Duration(30))

          if(ac.get_state() ==  GoalStatus.SUCCEEDED):
                rospy.loginfo("You have reached the destination")
                return True

          else:
                rospy.loginfo("The robot failed to reach the destination")
                return False

    # Function that stores the markov chain of the current map in the database
    def build_Markov_database(self):
        from pymongo import MongoClient
        client = MongoClient('localhost',62345)
        db = client.markov_chain_db
        # WHEN MAP CHANGE, MODIFY THE COLLECTION NAME FOR MARKOV CHAIN HERE
        collection = db.roi_proba_connexions_cs_lg
        # we delete the data in case there is already a markov chain for this floor cs_lg of UoB CS lab, and rebuild it
        collection.remove({})

        markov_chain=[]

        #process to fill in the markov chain 
        for i in range(0,self.nb_regions):
            useless,tab_proba = self.pick_new_region(self.array_connexions[i])
            temp={"ID_region":self.array_connexions[i][0],"proba_connexions":tab_proba}
            collection.insert(temp)
            markov_chain.append(temp)
            #collection.update({'ID_region':self.array_connexions[i][0]},temp,upsert=True,multi=False)
        """
        # we can print the result
        import pprint
        for post in collection.find():
            pprint.pprint(post)
        """
        return markov_chain

     # construct MarkovChain message based on MarkovChain.msg
    def get_markov_chain_message(self):

        chain = multiple_robots_simu.msg.MarkovChain()
        chain.header = Header(1, rospy.Time.now(), '/map')
        chain.id = "cs_lg"
        
        for i in range(0,self.nb_regions):
            markov_proba = multiple_robots_simu.msg.MarkovArrayProba()
            markov_proba.id_region = self.markov[i]['ID_region']
            temp = self.markov[i]['proba_connexions']
            print(temp)

            for j in range(0,len(temp)):
                markov_proba.id_connected_roi.append(temp[j][0])
                markov_proba.proba_connected_roi.append(str(temp[j][1]))

            chain.markov_chain.append(markov_proba)

        return chain

     # publish based on online markov chain
    def _publish_online_markov(self):
        chain_msg = self.get_markov_chain_message()
        print(chain_msg)
        meta = dict()
        meta["map"] = "/map"
        meta["taken"] = "online"
        
        if chain_msg is not None:
            self._store_client.insert(chain_msg, meta)
            rospy.loginfo("Total Regions: %d", self.nb_regions)
        else :
            rospy.loginfo("Markov_msg is None")
        


if __name__ == '__main__':
    rospy.init_node('robot_human_control', anonymous=False)  #false because we don't want 2 nodes in the same time
    with pymorse.Morse() as simu:
        try:
            rospy.loginfo("Simulation ready ! Robots can begin to move")
            control = Robot_human_control_morse(simu)
            control.simulation()
            rospy.spin()

        except rospy.ROSInterruptException:
            rospy.loginfo("map_navigation node terminated.")
    

