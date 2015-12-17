import numpy as np
import sys
import pylink
from pygame import font
import pygame
import os, re, linecache
import matplotlib.pyplot as plt
from math import tan, radians

## Time and duration are in frames (100 frames == 1 seconds)
## Position are in polar coordinate, in degrees
ECCENTRICITY = 13.5
STIMULUS1_SINGLEDURATION = 35
STIMULUS2_DURATION = 35
BACKGROUND =(0,0,0,255)
TARGET_SIZE = 0.4
FIXATION_SIZE = 0.2
GREEN = (0,190,0, 255)
RED = (254, 0,0, 255)
DISTRACTOR_SIZE = 0.283 #0.4 Target_size *sin 45
## Random Variables and leveled Variables
FIXATION_DURATION = (80, 30) ## 800 +- 300 ms
FIXATION_DURATION_LEVELS = [FIXATION_DURATION]
GAP_DURATION_SHORT = (10, 10) ## changed from 200 +- 100 ms to 100 +- 100 ms
GAP_DURATION_LONG = (40, 10) ## changed from 500 +- 100 ms to 400 +- 100 ms
GAP_LEVELS = [GAP_DURATION_SHORT, GAP_DURATION_LONG]
STIMULUS1_DOUBLEDURATION_SHORT = (35, 10) ## changed from 350 +- 100 ms to 250 += 100 ms? NO
STIMULUS1_DOUBLEDURATION_LONG = (65, 10) ## changed from 650 +- 100 ms to 550 += 100 ms? NO
S1_LEVELS = [STIMULUS1_DOUBLEDURATION_SHORT, STIMULUS1_DOUBLEDURATION_LONG]
POSITION_CONTROL_LEVELS = [-30, 30]
POSITION_EXP_LEVELS = [-30, 30, 150, -150]
## the first list give us which columns will be filled, the second list gives how this columns should be filled (levels).
CONTROL_LEVELS = [[3, -5, -4], [POSITION_CONTROL_LEVELS, FIXATION_DURATION_LEVELS, GAP_LEVELS]]
SINGLE_LEVELS = [[3, -5, -4], [ POSITION_EXP_LEVELS, FIXATION_DURATION_LEVELS, GAP_LEVELS]]
DOUBLE_LEVELS = [[3, -5, -4, -3],[ POSITION_EXP_LEVELS, FIXATION_DURATION_LEVELS, GAP_LEVELS, S1_LEVELS]]

# example of type_code (TRIAL_CODE) = 1213 :
# -- Position level = 3 => 150
# -- Fixation duration level = 1 => (80,30)
# -- Gap duration level = 2 => (40,10)
# -- S1 duration level = 1 => (65,10)

#DISTRACTOR_SIZE_Y = 0.3627
#DISTRACTOR_SIZE_X= 0.41888

##BACKGROUND = (211,211,211,255)#
##TARGET_SIZE = 2.5 ## is good for calibration
##GREEN = (0, 255,0,255)##
##GREEN = RED ##

'''
Timing of the Stimuli appearance:
-----------------------------------
Fixation btw 500ms and 1100ms
= 36 frames and 79.2 frames at 72 Hz
Target + Distractor appearance 250ms
= 18 frames at 72 Hz
Target alone for 500ms in addition
= 36 frames at 72 Hz
'''

