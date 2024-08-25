import Geography
import sys
sys.path.insert(1, '../Data/')
import Config as C
import LoadData

# Create National object
nat = Geography.Geography('National', 'National', C.incAvg, C.incSigma)

# Add State objects
nat.addChildren(LoadData.states)

# Add correlation matrix
nat.correlation = LoadData.cor

# Add polls
nat.addPolls(LoadData.polls)


# Run simulation
[incAvg, chalAvg, winRate, lossRate, simStateVote] = nat.runSimulation(10000)

print('Electoral College Vote:')
print('    ' + str(C.incCandidate) + ' - Average: ' + str(round(incAvg, 2)) + ' Electoral Votes | Chance of winning: ' + str(round(winRate * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Average: ' + str(round(chalAvg, 2)) + ' Electoral Votes | Chance of winning: ' + str(round(lossRate * 100, 2)) + '%')
print('    Chance of Electoral Vote Tie: ' + str(round((1 - winRate - lossRate) * 100, 2)) + '%')
print('')
print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.probWin * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.probWin) * 100, 2)) + '%')
print('')
for i in range(len(nat.children)):
    print(str(nat.children[i].name) + ':')
    print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.children[i].est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.children[i].probWin * 100, 2)) + '%')
    print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.children[i].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.children[i].probWin) * 100, 2)) + '%')
    print('')
