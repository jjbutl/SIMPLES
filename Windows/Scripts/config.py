#Import modules
from scipy import constants
import numpy as np
from numpy import inf
from configparser import ConfigParser
import os

#The configParameters class is creates config.ini if it doesn't
#already exist, and reads config.ini. The parameters can be accessed
#globally by any functions that import configParameters
class configParameters():
    def __init__(self, path="."):
        #'path' is where config.ini is read from
        #Check if config.ini exists, and if not, create it
        if os.path.exists('config.ini') == False:
            self.createConfig()
        #Read config.ini and save the parameters
        generalParameters, self.angles, self.initRotation, self.screens = self.configReader()
        #Unpack the generalParameters into an easily accessible form
        self.name = generalParameters['name']
        self.rays = int(generalParameters['rays'])
        self.dist = float(generalParameters['dist'])
        self.freq = (1400/float(generalParameters['freq']))**2
        self.dx = float(generalParameters['dx'])
        self.num = int(generalParameters['num'])
        self.c = constants.c

    #Creates config.ini if it doesn't already exist in the 'Scripts' directory
    def createConfig(self):
        config = ConfigParser()
        #Contains general parameters for the simulation
        config['GENERAL'] = {
            'name':'run1',
            'rays':1000,
            'dist':6.171e18,
            'freq':1400,
            'dx':1e-6,
        }
        config['ANGLES'] = {
            'coords':1,
            'xmin': -0.01,
            'xmax': 0.01,
            'ymin': -0.01,
            'ymax': 0.01
        }
        #Contains the dimensions, position and scattering properties of a screen
        config['SCREEN1'] = {
            'bottomx':-inf,
            'topx':inf,
            'bottomy':-inf,
            'topy':inf,
            'position':0.3,
            'rotation':0,
            'sigmax':1e-4,
            'sigmay':1e-4
        }
        #Write to config.ini
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    #Reads config.ini at the specified path
    def configReader(self):
        cfg = ConfigParser()
        #Read config.ini
        cfg.read('{}\\config.ini'.format(self.path))
        #Save the general parameters
        generalParameters = dict(cfg.items('GENERAL'))
        #Count the number of screens
        screens = len(cfg.sections()) - 2
        #Add total screens to generalParameters
        generalParameters['num'] = screens
        screenParameters = np.empty([screens, 8])
        #Add the parameters of each screen to an array
        for i in range(screens):
            name = "SCREEN{}".format(i+1)
            screen = list(dict(cfg.items(name)).values())
            for j in range(8):
                screenParameters[i,j] = float(screen[j])
        angleList = list(dict(cfg.items('ANGLES')).values())
        angles = np.empty(5)
        angles[0] = int(angleList[0])
        for i in range(4):
                angles[i+1] = float(angleList[i+1])
        if int(angleList[0]) == 0:
            initRotation = 0
        else:
            initRotation = screenParameters[int(angleList[0])-1,5]
        #Return the parameters
        return generalParameters, angles, initRotation, screenParameters