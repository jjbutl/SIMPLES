#Import modules
import h5py
import os
from config import configParameters as cfg
from configparser import ConfigParser

#The storage class saves and loads rayData.h5 and config.ini files
class storage(cfg):
    def __init__(self, path):
        #'path' is where config.ini is read from
        self.path = path
        cfg.__init__(self)
        #'directory' is where all simulation data is saved
        self.directory = '..\\Data\\{}'.format(self.name)

    #Saves rayData.h5 and config.ini to the directory
    def saveData(self, rayData):
        #Create the directory if it doesn't exist
        if os.path.exists(self.directory) == False:
            os.makedirs(self.directory)
        #Create and save rayData.h5
        h5f = h5py.File('{}\\rayData.h5'.format(self.directory), 'w')
        h5f.create_dataset('rayData', data=rayData)
        h5f.close()
        #Read config.ini in 'Scripts' and save a copy to the directory
        config = ConfigParser()
        config.read('config.ini')
        with open('{}\\config.ini'.format(self.directory), 'w') as configfile:
            config.write(configfile)

    #Loads rayData.h5
    def loadData(self):
        #Loads and returns rayData.h5
        h5f = h5py.File('{}\\rayData.h5'.format(self.path),'r')
        rayData = h5f['rayData'][:]
        h5f.close()
        return rayData