def createTableOfTrials(nb_trials, control_prop, block, subjectID, path):
    '''
    ##___________________________________________________________________________________________________________________________________________________________________
    ## --- TABLE description ---
    ## ------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ## -- > first row, which will be the header of the file:
    ## | distractor type | frequency of the distractor | block | subject ID
    ## -- > from the second row:
    ## | ntrial | trial type | Stim 1 ecc. | Stim 1 dir. | Stim 2 ecc. | Stim 2 dir. | T-D Distance | fixation_duration | gap duration | first stim_duration | second stim_duration | type code
    ##
    ##___________________________________________________________________________________________________________________________________________________________________
    ## --- Variable description:
    ##--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ## -- distractor type:
            "same" or "different" from the target
    ## -- frequency of the distractor:
            for instance, D20T80 for 20% of trials with distractor
    ## -- block:
            there is 5 block per condition, per subject
    ## -- subject ID:
            name or a number identifying the subject
    ##---------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ## -- ntrial:
            0,1,2,3,4,5 ...
    ## -- trial type:
            0 for control, 1 for single, 2 for double.
    ## -- Target eccentricity, Target direction:
            In single and double, the target can appear at 32 positions (8 per quadrant )
                - right top quadrant:   5.625,   11.25 ,   16.875,   22.5,   28.125,  33.75,   39.375,   45.
                - left top quadrant:  174.375,  168.75 ,  163.125,  157.5,  151.875, 146.25,  140.625,  135.
            ** NOTE: multiply by -1 for the bottom quadrants.
    ## -- Distractor eccentricity, Distractor direction:
            In double condition, the distractor is always on the other side of the target (-1)
            Note that in double condition, distractors and targets have the same eccentricity
    ## -- Target Distractor distance:
            In double condition, the distance is 2*target_eccentricity * tan(target_direction)
            ** NOTE: the 3 last distractor related variables are put at -1 if single condition
    ## -- fixation_duration, stimuli_duration, remaining_duration:
            They are use for the stimuli timing, there are given in frames.
    '''
    control_proportion = int(control_prop)
    info = ["Gap|No-Gap|ShortS1|LongS1 Mixted",
                            "DoubleStep %d0 %%"%control_proportion,
                            block, subjectID]

    ## WARNING YOU CAN'T HAVE MORE THAN 9 LEVELS for a condition (the type code is done with the decimal system)

    header = makeHeader(info)
    total_trials = nb_trials
    ## let do the count of trial per trial type:
    amount_of_test = int(control_proportion/20.0 * total_trials) ## distractor_freq = 2 or 8
    amount_of_control = (total_trials - amount_of_test*2)
    printStatisticProportion(1, total_trials, amount_of_test)

    #| ntrial | trial type | Stim 1 ecc. | Stim 1 dir. | Stim 2 ecc. | Stim 2 dir. | T-D Distance | fixation_duration | gap duration | first stim_duration | second stim_duration | type_code
    ## we create a table of "amount_of_control" rows, each row having the same content: (0, 0, eccentricity, 0 , -1, -1, -1):
    control_trials = np.tile((0, 0, ECCENTRICITY, 0 , -1, -1, -1, 0, 0, STIMULUS1_SINGLEDURATION, 0, 0), (amount_of_control, 1))
    control_trials = fillLevels(1, control_trials, CONTROL_LEVELS)

    single_trials = np.tile((0, 1, ECCENTRICITY, 0 , -1, -1, -1, 0, 0, STIMULUS1_SINGLEDURATION, 0, 0), (amount_of_test, 1))
    single_trials = fillLevels(1, single_trials, SINGLE_LEVELS)

    double_trials = np.tile((0, 2, ECCENTRICITY, 0 , ECCENTRICITY, 0, 0, 0, 0, 0, STIMULUS2_DURATION, 0), (amount_of_test, 1)) ## we don't use the column distance!
    double_trials = fillLevels(1, double_trials, DOUBLE_LEVELS)
    double_trials[:,5] = - double_trials[:,3] ## S2 is the vertical reflection of S1
    double_trials[:,6] = 2*ECCENTRICITY * np.tan(double_trials[:,3]) ## half of the distance (assumed that S1 and S2 are symetric)

    np.random.shuffle(control_trials)
    table = np.concatenate((single_trials, double_trials), axis = 0)
    np.random.shuffle(table)
    table = np.concatenate((control_trials, table), axis = 0)
    table[:,0] = np.arange(total_trials)+1

    np.savetxt(path, table, delimiter = "\t", header = header)
    print_stat(table)

    return info, table

def fillLevels(current_subdivision, table, levels_descr):
    ## WARNING: the last columns will be use to write the type code.
    nb_rows = table.shape[0]
    total_subdivision = current_subdivision
    for level in levels_descr[1]:
        total_subdivision *= len(level)

    if nb_rows % total_subdivision != 0:
        print "The number of rows has to be a multiple of the total number of subdivision:"
        print "Subdivisions par levels:", "*".join([str(len(l)) for l in levels_descr[1]]), "=", total_subdivision
        print "Number of row of the provided table:", nb_rows
        print "The table won't be created and the program will quit!"; sys.exit(0)

    condition = 0
    for index, LEVEL in zip(levels_descr[0], levels_descr[1]):
        nb_factor = len(LEVEL)
        repeat_factor = nb_rows/current_subdivision/nb_factor # we have two sublevel: short Gap and long Gap
        if isinstance(LEVEL[0], list) or isinstance(LEVEL[0], tuple):
            buffer = []
            for parameter_set in LEVEL:
                buffer.append(np.random.uniform(parameter_set[0]-parameter_set[1], parameter_set[0]+parameter_set[1], repeat_factor))
            buffer = np.concatenate(buffer, axis=1)
            ## the fourth last line would be simply np.repeat(LEVEL) if they were not random.
        else: ## cross the finger to be a number (float, int, etc...)
            buffer = np.repeat(LEVEL, repeat_factor)
        print condition
        type_code = np.repeat(np.arange(len(LEVEL))+1, repeat_factor)*(10**condition) ## that's kind of dirty to use the decimal system for coding the trial type.
        buffer = np.tile(buffer, current_subdivision)
        type_code = np.tile(type_code, current_subdivision)
        table[:, index] = buffer ## the 9th columns (fixation gap) is
        table[:, -1] += type_code
        current_subdivision *= nb_factor
        condition += 1
    return table

