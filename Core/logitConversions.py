import numpy as np
# This file contains all functions relating to converting between logits and
# percentages.

# The logit converts a percentage to a continuous value between -infinity and
# +infinity, allowing any additive or subtractive operation on this value to not
# result in the percentage going beyond [0, 1] when the logit is converted back.


# Adjusts the vote based on what the overall vote should be..
#
# Inputs:
#   voteInit - Original vote (list)
#   voteTurnout - Turnout of each geography (list)
#   voteTotalFinal - Final total vote of all geographies
# Optional Input:
#   tol - Tolarance for adjusting vote
# Output:
#   voteFinal - Final vote (list)
def adjustVote(voteInit, voteTurnout, voteTotalFinal, tol = 0.00001):
    sumProduct = sum([a * b for a, b in zip(voteInit, voteTurnout)])
    voteTotalCur = sumProduct / sum(voteTurnout)
    if abs(voteTotalCur / voteTotalFinal - 1) < tol:
        return voteInit
    else:
        diff = convertToLogit(voteTotalFinal) - convertToLogit(voteTotalCur)
        voteEstDiff = []
        for i in range(len(voteInit)):
            z = convertToLogit(voteInit[i]) + diff
            voteEstDiff.append(convertToPercentage(z))
        return adjustVote(voteEstDiff, voteTurnout, voteTotalFinal)


# Convert from a percentage to a logit format
#
# Input:
#   x - Value in percentage form
# Output:
#   z - Value in logit form
def convertToLogit(x):
    z = np.log(x / (1 - x))
    return z


# Convert from logit form to percentage
#
# Input:
#   z - Value in logit form
# Output:
#   x - Value in percentage form
def convertToPercentage(z):
    x = 1 / (1 + np.exp(-1 * z))
    return x


# Convert uncertainty from percentage form to logit form
#
# Input:
#   x - Value in percentage form
#   xSigma - Uncertainty in percentage form
# Output:
#   zSigma - Uncertainty in logit form
def convertSigmaFromLogit(x, xSigma):
    zSigma = xSigma / (x * (1 - x))
    return zSigma


# Convert Uncertainty from logit form to percentage
#
# Input:
#   z - Value in logit form
#   zSigma - Uncertainty in logit form
# Output:
#   xSigma - Uncertainty in percentage form
def convertSigmaToPercentage(z, zSigma):
    xSigma = zSigma * np.exp(-1 * z) / (1 + np.exp(-1 * z))**2
    return xSigma
