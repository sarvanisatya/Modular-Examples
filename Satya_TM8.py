# Modular Example - Dynamic Program - uncertain demands - mean and variance known - normal
# Coded by: Satya Malladi
#Adding buffer variable
# Sep 1st 2014
from __future__ import print_function
import os
import csv
import random
from gurobipy import*
#PARAMETERS_______________________________________________________________

ret = ['A', 'B', 'C']       # Retailers/Warehouses buying from the Modular Supply Units
modstations = ['S1', 'S2']  # Stations for modules
# Demands in each montth d[i][j] --- month i, retailer j
with open('modmean_nonstationary.csv', 'rb') as ex:
    d_mean = list(csv.reader(ex, skipinitialspace=True))
    d_mean = [i for i in d_mean if i]
with open('modsd.csv', 'rb') as ex:
    d_sd = list(csv.reader(ex, skipinitialspace=True))
    d_sd = [i for i in d_sd if i]
with open('modbudget.csv', 'rb') as ex:
    b = list(csv.reader(ex, skipinitialspace=True))
    b = [i for i in b if i]
T = 5     # No of periods = decision epochs T periods, T epochs. closing epoch not included
#num_ret = len(d_mean[0])# Read from costs file eg--  num_lines = sum(1 for line in open('modmean.csv'))
#num_epochs = len(d_mean) # = T
epochs = range(T)
rt = range(len(ret))
ms = range(len(modstations))
dem = open('dem.txt','w+')
d = {}
for t in epochs:
    d_mean[t] = [float(i) for i in d_mean[t]]
    d_sd[t] = [float(i) for i in d_sd[t]]
    b[t] = [float(i) for i in b[t]]
    for r in rt:
        d[t,r] = d_mean[t][r] #int(random.gauss(d_mean[t][r], d_sd[t][r]))
        print(d[t,r], end = '\t', file = dem)
    print('', file = dem)
st = 1            # No. of months for shifted capacity to become fully operational 
tr = [[0.7,.32, 1.5],[.69, .57,0.8]]   # Transportation / logistics cost from the two stations to different customers
setup = [14, 12]  # Setup costs at each station setup[i][j] => station j
shftcost = [[0,0.8],[0.5,0]]    # shftcost[i][j] shifting cost from station i to station j
sal = [9,8]    # Cost retrieved upon uninstalling a module without shifting
m = [0.2, 0.3]  # Maintenance cost of capacity every period
lndcost = [.4,.3]  # Land use cost per period
lostcost = [2,4,5] # Lost sales penalty
hcost = [2.5, 1.7] # Holding cost of modules
hp = [0.1,0.09] # Holding cost of product at stations
h = [ 0.15, 0.2, 0.17] # Holding cost of product t retailers
cap = 40     # Module Capacity
M = 10^6   # LARGE NUMBER Big M
tm8 = Model("modular")
#VARIABLES_______________________________________________________________
bfr = {} # Number of modules retained for one of the upcoming periods
y = {} # For capacity/ (no. of modules) at station xt_s => x of station s at epoch t
for t in epochs:
    for s in ms:
        y[t,s] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'y'+str(t+1)+"_"+str(s+1))
        bfr[t,s] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'bfr'+str(t+1)+"_"+str(s+1))
ys = {} # For # of modules shifted from i to j station at epoch t : yst_ij
for t in epochs:
    for i in ms:
        for j in ms:
            ys[t,i,j] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'ys'+str(t+1) +"_"+str(i+1)+str(j+1))
ad = {}  # multiple of module capacity to be additionally deployed to station i at epoch t or removed
for t in epochs:
    for s in ms:
        ad[t,s] = tm8.addVar(vtype = GRB.INTEGER, name = 'ad'+str(t+1)+"_"+str(s+1)) # set lb accly. 
slvg = {}
for t in epochs:
    for s in ms:
        slvg[t,s] = tm8.addVar(vtype = GRB.INTEGER, name = 'slvg'+str(t+1)+"_"+str(s+1)) # set lb accly. 
for s in ms:
    slvg[T,s]=tm8.addVar(vtype = GRB.INTEGER, name = 'slvg'+str(T+1)+"_"+str(s+1)) # set lb accly. 
    y[T,s] = tm8.addVar(vtype = GRB.INTEGER, name = 'y'+str(T+1)+"_"+str(s+1))  
x = {}           # demand flow from station s to retailer r at epoch t
for t in epochs:
    for s in ms:
        for r in rt:
            x[t,s,r] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'x'+str(t+1)+"_"+str(s+1)+str(r+1))
lnd = {} # Binary variable to know if station s is being used in period t
for t in epochs:
    for s in ms:
        lnd[t,s] = tm8.addVar(vtype = GRB.BINARY, name = 'lnd'+str(t+1)+"_"+str(s+1))
lost = {} # Lost sales at cusstomer r in period t - no of units
I = {}  # For product inventory at each retailer r in period t
for t in epochs:
    for r in rt:
        lost[t,r] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'lost'+str(t+1)+"_"+str(r+1))
        I[t,r] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'I'+str(t+1)+"_"+str(r+1))
