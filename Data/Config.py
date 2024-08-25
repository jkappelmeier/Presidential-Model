import datetime
import numpy as np
# This provides all constants/config values used by model
# Note that data comes from elections from 1972 - 2020


### Race Specific Strings

incParty = 'D' # Incumbent Party
incCandidate = 'Kamala Harris'
chalCandidate = 'Donald Trump'

incPresHomeState = 'California'
chalPresHomeState = 'Florida'
incVPHomeState = 'Minnesota'
chalVPHomeState = 'Ohio'

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


### State-Level Fundamental Constants
presHomeStateBoost = 0.1055 # This is not a percentage but rather in "normalized format"
# To convert from a normalized value to percent -> 1 / (1 + exp(-1*x)). Note that this value
# is a CHANGE in the normalized value not the normalized value itself.
vpHomeStateBoost = 0.0302
