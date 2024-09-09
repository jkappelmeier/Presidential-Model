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
        self.allGeographies = self.getAllGeographies(self.geographyHead)
        self.stateGeographies = []

        self.currentDate = currentDate
        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - self.currentDate).days
        self.time = np.arange(t0, tFinal-1, -1)

        # State Vector Fundamentals
        self.xFund = []
        self.xCovarianceFund = []
        self.xTurnoutEst = []

        # Polling Vector
        self.zPolls = []
        self.rPolls = []
        self.availFlags = []

        # State Vector Polling Estimates
        self.xPolling = []
        self.xCovariancePolling = []

        # Polling Vector
        self.zPolls = []
        self.rPolls = []
        self.availFlags = []

        # Final Estimate
        self.stateEst = []
        self.covariance = []

        self.initializeModel()


    # Initialize the fundamentals of the model with information from the
    # geographies
    def initializeModel(self):

        ### Initialize Fundamentals:

        # Set up mapping between state vector and full geography vector
        [stateChildren, parentToStateIndices] = self.getChildren(self.geographyHead)
        self.stateGeographies = stateChildren
        self.parentToStateIndices = parentToStateIndices
        H = np.zeros([len(self.allGeographies), len(stateChildren)])
        for i in range(len(self.allGeographies)):
            for k in range(len(parentToStateIndices)):
                if self.allGeographies[i].name == parentToStateIndices[k][0].name:
                    vec = np.zeros([1,len(stateChildren)])
                    s = 0
                    for l in parentToStateIndices[k][1]:
                        s = s + stateChildren[l].turnoutEst
                        vec[0,l] = stateChildren[l].turnoutEst
                    H[i,:] = vec/s

            for j in range(len(stateChildren)):
                if self.allGeographies[i].name == stateChildren[j].name:
                    H[i,j] = 1
                    
        self.stateGeoToAllGeoMap = H


        stateFundEst = []
        stateFundSigma = []
        stateTurnout = []
        for i in range(len(stateChildren)):
            stateFundEst.append(stateChildren[i].fundEst)
            stateFundSigma.append(stateChildren[i].fundSigma)
            stateTurnout.append(stateChildren[i].turnoutEst)

        # Adjust to estimate of national vote
        stateFundEst = logitConversions.adjustVote(stateFundEst, stateTurnout, self.geographyHead.fundEst)

        self.xFund = np.insert(np.array(stateFundEst) - self.geographyHead.fundEst, 0, self.geographyHead.fundEst)
        rho = np.zeros([len(self.xFund),len(self.xFund)])
        rho[1:,1:] = self.correlation
        rho[0,0] = 1
        stateFundSigma = np.insert(np.array(stateFundSigma),0,self.geographyHead.fundSigma)
        self.xCovarianceFund = np.multiply(np.transpose(np.matrix(stateFundSigma)) * np.matrix(stateFundSigma), np.matrix(rho))
        self.xTurnoutEst = np.array(stateTurnout)


        self.zPolls = np.zeros([len(self.time),len(self.allGeographies)])
        self.rPolls = np.zeros([len(self.time),len(self.allGeographies)])
        self.availFlags = np.zeros([len(self.time),len(self.allGeographies)],dtype=bool)

        self.xPolling = np.zeros([len(self.time),len(self.xFund)])
        self.xCovariancePolling = np.zeros([len(self.time),len(self.xFund),len(self.xFund)])

        self.stateEst = np.zeros(len(self.xFund))
        self.covariance = np.zeros([len(self.stateEst),len(self.stateEst)])


    # Add polls to the model
    #
    # Input:
    #   polls - List of polls to add to model
    def addPolls(self, polls):

        self.geographyHead.addPolls(polls)

        ### Initialize Polling measurements:
        for i in range(len(self.allGeographies)):
            for j in range(len(self.time)):
                for k in range(len(self.allGeographies[i].polls)):
                    if self.time[j] == (C.electionDate - self.allGeographies[i].polls[k].date).days:
                        if self.availFlags[j, i] == 0:
                            self.availFlags[j, i] = 1
                            self.zPolls[j, i] = self.allGeographies[i].polls[k].result
                            self.rPolls[j, i] = self.allGeographies[i].polls[k].sigma**2
                        else:
                            self.zPolls[j, i] = (self.zPolls[j, i] * self.allGeographies[i].polls[k].sigma**2 + self.allGeographies[i].polls[k].result * self.rPolls[j, i]) / (self.rPolls[j, i] + self.allGeographies[i].polls[k].sigma**2)
                            self.rPolls[j, i] = (1 - self.rPolls[j, i] / (self.rPolls[j, i] + self.allGeographies[i].polls[k].sigma**2)) * self.rPolls[j, i]


    # Run the polling average for all geography areas concurently with covariance
    def runPollingAvg(self):

        N = len(self.xFund)
        m = len(self.allGeographies)
        x0 = self.xFund
        p0 = 100000 * np.identity(N)

        # Set up process noise and bias
        rho = np.zeros([N,N])
        rho[1:,1:] = self.correlation
        rho[0,0] = 1
        qVec = np.zeros(N)
        biasVec = np.zeros(N)
        for i in range(N):
            if i == 0:
                qVec[i] = np.sqrt(self.geographyHead.pollingProcessNoise)
                biasVec[i] = self.geographyHead.pollingBiasSigma
            else:
                qVec[i] = np.sqrt(self.stateGeographies[i-1].pollingProcessNoise)
                biasVec[i] = self.stateGeographies[i-1].pollingBiasSigma
        qVec = np.matrix(qVec)
        biasVec = np.matrix(biasVec)
        Q = np.multiply(np.transpose(qVec)*qVec, rho)
        bias = np.multiply(np.transpose(biasVec)*biasVec, rho)

        # Set up measurement noise
        R = np.zeros([len(self.time), m, m])
        for i in range(len(self.time)):
            for j in range(m):
                R[i,j,j] = self.rPolls[i,j]

        # Set up sensitivity matrix
        H = np.zeros([m,N])
        H[:, 0] = np.ones([m])
        H[1:,1:] = self.stateGeoToAllGeoMap[1:,:]

        # Run Kalman Filter
        xK = np.transpose(np.matrix(x0))
        pK = p0
        for i in range(len(self.time)):
            pK = pK + Q

            if np.sum(self.availFlags[i, :]) > 0:
                zK = self.zPolls[i, self.availFlags[i, :]]
                zK = np.transpose(np.matrix(zK))
                hK = H[self.availFlags[i,:],:]
                hK = np.matrix(hK)

                rK = R[i, :, :]
                rK = rK[self.availFlags[i,:], :]
                rK = rK[:, self.availFlags[i, :]]
                rK = np.matrix(rK)

                y = zK - hK * xK
                S = hK * pK * np.transpose(hK) + rK
                K = pK * np.transpose(hK) * np.linalg.inv(S)

                xK = xK + K * y
                pK = (np.identity(N) - K * hK) * pK

            self.xPolling[i, :] = np.array(np.transpose(xK))
            self.xCovariancePolling[i, :, :] = np.array(pK + bias + self.time[i]*Q)



    # Estimate the vote for all states of the model.
    #
    def estimateVote(self):

        # Run all polling averages
        self.runPollingAvg()

        # Combine Fundamentals and Polling
        x = np.transpose(np.matrix(self.xFund))
        z = np.transpose(np.matrix(self.xPolling[-1,:]))
        y = z - x
        S = self.xCovarianceFund + np.matrix(self.xCovariancePolling[-1,:,:])
        K = self.xCovarianceFund * np.linalg.inv(S)

        xEst = x + K * y
        pEst = (np.identity(len(self.xFund)) - K) * self.xCovarianceFund

        # Add national vote to state PVIs
        H = np.matrix(np.ones([len(self.xFund)-1,len(self.xFund)]))
        H[:,1:] = np.identity(len(self.xFund)-1)

        xEst = H * xEst
        pEst = H * pEst * np.transpose(H)

        self.stateEst = xEst
        self.covariance = pEst
        
        self.finalEst = self.stateGeoToAllGeoMap*xEst
        self.finalCov = self.stateGeoToAllGeoMap*pEst*np.transpose(self.stateGeoToAllGeoMap)
        
        # Assign estimates
        for i in range(len(self.allGeographies)):
            self.allGeographies[i].est = self.finalEst[i, 0]
            self.allGeographies[i].sigma = np.sqrt(self.finalCov[i,i])
            winRate = norm.cdf((self.allGeographies[i].est - 0.5) / self.allGeographies[i].sigma)
            self.allGeographies[i].probWin = winRate
            

    # Please implement this method to simulate the election nRuns times.
    #
    # Inputs:
    #   nRuns - number of times to run election
    def runSimulation(self, nRuns):
        self.estimateVote()
        return []


    # Get all children (and children of children recursively)
    #
    # Input:
    #   geography - Head of geography object to search
    # Output:
    #   children - List of children geographies
    #   parentToStateIndices - List of relations between parent geographies and indices of children in the final state vector
    def getAllGeographies(self, geography, children = []):
        geography.model = self
        children.append(geography)
        if len(geography.children) > 0:
            for i in range(len(geography.children)):
                children = self.getAllGeographies(geography.children[i], children)
        return children


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
