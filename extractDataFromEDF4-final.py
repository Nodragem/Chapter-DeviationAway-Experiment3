import time
#tick = time.time()
import numpy as np
import re
import os
import glob
import ntpath


os.chdir(os.path.dirname(os.path.realpath(__file__)))
path_input = "raw_file/"
path_output = "numpy_file/"

list_names = []
list_files = glob.glob(path_input+"*.asc")
for p in list_files:
    list_names.append(ntpath.basename(p).split(".")[0]+"-np")
    
print list_files
print list_names

#raw_input("stop...")

for path_to_file, name in zip(list_files, list_names):
    ## open EDF file.
    fixation_ON = []
    stimuli_ON = []
    distractor_OFF = []
    end_times = []
    trial_id = []
    target_ecc = []
    target_dir = []
    trial_type = []
    digit_lines = []
    print "open and read EDF file..." + name
    with open(path_to_file) as f:
        for line in f:
            if re.match("\d+", line):
                digit_lines.append(line.split())

            elif "Fixation ON" in line:
                fixation_ON.append(map(int, re.findall("\d+", line))[0])
            elif "Fixation OFF" in line:
                stimuli_ON.append(map(int, re.findall("\d+", line))[0])
            elif "Distractor OFF" in line:
                distractor_OFF.append(map(int, re.findall("\d+", line))[0])
            elif "END" in line:
                end_times.append(map(int, re.findall("\d+", line))[0])
            elif "TRIALID" in line:
                t = np.array(line.split("[")[1].split(), dtype=float) # barbarian way
                #print t
                trial_id.append(int(t[0]+1)) ## strat from 1 and not from 0
                trial_type.append(int(t[1]))
                target_ecc.append(t[2])
                target_dir.append(t[3])

    print "conversion to Numpy Array"
    par = np.vstack((trial_id, trial_type, fixation_ON, stimuli_ON, distractor_OFF, end_times, target_ecc, target_dir)).T
    a = np.array(digit_lines)
    print "Replacement ... by NaN:"
    a = a[:, 0:6]
    a[a=="."] = np.nan
    real_time = a.astype(float)

    # trial id, type trial, stimuli ON, Target ecc, target direction, time, xp, yp, ps, xv, yv.  (11 columns)
    datamat = np.zeros((real_time.shape[0],11))
    datamat[:, 5:11] = real_time
    

    # create matrix of data
    end = [0]
    start = 0
    tick = time.time()
    print "Matrix creation"
    for index, p in enumerate(par): ## read index trial find in the EDF file.
        print "\r trial ID:", index,
        start = end[0] ## we start the search from the end of the previous 
        #print real_time[:,0] == p[-3]
        end = np.where(real_time[:,0] == (p[-3]-1))[0] ## we end the search at the end of the current trial
        #print start, end
        select = real_time[start:end,0] >= p[2]
        #print select
        #last_row 
        datamat[start:end,0:5][select,:] = np.tile(p[0:5], (np.sum(select),1) )
        datamat[start:end, 5][select] -= p[2] ## fixation_ON is the time zero

    tock = time.time() - tick
    print "saving..."
    raw_input("Done in %.4f second"%tock)
    np.save(path_output+name+".npy", datamat)

    print "end"



# import matplotlib.pyplot as plt
# select = (datamat[:,0] == 0)
# plt.scatter(datamat[select, 6], datamat[select, 7])
# plt.show()


