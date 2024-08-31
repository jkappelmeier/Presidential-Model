import Core.Geography as Geography
import Config as C

# This class represents the data for the national enviornment
class National(Geography.Geography):

    # Constructor for this class:
    #
    # Inputs:
    #   name - name for this object
    #   fundEst - fundamentals estimate of vote
    #   fundSigma - uncertainty in fundEst
    # Optional Inputs:
    #   pollingBiasSigma - final uncertainty in the bias for national polls
    #   pollingProcessNoise - variance gained every day from when a poll was
    #                         taken
    #   turnoutEst - total vote estimate (will be overwritten by child
    #                geographies)
    def __init__(self, name, fundEst, fundSigma, pollingBiasSigma = C.pollingBiasSigmaNat, pollingProcessNoise = C.pollingProcessNoiseNat, turnoutEst = 0):

        # Call superclass
        Geography.Geography.__init__(self, name)

        self.fundEst = fundEst
        self.fundSigma = fundSigma
        self.pollingBiasSigma = pollingBiasSigma
        self.pollingProcessNoise = pollingProcessNoise
        self.turnoutEst = turnoutEst
