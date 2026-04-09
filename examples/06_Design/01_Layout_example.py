# -*- coding: utf-8 -*-
"""
This example shows a layout optimization with varied bathymetry and soil
and then application of 3D cable designs, FOWT and substation design details,
cable rerouting to avoid obstacles, and more.

Layout objects inherit from Project, so they have access to all the
project methods (including unload etc)

An alternative method to including layout inputs is shown in the example at the bottom of 
fad/design/layout.py

This example will take a long time to run if not used on an HPC with the 
layout setting parallel=True. To simply see what the initial layout looks like 
instead of optimizing, comment out the sections labeled **COMMENT OUT TO SKIP OPTIMIZATION PROCESS**
"""

from copy import deepcopy
import numpy as np
import moorpy as mp
import fad
from fad.design.layout import Layout
from floris import (
    TimeSeries,
    WindRose,
    )
from moorpy.helpers import lines2ss
import pandas as pd
from fad.mooring.mooring import Mooring
from fad.anchors.anchor import Anchor
from fad.helpers import adjustMooring
import ruamel.yaml
yaml = ruamel.yaml.YAML()
from pyswarm import pso # change to whatever optimizer you're using
from fad.helpers import createRAFTDict
from fad.helpers import route_around_anchors
import os

# - - - - - Input Files
dir = os.path.dirname(os.path.realpath(__file__))
mdFile = os.path.join(dir,'Layout_Inputs','FCD_MoorDyn_ST.dat')
cableFile =  os.path.join(dir,'Layout_Inputs','cableConfigMaine.yaml')
bathFile =  os.path.join(dir,'Layout_Inputs','GulfofMaine_bathy.txt')
soilFile =  os.path.join(dir,'Layout_Inputs','GulfofMaine_soil.txt')
florisFile =  os.path.join(dir,'Layout_Inputs','gch_floating.yaml')
turbineFile =  os.path.join(dir,'Layout_Inputs','IEA-15-240-RWT.yaml')
fowtFile =  os.path.join(dir,'Layout_Inputs','VolturnUS.yaml')
subFile =  os.path.join(dir,'Layout_Inputs','substation.yaml')
wfile = os.path.join(dir,'Layout_Inputs','GulfOfMaine_metocean_1hr.txt')

# ----- Layout input information
nt = 20 # number of turbines
noss = 1 # number of substations
# conductor sizes for cables
iac_typical_conductor = np.array([300, 630, 1000])
# this examle uses a rectangular lease area, but can have any shape you want
lease_width = 10000 # length/width of the lease area
lease_length = 10000
oss_coords = np.array([[0, 0]]) # approx location of oss, will be updated by optimizer to fit in uniform grid
lease_coords = np.array([
                        (-lease_width/2, -lease_length/2),
                        (-lease_width/2, lease_length/2),
                        (lease_width/2, lease_length/2),
                        (lease_width/2, -lease_length/2)
                        ])
exclusion_coords = np.array([[(2800, 500), # coordinates for an exclusion zone within the lease
                    (4000, 500),
                    (3600, 3400),
                    (2800, 3400),
                    (2800, 500)]])

# ----- Optimization inputs -----
opt_mode = 'CAPEX'  # what do you want to optimize? (LCOE = 'LCOE2', AEP='AEP', CapEx='CAPEX')
opt_method = 'PSO' # optimizer type
use_FLORIS = False # Change to true if you're running AEP or LCOE optimization
# Uniform grid design variables initial values (Xu): [x-spacing [km], y-spacing [km], x-translation [km], y-translation [km], grid rotation [deg], grid skew [deg], platform rotation [deg]]
Xu = [1.65,   1.85, 0, 0 , 20, 10,  0] # this is the initial values for the uniform grid design variables, these will be changed by the optimizer
# lower and upper boundaries for each design variable in Xu
boundaries_UG = np.array(([1.111,2.7],[1.111,2.7],[-2.0,2.0],[-2.0,2.0],[0,180],[-30,30],[0,120]))
swarmsize = 2 # this is a small number for this example, generally would use swarmsize of well over 100+
niterations = 2 # this is a small number for this example, generally would use well over 100+ iterations



# ---- LOAD MOORPY SYSTEM -----
ms = mp.System(file=mdFile)
ms.initialize()
ms.solveEquilibrium()

# add in needed info from getLineProps (MBL,cost,d_nom)
for typ in ms.lineTypes.values():
    if 'chain' in typ['material']:
        d_nom = typ['d_vol']/1.8
        ms.setLineType(d_nom*1000,'chain',name=typ['name'])
    elif 'poly' in typ['material']:
        d_nom = typ['d_vol']/.86
        ms.setLineType(d_nom*1000,'polyester',name=typ['name'])
        
msNew = lines2ss(ms)

ss = deepcopy(msNew.lineList[0])
ss.rad_fair = 58
ss.z_fair = -14
rotation_mode = True
rot_rad = np.zeros((nt))


# ----- LOAD WIND DATA -----
colnames = ['YY','MM','DD','hh','WDIR10m','WSPD10m','WDIR150m','WSPD150m','MWD','WVHT','DPD','CDIR','CSPD','ATMP10m','WTMP']

df = pd.read_csv(wfile,sep='\t',engine='python',header=5,names=colnames)

ws = np.array(df['WSPD150m'].tolist())
wd = np.array(df['WDIR150m'].tolist())

