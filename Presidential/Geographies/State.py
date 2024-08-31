import Core.Geography as Geography
import Config as C

# This class represents the data for a state
class State(Geography.Geography):

    # Constructor for this class:
    #
    # Inputs:
    #   name - name for this object
    #   fundEst - fundamentals estimate of vote
    #   fundSigma - uncertainty in fundEst
    #   turnoutEst - total vote estimate
    #   electoralVotes - number of electoral votes
    # Optional Inputs:
    #   pollingBiasSigma - final uncertainty in the bias for national polls
    #   pollingProcessNoise - variance gained every day from when a poll was
    #                         taken
    def __init__(self, name, fundEst, fundSigma, turnoutEst, electoralVotes, pollingBiasSigma = C.pollingBiasSigmaState, pollingProcessNoise = C.pollingProcessNoiseState):

        # Call superclass
        Geography.Geography.__init__(self, name)

        self.fundEst = fundEst
        self.fundSigma = fundSigma
        self.pollingBiasSigma = pollingBiasSigma
        self.pollingProcessNoise = pollingProcessNoise
        self.turnoutEst = turnoutEst
        self.electoralVotes = electoralVotes
