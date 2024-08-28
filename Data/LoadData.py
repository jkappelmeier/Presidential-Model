import numpy as np
import csv
import sys
import Config as C
sys.path.insert(1, '../Model')
import Poll
import Geography

# Load in State Data
states = []
with open('../Data/StateFundamentals.csv') as csvfile:
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

            state = Geography.Geography(str(row[0]), 'State', est, float(row[2]), float(row[3]), int(row[4]))
            states.append(state)
        rowCount = rowCount + 1

# Load in polls
polls = []
with open('../Data/Polls.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            geography = str(row[0])
            date = str(row[1])
            result = [float(row[2][:-1]), float(row[3][:-1])]
            pollster = str(row[4])
            sampleSize = int(row[5])
            poll = Poll.Poll(geography, date, result, pollster, sampleSize)
            polls.append(poll)
        rowCount = rowCount + 1


# Load in correlation matrix
cor = np.zeros([len(states), len(states)])
with open('../Data/StateCorrelation.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            cor[rowCount - 1, :] = row[1:]
        rowCount = rowCount + 1
