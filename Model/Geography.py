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
    # Optional Inputs:
    #   turnoutEst - estimated turnout (# of votes)
    #   electoralVote - number of electoral votes
    #   currentDate - current date
    # Output:
    #   Instance of this class
    def __init__(self, name, level, est, sigma, turnoutEst = 0, electoralVote = 0, currentDate = C.currentDate):
        self.name = name
        self.level = level
        
        self.currentDate = currentDate
        
        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - self.currentDate).days
        self.time = np.arange(t0, tFinal, -1)

        self.est = est
        self.sigma = sigma

        self.fundEst = self.est
        self.fundSigma = self.sigma

        self.polls = []
        self.pollAvg = []
        self.pollSigma = []

        if level == 'National':
            self.pollingBiasSigma = C.pollingBiasSigmaNat
            self.pollingProcessNoise = C.pollingProcessNoiseNat
        elif level == 'State':
            self.pollingBiasSigma = C.pollingBiasSigmaState
            self.pollingProcessNoise = C.pollingProcessNoiseState

        self.turnoutEst = turnoutEst
        self.electoralVote = electoralVote
        self.correlation = []

        self.probWin = 0
        self.covariance = []

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
            if poll.geography == self.name and (self.currentDate - poll.date).days >= 0:
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
            qK = self.pollingProcessNoise

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
        
        # National vote est
        if len(self.polls) > 0:
            self.runPollingAvg()
            biasNoise = self.pollingBiasSigma**2
            q =  self.pollingProcessNoise
            pollingNoise = self.pollSigma[-1, 0]**2 + biasNoise + q * self.time[-1]

            self.est = (self.fundEst * pollingNoise + self.pollAvg[-1, 0] * self.fundSigma**2) / (pollingNoise + self.fundSigma**2)
            self.sigma = np.sqrt(pollingNoise * self.fundSigma**2 / (pollingNoise + self.fundSigma**2))
        winRate = norm.cdf((self.est - 0.5) / self.sigma)
        self.probWin = winRate

        # If has children then adjust the fundamentals estimate such that their sum matches the parent fundamentals estimate
        if len(self.children) > 0:

            # Get State-Level fundamentals data
            stateFundEst = []
            stateFundSigma = []
            stateTurnout = []
            for i in range(len(self.children)):
                stateFundEst.append(self.children[i].fundEst)
                stateFundSigma.append(self.children[i].sigma)
                stateTurnout.append(self.children[i].turnoutEst)

            # Adjust State-Fundamentals and run polling averages
            self.turnoutEst = sum(stateTurnout)
            stateFundEst = self.adjustVote(stateFundEst, stateTurnout, self.fundEst)

            statePollingEst = []
            statePollingSigma = []
            statePollingBiasAndProcessSigma = []
            for i in range(len(self.children)):
                self.children[i].fundEst = stateFundEst[i]

                self.children[i].runPollingAvg()
                statePollingEst.append(self.children[i].pollAvg[-1, 0])
                statePollingSigma.append(self.children[i].pollSigma[-1, 0])
                statePollingBiasAndProcessSigma.append(np.sqrt(self.children[i].pollingBiasSigma**2 + self.children[i].pollingProcessNoise * self.time[-1]))


            # State-level fundamentals estimate and covariance
            stateFundEst = np.transpose(np.matrix(stateFundEst))
            stateFundCovariance = np.multiply(np.transpose(np.matrix(stateFundSigma)) * np.matrix(stateFundSigma), self.correlation)

            # State-level polling estimate and covariance
            statePollingEst = np.transpose(np.matrix(statePollingEst))
            statePollingCovariance = np.multiply(np.matrix(np.identity(len(self.children))), np.transpose(np.matrix(statePollingSigma)) * np.matrix(statePollingSigma))
            statePollingCovarianceTotal = statePollingCovariance + np.multiply(np.transpose(np.matrix(statePollingBiasAndProcessSigma)) * np.matrix(statePollingBiasAndProcessSigma), self.correlation)

            # Combine state-level fundamentals and polling data
            y = statePollingEst - stateFundEst
            S = stateFundCovariance + statePollingCovarianceTotal
            K = stateFundCovariance * np.linalg.inv(S)
            stateFinalEst = stateFundEst + K * y
            stateFinalCovariance = (np.matrix(np.identity(len(self.children))) - K) * stateFundCovariance

            # Add national error
            stateFinalCovariance = stateFinalCovariance + np.matrix(np.ones([len(self.children), len(self.children)])) * self.sigma**2

            # Assign values to state estimates
            self.covariance = stateFinalCovariance
            for i in range(len(self.children)):
                self.children[i].est = stateFinalEst[i, 0]
                self.children[i].sigma = np.sqrt(stateFinalCovariance[i, i])
                winRate = norm.cdf((self.children[i].est - 0.5) / self.children[i].sigma)
                self.children[i].probWin = winRate

            # Adjusted popular vote estimate based on state estimates
            phi = np.matrix(stateTurnout) / self.turnoutEst
            self.est = (phi * stateFinalEst)[0, 0]
            self.sigma = np.sqrt((phi * self.covariance * np.transpose(phi))[0, 0])
            winRate = norm.cdf((self.est - 0.5) / self.sigma)
            self.probWin = winRate


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
            self.children[-1].currentDate = self.currentDate
            self.children[-1].time = self.time


    # Adjusts the vote based on what the overall vote should be
    #
    # Inputs:
    #   voteInit - Original vote (list)
    #   voteTurnout - Turnout of each geography (list)
    #   voteTotalFinal - Final total vote of all geographies
    # Optional Input:
    #   tol - Tolarance for adjusting vote
    # Output:
    #   voteFinal - Final vote (list)
    def adjustVote(self, voteInit, voteTurnout, voteTotalFinal, tol = 0.00001):
        sumProduct = sum([a * b for a, b in zip(voteInit, voteTurnout)])
        voteTotalCur = sumProduct / sum(voteTurnout)
        if abs(voteTotalCur / voteTotalFinal - 1) < tol:
            return voteInit
        else:
            diff = self.convertFromPercentage(voteTotalFinal) - self.convertFromPercentage(voteTotalCur)
            voteEstDiff = []
            for i in range(len(voteInit)):
                z = self.convertFromPercentage(voteInit[i]) + diff
                voteEstDiff.append(self.convertToPercentage(z))
            return self.adjustVote(voteEstDiff, voteTurnout, voteTotalFinal)


    # Simulate the eleciton nSamples times
    #
    # Input:
    #   nRuns - Number of times to simulate election
    # Output:
    #   incAvg - Average electoral vote of incumbent
    #   chalAvg - Average electoral vote of challenger
    #   winRate - Percent of times incumbent wins
    #   lossRate - Percent of times incumbent loses
    #   simStateVoteList - List of all the state results generated
    def runSimulation(self, nRuns):
        self.estimateVote()

        if len(self.children) > 0:

            # Collect data
            stateEst = []
            stateTurnout = []
            stateElectoralVotes = []
            for i in self.children:
                stateEst.append(i.est)
                stateTurnout.append(i.turnoutEst)
                stateElectoralVotes.append(i.electoralVote)
            stateEst = np.array(stateEst)
            stateTurnout = np.array(stateTurnout)
            stateElectoralVotes = np.array(stateElectoralVotes)

            nWins = 0
            nLoses = 0
            nECInc = []
            nECChal = []
            winPopAndLoseEC = 0
            winECAndLosePop = 0
            simStateVoteList = []
            for i in range(nRuns):
                simStateVote = np.random.multivariate_normal(stateEst, self.covariance)
                popVote = np.average(simStateVote, weights = stateTurnout)
                simStateWin = [1 if a_ > 0.5 else 0 for a_ in simStateVote]
                electoralVotesWon = np.dot(simStateWin, stateElectoralVotes)
                electoralVotesLost = sum(stateElectoralVotes) - electoralVotesWon
                nECInc.append(electoralVotesWon)
                nECChal.append(electoralVotesLost)
                if electoralVotesWon > electoralVotesLost:
                    nWins = nWins + 1
                    if popVote < 0.5:
                        winECAndLosePop = winECAndLosePop + 1
                elif electoralVotesWon < electoralVotesLost:
                    nLoses = nLoses + 1
                    if popVote > 0.5:
                        winPopAndLoseEC = winPopAndLoseEC + 1
                simStateVoteList.append(simStateVote)

                if i % 100 == 0:
                    print(str(i) + ' / ' + str(nRuns) + ' Runs completed')

            winRate = nWins /  nRuns
            lossRate = nLoses / nRuns
            incAvg = sum(nECInc) / nRuns
            chalAvg = sum(nECChal) / nRuns
            winPopAndLoseECChance = winPopAndLoseEC / nRuns
            winECAndLosePopChance = winECAndLosePop / nRuns

            return [incAvg, chalAvg, winRate, lossRate, winPopAndLoseECChance, winECAndLosePopChance, simStateVoteList]