def printStatisticProportion(n_pos, total_trials, amount_of_test):
    print "Total Trials: ", total_trials
    print "Total of Double Stim. Test:", amount_of_test
    print "   |---> trials per configuration:", amount_of_test/n_pos
    print "Total of Single Stim. Test:", amount_of_test
    amount_of_control = (total_trials - amount_of_test*2)
    print "Total of Vertical Controls:", amount_of_control
    if amount_of_test % n_pos != 0:
        print "Error: Can't test homogeneously ", n_pos, "configurations with", amount_of_test, "test trials"

def plot_trial_type(i, table):
    cond = i
    select = (table[:,1] == cond) & ((table[:,3] < 90) & (table[:,3] > -90))
    T_x, T_y = polToCart(table[select,2], table[select,3])
    D_x, D_y = polToCart(table[select,4]+1, table[select,5])
    plt.scatter(T_x, T_y, color="blue")
    plt.scatter(D_x, D_y, color="cyan")
    select = (table[:,1] == cond) & ((table[:,3] > 90) | (table[:,3] < -90))
    T_x, T_y = polToCart(table[select,2], table[select,3])
    D_x, D_y = polToCart(table[select,4]+1.5, table[select,5])
    plt.scatter(T_x, T_y, color="red")
    plt.scatter(D_x, D_y, color="magenta")
    plt.show()

def print_stat(table):
    print "\n -------------- \n MAIN STATISTIC: "
    y = np.bincount(table[:,1].astype(int))
    ii = np.nonzero(y)[0]
    ii =  np.array(zip(ii,y[ii]))
    print "trial_types: ", ii[:,0]
    print "frequency: ", ii[:,1]/float(table.shape[0])
    print "mean of timing based on 100 Hz: "
    print "fixation duration: %.3f"% (np.mean(table[:,-5])/100)
    print "gap duration: %.3f"% (np.mean(table[:,-4])/100)
    print "stim1 duration during double cond.: %.3f"% (np.mean(table[table[:,1] == 2,-3])/100)
    print "stim2 duration during double cond.: %.3f"% (np.mean(table[table[:,1] == 2,-2])/100)
    print "\n"

def cartToPol(x, y):
    r = np.sqrt(x**2 + y**2)
    theta = np.degrees(np.arctan2(y,x))
    return np.array((r, theta))

def polToCart(r, theta):
    x = r*np.cos(np.radians(theta))
    y = r*np.sin(np.radians(theta))
    return np.array((x, y))

def doRandomDotsTable(d_min, d_max, tol, number, r_min, r_max, res):
    ''' if distance min == -1, the function return just random target dots, without distractor'''
    distance_min = d_min
    distance_max = d_max
    tolerance = tol
    n = int(number)
    ecc_min = r_min
    ecc_max = r_max
    resolution = res

    R, D = np.meshgrid(np.linspace(ecc_min, ecc_max, 46), np.linspace(-90, 90, 91) )
    circle_comb = np.vstack( (R.flatten(), D.flatten()) )

    if distance_min == -1:
        r_index = np.random.randint(0, circle_comb.shape[1], number)
        return circle_comb[:, r_index]

    T_x = [];T_y = [];D_x = [];D_y = [];
    r_distance = np.random.uniform(distance_min,distance_max,n)
    distances = []
    print "start..."
    for i in xrange(n):
        dist_constraint = r_distance[i]
        dist_DT = -tolerance
        while not ((dist_DT > dist_constraint - tolerance) & (dist_DT < dist_constraint + tolerance)):
            r_index =  np.random.randint(0, circle_comb.shape[1], 1)
            t_r, t_d, = circle_comb[:, r_index]
            t_x, t_y = polToCart(t_r, t_d)
            r_index =  np.random.randint(0, circle_comb.shape[1], 1)
            d_r, d_d = circle_comb[:, r_index]
            d_x, d_y = polToCart(d_r, d_d)
            dist_DT = np.sqrt( (d_x-t_x)**2 + (d_y-t_y)**2 )
        T_x.append(t_x[0])
        T_y.append(t_y[0])
        D_x.append(d_x[0])
        D_y.append(d_y[0])
        distances.append(dist_DT)
    print "end"

    T_x,T_y,D_x, D_y = np.array(T_x).flatten(), np.array(T_y).flatten(), np.array(D_x).flatten(), np.array(D_y).flatten()
    distances = np.array(distances).flatten()
    #plot_figures(T_x, T_y, D_x, D_y, distances, 2*ecc_max, ecc_max, 5)
