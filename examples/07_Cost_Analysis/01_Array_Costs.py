# -*- coding: utf-8 -*-
"""
Get costs of array broken down by component type. Includes static cable routed length, cable appendage costs, anchor costs, etc
"""

from fad.project import Project
import os
import numpy as np
import matplotlib.pyplot as plt

# point to location of yaml file with uniform array info
dir = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir,'../OntologySample200m.yaml') # yaml file 

# load in yaml
project = Project(file=filename, raft=False)
project.plot2d()

cost_dict = project.getArrayCost() # call cost calculation function for all components & return a cost breakdown
print('\n--------- Array Cost Breakdown ---------\n')
for key,val in cost_dict.items():
    print(f'{key} cost: {val} [USD]\n')
    
# break down the cost of a cable to see where these costs are coming from 
# and show that cable routing, appendages, and buoyancy modules are reflected in the overall cost
print('\n--------- Single Cable Cost Breakdown ---------\n')
cab = project.cableList['cable1'] 
for i,sub in enumerate(cab.subcomponents):
    print(f'________{cab.id} subcomponent {i} Costs_________')
    print(f'subcomponent type: {type(sub).__name__}')
    # joints are handled a bit differently since they are actually dictionaries
    if isinstance(sub, dict):
        print(f'Joint cost: {sub["cost"]} [USD]')
    # otherwise, read out all the line items in the cost dictionary
    else:
        print(f'subcomponent {i} length: {sub.L} [m]')
        print(f'subcomponent {i} cost per length: {sub.cableType["cost"]} [USD/m]')
        for key,val in sub.cost.items():
            print(f'subcomponent {i} {key} cost: {val} [USD]')
print(f'========Cable {cab.id} overall cost: {np.round(cab.getCost(),2)} [USD]=========')
print(f'========Total array material cost: {np.round(np.sum([c for c in cost_dict.values()]),2)} [USD]=======')
