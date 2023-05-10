import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import csv

def vertex_quadratic(x, a, h, k):
    '''Returns y for a quadratic equation in vertex form parameterized by a, h,
    and k
    '''
    return a * (x-h)**2 + k

def root_quadratic(x, a, b, c):
    '''Returns y for a quadratic equation in root form parameterized by a, b,
    and c
    '''
    return a*(x-b)*(x-c)

def SRCV(set_data, reset_data, number_of_pulses):
    '''Computes smallest reproducible conductance variation
    '''
    error = 0
    #defined as average distance between adjacent points
    data_1 = set_data[:-1]
    data_2 = set_data[1:]
    error += sum((data_1 - data_2)**2)

    data_1 = reset_data[:-1]
    data_2 = reset_data[1:]
    error += sum((data_1 - data_2)**2)
    
    return error/number_of_pulses

def NLCV(set_data, reset_data, x_switch, number_of_pulses):
    '''Computes non-linearity of conductance variation
    '''
    error = 0
    #compute set branch non-linearity
    s_x = np.linspace(0, x_switch, len(set_data)).reshape(-1,1)
    model = LinearRegression()
    model.fit(s_x, set_data)
    regression_data = model.predict(s_x)
    error += sum((regression_data - set_data)**2)

    #compute reset branch non-linearity
    r_x = np.linspace(x_switch, number_of_pulses, len(reset_data)).reshape(-1,1)
    model = LinearRegression()
    model.fit(r_x, reset_data)
    regression_data = model.predict(r_x)
    error += sum((regression_data - reset_data)**2)

    error /= number_of_pulses
    return error

def ACV(set_data, reset_data, number_of_pulses):
    '''Computes asymmetry of conductance variation
    '''
    #reverse set data
    set_data = set_data[::-1]
    
    #pad shorter data with zeros
    if len(set_data) < len(reset_data):
        set_data = np.append(set_data, np.zeros(len(reset_data) - len(set_data)))
    else:
        reset_data = np.append(reset_data, np.zeros(len(set_data) - len(reset_data)))

    error = sum((set_data - reset_data)**2)/number_of_pulses

    return error

def NWA(switching_data, ideal_switching_data, number_of_pulses):
    '''Computes net write accuracy
    '''
    error = sum((switching_data - ideal_switching_data)**2)/number_of_pulses
    return error

def memristor(number_of_pulses, high_conductance, i):        
    #define SET branch
    #randomly choose between concave up or concave down
    flip = np.random.randint(2)

    #x_switch equation changes because you take the first root for concave down and second root for concave up
    if flip == 0:
        #CONCAVE DOWN
        #choose vertex between 1 and number of pulses for x, greater than max conductance for y
        #compute a given a point and vertex
        #y=a(x-h)^2+k
        s_h = np.random.uniform(number_of_pulses//5, number_of_pulses + number_of_pulses//5)
        s_k = np.random.uniform(high_conductance, high_conductance + high_conductance//5)
        s_a = -s_k/s_h**2
        x_switch = s_h-math.sqrt((high_conductance-s_k)/s_a)
    else:
        #CONCAVE UP
        #choose vertex less than or equal to zero for x, less than or equal to zero for y
        #compute a given a point and vertex
        s_h = np.random.uniform(-number_of_pulses - number_of_pulses//5, -number_of_pulses//5)
        s_k = np.random.uniform(0, -high_conductance//5)
        s_a = -s_k/s_h**2
        x_switch = s_h+math.sqrt((high_conductance-s_k)/s_a)

    #compute x switch
    x_switch = round(x_switch)
    if x_switch == 0 or x_switch == number_of_pulses:
        return 

    ###########################################################################################

    #define RESET branch
    #randomly choose between concave up or concave down
    flip = np.random.randint(2)

    if flip == 0:
        #CONCAVE DOWN
        #choose b sufficiently small to have a vertex on the left of the max conductance
        #y = a(x-b)(x-c)
        r_c = number_of_pulses
        r_b = np.random.uniform(-number_of_pulses//2, 2*x_switch-number_of_pulses)
        try:
            r_a = vertex_quadratic(x_switch, s_a, s_h, s_k)/((x_switch - r_b)*(x_switch - r_c))
        except:
            return
    else:
        #CONCAVE UP
        y_switch = vertex_quadratic(x_switch, s_a, s_h, s_k)
        r_b = x_switch
        r_c = np.random.uniform(2*number_of_pulses - x_switch, 2*number_of_pulses)
        try:
            r_a = -y_switch/((number_of_pulses - r_b)*(number_of_pulses - r_c))
        except:
            return

    ###########################################################################################

    #compute x and y values
    x_data = np.linspace(0,number_of_pulses, number_of_pulses+1)
    set_data = np.zeros(x_switch + 1)
    try:
        reset_data = np.zeros(number_of_pulses - x_switch + 1)
    except:
        return

    set_data = vertex_quadratic(x_data[:x_switch], s_a, s_h, s_k)
    try:
        reset_data = root_quadratic(x_data[x_switch:], r_a, r_b, r_c) + y_switch
    except UnboundLocalError:
        reset_data = root_quadratic(x_data[x_switch:], r_a, r_b, r_c)
    switching_data = np.append(set_data, reset_data)

    if len(set_data) == 0 or len(reset_data) == 0:
        return

    #compute ideal values
    ideal_switch = number_of_pulses//2
    ideal_set = x_data[:ideal_switch] * high_conductance / ideal_switch

    ideal_m = (0 - high_conductance)/(number_of_pulses - ideal_switch)
    ideal_b = high_conductance - ideal_m * ideal_switch
    ideal_reset = x_data[ideal_switch:] * ideal_m + ideal_b
    ideal_switching_data = np.append(ideal_set, ideal_reset)

    plt.figure()
    plt.plot(x_data, switching_data, label='Switching Behaviour')
    plt.plot(x_data, ideal_switching_data, label='Ideal Switching Behaviour')
    plt.legend()
    plt.xlim(0,number_of_pulses)
    plt.ylim(0,high_conductance+0.5)
    plt.savefig('continuous/'+str(i))
    plt.close()

    plt.figure()
    plt.scatter(x_data, switching_data, marker='.', label='Switching Behaviour')
    plt.scatter(x_data, ideal_switching_data, marker='.', label='Ideal Switching Behaviour')
    plt.legend()
    plt.xlim(0,number_of_pulses)
    plt.ylim(0,high_conductance+0.5)
    plt.savefig('scatter/'+str(i))
    plt.close()
    
    #compute errors
    errors = [
        i,
        NWA(switching_data, ideal_switching_data, number_of_pulses),
        SRCV(set_data, reset_data, number_of_pulses), 
        NLCV(set_data, reset_data, x_switch, number_of_pulses),
        ACV(set_data, reset_data, number_of_pulses)
        ]

    return errors
        
if __name__ == '__main__':
    number_of_pulses = 100
    high_conductance = 1
    
    errors = []
    i = 0
    while i < 25:
        val = memristor(number_of_pulses, high_conductance, i)
        if val != None: 
            errors.append(val)
            i += 1

    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Model #','NWA','SRCV', 'NLCV', 'ACV'])

        for error in errors:
            writer.writerow(error)
