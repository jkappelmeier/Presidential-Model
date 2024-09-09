import sys
sys.path.append('../')
import Presidential.Geographies.National as National
import Presidential.PresidentialModel as PresidentialModel
import Presidential.LoadData as LoadData
import datetime
import Config as C



# Create National object
nat = National.National('National', C.incAvg, C.incSigma)

# Add State objects
nat.addChildren(LoadData.states)

# Assign to Model
pres = PresidentialModel.PresidentialModel('Presidential Model', nat, LoadData.cor)


# Add polls
pres.addPolls(LoadData.polls)

pres.estimateVote()


# Run simulation
[incAvg, chalAvg, winRate, lossRate, winPopAndLoseEC, winECAndLosePop, simStateVote] = pres.runSimulation(10000)

print('')
print('Electoral College Vote:')
print('    ' + str(C.incCandidate) + ' - Average: ' + str(round(incAvg, 2)) + ' Electoral Votes | Chance of winning: ' + str(round(winRate * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Average: ' + str(round(chalAvg, 2)) + ' Electoral Votes | Chance of winning: ' + str(round(lossRate * 100, 2)) + '%')
print('    Chance of Electoral Vote Tie: ' + str(round((1 - winRate - lossRate) * 100, 2)) + '%')
print('    Chance of ' + str(C.incCandidate) + ' winning the popular vote and losing the Electoral College: ' + str(round(winPopAndLoseEC * 100, 2)) + '%')
print('    Chance of ' + str(C.chalCandidate) + ' winning the popular vote and losing the Electoral College: ' + str(round(winECAndLosePop * 100, 2)) + '%')
print('')
print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.probWin * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.probWin) * 100, 2)) + '%')
print('')
for i in range(len(nat.children)):
    print(str(nat.children[i].name) + ' (' + str(nat.children[i].electoralVotes) + '):')
    print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.children[i].est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.children[i].probWin * 100, 2)) + '%')
    print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.children[i].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.children[i].probWin) * 100, 2)) + '%')
    print('')
    if len(nat.children[i].children) > 0:
        for j in range(len(nat.children[i].children)):
            print('    ' + str(nat.children[i].children[j].name) + ' (' + str(nat.children[i].children[j].electoralVotes) + '):')
            print('        ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.children[i].children[j].est * 100, 2)) + '% | Chance of winning: ' + str(round(nat.children[i].children[j].probWin * 100, 2)) + '%')
            print('        ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.children[i].children[j].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - nat.children[i].children[j].probWin) * 100, 2)) + '%')
            print('')

# %%
