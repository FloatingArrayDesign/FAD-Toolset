import numpy as np
import matplotlib.pyplot as plt
from fad.design.LineDesign import LineDesign
import time
import os


# This first example introduces the basic concepts of the LineDesign tool while focusing on the different design modes

# LineDesign is the name of our mooring line design tool that can run various optimization algorithms to find the set 
# of mooring line parameters that minimize an objective (default is cost) while satisfying many constraints.
# It works in a 2D plane but considers the physical effects of repeated mooring lines at defined headings around the platform
# For example, what is the set of line diameters and line lengths of a semi-taut chain-nylon rope mooring line 
# for a floating offshore structure in 200 m with given platform offset limits?

# The LineDesign Python class is derived from a FAD-Toolset 'Mooring' class, which contains an underlying MoorPy Subsystem



# Set the location of the mooring line property coefficients file
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
moorprops_file = os.path.join(__location__ , 'MoorProps_LineDesign.yaml')

# output results function
def getResults(X, ld):
    X = np.asarray(X, dtype=float)
    X_denorm = X * np.asarray(ld.X_denorm, dtype=float)

    print('\n--- Optimization Results ---')
    print('Normalized design variables:   ', [f'{x:8.4f}' for x in X])
    print('Denormalized design variables: ', [f'{x:8.3f}' for x in X_denorm])

    if 'xe' in ld.log and len(ld.log['xe']) > 0:
        print(f"Internal solver line length result: {ld.log['xe'][-1]:.3f} m")
    else:
        print('Internal solver line length result: n/a')

    print('\nConstraint evaluations (value >= 0 is feasible):')
    for i, con in enumerate(ld.constraints):
        name = con.get('name', f'constraint_{i}')
        value = float(con.get('value', np.nan))
        threshold = con.get('threshold', 'n/a')
        offset = con.get('offset', 'n/a')
        print(f"  {name:<22s} value={value:9.3f}  threshold={threshold}  offset={offset}")

    print('\nCost breakdown:')
    print(f"  Mooring line cost ($k): {ld.lineCost/1e3:,.2f}")
    print(f"  Anchor cost ($k):       {ld.anchorCost/1e3:,.2f}")
    print(f"  Total cost ($k):        {ld.cost/1e3:,.2f}")
    print(f"  Iterations:             {ld.iter}")




# Set the inputs to the LineDesign tool in a 'settings' dictionary

depth = 200                             # Water depth [m]
settings = {}
settings['rBFair'] = [58,0,-14]         # fairlead location relative to platform centerline [m]
settings['fx_target'] = 1.95e6          # steady horizontal external force applied to the platform [N]
settings['kx_target'] = 2e4             # stiffness at the top of the mooring line that the line aims to match [N/m] 
settings['headings'] = [60, 180, 300]   # headings of mooring lines around the platform [deg]
settings['x_ampl'] = 10                 # an initial guess at the dynamic amplitude of motion about the mean offset of the platform [m]

settings['name'] = 'DEA-chain'          # an identifying name of the mooring line
settings['lineTypeNames'] = ['chain']   # a list of mooring line type names (keys) in order from anchor to fairlead, which will link to the MoorProps file keys
settings['anchorType'] = 'drag-embedment'   # name of the anchor ('drag-embedment'/'dea' or 'suction' supported)

settings['solve_for'] = 'none'          # the 'design mode' or 'solve_for' option
# solve_for = 'none' sets LineDesign to include offset limits as inequality constraints
# solve_for = 'offset' means LineDesign uses an internal solver to size one line length in every optimization iteration
#   to ensure the horizontal force of the mooring system is opposite and equal to the input horizontal force on the platform
#   in its input target (mean) offset position
# solve_for = 'tension' means LineDesign uses an internal solver to size one line length in every optimization iteration
#  to ensure the pretension of the line is equal to the target horizontal force on the platform
# solve_for = 'stiffness' means LineDesign uses an internal solver to size one line length in every optimization iteration
#   to ensure the stiffness of the top of the line equals the target stiffness value
# solve_for = 'ghost' means LineDesign uses an internal solver to size the anchoring radius and a line length to ensure 
#   a certain length of line remains on the seabed in the platform's mean offset position

settings['x_target'] = 35               # the target, or maximum, mean offset of the platform away from the anchor [m]
settings['x_mean_out'] = 35             # the mean offset of the platform away from the anchor [m] (typically the same as x_target)
settings['x_mean_in'] = 60              # the mean offset of the platform closest to the anchor [m]

# Design Variables
settings['allVars'] = [1000/10, 1000, 120]      # Initial Design Variable Conditions
# [Anchoring Radius [10m], Line Length [m], Line Diameter [mm] / Connection Point Weight [t], Line Length [m], Line Diameter [mm] / ...]
settings['Xindices'] = [0, 1, 2]                # Design Variable Types
# integer = design variable, 'c' = constant, 's' = solve_for (for use when design mode = 'offset', 'tension', or 'stiffness')

# Bounds
settings['Xmin'] = [10, 10, 10]                 # minimum design variable values (length=max(Xindices)+1) - COBYLA optimizer does not respect these
settings['Xmax'] = [1000, 1000, 120]            # maximum design variable values (length=max(Xindices)+1) - COBYLA optimizer does not respect these
settings['dX_last'] = [10, 10, 10]              # dopt2 optimizer control for navigability of each design variable

# Constraints - set up a list of dictionaries
settings['constraints'] = [dict(name='min_lay_length', index=0, threshold=20, offset='max'),    # minimum lay length in maximum offset position
                            dict(name='max_offset'    , index=0, threshold=60, offset='min'),   # maximum offset moving closest to the anchor
                            dict(name='max_offset'    , index=0, threshold=35, offset='max')]   # maximum offset moving away from the anchor
for j in range(len(settings['lineTypeNames'])):
    settings['constraints'].append(dict(name='tension_safety_factor', index=j, threshold=2.0, offset='max'))    # the maximum MBL/Tension ration for each line section
# other constraints available such as maximum lay length, rope_contact, or maximum 'sag' for shared lines


# Input these settings into LineDesign to create the object
ld1 = LineDesign(depth, lineProps=moorprops_file, **settings)

ld1.setNormalization()      # can normalize the inputs (design variables, constraints, objectives) to maintain consistency, but do not have to

# Run the LineDesign optimization (the primary function of the design tool)
X, min_cost = ld1.optimize(maxIter=400, plot=False, display=2, stepfac=4, method='COBYLA')
# different optimizers have different settings. COBYLA is quick but can stay local. GAs are slow but gloabl.

# Update the LineDesign object with the newly found optimal design variables in X (main function that the optimizers use to evaluate different design variables)
ld1.updateDesign(X, display=0)

# print out results
getResults(X, ld1)

# plot the design profile
ld1.plotProfile()

plt.show()

