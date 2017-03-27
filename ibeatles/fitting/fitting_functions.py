import numpy as np
import math
import numpy as np
from scipy.special import erf

        
def basic_fit(t, d_spacing, alpha, sigma, a1, a2):

    term2 = erf(-((t-d_spacing)/(sigma * math.sqrt(2))) + sigma/alpha)
    term1 = np.exp((t-d_spacing)/alpha + (sigma*sigma)/(2*alpha*alpha))
    term0 = erf(-((t-d_spacing)/(sigma*math.sqrt(2))))
    
    y = a1 + a2 * (term0 - (term1 * term2))   
    
    return y
    
def advanced_fit(t, d_spacing, alpha, sigma, a1, a2, a5, a6):
        
    term0 = a2 * (t - a6)
    term1 = ((a5 - a2) / 2) * (t - a6)
    term3 = erf(-((t-d_spacing)/(sigma * math.sqrt(2))))
    term4 = np.exp(-((t-d_spacing)/alpha) + ((sigma*sigma)/(2*alpha*alpha)))
    term5 = erf(-((t-d_spacing)/(sigma * math.sqrt(2))) + sigma/alpha)
    
    y = a1 + term0
    
