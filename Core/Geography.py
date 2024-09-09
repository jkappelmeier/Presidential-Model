import numpy as np
import Core.Poll as Poll
import datetime


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
