# Modular Example - Completely Deterministic Dynamic Program - improved
# Coded by: Satya Malladi
# Aug 5th 2014
from __future__ import print_function
import os
import csv
from gurobipy import*
#PARAMETERS_______________________________________________________________

ret = ['A', 'B', 'C']       # Retailers/Warehouses buying from the Modular Supply Units
modstations = ['S1', 'S2']  # Stations for modules
# Demands in each montth d[i][j] --- month i, retailer j
with open('modular.csv', 'rb') as ex:
    d = list(csv.reader(ex, skipinitialspace=True))
    d = [i for i in d if i]
T = 5     # No of periods = decision epochs T periods, T epochs. closing epoch not included
epochs = range(T)
for t in epochs:
    d[t] = [float(i) for i in d[t]]
st = 1            # No. of months for shifted capacity to become fully operational 
tr = [[0.7,.32, 1.5],[.69, .57,0.8]]   # Transportation / logistics cost from the two stations to different customers
setup = [14, 12]  # Setup costs at each station setup[i][j] => station j
shftcost = [[0,4],[5,0]]    # shftcost[i][j] shifting cost from station i to station j
sal = [9,8]    # Cost retrieved upon uninstalling a module without shifting
m = [0.2, 0.3]  # Maintenance cost of capacity every period
lndcost = [.12,.1]  # Land use cost per period
lostcost = [2,4,5] # Lost sales penalty
cap = 40     # Module Capacity
rt = range(len(ret))
ms = range(len(modstations))
tm4_2 = Model("modular_dp1")
#VARIABLES_______________________________________________________________

y = {} # For capacity/ (no. of modules) at station xt_s => x of station s at epoch t
for t in epochs:
    for s in ms:
        y[t,s] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'y'+str(t+1)+"_"+str(s+1))
ys = {} # For # of modules shifted from i to j station at epoch t : yst_ij
for t in epochs:
    for i in ms:
        for j in ms:
            ys[t,i,j] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'ys'+str(t+1) +"_"+str(i+1)+str(j+1))
ad = {}  # multiple of module capacity to be additionally deployed to station i at epoch t or removed
for t in epochs:
    for s in ms:
        ad[t,s] = tm4_2.addVar(vtype = GRB.INTEGER, name = 'ad'+str(t+1)+"_"+str(s+1)) # set lb accly. 
slvg = {}
for t in epochs:
    for s in ms:
        slvg[t,s] = tm4_2.addVar(vtype = GRB.INTEGER, ub =10, name = 'slvg'+str(t+1)+"_"+str(s+1)) # set lb accly. 
x = {}           # demand flow from station s to retailer r at epoch t
for t in epochs:
    for s in ms:
        for r in rt:
            x[t,s,r] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'x'+str(t+1)+"_"+str(s+1)+str(r+1))
lnd = {} # Binary variable to know if station s is being used in period t
for t in epochs:
    for s in ms:
        lnd[t,s] = tm4_2.addVar(vtype = GRB.BINARY, name = 'lnd'+str(t+1)+"_"+str(s+1))
lost = {} # Lost sales at cusstomer r in period t - no of units 
for t in epochs:
    for r in rt:
        lost[t,r] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'lost'+str(t+1)+"_"+str(r+1))
u = {}   # unused capacity at station s in period t
for t in epochs:
    for s in ms:
        u[t,s] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'u'+str(t+1)+"_"+str(s+1)) #ub = cap-1, 
z = {}
for t in epochs:
    for s in ms:
        z[t,s] = tm4_2.addVar(vtype = GRB.INTEGER, lb =0, name = 'z'+str(t+1)+"_"+str(s+1)) #ub = cap-1, 
tm4_2.update()
#CONSTRAINTS______________________________________________________________
k=1  # for numbering constraints
for t in epochs:
    for r in rt:      # 1) for each retailer in each period demand fulfillment
        tm4_2.addConstr(lost[t,r]+quicksum(x[t,s,r] for s in ms) == d[t][r],"c%d" % k)
        k+=1
for t in epochs:
    for s in ms:      # 2) for each station in each period capacity distribution
        tm4_2.addConstr(u[t,s] + quicksum(x[t,s,r] for r in rt) == cap*y[t,s],"c%d" % k)
        k+=1
        tm4_2.addConstr(ys[t,s,s]== 0, "c%d" % k)
        k+=1
        tm4_2.addConstr(y[t,s] <= ((quicksum(d[t][r] for r in rt)/cap) + 1)*lnd[t,s], "c%d" % k) # 3) for each station's land use
        k+=1
##        tm4_2.addConstr(y[t,s] >= lnd[t,s], "c%d" % k) redundant
##        k+=1
for s in ms:
    tm4_2.addConstr(ad[0,s]== 0, "c%d" % k)
    tm4_2.addConstr(slvg[0,s]== 0, "c%d" % k)
    tm4_2.addConstr(y[1,s]==y[0,s]-quicksum(ys[0,s,i] for i in ms)+ad[1,s]-slvg[1,s],"c%d" % k) # 4) Dyn Eq for the first period
    k+=1
    for t in range(1,T-1):     # for each station SYSTEM DYNAMICS EQN  includes [1, 2, .. ,T-1]
        tm4_2.addConstr(y[t+1,s]==y[t,s]-quicksum(ys[t,s,i] for i in ms) + quicksum(ys[t-1,i,s] for i in ms)+ad[t+1,s]-slvg[t+1,s],"c%d" % k)
        k+=1
        tm4_2.addConstr(slvg[t,s] <= z[t,s],"c%d" % k)
        k+=1
        tm4_2.addConstr(z[t,s] >= y[t,s] - y[t+1,s],"c%d" % k)
        k+=1
    tm4_2.addConstr(y[T-1,s]==y[T-2,s]+quicksum(ys[T-3,i,s] for i in ms) + ad[T-1,s]-slvg[T-1,s],"c%d" % k)   # Dyn Eq for the last period
    k+=1
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _      

#OBJECTIVE________________________________________________________________
cost1 = quicksum(setup[f]*(y[0,f]) for f in ms)   # First epoch setup cost
cost2a= quicksum(quicksum(setup[s]*ad[t,s] for s in ms) for t in epochs)# Additional setup cost 
cost2b= quicksum(quicksum(sal[s]*slvg[t,s] for s in ms) for t in epochs)# Salvage from retired modules      
cost2 = cost2a-cost2b
cost3 = quicksum(quicksum(m[s]*y[t,s] for s in ms) for t in epochs) # maintenance cost every period
cost4 = quicksum(quicksum(quicksum(shftcost[i][j]*ys[t,i,j] for i in ms)for j in ms) for t in epochs) # module shifting cost 
cost5 = quicksum(quicksum(quicksum(tr[s][r]*x[t,s,r] for s in ms)for r in rt) for t in epochs) # transportation cost
cost6 = quicksum(quicksum(lndcost[s]*lnd[t,s] for s in ms)for t in epochs)  # land use cost
cost7 = quicksum(quicksum(lostcost[r]*lost[t,r] for r in rt)for t in epochs)  # lost sales per period
tm4_2.setObjective(cost1+cost2+cost3+cost4+cost5+cost6+cost7+quicksum(quicksum(z[t,s] for s in ms) for t in epochs), GRB.MINIMIZE)
#OPTIMIZING______________________________________________________________
tm4_2.optimize()
tm4_2.write("tm4_2_LP.lp")
sol = open('tm4_2_soln.txt','w+')
for v in tm4_2.getVars():
    print(v.varName, v.x , file=sol)
print ( "Obj: ", tm4_2.objVal, file=sol)
