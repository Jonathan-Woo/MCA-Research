'''
Stuck-Fault (Quiescent Voltage Method)
1. Read to store conductance values off chip
2. Write +w to all cells
3. Calculate reference current
4. Apply test voltage to GROUP of rows
5. Write -w to RRAM cells
6. Discrepency between reference and measured current indicates stuck-fault
7. Repeat process the other way by applying test voltages to columns
8. Cross reference detected rows and columns to determine cells SA0
9. Repeat process for SA1 detection by writing -w first then +w

Conductance vs Switching Pulse Number Graph
1. Switch to LRS
2. Apply SET programming pulse
3. Read conductance
4. Repeat until conductance[i] - condutance[i-1] <= e where e is a pre-defined constant
5. Apply RESET programming pulse
4. Read conductance
5. Repeat until conductance[i] <= conductance[0]
'''
