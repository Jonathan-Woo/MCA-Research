import numpy as np

def rootQuadratic(x, a, b, c):
    '''Returns y for a quadratic equation in root form parameterized by a and roots b, c
    '''
    return a*(x - b)*(x - c)

def vertexQuadratic(x, a, h, k):
    '''Returns y for a quadratic equation in vertex form parameterized by a and vertex (h, k)
    '''
    return a*(x-h)**2+k

def SRCV(y):
    '''Returns SRCV given conductances y
    '''
    sol = 0
    for i in range(len(y)-1):
        sol += 

def NLCV(yLeft, yRight):
    '''Returns NLCV given conductances of left and right branches
    '''
    pass

def ACV(yLeft, yRight):
    '''Returns ACV given conductances of left and right branches
    '''
    pass

def error(aLeft, aRight, pulses):
    #construct data on right and left branches
    xLeft = np.arange(self.pulses)
    yLeft = rootQuadratic(xLeft, aLeft, 0, self.pulses)
    
    #define right quadratic using vertex form 
    #constrain vertex to the vertex of the left quadratic
    #randomize a
    xRight = np.arange(self.pulses, 1001)
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
    def __init__(self, SRCV, NLCV, ACV, pulses):
        self.SRCV = SRCV
        self.NLCV = NLCV
        self.ACV = ACV
        # self.maxConductance = maxConductance
        # self.minConductance = minConductance
        self.pulses = pulses
    def defineSwitchingBehaviour(self):
        '''Defines quadratic switching look up table of conductance vs number of pulses
        '''
        #define left quadratic using root form 
        #constrain left root and right roots
        #randomize a
        xLeft = np.arange(self.pulses)
        aLeft = np.random.random()
        rootLeft = np.random.random()
        yLeft = rootQuadratic(xLeft, aLeft, 0, self.pulses)
        
        #define right quadratic using vertex form 
        #constrain vertex to the vertex of the left quadratic
        #randomize a
        xRight = np.arange(self.pulses, 1001)
        aRight = np.random.random()
        vertexX = self.pulses/2
        vertexY = yLeft[vertexX]
        yRight = vertexQuadratic(xRight, aRight, vertexX, vertexY)
        #truncate yRight to when 0 conductance is reached
        for i in range(len(yRight)):
            if yRight[i] < 0:
                yRight = yRight[:i]
                break
        #truncate xRight to the length of yRight
        xRight = xRight[0:len(yRight)]

        #minimize error function 


    
