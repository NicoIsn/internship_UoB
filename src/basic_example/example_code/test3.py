#! /usr/bin/env morseexec

import pymorse

def done(evt):
    print("We have reached our destination!")

with pymorse.Morse() as simu:

    # Start the motion. It may take several seconds before finishing
    # The line below is however non-blocking
    goto_action = simu.atrv.motion.goto(18, 18, 0)

    # Register a callback to know when the action is done
    goto_action.add_done_callback(done)

    print("Am I currently moving? %s" % goto_action.running())

    while goto_action.running():
        simu.sleep(0.5)