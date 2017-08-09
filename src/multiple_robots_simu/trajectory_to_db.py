#!/usr/bin/env python

"""
Modele From Ferdian JOVAN
class TrajectoryManager(object) dans human_trajectory
"""
import time
import tf
import rospy
import math
import pymongo
import rospy
from nav_msgs.msg import Path
from strands_navigation_msgs.msg import TopologicalMap
from mongodb_store.message_store import MessageStoreProxy
from std_msgs.msg import Header
from human_trajectory.trajectory import Trajectory
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion, PoseArray

class InlinePoseTrajectory(object):
    def __init__(self, traj_topic):
        self.name=rospy.get_name()
        self.traj = Trajectory(0)
        self.nb_traj = 0
        self.robot_pose = Pose()
        self.seq = 0
        self._tfl = tf.TransformListener()
        self.map_info = rospy.get_param("~map_info", "")
        self._vis = rospy.get_param("~path_visualisation", "true")
        #self._pub = rospy.Publisher(self.name+'/trajectory/complete', Trajectory, queue_size=10) # Trajectories seems to be a msg format but not Trajectory
        
        rospy.loginfo("Connecting to topological_map...")
        self._sub_topo = rospy.Subscriber("/topological_map", TopologicalMap, self.map_callback, None, 10)

        self._store_client = MessageStoreProxy(collection="people_trajectory")

        rospy.loginfo("Connecting to %s...", traj_topic )
        rospy.Subscriber(traj_topic, PoseStamped, self.pose_callback, None, 10)

        rospy.loginfo("Connecting to /robot_pose...")
        rospy.Subscriber("/robot_pose", Pose, self.robot_pose_callback, None, 10)

    # get robot position on the traj_topic (/pose by default)
    def pose_callback(self, pose):
        """
        # we have to get the right transform of the pose
        try:
            tpose = self._tfl.transformPose("/map", pose)
        except tf.Exception:
            rospy.logwarn("Transformation from %s to /map can not be done at the moment" % pose.header.frame_id)
        # It dosn't work so we have to make the changes ourselves
        """
        tpose=Pose()
        tpose.position.x = -pose.pose.position.y -4.2
        tpose.position.y = pose.pose.position.x -4
        tpose.position.z = pose.pose.position.z
        tpose.orientation = pose.pose.orientation

        #now we can save it
        self.seq += 1
        self.traj.append_pose(tpose, pose.header, self.robot_pose,True)

    # Fonction call when there is something new on /robot_pose topic (content appears in arg in rob_pose)
    def robot_pose_callback(self,rob_pose):
        self.robot_pose = rob_pose

    def publish_trajectory(self):
        while not rospy.is_shutdown():
            self.seq = 0
            self.nb_traj+=1
            self.traj = Trajectory(str(self.nb_traj))
            rospy.loginfo("Waiting to fill in the Trajectory...")
            time.sleep(30)

            self._publish_online_data()
            #collection.insert(self.traj)
            #self._pub.publish(traj)
            if self._vis:
                self._add_in_nav_msgs(self.traj.uuid)
                self._publish_in_nav_msgs()

    # publish based on online data from people_tracker
    def _publish_online_data(self):
        traj_msg = self.traj.get_trajectory_message(True)
        traj_msg = self._traj_size_checking(self.traj.get_trajectory_message())
        meta = dict()
        meta["map"] = self.map_info
        meta["taken"] = "online"
        if traj_msg is not None:
            self._store_client.insert(traj_msg, meta)
            rospy.loginfo("Total trajectories: %d", self.nb_traj)
        else :
            rospy.loginfo("traj_msg is None")

    # check how many poses the trajectory has.
    # too long trajectory will not be stored (size restriction from mongodb)
    def _traj_size_checking(self, traj):
        if len(traj.robot) > 100000:
            rospy.logwarn("Trajectory %s is too big in size. It will not be stored" % traj.uuid)
            return None
        else:
            return traj

    # add each traj to be published in nav_msg/Path
    def _add_in_nav_msgs(self, uuid):
            rospy.loginfo("Creating a publisher for %s...", uuid)
            name = uuid.replace("-", "0")
            self.pub_nav = rospy.Publisher(
                self.name + '/' + name, Path, latch=True, queue_size=10
            )

    # publish each traj in nav_msg/Path format
    def _publish_in_nav_msgs(self):
        """
        Contenu du msg de trajectoire:
        std_msgs/Header header
        string uuid                             # human id
        geometry_msgs/PoseStamped[] trajectory  # human trajectory
        geometry_msgs/Pose[] robot              # robot's trajectory
        time start_time                         # time for the first detected pose
        time end_time                           # time for the last detected pose
        float32 trajectory_length               # in meters
        bool complete                           # complete or incremental trajectory
        int32 sequence_id                       # sequence id if incremental trajectory is chosen
        float32 trajectory_displacement         # between first and last pose (in meters)
        float32 displacement_pose_ratio         # ratio of displacement to number of poses
        """
        nav_msg = self.traj.get_nav_message()
        self.pub_nav.publish(nav_msg)

    # get map info from topological navigation
    def map_callback(self, msg):
        self.map_info = msg.map
        self._sub_topo.unregister()

if __name__ == '__main__':
    rospy.init_node('total_trajectory')

    tp = InlinePoseTrajectory(rospy.get_param("~traj_topic", "/pose"))
    tp.publish_trajectory()

    rospy.spin()


