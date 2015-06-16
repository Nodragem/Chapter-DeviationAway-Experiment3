#
# Copyright (c) 1996-2005, SR Research Ltd., All Rights Reserved
#
#


#from pylink import *
import pylink
import gc

import pygame
from pygame import display
import numpy as np

import utils


TARGET_SIZE = utils.TARGET_SIZE
FIXATION_SIZE = utils.FIXATION_SIZE
GREEN = utils.GREEN
RED = utils.RED
DISTRACTOR_SIZE = utils.DISTRACTOR_SIZE
#DISTRACTOR_SIZE_X, DISTRACTOR_SIZE_Y  = utils.DISTRACTOR_SIZE_X, utils.DISTRACTOR_SIZE_Y
BACKGROUND = utils.BACKGROUND

## Everything will be passed by the main module
FPS_CONTROL = 0
FRAME_INTERVALS = []
MyEyelink = None
MyMonitor = None
MySurface = None
MyTable = None
MyInfo = None
dummy = False
stimulus2 = None
stimulus1 = None
fixation = None
text = None
fps = None
clock = pygame.time.Clock()


def initStimuliX(MyEnv):
    global stimulus2, stimulus1, fixation, text, fps
    stimulus2 = utils.CrossDiag(MyEnv,size=DISTRACTOR_SIZE, line_width = 2)
      ## diameter
    fixation = utils.Cross(MyEnv,size=FIXATION_SIZE) ## size of the container box
    text = utils.NormalText(MyEnv, "Debug Mode", pos=(0,0))
    fps = utils.NormalText(MyEnv, "fps", pos=(0,20))
    fixation.setFillColor(RED)
    stimulus1 = utils.CrossDiag(MyEnv,size=DISTRACTOR_SIZE, line_width = 2)
    stimulus1.color2 = (0,0,0, 0) ## display a black distractor (invisible on a black backgroung :P )
    stimulus2.setFillColor(RED)
    stimulus1.setFillColor(RED)

def initStimuliO(MyEnv):
    global stimulus2, stimulus1, fixation, text, fps
    stimulus2 = utils.Circle(MyEnv,size=TARGET_SIZE, line_width = 2) ## diameter
    fixation = utils.Cross(MyEnv,size=FIXATION_SIZE) ## size of the container box
    text = utils.NormalText (MyEnv, "Debug Mode", pos=(0,0))
    fps = utils.NormalText (MyEnv, "fps", pos=(0,20))
    fixation.setFillColor(RED)
    stimulus1 = utils.Circle(MyEnv,size=TARGET_SIZE, line_width = 2)
    stimulus1.color2 = (0,0,0, 0)
    stimulus2.setFillColor(RED)
    stimulus1.setFillColor(RED) ##

def end_trial():
    '''Ends recording: adds 100 msec of data to catch final events'''
    MySurface.fill((0,0,0))
    ## should clear the screen!!!!!!!!!!!
    pylink.endRealTimeMode();
    pylink.pumpDelay(100);
    MyEyelink.stopRecording();
    while MyEyelink.getkey() :
        pass;

def giveParametersToEyeTracker(par): ## not needed here but can be personnalized
    MyEyelink.sendMessage("!V TRIAL_VAR trial_num  %d" %par[0] )
    MyEyelink.sendMessage("!V TRIAL_VAR trial_type  %d" %par[1] )
    MyEyelink.sendMessage("!V TRIAL_VAR target_ecc  %d" %par[2] )
    MyEyelink.sendMessage("!V TRIAL_VAR target_dir  %d" %par[3] )
    MyEyelink.sendMessage("!V TRIAL_VAR distractor_dir  %d" %par[4] )
    MyEyelink.sendMessage("!V TRIAL_VAR distractor_dir  %d" %par[5] )
    MyEyelink.sendMessage("!V TRIAL_VAR distance  %d" %par[6] )

def updateStimuliFromParameters(par):
    ''' | ntrial | trial type | Target ecc. | Target dir. | Distractor ecc. | Distractor dir. | T-D Distance
    trial type: 0 for control (center vertical saccades),
                1 for single,
                2 for double, '''

    global stimulus1, stimulus2, text, fixation

    if (par[1] == 2):
        """ double condition """
        stimulus2.drawn = True
        #distractor.setFillColor(distractor.color1)
        stim1_pos = utils.polToCart(par[2], par[3])
        fixation_pos = np.array((0,0))
        stim2_pos = utils.polToCart(par[4], par[5])

        if stim1_pos[0] < 0:
            offset = -stim1_pos
        else: ## not very useful...
            offset = -stim1_pos
        offset[1] = 0
        print offset, stim1_pos

        fixation.setPosDegCart(fixation_pos+offset)
        stimulus2.setPosDegCart(stim2_pos+offset)
        stimulus1.setPosDegCart(stim1_pos+offset)

    elif (par[1] == 1):
        """single stimulus condition"""
        stimulus2.drawn = False
                #distractor.setFillColor(distractor.color1)
        stim1_pos = utils.polToCart(par[2], par[3])
        fixation_pos = np.array((0,0))
        stim2_pos = utils.polToCart(par[4], par[5])

        if stim1_pos[0] < 0:
            offset = -stim1_pos ## getByName("stim1")
        else:
            offset = -stim1_pos
        offset[1] = 0
        print offset, stim1_pos

        fixation.setPosDegCart(fixation_pos+offset)
        stimulus2.setPosDegCart(stim2_pos+offset)
        stimulus1.setPosDegCart(stim1_pos+offset)

    elif (par[1] == 0):
        """ control condition """
        stimulus2.drawn = False
        stimulus1.setPosDegCart((0, utils.polToCart(par[2], par[3])[1]))
        fixation.setPosDegCart((0, - utils.polToCart(par[2], par[3])[1]))