## half of them are on the right side:
    #print T_x.shape[0], len(T_x)
    T_x[len(T_x)/2:-1] = -T_x[len(T_x)/2:-1]
    D_x[len(D_x)/2:-1] = -D_x[len(D_x)/2:-1]
    #plot_figures(T_x, T_y, D_x, D_y, distances, 2*ecc_max, ecc_max, 5)
    #plt.show()
    T_r, T_theta = cartToPol(T_x, T_y)
    D_r, D_theta = cartToPol(D_x, D_y)

    distances = np.array(distances).flatten()
    return (np.vstack((T_r,T_theta, D_r,D_theta,distances)))


def plot_figures(T_x, T_y, D_x, D_y, distances, h, w, bin_size):
    plt.figure()
    plt.subplot(211)
    plt.scatter(T_x,T_y, color='red')
    plt.scatter(D_x, D_y, color='green')
    plt.subplot(212)
    plt.scatter(D_x -T_x, D_y-T_y, color='blue')

    fig = plt.figure()
    yedges = np.arange(-h/2.,h/2. + 1, bin_size)
    xedges = np.arange(0,w+1, bin_size)
    ax = fig.add_subplot(221)
    ax.hist(T_x, bins=xedges)
    plt.title("Histogram of Target's Position (on X)")

    yedges = np.arange(-h/2.,h/2. + 1, bin_size)
    xedges = np.arange(0,2*w+1, bin_size)
    ax = fig.add_subplot(222)
    dist_hist = ax.hist(distances, bins = xedges)
    plt.title("Histogram of Distractor-Target distance (degrees)")


    yedges = np.arange(-h/2.,h/2. + 1, bin_size)
    xedges = np.arange(0,w+1, bin_size)
    H, xedges, yedges = np.histogram2d(T_x, T_y, bins=(xedges, yedges))
    X, Y = np.meshgrid(xedges[1:], yedges[1:])

    ax = fig.add_subplot(223)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
    plt.imshow(H.T,extent=extent,interpolation='nearest',origin='lower')
    plt.colorbar()
    plt.title("2D distribution of the Target (degrees)")

    yedges = np.arange(-h,h + 1, bin_size*2)
    xedges = np.arange(-2*w,2*w, bin_size*2)
    H, xedges, yedges = np.histogram2d(T_x-D_x, T_y-D_y, bins=(xedges, yedges))

    ax = fig.add_subplot(224)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
    plt.imshow(H.T,extent=extent,interpolation='nearest',origin='lower')
    plt.colorbar()
    plt.title("2D distribution of the Distractor from the Target (degrees)")

def initializeFromConditions(nb_trials):
    while True:
        namesubject = "NoName"
        while len (namesubject) > 2 :
            namesubject = raw_input("subject: ")

        freqDistractor = 8
##        first_stim_duration = "none"
##        while first_stim_duration not in ["st", "lg"] :
##            first_stim_duration = raw_input("Condition Stim: ")

        block = raw_input("block: ")

        filename_eyetracker = namesubject+"S1gpB"+block ## 8 letters for the eyextarchet
        path_to_eye_tracker_file = ".\\results\\%s.EDF"%filename_eyetracker
        path_to_table_file = ".\\tables\\%s-table.DATA"%filename_eyetracker

        create_new_file = False
        if os.path.isfile(path_to_eye_tracker_file) or os.path.isfile(path_to_table_file):
            print "Be carefull! "
            print path_to_eye_tracker_file, "already exist: ", os.path.isfile(path_to_eye_tracker_file)
            print path_to_table_file, "already exist: ", os.path.isfile(path_to_table_file)
            override = raw_input("Do you want to replace those files? (o/N) ")
            if override == "o":
                create_new_file = True

        else:
            create_new_file = True

        if create_new_file:
            info, table = createTableOfTrials(nb_trials, freqDistractor, block, namesubject,
                                              path_to_table_file)
            return info, table, path_to_table_file, path_to_eye_tracker_file

def openTable(file_path): ## open a test file if the sting is empty
    if file_path == "":
        file_path = ".\\tables\\TEST-table.DATA"
        eye_tracker_path = ".\\results\\TEST.EDF"
    else:
         eye_tracker_path = ""
    info = re.findall("[\w]+", linecache.getline(file_path, 2) )
    linecache.clearcache()
    if eye_tracker_path == "":
        repeat = True
        while repeat:
            EDFname = raw_input("Give a name to the EDF file: \n Info: %s"%str(info))
            eye_tracker_path = ".\\results\\"+ EDFname+".EDF"
            if os.path.isfile(eye_tracker_path):
                repeat = True
                print "Name already use!!"
            else:
                repeat = False
    table = np.loadtxt(file_path)
    return info, table, file_path, eye_tracker_path

