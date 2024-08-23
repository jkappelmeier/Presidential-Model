import National
import sys
sys.path.insert(1, '../Data/')
import Config as C

# Create National object
nat = National.National()

# Run simulation 10000 times
winRate = nat.runSimulation(10000)

print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.est * 100, 2)) + '% | Chance of winning: ' + str(round(winRate * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Esimate: ' + str(round((1 - nat.est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - winRate) * 100, 2)) + '%')
