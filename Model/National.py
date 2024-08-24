import sys
sys.path.insert(1, '../Data/')
import Config as C
import numpy as np
import Poll
import datetime
from scipy.stats import norm

# This class defines the properties and methods for the national vote and
# enviornment
class National:

    # Constructor for this class
    #
    # Output:
    #   Instance of this class
    def __init__(self):
        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - C.currentDate).days
        self.time = np.arange(t0, tFinal, -1)

        self.est = C.incAvg
        self.sigma = C.incSigma

        self.fundEst = self.est
        self.fundSigma = self.sigma

        self.polls = []
        self.pollAvg = []
        self.pollSigma = []

        self.probWin = 0


    # Add poll(s) to this object
    #
    # Inputs:
    #   geography - Geographic area that was polled
    #   date - Date of poll in format "MM/DD/YYYY"
    #   result - Result as a vector in format [incumbent, challenger]
    #   pollster - Name of pollster
    #   sampleSize - Sample size of poll
    def addPoll(self, poll):
        if isinstance(poll, list):
            for i in range(len(poll)):
                self.addPoll(poll[i])
        else:
            if len(self.polls) == 0:
                self.polls.append(poll)
            else:
                for i in range(len(self.polls)):
                    if (poll.date - self.polls[i].date).days <= 0:
                        self.polls.insert(i, poll)
                        return
                    self.polls.append(poll)



    # Estimate the polling average for the national enviornment using a Kalman
    # Filter approach
    #
    # Outputs:
    #   xVec - List of all candidate estimates over time
    #   pVec - List of all associated noises
    #   tVec - List of time to election from start of poll
    def runPollingAvg(self):
        tVec = self.time
        xVec = np.zeros([len(tVec), 1])
        pVec = np.zeros([len(tVec), 1])

        availFlagVec = np.zeros([len(tVec), 1])
        zVec = np.zeros([len(tVec), 1])
        rVec = np.zeros([len(tVec), 1])
        for i in range(len(tVec)):
            for j in range(len(self.polls)):
                if tVec[i] == (C.electionDate - self.polls[j].date).days:
                    if availFlagVec[i, 0] == 0:
                        availFlagVec[i, 0] = 1
                        zVec[i, 0] = self.polls[j].result
                        rVec[i, 0] = self.polls[j].sigma**2
                    else:
                        zVec[i, 0] = (zVec[i, 0] * self.polls[j].sigma**2 + self.polls[j].result * rVec[i, 0]) / (rVec[i, 0] + self.polls[j].sigma**2)
                        rVec[i, 0] = (1 - rVec[i, 0] / (rVec[i, 0] + self.polls[j].sigma**2)) * rVec[i, 0]

        x0 = self.est
        p0 = 100000
        qK = C.pollingProcessNoiseNat

        # Run Kalman Filter on polls
        for i in range(len(tVec)):

            if i == 0:
                xK = x0
                pK = p0
                dt = 0
            else:
                xK = xVec[i - 1, 0]
                pK = pVec[i - 1, 0]
                dt = tVec[i - 1] - tVec[i]

            pK = pK + qK * dt

            if availFlagVec[i, 0] == 1:

                # Measurement Update
                z = zVec[i, 0]
                R = rVec[i, 0]
                y = z - xK

                H = 1
                S = H * pK * H + R
                K = pK * H / S

                xKp1 = xK + K * y
                pKp1 = (1 - K * H) * pK
            else:
                xKp1 = xK
                pKp1 = pK

            xVec[i, 0] = xKp1
            pVec[i, 0] = pKp1

        self.pollAvg = xVec
        self.pollSigma = np.sqrt(pVec)


    # Estimate the vote for the current geographic object
    #
    def estimateVote(self):
        if len(self.polls) > 0:
            self.runPollingAvg()
            pollingNoise = self.pollSigma[-1, 0]**2 + C.pollingBiasSigmaNat**2 + C.pollingProcessNoiseNat * self.time[-1]
            self.est = (self.fundEst * pollingNoise + self.pollAvg[-1, 0] * self.fundSigma**2) / (pollingNoise + self.fundSigma**2)
            self.sigma = np.sqrt(pollingNoise * self.fundSigma**2 / (pollingNoise + self.fundSigma**2))


    # Simulate the eleciton nSamples times
    #
    # Output:
    #   winRate - Percent of times incumbent wins
    def runSimulation(self):
        self.estimateVote()
        winRate = norm.cdf((self.est - 0.5) / self.sigma)
        self.probWin = winRate