def sign(n):
    ''' take 0 or 1 as input, give -1 for 0 and 1 for 1'''
    return n*2-1

def drawCondition(FIX_duration, GAP_duration, S1_duration, S2_duration):
    S2_OFF = FIX_duration + GAP_duration + S1_duration + S2_duration ## could be replace with a cumsum of a line
    S1S2_OFFON = FIX_duration + GAP_duration + S1_duration
    S1_ON = FIX_duration + GAP_duration
    FIX_OFF = FIX_duration
    MyEyelink.flushKeybuttons(0)
    buttons =(0, 0);
    # Loop of realtime
    for frameN in xrange(S2_OFF):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                    k = pygame.key.get_pressed()
                    m = pygame.key.get_mods()
                    if m & pygame.KMOD_CTRL and k[pygame.K_q]:
                        end_trial();
                        print "Crtl + Q pressed: quit the program"
                        return pylink.ABORT_EXPT;
                    elif m & pygame.KMOD_CTRL and k[pygame.K_r]:
                        end_trial();
                        print "Crtl + R pressed: repeat trial"
                        return pylink.REPEAT_TRIAL
        MySurface.fill(BACKGROUND)
        # check input (should be in a function)
        if dummy:
            MyEyelink.update()

        error = MyEyelink.isRecording()  # First check if recording is aborted
        if error!=0:
            end_trial();
            return error

        # here you draw
        if frameN == 1:
            startTime = pylink.currentTime()
            fixation.draw()
            MyEyelink.sendMessage("STIMULUS Fixation ON %.3f %.3f SYNCTIME %d"%(fixation.getPolarPos(0), fixation.getPolarPos(1), pylink.currentTime()-startTime));
            while (pygame.event.wait().type != pygame.KEYDOWN): pass
            MyEyelink.sendMessage("STIMULUS Fixation PRESSED %.3f %.3f SYNCTIME %d"%(fixation.getPolarPos(0), fixation.getPolarPos(1), pylink.currentTime()-startTime));
        elif frameN < FIX_OFF:
            fixation.draw()
        elif frameN == FIX_OFF:
            MyEyelink.sendMessage("STIMULUS Fixation OFF %.3f %.3f SYNCTIME %d"%(fixation.getPolarPos(0), fixation.getPolarPos(1), pylink.currentTime()-startTime));
        elif frameN == S1_ON:
            startTime = pylink.currentTime()
            stimulus1.draw()
            MyEyelink.sendMessage("STIMULUS S1 ON %.3f %.3f SYNCTIME %d"%(stimulus1.getPolarPos(0), stimulus1.getPolarPos(1), pylink.currentTime()-startTime));
        elif frameN > S1_ON and frameN < S1S2_OFFON:
            stimulus1.draw()
        elif frameN == S1S2_OFFON:
            startTime = pylink.currentTime()
            stimulus2.draw()
            MyEyelink.sendMessage("STIMULUS S1 OFF %.3f %.3f SYNCTIME %d"%(stimulus1.getPolarPos(0), stimulus1.getPolarPos(1), pylink.currentTime()-startTime));
            MyEyelink.sendMessage("STIMULUS S2 ON %.3f %.3f SYNCTIME %d"%(stimulus2.getPolarPos(0), stimulus2.getPolarPos(1), pylink.currentTime()-startTime));
        elif frameN > S1S2_OFFON and frameN < (S2_OFF-1):
            stimulus2.draw()
        elif frameN == (S2_OFF-1):
            MyEyelink.sendMessage("STIMULUS S2 OFF %.3f %.3f SYNCTIME %d"%(stimulus2.getPolarPos(0), stimulus2.getPolarPos(1), pylink.currentTime()-startTime));
        if dummy:
            text.draw()
            utils.drawFPS(fps, clock)
        display.flip()
        FRAME_INTERVALS.append(clock.tick_busy_loop(FPS_CONTROL))

    end_trial();

    #The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer.
    #This is different than the end of recording message END that is logged when the trial recording ends.
    #Data viewer will not parse any messages, events, or samples that exist in the data file after this message.
    MyEyelink.sendMessage("TRIAL_RESULT %d"%(buttons[0]));
    return MyEyelink.getRecordingStatus()




