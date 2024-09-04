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
        for i in self.stateGeographies:
            stateElectoralVotes.append(i.electoralVotes)
        stateElectoralVotes = np.array(stateElectoralVotes)
        stateEst = np.array(np.transpose(self.stateEst))[0]

        nWins = 0
        nLoses = 0
        nECInc = []
        nECChal = []
        winPopAndLoseEC = 0
        winECAndLosePop = 0
        simStateVoteList = []
        for i in range(nRuns):
            simStateVote = np.random.multivariate_normal(stateEst, self.covariance)
            popVote = np.average(simStateVote, weights = self.stateTurnout)
            simStateWin = [1 if a_ > 0.5 else 0 for a_ in simStateVote]
            electoralVotesWon = np.dot(simStateWin, stateElectoralVotes)
            electoralVotesLost = sum(stateElectoralVotes) - electoralVotesWon

            # Electoral votes for Maine and Nebraska
            for j in range(len(self.parentToStateIndices)):
                geography = self.parentToStateIndices[j][0]
                indices = self.parentToStateIndices[j][1]
                if geography.name == 'Maine' or geography.name == 'Nebraska':
                    simCDVote = simStateVote[indices]
                    cdTurnout = np.array(self.stateTurnout)[indices]
                    statePopVote = np.average(simCDVote, weights = cdTurnout)
                    simStateVote = np.append(simStateVote,statePopVote)
                    if statePopVote > 0.5:
                        electoralVotesWon = electoralVotesWon + geography.electoralVotes
                    else:
                        electoralVotesLost = electoralVotesLost + geography.electoralVotes
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


            if i % 100 == 0:
                print(str(i) + ' / ' + str(nRuns) + ' Runs completed')

        winRate = nWins /  nRuns
        lossRate = nLoses / nRuns
        incAvg = sum(nECInc) / nRuns
        chalAvg = sum(nECChal) / nRuns
        winPopAndLoseECChance = winPopAndLoseEC / nRuns
        winECAndLosePopChance = winECAndLosePop / nRuns

        return [incAvg, chalAvg, winRate, lossRate, winPopAndLoseECChance, winECAndLosePopChance, simStateVoteList]
