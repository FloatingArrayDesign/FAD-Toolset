import numpy as np
import matplotlib.pyplot as plt
from fad.design.LineDesign import LineDesign
import os


SHOW_PLOTS = True



# Now let's change some of the input options, like design modes or optimizers



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


# Set up the 'settings' dictionary again, but for the offset design mode

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

settings['solve_for'] = 'offset'        # the 'design mode' or 'solve_for' option
settings['x_target'] = 20               # the expected/known mean offset of the platform
settings['x_mean_out'] = 20             # offset away from the anchor
settings['x_mean_in'] = 40              # offset closest to the anchor

settings['allVars'] = [1000/10, 1000, 120]      # Initial Design Variable Conditions
settings['Xindices'] = [0, 's', 1]              # new design variables, with a solve_for variable, to have the DEA-Chain line length solved internally
settings['Xmin'] = [10, 10]
settings['Xmax'] = [500, 500]
settings['dX_last'] = [10, 10]

# new constraint list
settings['constraints'] = [dict(name='min_lay_length', index=0, threshold=20, offset='max')]
# no more need to set up offset constraints, as the internal solve process associated with solve_for='offset' will size the line length to meet the offset equality
for j in range(len(settings['lineTypeNames'])):
    settings['constraints'].append(dict(name='tension_safety_factor', index=j, threshold=2.0, offset='max'))


ld2 = LineDesign(depth, lineProps=moorprops_file, **settings)
ld2.setNormalization()

print('\n=== solve_for: offset ===')
print(f"Mode inputs: Xindices={settings['Xindices']}, x_target={settings['x_target']}, fx_target={settings['fx_target']:.1f}")
X, min_cost = ld2.optimize(maxIter=400, plot=False, display=2, stepfac=4, method='COBYLA')
ld2.updateDesign(X, display=0)

# print out results
getResults(X, ld2)

# plot the design profile
ld2.plotProfile()

if SHOW_PLOTS:
    plt.show()

# nothing much should have changed from the "simple" script. Except this uses the 'offset' design mode, 
# which can reduce the number of design variables and constraints and use less optimization iterations






# We can run with solve_for = 'tension' too ('stiffness' has very similar inputs)
# keeping the same settings dictionary and just updating the necessary values
settings['solve_for'] = 'tension'
settings['fx_target'] = 400000

ld3 = LineDesign(depth, lineProps=moorprops_file, **settings)
ld3.setNormalization()

print('\n=== solve_for: tension ===')
print(f"Mode inputs: Xindices={settings['Xindices']}, fx_target={settings['fx_target']:.1f}")
X, min_cost = ld3.optimize(maxIter=400, plot=False, display=2, stepfac=4, method='COBYLA')
ld3.updateDesign(X, display=0)

# print out results
getResults(X, ld3)

# plot the design profile
ld3.plotProfile()

if SHOW_PLOTS:
    plt.show()



# Running with design mode = 'ghost'

settings['solve_for'] = 'ghost'
settings['fx_target'] = 1.95e6
settings['lay_target'] = 20

settings['Xindices'] = ['c', 0, 1]
settings['Xmin'] = [10, 10]
settings['Xmax'] = [10000, 500]
settings['dX_last'] = [10, 10]

settings['constraints'] = [dict(name='max_offset'    , index=0, threshold=34.4, offset='max')]
for j in range(len(settings['lineTypeNames'])):
    settings['constraints'].append(dict(name='tension_safety_factor', index=j, threshold=2.0, offset='max'))




ld4 = LineDesign(depth, lineProps=moorprops_file, **settings)
ld4.setNormalization()

print('\n=== solve_for: ghost ===')
print(f"Mode inputs: Xindices={settings['Xindices']}, lay_target={settings['lay_target']}, fx_target={settings['fx_target']:.1f}")
X, min_cost = ld4.optimize(maxIter=40, plot=False, display=3, stepfac=4, method='COBYLA')
ld4.updateDesign(X, display=0)

# print out results
getResults(X, ld4)

# plot the design profile
ld4.plotProfile()

if SHOW_PLOTS:
    plt.show()











