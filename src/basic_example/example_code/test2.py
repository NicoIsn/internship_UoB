import pymorse

def print_pos(pose):
    print("I'm currently at %s" % pose)

with pymorse.Morse() as simu:

    # subscribes to updates from the Pose sensor by passing a callback
    simu.atrv.pose.subscribe(print_pos)

    # sends a destination
    simu.atrv.waypoint.publish({'x' : 10.0, 'y': 5.0, 'z': 0.0,'tolerance' : 0.5,'speed' : 1.0})

    # Leave a couple of millisec to the simulator to start the action
    simu.sleep(0.1)

    # waits until we reach the target
    while simu.atrv.waypoint.get_status() != "Arrived":
        simu.sleep(0.5)

    print("Here we are!")
