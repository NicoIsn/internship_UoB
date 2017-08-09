#! /usr/bin/env morseexec

import pymorse

with pymorse.Morse("localhost", 4000) as simu:

    try:
        print(simu.robots)
        simu.quit()

    except pymorse.MorseServerError as mse:
        print('Oups! An error occured!')
        print(mse)