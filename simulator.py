import numpy as np
from scipy.optimize import curve_fit 
from random import normalvariate

def normalChoice(lst, mean=None, std=None):
    '''Returns sampled element from list list with normal distribution
    parameterized by mean mean and standard deviation std
    '''
    #choose mean to be the middle of the list if not provided
    if mean == None:
        mean = len(lst)//2

    if std == None:
        #CHOOSE DEFAULT STD
        std = len(lst)//2 - len(lst)//4

    while True:
        index = int(np.random.normal(mean, std) + 0.5)
        #check that sampled index is within bounds
        if 0 <= index < len(lst):
            return lst[index]

def quadratic(x, a, b, c):
    '''Returns y for a quadratic equation in standard form parameterized by a,
    b, and c
    '''
    return np.multiply(a, x**2) + np.multiply(b, x) + c

def linear(x, m, b):
    '''Returns y for a linear equation
    '''
    return np.multiply(m,x)+b

def SRCV(nPulses):
    '''Returns SRCV given conductances y
    '''
    return 1/nPulses

def NLCV(yLeft, yRight):
    '''Returns NLCV given conductances of left and right branches
    '''
    #for left branch
    xL = [*range(len(yLeft))]
    params = curve_fit(linear, xL, yLeft)
    mL = params[0][0]
    bL = params[0][1]
    yL = linear(xL, mL, bL)
    
    #for right branch
    xR = [*range(len(yLeft) - 1,len(yLeft) + len(yRight))]
    params = curve_fit(linear, xR, yRight)
    mR = params[0][0]
    bR = params[0][1]
    yR = linear(xR, mR, bR)

    return (abs(yLeft - yL) + abs(yRight - yR))/(abs(yL - yLeft[0])+abs(yR - yRight[0]))

def ACV(yLeft, yRight):
    '''Returns ACV given conductances of left and right branches
    '''
    #for k >= m/2
    if len(yLeft) >= len(yRight):
        denom = 0
        for i in range(len(yLeft)):
            if i >= len(yLeft) - len(yRight):
                #add difference between yLeft and complement position of yRight
                error += abs(yLeft[i] - yRight[len(yLeft) - i - 1])
            else:
                error += yLeft[i]
            denom += yLeft[i] - yLeft[0]

        return error/denom

def error(aLeft, aRight, pulses):
    #construct data on right and left branches
    xLeft = np.arange(pulses)
    yLeft = rootQuadratic(xLeft, aLeft, 0, self.pulses)
    
    #define right quadratic using vertex form 
    #constrain vertex to the vertex of the left quadratic
    #randomize a
    xRight = np.arange(pulses, 1001)
    vertexX = pulses/2
    vertexY = yLeft[vertexX]
    yRight = vertexQuadratic(xRight, aRight, vertexX, vertexY)
    #truncate yRight to when 0 conductance is reached
    for i in range(len(yRight)):
        if yRight[i] < 0:
            yRight = yRight[:i]
            break
    #truncate xRight to the length of yRight
    xRight = xRight[0:len(yRight)]

    #must remove one element for SRCV to avoid overlapped elements
    return SRCV(yLeft[:-1] + yRight) + NLCV(yLeft, yRight) + ACV(yLeft, yRight)

class memristor:
    def __init__(self, SRCV, NLCV, ACV, maxConductance, minConductance, pulses):
        self.SRCV = SRCV
        self.NLCV = NLCV
        self.ACV = ACV
        self.maxConductance = maxConductance
        self.minConductance = minConductance 
        self.pulses = pulses
    def defineSwitchingBehaviour(self):
        '''Defines quadratic switching look up table of conductance vs number of pulses
        '''
        #choose number of pulses before changing from SET to RESET by sampling
        #from normal distribution
        pulsesLst = [*range(self.pulses)]
        halfSwitching = normalChoice(pulsesLst)

        #SET goes up to and including half switching
        pulsesSet = np.arange(halfSwitching + 1)
        #RESET starts at half switching and stops at self.pulses
        pulsesReset = np.arange(halfSwitching, self.pulses + 1)

        #define conductance values 
        '''The math seems complicated by it's built off of the following model:
        https://www.desmos.com/calculator/1byoj4kgwm

        Since the two quadratic equations are subject to constraints, they can
        ultimately be written as functions of aSet and aReset alone.
        '''
        #initialize random aSet and aReset with constraints
        aSet = np.random.random() * ((-self.maxConductance + self.minConductance)/halfSwitching**2)
        conductanceSet = quadratic(pulsesSet, aSet, (self.maxConductance - self.minConductance - aSet*halfSwitching**2)/k, self.minConductance)

        aReset = np.random.random() * (-self.minConductance + self.maxConductance)/(-(halfSwitching-self.pulses)**2)
        conductanceSet = quadratic(pulsesReset, aReset, (self.minConductance - aReset*self.pulses**2 - self.maxConductance + aReset*halfSwitching**2)/(self.pulses - halfSwitching), self.maxConductance - aReset*halfSwitching**2 - ((self.minConductance - aReset*self.pulses**2 - self.maxConductance + aReset*halfSwitching)/(self.pulses - halfSwitching))*halfSwitching)
        
        #optimize aSet and aReset
        