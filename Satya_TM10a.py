# Modular - Simplest Interesting Model
# Coded by: Satya Malladi
# Sep 13th 2014
from __future__ import print_function
import os
import csv
import random
from gurobipy import*
#PARAMETERS_______________________________________________________________
modstations = ['S1', 'S2']  # Stations for modules
# Demands in each month d[i][j] --- month i, stataion j
with open('meanst.csv', 'rb') as ex:
    d_mean = list(csv.reader(ex, skipinitialspace=True))
    d_mean = [i for i in d_mean if i]
T = 3     # No of periods = decision epochs T periods, T epochs. closing epoch not included
epochs = range(T)
for t in epochs:
    d_mean[t] = [float(i) for i in d_mean[t]]
ms = range(len(modstations))
q = 2
c = [[0,1],[1,0]]    # module shifting cost
l= [2000,2000] # Lost sales penalty
cap = 20    # Module Capacity
n = 5 # Total number of available modules
tm10a = Model("modular")
#VARIABLES_______________________________________________________________
y = {} # For (no. of modules) at station
x = {} # No. of units produced at station 
L = {} # for unfulfilled demand at each station s in period t
for t in epochs:
    for s in ms:
        y[t,s] = tm10a.addVar(vtype = GRB.INTEGER, lb =0, name = 'y'+str(t+1)+"_"+str(s+1))
        x[t,s] = tm10a.addVar(vtype = GRB.INTEGER, lb =0, name = 'x'+str(t+1)+"_"+str(s+1))
        L[t,s] = tm10a.addVar(vtype = GRB.INTEGER, lb =0, name = 'L'+str(t+1)+"_"+str(s+1))
v = {} # For # of modules shifted from i to j station at epoch t 
for t in epochs:
    for i in ms:
        for j in ms:
            v[t,i,j] = tm10a.addVar(vtype = GRB.INTEGER, lb =0, name = 'v'+str(t+1) +"_"+str(i+1)+str(j+1))
tm10a.update()
#CONSTRAINTS______________________________________________________________
k=1  # for numbering constraints
for s in ms:
    for t in range(T):
        tm10a.addConstr(x[t,s] <=cap*y[t,s] ,"c%d" % k) # Demand fulfillment constraints
        k+=1
        tm10a.addConstr(L[t,s]+ x[t,s] >= d_mean[t][s] ,"c%d" % k) # Demand fulfillment constraints
        k+=1
        tm10a.addConstr(v[t,s,s]== 0, "c%d" % k)
        k+=1
    tm10a.addConstr(y[1,s] == y[0,s] - quicksum(v[0,s,i] for i in ms), "c%d" % k) #  System Dynamics Eqn - period 1-2
    k+=1
    for t in range(1,T-1):     
        tm10a.addConstr(y[t+1,s]== y[t,s]-quicksum(v[t,s,i] for i in ms) + quicksum(v[t-1,i,s] for i in ms),"c%d" % k) #  System Dynamics Eqn - period t ,t+1
        k+=1
tm10a.addConstr(quicksum(y[0,s] for s in ms)==n,"c%d" % k) # Use all available modules
k+=1
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _     

#OBJECTIVE________________________________________________________________
cost1 = quicksum(quicksum(q*x[t,s] for s in ms) for t in epochs) # module maintenance cost every period
cost2 = quicksum(quicksum(quicksum(c[i][j]*v[t,i,j] for i in ms)for j in ms) for t in epochs) # module shifting cost 
cost3 = quicksum(quicksum(l[s]*L[t,s] for s in ms)for t in epochs)  # lost sales per period
tm10a.setObjective(cost1+cost2+cost3, GRB.MINIMIZE)
#OPTIMIZING______________________________________________________________
tm10a.optimize()
tm10a.write("tm10a_LP.lp")
sol = open('tm10a_soln.txt','w+')
for v in tm10a.getVars():
    print(v.varName, v.x , file=sol)
print ( "Obj: ", tm10a.objVal, file=sol)
