import numpy as np
import csv
import sys
import Config as C
sys.path.insert(1, '../Model')
import Poll
import Geography

# Load in State Data
states = []
with open('../Data/StateData.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            if C.incParty == 'D':
                est = float(row[1])
            elif C.incParty == 'R':
                est = 1 - float(row[1])

            # Adjust for home state advantages
            if str(row[0]) == C.incPresHomeState:
                est = 1 / (1 + np.exp(-1 * (np.log(est / (1 - est)) + C.presHomeStateBoost)))
            if str(row[0]) == C.chalPresHomeState:
                est = 1 / (1 + np.exp(-1 * (np.log(est / (1 - est)) - C.presHomeStateBoost)))
            if str(row[0]) == C.incVPHomeState:
                est = 1 / (1 + np.exp(-1 * (np.log(est / (1 - est)) + C.vpHomeStateBoost)))
            if str(row[0]) == C.chalVPHomeState:
                est = 1 / (1 + np.exp(-1 * (np.log(est / (1 - est)) - C.vpHomeStateBoost)))

            state = Geography.Geography(str(row[0]), est, float(row[2]), float(row[3]))
            states.append(state)
        rowCount = rowCount + 1

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
