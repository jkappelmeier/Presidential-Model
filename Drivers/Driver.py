import sys
sys.path.append('../')
import Presidential.Geographies.National as National
import Presidential.PresidentialModel as PresidentialModel
import Presidential.LoadData as LoadData
from Presidential.Geographies.CongressionalDistrict import *
import datetime
import Config as C
import csv



# Create National object
nat = National.National('National', C.incAvg, C.incSigma)

# Add State objects
nat.addChildren(LoadData.states)

# Assign to Model
pres = PresidentialModel.PresidentialModel('Presidential Model', nat, LoadData.cor, currentDate = datetime.date(2024,9,18))


# Add polls
pres.addPolls(LoadData.polls)



# Run simulation
[incAvg, chalAvg, winRate, lossRate, winPopAndLoseEC, winECAndLosePop, tippingPoint, simStateVote] = pres.runSimulation(10000)

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
for i in range(len(pres.allGeographies)-1):
    if isinstance(pres.allGeographies[i+1],CongressionalDistrict):
        print('    ' + str(pres.allGeographies[i+1].name) + ' (' + str(pres.allGeographies[i+1].electoralVotes) + ' - ' + str(round(tippingPoint[i]*100,2))+'% Tipping Point Chance):')
        print('        ' + str(C.incCandidate) + ' - Estimate: ' + str(round(pres.allGeographies[i+1].est * 100, 2)) + '% | Chance of winning: ' + str(round(pres.allGeographies[i+1].probWin * 100, 2)) + '%')
        print('        ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - pres.allGeographies[i+1].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - pres.allGeographies[i+1].probWin) * 100, 2)) + '%')
        print('')
    else:
        print(str(pres.allGeographies[i+1].name) + ' (' + str(pres.allGeographies[i+1].electoralVotes) + ' - ' + str(round(tippingPoint[i]*100,2))+'% Tipping Point Chance):')
        print('    ' + str(C.incCandidate) + ' - Estimate: ' + str(round(pres.allGeographies[i+1].est * 100, 2)) + '% | Chance of winning: ' + str(round(pres.allGeographies[i+1].probWin * 100, 2)) + '%')
        print('    ' + str(C.chalCandidate) + ' - Estimate: ' + str(round((1 - pres.allGeographies[i+1].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - pres.allGeographies[i+1].probWin) * 100, 2)) + '%')
        print('')


# All Sims
with open('simulations.csv', 'w', newline = '') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    for row in simStateVote:
        spamwriter.writerow(row)
