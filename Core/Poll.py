import datetime
import numpy as np
import sys
sys.path.insert(0, '../Data/')
import Config as C


# Class that contains information regarding a poll
class Poll:

    # Constructor for this class
    #
    # Inputs:
    #   geography - Geographic area that was polled
    #   date - Date of poll in format "MM/DD/YYYY"
    #   result - Result as a vector in format [incumbent, challenger]
    #   pollster - Name of pollster
    #   sampleSize - Sample size of poll
    # Output:
    #   Instance of this class
    def __init__(self, geography, date, result, pollster = '', sampleSize = 1000):
        self.geography = geography
        dateArray = date.split("/")
        self.date = datetime.date(int(dateArray[2]), int(dateArray[0]), int(dateArray[1]))
        self.result = result[0] / sum(result)
        self.name = pollster
        self.N = sampleSize
        self.sigma = C.pollingSigmaSF * np.sqrt(1000 / sampleSize)
