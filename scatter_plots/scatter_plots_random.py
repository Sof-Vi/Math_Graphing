import numpy as np
import matplotlib.pyplot as plt 
#imports both mathplot and numpy which are neccesary for making the graph

x = np.random.rand(15) 
#Selects the points graphed on the x axis can be specified as well
y = np.random.rand(15)
#Selects the points graphed on the y axis can be specified as well

plt.scatter(x,y, c= 'blue',  marker= 'H', s= 67)
#controls the parameters for each thing, where c = color, marker = shape of point, s = size
plt.show()
#Show where the marker should be

#This is useful for data points since they are not treated like functions instead like individuals variables 
