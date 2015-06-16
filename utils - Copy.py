import numpy as np
import pylink
from pygame import font
import pygame
import os
import matplotlib.pyplot as plt
from math import tan, radians

def createTableOfTrials(subjectID, distractor_freq, distractor_type, block, path):
    '''
    ## --- TABLE description ---
    ## -- > first row, which will be the header of the file:
    ## | distractor type | frequency of the distractor | block | subject ID
    ## -- > from the second row:
    ## | ntrial | trial type | Target ecc. | Target dir. | Distractor ecc. | Distractor dir. | T-D Distance
    ##
    ## --- Variable description:
    ## distractor type: "same" or "different" from the target
    ## frequency of the distractor: for instance, D20T80 for 20% of trials with distractor
    ## block: there is 5 block per condition, per subject
    ## subject ID: name or a number identifying the subject
    ##
    ## ntrial: 0,1,2,3,4,5 ...
    ## trial type: 0 for double, 1 for single, 2 for random-double, 3 for random-single.
    ## Target eccentricity, Target direction:
    ##              In single and double, the target can appear at 32 positions (8 per quadrant )
    ##              right top quadrant:   5.625,   11.25 ,   16.875,   22.5,   28.125,  33.75,   39.375,   45.
    ##      left top quadrant:  174.375,  168.75 ,  163.125,  157.5,  151.875, 146.25,  140.625,  135.
    ##      Multiply by -1 for the bottom quadrants.
    ## Distractor eccentricity, Distractor direction:
    ##              In double condition, the distractor is always on the other side of the target (-1)
    ## Note that in double condition, distractors and targets have the same eccentricity
    ## Target Distractor distance.
    ##      In double condition, the distance is 2*target_eccentricity * tan(target_direction)
    ## the 3 last distractor related variables are put at -1 if single condition
    '''
    distractor_freq = int(distractor_freq)
    info = ["same" if distractor_type == 's' else "different",
                            "D%d0T%d0"%(distractor_freq, 10-distractor_freq),
                            block, subjectID]
    header = makeHeader(info)


    eccentricity = 25
    number_of_dist_tested = 8
    tar_positions = np.linspace(0, 45, number_of_dist_tested+1)[1:]
    tar_positions = np.hstack( (tar_positions, 180-tar_positions, -180+tar_positions, -tar_positions) )
    n_pos = len(tar_positions)
    ## we want 100 measures per subjects per distances minimum.
    ## 1600 trials per block, 5 blocks.
    total_trials = 1600
    #table = np.zeros((total_trials, 7))
    ## let do the count of trial per trial type:
    amount_of_double = distractor_freq/20. * total_trials
    amount_of_single = (total_trials - amount_of_double*2) / 2.
    amount_of_rsingle = amount_of_single
    amount_of_rdouble = amount_of_double

    single_trials = np.tile((0, 1, eccentricity, 0 , -1, -1, -1), (amount_of_single, 1))
    single_trials[:,3] = np.tile(tar_positions, amount_of_single/n_pos)
    double_trials = np.tile((0, 0, eccentricity, 0 , eccentricity, 0, 0), (amount_of_double, 1))
    double_trials[:,3] = np.tile(tar_positions, amount_of_double/n_pos)
    double_trials[:,5] = - double_trials[:,3]
    double_trials[:,6] = 2*eccentricity * np.tan(double_trials[:,3])

    ## Random trials parameters
    distance_min = 1.5
    distance_max = 38
    tolerance =0.5
    ecc_max = 35
    ecc_min = 5
    resolution = 0.5

    rsingle_trials = np.concatenate((np.tile((0,3), (amount_of_rsingle,1)),
                                    doRandomDotsTable(-1, -1, 0, amount_of_rsingle, ecc_min,
                                    ecc_max, resolution).T,
                                    np.tile((-1,-1,-1), (amount_of_rsingle,1))
                                    ), axis = 1     )

    rdouble_trials = np.concatenate((np.tile((0,2), (amount_of_rdouble,1)),
                                    doRandomDotsTable(distance_min, distance_max, tolerance, amount_of_rdouble, ecc_min, ecc_max, resolution).T
                                    ), axis = 1     )

    table = np.concatenate((single_trials, double_trials, rsingle_trials, rdouble_trials), axis = 0)

    np.random.shuffle(table)
    table[:,0] = np.arange(total_trials)
    np.savetxt(path, table, delimiter = "\t", header = header)

