import sys
sys.path.insert(1, '../Data/')
import Config as C
import numpy as np
import Poll
import datetime
from scipy.stats import norm

# This class defines the properties and methods for estimating the vote of this geographic area
class Geography:

    # Constructor for this class
    #
    # Inputs:
    #   name - name of this geography
    #   level - level of geography (National, State, etc)
    #   est - initial estimate
    #   sigma - initial uncertainty
    #   turnoutEst - estimated turnout (# of votes)
    # Output:
    #   Instance of this class
    def __init__(self, name, level, est, sigma, turnoutEst = 0):
        self.name = name
        self.level = level

        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - C.currentDate).days
        self.time = np.arange(t0, tFinal, -1)

        self.est = est
        self.sigma = sigma

        self.fundEst = self.est
        self.fundSigma = self.sigma

        self.polls = []
        self.pollAvg = []
        self.pollSigma = []

        self.turnoutEst = turnoutEst

        self.probWin = 0

        self.parent = []
        self.children = []


    # Add poll(s) to this object
    #
    # Inputs:
    #   geography - Geographic area that was polled
    #   date - Date of poll in format "MM/DD/YYYY"
    #   result - Result as a vector in format [incumbent, challenger]
    #   pollster - Name of pollster
    #   sampleSize - Sample size of poll
    def addPolls(self, poll):
        # If is a list of polls then loop through adding polls
        if isinstance(poll, list):
            for i in range(len(poll)):
                self.addPolls(poll[i])
        else:
            # If geography is same then add poll
            if poll.geography == self.name:
                if len(self.polls) == 0:
                    self.polls.append(poll)
                else:
                    for i in range(len(self.polls)):
                        if (poll.date - self.polls[i].date).days <= 0:
                            self.polls.insert(i, poll)
                            return
                        self.polls.append(poll)
            # If different geography then recursively search through children
            elif len(self.children) > 0:
                for i in self.children:
                    i.addPolls(poll)




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

        x0 = self.fundEst
        p0 = 100000


        # Run Kalman Filter on polls
        for i in range(len(tVec)):

            # Set process noise based on level
            if self.level == 'National':
                qK = C.pollingProcessNoiseNat
            elif self.level == 'State':
                qK = C.pollingProcessNoiseState

            if i == 0:
                xK = x0
                pK = p0
                dt = 0
            else:
                # If is child then adjust polling estimate to account for changes in parent polling average
                if isinstance(self.parent, Geography):
                    natPrev = self.parent.pollAvg[i - 1, 0]
                    natCur = self.parent.pollAvg[i, 0]

                    # Estimate state vote based on previous national polls
                    voteFundInit = []
                    voteTurnout = []
                    for j in range(len(self.parent.children)):
                        voteFundInit.append(self.parent.children[j].fundEst)
                        voteTurnout.append(self.parent.children[j].turnoutEst)
                    voteFundFinal = self.adjustVote(voteFundInit, voteTurnout, natPrev)

                    # Adjust vote of current poling average
                    adjustValue = 0
                    for j in range(len(self.parent.children)):
                        adjustValue = adjustValue + voteTurnout[j] * voteFundFinal[j] * (1 - voteFundFinal[j])
                    adjustValue = sum(voteTurnout) * (natCur - natPrev) / adjustValue

                    xK = xVec[i - 1, 0]
                    xK = 1 / (1 + np.exp(-1 * (np.log(xK / (1 - xK)) + adjustValue)))
                    # Add noise based on noise in parent polling average
                    parentNoise = self.parent.pollSigma[i, 0]**2 + self.parent.pollSigma[i - 1, 0]**2 - 2 * self.parent.pollSigma[i, 0] * self.parent.pollSigma[i - 1, 0]
                    qK = C.pollingProcessNoiseNat + parentNoise
                else:
                    xK = xVec[i - 1, 0]
                    qK = C.pollingProcessNoiseNat
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
        # If has polls then combine polls with fundamentals
        if len(self.polls) > 0:
            self.runPollingAvg()
            if self.level == 'National':
                biasNoise = C.pollingBiasSigmaNat**2
                q = C.pollingProcessNoiseNat
            elif self.level == 'State':
                biasNoise = C.pollingBiasSigmaState**2
                q = C.pollingProcessNoiseState
            pollingNoise = self.pollSigma[-1, 0]**2 + biasNoise + q * self.time[-1]
            self.est = (self.fundEst * pollingNoise + self.pollAvg[-1, 0] * self.fundSigma**2) / (pollingNoise + self.fundSigma**2)
            self.sigma = np.sqrt(pollingNoise * self.fundSigma**2 / (pollingNoise + self.fundSigma**2))

        # Otherwise just use fundamentals
        else:
            self.est = self.fundEst
            self.sigma = self.fundSigma

        # If has children then adjust the fundamentals estimate such that their sum matches the parent fundamentals estimate
        if len(self.children) > 0:
            voteFundInit = []
            voteTurnout = []
            for i in range(len(self.children)):
                voteFundInit.append(self.children[i].fundEst)
                voteTurnout.append(self.children[i].turnoutEst)
            self.turnoutEst = sum(voteTurnout)
            voteFundFinal = self.adjustVote(voteFundInit, voteTurnout, self.fundEst)
            for i in range(len(self.children)):
                self.children[i].fundEst = voteFundFinal[i]

        # Add error from parent geography
        if isinstance(self.parent, Geography):
            self.sigma = np.sqrt(self.sigma**2 + self.parent.sigma**2)


    # Add children to object.
    #
    # Inputs:
    #   child - child object or list of objects
    def addChildren(self, child):
        if isinstance(child, list):
            for i in range(len(child)):
                self.addChildren(child[i])
        else:
            self.children.append(child)
            self.children[-1].parent = self


    # Adjusts the vote based on what the overall vote should be
    #
    # Inputs:
    #   voteInit - Original vote (list)
    #   voteTurnout - Turnout of each geography (list)
    #   voteTotalFinal - Final total vote of all geographies
    # Optional Input:
    #   tol - Tolarance for adjusting vote
    # Output:
    #   voteFinal - FInal vote (list)
    def adjustVote(self, voteInit, voteTurnout, voteTotalFinal, tol = 0.00001):
        sumProduct = sum([a * b for a, b in zip(voteInit, voteTurnout)])
        voteTotalCur = sumProduct / sum(voteTurnout)
        if abs(voteTotalCur / voteTotalFinal - 1) < tol:
            return voteInit
        else:
            diff = np.log(voteTotalFinal / (1 - voteTotalFinal)) - np.log(voteTotalCur / (1 - voteTotalCur))
            voteEstDiff = []
            for i in range(len(voteInit)):
                x = np.log(voteInit[i] / (1 - voteInit[i])) + diff
                voteEstDiff.append(1 / (1 + np.exp(-1 * x)))
            return self.adjustVote(voteEstDiff, voteTurnout, voteTotalFinal)


    # Simulate the eleciton nSamples times
    #
    # Output:
    #   winRate - Percent of times incumbent wins
    def runSimulation(self):
        self.estimateVote()
        winRate = norm.cdf((self.est - 0.5) / self.sigma)
        self.probWin = winRate
        if len(self.children) > 0:
            for i in range(len(self.children)):
                self.children[i].runSimulation()
