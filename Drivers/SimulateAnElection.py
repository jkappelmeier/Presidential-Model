import sys
sys.path.append('../')
import Geography
import National
import PresidentialModel
import LoadData
import datetime
import Config as C


# Create National object
nat = National.National('National', C.incAvg, C.incSigma)

# Add State objects
nat.addChildren(LoadData.states)

# Assign to Model
pres = PresidentialModel.PresidentialModel('Presidential Model', nat, LoadData.cor)


# Add polls
nat.addPolls(LoadData.polls)


# Run simulation
[incAvg, chalAvg, winRate, lossRate, winPopAndLoseEC, winECAndLosePop, simStateVote] = nat.runSimulation(1)
simStateVote = simStateVote[0]
popVote = 0
totVote = 0
for i in range(len(simStateVote)):
    popVote = popVote + simStateVote[i] * nat.children[i].turnoutEst
    totVote = totVote + nat.children[i].turnoutEst

popVote = popVote / totVote

print('')
print('Electoral College Vote:')
print('    ' + str(C.incCandidate) + ': ' + str(round(incAvg, 2)) + ' Electoral Votes')
print('    ' + str(C.chalCandidate) + ': ' + str(round(chalAvg, 2)) + ' Electoral Votes')
print('')
print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(popVote * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - popVote) * 100, 2)) + '%')
print('')
for i in range(len(nat.children)):
    print(str(nat.children[i].name) + ' (' + str(nat.children[i].electoralVote) + '):')
    print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(simStateVote[i] * 100, 2)) + '%')
    print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - simStateVote[i]) * 100, 2)) + '%')
    print('')
    if len(nat.children[i].children) > 0:
        for j in range(len(nat.children[i].children)):
            print('    ' + str(nat.children[i].children[j].name) + ' (' + str(nat.children[i].children[j].electoralVotes) + '):')
            print('        ' + str(C.incCandidate) + ' - Estimate: ' + str(round(nat.children[i].children[j].est * 100, 2)) + '%')
            print('        ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - nat.children[i].children[j].est) * 100, 2)) + '%')
            print('')
# %%
