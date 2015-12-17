Experiment 2 (appendix) of the Chapter on Deviation Away from a previously fixated stimulus.

We basically used the program for the experiment on the extent of the Global Effect.
The main difference is that the fixation cross does not disappear automatically,
The participant need to press the space_bar to confirm he's fixating, then the trial starts after a random time.

That need to press a button increase drastically the time of the experiment.

However there is no distractor-target / identical stimuli condition.
All the conditions are with identical stimuli.

TRIAL TYPE:
	0 for control (center vertical saccades), 
		Fixation duration (after button press): 500-1100 ms (mean 800 ms)
		Stim. 1 duration: 350 ms
	1 for single,
		Fixation duration (after button press): 500-1100 ms (mean 800 ms)
		Stim. 1 duration: 350 ms
	2 for double,
		Fixation duration (after button press): 500-1100 ms (mean 800 ms)
		Stim. 1 duration: SEE EXPERIMENTAL CONDITION
		Stim. 2 diration: 350 ms.

EXPERIMENTAL CONDITION:
	S1st --> Stimulus 1 short duration (250-450ms, mean 350 ms)
	S1lg --> Stimulus 1 long duration (450-650ms, mean 550 ms)			

Only one distance is tested here. (30 degrees between the two stimuli, both at 13.5 degrees of eccentricity)

sectime = ((1000+800+350)*160+(1000+800+350)*320+(1000+800+S1st+350)*320)/1000
import time 
time.strftime("%H:%M:%S", time.localtime(sectime))


IN ONE SESSION:
	Nb_trial = 800
	20% control, 160
	40% test-double, 320
	40% test-single, 320

	This is done to get 4 bins of RT which contains 80 trials each.
	Breaks every 200 trials --> 3 breaks
	Calibration every 400 trials --> One Calibration in addition to the initial one.

TIME ESTIMATED:
	800 trials ~= 37min
	+ 15min instruction/Calib

	I tried this morning: 
	FOR THE CONDITION SHORT DURATION:
	Calibration -- 20 min (I was bad)
	Experiment -- 35 min (breaks/calib included)
	Data saving -- 6 min.
	TOTAL -- 1 hours and 1 minute.

NOTES:
	#MyMonitor = utils.Monitor("Geoffrey-PC",1024,720, distance = 20, width_cm = 50)
	MyMonitor = utils.Monitor("labo-Tom-PC",1280,1024, distance = 72, width_cm = 36.6)
	#MyMonitor = utils.Monitor("Labo-Tom-Big",1024,768, distance = 130, width_cm = 206)
