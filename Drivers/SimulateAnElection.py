import sys
sys.path.append('../')
import Presidential.Geographies.National as National
import Presidential.PresidentialModel as PresidentialModel
import Presidential.LoadData as LoadData
from Presidential.Geographies.CongressionalDistrict import *
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
[incAvg, chalAvg, winRate, lossRate, winPopAndLoseEC, winECAndLosePop, simStateVote] = pres.runSimulation(1)
simStateVote = simStateVote[0]
popVote = 0
totVote = 0
for i in range(len(pres.stateGeographies)):
    popVote = popVote + simStateVote[i] * pres.stateGeographies[i].turnoutEst
    totVote = totVote + pres.stateGeographies[i].turnoutEst

popVote = popVote / totVote

print('')
print('Electoral College Vote:')
print('    ' + str(C.incCandidate) + ' - Average: ' + str(round(incAvg, 2)) + ' Electoral Votes')
print('    ' + str(C.chalCandidate) + ' - Average: ' + str(round(chalAvg, 2)) + ' Electoral Votes')
print('')
print('Popular Vote:')
print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(popVote * 100, 2)) + '%')
print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - popVote) * 100, 2)) + '%')
print('')
stateCDSplitCount = 0
mostRecentCDSplit = ''
for i in range(len(pres.stateGeographies)):
    if isinstance(pres.stateGeographies[i],CongressionalDistrict) and pres.stateGeographies[i].parent.name != mostRecentCDSplit:
        print(str(pres.stateGeographies[i].parent.name) + ' (' + str(pres.stateGeographies[i].parent.electoralVotes) + '):')
        print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(simStateVote[len(pres.stateGeographies) + stateCDSplitCount] * 100, 2)) + '%')
        print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - simStateVote[len(pres.stateGeographies) + stateCDSplitCount]) * 100, 2)) + '%')
        print('')
        stateCDSplitCount = stateCDSplitCount + 1
        mostRecentCDSplit = pres.stateGeographies[i].parent.name
    if isinstance(pres.stateGeographies[i],CongressionalDistrict):
        print('    ' + str(pres.stateGeographies[i].name) + ' (' + str(pres.stateGeographies[i].electoralVotes) + '):')
        print('        ' + str(C.incCandidate) + ' - Estimate: ' + str(round(simStateVote[i] * 100, 2)) + '%')
        print('        ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - simStateVote[i]) * 100, 2)) + '%')
        print('')
    else:
        print(str(pres.stateGeographies[i].name) + ' (' + str(pres.stateGeographies[i].electoralVotes) + '):')
        print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(simStateVote[i] * 100, 2)) + '%')
        print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - simStateVote[i]) * 100, 2)) + '%')
        print('')
# %%
