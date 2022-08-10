#Import modules
import numpy as np
from config import configParameters as cfg
import matplotlib.pyplot as pp
from storage import storage
from matplotlib import colors

#The plots class produces and saves the plots
class plots(cfg):
    def __init__(self, path):
        #'path' is where config.ini is read from
        self.path = path
        cfg.__init__(self)

    #Calculate the time delay compared to a straight ray directly from the pulsar to Earth
    def timeDelay(self):
        time = np.empty([self.rays])
        flux = np.empty([self.rays])
        #Read in the flux and total time for each ray
        for x in range(self.rays):
            time[x] = np.sum(self.rayData[x,:,7])
        hit = self.rayData[:,-1,8]
        time[hit == False] = np.nan
        flux = self.rayData[:,-1,9]
        #Read the minimum time taken, and calculate the delay of the other rays with respect to this
        minTime = np.amin(time)
        delay = time - minTime
        #Return the delays and flux
        return delay, flux

    #Read the positions of each ray at each screen
    def rayPaths(self):
        screenPos = np.empty([self.num+2])
        paths = np.empty([self.rays,self.num+2,2])
        for x in range(self.rays):
            screenHits = np.empty([self.num+2,2])
            for i in range(self.num+1):
                screenHits[i] = np.array([self.rayData[x,i,2],self.rayData[x,i,3]])
            screenHits[-1] = np.array([self.rayData[x,-1,4],self.rayData[x,-1,5]])
            paths[x] = screenHits
        #Read the positions of each screen
        screenPos[0] = 0
        screenPos[1:-1] = self.screens[:,4] * self.dist
        screenPos[-1] = self.dist
        #Return the paths and screen positions
        return paths, screenPos

    #Plot where the rays hit the screens, weighted by the final flux
    def plotScreenHits(self):
        delay, flux = self.timeDelay()
        #Loop over number of screens
        for x in range(8):
            #Read the hit status, hit positions and flux
            hit = self.rayData[:,-1,8]
            hitx = self.rayData[:,-2,4]
            hity = self.rayData[:,-2,5]
            normalisedFlux = flux / np.amax(flux)
            #print(normalisedFlux)
            #Create the conditions that the flux is non-zero and the ray hit the screen
            condition = [(flux!=0) & (hit==True) & (delay < 0.25*(x+1)) & (delay>=0.25*x)]
            #Plot a 2d histogram, weighted by flux
            hist = pp.hist2d(hitx[tuple(condition)], hity[tuple(condition)], cmap="viridis", bins=100, norm=colors.LogNorm(vmax=10), weights=normalisedFlux[tuple(condition)])
            #Create axis labels
            #Show and save the figure
            fig = pp.gcf()
            ax = pp.gca()
            ax.set_title("Flux from points on final Screen, observed by Earth, time: " + str(x*0.25) + " to " + str((x+1)*0.25), fontsize=20, y=1.05)
            ax.set_xlabel("x Position (m)", fontsize=20)
            ax.set_ylabel("y Position (m)", fontsize=20)
            ax.tick_params(axis='x', labelsize=14)
            ax.tick_params(axis='y', labelsize=14)
            ax.yaxis.offsetText.set_fontsize(16)
            ax.xaxis.offsetText.set_fontsize(16)
            pp.tight_layout()
            ax.set_aspect(1)
            cbar = fig.colorbar(hist[3], ax=ax)
            cbar.set_label("Normalised flux", fontsize=20)
            cbar.ax.tick_params(labelsize=14)
            figManager = pp.get_current_fig_manager()
            figManager.window.showMaximized()
            pp.show()
            fig.savefig('{}\\plotHits.pdf'.format(self.path))
            pp.close()
    #Plot the time delay distribution
    def plotTime(self):
        delay, flux = self.timeDelay()
        condition = [(flux!=0) & (delay<=5.5)]
        pp.hist(delay[tuple(condition)], bins=50, weights=flux[tuple(condition)], density=True)
        fig = pp.gcf()
        ax = pp.gca()
        ax.set_title("Flux time delay", fontsize=24)
        ax.set_xlabel("Time Delay (s)", fontsize=20)
        ax.set_ylabel("Relative Flux", fontsize=20)
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)
        figManager = pp.get_current_fig_manager()
        figManager.window.showMaximized()
        pp.show()
        fig.savefig('{}\\plotTime.pdf'.format(self.path))
        pp.close()

    #Plot the paths of the first 50 rays
    def plotPaths(self):
        hits, screenPos = self.rayPaths()
        fig = pp.figure()
        ax = pp.axes(projection='3d')
        for i in range(50):
            ax.plot(hits[i,:,0], screenPos, hits[i,:,1])
        pp.show()
        pp.close()
        #fig.savefig('{}\\plotHitsChange.pdf'.format(self.path))

    #Call the plot functions
    def plot(self):
        self.rayData = storage(self.path).loadData()
        self.plotTime()
        self.plotScreenHits()
        #self.plotPaths()