def do_trial(par):
    '''Does the simple trial'''
    id_number = str(par[0])+" TRIAL_TYPE "+str(par[1])+" CODE_TYPE "+str(par[-1]) ## par contains the trial parameters
    ##This supplies the title at the bottom of the eyetracker display
#       message ="record_status_message 'Trial %s'"%id_number
#       MyEyelink.sendCommand(message);

    ##Always send a TRIALID message before starting to record.
    ##EyeLink Data Viewer defines the start of a trial by the TRIALID message.
    ##This message is different than the start of recording message START that is logged when the trial recording begins.
    ##The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.

    msg = "TRIALID %s"%id_number;
    MyEyelink.sendMessage(msg);

    ##This TRIAL_VAR command specifies a trial variable and value for the given trial.
    ##Send one message for each pair of trial condition variable and its corresponding value.
    ## You can put this in a function
    updateStimuliFromParameters(par)
    #giveParametersToEyeTracker(par)

    ## you can do a drifcorrection if you want
    ## fonction()

    error = MyEyelink.startRecording(1,1,1,1)
    if error:       return error;
    gc.disable(); # switch off the garbage collector
    #begin the realtime mode
    pylink.beginRealTimeMode(100)

    if not MyEyelink.waitForBlockStart(100, 1, 0):
        end_trial();
        print "ERROR: No link samples received!";
        return pylink.TRIAL_ERROR;


    ## we inserted the gap duration information at par[-4] and the type_code at par[-1]
    ## the fixation duration if now at par[-5]
    ## the gap duration is used by drawCondition
    ## (change from previous program: par[-3:] to par[-5:-1])
    ret_value = drawCondition(*par[-5:-1].astype(int));
    pylink.endRealTimeMode();
    gc.enable();
    return ret_value;





def run_trials(MyEnv, start, break_interval):
    ''' This function is used to run individual trials and handles the trial return values. '''

    ''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles
    the case of re-running a trial. '''
    global MySurface, MyMonitor, MyEyelink, MyTable, MyInfo, FPS_CONTROL
    MySurface, MyMonitor, MyEyelink, MyTable, MyInfo = MyEnv.getDetails()
    # Give the screen reference to Stimuli, and initialize them:
    FPS_CONTROL = MyMonitor.fps_control
    # Give the screen reference to Stimuli, and initialize them:
    initStimuliO(MyEnv)
    utils.displayInstruction(MyEnv, "instructions-same.txt")

    #Do the tracker setup at the beginning of the experiment.
    if MyEyelink.getTrackerVersion() == -1:
        global dummy
        dummy = True
        utils.displayTestScreen(MyEnv, 13., 16) # display test screen in dummy mode;
    nb_trials = len(MyTable[start:,0])

    for i, trial in enumerate(MyTable[start:,:]): ## read the parameter's table line-by-line from the start number

        if(MyEyelink.isConnected() ==0 or MyEyelink.breakPressed()): break;

        if i % break_interval == 0 and i>0:
            s = "Part %d on %d achieved !"%(i / break_interval, nb_trials/break_interval )
            event = utils.displayInstruction(MyEnv, "waiting_message.txt", additional_text = s)
            if event.key == pygame.K_r:
                event = utils.runCalibration(MyEnv)
            if event.key == pygame.K_ESCAPE:
                MyEyelink.sendMessage("EXPERIMENT ABORTED")
                return pylink.ABORT_EXPT, FRAME_INTERVALS;

        while 1:
            ret_value = do_trial(trial)
            pylink.endRealTimeMode()

            if (ret_value == pylink.TRIAL_OK):
                MyEyelink.sendMessage("TRIAL OK");
                break;
            elif (ret_value == pylink.SKIP_TRIAL):
                MyEyelink.sendMessage("TRIAL %s SKIPPED"%str(i));
                print "TRIAL %s SKIPPED"%str(i)
                break;
            elif (ret_value == pylink.ABORT_EXPT):
                MyEyelink.sendMessage("EXP. ABORTED AT TRIAL %s"%str(i));
                print "EXP. ABORTED AT TRIAL %s"%str(i)
                return pylink.ABORT_EXPT, FRAME_INTERVALS;
            elif (ret_value == pylink.REPEAT_TRIAL):
                utils.runCalibration(MyEnv)
                MyEyelink.sendMessage("TRIAL REPEATED after Calibration");
            else:
                MyEyelink.sendMessage("TRIAL ERROR")
                break;

    return 0, FRAME_INTERVALS;