time_series = TimeSeries(
    wind_directions=wd, wind_speeds=ws, turbulence_intensities=0.06
)
# The TimeSeries class has a method to generate a wind rose from a time series based on binning
wind_rose = time_series.to_WindRose(wd_step=5, ws_step=1)


# ----- SETUP LAYOUT SETTINGS -----
anchor_settings = {'anchor_design':{'A':15,'zlug':20},
                   'anchor_type':'DEA',
                   'anchor_resize':False,
                   'fix_zlug':True,
                   'FSdiff_max':{'Ha':.1,'Va':.2},
                   'FS_min':{'Ha':2,'Va':0},
                   'mass':9159}

# mooring line adjustment settings
adjuster_settings = {'method': 'horizontal', # adjust horizontal pretension when bathymetry changes
                     'i_line': [1], # index of line section to be altered to fit bathymetry
                     'span': 700-58, # horizontal distance from anchor to fairlead
                     }

layout_settings = {
                   'n_turbines': nt,
                   'n_cluster': 3, # number of cable strings entering each substation
                   'turb_rot': np.zeros((nt)),
                   'rotation_mode': True,
                   'cable_mode': True, # include cable routing
                   'oss_coords': oss_coords,
                   'boundary_coords': lease_coords,
                   'ss': ss,
                   'mooringAdjuster': adjustMooring, # use fad toolset adjuster function, or replace with your own
                   'adjuster_settings': adjuster_settings,
                   'bathymetry_file': bathFile,
                   'soil_file': soilFile,
                   'floris_file': florisFile,
                   'exclusion_coords': exclusion_coords,
                   'use_FLORIS': use_FLORIS, 
                   'wind_rose': wind_rose,
                   'mode': opt_mode,
                   'optimizer': opt_method,
                   'parallel': False, # parallelize floris AEP calculations
                   'anchor_settings': anchor_settings,
                   'noss': noss,
                   'iac_typical_conductor': iac_typical_conductor
                   }

# ----- INITIALIZE LAYOUT ------
layout1 = Layout(X=[], Xu=Xu, **layout_settings)

# plot the layout 2 ways
layout1.plotLayout()
layout1.plot2d()

# --- RUN LAYOUT OPTIMIZATION - **COMMENT OUT TO SKIP OPTIMIZATION PROCESS**---
# Note: if you're using a different optimizer, you'll need to change this section
res, fopt = pso(layout1.objectiveFunUG, 
                lb=boundaries_UG[:,0], 
                ub=boundaries_UG[:,1], 
                f_ieqcons=layout1.constraintFunsUG,  
                swarmsize=swarmsize, 
                omega=0.72984, 
                phip=0.6, 
                phig=0.8, 
                maxiter=niterations,
                minstep=1e-8, 
                minfunc=1e-8, 
                debug=True)
layout1.updateLayoutUG(Xu=res, level=2, refresh=True)  # do a higher-fidelity update

# Save best result design variables
print(res)
with open('Optimization_results.txt','w') as ofile:
    ofile.write(str(res))
ofile.close()

# ----- ADD FULL TURBINE, PLATFORM, & SUBSTATION DESIGN -----
# ensure fairlead radius and depth are right for FOWT platforms
for pf in layout1.platformList.values():
    if pf.entity == 'FOWT':
        pf.rFair = 58
        pf.zFair = -14
        
with open(turbineFile) as ft:
    turb = dict(yaml.load(ft))
layout1.turbineTypes = [turb]
with open(fowtFile) as ff:
    fowt = dict(yaml.load(ff))
layout1.platformTypes = []
layout1.platformTypes.append(fowt)

# We don't have a substation design, so just make a minimal platform type
# and combine it with the FOWT platform design for now...
sub = {'type': 'Substation',
       'rFair': 38,
       'zFair': -14}
sub = sub | fowt
# Note: this does not include mooring for the substation as
# it's assumed this will be different. 
# We only minimally consider substations as a 
# point(s) towards which we direct the cables 
# If you want a full substation design with moorings
# You'll have to add that in here!
layout1.platformTypes.append(sub)

for pf in layout1.platformList.values():
    if not pf.entity == 'Substation':
        layout1.addTurbine(typeID=1,platform=pf,turbine_dd=turb)
        pf.dd['type'] = 0
    else:
        pf.dd['type'] = 1
    

rd = createRAFTDict(layout1)
layout1.getRAFT(rd)
        
# ----- ADD 3D CABLE DESIGN -----
# load in cable configs
with open(cableFile) as fc:
    cC = yaml.load(fc)
cableConfig = dict(cC) # different cable designs for max and min depths defined in the file allow us to interpolate the designs and adjust the cable length and buoyancy for dpeth

# apply 3D cable design from cableFile to the layout, adjust dynamic cable headings, and rout static cables around anchors
layout1.addCablesConnections(layout1.iac_dic, # list of dictionaries describing 2D cable layout
                             cableConfig=cableConfig, # 3D cable design configurations
                             heading_buffer=30, # buffer angle between mooring lines and dynamic cabled
                             )
layout1.plot2d()
# let's try adjusting the dynamic cable heading the other way 
layout1.addCablesConnections(layout1.iac_dic,
                            cableConfig=cableConfig,
                            heading_buffer=30,
                            adj_dir=-1)
layout1.plot2d()
# re-route static cables to avoid anchor crossings
route_around_anchors(layout1,padding=100)
# re-create moorpy array with 3D cables
layout1.getMoorPyArray() 

# plot
layout1.plot3d(plot_fowt=True)
layout1.plot2d()

# unload to a yaml 
layout1.unload('optimized_array.yaml')