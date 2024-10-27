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
startDate =  datetime.date(2024,7,21) # Campaign Start Date


### National-Level Fundamental Consants

incAvg = 0.5142 # Average incumbent 2-party vote share
incSigma = 0.0501 # Standard deviation in incumbent 2-party vote share


### National-Level Polling Constants

pollingSigmaSF = 0.0566 # Average polling error at N = 1000
pollingProcessNoiseNat = 7.75e-6 # Polling process noise per day for national polls
pollingBiasSigmaNat = np.sqrt(0.000617) # National Polling Bias Noise


### State-Level Fundamental Constants
presHomeStateBoost = 0.1424 # This is not a percentage but rather in logit form.
vpHomeStateBoost = 0.0391


### State-Level Polling Constants

pollingProcessNoiseState = 6.57e-6
pollingBiasSigmaState = np.sqrt(5.23e-4)


### congressional District-Level Polling Constants
pollingProcessNoiseCD = 6.57e-6
pollingBiasSigmaCD = np.sqrt(5.23e-4)