## we test the table:
    print_stat(table)
    plot_trial_type(2, table)

    return info, table


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
    y = np.bincount(table[:,1].astype(int))
    ii = np.nonzero(y)[0]
    ii =  np.array(zip(ii,y[ii]))
    print ii[:,0]
    print ii[:,1]/float(table.shape[0])

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

def initializeFromConditions():
    while True:
        namesubject = "NoName"
        while len (namesubject) > 2 :
            namesubject = raw_input("subject: ")
        freqDistractor = None
        while freqDistractor not in ['2', '8']:
            freqDistractor = raw_input("Fd: ") ## 2 for 20% distractor, 5 for 50% distractor, 8 for 80%
        distr_type = None
        while distr_type not in ['d', 's']: ## d for different from target; s for similar to Target
            distr_type = raw_input("Td: ")
        block = raw_input("block: ")
        filename_eyetracker = namesubject+"F"+freqDistractor+"T"+distr_type+"B"+block ## 8 letters for the eyextarchet
        path_to_eye_tracker_file = ".\\results\\%s.EDF"%filename_eyetracker
        path_to_table_file = ".\\results\\%s-table.DATA"%filename_eyetracker

        if os.path.isfile(path_to_eye_tracker_file) or os.path.isfile(path_to_table_file):
            print "Be carefull! "
            print path_to_eye_tracker_file, "already exist: ", os.path.isfile(path_to_eye_tracker_file)
            print path_to_table_file, "already exist: ", os.path.isfile(path_to_table_file)
        else:
            info, table = createTableOfTrials(namesubject, freqDistractor, distr_type, block, path_to_table_file)
            return info, table, path_to_table_file, path_to_eye_tracker_file

def testConditions():
    info = ["different", "D80T20", "1", "MS"]
    table = np.loadtxt(".\\tables\\TEST-table.DATA")
    return info, table[0:100,:], ".\\tables\\TEST-table.DATA", ".\\results\\TEST-tracker.EDF"

def saveEyeTrackerData(Eyelink, src, dest):
    if Eyelink != None:
        # File transfer and cleanup!
        Eyelink.setOfflineMode();
        pylink.msecDelay(500);

        #Close the file and transfer it to Display PC
        Eyelink.closeDataFile()
        Eyelink.receiveDataFile(src, dest)

def runCalibration(MyEyelink, surf, calib_type, setup=True):
    if setup:
        MyEyelink.sendCommand("key_function space 'accept_target_fixation'");
        pylink.setCalibrationColors((255, 255, 255), (0, 0, 0));        #Sets the calibration target and background color
        pylink.setTargetSize(int(surf.get_rect().w/70), int(surf.get_rect().w/300));    #select best size for calibration target
        pylink.setCalibrationSounds("", "", "");
        pylink.setDriftCorrectSounds("", "off", "off");
        MyEyelink.sendCommand("calibration_type=%s"%calib_type);
    print "doTrackerSetup to do..."
    MyEyelink.doTrackerSetup()
    print "doTrackerSetup Done"

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
    header = '''| distractor type | frequency of the distractor | block | subject ID
     %s | %s| %s| %s
    ---------------------------------------------------------------------------------------------------
    | ntrial | trial type | Target ecc. | Target dir. | Distractor ecc. | Distractor dir. | T-D Distance '''%(info[0], info[1], info[2], info[3])
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
        self.fps_control = 0

    def setFPSControl(self, n):
        self.fps_control = n

    def degToPixelsCentered(self, deg): ## put also the origin on the center of the screen
        cmx = self.degToCm(deg[0])
        cmy = self.degToCm(deg[1])
        return int(round(cmx*self.pixelspercm + self.w/2.0)), int(round(cmy*self.pixelspercm + self.h/2.0))

    def degToPixels(self, deg): ## but also the origin on the center of the screen
        return int(round(self.degToCm(deg)*self.pixelspercm))

    def degToCm(self, deg):
        return self.distance * abs(np.tan(np.radians(deg))) * np.sign(deg)