def saveEyeTrackerData(Eyelink, src, dest):
    if Eyelink != None:
        # File transfer and cleanup!
        Eyelink.setOfflineMode();
        pylink.msecDelay(500);

        #Close the file and transfer it to Display PC
        Eyelink.closeDataFile()
        Eyelink.receiveDataFile(src, dest)

def runCalibration(MyEnv, setup=True):
    first_time = True
    while first_time or event.key == pygame.K_r :
        pylink.openGraphics()
        if setup:
            MyEnv.eyelink.sendCommand("key_function space 'accept_target_fixation'");
            pylink.setCalibrationColors((255, 255, 255), BACKGROUND[0:3]);        #Sets the calibration target and background color
            pylink.setTargetSize(int(MyEnv.surf.get_rect().w/70), int(MyEnv.surf.get_rect().w/300));    #select best size for calibration target
            pylink.setCalibrationSounds("", "", "");
            pylink.setDriftCorrectSounds("", "off", "off");
            MyEnv.eyelink.sendCommand("calibration_type=%s"%MyEnv.calib_type);
        print "doTrackerSetup to do..."
        MyEnv.eyelink.doTrackerSetup()
        print "doTrackerSetup Done"
        pylink.closeGraphics()
        event = displayInstruction(MyEnv, "calibration_done.txt")
        first_time = False
    return event

def configEDFfile(MyEyelink):
    tracker_software_ver = 0
    eyelink_ver = MyEyelink.getTrackerVersion()

    if eyelink_ver == 3:
        tvstr = MyEyelink.getTrackerVersionString()
        vindex = tvstr.find("EYELINK CL")
        tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))


    if eyelink_ver>=2:
        MyEyelink.sendCommand("select_parser_configuration 0")
        if eyelink_ver == 2: #turn off scenelink camera stuff
            MyEyelink.sendCommand("scene_camera_gazemap = NO")
    else:
        MyEyelink.sendCommand("saccade_velocity_threshold = 35")
        MyEyelink.sendCommand("saccade_acceleration_threshold = 9500")

    # set EDF file contents
    MyEyelink.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
    #                        ^^^
    if tracker_software_ver>=4:
        MyEyelink.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
    else:
        MyEyelink.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

    # set link data (used for gaze cursor)
    # Create a link to send the data in realtime on the Display PC:
    MyEyelink.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
    #                        ^^^
    if tracker_software_ver>=4:
        MyEyelink.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
    else:
        MyEyelink.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")


def makeHeader(info):
    header = '''| condition | frequency of the distractor | block | subject ID
     %s | %s| %s| %s
    ---------------------------------------------------------------------------------------------------
    | ntrial | trial type | Stim 1 ecc. | Stim 1 dir. | Stim 2 ecc. | Stim 2 dir. | T-D Distance | fixation_duration | gap duration | first stim_duration | second stim_duration '''%(info[0], info[1], info[2], info[3])
    return header

def getTxtBitmap(text, dim):
    ''' This function is used to create a page of text. '''

    ''' return image object if successful; otherwise None '''

    if(not font.get_init()):
        font.init()
    fnt = font.Font("cour.ttf",15)
    fnt.set_bold(1)
    sz = fnt.size(text[0])
    bmp = Surface(dim)

    bmp.fill((255,255,255,255))
    for i in range(len(text)):
        txt = fnt.render(text[i],1,(0,0,0,255), (255,255,255,255))
        bmp.blit(txt, (0,sz[1]*i))

    return bmp

class Monitor():
    def __init__(self, name, w, h, distance, width_cm):
        self.name = name
        self.w = w
        self.h = h
        self.size = np.array((w, h))
        self.distance = distance
        self.width_cm = width_cm
        self.pixelspercm = w/float(width_cm)
        self.degreespercm = self.distance * abs(np.tan(np.radians(1.0))) * np.sign(1.0)
        self.degreesperpixel = self.degreespercm/self.pixelspercm
        self.fps_control = 0

    def setFPSControl(self, n):
        self.fps_control = n

    def degToPixelsCentered(self, pos_deg): ## to use for position: put the origin on the center of the screen
        ''' deg is a position vector '''
        cmx = self.degToCm(pos_deg[0])
        cmy = self.degToCm(pos_deg[1])
        return int(round(cmx*self.pixelspercm + self.w/2.0)), int(round(cmy*self.pixelspercm + self.h/2.0))

    def degToPixels(self, size_deg): ## to use for size
        if type(size_deg) == int or type(size_deg) == float:
            return int(round(self.degToCm(size_deg)*self.pixelspercm))
        else:
            return np.round(self.degToCm(size_deg)*self.pixelspercm).astype(int)

    def degToCm(self, deg):
        return self.distance * abs(np.tan(np.radians(deg))) * np.sign(deg)

