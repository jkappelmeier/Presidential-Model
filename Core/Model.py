import datetime
import numpy as np
import Config as C
from scipy.stats import norm
import Core.logitConversions as logitConversions

# This model contains the properties and methods for the overall model
class Model:

    # Constructor for this class
    #
    # Inputs:
    #   name - name of this object
    #   geography - Head of geography class tree
    #   cor - correlation matrix to be used (must match lengths of all children of geography)
    #   currentDate - current date to run Model
    # Output:
    #   Instance of this class
    def __init__(self, name, geography, cor, currentDate = C.currentDate):
        self.name = name
        self.geographyHead = geography
        self.correlation = cor
        self.geographyHead.model = self

        self.currentDate = currentDate
        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - self.currentDate).days
        self.time = np.arange(t0, tFinal, -1)

        [children, parentToStateIndices] = self.getChildren(geography)
        self.stateGeographies = children # The "states" of the model are all
        # children of geographies. Note that states in this context are not
        # states in states of the US. "states" is merely refering the elements
        # of the model so a "state" can be a congressional district for example.

        self.parentToStateIndices = parentToStateIndices # This contains the
        # indices that relate the geographies with children to the state vector

        # Collect all fundamental estimates, uncertainty and turnout of states
        # into lists
        stateFundEst = []
        stateFundSigma = []
        stateTurnout = []
        for i in range(len(self.stateGeographies)):
            stateFundEst.append(self.stateGeographies[i].fundEst)
            stateFundSigma.append(self.stateGeographies[i].fundSigma)
            stateTurnout.append(self.stateGeographies[i].turnoutEst)
        self.stateFundEst = stateFundEst
        self.stateFundSigma = stateFundSigma
        self.stateTurnout = stateTurnout

        # Final Estimate
        self.stateEst = []
        self.covariance = []

    # Estimate the vote for all states of the model.
    #
    def estimateVote(self):

        # Run all polling averages
        self.runAllPollingAverages(self.geographyHead)

        # National vote est
        biasNoise = self.geographyHead.pollingBiasSigma**2
        q =  self.geographyHead.pollingProcessNoise
        pollingNoise = self.geographyHead.pollSigma[-1, 0]**2 + biasNoise + q * self.time[-1]

        natSigma = np.sqrt(pollingNoise * self.geographyHead.fundSigma**2 / (pollingNoise + self.geographyHead.fundSigma**2))

        # If has children then adjust the fundamentals estimate such that their
        # sum matches the parent fundamentals estimate
        if len(self.stateGeographies) > 1:

            # Adjust State-Fundamentals and run polling averages
            stateFundEst = logitConversions.adjustVote(self.stateFundEst, self.stateTurnout, self.geographyHead.fundEst)

            statePollingEst = []
            statePollingSigma = []
            statePollingBiasAndProcessSigma = []
            for i in range(len(self.stateGeographies)):
                self.stateGeographies[i].fundEst = stateFundEst[i]
                statePollingEst.append(self.stateGeographies[i].pollAvg[-1, 0])
                statePollingSigma.append(self.stateGeographies[i].pollSigma[-1, 0])
                statePollingBiasAndProcessSigma.append(np.sqrt(self.stateGeographies[i].pollingBiasSigma**2 + self.stateGeographies[i].pollingProcessNoise * self.time[-1]))


            # State-level fundamentals estimate and covariance
            stateFundEst = np.transpose(np.matrix(stateFundEst))
            stateFundCovariance = np.multiply(np.transpose(np.matrix(self.stateFundSigma)) * np.matrix(self.stateFundSigma), self.correlation)

            # State-level polling estimate and covariance
            statePollingEst = np.transpose(np.matrix(statePollingEst))
            statePollingCovariance = np.multiply(np.matrix(np.identity(len(self.stateGeographies))), np.transpose(np.matrix(statePollingSigma)) * np.matrix(statePollingSigma))
            statePollingCovarianceTotal = statePollingCovariance + np.multiply(np.transpose(np.matrix(statePollingBiasAndProcessSigma)) * np.matrix(statePollingBiasAndProcessSigma), self.correlation)

            # Combine state-level fundamentals and polling data
            y = statePollingEst - stateFundEst
            S = stateFundCovariance + statePollingCovarianceTotal
            K = stateFundCovariance * np.linalg.inv(S)
            stateFinalEst = stateFundEst + K * y
            stateFinalCovariance = (np.matrix(np.identity(len(self.stateGeographies))) - K) * stateFundCovariance

            # Add national error
            stateFinalCovariance = stateFinalCovariance + np.matrix(np.ones([len(self.stateGeographies), len(self.stateGeographies)])) * natSigma**2

            # Final State Estimate and Covariance
            self.stateEst = stateFinalEst
            self.covariance = stateFinalCovariance

            # Assign values to state estimates
            self.covariance = stateFinalCovariance
            for i in range(len(self.stateGeographies)):
                self.stateGeographies[i].est = stateFinalEst[i, 0]
                self.stateGeographies[i].sigma = np.sqrt(stateFinalCovariance[i, i])
                winRate = norm.cdf((self.stateGeographies[i].est - 0.5) / self.stateGeographies[i].sigma)
                self.stateGeographies[i].probWin = winRate

            # Adjust popular vote estimates in all geographies with children
            for i in range(len(self.parentToStateIndices)):
                parent = self.parentToStateIndices[i][0]
                indices = self.parentToStateIndices[i][1]
                childrenTurnout = np.array(self.stateTurnout)[indices]
                childrenEst = np.matrix(self.stateEst[indices])
                childrenCov = np.matrix(self.covariance[indices][:, indices])

                phi = np.matrix(childrenTurnout) / sum(childrenTurnout)

                est = (phi * childrenEst)[0, 0]
                sigma = np.sqrt((phi * childrenCov * np.transpose(phi))[0, 0])
                winRate = norm.cdf((est - 0.5) / sigma)
                parent.est = est
                parent.sigma = sigma
                parent.probWin = winRate


    # Please implement this method to simulate the election nRuns times.
    def runSimulation(self, nRuns):
        self.estimateVote()
        return []


    # Get all children (and children of children recursively) as well as relation between and parents to the list of children
    #
    # Input:
    #   geography - Head of geography object to search
    # Output:
    #   children - List of children geographies
    #   parentToStateIndices - List of relations between parent geographies and indices of children in the final state vector
    def getChildren(self, geography, children = [], parentToStateIndices = []):
        geography.model = self
        if len(geography.children) == 0:
            children.append(geography)
        else:
            initLen = len(children)
            for i in range(len(geography.children)):
                [children, parentToStateIndices] = self.getChildren(geography.children[i], children, parentToStateIndices)
            finalLen = len(children)
            parentToStateIndices.append([geography, np.arange(initLen, finalLen, 1)])
        return [children, parentToStateIndices]


    # Runs all polling averages of the model
    #
    # geography - geography to run polling average on
    def runAllPollingAverages(self, geography):
        geography.runPollingAvg()
        if len(geography.children) > 0:
            for i in range(len(geography.children)):
                self.runAllPollingAverages(geography.children[i])
