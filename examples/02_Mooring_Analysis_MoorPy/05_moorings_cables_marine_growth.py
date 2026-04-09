# -*- coding: utf-8 -*-
"""
Simple driver file to create an FAModel project and make a moorpy system model
of the array including moorings and dynamic cables.
The input file only contains the bare minimum information to build a moorpy
array with moorings and dynamic cables (static cables are not modeled in MoorPy)

For more information on MoorPy, please see MoorPy documentation at https://github.com/NREL/MoorPy
"""

from fad import Project
import matplotlib.pyplot as plt
import numpy as np
import os
from copy import deepcopy

# define name of ontology input file
dir = os.path.dirname(os.path.realpath(__file__))
input_file = os.path.join(dir,'05_moorings_cables_marine_growth.yaml')

# initialize Project class with input file, we don't need RAFT for this so mark False
project = Project(file=input_file,raft=False)

# create moorpy array
project.getMoorPyArray()

project.plot3d()
# - - - Let's add marine growth to moorings and cables - - - 
# pick a mooring line to check that mg was added on
moor_to_check = list(project.mooringList.values())[0]

# pull out nominal diameter of top line section before adding marine growth
reg_line_d = deepcopy(moor_to_check.ss.lineList[-1].type['d_nom'])
print('\n-------------------Initial mooring line properties--------------------')
print(moor_to_check.ss.lineList[-1].type) # top line section
print('----------------------------------------------------------------------\n')
# Note: all line properties for all sections of a mooring line can be accessed in moor_to_check.ss.lineTypes
# to ge the specific line properties of a specific section of a mooring line, use moor_to_check.ss.lineList[x].type
# where x is the index of the line section. Adding marine growth generally increases # of line sections

# add marine growth to all mooring lines (mg added based on dict in yaml)
print('Adding marine growth')
project.getMarineGrowth(tol=2.5) # tol is tolerance for depth that the mooring line changes from one thickness to the next. 
# If tol=2.5 and thickness changes at -40 m, the thickness change can be -40 +/- 2.5 m

print('\n----------Marine growth 0.05 m thick mooring line properties-----------')
print(moor_to_check.ss.lineList[-1].type) # top line section
print('----------------------------------------------------------------------\n')
    
# pull out nominal diameter of top line section after applying marine growth
mg_line_d = moor_to_check.ss.lineList[-1].type['d_nom']

# at top, the nominal diameter should have increased 0.2 m (.1 m thickness on each side)
print('\nPristine line nominal diameter just below surface: ',reg_line_d)
print('Marine growth line nominal diameter just below surface: ',mg_line_d)

# plot again just to make sure the mooring still looks right
project.plot3d()

