#Import modules
import scipy.stats as stats
import numpy as np
import math
import random
from config import configParameters as cfg
from storage import storage

#The rayPhysics class calculates the path of the rays and runs the simulation
class rayPhysics(cfg):
    def __init__(self, path="."):
        #'path' is where config.ini is read from
        self.path = path
        cfg.__init__(self)

    #Check if the ray hit the screen and return True or False
    def hitScreen(self, rayPos, screenSize):
        #Check if the position of the ray is within the bounds of the screen
        if rayPos[0] >= screenSize[0,0] and rayPos[0] <= screenSize[0,1] and rayPos[1] >= screenSize[1,0] and rayPos[1] <= screenSize[1,1]:
            return True
        else:
            return False

    #Calculate and return the flux from the final screen
    def gaussianEmission(self, emissionAngle, sigma, initialAngle):
        #Calculate cumulative probability of each emission angle, plus or minus dx
        xminus = stats.norm.cdf(emissionAngle[0]-self.dx/2, loc=initialAngle[0], scale=sigma[0] * self.freq)
        xplus = stats.norm.cdf(emissionAngle[0]+self.dx/2, loc=initialAngle[0], scale=sigma[0] * self.freq)
        yminus = stats.norm.cdf(emissionAngle[1]-self.dx/2, loc=initialAngle[1], scale=sigma[1] * self.freq)
        yplus = stats.norm.cdf(emissionAngle[1]+self.dx/2, loc=initialAngle[1], scale=sigma[1] * self.freq)
        #Calculate and return flux
        flux = abs(xplus - xminus) * abs(yplus - yminus)
        if flux < 1e-20:
            flux=0
        return flux

    #Pick and return an angle according to a gaussian distribution
    def gaussianRandom(self, sigma, initialAngle):
        #Pick and return an angle according to a gaussian distribution
        xAngle = stats.norm.rvs(loc=initialAngle[0], scale=sigma[0] * self.freq)
        yAngle = stats.norm.rvs(loc=initialAngle[1], scale=sigma[1] * self.freq)
        emissionAngle = np.array([xAngle, yAngle])
        return emissionAngle

    def rotate(self, coord, rotation):
        xprime = coord[0] * math.cos(math.radians(rotation)) + coord[1] * math.sin(math.radians(rotation))
        yprime = -coord[0] * math.sin(math.radians(rotation)) + coord[1] * math.cos(math.radians(rotation))
        return np.array([xprime, yprime])

    #Calculate the path of the first ray
    def firstRay(self, screenProperties, initialRayPos=[0,0]):
        #Pick an emission angle according to the uniform distribution within the specified range
        emissionAngleRF = [random.uniform(self.angles[1], self.angles[2]), random.uniform(self.angles[3],self.angles[4])]
        #Read the screen size and distance
        screenSize = np.array([[screenProperties[0], screenProperties[1]], [screenProperties[2], screenProperties[3]]])
        screenDistance = screenProperties[4] * self.dist
        #Calculate the new position of the ray (at the first screen)
        newRayPosRF = screenDistance * np.array([math.tan(math.radians(emissionAngleRF[0])), math.tan(math.radians(emissionAngleRF[1]))])
        newRayPos = self.rotate(newRayPosRF, -self.initRotation)
        #Calculate the path distance and time
        pathDistance = np.sqrt(screenDistance**2 + newRayPos[0]**2 + newRayPos[1]**2)
        pathTime = pathDistance / self.c
        #Check if the ray hit the screen
        hit = self.hitScreen(newRayPos, screenSize)
        emissionAngle = [math.degrees(np.arctan2(newRayPos[0], screenDistance)), math.degrees(np.arctan2(newRayPos[1], screenDistance))]
        #print(emissionAngle)
        #print(emissionAngleRotated)
        #Return data
        return [emissionAngle[0], emissionAngle[1], initialRayPos[0], initialRayPos[1], newRayPos[0], newRayPos[1], pathDistance, pathTime, hit, 1]

    #Calculate the path of the ray from one screen to another
    def middleRay(self, screenProperties, previousRay):
        #Read the screen size and distance
        screenSize = np.array([[screenProperties[1,0], screenProperties[1,1]],[screenProperties[1,2], screenProperties[1,3]]])
        screenDistance = (screenProperties[1,4] - screenProperties[0,4]) * self.dist
        #Check if the ray hit the previous screen and set the initial ray position
        previousHit = previousRay[8]
        initialRayPos = np.array([previousRay[4],previousRay[5]])
        if previousHit == True:
            #Scatter the ray according to the gaussian distribution
            #Read the intercept angle, and calculate its projection in the xy plane
            previousAngle = np.array([previousRay[0],previousRay[1]])
            previousAnglePosition = screenDistance * np.array([math.tan(math.radians(previousAngle[0])), math.tan(math.radians(previousAngle[1]))])
            #Transform this projection into the rotated frame, and convert back to the angle
            previousAnglePositionRF = self.rotate(np.array([previousAnglePosition[0],previousAnglePosition[1]]), screenProperties[0,5])
            previousAngleRF = [math.degrees(np.arctan2(previousAnglePositionRF[0], screenDistance)), math.degrees(np.arctan2(previousAnglePositionRF[1], screenDistance))]
            
            emissionAngleRF = self.gaussianRandom([screenProperties[0][6],screenProperties[0][7]], previousAngleRF)
            emissionAnglePositionRF = screenDistance * np.array([math.tan(math.radians(emissionAngleRF[0])), math.tan(math.radians(emissionAngleRF[1]))])

            emissionAnglePosition = self.rotate(np.array([emissionAnglePositionRF[0], emissionAnglePositionRF[1]]), -screenProperties[0,5])
            emissionAngle = [math.degrees(np.arctan2(emissionAnglePosition[0], screenDistance)), math.degrees(np.arctan2(emissionAnglePosition[1], screenDistance))]

            changeRayPos = screenDistance * np.array([math.tan(math.radians(emissionAngle[0])), math.tan(math.radians(emissionAngle[1]))])
            newRayPos = initialRayPos + changeRayPos
            pathDistance = np.sqrt(screenDistance**2 + changeRayPos[0]**2 + changeRayPos[1]**2)
            pathTime = pathDistance / self.c
            emissionAngle = [math.degrees(np.arctan2(changeRayPos[0], screenDistance)), math.degrees(np.arctan2(changeRayPos[1], screenDistance))]
        else:
            #Continue the ray along its path
            emissionAngle = np.array([previousRay[0],previousRay[1]])
            changeRayPos = screenDistance * np.array([math.tan(math.radians(emissionAngle[0])), math.tan(math.radians(emissionAngle[1]))])
            newRayPos = initialRayPos + changeRayPos
            pathDistance = np.sqrt(screenDistance**2 + changeRayPos[0]**2 + changeRayPos[1]**2)
            pathTime = pathDistance / self.c
        #Calculate and update the ray position, path distance and time
        #Check if the ray hit the screen
        hit = self.hitScreen(newRayPos, screenSize)
        #Return data
        return [emissionAngle[0], emissionAngle[1], initialRayPos[0], initialRayPos[1], newRayPos[0], newRayPos[1], pathDistance, pathTime, hit, 1]

    #Calculate the path of the ray from the final screen to Earth
    def finalRay(self, screenProperties, previousRay):
        #Calculate the distance to Earth
        screenDistance = (1 - screenProperties[4]) * self.dist
        #Check if the ray hit the previous screen and set the initial ray position
        previousHit = previousRay[8]
        initialRayPos = np.array([previousRay[4],previousRay[5]])
        #Calculate the angle required to hit Earth, and its projection in the xy plane
        requiredAngle = np.array([math.degrees(np.arctan2(-initialRayPos[0], screenDistance)),math.degrees(np.arctan2(-initialRayPos[1], screenDistance))])
        requiredAnglePosition = [-initialRayPos[0],-initialRayPos[1]]
        #Transform this projection into the rotated frame, and convert back to the angle
        requiredAnglePositionRF = self.rotate(np.array(requiredAnglePosition), screenProperties[5])
        requiredAngleRF = np.array([math.degrees(np.arctan2(requiredAnglePositionRF[0], screenDistance)),math.degrees(np.arctan2(requiredAnglePositionRF[1], screenDistance))])
        #Read the intercept angle, and calculate its projection in the xy plane
        previousAngle = np.array([previousRay[0],previousRay[1]])
        previousAnglePosition = screenDistance * np.array([math.tan(math.radians(previousAngle[0])), math.tan(math.radians(previousAngle[1]))])
        #Transform this projection into the rotated frame, and convert back to the angle
        previousAnglePositionRF = self.rotate(np.array([previousAnglePosition[0],previousAnglePosition[1]]), screenProperties[5])
        previousAngleRF = [math.degrees(np.arctan2(previousAnglePositionRF[0], screenDistance)), math.degrees(np.arctan2(previousAnglePositionRF[1], screenDistance))]
        if previousHit == True:
            #Force the scattering angle to be the required angle, and scale the flux as the probability of this according to the gaussian distribution
            flux = self.gaussianEmission(requiredAngleRF, [screenProperties[6],screenProperties[7]], previousAngleRF)
            #Set the new ray position to Earth and set hit as True
            newRayPos = [0,0]
            hit = True
            emissionAngle = requiredAngle
        else:
            #Continue the ray along its path
            emissionAngle = np.array([previousRay[0],previousRay[1]])
            #Calculate the difference between the required and actual angle
            angleDifference = np.array([np.abs(emissionAngle[0]-requiredAngle[0]), np.abs(emissionAngle[1]-requiredAngle[1])])
            #Calculate and update the ray position
            changeRayPos = screenDistance * np.array([math.tan(math.radians(emissionAngle[0])), math.tan(math.radians(emissionAngle[1]))])
            newRayPos = initialRayPos + changeRayPos
            #If the angle difference is small enough, then count as hitting Earth with full flux
            if angleDifference.all() <= self.dx/2:
                flux=1
                hit=True
            else:
                flux=0
                hit=False
        #Calculate and update the path distance and time
        pathDistance = np.sqrt(screenDistance**2 + initialRayPos[0]**2 + initialRayPos[1]**2)
        pathTime = pathDistance / self.c
        #Return data
        return [emissionAngle[0], emissionAngle[1], initialRayPos[0], initialRayPos[1], newRayPos[0], newRayPos[1], pathDistance, pathTime, hit, flux]

    #Run the simulation
    def emitRays(self):
        rayData = np.empty([self.rays, self.num+1, 10])
        #Loop over number of rays
        for x in range(self.rays):
            #Set screenProperties to those of the first screen
            screenProperties = self.screens[0]
            #Calculate the ray data for between the pulsar and first screen
            rayData[x][0] = self.firstRay(screenProperties)
            #Check if there is more than one screen
            if self.num > 1:
                #Loop over each ray between screens
                for i in range(1,self.num):
                    #Set previousRay to the data from the incoming ray
                    previousRay = rayData[x][i-1]
                    #Set screenProperties to those of the previous and next screen
                    screenProperties = np.array([self.screens[i-1], self.screens[i]])
                    #Calculate the ray data for between the previous and next screen
                    rayData[x][i] = self.middleRay(screenProperties, previousRay)
            #Set previousRay to the data from the incoming ray to the final screen
            previousRay = rayData[x][-2]
            #Set screenProperties to those of the final screen
            screenProperties = self.screens[-1]
            #Calculate the ray data for between the final screen and Earth
            rayData[x][-1] = self.finalRay(screenProperties, previousRay)
        #Save the rayData
        storage(self.path).saveData(rayData)