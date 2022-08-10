#Import modules
import os
from configparser import ConfigParser

#Take user input of the name of the simulation they wish to run plots for,
#and return as a directory path
def userInput():
        pathExists = False
        #Loop until the specified path exists
        while pathExists == False:
            #Ask the user for input
            run = input("Enter the name of the simulation you wish to plot. Press enter to default to the name in the current .ini file: ")
            #If the user presses enter, read the name in the config.ini file located in Scripts and return as a path
            if run == "":
                cfg = ConfigParser()
                cfg.read('config.ini')
                location = cfg['GENERAL']['name']
                return '../Data/{}'.format(location)
            #Check if the simulation name given has a valid path
            pathExists = os.path.exists('../Data/{}'.format(run))
            #Return as a path if true, or let the user know this is not a valid name and ask for input again
            if pathExists == True:
                return '../Data/{}'.format(run)
            else:
                print("This is not a valid simulation.")