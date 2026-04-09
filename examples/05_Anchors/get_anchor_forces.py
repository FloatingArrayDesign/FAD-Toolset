"""

Simple driver file to create a RAFT model of a 2-platform array with turbines.
This file then adds a wave spectrum to run, analyzes that case, and plots the results.

For more information on using RAFT, please see RAFT documentation at https://github.com/WISDEM/RAFT
"""

from fad import Project
import matplotlib.pyplot as plt
import os

# define name of ontology input file
dir = os.path.dirname(os.path.realpath(__file__))
input_file = os.path.join(dir,'inputs','sharedanch_example.yaml')

# initialize Project class with input file
project = Project(file=input_file,raft=True)

project.plot3d(plot_fowt=True) # plot the system


#---Let's get the max anchor forces due to turbine thrust and wave displacement

# first apply a wave motion amplitude
for platform in project.platformList.values():
    platform.x_ampl = 10 # [m]
    
# now go through each anchor and run the worst-case scenarios (has considerations for shared anchors as well)
print('{:-^41}'.format('Max Anchor Loads'))
print('Anchor ID | Horizontal Max | Vertical Max')
for anchor in project.anchorList.values():
    anchor.calcMudlineLoads()
    print('{0:s}         {1:.2e} [N]     {2:.2e} [N]'.format(anchor.id,anchor.loads["Hm"],anchor.loads["Vm"]))

plt.show()