G = {} # for product inventory at each station s in period t
for t in epochs:
    for s in ms:
        #z[t,s] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'z'+str(t+1)+"_"+str(s+1))
        G[t,s] = tm8.addVar(vtype = GRB.INTEGER, lb =0, name = 'G'+str(t+1)+"_"+str(s+1))
tm8.update()
#CONSTRAINTS______________________________________________________________
k=1  # for numbering constraints
# 1) for each retailer in each period demand fulfillment_ _ _ _ _ _ _ _ _ _ _ _ _ _ _
for r in rt:
    for t in range(T-1):      
        tm8.addConstr(lost[t,r]+quicksum(x[t,s,r] for s in ms) + I[t,r] == d[t,r]+ I[t+1,r],"c%d" % k)
        k+=1
        tm8.addConstr(lost[t,r]>= d[t,r] - quicksum(x[t,s,r] for s in ms) - I[t,r],"c%d" % k)
        k+=1
        tm8.addConstr(I[t+1,r]>= -d[t,r]+ quicksum(x[t,s,r] for s in ms) + I[t,r],"c%d" % k)
        k+=1
    tm8.addConstr(I[0,r]== 0, "c%d" % k)
    k+=1
    tm8.addConstr(quicksum(x[T-1,s,r] for s in ms)+lost[T-1,r] + I[T-1,r]== d[T-1,r], "c%d" % k)
    k+=1
# 2) for each station in each period capacity distribution_ _ _ _ _ _ _ _ _ _ _ _ _ _ _
for s in ms:
    for t in range(T-1):
        tm8.addConstr(G[t+1,s] + quicksum(x[t,s,r] for r in rt) == cap*y[t,s] + G[t,s],"c%d" % k)
        k+=1
        tm8.addConstr(G[t+1,s] >= G[t,s]+cap*y[t,s] - quicksum(x[t,s,r] for r in rt),"c%d" % k)
        k+=1
    tm8.addConstr(G[0,s]== 0, "c%d" % k)
    k+=1
    tm8.addConstr(quicksum(x[T-1,s,r] for r in rt)== cap*y[T-1,s]+ G[T-1,s] , "c%d" % k)
    k+=1
# 3) Station Land Use Constraints_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
for t in epochs:
    for s in ms:
        tm8.addConstr(ys[t,s,s]== 0, "c%d" % k)
        k+=1
        tm8.addConstr(y[t,s] +bfr[t,s] <= M*lnd[t,s], "c%d" % k) 
        k+=1
# 4) Budget constraint on capacity maintenance for each period_ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _
for t in epochs:
    tm8.addConstr(quicksum(m[s]*(y[t,s]+bfr[t,s]) for s in ms) <= b[t][0], "c%d" % k) 
    k+=1
# 5) Extra eqns for balancing state dynamics equation _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
for s in ms:
    tm8.addConstr(ad[0,s]== 0, "c%d" % k)
    k+=1
    tm8.addConstr(slvg[0,s]== 0, "c%d" % k)
    k+=1
    tm8.addConstr(bfr[0,s]== 0, "c%d" % k)
    k+=1
    # 5a) Dyn Eq for the first period_ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    tm8.addConstr(y[1,s]+bfr[1,s]==bfr[0,s]+y[0,s]-quicksum(ys[0,s,i] for i in ms)+ad[1,s]-slvg[1,s],"c%d" % k) 
    k+=1
    # 5b) for each station SYSTEM DYNAMICS EQN  includes [1, 2, .. ,T-1]_ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    for t in range(1,T-1):     
        tm8.addConstr(y[t+1,s]+bfr[t+1,s]==bfr[t,s]+y[t,s]-quicksum(ys[t,s,i] for i in ms) + quicksum(ys[t-1,i,s] for i in ms)+ad[t+1,s]-slvg[t+1,s],"c%d" % k)
        k+=1
    # 5c) Dyn Eq for the last+1 period_ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    tm8.addConstr(y[T,s]==bfr[T-1,s]+y[T-1,s]+quicksum(ys[T-2,i,s] for i in ms) -slvg[T,s],"c%d" % k)   
    k+=1
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _ _ _ _ _ _ _ _ _ _ _ _ _ __ _     

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
cost8 = quicksum(quicksum(hcost[s]*bfr[t,s] for s in ms)for t in epochs)  # holding cost of buffer inventory
cost9 = quicksum(quicksum(hp[s]*G[t,s] for s in ms) for t in epochs) # holding cost of product at stations
cost10 = quicksum(quicksum(h[r]*I[t,r] for r in rt) for t in epochs) # holding cost of product at retialers
tm8.setObjective(cost1+cost2+cost3+cost4+cost5+cost6+cost7+cost8+cost9+cost10, GRB.MINIMIZE)
#OPTIMIZING______________________________________________________________
tm8.optimize()
tm8.write("tm8_LP.lp")
sol = open('tm8_soln.txt','w+')
for v in tm8.getVars():
    print(v.varName, v.x , file=sol)
print ( "Obj: ", tm8.objVal, file=sol)