### Percentage to Noramlized format conversion methods. The purpose of the
# normalized format is transform values from the percentage format to a space
# where values can be negative and greater than 1. Then by converting back this
# prevents the negative percentages or percentages beyond 1.

    # Convert from a percentage to a normalized format
    #
    # Input:
    #   x - Value in percentage form
    # Output:
    #   z - Value in normalized form
    def convertFromPercentage(self, x):
        z = np.log(x / (1 - x))
        return z

    # Convert from a normalized format to a percentage
    #
    # Input:
    #   z - Value in normalized format
    # Output:
    #   x - Value in percentage form
    def convertToPercentage(self, z):
        x = 1 / (1 + np.exp(-1 * z))
        return x


    # Convert uncertainty from percentage form to normalized form
    #
    # Input:
    #   x - Value in percentage form
    #   xSigma - Uncertainty in percentage form
    # Output:
    #   zSigma - Uncertainty in normalized form
    def convertSigmaFromPercentage(self, x, xSigma):
        zSigma = xSigma / (x * (1 - x))
        return zSigma


    # Convert Uncertainty from normalized form to percentage
    #
    # Input:
    #   z - Value in normalized form
    #   zSigma - Uncertainty in normalized form
    # Output:
    #   xSigma - Uncertainty in percentage form
    def convertSigmaToPercentage(self, z, zSigma):
        xSigma = zSigma * np.exp(-1 * z) / (1 + np.exp(-1 * z))**2
        return xSigma
