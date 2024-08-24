import datetime
import numpy as np
# This provides all constants/config values used by model
# Note that data comes from elections from 1972 - 2020


### Race Specific Strings

incParty = 'D' # Incumbent Party
incCandidate = 'Kamala Harris'
chalCandidate = 'Donald Trump'

currentDate = datetime.date.today() # Current Date
electionDate = datetime.date(2024,11,5) # Election Date
startDate =  datetime.date(2024,7,22) # Campaign Start Date


### National-Level Fundamental Consants

incAvg = 0.5142 # Average incumbent 2-party vote share
incSigma = 0.0501 # Standard deviation in incumbent 2-party vote share


### National-Level Polling Constants

pollingSigmaSF = 0.04 # Average polling error at N = 1000
pollingProcessNoiseNat = 7.15e-6 # Polling process noise per day for national polls
pollingBiasSigmaNat = np.sqrt(0.000617) # National Polling Bias Noise