class Environment():
    def __init__(self, surf, monitor, eyelink, table, info,calib_type = "HV13", units='deg'):
        self.surf = surf
        self.calib_type = calib_type
        self.monitor = monitor
        self.eyelink = eyelink
        self.table = table
        self.info = info

    def getDetails(self):
        return (self.surf, self.monitor, self.eyelink, self.table, self.info)

class Shape():
    def __init__(self, MyEnvironment, size, pos, fill_color = (255,255,255), edge_color = (0,0,0), line_width = 0 , units ='deg'):
        self.mysurf = MyEnvironment.surf
        self.mymonitor = MyEnvironment.monitor
        self.fill_color = fill_color
        self.edge_color = edge_color
        self.drawn = True
        if type(size) == int or type(size) == float:
            size = (size,size)
        if units == "deg":
            self.size_deg = size
            self.size = self.mymonitor.degToPixels(size)
        else:
            self.size = size
            self.size_deg = 0
        print "A new Shape has been created! Size: ", self.size
        self.pos_deg = pos ## keep track of position in degrees
        self.pos_polar = cartToPol(pos[0], pos[1])
        self.pos = self.mymonitor.degToPixelsCentered(pos)
        self.texture = pygame.Surface((self.size[0] + 2*line_width, self.size[1] + 2*line_width), flags = pygame.SRCALPHA)
        #self.texture = pygame.Surface((self.size[0] , self.size[1] ), flags = pygame.SRCALPHA)
        self.texture.fill((255,155,255,0)) ## fill the surface with a transparent background
        self.rect = self.texture.get_rect()
        self.rect.center = self.pos
        self.line_width = line_width ## the line_width is directly in pixels
        self.units = units ## not very usefull
        self.color1 = []
        self.color2 = []
        ## for debugging:
        #self.texture.fill((158,158,158))
        ## ------------
        self.createShape()

    def createShape(self): ## to be override
        pass

    def setFillColor(self,rgb):
        self.fill_color = rgb
        self.createShape()

    def setEdgeColor(self,rgb):
        self.edge_color = rgb
        self.createShape()

    def setPosDegCart(self, pos):
        self.pos_deg = pos
        self.pos_polar = cartToPol(pos[0], pos[1])
        self.pos = self.mymonitor.degToPixelsCentered(pos)
        self.rect.center = self.pos

    def setPos(self, pos):
        self.setPosDegCart(pos)

    def getPolarPos(self, i):
        return self.pos_polar[i]

    def getDegPos(self, i):
        return self.pos_deg[i]

    def getPixelPos(self, i):
        return self.pos[i]

    def draw(self):
        if self.drawn:
            self.mysurf.blit(self.texture, self.rect.topleft)


class Cross(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )
        print "Orthonormal Cross Created."

    def createShape(self):
        l = self.line_width
        pygame.draw.line(self.texture, self.fill_color, (self.size[0]/2.,0) , (self.size[0]/2., self.size[1]-l), self.line_width)
        pygame.draw.line(self.texture, self.fill_color, (0,self.size[1]/2.), (self.size[0]-l, self.size[1]/2.), self.line_width)

class Slash(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )
        print "Slash Created."

    def createShape(self):
        #pygame.draw.line(self.texture, self.fill_color, (0,0) , (self.size[0], self.size[1]), self.line_width)
        pygame.draw.line(self.texture, self.fill_color, (-1,self.size[1]), (self.size[0], -1), self.line_width)

class AntiSlash(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )
        print "AntiSlash Created."

    def createShape(self):
        pygame.draw.line(self.texture, self.fill_color, (0,0) , (self.size[0], self.size[1]), self.line_width)
        #pygame.draw.line(self.texture, self.fill_color, (-1,self.size[1]), (self.size[0], -1), self.line_width)

class TriangleUp(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )
        if units == "deg":
            gravityshift = np.array( (0 ,  self.size_deg[1]/2.0 - self.size_deg[1]/3.0  ) ) ## assume a eauilateral
            self.gravityshift = self.mymonitor.degToPixels(gravityshift)
        else:
            self.gravityshift = np.array( (0 ,  int(round(self.size[1]/2.0 - self.size[1]/3.0))  ) )
        print "TriangleUp Created."

    def createShape(self):
        #pygame.polygon.lines(self.texture, self.fill_color, [(0,self.size[1]),(self.size[0]/2, 0),(self.size[0], self.size[1]), (0,self.size[1])], self.line_width)
        l = self.line_width
        pygame.draw.lines(self.texture, self.fill_color, True, [(l,self.size[1]-l),(self.size[0]/2, l),(self.size[0]-l, self.size[1]-l)], self.line_width)
    def draw(self):
        pos = self.rect.topleft - self.gravityshift
        self.mysurf.blit(self.texture, pos)

