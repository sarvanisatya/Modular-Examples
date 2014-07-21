# Coded by Satya Malladi

#import numpy as np
#from numpy import *
from lpsolve55 import *
lp = lpsolve('make_lp', 0, 10)
lpsolve('set_verbose', lp, IMPORTANT)
# Variables: x1, x2, y11, y12, y13, y14, y21, y22, y23, y24
#Objective
ret = lpsolve('set_obj_fn', lp, [4, 4, 4, 3, 5, 8, 7, 6, 4, 5])
# Demand - Supply Constraints
ret = lpsolve('add_constraint', lp, [-40, 0, 10, 10, 10, 10, 0, 0, 0, 0], LE, 0)
ret = lpsolve('add_constraint', lp, [0, -40, 0, 0, 0, 0, 10, 10, 10, 10], LE, 0)
# tried [25 35 45 10], [40 35 45 10], [10, 35, 45, 30], [10, 10, 10, 10]

#Demand shhould be served by only one of the stations
ret = lpsolve('add_constraint', lp, [0, 0, 1, 0, 0, 0, 1, 0, 0, 0], EQ, 1)
ret = lpsolve('add_constraint', lp, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0], EQ, 1)
ret = lpsolve('add_constraint', lp, [0, 0, 0, 0, 1, 0, 0, 0, 1, 0], EQ, 1)
ret = lpsolve('add_constraint', lp, [0, 0, 0, 0, 0, 1, 0, 0, 0, 1], EQ, 1)
#Integrality Constraints
ret = lpsolve('set_int',lp, 1,1)
ret = lpsolve('set_int',lp, 2,1)
ret = lpsolve('set_int',lp, 3,1)
ret = lpsolve('set_int',lp, 4,1)
ret = lpsolve('set_int',lp, 5,1)
ret = lpsolve('set_int',lp, 6,1)
ret = lpsolve('set_int',lp, 7,1)
ret = lpsolve('set_int',lp, 8,1)
ret = lpsolve('set_int',lp, 9,1)
ret = lpsolve('set_int',lp, 10,1)
#Setting Lower Bounds
ret = lpsolve('set_lowbo',lp, 1, 0)
ret = lpsolve('set_lowbo',lp, 2, 0)
ret = lpsolve('set_lowbo',lp, 3, 0)
ret = lpsolve('set_lowbo',lp, 4, 0)
ret = lpsolve('set_lowbo',lp, 5, 0)
ret = lpsolve('set_lowbo',lp, 6, 0)
ret = lpsolve('set_lowbo',lp, 7, 0)
ret = lpsolve('set_lowbo',lp, 8, 0)
ret = lpsolve('set_lowbo',lp, 9, 0)
ret = lpsolve('set_lowbo',lp, 10, 0)
#Setting Upper Bounds
ret = lpsolve('set_upbo',lp, 1, 4)
ret = lpsolve('set_upbo',lp, 2, 4)
ret = lpsolve('set_upbo',lp, 3, 1)
ret = lpsolve('set_upbo',lp, 4, 1)
ret = lpsolve('set_upbo',lp, 5, 1)
ret = lpsolve('set_upbo',lp, 6, 1)
ret = lpsolve('set_upbo',lp, 7, 1)
ret = lpsolve('set_upbo',lp, 8, 1)
ret = lpsolve('set_upbo',lp, 9, 1)
ret = lpsolve('set_upbo',lp, 10, 1)
#Solving LP
ret = lpsolve('write_lp', lp, 'a.lp')
lpsolve('solve', lp)
#print lpsolve('get_objective', lp)
print lpsolve('get_variables', lp)[0]
# print lpsolve('get_constraints', lp)[0]
obj = lpsolve('get_objective', lp)
print " Objective is %d " % obj
#print obj
[x, ret] = lpsolve('get_variables', lp)
#lpsolve('delete_lp', lp)
