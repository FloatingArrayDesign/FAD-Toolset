"""

Simple driver file to create a RAFT model of a 2-platform array with turbines.
This file then adds a wave spectrum to run, analyzes that case, and plots the results.

For more information on using RAFT, please see RAFT documentation at https://github.com/WISDEM/RAFT
"""

from fad import Project
import matplotlib.pyplot as plt
import os
from fad.helpers import createRAFTDict

# define name of ontology input file
dir = os.path.dirname(os.path.realpath(__file__))
input_file = os.path.join(dir,'02_FOWT.yaml')

# define an output file to store RAFT results in
RAFT_outfile = os.path.join(dir,'02_FOWT_RAFT_results.xlsx')

# initialize Project class with input file
project = Project(file=input_file,raft=True)

project.plot3d(plot_fowt=True) # plot the system

# - - - Let's adjust the heading of one platform, and then re-create the raft model - - - 
project.platformList['fowt0'].setPosition(project.platformList['fowt0'].r, heading=180, degrees=True) # rotate platform 180 degrees

project.getMoorPyArray() # re-create the moorpy array

rd = createRAFTDict(project) # create new raft input dictionary that will account for the heading change

project.getRAFT(rd) # create new RAFT model

project.plot3d(plot_fowt=True) # plot updated system

# pull out RAFT object
raft_model = project.array # store short cut to raft model 

# - - - Let's try running a case - - - 
## First, let's add a case in to the model's design dictionary (since we didn't add this in the ontology)
raft_model.design['cases'] = {}
raft_model.design['cases']['keys'] = ['wind_speed', 'wind_heading', 'turbulence', 'turbine_status', 'yaw_misalign', 'wave_spectrum', 'wave_period', 'wave_height', 'wave_heading']
raft_model.design['cases']['data'] = [[     0,         0,             0,             'operating',        0,             'JONSWAP',         12,           6,              0        ]]

# analyze our case
raft_model.analyzeCases(display=True) # display what's happening for fun

# plot RAFT results
raft_model.plotResponses()
raft_model.plot()

# record the results to an excel file
project.mapRAFTResults() # first need to map results to the project class
print(f'Writing RAFT results to excel file {RAFT_outfile}')
project.generateSheets(RAFT_outfile)

plt.show()