class TriangleDown(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )
        gravityshift = np.array( (0 ,  self.size_deg[1]/2.0 - self.size_deg[1]/3.0  ) ) ## assume a eauilateral
        self.gravityshift = self.mymonitor.degToPixels(gravityshift)
        print "TriangleDown Created."
        #print "gravityshift:", self.gravityshift

    def createShape(self):
        l = self.line_width
        pygame.draw.lines(self.texture, self.fill_color, True, [(l,l), (self.size[0]/2, self.size[1]-l), (self.size[0]-l, l)], self.line_width)

    def draw(self):
        pos = self.rect.topleft + self.gravityshift
        self.mysurf.blit(self.texture, pos)

class CrossDiag(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        print "CrossDiag Created."
        Shape.__init__(self,MyEnvironment, size, pos, fill_color , edge_color , line_width , units )

    def createShape(self):
        pygame.draw.line(self.texture, self.fill_color, (0,0) , (self.size[0], self.size[1]), self.line_width)
        pygame.draw.line(self.texture, self.fill_color, (-1,self.size[1]), (self.size[0], -1), self.line_width)


class Circle(Shape):
    def __init__(self, MyEnvironment, size=(1,1), pos=(0,0), fill_color = (255,255,255), edge_color = (0,255,0), line_width = 1, units ='deg'):
        Shape.__init__(self,MyEnvironment,size, pos, fill_color , edge_color , line_width , units )
        print "Circle Created."

    def createShape(self):
        l = self.line_width
        box = (l,l, self.size[0]-l, self.size[1]-l)

        pygame.draw.ellipse(self.texture, self.fill_color, box , self.line_width)

    def setRadius(self, r1, r2):
        self.size = self.mymonitor.degToPixels(np.array((r1,r2)))
        self.texture = pygame.Surface((self.size[0], self.size[1]))
        self.rect = self.texture.get_rect()
        self.rect.center = self.pos


class TextStim(Shape): ## in degree and align on the center
    def __init__(self, MyEnvironment, text, pos = (0,0), fill_color = (255,255,255), edge_color = (0,0,0), width = 0, units ='deg'):
        self.text = text
        Shape.__init__(self,MyEnvironment, (1,1), pos, fill_color , edge_color , width , units)
        self.rect = self.texture.get_rect()
        self.size = self.rect.size
        self.rect.center = self.pos
        print "Textual Stimulation Created."

    def createShape(self):
        if(not font.get_init()):
            font.init()
        self.fnt = font.Font("cour.ttf",15)
        self.fnt.set_bold(1)
        self.texture = self.fnt.render(self.text,1,self.fill_color, self.edge_color)

    def setText(self, text):
        self.text = text
        self.texture = self.fnt.render(self.text,1,self.fill_color, self.edge_color)
        self.rect = self.texture.get_rect()
        self.rect.center = self.pos



class NormalText(Shape): ## in pixel, and align on the top-left
    def __init__(self, MyEnvironment, text, pos = (0,0), fill_color = (255,255,255), edge_color = (0,0,0), width = 0, units ='px'):
        self.text = text
        Shape.__init__(self,MyEnvironment, (1,1), pos, fill_color , edge_color , width , units)
        self.pos = pos ## cancel the transformation degrees to pixels
        self.rect = self.texture.get_rect()
        self.size = self.rect.size
        self.rect.topleft = self.pos
        print "Text Created."

    def createShape(self):
        if(not font.get_init()):
            font.init()
        self.fnt = font.Font("cour.ttf",15)
        self.fnt.set_bold(1)
        self.texture = self.fnt.render(self.text,1,self.fill_color, self.edge_color)

    def setText(self, text):
        self.text = text
        self.texture = self.fnt.render(self.text,1,self.fill_color, self.edge_color)
        self.rect = self.texture.get_rect()
        self.rect.topleft = self.pos

    def setPos(self, pos):
        self.pos = pos
        self.rect.topleft = self.pos




def drawFPS(fps, clock):
    text = "FPS: %d"%clock.get_fps()
    fps.setText(text)
    fps.draw()

def run_driftCorrection(MyEyelink):
    #The following does drift correction at the begin of each trial
    while 1:
        # Checks whether we are still connected to the tracker

        if not MyEyelink.isConnected():
            return ABORT_EXPT;

        # Does drift correction and handles the re-do camera setup situations
        try:
            error = MyEyelink.doDriftCorrect(surf.get_rect().w/2,surf.get_rect().h/2,1,1)
            error = 0
            if error != 27:
                break;
            else:
                MyEyelink.doTrackerSetup();
        except:
            MyEyelink.doTrackerSetup()


def getTxtBitmap(text, txt_color = (0,0,0,255),bg_color = (255,255,255,255)):
    ''' This function is used to create a page of text. '''

    ''' return image object if successful; otherwise None '''

    if(not font.get_init()):
        font.init()
    fnt = font.Font("cour.ttf",15)
    fnt.set_bold(1)
    sz = fnt.size(max(text, key=len))

    bmp = pygame.Surface( (sz[0], len(text)*sz[1]) )

    bmp.fill(bg_color)
    for i in range(len(text)):
        txt = fnt.render(text[i],1,txt_color, bg_color)
        bmp.blit(txt, (0, sz[1]*i))

    return bmp

def displayInstruction(MyEnv, text_file, waiting = True, additional_text = ""):
    text = "Text not found..."
    if text_file != "":
        with open(text_file) as f:
            text =  [line.rstrip() for line in f]
            text.append(additional_text)
            text_bmp = getTxtBitmap(text, txt_color =(255,255,255,255),bg_color = BACKGROUND)
    else:
        text= [additional_text]
        text_bmp = getTxtBitmap(text, txt_color =(255,255,255,255),bg_color = BACKGROUND)

    pressed = False
    while not pressed:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed = True
        MyEnv.surf.fill(BACKGROUND)
        pos = text_bmp.get_rect()
        pos.centerx, pos.centery = MyEnv.monitor.w/2., MyEnv.monitor.h/2
        MyEnv.surf.blit(text_bmp,pos)
        pygame.display.flip()
        if not waiting:
            return
    return event

def displayTestScreen(MyEnv, ecc, n):
    global BACKGROUND, RED, GREEN
    text = NormalText (MyEnv, "Dummy Mode", pos=(0,0))
    ecc = 13.0
    tar_positions = np.linspace(0, 45, 9)[1:]
    tar_positions = np.hstack( (tar_positions, 180-tar_positions, -180+tar_positions, -tar_positions) )
    n_pos = len(tar_positions)
    target_t = Circle(MyEnv,size=TARGET_SIZE, line_width = 2)
    target_t.setFillColor(RED)
    dist_t = CrossDiag(MyEnv,size=DISTRACTOR_SIZE, line_width = 2)
    dist_t.setFillColor(GREEN)
    fixation_t = Circle(MyEnv,size=TARGET_SIZE, line_width = 2)
    fixation_t.setFillColor(GREEN)
    print "position:", fixation_t.pos, "rectangle center:", fixation_t.rect.center
    print "reectangle coordinate:", fixation_t.rect

    distractor_shown = True
    pressed = False
    speed = np.array((1,1,1,0))
    stimulus_color = GREEN
    selected = BACKGROUND
    mark = "BG"
    while not pressed:
        MyEnv.surf.fill(BACKGROUND)
        for angle in tar_positions:
            ##angle = i/float(n) * 360
            target_t.setPos(polToCart(ecc, angle))
            dist_t.setPos(polToCart(ecc, angle))
            if distractor_shown:
                dist_t.draw()
            target_t.draw()
        text.setText("Color %s: %s"%(mark, str(selected)))
        text.draw()
        fixation_t.draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pressed = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                #stimulus_color = GREEN
                selected = GREEN
                mark = "G"
                speed = np.array((0,1,0,0))

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                #stimulus_color = RED
                selected = RED
                mark = "R"
                speed = np.array((1,0,0,0))

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                selected = BACKGROUND
                mark = "BG"
                speed = np.array((1,1,1,0))

            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                selected = GREEN
                mark = "G"
                speed = np.array((0,0,0,1))

            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                target_t = CrossDiag(MyEnv,size=DISTRACTOR_SIZE, line_width = 2)
                target_t.setFillColor(stimulus_color)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                target_t = Circle(MyEnv,size=TARGET_SIZE, line_width = 2)
                target_t.setFillColor(stimulus_color)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                distractor_shown = not distractor_shown

            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                selected = (np.array(selected) + speed)% 256
                selected = selected.tolist()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                selected = (np.array(selected) - speed)%256
                selected = selected.tolist()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                speed *= 2
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                speed /= speed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                print BACKGROUND, RED, GREEN

        if mark == "BG":
            BACKGROUND = selected
        elif mark == "R":
            RED = selected
            stimulus_color = RED
        elif mark == "G":
            GREEN = selected
            stimulus_color = GREEN
        fixation_t.setFillColor(stimulus_color)
        target_t.setFillColor(stimulus_color)