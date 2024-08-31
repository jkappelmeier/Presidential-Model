import numpy as np
import Core.Poll as Poll
import datetime
import Config as C
import Core.logitConversions as logitConversions


# This is an abstract class that defines the properties and methods for
# estimating the vote of a geographic area
class Geography:

    # Constructor for this class
    #
    # Inputs:
    #   name - name of this geography
    # Output:
    #   Instance of this class
    def __init__(self, name):
        self.name = name

        # Abstract properties that must be implemented
        self.fundEst = 0
        self.fundSigma = 0
        self.pollingBiasSigma = 0
        self.pollingProcessNoise = 0
        self.turnoutEst = 0

        # Relations to other objects
        self.parent = []
        self.children = []
        self.model = []

        # Polling data
        self.polls = []
        self.pollAvg = []
        self.pollSigma = []

        # Final Estimate
        self.est = 0
        self.sigma = 0
        self.probWin = 0




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
            if poll.geography == self.name and (self.model.currentDate - poll.date).days >= 0:
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
        tVec = self.model.time
        xVec = np.zeros([len(tVec), 1])
        pVec = np.zeros([len(tVec), 1])

        # Organize polling "measurements" into vectors
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

        # Inital uncertainty that is very large... uncertainty of fundamentals
        # is incorporating later in estimateVote().
        x0 = self.fundEst
        p0 = 100000


        # Run Kalman Filter on polls
        for i in range(len(tVec)):

            if i == 0:
                xK = x0
                pK = p0
                qK = self.pollingProcessNoise
                dt = 0
            else:
                # If is child then adjust polling estimate to account for changes in parent polling average
                [xK, qK] = self.adjustPolls(xVec[i - 1, 0], tVec[i])
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


    # This method is used for adjusting polling the case where the parent
    # geography has polling movement. For example if a poll hasn't happened in a
    # while in a state, but the national polling has moved by 10 points in one
    # direction, adjust acordingly.
    #
    # Input:
    #   xKPrev - Previous estimate of poll
    #   t - Current time
    # Outputs:
    #   xK - New estimate at current time
    #   qK - Process noise, accounting for current process noise and uncertainty
    #        in the polling movement of the parent class
    def adjustPolls(self, xKPrev, t):

        # Get index of current time
        i = np.where(self.model.time == t)[0]
        # If geography has parent geography search for polling movement in that class
        if isinstance(self.parent, Geography):
            # If parent has no polls at current time look for movement in parent of parent polls
            if self.parent.pollSigma[i - 1, 0] > 100:
                [xK, qK] = self.parent.adjustPolls(xKPrev, t)
                qK = qK + self.pollingProcessNoise
            else:
                parentPrev = self.parent.pollAvg[i - 1, 0]
                parentCur = self.parent.pollAvg[i, 0]

                # Estimate state vote based on previous polls of parent geography
                voteFundInit = []
                voteTurnout = []
                for j in range(len(self.parent.children)):
                    voteFundInit.append(self.parent.children[j].fundEst)
                    voteTurnout.append(self.parent.children[j].turnoutEst)
                voteFundFinal = logitConversions.adjustVote(voteFundInit, voteTurnout, parentPrev)

                # Adjust vote of current polling average
                adjustValue = 0
                for j in range(len(self.parent.children)):
                    adjustValue = adjustValue + voteTurnout[j] * voteFundFinal[j] * (1 - voteFundFinal[j])
                adjustValue = sum(voteTurnout) * (parentCur - parentPrev) / adjustValue

                xK = 1 / (1 + np.exp(-1 * (np.log(xKPrev / (1 - xKPrev)) + adjustValue)))

                # Add noise based on noise in parent polling average
                rho = self.parent.pollSigma[i, 0] / np.sqrt(self.parent.pollSigma[i, 0]**2 + self.parent.pollingProcessNoise) # Correlation between i and i-1
                parentNoise = self.parent.pollSigma[i, 0]**2 + self.parent.pollSigma[i - 1, 0]**2 - 2 * self.parent.pollSigma[i, 0] * self.parent.pollSigma[i - 1, 0] * rho
                qK = self.pollingProcessNoise + parentNoise
        # Otherwise just use previous polling value
        else:
            xK = xKPrev
            qK = self.pollingProcessNoise
        return [xK, qK]


    # Add children to object.
    #
    # Inputs:
    #   child - child object or list of objects
    def addChildren(self, child):
        if isinstance(child, list):
            # Sum votes from children
            totVotes = 0
            for i in range(len(child)):
                self.addChildren(child[i])
                totVotes = totVotes + child[i].turnoutEst
            self.turnoutEst = totVotes
        else:
            self.children.append(child)
            self.children[-1].parent = self
            self.children[-1].model = self.model