class Environment():
    def __init__(self, surf, monitor, eyelink, table, info, units='deg'):
        self.surf = surf
        self.monitor = monitor
        self.eyelink = eyelink
        self.table = table
        self.info = info

    def getDetails(self):
        return (self.surf, self.monitor, self.eyelink, self.table, self.info)

class Shape():
    def __init__(self, MyEnvironment, fill_color = [255,255,255], edge_color = [0,0,0], width = 0 , units ='deg'):
        self.mysurf = MyEnvironment.surf
        self.mymonitor = MyEnvironment.monitor
        self.fill_color = fill_color
        self.edge_color = edge_color
        self.width = self.mymonitor.degToPixels(width)
        self.units = units
        self.color1 = []
        self.color2 = []

    def setFillColor(self,rgb):
        self.fill_color = rgb

    def setEdgeColor(self,rgb):
        self.edge_color = rgb

    def draw(self):
        pass




class Circle(Shape):
    def __init__(self, MyEnvironment, radius=1, center=(0,0), fill_color = [255,255,255], edge_color = [0,0,0], width = 0, units ='deg'):
        Shape.__init__(self,MyEnvironment, fill_color , edge_color , width , units )
        self.radius = self.mymonitor.degToPixels(radius)
        self.pos_deg = center
        x, y= self.mymonitor.degToPixelsCentered(center)
        self.pos = (x - self.radius, y - self.radius)

    def setRadius(self, r):
        self.radius = self.mymonitor.degToPixels(r)
    def setPos(self, pos):
        self.pos_deg = pos
        x, y = self.mymonitor.degToPixelsCentered(pos)
        self.pos = (x - self.radius, y - self.radius)
    def draw(self):
        pygame.draw.circle(self.mysurf, self.fill_color, self.pos, self.radius, self.width)

class TextStim(Shape): ## in degree and align on the center
    def __init__(self, MyEnvironment, text, center = (0,0), fill_color = (255,255,255), edge_color = (0,0,0), width = 0, units ='deg'):
        Shape.__init__(self,MyEnvironment, fill_color , edge_color , width , units)
        if(not font.get_init()):
            font.init()
        self.pos = center
        self.fnt = font.Font("cour.ttf",15)
        self.fnt.set_bold(1)
        self.text = self.fnt.render(text,1,self.fill_color, self.edge_color)
        self.textRect = self.text.get_rect()
        self.textRect.centerx, self.textRect.centery = self.mymonitor.degToPixelsCentered(self.pos)

    def setText(self, text):
        self.text = self.fnt.render(text,1,self.fill_color, self.edge_color)
        self.textRect = self.text.get_rect()
        self.textRect.centerx, self.textRect.centery = self.mymonitor.degToPixelsCentered(self.pos)


    def setPos(self, pos):
        self.pos = pos
        self.textRect.centerx, self.textRect.centery = self.mymonitor.degToPixelsCentered(self.pos)

    def draw(self):
        self.mysurf.blit(self.text, self.textRect)

class NormalText(Shape): ## in pixel, and align on the top-left
    def __init__(self, MyEnvironment, text, pos = (0,0), fill_color = (255,255,255), edge_color = (0,0,0), width = 0, units ='px'):
        Shape.__init__(self,MyEnvironment, fill_color , edge_color , width , units)
        if(not font.get_init()):
            font.init()
        self.pos = pos
        self.fnt = font.Font("cour.ttf",15)
        self.fnt.set_bold(1)
        self.text = self.fnt.render(text,1,self.fill_color, self.edge_color)
        self.textRect = self.text.get_rect()
        self.textRect.centerx, self.textRect.centery = self.pos[0], self.pos[1]

    def setText(self, text):
        self.text = self.fnt.render(text,1,self.fill_color, self.edge_color)
        self.textRect = self.text.get_rect()
        self.textRect.topleft = self.pos


    def setPos(self, pos):
        self.pos = pos
        self.textRect.topleft = self.pos

    def draw(self):
        self.mysurf.blit(self.text, self.textRect)


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


def getTxtBitmap(text, bg_color = (255,255,255,255)):
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
        txt = fnt.render(text[i],1,(0,0,0,255), (255,255,255,255))
        bmp.blit(txt, (0, sz[1]*i))

    return bmp

