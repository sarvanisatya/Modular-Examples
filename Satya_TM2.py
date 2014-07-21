# Modular Example - 3 stage stochastic program
# Coded by: Satya Malladi
#July 20th 2014
import os
from gurobipy import*

tm2 = Model("modular")
#PARAMETERS
ret = ['A', 'B', 'C']       # Retailers/Warehouses buying from the Modular Supply Units
modstations = ['S1', 'S2']  # Stations for modules
srio = ['low', 'exp', 'hi']  # Scenarios
d_sc = [0,0]
# Demands under different scenarios in two different stages  d_sc[i][j][k] --- stage i, scenario j, retailer k
d_sc[0] = [[200,240, 160],[250, 300, 200],[300,360,240]]
d_sc[1] = [[300,270, 180],[280, 320, 240],[350,400,500]]
tr = [[7,8, 15],[11, 7,4]]   # Transportation / logistics cost from the two stations to different customers
setup = [[14, 15],[5,6]]  # Setup costs at each station setup[i][j] => stage i, station j
cap = 40     # Module Capacity
ps = [[0.3,0.5,0.2],[0.4,0.5,0.1]]
rt = range(len(ret))
ms = range(len(modstations))
snrio = range(len(srio))
#VARIABLES_______________________________________________________________
x = {}              # For capacity/ (no. of modules) allocation to different stations  first and second stage xij => x of station i and stage j
for s in ms:
    for i in range(2):
        x[s,i] = tm2.addVar(vtype = GRB.INTEGER, name = 'x'+str(s+1)+str(i+1))

y = {}              # For amount of demand at retailer r filled by station s in time period t in stage i: ysr_t,i second and third stage variables
for s in ms: 
    for r in rt:
        for t in snrio:
            for i in range(2):
                y[s,r,t,i] = tm2.addVar(vtype = GRB.CONTINUOUS, ub = 1, name = 'y'+str(s+1)+str(r+1)+"_"+str(t+1)+"_"+str(i+1))
            # ysrti can be integral if each retailer must be served by only one station.
tm2.update()
ey = {}  # Expected i-j flow station to retailer
ed = {}  # Expected Demand at retailer
for r in rt:
    for i in range(2):
        ed[r,i] = quicksum(ps[i][t]*d_sc[i][t][r] for t in snrio)
        for s in ms:
            ey[s,r,i] = quicksum(ps[i][t]*y[s,r,t,i] for t in snrio)
#OBJECTIVE________________________________________________________________
stg1cost = quicksum(setup[0][f]*(x[f,0]) for f in ms)
stg2cost = quicksum(setup[1][f]*(x[f,1]) for f in ms)+quicksum(quicksum(tr[s][r]*ey[s,r,0] for s in ms) for r in rt)
stg3cost = quicksum(quicksum(tr[s][r]*ey[s,r,1] for s in ms) for r in rt)
tm2.setObjective(stg1cost+stg2cost+stg3cost)
#CONSTRAINTS______________________________________________________________
k=1  # for numbering constraints
for t in snrio:
    tm2.addConstr(cap*quicksum(x[s,0] for s in ms) >= quicksum(d_sc[0][t][r] for r in rt), "c%d" % k)   # All Demand should be satisfied always constraint
    k+=1                                    # Alternately can include penalty for demand unfulfilled
for i in range(2):
    for t in snrio:
        for s in ms:
            tm2.addConstr(cap*quicksum(x[s,j]for j in range(i+1)) >= quicksum(d_sc[i][t][r]*y[s,r,t,i] for r in rt), "c%d" % k)
            k+=1             # Capacity must be geq than the demand fulfilled by each station                                                                 
        for r in rt:
            tm2.addConstr(quicksum(y[s,r,t,i] for s in ms) == 1,"c%d" % k)              # The entire demand at each retailer must be fulfilled
            k+=1
#OPTIMIZING______________________________________________________________
tm2.optimize()
tm2.write("TM2_LP.lp")
for v in tm2.getVars():
    print v.varName, v.x
print 'Obj: ', tm2.objVal

