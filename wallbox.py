# -*- coding: utf-8 -*-
#Thanks to Steven Devlan for the inital concept of this code. I extended the code to work with mp3s and others. 


import RPi.GPIO as GPIO
import time
import sys
import os
import httplib
import csv
import logging
from multiprocessing import Process, Queue




#contants and literals
SELECTION_LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H",
                     "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V")
WALLBOX = 13

#>>>these constants can be changed to fit the characteristics of your wallbox
MAXMIMUM_GAP = 0.8
MINIMUM_PULSE_GAP_WIDTH = 0.014
LETTER_NUMBER_GAP = 0.12


# set up IO port for input

GPIO.setmode(GPIO.BOARD)
GPIO.setup(WALLBOX, GPIO.IN)


# this function tests if a pulse or gap is wide enough to be registered
# this is needed for two reasons. 1) Sometimes the wallbox will generate an errant pulse
# which will cause errors if interpretted as a proper contact pulse 2) because of the
# way that I have tapped the wallbox pulses, there will be short gaps inside each pulse
# that need to be ignored

def state_has_changed(starting_state):
    starting_time = time.time()
    elapsed_time = 0

    for i in range(200):
        if not(GPIO.input(WALLBOX)) != starting_state:
            elapsed_time = time.time() - starting_time
            return False
    return True

# this function is called as soon as the main loop determines that a train of pulses
# has started.  It begins by counting the number pulses, then when it encounters a larger
# gap, it starts incrementing the letters.  If your wallbox uses the opposite order
# you will need to change this.  Also the final calculation of the track may need to be changed
# as some boxes have additional pulses at either the start or the end of the train
# once it encounters a gap over a pre-determined maxmimum we know that the rotator arm
# has stopped and we calculate the track


def calculate_track(logger):

    state = True
    count_of_number_pulses = 1  # since we are in the first pulse
    count_of_letter_pulses = 0
    length_of_last_gap = 0
    first_train = True
    time_of_last_gap = time.time()

    while length_of_last_gap < MAXMIMUM_GAP:
        if not(GPIO.input(WALLBOX)) != state:

            # state has changed but check it is not anomaly
            if state_has_changed(not state):
                logger.debug("State has changed")
                state = not state  # I use this rather than the GPIO value just in case GPIO has changed - unlikely but possible
                if state:  # indicates we're in a new pulse
                    length_of_last_gap = time.time() - time_of_last_gap
                    if(length_of_last_gap > MINIMUM_PULSE_GAP_WIDTH):
                        #logger.debug("Pulse.  Last gap: %.3f" %length_of_last_gap)

                        if length_of_last_gap > LETTER_NUMBER_GAP:  # indicates we're into the second train of pulses
                            first_train = False

                        if first_train:
                            count_of_letter_pulses += 1
                        else:
                            count_of_number_pulses += 1
                else:  # indicates we're in a new gap
                    time_of_last_gap = time.time()
        else:
            # update gap length and continue to poll
            length_of_last_gap = time.time() - time_of_last_gap

    track = SELECTION_LETTERS[
        count_of_letter_pulses - 1] + str((count_of_number_pulses - 1))
    logger.debug("+++ TRACK FOUND +++ Track Selection: %s ", track)
    return (SELECTION_LETTERS[count_of_letter_pulses - 1], str((count_of_number_pulses - 3)))


      
def wallboxMonitor(logger, lightBridge):
    command = False
    parentalMode = False
    logger.debug("In Wallbox monitor")


    possibles = globals().copy()
    possibles.update(locals())

    logger.debug("Pre loop wallbox")
    while True:
        time.sleep(0.00095)
        if(command):
            if(time_to_wait <= time.time()):
                logger.info("Command timeout")
                command = False
        if not (GPIO.input(WALLBOX)):
            if state_has_changed(True):
                trackLet, trackNum = calculate_track(logger)
                if(trackNum == '10'):
                            # 10 pulses is key 0
                    trackNum = '0'
                logger.info(" track %s , track num %s ", trackLet, trackNum)
                track = trackLet + trackNum
                if(track == 'A1'):
                    logger.info("A1 - command track")
                    time_to_wait = time.time() + 30
                    command = True
                # command track, next input will be a command. Timeout after 30
                # seconds
                 
                elif(track == 'R0'):
                    # Reboot
                    # Reboot time
                    logger.info(
                        "Reboot Time, rebooting computer")
                    try:
                        os.system("/sbin/reboot")
                    except Exception, err:
                        logger.error("couldn't reboot ")

                elif(command == True):
                        # thius is a command, not a song
                    logger.info("Command processed")
                    command = False
                else:
                    # play song from database.
                    logger.debug("song")
                    try:
                        # try play a song
                        try:
                            turnOnProc.terminate()
                        except:
                            logger.info(
                                "turnonproc failed to terminate, this is ok on first run")

                        with open('./database/JukeBoxSongs.csv') as csvfile:
                            reader = csv.DictReader(csvfile)
                            logger.debug("Opened csv file")
                            for row in reader:
                                if(row['Key-letter'] == trackLet):
                                    if(row['Key-number'] == trackNum):
                                        logger.info("Row %s, url %s", row[
                                                    'Track Name'], row['URL'])
                                            try:
                                              #play song 
                    except Exception, err:
                        logger.exception(
                            "Error playing song after getting track")


if __name__ == '__main__':

    # logger
    logger = logging.getLogger()

    wallboxMonitor(logger)
