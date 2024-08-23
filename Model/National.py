import sys
sys.path.insert(1, '../Data/')
import Config as C
import numpy as np

# This class defines the properties and methods for the national vote and
# enviornment
class National:

    # Constructor for this class
    #
    # Output:
    #   Instance of this class
    def __init__(self):
        self.est = C.incAvg
        self.estSigma = C.incSigma


    # Simulate the eleciton nSamples times
    #
    # Input:
    #   nSamples - Number of times to run simulation
    # Output:
    #   winRate - Percent of times incumbent wins
    def runSimulation(self, nSamples):

        nWins = 0
        for i in range(nSamples):
            natVote = np.random.normal(self.est, self.estSigma, 1)
            if natVote > 0.5:
                nWins = nWins + 1

        winRate = nWins / nSamples
        return winRate
