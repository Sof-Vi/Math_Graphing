import numpy as np
import matplotlib.pyplot as plt 
#imports both mathplot and numpy which are neccesary for making the graph

x = [200, 200, 200, 200, 200, 200, 200]
#Uses the proton run log data where the x axis represents the energy. 
y = [1.29677E-11, 2.22845E-11, 4.51678E-11, 1.04395E-11, 8.63505E-11, 2.60134E-11, 2.33483E-11]
#Uses the proton run log data where the y axis represent the FTF

plt.scatter(x, y, c= 'blue',  marker= 'H', s= 67)
#controls the parameters for each thing, where c = color, marker = shape of point, s = size
plt.show()
#Show where the marker should be

#This is useful for data points since they are not treated like functions instead like individuals variables 
