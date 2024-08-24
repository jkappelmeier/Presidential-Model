import National
import sys
sys.path.insert(1, '../Data/')
import Config as C
import LoadData

# Create National object
nat = National.National()

# Add polls
nat.addPoll(LoadData.natPolls)

# Run simulation
nat.runSimulation()

print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.probWin * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Esimate: ' + str(round((1 - nat.est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.probWin) * 100, 2)) + '%')
