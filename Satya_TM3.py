# Modular Example - Completely Deterministic Dynamic Program
# Coded by: Satya Malladi
#July 27th 2014
import os
from gurobipy import*

tm3 = Model("modular_dp")
#PARAMETERS
ret = ['A', 'B', 'C']       # Retailers/Warehouses buying from the Modular Supply Units
modstations = ['S1', 'S2']  # Stations for modules
# Demands in two different seasons d_sc[i][j] --- season i, retailer k
d_sc = [0,0]
d_sc[0] = [20,21, 100]    # Season 1 - first 6 months 
d_sc[1] = [11,10, 45]    # Season 2 - next 6 months
downtime = 1            # No. of months for shifted capacity to become fully operational 
tr = [[0.7,.32, 1.5],[.69, .57,0.8]]   # Transportation / logistics cost from the two stations to different customers
setup = [14, 12]  # Setup costs at each station setup[i][j] => station j
shftcost = [[0,2],[1,0]]    # shftcost[i][j] shifting cost from station i to station j
adcost = [5,6]   # Cost of adding a module externally after the initial setup is already made
dis = [9,10]    # Cost retrieved upoon uninstalling a module
cap = 40     # Module Capacity
rt = range(len(ret))
ms = range(len(modstations))
ss = range(2)
T = 18       # No of periods / decision epochs
epochs = range(T)
#VARIABLES_______________________________________________________________
x = {}              # For capacity/ (no. of modules) allocation to different stations  first and second season xij => x of station i and season j
for s in ms:
    for i in ss:
        x[s,i] = tm3.addVar(vtype = GRB.INTEGER, name = 'x'+str(s+1)+str(i+1))

y = {}              # For amount of demand at retailer r filled by station s in time period t in stage i: ysr_t,i second and third stage variables
for s in ms: 
    for r in rt:
        for i in ss:
            y[s,r,i] = tm3.addVar(vtype = GRB.INTEGER,ub = d_sc[i][r], name = 'y'+"_"+str(s+1)+str(r+1)+str(i+1)) # ysri integral - actual flow amounts
shft = {}           # multiple of module capacity to be shifted from station i to station j.
for i in ms:
    for j in ms:
        for t in ss:
            shft[i,j,t] = tm3.addVar(vtype = GRB.INTEGER, name = 'shft'+"_"+str(i+1)+str(j+1)+str(t+1))
add = {}             # multiple of module capacity to be additionally deployed to station i add[i]
for i in ss:
    for s in ms:
        add[s,i] = tm3.addVar(vtype = GRB.INTEGER, name = 'add'+str(s+1)+str(i+1))
tm3.update()
for s in ms:
    add[s,0] = 0
    for t in ms:
        shft[s,t,0] = 0
#CONSTRAINTS______________________________________________________________
k=1  # for numbering constraints
for i in ss:
    for s in ms:
        tm3.addConstr(cap*(x[s,i]) >= quicksum(y[s,r,i] for r in rt), "c%d" % k)   # 
        k+=1            # Capacity must be geq than the demand fulfilled by each station
for i in ms:
    for j in ms:
        tm3.addConstr(shft[i,j,1] <= max(0,min(x[i,0]-x[i,1],x[j,1]-x[j,0])),"c%d" % k)
        k+=1
for s in ms:
##    for i in ss:
##        if i>0:
##            tm3.addConstr(add[s,i] == x[s,i]-quicksum(shft[l,s,i] for l in ms),"c%d" % k)
##            k+=1
    tm3.addConstr(x[s,0]+add[s,1]+quicksum(shft[p,s,1] for p in ms)== x[s,1],"c%d" % k)
    k+=1
    shft[s,s,1].ub = 0
    shft[s,s,1].lb = 0
for r in rt:
    for i in ss:
        tm3.addConstr(quicksum(y[s,r,i] for s in ms) == d_sc[i][r],"c%d" % k)              # The entire demand at each retailer must be fulfilled in season 1
        k+=1
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _      
cum_rwd = 0
for t in epochs:
    for s in ms:
        cum_rwd+= quicksum(y[s,r,t/9]*tr[s][r] for r in rt)
#OBJECTIVE________________________________________________________________
ssn1cost = quicksum(setup[f]*(x[f,0]) for f in ms)
ssn2cost = quicksum(adcost[f]*add[f,1] for f in ms) - quicksum(max(x[f,0]-x[f,1],0)*dis[f] for f in ms)
ssn2csta = quicksum(quicksum(shftcost[i][j]*shft[i,j,1] for i in ms)for j in ms) 
tm3.setObjective(ssn1cost+ssn2cost+ssn2csta+cum_rwd)
#OPTIMIZING______________________________________________________________
tm3.optimize()
tm3.write("TM3_LP.lp")
for v in tm3.getVars():
    print v.varName, v.x
print 'Obj: ', tm3.objVal
