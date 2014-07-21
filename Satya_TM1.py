# Modular Example 2 stage stochastic program

import os
from gurobipy import*

tm1 = Model("modular")
#PARAMETERS
ret = ['A', 'B', 'C']       # Retailers/Warehouses buying from the Modular Supply Units
modstations = ['S1', 'S2']  # Stations for modules
srio = ['low', 'exp', 'hi']  # Scenarios
d_sc =[[200,240, 160],[250, 300, 200],[300,360,240]]  # Demands under different scenarios
trf = [[7,8, 12],[11, 7,4]]   # Transportation / logistics cost from the two stations to different customers
setup = [14, 15]  # Setup costs at each station
cap = 40     # Module Capacity
ps = [0.3,0.5,0.2]
rt = range(len(ret))
ms = range(len(modstations))
snrio = range(len(srio))
#VARIABLES
x = []              # For capacity/ (no. of modules) allocation to different stations 
for c in ms:
    x.append(tm1.addVar(vtype = GRB.INTEGER, name = "x%d" % (c+1)))
y = {}              # For amount of demand at retailer j filled by station i in time period t yij_t
for s in ms: 
    for r in rt:
        for t in snrio:
            y[s,r,t] = tm1.addVar(vtype = GRB.CONTINUOUS, ub = 1, name = 'y'+str(s+1)+str(r+1)+"_"+str(t+1))
            # yijt can be integral if each retailer must be served by only one station.
tm1.update()
ey = {}  # Expected i-j flow station to retailer
ed = {}  # Expected Demand at retailer
for s in ms:
    ed[r] = quicksum(ps[t]*d_sc[t][r] for t in snrio)
    for r in rt:
        ey[s,r] = quicksum(ps[t]*y[s,r,t] for t in snrio)
#OBJECTIVE
stg1cost = quicksum(setup[f]*x[f] for f in ms)
stg2cost = quicksum(quicksum(trf[s][r]*ey[s,r] for s in ms) for r in rt)
tm1.setObjective(stg1cost+stg2cost)
#CONSTRAINTS
k=1  # for numbering constraints
for t in snrio:
    tm1.addConstr(cap*quicksum(x[i] for i in ms) >= quicksum(d_sc[t][r] for r in rt), "c%d" % k)   # Demand should be satisfied always constraint
    k+=1                                                                    # Alternately can include penalty for demand unfulfilled
for t in snrio:
    for i in ms:
        tm1.addConstr(cap*x[i] >= quicksum(d_sc[t][r]*y[i,r,t] for r in rt), "c%d" % k)   # Capacity must be geq than the demand fulfilled by each station
        k+=1                                                                    
for t in snrio:
    for r in rt:
        tm1.addConstr(quicksum(y[s,r,t] for s in ms) == 1,"c%d" % k)              # The entire demand at each retailer must be fulfilled
        k+=1
tm1.optimize()
tm1.write("TM1_LP.lp")
for v in tm1.getVars():
    print v.varName, v.x
print 'Obj: ', tm1.objVal

