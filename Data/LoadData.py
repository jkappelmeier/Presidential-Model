import numpy as np
import csv
import sys
sys.path.insert(1, '../Model')
import Poll

# Load in National Polls
natPollsData = []
natPolls = []
with open('../Data/Polling/National.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            natPollsData.append(row)
        rowCount = rowCount + 1

for i in range(len(natPollsData)):
    geography = str(natPollsData[i][0])
    date = str(natPollsData[i][1])
    result = [float(natPollsData[i][2][:-1]), float(natPollsData[i][3][:-1])]
    pollster = str(natPollsData[i][4])
    sampleSize = int(natPollsData[i][5])
    poll = Poll.Poll(geography, date, result, pollster, sampleSize)
    natPolls.append(poll)
