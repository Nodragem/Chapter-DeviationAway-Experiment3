#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Geoffrey
#
# Created:     31/01/2014
# Copyright:   (c) c1248317 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import pygame
from pylink import *

class DummyEyeLink():
    def __init__(self):
        pygame.init()
        self.mysample = Sample()
        self.brk = False
        self.escape = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                self.mysample.myeye.setGaze(pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:
                k = pygame.key.get_pressed()
                m = pygame.key.get_mods()
                if m & pygame.KMOD_CTRL and k[pygame.K_v]:
                    self.brk = True
                    print "Crtl + V pressed"
                if event.key == pygame.K_ESCAPE:
                    self.escape = True
                    print "Escape Pressed"

    def doTrackerSetup(self):
        pass
    def doDriftCorrect(self, a,b,c,d):
        pass
    def waitForBlockStart(self, a, b, c):
        return True
    def openDataFile(self,s):
        print "Dummy doesn't really open", s
    def startRecording(self, a,b,c,d):
        print "Dummy starts recording..."

    def endRealTimeMode(self):
        pass
    def startRealTimeMode(self):
        pass

    def bitmapSaveAndBackdrop(self, m,l,k,j,i,h,g,f,e, d,c,b,a):
        pass

    def eyeAvailable(self):
        return 2

    def setOfflineMode(self):
        pass
    def sendCommand(self,s):
        print "Dummy received command:", s
    def sendMessage(self,s):
        print "Dummy received message:", s
    def getTrackerVersion(self):
        return -1
    def getRecordingStatus(self):
        return TRIAL_OK
    def getTrackerVersionString(self):
        return "0.0"
    def isConnected(self):
        return True
    def isRecording(self):
        return 0
    def stopRecording(self):
        print "Dummy stops recording..."
    def getkey(self):
        return False
    def breakPressed(self):
        if self.brk:
            self.brk = False
            return True
        return False

    def escapePressed(self):
        if self.escape:
            self.escape = False
            return True
        return False

    def closeDataFile(self):
        print "Dummy doesn't really close the Data File."
    def receiveDataFile(self, a, b):
        print "Dummy doesn't really send the data to the Display PC."
    def close(self):
        pass
    def flushKeybuttons(self, n):
        pass
    def getLastButtonPress(self):
        return (0,0,0,0,0)
    def getNewestSample(self):
        return self.mysample

class Sample():
    def __init__(self):
        self.myeye = Eye()
    def getRightEye(self):
        return self.myeye
    def getLeftEye(self):
        return self.myeye
    def isRightSample(self):
        return True
    def isLeftSample(self):
        return True

class Eye():
    def __init__(self):
        self.x = 0
        self.y = 0
    def getGaze(self):
        print self.x, self.y
        return (self.x, self.y)
    def setGaze(self, vector):
        self.x, self.y = vector[0], vector[1]

