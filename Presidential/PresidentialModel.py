import Core.Model as Model
import Config as C
import numpy as np

# Implements the Model superclass for the presidential election
class PresidentialModel(Model.Model):

    # Constructor for this class
    #
    # Inputs:
    #   name - name of this object
    #   geography - Head of geography class tree
    #   cor - correlation matrix to be used (must match lengths of all children of geography)
    #   currentDate - current date to run Model
    # Output:
    #   Instance of this class
    def __init__(self, name, geography, cor, currentDate = C.currentDate):

        # Call superclass
        Model.Model.__init__(self, name, geography, cor, currentDate)


    # Simulate the eleciton nSamples times
    #
    # Input:
    #   nRuns - Number of times to simulate election
    # Output:
    #   incAvg - Average electoral vote of incumbent
    #   chalAvg - Average electoral vote of challenger
    #   winRate - Percent of times incumbent wins
    #   lossRate - Percent of times incumbent loses
    #   simStateVoteList - List of all the state results generated
    def runSimulation(self, nRuns):
        self.estimateVote()

        # Collect data
        stateElectoralVotes = []
        for i in self.allGeographies:
            if i.name != self.geographyHead.name:
                stateElectoralVotes.append(i.electoralVotes)
        stateElectoralVotes = np.array(stateElectoralVotes)
        stateEst = np.array(np.transpose(self.finalEst))[0]

        nWins = 0
        nLoses = 0
        nECInc = []
        nECChal = []
        winPopAndLoseEC = 0
        winECAndLosePop = 0
        simStateVoteList = []
        tippingPoint = np.zeros(len(stateEst)-1)
        for i in range(nRuns):
            simVote = np.random.multivariate_normal(stateEst, self.finalCov)
            popVote = simVote[0]
            simStateVote = simVote[1:]
            simStateWin = [1 if a_ > 0.5 else 0 for a_ in simStateVote]
            electoralVotesWon = np.dot(simStateWin, stateElectoralVotes)
            electoralVotesLost = sum(stateElectoralVotes) - electoralVotesWon
            nECInc.append(electoralVotesWon)
            nECChal.append(electoralVotesLost)

            if electoralVotesWon > electoralVotesLost:
                nWins = nWins + 1
                if popVote < 0.5:
                    winECAndLosePop = winECAndLosePop + 1
            elif electoralVotesWon < electoralVotesLost:
                nLoses = nLoses + 1
                if popVote > 0.5:
                    winPopAndLoseEC = winPopAndLoseEC + 1
            simStateVoteList.append(simStateVote)

            # Find Tipping Point State
            sortedIndices = np.argsort(simStateVote)
            ec = 0
            count = 0
            while ec < 269:
                ec = ec + stateElectoralVotes[sortedIndices[count]]
                count = count + 1
            tippingPoint[sortedIndices[count-1]] = tippingPoint[sortedIndices[count-1]] + 1
            if self.allGeographies[sortedIndices[count-1]+1].name == 'Illinois':
                a = 1
            #print(self.allGeographies[sorted_indices[count-1]+1].name)


            if i % 100 == 0:
                print(str(i) + ' / ' + str(nRuns) + ' Runs completed')

        #for i in range(len(tippingPoint)):
        #    print(self.allGeographies[i+1].name +', '+str(round(simStateVote[i]*100,2))+'%')
        winRate = nWins /  nRuns
        lossRate = nLoses / nRuns
        incAvg = sum(nECInc) / nRuns
        chalAvg = sum(nECChal) / nRuns
        winPopAndLoseECChance = winPopAndLoseEC / nRuns
        winECAndLosePopChance = winECAndLosePop / nRuns
        tippingPoint = tippingPoint / np.sum(tippingPoint)

        return [incAvg, chalAvg, winRate, lossRate, winPopAndLoseECChance, winECAndLosePopChance, tippingPoint, simStateVoteList]
